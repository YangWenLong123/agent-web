import asyncio
import json
import time
import unittest
import os
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from fastapi_demo.deepseek import DeepSeekSettings, Generation, GenerationStore
from fastapi_demo.main import app


def upstream_stream(parts, finish="stop", done=True):
    chunks = [": heartbeat\n\n"]
    for part in parts:
        chunks.append("data: " + json.dumps({"choices": [{"index": 0, "delta": {"content": part}, "finish_reason": None}]}) + "\n\n")
    chunks.append("data: " + json.dumps({"choices": [{"index": 0, "delta": {}, "finish_reason": finish}], "usage": {"total_tokens": 12}}) + "\n\n")
    if done:
        chunks.append("data: [DONE]\n\n")
    return "".join(chunks)


class DeepSeekTests(unittest.IsolatedAsyncioTestCase):
    async def run_generation(self, response):
        requests = []

        def handler(request):
            requests.append(request)
            return response

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            store = GenerationStore(DeepSeekSettings(api_key="test-secret", model="deepseek-v4-pro"), client)
            job = store.create("介绍 SSE")
            await job.task
        return job, requests

    async def test_streams_json_and_calls_expected_model(self):
        job, requests = await self.run_generation(httpx.Response(200, text=upstream_stream(['{"answer":', '"你好\\n世界"}'])))
        self.assertEqual([event for event, _ in job.events], ["message", "message", "done"])
        self.assertEqual(job.events[-1][1]["result"], {"answer": "你好\n世界"})
        self.assertEqual(job.events[-1][1]["count"], 2)
        body = json.loads(requests[0].content)
        self.assertEqual(body["model"], "deepseek-v4-pro")
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertEqual(body["messages"][-1]["content"], "介绍 SSE")
        self.assertEqual(str(requests[0].url), "https://api.deepseek.com/v1/chat/completions")
        self.assertEqual(len(requests), 1)

    async def test_http_errors_do_not_leak_upstream_body(self):
        for code in (401, 402, 429, 500):
            job, _ = await self.run_generation(httpx.Response(code, text="test-secret raw upstream body"))
            self.assertEqual(job.events[-1][0], "failure")
            self.assertNotIn("test-secret", json.dumps(job.events))
            self.assertIsNotNone(job.finished_at)

    async def test_incomplete_invalid_and_truncated_json_fail(self):
        for body in (
            upstream_stream(['{"answer":"partial'], finish="length"),
            upstream_stream(['not JSON']),
            upstream_stream(['{"answer":"ok"}'], done=False),
            upstream_stream(['{"other":"wrong shape"}']),
        ):
            job, _ = await self.run_generation(httpx.Response(200, text=body))
            self.assertEqual(job.events[-1][0], "failure")
            self.assertNotIn("done", [event for event, _ in job.events])

    async def test_shutdown_cancels_active_generation(self):
        entered = asyncio.Event()

        async def handler(request):
            entered.set()
            await asyncio.Event().wait()

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            store = GenerationStore(DeepSeekSettings(api_key="test"), client)
            job = store.create("test")
            await entered.wait()
            await store.close()
            self.assertTrue(job.task.cancelled())


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"CHAT_DB_BACKEND": "sqlite", "CHAT_DB_PATH": ":memory:"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_post_then_resume_reuses_one_model_request(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(200, text=upstream_stream(['{"answer":', '"真实流协议"}']))

        with TestClient(app) as client:
            upstream = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            app.state.generations.client = upstream
            app.state.generations.settings = DeepSeekSettings(api_key="test-secret")
            try:
                created = client.post("/api/sse/generations", json={"content": "请回答"})
                self.assertEqual(created.status_code, 201)
                stream_id = created.json()["stream_id"]
                full = client.get(f"/api/sse/jsonlines?stream_id={stream_id}")
                resumed = client.get(f"/api/sse/jsonlines?stream_id={stream_id}&after_id=1")
                self.assertEqual(full.status_code, 200)
                self.assertIn("event: done", full.text)
                self.assertTrue(resumed.text.startswith("id: 2\n"))
                self.assertNotIn('"index": 1', resumed.text)
                self.assertEqual(len(requests), 1)
            finally:
                client.portal.call(upstream.aclose)

    def test_replay_cursor_errors_and_no_new_upstream_call(self):
        with TestClient(app) as client:
            store = app.state.generations
            job = Generation(stream_id="a" * 32)
            job.append("message", {"type": "delta", "index": 1, "content": '{"answer":'})
            job.append("message", {"type": "delta", "index": 2, "content": '"你好"}'})
            job.append("done", {"type": "done", "count": 2, "result": {"answer": "你好"}})
            job.finished_at = time.monotonic()
            store.jobs[job.stream_id] = job
            response = client.get(f"/api/sse/jsonlines?stream_id={job.stream_id}&after_id=1")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.headers["content-type"].startswith("text/event-stream"))
            self.assertTrue(response.text.startswith("id: 2\n"))
            self.assertNotIn('"index": 1', response.text)
            self.assertIn("event: done", response.text)
            self.assertEqual(client.get(f"/api/sse/jsonlines?stream_id={job.stream_id}&after_id=4").status_code, 422)
            self.assertEqual(client.get(f"/api/sse/jsonlines?stream_id={'b' * 32}").status_code, 404)
            self.assertEqual(client.get("/api/sse/jsonlines").status_code, 422)
            for content in ("", "  ", "x" * 8001):
                self.assertEqual(client.post("/api/sse/generations", json={"content": content}).status_code, 422)
            self.assertEqual(client.get("/api/users/").status_code, 200)
            store.settings = DeepSeekSettings(api_key="")
            self.assertEqual(client.post("/api/sse/generations", json={"content": "hi"}).status_code, 503)
            job.finished_at -= 1801
            self.assertEqual(client.get(f"/api/sse/jsonlines?stream_id={job.stream_id}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
