# 06 — The coding standard

The rules that make this a standard rather than a convention. CI enforces the
mechanical ones; the rest are review norms.

## Rules

1. **Never write a one-off eval function.** Metrics live only in
   `eval_lib/metrics.py`, used by name from the spec. New metric → add it there
   (with a unit test) and bump `metric_lib_version`.
2. **Pin everything.** Dataset and model must reference a real HF commit SHA,
   never `main`/`latest`. The spec is rejected otherwise.
3. **Specs are immutable once a run exists.** To change a spec, bump
   `spec_version` — don't silently edit a spec other runs were measured against.
4. **Log the full golden record.** Every run logs `paper_id`, `git_commit`,
   `hf_dataset_id`, `eval_spec_hash`, `metric_lib_version` (the runner does this
   for you — don't bypass `run_paper`).
5. **Proposals fork, never fork the paper.** Reuse the spec; add `proposal.py`.
6. **Run in the pinned environment.** Use the Docker image (or the pinned
   `requirements.txt`) so scores are environment-independent.

## Where specs live (when to register in paper-registry)

- **Always required:** every run has a *valid* `eval_spec.yaml` — `run_paper`
  logs its `eval_spec_hash` + the file as an artifact. Comparability comes from
  the hash, not the file's location.
- **Register in [paper-registry](https://github.com/dream-ai-lab/paper-registry)
  (policy):** for any shared/official paper, or before a result becomes a
  baseline — so there is one reviewed, discoverable contract per `paper_id`.
- **Skip registering:** quick/personal/throwaway experiments — keep the spec in
  your own repo; the run is still valid.

Full policy: [paper-registry README](https://github.com/dream-ai-lab/paper-registry#when-must-a-spec-be-registered-here).

## What CI checks

- `eval_lib/metrics.py` behaves (known inputs → known scores).
- The canonical spec hash is order/whitespace independent.
- **Every** `eval_spec.yaml` in `paper-registry/` is valid: pinned dataset +
  model, known metrics, required fields present.

A PR that breaks any of these fails the build — that is what turns "we agreed
to do X" into an enforced standard.

## Adding a metric

```python
# eval_lib/metrics.py
@register("my_metric")
def my_metric(preds, refs) -> float:
    ...
```

Add a test in `tests/test_metrics.py`, bump `eval_lib/version.py`, done. It is
now usable from any spec by name.
