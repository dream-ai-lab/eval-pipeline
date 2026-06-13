"""The standard eval runner.

Every experiment goes through ``run_paper``. It loads the pinned dataset,
runs the caller's ``model_fn``, computes metrics from the shared library,
and logs the golden record to MLflow. Reproduce and proposal runs use the
SAME path — the only difference is the ``role`` tag and an optional parent
run id — which is what makes deltas comparable.
"""

from __future__ import annotations

import os
import subprocess
from typing import Callable, Sequence

import mlflow

from . import metrics, version
from .data import load_eval_split
from .spec import load_spec, metric_names

# model_fn takes the list of input texts and returns predicted labels.
ModelFn = Callable[[Sequence[str]], Sequence[int]]


def _git_commit() -> str:
    # In a container the source is COPYied without .git; the build passes the
    # commit through GIT_COMMIT so the golden record stays accurate.
    env = os.environ.get("GIT_COMMIT")
    if env:
        return env
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        )
        return out.strip()
    except Exception:
        return "unknown"


def check_target(results: dict, target) -> bool:
    """True iff every metric in ``reproduce_target`` lands within [min, max]."""
    target = target or {}
    for name, rng in vars(target).items() if hasattr(target, "__dict__") else target.items():
        rng = vars(rng) if hasattr(rng, "__dict__") else rng
        v = results.get(name)
        if v is None or not (rng["min"] <= v <= rng["max"]):
            return False
    return True


def run_paper(
    spec_path: str,
    model_fn: ModelFn,
    role: str = "reproduce",
    parent_run_id: str | None = None,
    run_name: str | None = None,
) -> dict:
    """Validate spec → load data → run model → log golden record to MLflow.

    Returns ``{run_id, results, reproduce_passed}``.
    """
    spec = load_spec(spec_path)
    names = metric_names(spec)

    texts, refs = load_eval_split(spec)
    preds = list(model_fn(texts))
    if len(preds) != len(refs):
        raise ValueError(f"model_fn returned {len(preds)} preds for {len(refs)} examples")

    results = metrics.evaluate(preds, refs, names)
    passed = check_target(results, spec.reproduce_target)

    # The five required golden-record fields (logged as params AND tags so
    # they show up both in run detail and in filterable search).
    golden = {
        "paper_id": spec.paper_id,
        "git_commit": _git_commit(),
        "hf_dataset_id": f"{spec.dataset.hf_id}@{spec.dataset.version}",
        "eval_spec_hash": spec.hash,
        "metric_lib_version": version.__version__,
    }

    mlflow.set_experiment(spec.paper_id)
    with mlflow.start_run(run_name=run_name or f"{role}-{spec.paper_id}") as active:
        mlflow.log_params(golden)
        mlflow.log_param("hf_model_id", f"{spec.model.hf_id}@{spec.model.revision}")
        mlflow.set_tags(
            {
                **golden,
                "role": role,
                "reproduce_passed": str(passed),
            }
        )
        if parent_run_id:
            mlflow.set_tag("parent_run_id", parent_run_id)
        mlflow.log_metrics(results)

        # For a proposal, log the delta vs the baseline (parent) run.
        if role == "proposal" and parent_run_id:
            base = mlflow.get_run(parent_run_id).data.metrics
            for k, v in results.items():
                if k in base:
                    mlflow.log_metric(f"delta_{k}", v - base[k])

        run_id = active.info.run_id

    return {"run_id": run_id, "results": results, "reproduce_passed": passed}
