#!/usr/bin/env python3
"""
contract_validator.py — stdlib-only validator for shared-contract JSON.

Validates JSON files containing AI platform shared contracts
(ModelRequest, ModelResponse, ContextBundle, SafetyDecision, ToolInvocation,
EvalRun, AuditEvent) against required field schemas.

Usage:
    python3 scripts/contract_validator.py --input contract.json
    python3 scripts/contract_validator.py --input contract.json --type ModelRequest
    python3 scripts/contract_validator.py --dir contracts/ --type all
    python3 scripts/contract_validator.py --input contract.json --output report.json

Exit codes:
    0 — all contracts valid
    1 — one or more validation failures
    2 — input file not found or malformed JSON
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Contract schemas
# ---------------------------------------------------------------------------
# Each contract has: required fields (must be present and non-null)
# and typed fields (must be of the specified Python type if present).
# Field type "any" means present and non-empty but type is not enforced.

CONTRACTS: dict[str, dict] = {
    "ModelRequest": {
        "required": ["caller", "task_type", "risk_tier", "input"],
        "typed": {
            "caller": str,
            "task_type": str,
            "risk_tier": (str, int),
            "input": (str, dict, list),
            "allowed_providers": list,
            "allowed_models": list,
        },
        "enum": {
            "risk_tier": [0, 1, 2, "0", "1", "2", "tier0", "tier1", "tier2"],
        },
        "description": "Outbound model call with caller identity, task type, risk tier, and input.",
    },
    "ModelResponse": {
        "required": ["request_id", "output", "schema_valid"],
        "typed": {
            "request_id": str,
            "output": (str, dict, list),
            "schema_valid": bool,
            "citations": list,
            "evidence_refs": list,
        },
        "description": "Model response with validation status and optional citations.",
    },
    "ContextBundle": {
        "required": ["tenant_id", "surface", "live_facts", "freshness_class"],
        "typed": {
            "tenant_id": str,
            "surface": str,
            "live_facts": (dict, list),
            "retrieved_evidence": list,
            "derived_memory": list,
            "freshness_class": str,
            "provenance": (str, dict),
        },
        "description": "Surface-specific context assembly with tenant scope, freshness, and provenance.",
    },
    "SafetyDecision": {
        "required": ["decision", "reason"],
        "typed": {
            "decision": str,
            "reason": str,
            "redacted_fields": list,
            "escalation_target": str,
        },
        "enum": {
            "decision": ["allowed", "redacted", "blocked", "escalate-to-human"],
        },
        "description": "Safety gate decision with reason and optional escalation target.",
    },
    "ToolInvocation": {
        "required": ["principal", "tool_name", "approved_scope"],
        "typed": {
            "principal": str,
            "tool_name": str,
            "approved_scope": (str, list),
            "result": "any",
            "side_effect_status": str,
        },
        "enum": {
            "side_effect_status": ["none", "pending", "committed", "failed", "rolled_back"],
        },
        "description": "Tool call record with principal identity, approved scope, and side-effect status.",
    },
    "EvalRun": {
        "required": ["suite_version", "judged_dimensions", "score", "status"],
        "typed": {
            "suite_version": str,
            "judged_dimensions": list,
            "score": (int, float),
            "status": str,
            "regression_notes": (str, list),
        },
        "enum": {
            "status": ["pass", "fail", "pending", "error"],
        },
        "description": "Evaluation run with suite version, scores, and regression notes.",
    },
    "AuditEvent": {
        "required": ["trace_id", "actor", "feature", "provider", "data_class", "retention_class"],
        "typed": {
            "trace_id": str,
            "actor": str,
            "feature": str,
            "provider": str,
            "data_class": str,
            "approval_event": (str, dict),
            "retention_class": str,
        },
        "description": "Audit trail event with trace ID, actor, provider, data class, and retention class.",
    },
}


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def detect_contract_type(data: dict) -> Optional[str]:
    """Heuristic: guess contract type from the keys present in the dict."""
    scores: dict[str, int] = {}
    for ctype, schema in CONTRACTS.items():
        matched = sum(1 for f in schema["required"] if f in data)
        scores[ctype] = matched
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else None


def validate_contract(data: dict, contract_type: str) -> list[str]:
    """
    Validate a contract dict against the named contract schema.
    Returns a list of error strings (empty list = valid).
    """
    if contract_type not in CONTRACTS:
        return [f"Unknown contract type: {contract_type!r}. Valid types: {list(CONTRACTS.keys())}"]

    schema = CONTRACTS[contract_type]
    errors: list[str] = []

    # Required fields
    for field in schema["required"]:
        if field not in data:
            errors.append(f"Missing required field: {field!r}")
        elif data[field] is None:
            errors.append(f"Required field is null: {field!r}")
        elif data[field] == "" and isinstance(data[field], str):
            errors.append(f"Required field is empty string: {field!r}")

    # Type checks
    for field, expected_type in schema.get("typed", {}).items():
        if field not in data or data[field] is None:
            continue
        if expected_type == "any":
            continue
        if not isinstance(data[field], expected_type):
            actual = type(data[field]).__name__
            if isinstance(expected_type, tuple):
                expected_names = " or ".join(t.__name__ for t in expected_type)
            else:
                expected_names = expected_type.__name__
            errors.append(f"Field {field!r}: expected {expected_names}, got {actual}")

    # Enum checks
    for field, valid_values in schema.get("enum", {}).items():
        if field in data and data[field] is not None:
            if data[field] not in valid_values:
                errors.append(
                    f"Field {field!r}: value {data[field]!r} not in allowed values {valid_values}"
                )

    return errors


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def load_json_file(path: Path) -> Any:
    """Load a JSON file. May be a dict or a list of dicts."""
    with path.open(encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"ERROR: malformed JSON in {path}: {exc}", file=sys.stderr)
            sys.exit(2)


def collect_files(args) -> list[tuple[Path, Optional[str]]]:
    """Return list of (path, contract_type_or_None) from CLI args."""
    pairs: list[tuple[Path, Optional[str]]] = []
    requested_type = None if args.type == "auto" or args.type == "all" else args.type

    if args.input:
        p = Path(args.input)
        if not p.exists():
            print(f"ERROR: file not found: {p}", file=sys.stderr)
            sys.exit(2)
        pairs.append((p, requested_type))

    if args.dir:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"ERROR: not a directory: {d}", file=sys.stderr)
            sys.exit(2)
        for p in sorted(d.glob("*.json")):
            pairs.append((p, requested_type))

    return pairs


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def run_validation(pairs: list[tuple[Path, Optional[str]]]) -> list[dict]:
    results = []
    for file_path, forced_type in pairs:
        raw = load_json_file(file_path)
        # Support both single-object and list-of-objects files
        items = raw if isinstance(raw, list) else [raw]
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                results.append({
                    "file": str(file_path),
                    "index": idx,
                    "contract_type": None,
                    "status": "error",
                    "errors": [f"Expected a JSON object, got {type(item).__name__}"],
                })
                continue

            ctype = forced_type or detect_contract_type(item)
            if not ctype:
                results.append({
                    "file": str(file_path),
                    "index": idx,
                    "contract_type": None,
                    "status": "error",
                    "errors": ["Could not detect contract type — no matching required fields."],
                })
                continue

            errors = validate_contract(item, ctype)
            results.append({
                "file": str(file_path),
                "index": idx,
                "contract_type": ctype,
                "status": "valid" if not errors else "invalid",
                "errors": errors,
            })

    return results


def print_results(results: list[dict]) -> None:
    total = len(results)
    valid = sum(1 for r in results if r["status"] == "valid")
    invalid = sum(1 for r in results if r["status"] == "invalid")
    errors = sum(1 for r in results if r["status"] == "error")

    print(f"\n=== Contract Validator Report ===")
    print(f"Contracts checked: {total}")
    print(f"  Valid:    {valid}")
    print(f"  Invalid:  {invalid}")
    print(f"  Errors:   {errors}")

    if invalid or errors:
        print("\n--- Issues ---")
        for r in results:
            if r["status"] in ("invalid", "error"):
                label = f"{r['file']}" + (f" [item {r['index']}]" if r["index"] > 0 else "")
                ctype = r.get("contract_type") or "unknown"
                print(f"\n[{r['status'].upper()}] {label} (type: {ctype})")
                for err in r["errors"]:
                    print(f"  - {err}")
    else:
        print("\nAll contracts are valid.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate AI platform shared-contract JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", "-i", metavar="FILE",
                       help="Path to a single JSON contract file.")
    group.add_argument("--dir", metavar="DIR",
                       help="Directory of JSON contract files to validate.")
    p.add_argument("--type", "-t", default="auto",
                   choices=list(CONTRACTS.keys()) + ["auto", "all"],
                   help="Contract type to validate against. Default: auto-detect.")
    p.add_argument("--output", "-o", metavar="FILE",
                   help="Optional path to write JSON validation report.")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    pairs = collect_files(args)
    if not pairs:
        print("No input files found.", file=sys.stderr)
        sys.exit(2)

    results = run_validation(pairs)
    print_results(results)

    if args.output:
        out_path = Path(args.output)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)
        print(f"\nReport written to: {out_path}")

    has_issues = any(r["status"] in ("invalid", "error") for r in results)
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
