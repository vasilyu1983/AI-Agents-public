#!/usr/bin/env python3
"""Call quality scorer for voice bots.

Scores call quality from transcripts and metadata.
Checks conversation completion, user repetition rate, response latency,
and optionally WER against reference transcripts.

Usage:
    python3 call_quality_scorer.py --input calls.jsonl [--output scores.json]

Input format (JSONL — one call per line):
    {
        "call_id": "call_001",
        "duration_seconds": 120,
        "outcome": "resolved",
        "turns": [
            {
                "role": "user",
                "content": "Where is my order?",
                "latency_ms": null
            },
            {
                "role": "assistant",
                "content": "I'll look that up for you...",
                "latency_ms": 650
            }
        ],
        "reference_transcript": "optional ground truth for WER calculation",
        "metadata": {
            "user_hung_up": false,
            "transferred_to_human": false,
            "error_occurred": false
        }
    }
"""

import argparse
import json
import re
import sys
from pathlib import Path


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate using Levenshtein distance on words.

    Returns WER as a float (0.0 = perfect, 1.0 = 100% error rate).
    """
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    # Dynamic programming for edit distance
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]

    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j

    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(
                    d[i - 1][j] + 1,      # deletion
                    d[i][j - 1] + 1,      # insertion
                    d[i - 1][j - 1] + 1,  # substitution
                )

    return min(d[len(ref_words)][len(hyp_words)] / len(ref_words), 1.0)


def score_completion(call: dict) -> float:
    """Score call completion. 0.0 to 1.0."""
    outcome = call.get("outcome", "unknown")
    metadata = call.get("metadata", {})

    if outcome == "resolved":
        return 1.0
    elif outcome == "transferred":
        # Transfer is acceptable but not ideal
        return 0.6
    elif metadata.get("user_hung_up"):
        return 0.1
    elif metadata.get("error_occurred"):
        return 0.0
    elif outcome == "abandoned":
        return 0.2
    return 0.3


def score_repetition(call: dict) -> float:
    """Score user repetition rate. Lower repetition = higher score. 0.0 to 1.0."""
    turns = call.get("turns", [])
    user_messages = [t["content"].lower().strip() for t in turns if t["role"] == "user"]

    if len(user_messages) <= 1:
        return 1.0

    # Check for similar consecutive messages (user repeating themselves)
    repetitions = 0
    for i in range(1, len(user_messages)):
        # Simple similarity: check if messages share > 60% of words
        words_a = set(user_messages[i - 1].split())
        words_b = set(user_messages[i].split())
        if words_a and words_b:
            overlap = len(words_a & words_b) / max(len(words_a), len(words_b))
            if overlap > 0.6:
                repetitions += 1

    repetition_rate = repetitions / (len(user_messages) - 1)

    if repetition_rate == 0:
        return 1.0
    elif repetition_rate < 0.15:
        return 0.8
    elif repetition_rate < 0.3:
        return 0.5
    return 0.2


def score_latency(call: dict) -> float:
    """Score response latency. Lower = better. 0.0 to 1.0."""
    turns = call.get("turns", [])
    latencies = [
        t["latency_ms"]
        for t in turns
        if t["role"] == "assistant" and t.get("latency_ms") is not None
    ]

    if not latencies:
        return 0.5  # No data

    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    score = 1.0

    # Penalize high average latency
    if avg_latency > 1000:
        score -= 0.4
    elif avg_latency > 700:
        score -= 0.2
    elif avg_latency > 500:
        score -= 0.1

    # Penalize spikes
    if max_latency > 2000:
        score -= 0.3
    elif max_latency > 1500:
        score -= 0.1

    return max(score, 0.0)


def score_call(call: dict) -> dict:
    """Score a single call across all dimensions."""
    scores = {
        "completion": round(score_completion(call), 2),
        "low_repetition": round(score_repetition(call), 2),
        "latency": round(score_latency(call), 2),
    }

    # WER if reference transcript available
    ref = call.get("reference_transcript")
    if ref:
        # Combine all assistant turns as hypothesis
        assistant_text = " ".join(
            t["content"] for t in call.get("turns", []) if t["role"] == "assistant"
        )
        wer = calculate_wer(ref, assistant_text)
        scores["wer"] = round(wer, 3)
        scores["wer_score"] = round(max(1.0 - wer, 0.0), 2)

    # Overall score (weighted average)
    weights = {"completion": 0.4, "low_repetition": 0.25, "latency": 0.2}
    if "wer_score" in scores:
        weights["wer_score"] = 0.15
        # Rebalance
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}

    overall = sum(scores.get(k, 0) * w for k, w in weights.items())
    scores["overall"] = round(overall, 2)

    return {
        "call_id": call.get("call_id", "unknown"),
        "duration_seconds": call.get("duration_seconds"),
        "outcome": call.get("outcome"),
        "scores": scores,
    }


def aggregate_scores(results: list[dict]) -> dict:
    """Compute aggregate statistics."""
    if not results:
        return {"count": 0}

    dimensions = list(results[0]["scores"].keys())
    aggregates = {}

    for dim in dimensions:
        values = [r["scores"][dim] for r in results if dim in r["scores"]]
        if values:
            aggregates[dim] = {
                "mean": round(sum(values) / len(values), 3),
                "min": round(min(values), 3),
                "max": round(max(values), 3),
            }

    outcomes = [r["outcome"] for r in results if r.get("outcome")]
    outcome_counts = {}
    for o in outcomes:
        outcome_counts[o] = outcome_counts.get(o, 0) + 1

    return {
        "count": len(results),
        "metrics": aggregates,
        "outcome_distribution": outcome_counts,
    }


def main():
    parser = argparse.ArgumentParser(description="Score voice bot call quality.")
    parser.add_argument("--input", required=True, help="JSONL file with call data")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    calls = []
    for line in input_path.read_text().strip().split("\n"):
        if line.strip():
            calls.append(json.loads(line))

    results = [score_call(call) for call in calls]
    aggregate = aggregate_scores(results)

    output = {"summary": aggregate, "results": results}
    output_json = json.dumps(output, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Results written to {args.output}")
    else:
        print(output_json)

    # Summary to stderr
    print(f"\n--- Call Quality ({aggregate['count']} calls) ---", file=sys.stderr)
    for dim, stats in aggregate.get("metrics", {}).items():
        print(f"  {dim}: mean={stats['mean']:.2f}", file=sys.stderr)
    if aggregate.get("outcome_distribution"):
        print(f"  outcomes: {aggregate['outcome_distribution']}", file=sys.stderr)


if __name__ == "__main__":
    main()
