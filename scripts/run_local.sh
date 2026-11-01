#!/usr/bin/env bash
set -e
if [ ! -f .env ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
fi
echo "Starting CFIC API on http://localhost:8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
