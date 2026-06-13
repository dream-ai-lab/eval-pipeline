"""Capture MLflow UI screenshots with Playwright (for docs/demo)."""

import json
import os
import urllib.parse

import mlflow
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5000"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
os.environ.setdefault("MLFLOW_TRACKING_URI", BASE)


def exp_id(name):
    return mlflow.get_experiment_by_name(name).experiment_id


def latest(name, role):
    e = mlflow.get_experiment_by_name(name)
    df = mlflow.search_runs([e.experiment_id], f"tags.role = '{role}'",
                            order_by=["start_time DESC"], max_results=1)
    return df.iloc[0]["run_id"]


def main():
    os.makedirs(OUT, exist_ok=True)
    sst2, emo = exp_id("distilbert-sst2"), exp_id("distilbert-emotion")
    rep, prop = latest("distilbert-sst2", "reproduce"), latest("distilbert-sst2", "proposal")
    emorep = latest("distilbert-emotion", "reproduce")

    runs = urllib.parse.quote(json.dumps([rep, prop]))
    exps = urllib.parse.quote(json.dumps([str(sst2)]))
    compare = f"{BASE}/#/compare-runs?runs={runs}&experiments={exps}"

    shots = [
        (f"{BASE}/#/experiments/{sst2}", "01_sst2_runs_table"),
        (f"{BASE}/#/experiments/{sst2}/runs/{rep}", "02_reproduce_run_detail"),
        (f"{BASE}/#/experiments/{sst2}/runs/{prop}", "03_proposal_run_detail"),
        (compare, "04_compare_reproduce_vs_proposal"),
        (f"{BASE}/#/experiments/{emo}/runs/{emorep}", "05_emotion_run_detail"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1680, "height": 1050})
        for url, name in shots:
            page.goto(url, wait_until="load", timeout=30000)
            page.wait_for_timeout(3500)  # let the SPA + tables render
            path = os.path.join(OUT, name + ".png")
            page.screenshot(path=path, full_page=True)
            print("saved", os.path.relpath(path))
        browser.close()


if __name__ == "__main__":
    main()
