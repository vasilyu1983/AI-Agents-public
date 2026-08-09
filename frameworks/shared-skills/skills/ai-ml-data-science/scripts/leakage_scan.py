#!/usr/bin/env python3
"""
leakage_scan.py — Data leakage scanner for ML feature/target specifications.

Reads a column metadata spec (JSON or JSONL) and flags three leakage
anti-patterns:

  1. TIME LEAKAGE   — features whose observation timestamp is after the
                      label timestamp, or features explicitly tagged as
                      "future" or post-event.
  2. TARGET LEAKAGE — features that are transformations of, proxies for,
                      or direct copies of the target column.
  3. ID LEAKAGE     — identifier or row-key columns included as model inputs,
                      which can cause spurious memorisation.

This is a static analysis tool only — it inspects metadata, not raw data.
Pair it with a data-distribution check (EDA) for runtime leakage detection.

Usage:
    python leakage_scan.py --spec spec.json
    python leakage_scan.py --spec spec.jsonl --output report.json --verbose
    python leakage_scan.py --help

Spec format (JSON, single object or array, or JSONL):
    {
      "target": "churn",
      "columns": [
        {
          "name": "customer_id",
          "role": "id",           // "feature" | "target" | "id" | "timestamp"
          "observation_time": "T",
          "label_time": "T+30d",
          "tags": [],
          "description": "primary key"
        },
        {
          "name": "days_since_churn",
          "role": "feature",
          "tags": ["post_event"],
          "description": "days since churn event"
        }
      ]
    }

Fields per column:
    name             — column name (required)
    role             — "feature" | "target" | "id" | "timestamp" (default: feature)
    observation_time — ISO timestamp or symbolic label when feature is observed
    label_time       — ISO timestamp or symbolic label when target is observed
    tags             — list of string tags; recognized: "future", "post_event",
                       "derived_from_target", "proxy_target", "row_key"
    description      — free text; scanned for leakage keywords

Exit code: 0 if no leakage found, 1 if leakage detected, 2 on input error.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Keywords that suggest a column may leak the target (case-insensitive)
_TARGET_LEAK_KEYWORDS = [
    "churn_reason", "cancel_reason", "refund", "claim_paid",
    "default_flag", "fraud_label", "outcome", "result", "post_event",
    "after_event", "derived_from_target", "proxy_target",
    "target_", "_target",
]

# Keywords in column names or descriptions that suggest ID leakage
_ID_KEYWORDS = [
    r"\b(id|key|pk|guid|uuid|rownum|index|row_id|record_id)\b",
    r"_id$", r"^id_",
]

# Tags that directly indicate leakage
_FUTURE_TAGS = {"future", "post_event", "after_event", "forward_looking"}
_TARGET_PROXY_TAGS = {"derived_from_target", "proxy_target", "target_proxy", "label_proxy"}
_ID_TAGS = {"row_key", "primary_key", "foreign_key", "record_id"}


def _is_after(obs: str | None, label: str | None) -> bool:
    """Naive symbolic check: flag if obs contains '+' relative to a baseline."""
    if not obs or not label:
        return False
    obs_l, label_l = obs.lower(), label.lower()
    if obs_l == label_l:
        return False
    if re.search(r"T\+|t\+|\+\d", obs_l) and not re.search(r"T\+|t\+|\+\d", label_l):
        return True
    return False


def scan_columns(spec: dict) -> list[dict]:
    """Return list of leakage findings."""
    target_name = spec.get("target", "").lower()
    columns = spec.get("columns", [])
    findings = []

    for col in columns:
        name = col.get("name", "")
        role = col.get("role", "feature").lower()
        tags = {t.lower() for t in col.get("tags", [])}
        description = col.get("description", "").lower()
        obs_time = col.get("observation_time")
        label_time = col.get("label_time")

        # Skip target and timestamp columns themselves
        if role in ("target", "timestamp"):
            continue

        # --- TIME LEAKAGE ---
        if role == "feature":
            time_leaked = False
            if _FUTURE_TAGS & tags:
                findings.append({
                    "column": name,
                    "leakage_type": "TIME_LEAKAGE",
                    "reason": f"tagged as future/post-event: {_FUTURE_TAGS & tags}",
                    "severity": "HIGH",
                })
                time_leaked = True
            if not time_leaked and _is_after(obs_time, label_time):
                findings.append({
                    "column": name,
                    "leakage_type": "TIME_LEAKAGE",
                    "reason": f"observation_time={obs_time!r} appears after label_time={label_time!r}",
                    "severity": "HIGH",
                })

        # --- TARGET LEAKAGE ---
        if role == "feature":
            tl_reasons = []
            if _TARGET_PROXY_TAGS & tags:
                tl_reasons.append(f"tagged as target-proxy: {_TARGET_PROXY_TAGS & tags}")
            if target_name and target_name in name.lower():
                tl_reasons.append(f"column name contains target name '{target_name}'")
            for kw in _TARGET_LEAK_KEYWORDS:
                if kw in name.lower() or kw in description:
                    tl_reasons.append(f"leakage keyword '{kw}' in name/description")
                    break
            if tl_reasons:
                findings.append({
                    "column": name,
                    "leakage_type": "TARGET_LEAKAGE",
                    "reason": "; ".join(tl_reasons),
                    "severity": "HIGH",
                })

        # --- ID LEAKAGE ---
        id_reasons = []
        if role == "id" or _ID_TAGS & tags:
            id_reasons.append(f"role={role!r} or id-related tags={_ID_TAGS & tags}")
        else:
            for pattern in _ID_KEYWORDS:
                if re.search(pattern, name.lower()):
                    id_reasons.append(f"name matches ID pattern: {pattern}")
                    break
        if id_reasons:
            findings.append({
                "column": name,
                "leakage_type": "ID_LEAKAGE",
                "reason": "; ".join(id_reasons),
                "severity": "MEDIUM",
            })

    return findings


def load_spec(path: Path) -> list[dict]:
    """Load JSON/JSONL spec, always returning a list of spec dicts."""
    text = path.read_text(encoding="utf-8")
    specs = []
    # Try JSONL first
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                specs.append(obj)
            elif isinstance(obj, list):
                specs.extend(obj)
        except json.JSONDecodeError:
            if lineno == 1:
                # Might be multi-line JSON; fall through
                break
    if specs:
        return specs
    # Try full JSON
    obj = json.loads(text)
    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list):
        return obj
    raise ValueError("Spec must be a JSON object, array, or JSONL.")


def run(spec_path: Path, output_path: Path | None, verbose: bool) -> int:
    try:
        specs = load_spec(spec_path)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {spec_path}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[ERROR] Could not parse spec: {e}", file=sys.stderr)
        return 2

    all_findings = []
    for spec in specs:
        findings = scan_columns(spec)
        all_findings.extend(findings)

    total = len(all_findings)
    by_type: dict[str, int] = {}
    for f in all_findings:
        by_type[f["leakage_type"]] = by_type.get(f["leakage_type"], 0) + 1

    if verbose or total > 0:
        for f in all_findings:
            print(f"[{f['severity']}] {f['leakage_type']:20s} column={f['column']!r}  {f['reason']}")

    print(f"\nLeakage scan complete: {total} issue(s) found.")
    for k, v in sorted(by_type.items()):
        print(f"  {k}: {v}")

    report = {
        "total_issues": total,
        "by_type": by_type,
        "findings": all_findings,
    }

    if output_path:
        with output_path.open("w") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to: {output_path}")

    return 1 if total > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Static leakage scanner for ML feature/target column specs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--spec", required=True, type=Path, help="Column spec JSON or JSONL file")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON report path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print each finding")
    args = parser.parse_args()
    sys.exit(run(args.spec, args.output, args.verbose))


if __name__ == "__main__":
    main()
