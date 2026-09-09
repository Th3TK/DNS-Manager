FROM python:3.14-slim

WORKDIR /backend

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock alembic.ini ./

RUN uv sync --locked --no-dev

COPY app ./app

COPY migrations ./migrations

CMD ["uv", "run", "--no-dev", "--exact", "uvicorn", "app.main:app", "--host", "0.0.0.0"]