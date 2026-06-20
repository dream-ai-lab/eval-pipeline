"""Search experiment results logged by the team and inspect their full config.

Reads from Weights & Biases via the public API. Target the team's entity/project
with the environment:

    export WANDB_ENTITY=dream-ai-lab     # the team
    export WANDB_PROJECT=eval-lib        # optional; defaults to "eval-lib"
    wandb login                          # or set WANDB_API_KEY

Examples:

    # all runs for a paper (newest first) — runs are grouped by paper_id
    python tools/search.py --paper distilbert-sst2

    # only reproduces that beat 0.90 accuracy
    python tools/search.py --paper distilbert-sst2 --role reproduce \
        --filter "accuracy > 0.90"

    # every config field + metric + file for one run
    python tools/search.py --run d1309a87
"""

import argparse
import os

import wandb

_OPS = {">": "$gt", ">=": "$gte", "<": "$lt", "<=": "$lte", "==": "$eq", "=": "$eq"}


def _project_path() -> str:
    """``entity/project`` (or just ``project`` if no entity is set)."""
    project = os.environ.get("WANDB_PROJECT", "eval-lib")
    entity = os.environ.get("WANDB_ENTITY")
    return f"{entity}/{project}" if entity else project


def _parse_filter(expr: str):
    """Parse ``metric OP value`` (e.g. ``accuracy > 0.90``) into a W&B filter."""
    for sym in (">=", "<=", "==", ">", "<", "="):
        if sym in expr:
            key, val = expr.split(sym, 1)
            return f"summary_metrics.{key.strip()}", {_OPS[sym]: float(val)}
    raise SystemExit(f"bad --filter {expr!r}; use e.g. \"accuracy > 0.90\"")


def _metrics(summary) -> dict:
    """Numeric, non-internal entries from a run summary (W&B prefixes its own
    bookkeeping keys with '_')."""
    out = {}
    for k in summary.keys():
        if k.startswith("_"):
            continue
        v = summary[k]
        if isinstance(v, (int, float)):
            out[k] = v
    return out


def _dump_run(api, run_id: str) -> None:
    r = api.run(f"{_project_path()}/{run_id}")
    print(f"run_id: {r.id}")
    print(f"name: {r.name}   paper(group): {r.group}   job_type: {r.job_type}   state: {r.state}\n")

    print("-- config (golden record + full config) --")
    for k in sorted(r.config):
        print(f"  {k:24} = {r.config[k]}")

    metrics = _metrics(r.summary)
    print("\n-- metrics --")
    for k in sorted(metrics):
        print(f"  {k:24} = {metrics[k]:.4f}" if isinstance(metrics[k], float) else f"  {k:24} = {metrics[k]}")

    print("\n-- files -- (incl. the exact eval_spec)")
    try:
        names = [f.name for f in r.files() if "eval_spec" in f.name or f.name.endswith(".yaml")]
        print("  " + (", ".join(names) if names else "(none)"))
    except Exception as e:  # the run's files may be unreachable
        print(f"  (unavailable: {e})")


def _search(args) -> None:
    api = wandb.Api()

    filters = {}
    if args.paper:
        filters["group"] = args.paper
    if args.role:
        filters["config.role"] = args.role
    if args.filter:
        key, cond = _parse_filter(args.filter)
        filters[key] = cond

    runs = api.runs(_project_path(), filters=filters or None, order="-created_at")
    runs = list(runs)
    if not runs:
        print("no matching runs")
        return

    print(f"{len(runs)} run(s):\n")
    for r in runs:
        paper = r.group or r.config.get("paper_id", "?")
        role = r.config.get("role", r.job_type or "?")
        tier = r.config.get("eval_tier", "?")
        metrics = " ".join(
            f"{k}={v:.4f}" for k, v in sorted(_metrics(r.summary).items()) if not k.startswith("delta_")
        )
        print(f"  {r.id}  [{paper}/{role}/{tier}]  {metrics}")
    print("\nInspect full config:  python tools/search.py --run <run_id>")


def main():
    ap = argparse.ArgumentParser(description="Search team eval results in Weights & Biases")
    ap.add_argument("--paper", help="paper_id (W&B run group)")
    ap.add_argument("--role", choices=["reproduce", "proposal"], help="filter by role")
    ap.add_argument("--filter", help='metric threshold, e.g. "accuracy > 0.90"')
    ap.add_argument("--run", help="dump all config/metrics/files for one run id")
    args = ap.parse_args()

    if args.run:
        _dump_run(wandb.Api(), args.run)
    else:
        _search(args)


if __name__ == "__main__":
    main()
