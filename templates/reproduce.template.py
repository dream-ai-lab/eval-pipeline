"""TEMPLATE reproduce script. Copy to experiments/<paper_id>/reproduce.py.

You only implement ``model_fn``: given a list of input texts, return a list
of predicted label ids aligned to the dataset's label_field. eval_lib does
the rest (data loading, metrics, MLflow logging, target check).
"""

import os
import random

import numpy as np
import torch
from transformers import pipeline

from eval_lib import load_spec, run_paper

SPEC = os.path.join(
    os.path.dirname(__file__), "..", "..", "paper-registry", "<paper-id>", "eval_spec.yaml"
)

# Map the model's output label strings to the dataset's label ids.
LABEL2ID = {}  # TODO: fill in


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_model_fn(spec):
    clf = pipeline(
        "text-classification",
        model=spec.model.hf_id,
        revision=spec.model.revision,
        device=-1,
    )

    def model_fn(texts):
        outs = clf(
            list(texts),
            batch_size=spec.inference.batch_size,
            truncation=True,
            max_length=spec.inference.max_length,
        )
        return [LABEL2ID[o["label"]] for o in outs]

    return model_fn


def main():
    spec = load_spec(SPEC)
    set_seed(spec.inference.seed)
    result = run_paper(SPEC, build_model_fn(spec), role="reproduce")
    print(f"[reproduce] {spec.paper_id}: {result['results']} | passed={result['reproduce_passed']}")


if __name__ == "__main__":
    main()
