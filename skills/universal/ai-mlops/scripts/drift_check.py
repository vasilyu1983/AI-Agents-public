#!/usr/bin/env python3
"""
drift_check.py — Production distribution drift checker (PSI + KL divergence). Stdlib-only.

Input is per-bin COUNTS for each feature (not proportions): PSI's no-drift noise
depends on the sample sizes, so the checker needs them.

    baseline.json: {"feature_a": [120, 340, 510, 30], "feature_b": [900, 100]}
    current.json:  {"feature_a": [ 14,  40,  61,  5], "feature_b": [ 88,  12]}
    (a bare list is accepted for a single feature)

Method:
    1. Baseline bins with fewer than --min-bin-count observations are pooled into
       one bin (in both files), so a near-empty bin cannot dominate PSI.
    2. Additive smoothing (--alpha per bin) before normalising; no epsilon clamp.
    3. Noise floor: with no drift, PSI is approximately (1/n + 1/m) * chi2(B-1),
       so its mean is (B-1)(1/n + 1/m) and it FALLS as the windows grow. The 99th
       percentile of that null is printed per feature.
    4. Severity uses one threshold pair, applied only above the noise floor:
           OK    PSI <= max(warn, p99 noise)
           WARN  above that, up to max(alert, p99 noise)
           ALERT PSI >  max(alert, p99 noise)
       Defaults: warn 0.1, alert 0.2 (conventional effect-size cut-offs, not laws).

Exit code: 0 no ALERT, 1 any ALERT, 2 invalid input (negative, fractional or
non-finite counts, empty window, mismatched bins or features).

Usage:
    python drift_check.py --baseline baseline.json --current current.json
    python drift_check.py --baseline b.json --current c.json --output report.json --verbose
"""

import argparse
import json
import math
import sys
from pathlib import Path

DEFAULT_WARN = 0.1
DEFAULT_ALERT = 0.2
DEFAULT_ALPHA = 0.5
DEFAULT_MIN_BIN = 5
Z_99 = 2.3263478740408408  # standard normal 0.99 quantile


class InputError(ValueError):
    pass


def chi2_quantile_wh(k: int, z: float = Z_99) -> float:
    """Wilson-Hilferty approximation of the chi-square quantile with k d.o.f."""
    a = 2.0 / (9.0 * k)
    return k * (1.0 - a + z * math.sqrt(a)) ** 3


def check_counts(name: str, which: str, values: object) -> list[float]:
    if not isinstance(values, list) or len(values) < 2:
        raise InputError(f"{which} feature {name!r}: need a list of at least 2 bin counts")
    out = []
    for i, v in enumerate(values):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise InputError(f"{which} feature {name!r} bin {i}: count must be a finite number, got {v!r}")
        if v < 0:
            raise InputError(f"{which} feature {name!r} bin {i}: negative count {v}")
        if float(v) != int(v):
            raise InputError(f"{which} feature {name!r} bin {i}: counts must be whole numbers, got {v} "
                             "(proportions carry no sample size; pass bin counts)")
        out.append(float(v))
    if sum(out) <= 0:
        raise InputError(f"{which} feature {name!r}: window is empty (all counts 0)")
    return out


def pool_sparse(base: list[float], cur: list[float], min_bin: int) -> tuple[list[float], list[float], int]:
    """Pool baseline bins below min_bin into one bin. Returns (base, cur, pooled_count)."""
    keep = [i for i, b in enumerate(base) if b >= min_bin]
    sparse = [i for i, b in enumerate(base) if b < min_bin]
    if not sparse:
        return base, cur, 0
    nb = [base[i] for i in keep] + [sum(base[i] for i in sparse)]
    nc = [cur[i] for i in keep] + [sum(cur[i] for i in sparse)]
    return nb, nc, len(sparse)


def smoothed(counts: list[float], alpha: float) -> list[float]:
    total = sum(counts) + alpha * len(counts)
    return [(c + alpha) / total for c in counts]


def psi(b: list[float], c: list[float]) -> float:
    return sum((ci - bi) * math.log(ci / bi) for bi, ci in zip(b, c))


def kl(b: list[float], c: list[float]) -> float:
    """D_KL(current || baseline) on smoothed proportions."""
    return sum(ci * math.log(ci / bi) for bi, ci in zip(b, c))


def load(path: Path) -> dict:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return {"__distribution__": data}
    if isinstance(data, dict) and data:
        return data
    raise InputError(f"{path}: expected a non-empty object of feature -> bin counts, or a list")


