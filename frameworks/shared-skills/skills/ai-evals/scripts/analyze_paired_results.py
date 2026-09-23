#!/usr/bin/env python3
"""Analyze frozen paired baseline/candidate evaluation results."""

import argparse
import csv
import json
import math
import random
from collections import defaultdict


def _finite_mean(values, name):
    values = list(values)
    scale = max(abs(value) for value in values)
    if scale == 0:
        return 0.0
    ratio = math.fsum(value / scale for value in values) / len(values)
    ratio = max(-1.0, min(1.0, ratio))
    result = ratio * scale
    if not math.isfinite(result):
        raise ValueError(f"derived {name} must be finite")
    return result


def _boolean(value, field, row_number):
    if value in (None, ""):
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no"}:
        return False
    raise ValueError(f"row {row_number}: {field} must be a boolean")


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            fieldnames = next(reader)
        except StopIteration as exc:
            raise ValueError("CSV requires a header row") from exc
        if len(fieldnames) != len(set(fieldnames)):
            duplicates = sorted({name for name in fieldnames if fieldnames.count(name) > 1})
            raise ValueError(f"CSV header names must be unique; duplicated: {', '.join(duplicates)}")
        required = {"unit_id", "baseline", "candidate"}
        if not required.issubset(fieldnames):
            raise ValueError("CSV requires unit_id, baseline, and candidate columns")
        if ("critical_baseline" in fieldnames) != ("critical_candidate" in fieldnames):
            raise ValueError("provide both critical_baseline and critical_candidate columns, or neither")
        rows, seen = [], set()
        for number, values in enumerate(reader, 2):
            if len(values) != len(fieldnames):
                raise ValueError(f"row {number}: expected {len(fieldnames)} columns, found {len(values)}")
            raw = dict(zip(fieldnames, values))
            unit_id = raw["unit_id"].strip()
            if not unit_id or unit_id in seen:
                raise ValueError(f"row {number}: unit_id must be non-empty and unique")
            seen.add(unit_id)
            try:
                baseline = float(raw["baseline"])
                candidate = float(raw["candidate"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"row {number}: scores must be numeric") from exc
            if not math.isfinite(baseline) or not math.isfinite(candidate):
                raise ValueError(f"row {number}: scores must be finite")
            difference = candidate - baseline
            if not math.isfinite(difference):
                raise ValueError(f"row {number}: candidate-minus-baseline difference must be finite")
            rows.append({
                "unit_id": unit_id,
                "cluster_id": (raw.get("cluster_id") or unit_id).strip(),
                "stratum": (raw.get("stratum") or "all").strip(),
                "baseline": baseline,
                "candidate": candidate,
                "critical_baseline": _boolean(raw.get("critical_baseline"), "critical_baseline", number),
                "critical_candidate": _boolean(raw.get("critical_candidate"), "critical_candidate", number),
            })
            if not rows[-1]["cluster_id"] or not rows[-1]["stratum"]:
                raise ValueError(f"row {number}: cluster_id and stratum must be non-empty")
    if not rows:
        raise ValueError("CSV must contain at least one paired row")
    critical_values = [row[field] for row in rows for field in ("critical_baseline", "critical_candidate")]
    if any(value is not None for value in critical_values) and any(value is None for value in critical_values):
        raise ValueError("critical failure fields must be populated for every row or omitted for every row")
    return rows


def estimate(rows, estimand):
    differences = [row["candidate"] - row["baseline"] for row in rows]
    if estimand == "unit_mean":
        return _finite_mean(differences, "effect")
    clusters = defaultdict(list)
    for row, difference in zip(rows, differences):
        clusters[row["cluster_id"]].append(difference)
    return _finite_mean((_finite_mean(values, "cluster effect") for values in clusters.values()), "effect")


def level_mean(rows, field, estimand):
    if estimand == "unit_mean":
        return _finite_mean((row[field] for row in rows), f"{field} mean")
    clusters = defaultdict(list)
    for row in rows:
        clusters[row["cluster_id"]].append(row[field])
    return _finite_mean(
        (_finite_mean(values, f"cluster {field} mean") for values in clusters.values()),
        f"{field} mean",
    )


def _percentile(values, probability):
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    result = ordered[lower] * (1 - weight) + ordered[upper] * weight
    if not math.isfinite(result):
        raise ValueError("derived percentile must be finite")
    return result


def analyze_group(rows, estimand, reps, alpha, rng):
    clusters = defaultdict(list)
    for row in rows:
        clusters[row["cluster_id"]].append(row)
    cluster_ids = sorted(clusters)
    interval = None
    interval_status = "undefined: fewer than two independent clusters"
    if len(cluster_ids) >= 2:
        draws = []
        for _ in range(reps):
            sampled = [rng.choice(cluster_ids) for _ in cluster_ids]
            if estimand == "unit_mean":
                sample_rows = [row for cluster_id in sampled for row in clusters[cluster_id]]
                draws.append(estimate(sample_rows, estimand))
            else:
                draws.append(_finite_mean(
                    (estimate(clusters[cluster_id], "unit_mean") for cluster_id in sampled),
                    "bootstrap effect",
                ))
        interval = {
            "confidence_level": 1 - alpha,
            "lower": _percentile(draws, alpha / 2),
            "upper": _percentile(draws, 1 - alpha / 2),
        }
        interval_status = "reported"
    return {
        "units": len(rows),
        "clusters": len(cluster_ids),
        "baseline_mean_for_estimand": level_mean(rows, "baseline", estimand),
        "candidate_mean_for_estimand": level_mean(rows, "candidate", estimand),
        "effect_candidate_minus_baseline": estimate(rows, estimand),
        "bootstrap_percentile_interval": interval,
        "interval_status": interval_status,
    }


def critical_summary(rows):
    if rows[0]["critical_baseline"] is None:
        return {"available": False, "reason": "critical failure columns were not provided"}
    baseline = sum(row["critical_baseline"] for row in rows)
    candidate = sum(row["critical_candidate"] for row in rows)
    return {
        "available": True,
        "units": len(rows),
        "baseline_failures": baseline,
        "candidate_failures": candidate,
        "baseline_failure_rate": baseline / len(rows),
        "candidate_failure_rate": candidate / len(rows),
        "failure_rate_change": (candidate - baseline) / len(rows),
        "new_candidate_failures": sum(row["critical_candidate"] and not row["critical_baseline"] for row in rows),
        "resolved_candidate_failures": sum(row["critical_baseline"] and not row["critical_candidate"] for row in rows),
    }


def analyze(rows, estimand="unit_mean", reps=10000, alpha=0.05, seed=20260908):
    if estimand not in {"unit_mean", "cluster_mean"}:
        raise ValueError("estimand must be unit_mean or cluster_mean")
    if reps < 100:
        raise ValueError("bootstrap_reps must be at least 100")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    strata = {name: [row for row in rows if row["stratum"] == name] for name in sorted({r["stratum"] for r in rows})}
    rng = random.Random(seed)
    return {
        "analysis": "paired_cluster_bootstrap",
        "estimand": estimand,
        "weighting": "each captured unit has equal weight" if estimand == "unit_mean" else "each cluster has equal weight after averaging its units",
        "resampling": "sample cluster IDs uniformly with replacement; retain every baseline/candidate pair in each sampled cluster; recompute the declared weighted estimand in each replicate",
        "bootstrap_reps": reps,
        "seed": seed,
        "results": {
            "overall": analyze_group(rows, estimand, reps, alpha, rng),
            "by_stratum": {name: analyze_group(group, estimand, reps, alpha, rng) for name, group in strata.items()},
        },
        "critical_failures": {
            "overall": critical_summary(rows),
            "by_stratum": {name: critical_summary(group) for name, group in strata.items()},
        },
        "interpretation_limit": "Percentile intervals describe resampling uncertainty for the declared captured-unit or cluster population; they do not establish generic bootstrap validity or live-model performance.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("--estimand", choices=("unit_mean", "cluster_mean"), default="unit_mean")
    parser.add_argument("--bootstrap-reps", type=int, default=10000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20260908)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = analyze(load_rows(args.input_csv), args.estimand, args.bootstrap_reps, args.alpha, args.seed)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
