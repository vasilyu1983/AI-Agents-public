#!/usr/bin/env python3
"""Layer 3 — eval-gated promotion of a consolidated principle into skill logic.

The gap this closes: moving a load-bearing entry from learnings.consolidated.md
into the host skill's references/ (consolidation-protocol.md step 5) was a pure
human judgment call with NO objective backstop. This script makes that promotion
*gated*: a principle cannot be promoted unless it has a registered regression
eval that is DISCRIMINATING — it passes with the principle applied AND fails
without it. An eval that cannot fail when the principle is reverted is invalid
(coding-behavior Rule 9).

This script NEVER edits the host skill's SKILL.md or references/. Like
consolidate.py, promotion-out stays a human edit. The gate only decides whether
the human is *allowed* to do it, and prints the exact edit on a pass.

Eval cases live in <skill_dir>/promotion-evals/<slug>.json. Schema and authoring
protocol: references/promotion-protocol.md.

Modes:
  --audit                run every registered eval; one line each; non-zero exit
                         if any is not discriminating (use this in a PR check)
  --check <eval.json>    validate + run one eval verbosely
  --gate "<principle>"   the gate: find the eval for this principle, run it,
                         print the exact manual edit on pass, refuse on fail

Grading is deterministic by default (zero model cost, capability-agnostic).
Set PROMOTION_EVAL_CMD to a command that reads a prompt on stdin and prints
PASS or FAIL to use model grading for grader=="model" cases.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

EVAL_DIR_NAME = "promotion-evals"
LEDGER_NAME = "learnings.promotions.jsonl"
REQUIRED_KEYS = ("skill", "principle", "scenario", "grader", "assertion", "samples")
ASSERT_TYPES = ("contains", "not_contains", "regex", "equals", "json_path")


def die(msg: str, code: int = 1) -> None:
    print(f"promote_learning: {msg}", file=sys.stderr)
    sys.exit(code)


def _apply_assertion(assertion: dict, sample: str) -> bool:
    """Deterministic [Rule 5]. True iff `sample` satisfies `assertion`."""
    a_type = assertion.get("type")
    pattern = assertion.get("pattern", "")
    if a_type == "contains":
        return pattern in sample
    if a_type == "not_contains":
        return pattern not in sample
    if a_type == "regex":
        return re.search(pattern, sample) is not None
    if a_type == "equals":
        return sample.strip() == str(pattern).strip()
    if a_type == "json_path":
        # pattern = "a.b.c==expected" — dotted path on a JSON sample
        path, _, expected = pattern.partition("==")
        try:
            cur = json.loads(sample)
            for key in path.split("."):
                cur = cur[key] if key else cur
        except Exception:
            return False
        return str(cur).strip() == expected.strip()
    die(f"unknown assertion type: {a_type!r} (allowed: {', '.join(ASSERT_TYPES)})")
    return False  # unreachable


def _model_grade(eval_obj: dict, sample: str) -> bool:
    cmd = os.environ.get("PROMOTION_EVAL_CMD")
    if not cmd:
        die(
            f"eval {eval_obj['skill']!r} declares grader='model' but "
            "PROMOTION_EVAL_CMD is unset. Refusing to silently pass "
            "(fail loud). Set it or change the eval to a deterministic grader."
        )
    prompt = (
        "You are grading whether a skill behavior sample honors a principle.\n"
        f"PRINCIPLE: {eval_obj['principle']}\n"
        f"SCENARIO: {eval_obj['scenario']}\n"
        f"SAMPLE:\n{sample}\n\n"
        "Output exactly PASS if the sample honors the principle, else FAIL."
    )
    try:
        out = subprocess.run(
            ["bash", "-c", cmd], input=prompt,
            capture_output=True, text=True, timeout=120,
        ).stdout.strip().upper()
    except Exception as e:  # fail loud, never silent-pass
        die(f"PROMOTION_EVAL_CMD failed for {eval_obj['skill']!r}: {e!r}")
        return False
    return out.startswith("PASS")


def grade(eval_obj: dict, sample: str) -> bool:
    if eval_obj.get("grader") == "model":
        return _model_grade(eval_obj, sample)
    return _apply_assertion(eval_obj["assertion"], sample)


def validate(eval_obj: dict, path: Path) -> None:
    for k in REQUIRED_KEYS:
        if k not in eval_obj:
            die(f"{path.name}: missing required key {k!r}")
    if not str(eval_obj["principle"]).strip():
        die(f"{path.name}: empty principle")
    samples = eval_obj["samples"]
    if "with_principle" not in samples or "without_principle" not in samples:
        die(f"{path.name}: samples must have with_principle AND without_principle")
    if eval_obj["grader"] not in ("deterministic", "model"):
        die(f"{path.name}: grader must be 'deterministic' or 'model'")
    if eval_obj["grader"] == "deterministic":
        if eval_obj["assertion"].get("type") not in ASSERT_TYPES:
            die(f"{path.name}: assertion.type must be one of {ASSERT_TYPES}")


def run_one(path: Path) -> tuple[bool, str]:
    """Returns (discriminating, detail). Discriminating == gate may open."""
    try:
        eval_obj = json.loads(path.read_text())
    except Exception as e:
        return False, f"unparseable JSON: {e!r}"
    validate(eval_obj, path)
    s = eval_obj["samples"]
    with_pass = grade(eval_obj, s["with_principle"])
    without_pass = grade(eval_obj, s["without_principle"])
    # Discriminating = passes WITH the principle, fails WITHOUT it.
    discriminating = with_pass and not without_pass
    if discriminating:
        return True, "discriminating (with=PASS, without=FAIL)"
    if with_pass and without_pass:
        return False, "NON-FALSIFIABLE: passes even without the principle"
    if not with_pass and not without_pass:
        return False, "BROKEN: fails even with the principle applied"
    return False, "INVERTED: fails with, passes without"


def find_eval_for(skill_dir: Path, principle: str) -> Path | None:
    eval_dir = skill_dir / EVAL_DIR_NAME
    if not eval_dir.is_dir():
        return None
    norm = " ".join(principle.lower().split())
    for f in sorted(eval_dir.glob("*.json")):
        try:
            obj = json.loads(f.read_text())
        except Exception:
            continue
        if " ".join(str(obj.get("principle", "")).lower().split()) == norm:
            return f
    return None


def ledger_append(skill_dir: Path, principle: str, eval_file: str) -> None:
    line = json.dumps({
        "date": _dt.date.today().isoformat(),
        "skill": skill_dir.name,
        "principle": principle,
        "eval": eval_file,
        "gate": "passed",
    })
    with (skill_dir / LEDGER_NAME).open("a") as fh:
        fh.write(line + "\n")


def cmd_audit(skill_dir: Path) -> int:
    eval_dir = skill_dir / EVAL_DIR_NAME
    files = sorted(eval_dir.glob("*.json")) if eval_dir.is_dir() else []
    if not files:
        print(f"{skill_dir.name}  promotion-evals=0  status=none")
        return 0  # no evals registered is not itself a failure
    bad = 0
    for f in files:
        ok, detail = run_one(f)
        flag = "OK  " if ok else "FAIL"
        if not ok:
            bad += 1
        print(f"  [{flag}] {f.name}: {detail}")
    print(f"{skill_dir.name}  promotion-evals={len(files)}  failing={bad}  "
          f"status={'ok' if bad == 0 else 'warn'}")
    return 1 if bad else 0


def cmd_check(eval_file: Path) -> int:
    if not eval_file.is_file():
        die(f"not a file: {eval_file}")
    ok, detail = run_one(eval_file)
    print(f"{eval_file.name}: {detail}")
    print("gate would OPEN for this principle." if ok
          else "gate would REFUSE — fix the eval before promoting.")
    return 0 if ok else 1


def cmd_gate(skill_dir: Path, principle: str) -> int:
    eval_file = find_eval_for(skill_dir, principle)
    if eval_file is None:
        die(
            f"no registered eval for this principle in "
            f"{skill_dir / EVAL_DIR_NAME}.\n"
            "Promotion REFUSED. Author one from "
            "agents-skills-feedback-loop/assets/promotion-eval.template.md "
            "(see references/promotion-protocol.md).",
            code=2,
        )
    ok, detail = run_one(eval_file)
    if not ok:
        die(f"eval {eval_file.name} is {detail}. Promotion REFUSED.", code=2)
    ledger_append(skill_dir, principle, eval_file.name)
    print(
        f"GATE OPEN — eval {eval_file.name}: {detail}\n\n"
        f"You may now promote this principle by hand:\n"
        f"  1. Add it to the host skill's references/ (NOT SKILL.md auto-edit).\n"
        f"  2. Delete it from {skill_dir.name}/learnings.consolidated.md.\n"
        f"  3. Keep {eval_file.name} — it is now a permanent regression eval;\n"
        f"     re-run via `--audit` before any PR touching this skill.\n\n"
        f"Recorded to {skill_dir.name}/{LEDGER_NAME}."
    )
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("skill_dir", type=Path)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--audit", action="store_true")
    g.add_argument("--check", metavar="EVAL_JSON")
    g.add_argument("--gate", metavar="PRINCIPLE")
    args = p.parse_args()

    if not args.skill_dir.is_dir():
        die(f"not a directory: {args.skill_dir}")

    if args.audit:
        return cmd_audit(args.skill_dir)
    if args.check:
        return cmd_check(Path(args.check))
    return cmd_gate(args.skill_dir, args.gate)


if __name__ == "__main__":
    raise SystemExit(main())
