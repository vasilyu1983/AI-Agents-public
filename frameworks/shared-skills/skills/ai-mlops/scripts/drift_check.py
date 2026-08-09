#!/usr/bin/env python3
"""
drift_check.py — Production distribution drift checker (PSI + KL divergence).

Computes Population Stability Index (PSI) and KL divergence between a baseline
distribution and a current distribution loaded from JSON files. Stdlib-only.

PSI interpretation:
    < 0.1  — no significant drift
    0.1–0.2 — moderate drift, monitor closely
    > 0.2  — significant drift, consider retraining

Usage:
    python drift_check.py --baseline baseline.json --current current.json
    python drift_check.py --baseline baseline.json --current current.json \\
        --output report.json --threshold 0.2 --verbose
    python drift_check.py --help

Input JSON format:
    {
      "feature_name": [0.05, 0.10, 0.20, 0.30, 0.25, 0.10],   // probability array (must sum to ~1)
      "other_feature": [0.3, 0.4, 0.2, 0.1]
    }
    OR list form for a single feature:
    [0.05, 0.10, 0.20, 0.30, 0.25, 0.10]

Both files must have the same keys and same-length arrays for each key.

Exit code: 0 if all features within threshold, 1 if any exceed threshold, 2 on error.
"""

import argparse
import json
import math
import sys
from pathlib import Path


EPSILON = 1e-9  # avoid log(0)


def normalize(dist: list[float]) -> list[float]:
    total = sum(dist)
    if total <= 0:
        raise ValueError("Distribution must contain positive values.")
    return [v / total for v in dist]


def psi(baseline: list[float], current: list[float]) -> float:
    """Population Stability Index."""
    if len(baseline) != len(current):
        raise ValueError(f"Distributions must have the same length: {len(baseline)} vs {len(current)}")
    b = normalize(baseline)
    c = normalize(current)
    result = 0.0
    for bi, ci in zip(b, c):
        bi = max(bi, EPSILON)
        ci = max(ci, EPSILON)
        result += (ci - bi) * math.log(ci / bi)
    return result


def kl_divergence(baseline: list[float], current: list[float]) -> float:
    """KL divergence D_KL(current || baseline)."""
    if len(baseline) != len(current):
        raise ValueError(f"Distributions must have the same length.")
    b = normalize(baseline)
    c = normalize(current)
    return sum(
        ci * math.log(max(ci, EPSILON) / max(bi, EPSILON))
        for bi, ci in zip(b, c)
        if ci > EPSILON
    )


def severity(psi_val: float) -> str:
    if psi_val < 0.1:
        return "OK"
    if psi_val < 0.2:
        return "WARN"
    return "ALERT"


def load_distributions(path: Path) -> dict[str, list[float]]:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return {"__distribution__": data}
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if isinstance(v, list)}
    raise ValueError(f"Unsupported format in {path}")


def run(
    baseline_path: Path,
    current_path: Path,
    output_path: Path | None,
    threshold: float,
    verbose: bool,
) -> int:
    try:
        baseline = load_distributions(baseline_path)
        current = load_distributions(current_path)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    features = sorted(set(baseline) & set(current))
    missing_base = set(current) - set(baseline)
    missing_cur = set(baseline) - set(current)

    if missing_base:
        print(f"[WARN] Features in current but not baseline (skipped): {missing_base}", file=sys.stderr)
    if missing_cur:
        print(f"[WARN] Features in baseline but not current (skipped): {missing_cur}", file=sys.stderr)

    if not features:
        print("[ERROR] No overlapping features to compare.", file=sys.stderr)
        return 2

    results = []
    any_alert = False

    for feat in features:
        try:
            psi_val = psi(baseline[feat], current[feat])
            kl_val = kl_divergence(baseline[feat], current[feat])
        except ValueError as e:
            print(f"[WARN] Skipping {feat!r}: {e}", file=sys.stderr)
            continue

        sev = severity(psi_val)
        if sev in ("WARN", "ALERT") or psi_val >= threshold:
            any_alert = True

        entry = {
            "feature": feat,
            "psi": round(psi_val, 6),
            "kl_divergence": round(kl_val, 6),
            "severity": sev,
            "exceeds_threshold": psi_val >= threshold,
        }
        results.append(entry)

        if verbose or sev != "OK":
            flag = "!" if psi_val >= threshold else " "
            print(f"[{sev:5s}]{flag} {feat:<35} PSI={psi_val:.4f}  KL={kl_val:.4f}")

    if not results:
        print("[ERROR] No results computed.", file=sys.stderr)
        return 2

    exceeded = sum(1 for r in results if r["exceeds_threshold"])
    print(f"\nDrift check: {len(results)} feature(s), {exceeded} exceed threshold ({threshold}).")

    report = {
        "baseline": str(baseline_path),
        "current": str(current_path),
        "threshold": threshold,
        "features_checked": len(results),
        "features_exceeded": exceeded,
        "results": results,
    }

    if output_path:
        with output_path.open("w") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to: {output_path}")

    return 1 if exceeded > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PSI + KL drift check between baseline and current distributions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--baseline", required=True, type=Path, help="Baseline distribution JSON")
    parser.add_argument("--current", required=True, type=Path, help="Current distribution JSON")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON report")
    parser.add_argument(
        "--threshold", type=float, default=0.2,
        help="PSI threshold for exit-code-1 alert (default: 0.2)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print all features, not just alerts")
    args = parser.parse_args()
    sys.exit(run(args.baseline, args.current, args.output, args.threshold, args.verbose))


if __name__ == "__main__":
    main()
