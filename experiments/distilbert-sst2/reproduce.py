"""Reproduce DistilBERT's SST-2 result by evaluating the released checkpoint.

This is the EXPERIMENT-member side of the contract: you only write
``model_fn`` (text -> predicted label). Everything else — dataset loading,
metrics, MLflow logging, the reproduce-target check — is handled by
eval_lib so every paper is run the exact same way.
"""

import os
import random

import numpy as np
import torch
from transformers import pipeline

from eval_lib import load_spec, run_paper

SPEC = os.path.join(
    os.path.dirname(__file__), "..", "..", "paper-registry", "distilbert-sst2", "eval_spec.yaml"
)

# distilbert-sst2 emits these label strings; map to dataset label ids.
LABEL2ID = {"NEGATIVE": 0, "POSITIVE": 1}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_model_fn(spec):
    clf = pipeline(
        "text-classification",
        model=spec.model.hf_id,
        revision=spec.model.revision,
        device=-1,  # CPU — deterministic and portable
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
    print(
        f"[reproduce] {spec.paper_id}: {result['results']} "
        f"| target_passed={result['reproduce_passed']} | run_id={result['run_id']}"
    )


if __name__ == "__main__":
    main()
