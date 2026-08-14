#!/bin/bash

echo "Stopping containers..."
docker compose -f "docker-compose.dev.yml" down

echo "Building images without cache..."
docker compose -f "docker-compose.dev.yml" build --no-cache

echo "Starting containers..."
docker compose -f "docker-compose.dev.yml" up -d