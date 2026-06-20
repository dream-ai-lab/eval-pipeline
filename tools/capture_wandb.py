"""Capture W&B UI screenshots with Playwright (for docs/demo).

Resolves the latest runs via the W&B API, then screenshots their pages. Needs
online access (WANDB_ENTITY + a logged-in session or a public project) — set:

    export WANDB_ENTITY=dream-ai-lab
    export WANDB_PROJECT=eval-lib

Run after the experiments have logged to W&B. For a private project, the
headless browser must carry a logged-in session (see Playwright storage state).
"""

import os

import wandb
from playwright.sync_api import sync_playwright

ENTITY = os.environ.get("WANDB_ENTITY", "dream-ai-lab")
PROJECT = os.environ.get("WANDB_PROJECT", "eval-lib")
BASE = f"https://wandb.ai/{ENTITY}/{PROJECT}"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")


def latest(paper, role):
    runs = wandb.Api().runs(
        f"{ENTITY}/{PROJECT}",
        filters={"group": paper, "config.role": role},
        order="-created_at",
    )
    for r in runs:
        return r.id
    raise SystemExit(f"no {role} run for {paper} in {ENTITY}/{PROJECT}")


def main():
    os.makedirs(OUT, exist_ok=True)
    rep = latest("distilbert-sst2", "reproduce")
    prop = latest("distilbert-sst2", "proposal")
    emorep = latest("distilbert-emotion", "reproduce")

    shots = [
        (f"{BASE}/groups/distilbert-sst2", "01_sst2_runs_table"),
        (f"{BASE}/runs/{rep}", "02_reproduce_run_detail"),
        (f"{BASE}/runs/{prop}", "03_proposal_run_detail"),
        (f"{BASE}/runs/{prop}/overview", "04_compare_reproduce_vs_proposal"),
        (f"{BASE}/runs/{emorep}", "05_emotion_run_detail"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1680, "height": 1050})
        for url, name in shots:
            page.goto(url, wait_until="load", timeout=30000)
            page.wait_for_timeout(4000)  # let the SPA + charts render
            path = os.path.join(OUT, name + ".png")
            page.screenshot(path=path, full_page=True)
            print("saved", os.path.relpath(path))
        browser.close()


if __name__ == "__main__":
    main()
