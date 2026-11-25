import asyncio
import json
import tempfile
import unittest
from pathlib import Path

import httpx

from fastapi_demo.conversations import ConversationBusy, ConversationRepository
from fastapi_demo.deepseek import DeepSeekSettings, GenerationStore


class PersistenceTests(unittest.TestCase):
    def test_saved_history_survives_restart_and_marks_unfinished_turn(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chat.sqlite3"
            repository = ConversationRepository(path)
            conversation, first = repository.begin_turn("我的项目叫流星", "a" * 32, "deepseek-v4-pro", None, 0)
            repository.save_turn(first["id"], '{"answer":"记住了"}', status="completed", result={"answer": "记住了"})
            _, second = repository.begin_turn("继续介绍", "b" * 32, "deepseek-v4-pro", conversation["id"], 1)
            repository.save_turn(second["id"], '{"answer":"部分内容')
            repository.close()
            restored = ConversationRepository(path)
            detail = restored.get(conversation["id"])
            self.assertEqual(len(detail["turns"]), 2)
            self.assertEqual(detail["turns"][0]["answer"], "记住了")
            self.assertEqual(detail["turns"][1]["status"], "interrupted")
            self.assertIn("部分内容", detail["turns"][1]["raw_json"])
            history = restored.history(conversation["id"], "项目叫什么")
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["content"], "我的项目叫流星")
            self.assertEqual(restored.list_conversations()[0]["turn_count"], 2)
            restored.close()

    def test_busy_conversation_is_rejected_and_context_is_bounded_and_isolated(self):
        repository = ConversationRepository()
        conversation, turn = repository.begin_turn("第0轮", "a" * 32, "model", None, 0)
        with self.assertRaises(ConversationBusy):
            repository.begin_turn("并发发送", "b" * 32, "model", conversation["id"], 0)
        repository.save_turn(turn["id"], '{}', status="completed", result={"answer": "答0"})
        for index in range(1, 22):
            _, turn = repository.begin_turn(f"第{index}轮", "a" * 32, "model", conversation["id"], index)
            repository.save_turn(turn["id"], '{}', status="completed", result={"answer": f"答{index}"})
        history = repository.history(conversation["id"], "下一轮")
        self.assertEqual(len(history), 40)
        self.assertEqual(history[0]["content"], "第2轮")
        other, _ = repository.begin_turn("独立对话", "c" * 32, "model", None, 0)
        self.assertEqual(repository.history(other["id"], "你好"), [])
        self.assertEqual(len(repository.get(conversation["id"])["turns"]), 22)
        repository.close()


class ModelMemoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_second_request_contains_prior_question_and_answer(self):
        requests = []

        def handler(request):
            requests.append(json.loads(request.content))
            result = json.dumps({"answer": "记住了" if len(requests) == 1 else "流星"}, ensure_ascii=False)
            chunks = [
                {"choices": [{"delta": {"content": result}, "finish_reason": None}]},
                {"choices": [{"delta": {}, "finish_reason": "stop"}]},
            ]
            body = "".join("data: " + json.dumps(chunk) + "\n\n" for chunk in chunks) + "data: [DONE]\n\n"
            return httpx.Response(200, text=body)

        repository = ConversationRepository()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            store = GenerationStore(DeepSeekSettings(api_key="test"), client, repository)
            first = store.create("我的项目叫流星")
            await first.task
            second = store.create("项目叫什么？", first.conversation_id)
            await second.task
            messages = requests[1]["messages"]
            self.assertEqual([message["role"] for message in messages], ["system", "user", "assistant", "user"])
            self.assertEqual(messages[1]["content"], "我的项目叫流星")
            self.assertEqual(json.loads(messages[2]["content"]), {"answer": "记住了"})
            self.assertEqual(messages[3]["content"], "项目叫什么？")
            self.assertEqual(second.context_count, 1)
            self.assertEqual(len(repository.get(first.conversation_id)["turns"]), 2)
            await store.close()
        repository.close()
