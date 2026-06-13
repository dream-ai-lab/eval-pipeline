"""TEMPLATE proposal script. Copy to experiments/<paper_id>/proposal.py.

A proposal reuses the paper's eval_spec, forks the baseline reproduce run in
MLflow, and the runner logs the delta automatically. Do NOT create a new
paper_id or spec for a proposal.
"""

import os
import random

import mlflow
import numpy as np
import torch

from eval_lib import load_spec, run_paper

SPEC = os.path.join(
    os.path.dirname(__file__), "..", "..", "paper-registry", "<paper-id>", "eval_spec.yaml"
)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_model_fn(spec):
    # TODO: build your improved model_fn(texts) -> list[int]
    raise NotImplementedError


def latest_reproduce_run(paper_id):
    exp = mlflow.get_experiment_by_name(paper_id)
    if exp is None:
        return None
    df = mlflow.search_runs(
        [exp.experiment_id],
        filter_string="tags.role = 'reproduce'",
        order_by=["start_time DESC"],
        max_results=1,
    )
    return None if len(df) == 0 else df.iloc[0]["run_id"]


def main():
    spec = load_spec(SPEC)
    set_seed(spec.inference.seed)
    parent = latest_reproduce_run(spec.paper_id)
    if parent is None:
        raise SystemExit("No baseline reproduce run found — run reproduce.py first.")
    result = run_paper(SPEC, build_model_fn(spec), role="proposal", parent_run_id=parent)
    print(f"[proposal] {spec.paper_id}: {result['results']} | forked={parent}")


if __name__ == "__main__":
    main()
