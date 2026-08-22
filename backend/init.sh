#!/bin/sh

set -e

echo "Running database migrations..."

uv run alembic upgrade head

echo "Initializing admin user..."

uv run python -m app.scripts.init_admin

echo "Initialization complete."