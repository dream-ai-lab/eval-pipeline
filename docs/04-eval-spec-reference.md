# 04 — eval_spec.yaml reference

The spec is the pinned contract for a paper. It is validated by
`eval_lib/spec.py` (locally and in CI). Once a run exists against a spec, treat
it as **immutable** — bump `spec_version` instead of editing in place.

| Field | Required | Notes |
|---|---|---|
| `spec_version` | yes | Bump on any change after a run exists |
| `paper_id` | yes | kebab-case, unique; also the MLflow experiment name |
| `task` | yes | Free-text task name |
| `metric_lib_version` | yes | Pins the metric code; bump when metrics change |
| `dataset.hf_id` | yes | HF dataset repo |
| `dataset.config` | no | HF config name, or `null` |
| `dataset.split` | yes | e.g. `validation`, `test` |
| `dataset.version` | yes | Human pin recorded in the golden record; not `latest` |
| `dataset.revision` | yes | **Real HF commit SHA** — what is actually loaded; not `main` |
| `dataset.text_field` | yes | Input column |
| `dataset.label_field` | yes | Gold label column |
| `model.hf_id` | yes | HF model repo |
| `model.revision` | yes | **Real HF commit SHA**; not `main` |
| `inference.seed` | yes | Seeds python/numpy/torch |
| `inference.max_length` | yes | Truncation length (affects the score) |
| `inference.batch_size` | yes | Eval batch size |
| `metrics.primary` | yes | Must exist in `eval_lib/metrics.py` |
| `metrics.secondary` | no | List; all must exist in metric_lib |
| `baseline_scores.paper_reported` | yes | `value` + exact `metric_variant` + `source` |
| `baseline_scores.our_reproduce` | yes | `value: null` — recorded in MLflow, not hand-edited |
| `reproduce_target.<metric>` | yes | `{min, max}` acceptance band for the primary metric |

## Why two separate baseline scores?

`paper_reported` and `our_reproduce` are kept apart with an explicit
`metric_variant` because the paper may use a different tokenisation/variant
(e.g. tokenised BLEU vs sacreBLEU). Comparing across variants silently is how
"comparable" numbers stop being comparable.

## Validation rules (enforced)

- dataset `version` pinned (not empty / `latest`)
- dataset and model `revision` pinned (not empty / `main`)
- every referenced metric exists in `eval_lib/metrics.py`
- `reproduce_target` entries are `{min, max}`
