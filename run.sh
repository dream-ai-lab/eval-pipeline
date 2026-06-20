#!/usr/bin/env bash
# One command to prove the standard end to end in Docker (Linux / macOS).
# Runs log to Weights & Biases. Set WANDB_API_KEY + WANDB_ENTITY to push to the
# team; otherwise `export WANDB_MODE=offline` to run without a network (the
# proposal step needs online W&B to fork its baseline).
# Usage: ./run.sh
set -euo pipefail

export GIT_COMMIT="$(git rev-parse --short HEAD)"
COMPOSE="docker/docker-compose.yml"

echo "==> Building image"
docker compose -f "$COMPOSE" build reproduce-sst2

echo "==> Reproduce SST-2"
docker compose -f "$COMPOSE" run --rm reproduce-sst2

echo "==> Proposal SST-2 (forks baseline, logs delta)"
docker compose -f "$COMPOSE" run --rm proposal-sst2

echo "==> Reproduce Emotion"
docker compose -f "$COMPOSE" run --rm reproduce-emotion

echo "==> Done. View runs at https://wandb.ai/${WANDB_ENTITY:-<entity>}/${WANDB_PROJECT:-eval-lib}"
