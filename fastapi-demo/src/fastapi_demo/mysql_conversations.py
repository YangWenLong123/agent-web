import json
import os
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

import pymysql
from pymysql.cursors import DictCursor

from fastapi_demo.conversations import ConversationBusy, ConversationNotFound, ConversationRepository, now


@dataclass(frozen=True)
class MySQLSettings:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: str = field(default="", repr=False)
    database: str = "deepseek_chat"

    def __post_init__(self):
        # 库名用于 CREATE DATABASE 标识符，禁止任意 SQL 字符。
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", self.database):
            raise ValueError("MYSQL_DATABASE 必须以英文字母开头，只能包含字母、数字和下划线，长度不超过 64。")
        if not 1 <= self.port <= 65535:
            raise ValueError("MYSQL_PORT 必须在 1–65535 之间。")

    @classmethod
    def from_env(cls) -> "MySQLSettings":
        return cls(
            host=os.getenv("MYSQL_HOST", cls.host),
            port=int(os.getenv("MYSQL_PORT", str(cls.port))),
            user=os.getenv("MYSQL_USER", cls.user),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", cls.database),
        )


class MySQLConversationRepository(ConversationRepository):
    """与 SQLite 相同的问答接口；每次操作使用独立连接及事务。"""

    def __init__(self, settings: MySQLSettings, *, recover_unfinished: bool = True):
        self.settings = settings
        with self._connect(select_database=False) as connection:
            connection.cursor().execute(
                f"CREATE DATABASE IF NOT EXISTS `{settings.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        schema = Path(__file__).with_name("mysql_schema.sql").read_text()
        with self._connect() as connection:
            cursor = connection.cursor()
            for statement in schema.split(";"):
                if statement.strip():
                    cursor.execute(statement)
            if recover_unfinished:
                cursor.execute(
                    "UPDATE turns SET status='interrupted', error=%s WHERE status='generating'",
                    ("服务已重启，本次生成中断；已保存收到的内容。",),
                )

    @contextmanager
    def _connect(self, *, select_database: bool = True):
        connection = pymysql.connect(
            host=self.settings.host, port=self.settings.port,
            user=self.settings.user, password=self.settings.password,
            database=self.settings.database if select_database else None,
            charset="utf8mb4", cursorclass=DictCursor,
            connect_timeout=5, read_timeout=10, write_timeout=10,
            autocommit=False,
        )
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _conversation(cursor, conversation_id: str, *, lock: bool = False) -> dict:
        cursor.execute("SELECT * FROM conversations WHERE id=%s" + (" FOR UPDATE" if lock else ""), (conversation_id,))
        row = cursor.fetchone()
        if row is None:
            raise ConversationNotFound
        return row

    @staticmethod
    def decode_turn(row) -> dict:
        turn = ConversationRepository.decode_turn(row)
        turn.pop("sequence_no", None)
        return turn

    def list_conversations(self) -> list[dict]:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT c.*, COALESCE(t.turn_count, 0) AS turn_count
                FROM conversations c LEFT JOIN (
                    SELECT conversation_id, COUNT(*) AS turn_count FROM turns GROUP BY conversation_id
                ) t ON c.id=t.conversation_id ORDER BY c.updated_at DESC, c.id
            """)
            return cursor.fetchall()

    def get(self, conversation_id: str) -> dict:
        with self._connect() as connection:
            cursor = connection.cursor()
            conversation = self._conversation(cursor, conversation_id)
            cursor.execute("SELECT * FROM turns WHERE conversation_id=%s ORDER BY sequence_no", (conversation_id,))
            return {**conversation, "turns": [self.decode_turn(row) for row in cursor.fetchall()]}

    def _history_rows(self, conversation_id: str) -> list:
        with self._connect() as connection:
            cursor = connection.cursor()
            self._conversation(cursor, conversation_id)
            cursor.execute(
                "SELECT content, result_json FROM turns WHERE conversation_id=%s AND status='completed' ORDER BY sequence_no DESC LIMIT 20",
                (conversation_id,),
            )
            return cursor.fetchall()

    def begin_turn(self, content: str, stream_id: str, model: str, conversation_id: str | None, context_count: int) -> tuple[dict, dict]:
        timestamp = now()
        with self._connect() as connection:
            cursor = connection.cursor()
            if conversation_id is None:
                conversation_id = uuid4().hex
                cursor.execute(
                    "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (%s, %s, %s, %s)",
                    (conversation_id, " ".join(content.split())[:32], timestamp, timestamp),
                )
            # 锁住对话行，检查与插入处在同一事务，防止并发创建两条生成记录。
            conversation = self._conversation(cursor, conversation_id, lock=True)
            cursor.execute("SELECT 1 FROM turns WHERE conversation_id=%s AND status='generating' LIMIT 1", (conversation_id,))
            if cursor.fetchone():
                raise ConversationBusy
            turn_id = uuid4().hex
            cursor.execute("""
                INSERT INTO turns (id, conversation_id, content, answer, raw_json, status, error, stream_id, model, context_count, created_at, updated_at)
                VALUES (%s, %s, %s, '', '', 'generating', '', %s, %s, %s, %s, %s)
            """, (turn_id, conversation_id, content, stream_id, model, context_count, timestamp, timestamp))
            cursor.execute("UPDATE conversations SET updated_at=%s WHERE id=%s", (timestamp, conversation_id))
            cursor.execute("SELECT * FROM turns WHERE id=%s", (turn_id,))
            return {**conversation, "updated_at": timestamp}, self.decode_turn(cursor.fetchone())

    def save_turn(self, turn_id: str, raw_json: str, *, status: str = "generating", result: dict | None = None, usage: dict | None = None, error: str = "") -> None:
        timestamp = now()
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE turns SET raw_json=%s, answer=%s, result_json=%s, usage_json=%s, status=%s, error=%s, updated_at=%s WHERE id=%s
            """, (
                raw_json, result.get("answer", "") if result else "",
                json.dumps(result, ensure_ascii=False) if result is not None else None,
                json.dumps(usage) if usage is not None else None,
                status, error, timestamp, turn_id,
            ))
            cursor.execute("""
                UPDATE conversations SET updated_at=%s WHERE id=(SELECT conversation_id FROM turns WHERE id=%s)
            """, (timestamp, turn_id))

    def migrate_from_sqlite(self, path: Path) -> dict:
        """只读源库；同 ID 同内容则跳过，冲突时回滚，绝不覆盖目标历史。"""
        path = path.resolve(strict=True)
        source = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
        source.row_factory = sqlite3.Row
        try:
            source.execute("BEGIN")
            rows = {table: [dict(row) for row in source.execute(f"SELECT * FROM {table} ORDER BY rowid")]
                    for table in ("conversations", "turns")}
        finally:
            source.close()
        if any(row["status"] == "generating" for row in rows["turns"]):
            raise ValueError("源库仍有生成中的回答，请先正常停止后端服务，再迁移。")
        counts = {"conversations": 0, "turns": 0}
        with self._connect() as connection:
            cursor = connection.cursor()
            for table, records in rows.items():
                for row in records:
                    cursor.execute(f"SELECT * FROM {table} WHERE id=%s", (row["id"],))
                    existing = cursor.fetchone()
                    if existing is None:
                        columns = ", ".join(f"`{key}`" for key in row)
                        placeholders = ", ".join(["%s"] * len(row))
                        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(row.values()))
                        counts[table] += 1
                        cursor.execute(f"SELECT * FROM {table} WHERE id=%s", (row["id"],))
                        existing = cursor.fetchone()
                    if any(existing.get(key) != value for key, value in row.items()):
                        raise ValueError(f"迁移校验失败：{table} 中存在不同内容的同 ID 记录，目标历史未被覆盖。")
        return {"source_conversations": len(rows["conversations"]), "source_turns": len(rows["turns"]), "inserted": counts}

    def close(self) -> None:
        # 连接均在每次操作结束时关闭，实例本身没有常驻连接。
        pass
