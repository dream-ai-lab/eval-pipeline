# 05 — Role workflows

## Survey member

Reads the paper, fills the contract. No code.

1. `python tools/new_paper.py <paper-id>`
2. Complete `paper-registry/<paper-id>/eval_spec.yaml`:
   - pin dataset + model to real HF commit SHAs
   - map the paper's reported metric to a name in `eval_lib/metrics.py`
   - record `paper_reported` with the exact `metric_variant`
   - set a sensible `reproduce_target` band
3. Open a PR. CI validates the spec.

## Experiment member

Reproduces the result.

1. Implement `model_fn(texts) -> list[int]` in
   `experiments/<paper-id>/reproduce.py`.
2. Run it (Docker or local). The runner logs the golden record to MLflow and
   checks `reproduce_target`.
3. If passed, record the run id + score in `baseline_registry.yaml`.

## Proposal member

Tries to beat the baseline.

1. Do **not** create a new paper or spec. Edit
   `experiments/<paper-id>/proposal.py` with your improved `model_fn`.
2. Run it. It auto-finds the latest accepted reproduce run, forks it
   (`role=proposal`, `parent_run_id=...`), and the runner logs
   `delta_<metric>` against the baseline.
3. Compare directly in the MLflow UI — no spreadsheet.

## Why this keeps numbers comparable

Everyone goes through the same `run_paper` path with the same metric library
and the same pinned spec. The only differences a proposal introduces are the
`role` tag and the `model_fn` — so the delta is honest.
