#!/usr/bin/env python3
"""
agent_eval_runner.py — Lightweight agent evaluation runner.

Reads a JSONL file of task/expected/actual triples and reports pass rates.

SCOPE: This script handles offline pass/fail scoring only. For adversarial
attack suites, multi-turn evaluation harnesses, or regression gates, delegate
to the qa-agent-testing skill (../qa-agent-testing/SKILL.md).

Usage:
    python agent_eval_runner.py --input results.jsonl
    python agent_eval_runner.py --input results.jsonl --output report.json
    python agent_eval_runner.py --input results.jsonl --mode substring
    python agent_eval_runner.py --help

Input JSONL format (one JSON object per line):
    {"task": "Summarise in 1 sentence", "expected": "brief", "actual": "A brief summary."}

Fields:
    task     — human-readable task description (used in output only)
    expected — substring or exact string the actual output must contain/match
    actual   — the agent's actual output
    mode     — (optional per-record) "substring" | "exact" | "nonempty"
               overrides the global --mode for that record

Exit code: 0 if pass_rate == 1.0, 1 otherwise.
"""

import argparse
import json
import sys
from pathlib import Path


def evaluate_record(record: dict, default_mode: str) -> tuple[bool, str]:
    """Return (passed, reason) for a single record."""
    task = record.get("task", "")
    expected = record.get("expected", "")
    actual = record.get("actual", "")
    mode = record.get("mode", default_mode)

    if mode == "nonempty":
        passed = bool(actual and actual.strip())
        reason = "non-empty check"
    elif mode == "exact":
        passed = actual.strip() == expected.strip()
        reason = f"exact match expected={repr(expected)[:60]}"
    else:  # substring (default)
        passed = expected.lower() in actual.lower()
        reason = f"substring expected={repr(expected)[:60]}"

    return passed, reason


def run(input_path: Path, output_path: Path | None, mode: str, verbose: bool) -> int:
    records = []
    try:
        with input_path.open() as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append((lineno, json.loads(line)))
                except json.JSONDecodeError as e:
                    print(f"[WARN] line {lineno}: skipped — JSON parse error: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 2

    if not records:
        print("[ERROR] No valid records found in input file.", file=sys.stderr)
        return 2

    results = []
    passed_count = 0

    for lineno, record in records:
        passed, reason = evaluate_record(record, mode)
        if passed:
            passed_count += 1
        result = {
            "lineno": lineno,
            "task": record.get("task", ""),
            "passed": passed,
            "mode": record.get("mode", mode),
            "reason": reason,
        }
        results.append(result)
        if verbose:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] line {lineno}: {record.get('task', '')[:60]} — {reason}")

    total = len(results)
    pass_rate = passed_count / total if total > 0 else 0.0

    summary = {
        "total": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "pass_rate": round(pass_rate, 4),
        "results": results,
    }

    print(f"\nResults: {passed_count}/{total} passed  ({pass_rate:.1%})")

    if output_path:
        with output_path.open("w") as f:
            json.dump(summary, f, indent=2)
        print(f"Report written to: {output_path}")

    return 0 if pass_rate == 1.0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline agent evaluation runner — reads JSONL task/expected/actual triples.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, type=Path, help="Input JSONL file path")
    parser.add_argument("--output", type=Path, default=None, help="Optional output JSON report path")
    parser.add_argument(
        "--mode",
        choices=["substring", "exact", "nonempty"],
        default="substring",
        help="Default match mode (default: substring). Per-record 'mode' field overrides this.",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-record pass/fail")
    args = parser.parse_args()

    sys.exit(run(args.input, args.output, args.mode, args.verbose))


if __name__ == "__main__":
    main()
