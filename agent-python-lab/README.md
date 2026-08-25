# 创建项目

```sh
uv init agent-python-lab
cd agent-python-lab

uv python install 3.12
uv python pin 3.12

uv add fastapi "uvicorn[standard]" httpx pydantic-settings
uv add --dev pytest pytest-asyncio ruff mypy
```

# 创建 app/main.py

````python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

# 运行项目

```sh
uv run uvicorn app.main:app --reload
````

# 访问

- API：http://127.0.0.1:8000/health
- Swagger：http://127.0.0.1:8000/docs

# 测试和检查

```sh
uv run pytest
uv run ruff check .
uv run mypy app
```
