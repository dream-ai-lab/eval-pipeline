"""Scaffold a new paper from the templates.

    python tools/new_paper.py <paper-id>

Creates paper-registry/<paper-id>/eval_spec.yaml and
experiments/<paper-id>/{reproduce.py,proposal.py} from templates/, with the
paper id substituted. A newcomer fills the spec + model_fn and is done.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _write(dst: str, content: str) -> None:
    if os.path.exists(dst):
        raise SystemExit(f"refusing to overwrite existing file: {dst}")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"created {os.path.relpath(dst, ROOT)}")


def _read_template(name: str) -> str:
    with open(os.path.join(ROOT, "templates", name), "r", encoding="utf-8") as f:
        return f.read()


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python tools/new_paper.py <paper-id>")
    paper_id = sys.argv[1].strip()

    spec = _read_template("eval_spec.template.yaml").replace("<paper-id>", paper_id)
    reproduce = _read_template("reproduce.template.py").replace("<paper-id>", paper_id)
    proposal = _read_template("proposal.template.py").replace("<paper-id>", paper_id)

    _write(os.path.join(ROOT, "paper-registry", paper_id, "eval_spec.yaml"), spec)
    _write(os.path.join(ROOT, "experiments", paper_id, "reproduce.py"), reproduce)
    _write(os.path.join(ROOT, "experiments", paper_id, "proposal.py"), proposal)

    print(
        f"\nNext:\n  1. Fill paper-registry/{paper_id}/eval_spec.yaml (survey member)\n"
        f"  2. Implement model_fn in experiments/{paper_id}/reproduce.py\n"
        f"  3. python experiments/{paper_id}/reproduce.py"
    )


if __name__ == "__main__":
    main()
