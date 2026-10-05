#!/usr/bin/env python3
"""Score a context-layer assessment against assets/eval/context-layer-scorecard.md.

Input: JSONL rows {"category": "...", "item": "...", "score": 0|1|2, "notes": "..."}.
Category and item text are matched after normalization (case, whitespace, backticks,
arrows and dashes), so rows copied from the markdown scorecard match the table below.

Exit codes: 0 scored; 1 validation failure (unknown or missing items, bad scores);
2 unreadable input. Missing items fail unless --allow-partial is given, in which
case they are reported and the total is computed over the scored subset.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SCORECARD = {
    "Operational Truth": [
        "Live user/customer facts fetched from source-of-truth systems",
        "Tenant and ACL boundaries explicit",
    ],
    "Memory": [
        "Structured memory exists",
        "Memory has provenance, confidence, and expiry",
    ],
    "Retrieval": [
        "Retrieval has evidence IDs and freshness",
        "Retrieval and answer quality are evaluated separately",
    ],
    "Graph": [
        "Graph use is justified by the problem",
        "Inferred edges are separated from operational edges",
        "Temporal validity and fact expiry are defined for graph edges",
    ],
    "Context Assembly": [
        "Per-surface bundles are explicit",
        "Model projection is bounded and allowlisted",
        "Context compression and token budget management are explicit",
        "Pointer-first refs used for large or tool-rich surfaces before loading payloads",
        "Managed memory or hosted retrieval boundaries are explicit (truth, audit, delete)",
        "Multimodal artifacts use typed projections rather than raw payload stuffing",
    ],
    "Emotional Context": [
        "Emotional/mood signals captured and passed to context assembly",
        "AI responses modulate tone based on user state (not just static brand voice)",
        "Context metadata presented as warm narrative (emotional frame), not raw metrics",
        "Cross-surface signal flow exists (e.g., journaling mood -> chat context)",
    ],
    "Feedback": [
        "Corrections and outcomes are captured",
        "Learning loop improves derived context without overwriting truth",
        "Inline reactions tied to context bundle IDs (not just general satisfaction)",
        "Feedback fatigue managed (limited surfaces, one-shot per response)",
    ],
    "Pattern Selection And Sweep": [
        "Design cites named pattern IDs from patterns-catalog.md (P1-P25)",
        "Anti-pattern sweep run against anti-patterns-catalog.md (A1-A49)",
        "Each applicable anti-pattern marked BLOCKED by <pattern> or NOT BLOCKED (accepted: ...)",
        "Contradictions categorized as attribution / temporal / stale with ingest-time detection",
    ],
    "Knowledge Compilation": [
        "Extract -> reconcile -> supersede pipeline runs at ingest, not at query time",
        "Every claim tagged extracted | inferred | ambiguous with source_episode_id",
        "Confidence decays with time and strengthens with reinforcement",
        "Recurring queries hit compiled synthesis pages, not re-run retrieval end-to-end",
    ],
    "Review & Inspection Surface": [
        "Every fact can be traced to a raw source episode in <=3 actions",
        "Per-fact confidence is visible to operators",
        "Contradictions appear in a queue grouped by category, not only as page flags",
        "Approve / reject / supersede workflow exists (staging -> production) when the KB is user-visible",
        "Ingest-time contradiction detection confirmed (not query-time)",
        "Forget path is non-destructive (closes validity window; hard delete reserved for compliance)",
    ],
    "Context Window Hygiene": [
        "F1 context poisoning has a documented defense (provenance + confidence + invalidation)",
        "F2 context distraction has a documented defense (token-budget cap + history compaction)",
        "F3 context clash has a documented defense (ingest-time contradiction detection + per-surface tool allowlist)",
        "F4 context confusion has a documented defense (just-in-time selection + surface-tuned tool allowlist)",
        "Runtime verbs write / select / compress / isolate are explicitly assigned to an assembly-layer component",
        "Runtime refs resolve only on demand and preserve provenance after expansion",
        "Tool-result compaction recipe wired into the agent loop (A24 blocked)",
    ],
    "Sub-Agent Isolation": [
        "Long-horizon sub-tasks use P11 sub-agents rather than the parent window",
        "Sub-agent handoff contract defined (task brief, tool allowlist, output schema, token budget)",
        "Sub-agent summary preserves citations or episode IDs so the parent can re-fetch detail",
    ],
    "Security": [
        "Token-origin tagging in the system prompt distinguishes instructions from data (A23 blocked)",
        "Tool allowlists are per-surface, not global",
        "Adversarial / injection corpus runs in evals and gates release",
        "PII scrubbing runs before embed and before log",
        "Destructive or external-effect tools require explicit confirmation",
        "Cross-tenant smoke tests pass at storage layer, not only at query layer",
    ],
    "State Maintenance": [
        "Current state rows link to supporting evidence spans (P22)",
        "Section-level scope and sensitivity filters apply inside each retrieval leg before fusion (P23, P24)",
        "Tombstones cascade to derived indexes, graph, and observations (A40 blocked)",
        "State-maintenance eval covers update, rename, relationship change, deletion, supersession, as-of, duplicate and out-of-order events, stale secondary sources, role confusion, and scope leakage",
    ],
}

BANDS = [
    (0, 29, "fragmented context system"),
    (30, 49, "solid partial context layer"),
    (50, 73, "strong context-layer architecture with named patterns, basic hygiene, and feedback"),
    (74, 114, "complete context layer"),
]

_NORMALIZE = [
    ("→", "->"),  # right arrow
    ("≤", "<="),  # less-or-equal
    ("–", "-"),  # en dash
    ("—", "-"),  # em dash
    ("`", ""),
    ("references/", ""),
]


def normalize(text: str) -> str:
    """Fold the markdown scorecard's typography onto the script's ASCII keys."""
    out = str(text).strip().lower()
    for old, new in _NORMALIZE:
        out = out.replace(old, new)
    out = re.sub(r"\s*\([^)]*only\)$", "", out)  # e.g. "(P7 designs only)" category suffix
    return re.sub(r"\s+", " ", out)


_INDEX = {
    (normalize(category), normalize(item)): (category, item)
    for category, items in SCORECARD.items()
    for item in items
}
_CATEGORY_INDEX = {normalize(category): category for category in SCORECARD}


def _load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"line {line_number}: row must be an object")
            rows.append(row)
    return rows


def _interpret(score: int) -> str:
    for low, high, label in BANDS:
        if low <= score <= high:
            return label
    return "unknown"


def score_rows(rows: list[dict]) -> tuple[dict[tuple[str, str], int], list[str]]:
    """Return {(category, item): score} plus a list of validation errors."""
    scored: dict[tuple[str, str], int] = {}
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        category = row.get("category", "")
        item = row.get("item", "")
        score = row.get("score")
        if score not in (0, 1, 2) or isinstance(score, bool):
            errors.append(f"row {index}: score must be 0, 1, or 2 (got {score!r})")
            continue
        key = (normalize(category), normalize(item))
        if key not in _INDEX:
            if key[0] in _CATEGORY_INDEX:
                errors.append(f"row {index}: unknown item in [{category}]: {item!r}")
            else:
                errors.append(f"row {index}: unknown category {category!r}")
            continue
        canonical = _INDEX[key]
        if canonical in scored:
            errors.append(f"row {index}: duplicate item [{canonical[0]}] {canonical[1]}")
            continue
        scored[canonical] = score
    return scored, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score a context-layer assessment against the scorecard.",
    )
    parser.add_argument(
        "path",
        help=(
            "JSONL file with rows: "
            '{"category": "...", "item": "...", "score": 0|1|2, "notes": "..."}'
        ),
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Report missing scorecard items instead of failing on them.",
    )
    args = parser.parse_args(argv)

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        rows = _load_rows(path)
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not rows:
        print("ERROR: no rows found", file=sys.stderr)
        return 2

    scored, errors = score_rows(rows)

    all_expected = {(cat, item) for cat, items in SCORECARD.items() for item in items}
    missing = sorted(all_expected - set(scored))
    if missing and not args.allow_partial:
        errors.extend(f"missing scorecard item: [{cat}] {item}" for cat, item in missing)

    if errors:
        print("VALIDATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
        return 1

    if missing:
        print("WARNING: missing scorecard items (--allow-partial):")
        for cat, item in missing:
            print(f"  - [{cat}] {item}")
        print()

    total = 0
    max_possible = len(all_expected) * 2
    print("CONTEXT LAYER SCORECARD")
    print("=" * 50)

    for category, items in SCORECARD.items():
        cat_total = 0
        cat_max = len(items) * 2
        for item in items:
            score = scored.get((category, item))
            marker = f"{score}/2" if score is not None else "MISSING"
            print(f"  [{marker}] {item}")
            if score is not None:
                cat_total += score
        total += cat_total
        print(f"  {category}: {cat_total}/{cat_max}")
        print()

    print("=" * 50)
    print(f"TOTAL: {total}/{max_possible}")
    if missing:
        print(f"SCORED ITEMS: {len(scored)}/{len(all_expected)} (partial; band is provisional)")
    print(f"INTERPRETATION: {_interpret(total)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
