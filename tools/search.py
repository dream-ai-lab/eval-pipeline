"""Search experiment results logged by the team and inspect their full config.

Connects to the MLflow server in MLFLOW_TRACKING_URI (defaults to the local
./mlruns store). Examples:

    # all runs for a paper (newest first)
    python tools/search.py --paper distilbert-sst2

    # only accepted reproduces that beat 0.92 accuracy
    python tools/search.py --paper distilbert-sst2 --role reproduce \
        --filter "metrics.accuracy > 0.90"

    # every config param + metric + tag for one run
    python tools/search.py --run d1309a87045b4a22b11353733975a1d3

Point at the shared server with:
    setx MLFLOW_TRACKING_URI http://<server>:5000   (or export on Linux)
"""

import argparse

import mlflow


def _dump_run(client, run_id: str) -> None:
    r = client.get_run(run_id)
    print(f"run_id: {run_id}")
    print(f"experiment: {client.get_experiment(r.info.experiment_id).name}")
    print(f"status: {r.info.status}\n")

    print("-- tags (golden record) --")
    for k in sorted(r.data.tags):
        if not k.startswith("mlflow."):
            print(f"  {k:22} = {r.data.tags[k]}")

    print("\n-- params (full config) --")
    for k in sorted(r.data.params):
        print(f"  {k:22} = {r.data.params[k]}")

    print("\n-- metrics --")
    for k in sorted(r.data.metrics):
        print(f"  {k:22} = {r.data.metrics[k]:.4f}")

    try:
        arts = [a.path for a in client.list_artifacts(run_id, "eval_spec")]
        if arts:
            print(f"\n-- artifacts -- (exact spec)\n  {', '.join(arts)}")
    except Exception as e:  # artifact store may be unreachable from a client
        print(f"\n-- artifacts -- (unavailable: {e})")


def _search(args) -> None:
    client = mlflow.MlflowClient()

    if args.paper:
        exp = mlflow.get_experiment_by_name(args.paper)
        if exp is None:
            raise SystemExit(f"no experiment named '{args.paper}'")
        exp_ids = [exp.experiment_id]
    else:
        exp_ids = [e.experiment_id for e in client.search_experiments()]

    clauses = []
    if args.role:
        clauses.append(f"tags.role = '{args.role}'")
    if args.filter:
        clauses.append(args.filter)
    filter_string = " and ".join(clauses)

    df = mlflow.search_runs(exp_ids, filter_string=filter_string, order_by=["start_time DESC"])
    if len(df) == 0:
        print("no matching runs")
        return

    cols = ["run_id", "tags.paper_id", "tags.role", "tags.reproduce_passed",
            "params.model.hf_id", "params.dataset.revision", "params.inference.seed"]
    metric_cols = [c for c in df.columns if c.startswith("metrics.") and not c.startswith("metrics.delta")]
    cols += metric_cols
    have = [c for c in cols if c in df.columns]

    print(f"{len(df)} run(s):\n")
    for _, row in df[have].iterrows():
        rid = row["run_id"]
        paper = row.get("tags.paper_id", "?")
        role = row.get("tags.role", "?")
        metrics = " ".join(
            f"{c.split('.', 1)[1]}={row[c]:.4f}" for c in metric_cols if c in row and row[c] == row[c]
        )
        print(f"  {rid}  [{paper}/{role}]  {metrics}")
    print(f"\nInspect full config:  python tools/search.py --run <run_id>")


def main():
    ap = argparse.ArgumentParser(description="Search team eval results in MLflow")
    ap.add_argument("--paper", help="paper_id (MLflow experiment)")
    ap.add_argument("--role", choices=["reproduce", "proposal"], help="filter by role")
    ap.add_argument("--filter", help="extra MLflow filter, e.g. \"metrics.accuracy > 0.92\"")
    ap.add_argument("--run", help="dump all params/metrics/tags for one run id")
    args = ap.parse_args()

    if args.run:
        _dump_run(mlflow.MlflowClient(), args.run)
    else:
        _search(args)


if __name__ == "__main__":
    main()
