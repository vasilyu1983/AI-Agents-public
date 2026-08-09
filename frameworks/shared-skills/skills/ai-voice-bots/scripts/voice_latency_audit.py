#!/usr/bin/env python3
"""Voice pipeline latency auditor.

Analyzes pipeline execution logs to produce a latency breakdown report
with per-component percentile distributions (p50, p90, p99).

Usage:
    python3 voice_latency_audit.py --input pipeline_logs.jsonl [--budget 700] [--output report.json]

Input format (JSONL — one pipeline execution per line):
    {
        "call_id": "call_001",
        "timestamp": "2026-03-31T14:30:00Z",
        "components": {
            "vad": {"start_ms": 0, "end_ms": 250},
            "stt": {"start_ms": 250, "end_ms": 400},
            "llm": {"start_ms": 400, "end_ms": 620},
            "tts": {"start_ms": 620, "end_ms": 720},
            "network": {"start_ms": 0, "end_ms": 30}
        },
        "total_turn_ms": 750
    }

Output: per-component percentile distributions and budget compliance report.
"""

import argparse
import json
import sys
from pathlib import Path


# Default latency budgets per component (ms)
DEFAULT_BUDGETS = {
    "vad": 300,
    "stt": 200,
    "llm": 300,
    "tts": 150,
    "network": 50,
}
DEFAULT_TOTAL_BUDGET = 700


def percentile(values: list[float], p: float) -> float:
    """Calculate percentile from sorted values."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_vals):
        return sorted_vals[f]
    return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])


def extract_component_latencies(logs: list[dict]) -> dict[str, list[float]]:
    """Extract latency values per component from logs."""
    component_latencies: dict[str, list[float]] = {}
    total_latencies: list[float] = []

    for log in logs:
        components = log.get("components", {})
        for name, timing in components.items():
            if name not in component_latencies:
                component_latencies[name] = []
            duration = timing.get("end_ms", 0) - timing.get("start_ms", 0)
            component_latencies[name].append(duration)

        total = log.get("total_turn_ms")
        if total is not None:
            total_latencies.append(total)

    component_latencies["total"] = total_latencies
    return component_latencies


def analyze_component(name: str, values: list[float], budget: float) -> dict:
    """Analyze latency distribution for a single component."""
    if not values:
        return {"name": name, "count": 0, "budget_ms": budget}

    p50 = percentile(values, 50)
    p90 = percentile(values, 90)
    p99 = percentile(values, 99)

    return {
        "name": name,
        "count": len(values),
        "budget_ms": budget,
        "p50_ms": round(p50, 1),
        "p90_ms": round(p90, 1),
        "p99_ms": round(p99, 1),
        "min_ms": round(min(values), 1),
        "max_ms": round(max(values), 1),
        "mean_ms": round(sum(values) / len(values), 1),
        "within_budget_pct": round(sum(1 for v in values if v <= budget) / len(values) * 100, 1),
        "exceeds_budget": p90 > budget,
    }


def generate_report(logs: list[dict], total_budget: float, component_budgets: dict) -> dict:
    """Generate full latency audit report."""
    component_latencies = extract_component_latencies(logs)

    analyses = {}
    for name, values in component_latencies.items():
        budget = component_budgets.get(name, total_budget if name == "total" else 0)
        analyses[name] = analyze_component(name, values, budget)

    # Identify bottlenecks (components where p90 exceeds budget)
    bottlenecks = [
        {"component": name, "p90_ms": a["p90_ms"], "budget_ms": a["budget_ms"], "overage_ms": round(a["p90_ms"] - a["budget_ms"], 1)}
        for name, a in analyses.items()
        if a.get("exceeds_budget", False) and name != "total"
    ]
    bottlenecks.sort(key=lambda x: x["overage_ms"], reverse=True)

    total_analysis = analyses.get("total", {})

    return {
        "summary": {
            "total_executions": len(logs),
            "total_budget_ms": total_budget,
            "total_p50_ms": total_analysis.get("p50_ms", 0),
            "total_p90_ms": total_analysis.get("p90_ms", 0),
            "total_p99_ms": total_analysis.get("p99_ms", 0),
            "within_budget_pct": total_analysis.get("within_budget_pct", 0),
            "pass": total_analysis.get("p90_ms", 0) <= total_budget,
        },
        "components": {k: v for k, v in analyses.items() if k != "total"},
        "total": total_analysis,
        "bottlenecks": bottlenecks,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit voice pipeline latency.")
    parser.add_argument("--input", required=True, help="JSONL file with pipeline execution logs")
    parser.add_argument("--budget", type=int, default=DEFAULT_TOTAL_BUDGET, help="Total turn latency budget in ms (default: 700)")
    parser.add_argument("--output", default=None, help="Output JSON file (optional, defaults to stdout)")
    args = parser.parse_args()

    # Load logs
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    logs = []
    for line in input_path.read_text().strip().split("\n"):
        if line.strip():
            logs.append(json.loads(line))

    if not logs:
        print("Error: No pipeline executions found in input.", file=sys.stderr)
        sys.exit(1)

    # Generate report
    report = generate_report(logs, args.budget, DEFAULT_BUDGETS)

    # Output
    output_json = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Report written to {args.output}")
    else:
        print(output_json)

    # Print summary to stderr
    summary = report["summary"]
    status = "PASS" if summary["pass"] else "FAIL"
    print(f"\n--- Latency Audit ({summary['total_executions']} executions) [{status}] ---", file=sys.stderr)
    print(f"Total: p50={summary['total_p50_ms']}ms, p90={summary['total_p90_ms']}ms, p99={summary['total_p99_ms']}ms (budget: {args.budget}ms)", file=sys.stderr)
    print(f"Within budget: {summary['within_budget_pct']}%", file=sys.stderr)

    if report["bottlenecks"]:
        print("\nBottlenecks (p90 exceeds budget):", file=sys.stderr)
        for b in report["bottlenecks"]:
            print(f"  {b['component']}: p90={b['p90_ms']}ms (budget: {b['budget_ms']}ms, +{b['overage_ms']}ms)", file=sys.stderr)

    print("\nPer-component:", file=sys.stderr)
    for name, comp in report["components"].items():
        flag = " ⚠" if comp.get("exceeds_budget") else ""
        print(f"  {name}: p50={comp['p50_ms']}ms, p90={comp['p90_ms']}ms (budget: {comp['budget_ms']}ms){flag}", file=sys.stderr)


if __name__ == "__main__":
    main()
