import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from uuid import uuid4

import httpx

from fastapi_demo.conversations import ConversationRepository


@dataclass(frozen=True)
class DeepSeekSettings:
    api_key: str = field(repr=False)
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-v4-pro"

    @classmethod
    def from_env(cls) -> "DeepSeekSettings":
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
            base_url=os.getenv("DEEPSEEK_BASE_URL", cls.base_url).rstrip("/"),
            model=os.getenv("DEEPSEEK_MODEL", cls.model),
        )


@dataclass
class Generation:
    stream_id: str
    conversation_id: str = ""
    turn_id: str = ""
    title: str = ""
    context_count: int = 0
    events: list[tuple[str, dict]] = field(default_factory=list)
    changed: asyncio.Event = field(default_factory=asyncio.Event)
    finished_at: float | None = None
    task: asyncio.Task | None = None

    def append(self, event: str, payload: dict) -> None:
        self.events.append((event, payload))
        self.changed.set()


class GenerationError(Exception):
    """只携带可展示给客户端的错误，不包含上游响应或密钥。"""


class GenerationStore:
    """单进程演示用任务缓存；暂停订阅时继续生成，以支持准确续传。"""

    def __init__(self, settings: DeepSeekSettings, client: httpx.AsyncClient, repository: ConversationRepository | None = None):
        self.settings = settings
        self.client = client
        self.jobs: dict[str, Generation] = {}
        self.repository = repository or ConversationRepository()

    def prune(self) -> None:
        now = time.monotonic()
        for stream_id, job in list(self.jobs.items()):
            if job.finished_at is not None and now - job.finished_at > 1800:
                del self.jobs[stream_id]

    def create(self, content: str, conversation_id: str | None = None) -> Generation:
        self.prune()
        if not self.settings.api_key:
            raise GenerationError("后端尚未配置 DEEPSEEK_API_KEY。")
        if len(self.jobs) >= 16:
            completed = next((key for key, job in self.jobs.items() if job.finished_at is not None), None)
            if completed is None:
                raise GenerationError("当前生成任务较多，请稍后再试。")
            del self.jobs[completed]
        history = self.repository.history(conversation_id, content)
        stream_id = uuid4().hex
        conversation, turn = self.repository.begin_turn(content, stream_id, self.settings.model, conversation_id, len(history) // 2)
        job = Generation(
            stream_id=stream_id, conversation_id=conversation["id"], turn_id=turn["id"],
            title=conversation["title"], context_count=len(history) // 2,
        )
        self.jobs[job.stream_id] = job
        job.task = asyncio.create_task(self.generate(job, content, history))
        return job

    async def generate(self, job: Generation, content: str, history: list[dict]) -> None:
        fragments: list[str] = []
        finish_reason = None
        usage = None
        last_saved = time.monotonic()
        error_message = ""
        try:
            async with asyncio.timeout(300):
                async with self.client.stream(
                    "POST",
                    f"{self.settings.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.api_key}"},
                    json={
                        "model": self.settings.model,
                        "thinking": {"type": "disabled"},
                        "messages": [
                            {"role": "system", "content": '请回答用户的问题。必须只输出一个合法的 JSON 对象，格式为 {"answer": "你的回答"}，不要输出 Markdown 代码块。'},
                            *history,
                            {"role": "user", "content": content},
                        ],
                        "stream": True,
                        "stream_options": {"include_usage": True},
                        "response_format": {"type": "json_object"},
                        "max_tokens": 2048,
                    },
                ) as response:
                    if response.status_code != 200:
                        messages = {
                            401: "DeepSeek 密钥无效，请检查后端配置。",
                            402: "DeepSeek 账户余额不足，请充值后重试。",
                            429: "DeepSeek 请求过于频繁，请稍后重试。",
                        }
                        raise GenerationError(messages.get(response.status_code, f"DeepSeek 服务返回错误（HTTP {response.status_code}），请稍后重试。"))
                    saw_done = False
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        raw = line[5:].strip()
                        if raw == "[DONE]":
                            saw_done = True
                            break
                        if not raw:
                            continue
                        chunk = json.loads(raw)
                        if chunk.get("error"):
                            raise GenerationError("DeepSeek 返回流式错误，请重新发送。")
                        if chunk.get("usage") is not None:
                            usage = chunk["usage"]
                        for choice in chunk.get("choices", []):
                            if choice.get("index", 0) != 0:
                                continue
                            delta = choice.get("delta", {}).get("content")
                            if delta:
                                if not isinstance(delta, str) or len(fragments) >= 20000:
                                    raise GenerationError("模型返回的数据超出处理范围。")
                                fragments.append(delta)
                                job.append("message", {"type": "delta", "index": len(fragments), "content": delta})
                                if time.monotonic() - last_saved >= 1:
                                    self.repository.save_turn(job.turn_id, "".join(fragments))
                                    last_saved = time.monotonic()
                            if choice.get("finish_reason"):
                                finish_reason = choice["finish_reason"]
                    if not saw_done:
                        raise GenerationError("模型连接提前结束，请重新发送。")
            if finish_reason != "stop":
                raise GenerationError("模型未完整返回结果，可能达到输出长度限制，请缩短问题后重试。")
            result = json.loads("".join(fragments))
            if not isinstance(result, dict) or not isinstance(result.get("answer"), str):
                raise GenerationError("模型未返回约定的 JSON 对象，请重新发送。")
            self.repository.save_turn(job.turn_id, "".join(fragments), status="completed", result=result, usage=usage)
            job.append("done", {
                "type": "done", "count": len(fragments), "result": result,
                "model": self.settings.model, "usage": usage,
            })
        except GenerationError as exc:
            error_message = str(exc)
        except (TimeoutError, httpx.TimeoutException):
            error_message = "模型响应超时，请稍后重新发送。"
        except httpx.HTTPError:
            error_message = "无法连接 DeepSeek 服务，请检查后端网络。"
        except (ValueError, TypeError, AttributeError, KeyError):
            error_message = "模型返回的数据格式异常，请重新发送。"
        except asyncio.CancelledError:
            self.repository.save_turn(job.turn_id, "".join(fragments), status="interrupted", error="服务已停止，本次生成中断。")
            raise
        except Exception:
            error_message = "生成任务异常，请重新发送。"
        finally:
            if error_message:
                self.repository.save_turn(job.turn_id, "".join(fragments), status="error", error=error_message)
                job.append("failure", {"type": "error", "message": error_message})
            job.finished_at = time.monotonic()
            job.changed.set()

    async def close(self) -> None:
        tasks = [job.task for job in self.jobs.values() if job.task is not None]
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
