import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ConversationNotFound(Exception):
    pass


class ConversationBusy(Exception):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationRepository:
    """保存完整问答；模型上下文只选取最近的完整问答。"""

    def __init__(self, path: str | Path = ":memory:"):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY, title TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS turns (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL REFERENCES conversations(id),
                content TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '',
                raw_json TEXT NOT NULL DEFAULT '', result_json TEXT,
                status TEXT NOT NULL, error TEXT NOT NULL DEFAULT '',
                stream_id TEXT NOT NULL, model TEXT NOT NULL,
                usage_json TEXT, context_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS turns_conversation ON turns(conversation_id);
        """)
        # 服务重启后无法恢复原模型连接，保留已持久化片段并明确标记中断。
        with self.connection:
            self.connection.execute(
                "UPDATE turns SET status='interrupted', error=? WHERE status='generating'",
                ("服务已重启，本次生成中断；已保存收到的内容。",),
            )

    def list_conversations(self) -> list[dict]:
        rows = self.connection.execute("""
            SELECT c.*, COUNT(t.id) AS turn_count
            FROM conversations c LEFT JOIN turns t ON c.id=t.conversation_id
            GROUP BY c.id ORDER BY c.updated_at DESC
        """).fetchall()
        return [dict(row) for row in rows]

    def get(self, conversation_id: str) -> dict:
        row = self.connection.execute("SELECT * FROM conversations WHERE id=?", (conversation_id,)).fetchone()
        if row is None:
            raise ConversationNotFound
        turns = self.connection.execute(
            "SELECT * FROM turns WHERE conversation_id=? ORDER BY rowid", (conversation_id,)
        ).fetchall()
        result = dict(row)
        result["turns"] = [self.decode_turn(turn) for turn in turns]
        return result

    @staticmethod
    def decode_turn(row) -> dict:
        turn = dict(row)
        turn["result"] = json.loads(turn.pop("result_json") or "null")
        turn["usage"] = json.loads(turn.pop("usage_json") or "null")
        return turn

    def history(self, conversation_id: str | None, current_content: str) -> list[dict]:
        if conversation_id is None:
            return []
        rows = self._history_rows(conversation_id)
        pairs = []
        size = len(current_content)
        for row in rows:
            size += len(row["content"]) + len(row["result_json"])
            if size > 32000:
                break
            pairs.append([
                {"role": "user", "content": row["content"]},
                {"role": "assistant", "content": row["result_json"]},
            ])
        return [message for pair in reversed(pairs) for message in pair]

    def _history_rows(self, conversation_id: str) -> list:
        self.get(conversation_id)
        return self.connection.execute(
            "SELECT content, result_json FROM turns WHERE conversation_id=? AND status='completed' ORDER BY rowid DESC LIMIT 20",
            (conversation_id,),
        ).fetchall()

    def begin_turn(self, content: str, stream_id: str, model: str, conversation_id: str | None, context_count: int) -> tuple[dict, dict]:
        timestamp = now()
        with self.connection:
            if conversation_id is None:
                conversation_id = uuid4().hex
                title = " ".join(content.split())[:32]
                self.connection.execute(
                    "INSERT INTO conversations VALUES (?, ?, ?, ?)",
                    (conversation_id, title, timestamp, timestamp),
                )
            else:
                self.get(conversation_id)
                if self.connection.execute(
                    "SELECT 1 FROM turns WHERE conversation_id=? AND status='generating'", (conversation_id,)
                ).fetchone():
                    raise ConversationBusy
            turn_id = uuid4().hex
            self.connection.execute("""
                INSERT INTO turns (id, conversation_id, content, status, stream_id, model, context_count, created_at, updated_at)
                VALUES (?, ?, ?, 'generating', ?, ?, ?, ?, ?)
            """, (turn_id, conversation_id, content, stream_id, model, context_count, timestamp, timestamp))
            self.connection.execute("UPDATE conversations SET updated_at=? WHERE id=?", (timestamp, conversation_id))
        conversation = self.get(conversation_id)
        return {key: value for key, value in conversation.items() if key != "turns"}, conversation["turns"][-1]

    def save_turn(self, turn_id: str, raw_json: str, *, status: str = "generating", result: dict | None = None, usage: dict | None = None, error: str = "") -> None:
        timestamp = now()
        with self.connection:
            self.connection.execute("""
                UPDATE turns SET raw_json=?, answer=?, result_json=?, usage_json=?, status=?, error=?, updated_at=? WHERE id=?
            """, (
                raw_json, result.get("answer", "") if result else "",
                json.dumps(result, ensure_ascii=False) if result is not None else None,
                json.dumps(usage) if usage is not None else None,
                status, error, timestamp, turn_id,
            ))
            self.connection.execute("""
                UPDATE conversations SET updated_at=? WHERE id=(SELECT conversation_id FROM turns WHERE id=?)
            """, (timestamp, turn_id))

    def close(self) -> None:
        self.connection.close()


def create_repository() -> ConversationRepository:
    """按配置选择存储；MySQL 连接失败时直接报错，避免误写到其他数据库。"""
    backend = os.getenv("CHAT_DB_BACKEND", "mysql").strip().lower()
    if backend == "mysql":
        from fastapi_demo.mysql_conversations import MySQLConversationRepository, MySQLSettings

        return MySQLConversationRepository(MySQLSettings.from_env())
    if backend == "sqlite":
        path = os.getenv("CHAT_DB_PATH", str(Path(__file__).resolve().parents[2] / "data" / "chat.sqlite3"))
        return ConversationRepository(path)
    raise ValueError("CHAT_DB_BACKEND 仅支持 mysql 或 sqlite。")
