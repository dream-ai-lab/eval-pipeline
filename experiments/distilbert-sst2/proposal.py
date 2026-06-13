"""A proposal on top of the SST-2 reproduce baseline.

Demonstrates the proposal workflow: it does NOT create a new paper or
spec — it reuses the same eval_spec, forks the baseline reproduce run in
MLflow (role=proposal, parent_run_id), and the runner logs the delta
automatically. The "improvement" here is a probability-average ensemble of
the distilled model with a stronger RoBERTa SST-2 checkpoint.
"""

import os
import random

import mlflow
import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from eval_lib import load_spec, run_paper

SPEC = os.path.join(
    os.path.dirname(__file__), "..", "..", "paper-registry", "distilbert-sst2", "eval_spec.yaml"
)

# Both checkpoints use index 0 = negative, 1 = positive, so we can average
# their probabilities directly by index.
ENSEMBLE = [
    ("distilbert-base-uncased-finetuned-sst-2-english", "714eb0fa89d2f80546fda750413ed43d93601a13"),
    ("textattack/roberta-base-SST-2", "84ee248b91053ef5d0c748bbac4edfba1cf89584"),
]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _load(hf_id, revision):
    tok = AutoTokenizer.from_pretrained(hf_id, revision=revision)
    model = AutoModelForSequenceClassification.from_pretrained(hf_id, revision=revision)
    model.eval()
    return tok, model


def build_model_fn(spec):
    members = [_load(hf_id, rev) for hf_id, rev in ENSEMBLE]
    bs = spec.inference.batch_size
    max_len = spec.inference.max_length

    @torch.no_grad()
    def model_fn(texts):
        texts = list(texts)
        preds = []
        for i in range(0, len(texts), bs):
            batch = texts[i : i + bs]
            avg_probs = None
            for tok, model in members:
                enc = tok(batch, padding=True, truncation=True, max_length=max_len, return_tensors="pt")
                probs = torch.softmax(model(**enc).logits, dim=-1)
                avg_probs = probs if avg_probs is None else avg_probs + probs
            preds.extend(torch.argmax(avg_probs, dim=-1).tolist())
        return preds

    return model_fn


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
    print(
        f"[proposal] {spec.paper_id}: {result['results']} "
        f"| forked baseline={parent} | run_id={result['run_id']}"
    )


if __name__ == "__main__":
    main()
