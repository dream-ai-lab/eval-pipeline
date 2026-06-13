# One command to prove the standard end to end in Docker.
# Usage: .\run.ps1
$ErrorActionPreference = "Stop"
$env:GIT_COMMIT = (git rev-parse --short HEAD)
$compose = "docker/docker-compose.yml"

Write-Host "==> Building image + starting MLflow server" -ForegroundColor Cyan
docker compose -f $compose up -d --build mlflow

Write-Host "==> Reproduce SST-2" -ForegroundColor Cyan
docker compose -f $compose run --rm reproduce-sst2

Write-Host "==> Proposal SST-2 (forks baseline, logs delta)" -ForegroundColor Cyan
docker compose -f $compose run --rm proposal-sst2

Write-Host "==> Reproduce Emotion" -ForegroundColor Cyan
docker compose -f $compose run --rm reproduce-emotion

Write-Host "==> Done. MLflow UI: http://localhost:5000" -ForegroundColor Green
