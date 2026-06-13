#!/usr/bin/env bash
# One command to prove the standard end to end in Docker (Linux / macOS).
# Usage: ./run.sh
set -euo pipefail

export GIT_COMMIT="$(git rev-parse --short HEAD)"
COMPOSE="docker/docker-compose.yml"

echo "==> Building image + starting MLflow server"
docker compose -f "$COMPOSE" up -d --build mlflow

echo "==> Reproduce SST-2"
docker compose -f "$COMPOSE" run --rm reproduce-sst2

echo "==> Proposal SST-2 (forks baseline, logs delta)"
docker compose -f "$COMPOSE" run --rm proposal-sst2

echo "==> Reproduce Emotion"
docker compose -f "$COMPOSE" run --rm reproduce-emotion

echo "==> Done. MLflow UI: http://localhost:5000"
