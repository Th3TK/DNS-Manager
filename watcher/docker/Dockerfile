FROM python:3.14-slim

WORKDIR /watcher

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev

COPY src ./src

CMD ["uv", "run", "--no-dev", "python", "-m", "src.main"]