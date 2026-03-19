#!/usr/bin/env -S just

set dotenv-load := true

help:
    @just --list

# Start development server locally
dev:
    uv run python -m brieffenster_generator.app

# Start with Docker
docker-up:
    docker compose up --build

# Format and lint code
format:
    uv run ruff check --fix
    uv run ruff format

# Run all checks
check:
    uv run ruff check
    uv run ruff format --check
