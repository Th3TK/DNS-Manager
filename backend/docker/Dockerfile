FROM python:3.14-slim

WORKDIR /backend

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock alembic.ini init.sh ./

RUN uv sync --no-dev

COPY app ./app

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]