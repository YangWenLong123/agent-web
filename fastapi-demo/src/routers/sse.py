import asyncio
import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from fastapi_demo.deepseek import GenerationError, GenerationStore
from fastapi_demo.conversations import ConversationBusy, ConversationNotFound

router = APIRouter()


class GenerateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    content: str = Field(min_length=1, max_length=8000, description="发送给大模型的内容")
    conversation_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$", description="继续已有对话时传入；不传则新建")


class GenerateResponse(BaseModel):
    stream_id: str
    model: str
    conversation_id: str
    turn_id: str
    title: str
    context_count: int


@router.post("/generations", response_model=GenerateResponse, status_code=201, summary="发送内容，创建 DeepSeek 生成任务")
async def create_generation(body: GenerateRequest, request: Request) -> GenerateResponse:
    store: GenerationStore = request.app.state.generations
    try:
        job = store.create(body.content, body.conversation_id)
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="对话不存在，请新建对话。") from None
    except ConversationBusy:
        raise HTTPException(status_code=409, detail="当前对话仍在生成，请继续接收或等待完成后再发送。") from None
    except GenerationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None
    return GenerateResponse(
        stream_id=job.stream_id, model=store.settings.model, conversation_id=job.conversation_id,
        turn_id=job.turn_id, title=job.title, context_count=job.context_count,
    )


@router.get("/conversations", summary="读取已保存的历史对话")
async def list_conversations(request: Request):
    return request.app.state.generations.repository.list_conversations()


@router.get("/conversations/{conversation_id}", summary="读取对话中的全部问答")
async def get_conversation(conversation_id: str, request: Request):
    try:
        return request.app.state.generations.repository.get(conversation_id)
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="对话不存在。") from None


@router.get(
    "/jsonlines",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
    summary="实时订阅 DeepSeek JSON 数据，支持游标续传",
)
async def stream_jsonlines(
    request: Request,
    stream_id: Annotated[str, Query(pattern=r"^[a-f0-9]{32}$", description="创建任务返回的 ID")],
    after_id: Annotated[int, Query(ge=0, description="最后收到的 SSE 事件 ID")] = 0,
) -> StreamingResponse:
    store: GenerationStore = request.app.state.generations
    store.prune()
    job = store.jobs.get(stream_id)
    if job is None:
        raise HTTPException(status_code=404, detail="生成记录不存在或已过期，请重新发送。")
    if after_id > len(job.events):
        raise HTTPException(status_code=422, detail="after_id 超出已有事件范围")

    async def generate() -> AsyncIterator[str]:
        cursor = after_id
        while True:
            if await request.is_disconnected():
                return
            if cursor < len(job.events):
                event, payload = job.events[cursor]
                cursor += 1
                event_line = "" if event == "message" else f"event: {event}\n"
                yield f"id: {cursor}\n{event_line}data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            elif job.finished_at is not None:
                return
            else:
                job.changed.clear()
                try:
                    await asyncio.wait_for(job.changed.wait(), timeout=15)
                except TimeoutError:
                    yield ": keep-alive\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
