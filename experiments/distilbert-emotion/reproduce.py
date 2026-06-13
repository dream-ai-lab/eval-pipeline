"""Reproduce DistilBERT-emotion via the same standard runner.

Identical structure to the SST-2 experiment — only ``model_fn`` and the
label mapping differ. That sameness is the point: the standard makes a new
paper a copy-the-template-and-fill-model_fn job.
"""

import os
import random

import numpy as np
import torch
from transformers import pipeline

from eval_lib import load_spec, run_paper

SPEC = os.path.join(
    os.path.dirname(__file__), "..", "..", "paper-registry", "distilbert-emotion", "eval_spec.yaml"
)

# Model emits emotion names; dataset uses these ids (same ordering).
EMO2ID = {"sadness": 0, "joy": 1, "love": 2, "anger": 3, "fear": 4, "surprise": 5}


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
        return [EMO2ID[o["label"]] for o in outs]

    return model_fn


def main():
    spec = load_spec(SPEC)
    set_seed(spec.inference.seed)
    result = run_paper(SPEC, build_model_fn(spec), role="reproduce")
    print(
        f"[reproduce] {spec.paper_id}: {result['results']} "
        f"| target_passed={result['reproduce_passed']} | run_id={result['run_id']}"
    )


if __name__ == "__main__":
    main()
