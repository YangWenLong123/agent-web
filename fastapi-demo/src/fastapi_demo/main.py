from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi_demo.deepseek import DeepSeekSettings, GenerationStore
from fastapi_demo.conversations import create_repository
from routers.sse import router as sse_router
from routers.users import router as users_router

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=15)) as client:
        repository = create_repository()
        store = GenerationStore(DeepSeekSettings.from_env(), client, repository)
        app.state.generations = store
        try:
            yield
        finally:
            await store.close()
            repository.close()


app = FastAPI(lifespan=lifespan)
app.include_router(users_router, prefix="/api/users", tags=["用户管理"])
app.include_router(sse_router, prefix="/api/sse", tags=["DeepSeek SSE"])

# API 路由优先匹配，前端构建产物由同源静态服务提供。
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
