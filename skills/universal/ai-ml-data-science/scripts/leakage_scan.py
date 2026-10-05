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
from datetime import datetime
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
    """Compare ISO times or offsets from the same symbolic baseline."""
    if not obs or not label:
        return False
    symbolic = re.compile(r"t(?:([+-])(\d+)(s|m|h|d))?", re.I)
    left, right = symbolic.fullmatch(obs), symbolic.fullmatch(label)
    if left and right:
        def offset(match):
            if match.group(1) is None:
                return 0
            scale = {"s": 1, "m": 60, "h": 3600, "d": 86400}[match.group(3).lower()]
            return int(match.group(2)) * scale * (1 if match.group(1) == "+" else -1)
        return offset(left) > offset(right)
    try:
        return datetime.fromisoformat(obs) > datetime.fromisoformat(label)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot compare observation_time={obs!r} and cutoff={label!r}: use matching ISO times or T offsets") from exc


def validate_spec(spec: dict) -> None:
    """Reject incomplete or mistyped metadata instead of reporting a clean scan."""
    if not isinstance(spec, dict):
        raise ValueError("Each spec must be an object")
    if not isinstance(spec.get("target"), str) or not spec["target"].strip():
        raise ValueError("target must be a non-empty string")
    columns = spec.get("columns")
    if not isinstance(columns, list) or not columns:
        raise ValueError("columns must be a non-empty array")
    if "prediction_time" in spec and (not isinstance(spec["prediction_time"], str) or not spec["prediction_time"].strip()):
        raise ValueError("prediction_time must be a non-empty string")
    for col in columns:
        if not isinstance(col, dict) or not isinstance(col.get("name"), str) or not col["name"].strip():
            raise ValueError("Each column must have a non-empty name")
        if col.get("role", "feature") not in ("feature", "target", "id", "timestamp"):
            raise ValueError(f"Unknown role for column {col['name']!r}")
        tags = col.get("tags", [])
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise ValueError(f"tags must be an array of strings for {col['name']!r}")
        for key in ("description", "observation_time", "label_time"):
            if key in col and (not isinstance(col[key], str) or (key != "description" and not col[key].strip())):
                raise ValueError(f"{key} must be a string for {col['name']!r}")
        # Even explicitly tagged features must not hide malformed time metadata.
        cutoff = spec.get("prediction_time", col.get("label_time"))
        if col.get("observation_time") and cutoff:
            _is_after(col["observation_time"], cutoff)


def scan_columns(spec: dict) -> list[dict]:
    """Return list of leakage findings."""
    validate_spec(spec)
    target_name = spec.get("target", "").lower()
    columns = spec.get("columns", [])
    findings = []

    for col in columns:
        name = col.get("name", "")
        role = col.get("role", "feature").lower()
        tags = {t.lower() for t in col.get("tags", [])}
        description = col.get("description", "").lower()
        obs_time = col.get("observation_time")
        label_time = spec.get("prediction_time", col.get("label_time"))

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
    if path.suffix.lower() == ".jsonl":
        specs = []
        for lineno, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                specs.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL record at line {lineno}: {exc}") from exc
    else:
        obj = json.loads(text)
        specs = obj if isinstance(obj, list) else [obj]
    if not specs:
        raise ValueError("Spec must contain at least one object")
    for spec in specs:
        validate_spec(spec)
    return specs


def run(spec_path: Path, output_path: Path | None, verbose: bool) -> int:
    try:
        specs = load_spec(spec_path)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {spec_path}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as e:
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
        try:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
        except OSError as exc:
            print(f"[ERROR] Cannot write {output_path}: {exc}", file=sys.stderr)
            return 2
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
