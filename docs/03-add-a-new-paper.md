# 03 — Add a new paper

A new paper is a copy-the-template-and-fill-`model_fn` job. ~15 minutes.

## 1. Scaffold

```powershell
python tools/new_paper.py my-paper-id
```

Creates:
- `paper-registry/my-paper-id/eval_spec.yaml`
- `experiments/my-paper-id/reproduce.py`
- `experiments/my-paper-id/proposal.py`

## 2. Fill the spec (survey member)

Edit `paper-registry/my-paper-id/eval_spec.yaml`. Every `<...>` must be
replaced. Field-by-field help: [04-eval-spec-reference.md](04-eval-spec-reference.md).

Get the **real** HF commit SHAs (never `main`):

```powershell
(Invoke-RestMethod "https://huggingface.co/api/models/<org/model>").sha
(Invoke-RestMethod "https://huggingface.co/api/datasets/<org/dataset>").sha
```

`metrics.primary` / `secondary` must already exist in `eval_lib/metrics.py`.
Need a new metric? Add it there first (see [06-standard.md](06-standard.md)) —
never write a one-off eval function.

## 3. Implement `model_fn` (experiment member)

In `reproduce.py`, fill `LABEL2ID` (model label string → dataset label id) and,
if the task isn't text-classification, the body of `model_fn`. The contract is
simply: **`model_fn(texts) -> list[int]`** aligned to the dataset's
`label_field`.

## 4. Run

```powershell
$env:PYTHONPATH = (Get-Location)
python experiments/my-paper-id/reproduce.py
```

If `target_passed=True`, record the run in `paper-registry/baseline_registry.yaml`.

## 5. Validate before pushing

```powershell
pytest tests/ -q     # validates your new spec too
```

CI runs the same check on your PR.
