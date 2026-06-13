"""Re-capture the classic runs table (needs the 'Model training' toggle)."""

import os

import mlflow
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5000"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
os.environ.setdefault("MLFLOW_TRACKING_URI", BASE)

sst2 = mlflow.get_experiment_by_name("distilbert-sst2").experiment_id

with sync_playwright() as p:
    page = p.chromium.launch().new_page(viewport={"width": 1680, "height": 1050})
    page.goto(f"{BASE}/#/experiments/{sst2}", wait_until="load", timeout=30000)
    page.wait_for_timeout(2000)
    # Dismiss the "Detect Issues" popover if present.
    try:
        page.get_by_role("button", name="Got it").click(timeout=3000)
    except Exception:
        pass
    # Switch from GenAI view to the classic Model-training runs table.
    try:
        page.get_by_text("Model training", exact=True).click(timeout=5000)
    except Exception:
        pass
    page.wait_for_timeout(3500)
    path = os.path.join(OUT, "01_sst2_runs_table.png")
    page.screenshot(path=path, full_page=True)
    print("saved", os.path.relpath(path))
