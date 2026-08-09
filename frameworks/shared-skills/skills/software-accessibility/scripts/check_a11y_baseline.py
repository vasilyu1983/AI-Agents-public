#!/usr/bin/env python3
"""
check_a11y_baseline.py

Validates a WCAG 2.2 AA accessibility claims file against required Success
Criteria coverage. Reads a JSON file containing addressed SC claims and reports
any missing required criteria.

Exit codes:
  0  All required criteria addressed
  1  One or more required criteria missing or claims file is invalid

Usage:
  python3 check_a11y_baseline.py --help
  python3 check_a11y_baseline.py --claims path/to/claims.json
  python3 check_a11y_baseline.py --claims path/to/claims.json --level AA
  python3 check_a11y_baseline.py --generate-template > claims.json

Claims file schema:
  {
    "component": "string (optional label)",
    "addressed": [
      {
        "sc": "1.1.1",
        "status": "pass|fail|na",
        "note": "optional free-text evidence"
      }
    ]
  }
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# WCAG 2.2 Success Criteria registry (level A and AA only)
# Source: https://www.w3.org/TR/WCAG22/
# ---------------------------------------------------------------------------

@dataclass
class SC:
    id: str
    level: Literal["A", "AA", "AAA"]
    name: str
    removed: bool = False


WCAG_22_CRITERIA: list[SC] = [
    # 1.1 Text Alternatives
    SC("1.1.1", "A", "Non-text Content"),
    # 1.2 Time-based Media
    SC("1.2.1", "A", "Audio-only and Video-only (Prerecorded)"),
    SC("1.2.2", "A", "Captions (Prerecorded)"),
    SC("1.2.3", "A", "Audio Description or Media Alternative (Prerecorded)"),
    SC("1.2.4", "AA", "Captions (Live)"),
    SC("1.2.5", "AA", "Audio Description (Prerecorded)"),
    # 1.3 Adaptable
    SC("1.3.1", "A", "Info and Relationships"),
    SC("1.3.2", "A", "Meaningful Sequence"),
    SC("1.3.3", "A", "Sensory Characteristics"),
    SC("1.3.4", "AA", "Orientation"),
    SC("1.3.5", "AA", "Identify Input Purpose"),
    # 1.4 Distinguishable
    SC("1.4.1", "A", "Use of Color"),
    SC("1.4.2", "A", "Audio Control"),
    SC("1.4.3", "AA", "Contrast (Minimum)"),
    SC("1.4.4", "AA", "Resize Text"),
    SC("1.4.5", "AA", "Images of Text"),
    SC("1.4.10", "AA", "Reflow"),
    SC("1.4.11", "AA", "Non-text Contrast"),
    SC("1.4.12", "AA", "Text Spacing"),
    SC("1.4.13", "AA", "Content on Hover or Focus"),
    # 2.1 Keyboard Accessible
    SC("2.1.1", "A", "Keyboard"),
    SC("2.1.2", "A", "No Keyboard Trap"),
    SC("2.1.4", "A", "Character Key Shortcuts"),
    # 2.2 Enough Time
    SC("2.2.1", "A", "Timing Adjustable"),
    SC("2.2.2", "A", "Pause, Stop, Hide"),
    # 2.3 Seizures and Physical Reactions
    SC("2.3.1", "A", "Three Flashes or Below Threshold"),
    # 2.4 Navigable
    SC("2.4.1", "A", "Bypass Blocks"),
    SC("2.4.2", "A", "Page Titled"),
    SC("2.4.3", "A", "Focus Order"),
    SC("2.4.4", "A", "Link Purpose (In Context)"),
    SC("2.4.5", "AA", "Multiple Ways"),
    SC("2.4.6", "AA", "Headings and Labels"),
    SC("2.4.7", "AA", "Focus Visible"),
    SC("2.4.11", "AA", "Focus Not Obscured (Minimum)"),
    SC("2.4.13", "AA", "Focus Appearance"),
    # 2.5 Input Modalities
    SC("2.5.1", "A", "Pointer Gestures"),
    SC("2.5.2", "A", "Pointer Cancellation"),
    SC("2.5.3", "A", "Label in Name"),
    SC("2.5.4", "A", "Motion Actuation"),
    SC("2.5.7", "AA", "Dragging Movements"),
    SC("2.5.8", "AA", "Target Size (Minimum)"),
    # 3.1 Readable
    SC("3.1.1", "A", "Language of Page"),
    SC("3.1.2", "AA", "Language of Parts"),
    # 3.2 Predictable
    SC("3.2.1", "A", "On Focus"),
    SC("3.2.2", "A", "On Input"),
    SC("3.2.3", "AA", "Consistent Navigation"),
    SC("3.2.4", "AA", "Consistent Identification"),
    SC("3.2.6", "AA", "Consistent Help"),
    # 3.3 Input Assistance
    SC("3.3.1", "A", "Error Identification"),
    SC("3.3.2", "A", "Labels or Instructions"),
    SC("3.3.3", "AA", "Error Suggestion"),
    SC("3.3.4", "AA", "Error Prevention (Legal, Financial, Data)"),
    SC("3.3.7", "A", "Redundant Entry"),
    SC("3.3.8", "AA", "Accessible Authentication (Minimum)"),
    # 4.1 Compatible
    # 4.1.1 Parsing was removed in WCAG 2.2
    SC("4.1.1", "A", "Parsing (removed in WCAG 2.2)", removed=True),
    SC("4.1.2", "A", "Name, Role, Value"),
    SC("4.1.3", "AA", "Status Messages"),
]

SC_BY_ID: dict[str, SC] = {sc.id: sc for sc in WCAG_22_CRITERIA}

REQUIRED_LEVELS = {"A": {"A"}, "AA": {"A", "AA"}}


# ---------------------------------------------------------------------------
# Template generator
# ---------------------------------------------------------------------------

def generate_template(level: str = "AA") -> dict:
    levels = REQUIRED_LEVELS.get(level, {"A", "AA"})
    addressed = []
    for sc in WCAG_22_CRITERIA:
        if sc.removed:
            continue
        if sc.level not in levels:
            continue
        addressed.append({
            "sc": sc.id,
            "status": "pass",
            "note": f"{sc.name} — add evidence here",
        })
    return {
        "component": "my-component",
        "addressed": addressed,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    missing: list[SC] = field(default_factory=list)
    failed: list[tuple[SC, str]] = field(default_factory=list)
    unknown_scs: list[str] = field(default_factory=list)
    addressed_ids: set[str] = field(default_factory=set)


def validate_claims(claims: dict, level: str) -> ValidationResult:
    result = ValidationResult()
    required_levels = REQUIRED_LEVELS.get(level, {"A", "AA"})

    # Parse addressed claims
    addressed_raw = claims.get("addressed", [])
    if not isinstance(addressed_raw, list):
        raise ValueError("'addressed' must be an array")

    addressed_map: dict[str, str] = {}  # sc_id -> status
    addressed_notes: dict[str, str] = {}

    for entry in addressed_raw:
        if not isinstance(entry, dict):
            raise ValueError(f"Each entry in 'addressed' must be an object, got: {entry!r}")
        sc_id = entry.get("sc", "").strip()
        status = entry.get("status", "").strip().lower()
        note = entry.get("note", "")
        if not sc_id:
            raise ValueError("Each addressed entry must have an 'sc' field")
        if status not in {"pass", "fail", "na"}:
            raise ValueError(f"SC {sc_id}: status must be 'pass', 'fail', or 'na', got {status!r}")
        if sc_id not in SC_BY_ID:
            result.unknown_scs.append(sc_id)
        addressed_map[sc_id] = status
        addressed_notes[sc_id] = note

    result.addressed_ids = set(addressed_map.keys())

    # Check required criteria
    for sc in WCAG_22_CRITERIA:
        if sc.removed:
            continue
        if sc.level not in required_levels:
            continue
        if sc.id not in addressed_map:
            result.missing.append(sc)
        elif addressed_map[sc.id] == "fail":
            result.failed.append((sc, addressed_notes.get(sc.id, "")))

    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(component: str, level: str, result: ValidationResult) -> int:
    errors = len(result.missing) + len(result.failed)
    status = "PASS" if errors == 0 else "FAIL"

    print(f"## Accessibility Baseline Check — {component}")
    print()
    print(f"- Status:  {status}")
    print(f"- Level:   WCAG 2.2 {level}")
    print(f"- Addressed: {len(result.addressed_ids)}")
    print(f"- Missing:   {len(result.missing)}")
    print(f"- Failed:    {len(result.failed)}")
    print(f"- Unknown SCs in claims: {len(result.unknown_scs)}")
    print()

    if result.missing:
        print("## Missing Required Criteria")
        for sc in result.missing:
            print(f"  - [{sc.level}] {sc.id} {sc.name}")
        print()

    if result.failed:
        print("## Failed Criteria")
        for sc, note in result.failed:
            note_str = f" — {note}" if note else ""
            print(f"  - [{sc.level}] {sc.id} {sc.name}{note_str}")
        print()

    if result.unknown_scs:
        print("## Unknown SC IDs in Claims (may be typos or future criteria)")
        for sc_id in result.unknown_scs:
            print(f"  - {sc_id}")
        print()

    if status == "PASS":
        print("All required criteria addressed with pass or na status.")

    return 0 if errors == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a WCAG 2.2 accessibility claims file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--claims",
        type=Path,
        help="Path to the claims JSON file to validate",
    )
    parser.add_argument(
        "--level",
        choices=["A", "AA"],
        default="AA",
        help="Conformance level to check against (default: AA)",
    )
    parser.add_argument(
        "--generate-template",
        action="store_true",
        help="Print a template claims.json to stdout and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.generate_template:
        template = generate_template(args.level)
        print(json.dumps(template, indent=2))
        return 0

    if not args.claims:
        print("Error: --claims is required unless --generate-template is used", file=sys.stderr)
        print("Run with --help for usage.", file=sys.stderr)
        return 2

    claims_path = args.claims.resolve()
    if not claims_path.exists():
        print(f"Error: claims file not found: {claims_path}", file=sys.stderr)
        return 2

    try:
        claims = json.loads(claims_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {claims_path}: {exc}", file=sys.stderr)
        return 2

    if not isinstance(claims, dict):
        print("Error: claims file must be a JSON object", file=sys.stderr)
        return 2

    component = claims.get("component", str(claims_path.name))

    try:
        result = validate_claims(claims, args.level)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return print_report(component, args.level, result)


if __name__ == "__main__":
    sys.exit(main())
