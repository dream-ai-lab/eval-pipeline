# 02 — Quickstart

## Option A — Docker (recommended, proves reproducibility)

From the repo root:

```powershell
.\run.ps1
```

This builds the pinned image, starts the MLflow server, then runs the two
reproduces and the proposal. Open http://localhost:5000 to compare runs.

Run the steps manually if you prefer:

```powershell
$env:GIT_COMMIT = (git rev-parse --short HEAD)
docker compose -f docker/docker-compose.yml up -d --build mlflow
docker compose -f docker/docker-compose.yml run --rm reproduce-sst2
docker compose -f docker/docker-compose.yml run --rm proposal-sst2
docker compose -f docker/docker-compose.yml run --rm reproduce-emotion
```

**Reproducibility check:** run `reproduce-sst2` twice — the accuracy is
identical because the dataset, model, and environment are all pinned.

## Option B — Local Python

```powershell
pip install torch==2.12.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location)
python experiments/distilbert-sst2/reproduce.py
```

By default this logs to a local `./mlruns` folder. To use a shared server:
`$env:MLFLOW_TRACKING_URI = "http://<server>:5000"`.

## Run the tests

```powershell
$env:PYTHONPATH = (Get-Location)
pytest tests/ -q
```
