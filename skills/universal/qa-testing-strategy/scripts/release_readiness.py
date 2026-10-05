#!/usr/bin/env python3
"""Release readiness: hard gates first, weighted score only for residual signals.

Hard gates are non-compensatory. A failing security scan, a failing critical-journey
E2E, or any open P0 returns BLOCK before any scoring happens, so no amount of green
elsewhere can offset them. Missing hard-gate inputs are treated as failing (fail closed).

Usage:
    python3 release_readiness.py metrics.json
    echo '{"security_clean": false}' | python3 release_readiness.py -

Exit codes: 0 SHIP, 1 HOLD or BLOCK, 2 invalid input.
"""
from __future__ import annotations

import json
import sys

HARD_GATES = {
    "security_clean": "security scan has no unresolved critical/high findings",
    "critical_e2e_pass": "every critical-journey E2E passed on this build",
    "no_open_p0": "no open P0 defects against this release",
}

# Weights for residual (compensatory) signals only; they sum to 1.0.
WEIGHTS = {
    "test_pass_rate": 0.30,
    "e2e_pass_rate": 0.20,
    "flake_rate_inverse": 0.15,
    "performance_pass": 0.20,
    "staging_soak": 0.15,
}

SHIP_AT = 85
HOLD_AT = 70


def release_readiness(metrics: dict) -> dict:
    failed = [name for name in HARD_GATES if metrics.get(name) is not True]
    if failed:
        return {
            "recommendation": "BLOCK",
            "ready": False,
            "hard_gate_failures": failed,
            "overall_score": None,
        }

    scores = {
        "test_pass_rate": min(float(metrics.get("test_pass_rate", 0)), 100.0),
        "e2e_pass_rate": min(float(metrics.get("e2e_pass_rate", 0)), 100.0),
        "flake_rate_inverse": max(100.0 - float(metrics.get("flake_rate", 100)), 0.0),
        "performance_pass": 100.0 if metrics.get("performance_pass") is True else 0.0,
        "staging_soak": min(float(metrics.get("staging_soak_hours", 0)) / 4 * 100, 100.0),
    }
    total = round(sum(scores[k] * WEIGHTS[k] for k in WEIGHTS), 1)
    if total >= SHIP_AT:
        rec = "SHIP"
    elif total >= HOLD_AT:
        rec = "HOLD"
    else:
        rec = "BLOCK"
    return {
        "recommendation": rec,
        "ready": rec == "SHIP",
        "hard_gate_failures": [],
        "overall_score": total,
        "component_scores": {k: round(v, 1) for k, v in scores.items()},
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        raw = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
        metrics = json.loads(raw)
        if not isinstance(metrics, dict):
            raise ValueError("metrics must be a JSON object")
        result = release_readiness(metrics)
    except (OSError, ValueError, TypeError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["recommendation"] == "SHIP" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
