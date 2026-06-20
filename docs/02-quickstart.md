# 02 — Quickstart

Clone with the submodule (the spec catalog):

```bash
git clone --recursive https://github.com/dream-ai-lab/eval-pipeline
# already cloned? git submodule update --init
```

## Option A — Docker (recommended, proves reproducibility)

From the repo root:

```bash
./run.sh          # Linux / macOS
```
```powershell
.\run.ps1         # Windows
```

This builds the pinned image, then runs the two reproduces and the proposal.
Open `https://wandb.ai/<entity>/<project>` to compare runs.

Run the steps manually if you prefer:

```bash
# Linux / macOS
export GIT_COMMIT="$(git rev-parse --short HEAD)"
docker compose -f docker/docker-compose.yml run --rm reproduce-sst2
docker compose -f docker/docker-compose.yml run --rm proposal-sst2
docker compose -f docker/docker-compose.yml run --rm reproduce-emotion
```
```powershell
# Windows PowerShell
$env:GIT_COMMIT = (git rev-parse --short HEAD)
docker compose -f docker/docker-compose.yml run --rm reproduce-sst2
docker compose -f docker/docker-compose.yml run --rm proposal-sst2
docker compose -f docker/docker-compose.yml run --rm reproduce-emotion
```

**Reproducibility check:** run `reproduce-sst2` twice — the accuracy is
identical because the dataset, model, and environment are all pinned.

## Option B — Local Python

`requirements.txt` installs the pinned `eval-lib` (no `PYTHONPATH` needed):

```bash
pip install -r requirements.txt
python experiments/distilbert-sst2/reproduce.py
```

By default this logs to W&B using `WANDB_ENTITY` (team) and `WANDB_PROJECT`
(defaults to `eval-lib`). Authenticate once with `wandb login` or set
`WANDB_API_KEY`. To run offline without a network connection, set
`WANDB_MODE=offline` and run `wandb sync` afterwards.

## Validate the registry specs

```bash
pip install "git+https://github.com/dream-ai-lab/eval-lib@v0.1.0"
cd paper-registry && python validate.py
```

(`eval_lib`'s own unit tests live in the
[eval-lib](https://github.com/dream-ai-lab/eval-lib) repo.)
