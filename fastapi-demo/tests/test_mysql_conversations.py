import asyncio
import json
import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import httpx
from dotenv import load_dotenv

from fastapi_demo.conversations import ConversationBusy, ConversationNotFound, ConversationRepository, create_repository
from fastapi_demo.deepseek import DeepSeekSettings, GenerationStore
from fastapi_demo.mysql_conversations import MySQLConversationRepository, MySQLSettings


class MySQLConfigTests(unittest.TestCase):
    def test_database_identifier_and_port_are_validated_and_password_is_hidden(self):
        for name in ("", "a`; DROP DATABASE a", "a-b", "a" * 65):
            with self.assertRaises(ValueError):
                MySQLSettings(database=name)
        with self.assertRaises(ValueError):
            MySQLSettings(port=0)
        self.assertNotIn("test-password", repr(MySQLSettings(password="test-password")))
        with patch.dict(os.environ, {"CHAT_DB_BACKEND": "unknown"}):
            with self.assertRaises(ValueError):
                create_repository()


@unittest.skipUnless(os.getenv("RUN_MYSQL_TESTS") == "1", "设置 RUN_MYSQL_TESTS=1 运行本地 MySQL 集成测试")
class MySQLIntegrationTests(unittest.TestCase):
    def setUp(self):
        load_dotenv(Path(__file__).resolve().parents[1] / ".env")
        self.settings = replace(MySQLSettings.from_env(), database="deepseek_test_" + uuid4().hex[:16])
        self.repository = MySQLConversationRepository(self.settings)
        self.addCleanup(self.cleanup_database)

    def cleanup_database(self):
        self.repository.close()
        # 只清理本测试创建的随机独立库，绝不访问真实对话库。
        with self.repository._connect(select_database=False) as connection:
            connection.cursor().execute(f"DROP DATABASE `{self.settings.database}`")

    def completed_turn(self, content="我的项目叫流星 🚀", conversation_id=None):
        conversation, turn = self.repository.begin_turn(content, uuid4().hex, "deepseek-v4-pro", conversation_id, 0)
        result = {"answer": "记住了 🚀\n继续说吧", "nested": {"quote": '"引用"'}}
        self.repository.save_turn(turn["id"], json.dumps(result, ensure_ascii=False), status="completed", result=result, usage={"total_tokens": 20})
        return conversation, turn

    def test_persistence_reopen_partial_recovery_and_unicode(self):
        conversation, first = self.completed_turn()
        _, second = self.repository.begin_turn("继续", uuid4().hex, "model", conversation["id"], 1)
        self.repository.save_turn(second["id"], '{"answer":"部分内容 🚀')
        restored = MySQLConversationRepository(self.settings)
        detail = restored.get(conversation["id"])
        self.assertEqual(detail["turns"][0]["answer"], "记住了 🚀\n继续说吧")
        self.assertEqual(detail["turns"][0]["usage"], {"total_tokens": 20})
        self.assertEqual(detail["turns"][1]["status"], "interrupted")
        self.assertIn("部分内容 🚀", detail["turns"][1]["raw_json"])
        self.assertEqual(len(restored.history(conversation["id"], "你好")), 2)
        self.assertEqual(restored.list_conversations()[0]["turn_count"], 2)
        self.assertNotIn("sequence_no", detail["turns"][0])
        with self.assertRaises(ConversationNotFound):
            restored.get("0" * 32)

    def test_simultaneous_generation_is_locked_and_rejected_without_extra_rows(self):
        conversation, _ = self.completed_turn()
        barrier = threading.Barrier(2)

        def create_turn():
            barrier.wait(timeout=5)
            try:
                self.repository.begin_turn("并发问题", uuid4().hex, "model", conversation["id"], 1)
                return "created"
            except ConversationBusy:
                return "busy"

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: create_turn(), range(2)))
        self.assertCountEqual(results, ["created", "busy"])
        self.assertEqual(len(self.repository.get(conversation["id"])["turns"]), 2)

    def test_context_limit_order_and_isolation(self):
        conversation_id = None
        for index in range(22):
            conversation, _ = self.completed_turn(f"第{index}轮", conversation_id)
            conversation_id = conversation["id"]
        history = self.repository.history(conversation_id, "下一轮")
        self.assertEqual(len(history), 40)
        self.assertEqual(history[0]["content"], "第2轮")
        self.assertEqual(history[-2]["content"], "第21轮")
        other, _ = self.repository.begin_turn("另一个对话", uuid4().hex, "model", None, 0)
        self.assertEqual(self.repository.history(other["id"], "你好"), [])
        # 单条历史超过字符窗口时不发送该历史，但完整记录仍保存。
        _, turn = self.repository.begin_turn("大回答", uuid4().hex, "model", conversation_id, 0)
        self.repository.save_turn(turn["id"], "", status="completed", result={"answer": "字" * 32000})
        self.assertEqual(self.repository.history(conversation_id, "继续"), [])
        self.assertEqual(len(self.repository.get(conversation_id)["turns"]), 23)

    def test_sqlite_migration_is_verified_repeatable_and_rolls_back_on_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.sqlite3"
            source = ConversationRepository(path)
            conversation, turn = source.begin_turn("迁移问题 🚀", uuid4().hex, "model", None, 0)
            source.save_turn(turn["id"], '{"answer":"原回答"}', status="completed", result={"answer": "原回答"})
            original = source.get(conversation["id"])
            first = self.repository.migrate_from_sqlite(path)
            self.assertEqual(first["inserted"], {"conversations": 1, "turns": 1})
            self.assertEqual(self.repository.get(conversation["id"]), original)
            second = self.repository.migrate_from_sqlite(path)
            self.assertEqual(second["inserted"], {"conversations": 0, "turns": 0})
            extra, _ = source.begin_turn("冲突前新增的对话", uuid4().hex, "model", None, 0)
            # 生成中的源记录必须拒绝。
            with self.assertRaises(ValueError):
                self.repository.migrate_from_sqlite(path)
            source.connection.execute("UPDATE turns SET status='interrupted' WHERE status='generating'")
            source.connection.commit()
            # 调整读取顺序，确保新增记录也随后续冲突一起回滚。
            source.connection.execute("UPDATE conversations SET rowid=100 WHERE id=?", (conversation["id"],))
            source.connection.execute("UPDATE turns SET answer='冲突回答' WHERE id=?", (turn["id"],))
            source.connection.commit()
            with self.assertRaises(ValueError):
                self.repository.migrate_from_sqlite(path)
            self.assertEqual(self.repository.get(conversation["id"]), original)
            with self.assertRaises(ConversationNotFound):
                self.repository.get(extra["id"])
            self.assertTrue(path.exists())
            source.close()

    def test_mysql_model_request_contains_saved_memory(self):
        conversation, _ = self.completed_turn()
        requests = []

        def handler(request):
            requests.append(json.loads(request.content))
            payload = {"choices": [{"delta": {"content": '{"answer":"流星"}'}, "finish_reason": "stop"}]}
            return httpx.Response(200, text="data: " + json.dumps(payload) + "\n\ndata: [DONE]\n\n")

        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                store = GenerationStore(DeepSeekSettings(api_key="test"), client, self.repository)
                job = store.create("项目叫什么？", conversation["id"])
                await job.task
                self.assertEqual(job.events[-1][0], "done")
                self.assertEqual(job.context_count, 1)
                await store.close()

        asyncio.run(run())
        self.assertEqual(requests[0]["messages"][1]["content"], "我的项目叫流星 🚀")
        self.assertEqual(self.repository.get(conversation["id"])["turns"][-1]["answer"], "流星")

    def test_live_routes_use_configured_mysql_repository(self):
        from fastapi.testclient import TestClient
        from fastapi_demo.main import app

        conversation, _ = self.completed_turn()
        with patch.dict(os.environ, {"CHAT_DB_BACKEND": "mysql", "MYSQL_DATABASE": self.settings.database}):
            with TestClient(app) as client:
                self.assertIsInstance(app.state.generations.repository, MySQLConversationRepository)
                response = client.get(f"/api/sse/conversations/{conversation['id']}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["turns"][0]["content"], "我的项目叫流星 🚀")
                self.assertEqual(client.get("/api/sse/conversations").json()[0]["turn_count"], 1)
