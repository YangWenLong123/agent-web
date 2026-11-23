#FROM ubuntu:latest
#LABEL authors="along"
#
#ENTRYPOINT ["top", "-b"]

FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN uv pip install --system --require-hashes \
    -r /tmp/requirements.txt

COPY dist/*.whl /tmp/

RUN uv pip install --system --no-deps /tmp/*.whl

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "fastapi_demo.main:app", "--host", "0.0.0.0", "--port", "8000"]