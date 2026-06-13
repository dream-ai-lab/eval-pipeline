# eval-pipeline

A **shared evaluation standard** for the research group: one contract, one
metric library, one runner — so reproduce results are comparable, reusable,
and have a clear baseline for proposals.

This repo is both the standard *and* a worked proof of it: two papers are
reproduced end-to-end, and the whole thing runs in Docker so anyone gets the
same numbers on any machine.

![Eval-pipeline workflow](docs/workflow.svg)

## What's here

| Path | What it is |
|---|---|
| `eval_lib/` | Shared package: metrics (by name), spec validation, the MLflow runner |
| `paper-registry/` | One `eval_spec.yaml` per paper — the pinned contract |
| `experiments/` | Per-paper `reproduce.py` / `proposal.py` (you only write `model_fn`) |
| `templates/` + `tools/new_paper.py` | Scaffold a new paper in one command |
| `tools/search.py` | Find teammates' runs and dump their full config |
| `docker/` | `mlflow` server + pinned `runner` image |
| `tests/` + `.github/workflows/ci.yml` | Enforce the standard on every PR |
| `docs/` | Onboarding — start at [docs/01-overview.md](docs/01-overview.md) |

## Quickstart (Docker — proves reproducibility)

```bash
./run.sh        # Linux / macOS
```
```powershell
.\run.ps1       # Windows
```

Builds the image, starts MLflow, runs both reproduces + the proposal, then
open the MLflow UI at http://localhost:5000.

## Proven results

| Experiment | Metric | Result | Paper-reported | Target |
|---|---|---|---|---|
| reproduce `distilbert-sst2` | accuracy | **0.9106** | 0.913 | [0.90, 0.92] ✓ |
| proposal `distilbert-sst2` (ensemble) | accuracy | **0.9278** | — | delta **+0.017** |
| reproduce `distilbert-emotion` | macro-F1 | **0.9065** | — | [0.80, 0.95] ✓ |

## What it looks like

Every run records its full config + golden record, and proposals show the
auto-computed delta against the baseline:

| Reproduce run (full config) | Proposal run (auto delta) |
|---|---|
| ![reproduce run detail](screenshots/02_reproduce_run_detail.png) | ![proposal run detail](screenshots/03_proposal_run_detail.png) |

Compare reproduce vs proposal directly — no spreadsheet:

![compare runs](screenshots/04_compare_reproduce_vs_proposal.png)

## Find a teammate's result

```bash
export MLFLOW_TRACKING_URI=http://<server>:5000          # Linux/macOS
# $env:MLFLOW_TRACKING_URI = "http://<server>:5000"      # Windows PowerShell
python tools/search.py --role reproduce --filter "metrics.accuracy > 0.90"
python tools/search.py --run <run_id>   # full config: every param + the spec
```

See [docs/07-finding-results.md](docs/07-finding-results.md).

New here? Read [docs/02-quickstart.md](docs/02-quickstart.md) then
[docs/03-add-a-new-paper.md](docs/03-add-a-new-paper.md).
