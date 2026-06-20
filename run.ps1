# One command to prove the standard end to end in Docker.
# Runs log to Weights & Biases. Set WANDB_API_KEY + WANDB_ENTITY to push to the
# team; otherwise set WANDB_MODE=offline to run without a network (the proposal
# step needs online W&B to fork its baseline).
# Usage: .\run.ps1
$ErrorActionPreference = "Stop"
$env:GIT_COMMIT = (git rev-parse --short HEAD)
$compose = "docker/docker-compose.yml"

Write-Host "==> Building image" -ForegroundColor Cyan
docker compose -f $compose build reproduce-sst2

Write-Host "==> Reproduce SST-2" -ForegroundColor Cyan
docker compose -f $compose run --rm reproduce-sst2

Write-Host "==> Proposal SST-2 (forks baseline, logs delta)" -ForegroundColor Cyan
docker compose -f $compose run --rm proposal-sst2

Write-Host "==> Reproduce Emotion" -ForegroundColor Cyan
docker compose -f $compose run --rm reproduce-emotion

$entity = if ($env:WANDB_ENTITY) { $env:WANDB_ENTITY } else { "<entity>" }
$project = if ($env:WANDB_PROJECT) { $env:WANDB_PROJECT } else { "eval-lib" }
Write-Host "==> Done. View runs at https://wandb.ai/$entity/$project" -ForegroundColor Green