def evaluate(baseline: dict, current: dict, warn: float, alert: float,
             alpha: float, min_bin: int) -> list[dict]:
    if set(baseline) != set(current):
        raise InputError(
            f"feature sets differ: only in baseline {sorted(set(baseline) - set(current))}, "
            f"only in current {sorted(set(current) - set(baseline))} (a vanished or new feature "
            "is itself a pipeline change; fix the inputs instead of skipping it)")
    results = []
    for feat in sorted(baseline):
        b = check_counts(feat, "baseline", baseline[feat])
        c = check_counts(feat, "current", current[feat])
        if len(b) != len(c):
            raise InputError(f"feature {feat!r}: {len(b)} baseline bins vs {len(c)} current bins")
        b, c, pooled = pool_sparse(b, c, min_bin)
        n, m, bins = sum(b), sum(c), len(b)
        if bins < 2:
            raise InputError(f"feature {feat!r}: fewer than 2 bins left after pooling sparse bins")
        pb, pc = smoothed(b, alpha), smoothed(c, alpha)
        psi_val = psi(pb, pc)
        scale = 1.0 / n + 1.0 / m
        noise_mean = (bins - 1) * scale
        noise_p99 = scale * chi2_quantile_wh(bins - 1)
        warn_eff, alert_eff = max(warn, noise_p99), max(alert, noise_p99)
        sev = "OK" if psi_val <= warn_eff else ("WARN" if psi_val <= alert_eff else "ALERT")
        results.append({
            "feature": feat, "psi": round(psi_val, 6), "kl_divergence": round(kl(pb, pc), 6),
            "n_baseline": int(n), "n_current": int(m), "bins": bins, "pooled_sparse_bins": pooled,
            "noise_mean": round(noise_mean, 6), "noise_p99": round(noise_p99, 6),
            "warn_at": round(warn_eff, 6), "alert_at": round(alert_eff, 6), "severity": sev,
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PSI + KL drift check on per-bin counts, with a sample-size noise floor.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--baseline", required=True, type=Path, help="Baseline bin-count JSON")
    parser.add_argument("--current", required=True, type=Path, help="Current-window bin-count JSON")
    parser.add_argument("--output", type=Path, default=None, help="Write a JSON report here")
    parser.add_argument("--warn", type=float, default=DEFAULT_WARN, help="PSI warn level (default 0.1)")
    parser.add_argument("--threshold", "--alert", dest="alert", type=float, default=DEFAULT_ALERT,
                        help="PSI alert level; exit 1 above it (default 0.2)")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA, help="Additive smoothing per bin (default 0.5)")
    parser.add_argument("--min-bin-count", type=int, default=DEFAULT_MIN_BIN,
                        help="Pool baseline bins with fewer observations than this (default 5)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print every feature, not just WARN/ALERT")
    args = parser.parse_args()

    if (not all(math.isfinite(value) for value in (args.warn, args.alert, args.alpha))
            or not (0 < args.warn <= args.alert) or args.alpha <= 0 or args.min_bin_count < 0):
        print("[ERROR] need finite 0 < --warn <= --threshold, finite --alpha > 0, "
              "--min-bin-count >= 0", file=sys.stderr)
        sys.exit(2)
    try:
        results = evaluate(load(args.baseline), load(args.current), args.warn, args.alert,
                           args.alpha, args.min_bin_count)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(2)
    except (json.JSONDecodeError, InputError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(2)

    for r in results:
        if args.verbose or r["severity"] != "OK":
            print(f"[{r['severity']:5s}] {r['feature']:<30} PSI={r['psi']:.4f}  noise p99={r['noise_p99']:.4f}  "
                  f"n={r['n_baseline']}/{r['n_current']}  bins={r['bins']}"
                  + (f"  pooled={r['pooled_sparse_bins']}" if r["pooled_sparse_bins"] else ""))
    alerts = sum(1 for r in results if r["severity"] == "ALERT")
    warns = sum(1 for r in results if r["severity"] == "WARN")
    print(f"\nDrift check: {len(results)} feature(s), {alerts} ALERT, {warns} WARN "
          f"(warn {args.warn}, alert {args.alert}, each raised to the feature's p99 noise floor).")
    if args.output:
        args.output.write_text(json.dumps({"warn": args.warn, "alert": args.alert, "results": results}, indent=2))
        print(f"Report written to: {args.output}")
    sys.exit(1 if alerts else 0)


if __name__ == "__main__":
    main()
