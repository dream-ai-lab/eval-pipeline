# 03 — Add a new paper

A new paper gets its **own repo**, created from the template. You never PR
experiment code into a central repo. ~15 minutes.

## 1. Create the repo from the template

Click **“Use this template”** on
[experiment-template](https://github.com/dream-ai-lab/experiment-template), or:

```bash
gh repo create dream-ai-lab/reproduce-<paper-id> \
  --template dream-ai-lab/experiment-template --public --clone
```

It ships a working SST-2 example and is already wired to a pinned `eval-lib`.

## 2. Register + fill the spec (survey member)

Add `eval_spec.yaml` to the
[paper-registry](https://github.com/dream-ai-lab/paper-registry) (PR) and copy
it into your repo. Every `<...>` must be replaced — field help in
[04-eval-spec-reference.md](04-eval-spec-reference.md).

Get the **real** HF commit SHAs (never `main`):

```bash
# Linux / macOS
curl -s https://huggingface.co/api/models/<org/model>   | python -c "import sys,json;print(json.load(sys.stdin)['sha'])"
curl -s https://huggingface.co/api/datasets/<org/dataset> | python -c "import sys,json;print(json.load(sys.stdin)['sha'])"
```
```powershell
# Windows PowerShell
(Invoke-RestMethod "https://huggingface.co/api/models/<org/model>").sha
(Invoke-RestMethod "https://huggingface.co/api/datasets/<org/dataset>").sha
```

`metrics.primary` / `secondary` must already exist in `eval-lib`. Need a new
metric? PR it to [eval-lib](https://github.com/dream-ai-lab/eval-lib) first and
bump its version (see [06-standard.md](06-standard.md)) — never write a one-off.

## 3. Implement `model_fn` (experiment member)

In `reproduce.py`, fill `LABEL2ID` (model label string → dataset label id) and,
if the task isn't text-classification, the body of `model_fn`. The contract is
simply: **`model_fn(texts) -> list[int]`** aligned to the dataset's
`label_field`.

## 4. Run

```bash
pip install -r requirements.txt    # pulls eval-lib (pinned) + torch + transformers
python reproduce.py
```

If `target_passed=True`, record the run in the registry's
`baseline_registry.yaml` (PR). Log to the shared server with
`MLFLOW_TRACKING_URI=http://<server>:5000`.

## 5. CI

Your repo's CI installs the pinned `eval-lib` and validates `eval_spec.yaml`
automatically on every push — no central PR for the experiment itself.
