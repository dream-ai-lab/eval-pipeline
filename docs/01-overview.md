# 01 — Overview

![Eval-pipeline workflow](workflow.svg)

## The problem

The group reproduces papers across many people. Without a shared contract:

1. **Metrics don't match** — everyone computes BLEU/F1/accuracy slightly
   differently, so numbers aren't comparable even for the same paper.
2. **Results aren't reusable** — after a reproduce, nobody knows which dataset
   version, config, or seed was used.
3. **No clear baseline** — a proposal has no anchor to measure improvement
   against.

## The standard, in three layers

**Layer 1 — Shared contract.** Each paper has an `eval_spec.yaml` (pinned
dataset + model + metric library version) in `paper-registry/`. Metrics live
only in `eval_lib/metrics.py`. The accepted reproduce run is recorded in
`baseline_registry.yaml`.

**Layer 2 — Role workflows.** A *survey* member fills the spec. An *experiment*
member writes a `model_fn` and runs the standard runner. A *proposal* member
forks the baseline run and the delta is computed automatically. See
[05-roles.md](05-roles.md).

**Layer 3 — Unified tooling.** One runner (`eval_lib.run_paper`) logs the same
golden record for every run to a shared MLflow server. Docker pins the
environment. CI validates every spec.

## Repo layout (how the layers map to repos)

![Repo pipeline & data flow](pipeline.svg)

## How a run flows

```
eval_spec.yaml ─▶ load + validate + hash ─▶ load pinned dataset
                                              │
            your model_fn(texts) ─▶ preds ────┤
                                              ▼
                 metric_lib.evaluate(by name) ─▶ MLflow run
                   (paper_id, git_commit, hf_dataset_id,
                    eval_spec_hash, metric_lib_version,
                    metrics, reproduce_passed)
```

## The golden record (logged every run)

Five required fields make any run traceable and comparable:
`paper_id`, `git_commit`, `hf_dataset_id` (with version), `eval_spec_hash`,
`metric_lib_version`. The model id+revision and all metrics are logged too.
