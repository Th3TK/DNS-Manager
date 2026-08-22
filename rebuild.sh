#!/bin/bash

echo "Stopping containers..."
docker compose -f "docker-compose.yml" down

echo "Building images without cache..."
docker compose -f "docker-compose.yml" build --no-cache

echo "Starting containers..."
docker compose -f "docker-compose.yml" up -d