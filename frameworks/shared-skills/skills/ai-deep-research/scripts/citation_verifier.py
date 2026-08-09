#!/usr/bin/env python3
"""
citation_verifier.py — stdlib-only citation verifier for deep-research workflows.

Reads a JSONL file of {claim, source_url, supporting_quote} entries.
Checks each entry and reports:
  - supported: supporting_quote is non-empty and substantively matches the claim
  - unsupported: no supporting_quote or quote is generic/empty
  - needs_review: quote present but weak signal

Usage:
    python3 scripts/citation_verifier.py --input claims.jsonl
    python3 scripts/citation_verifier.py --input claims.jsonl --strict
    python3 scripts/citation_verifier.py --input claims.jsonl --output report.jsonl

Input JSONL format (one JSON object per line):
    {"claim": "...", "source_url": "...", "supporting_quote": "..."}

Optional fields:
    {"claim": "...", "source_url": "...", "supporting_quote": "...",
     "ledger_id": "L001", "evidence_tier": "primary", "date_published": "2025-01-01"}

Exit codes:
    0 — all claims supported
    1 — one or more unsupported claims found
    2 — input file not found or malformed
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_QUOTE_WORDS = 5          # Minimum word count for a quote to be considered substantive
GENERIC_QUOTES = {            # Exact or near-exact quotes that add no evidence
    "",
    "see above",
    "see source",
    "n/a",
    "na",
    "none",
    "not available",
    "not provided",
    "todo",
    "tbd",
    "-",
    "...",
}


# ---------------------------------------------------------------------------
# Core verification logic
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation from edges."""
    return re.sub(r"\s+", " ", text.strip().lower().strip(".,;:!?"))


def quote_is_substantive(quote: str) -> bool:
    """Return True if the quote meets the minimum content bar."""
    q = normalize(quote)
    if q in GENERIC_QUOTES:
        return False
    word_count = len(q.split())
    return word_count >= MIN_QUOTE_WORDS


def claim_words(claim: str) -> set:
    """Extract meaningful words from a claim (lowercase, no stopwords)."""
    stopwords = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "it", "its",
        "this", "that", "these", "those", "as", "if", "so", "than", "not",
    }
    words = re.findall(r"\b[a-z0-9]+\b", claim.lower())
    return {w for w in words if w not in stopwords and len(w) > 2}


def compute_overlap(claim: str, quote: str) -> float:
    """
    Return the fraction of meaningful claim words present in the quote.
    Range [0.0, 1.0]. A score >= 0.3 is treated as a weak positive signal.
    This is a heuristic — it does not verify semantic accuracy.
    """
    claim_kw = claim_words(claim)
    if not claim_kw:
        return 0.0
    quote_lower = quote.lower()
    matched = sum(1 for w in claim_kw if w in quote_lower)
    return matched / len(claim_kw)


def verify_entry(entry: dict, strict: bool = False) -> dict:
    """
    Verify a single claim entry.

    Returns a result dict with:
        claim, source_url, verdict, reason, overlap_score
    Optional passthrough fields: ledger_id, evidence_tier, date_published
    """
    claim = str(entry.get("claim", "")).strip()
    source_url = str(entry.get("source_url", "")).strip()
    quote = str(entry.get("supporting_quote", "")).strip()

    result = {
        "claim": claim,
        "source_url": source_url,
        "supporting_quote": quote,
        "ledger_id": entry.get("ledger_id"),
        "evidence_tier": entry.get("evidence_tier"),
        "date_published": entry.get("date_published"),
        "verdict": None,
        "reason": None,
        "overlap_score": None,
    }

    # --- Guard: empty claim ---
    if not claim:
        result["verdict"] = "needs_review"
        result["reason"] = "Empty claim — cannot verify."
        result["overlap_score"] = 0.0
        return result

    # --- Guard: no URL ---
    if not source_url:
        result["verdict"] = "unsupported"
        result["reason"] = "No source URL provided."
        result["overlap_score"] = 0.0
        return result

    # --- Guard: no quote ---
    if not quote:
        result["verdict"] = "unsupported"
        result["reason"] = "No supporting quote provided."
        result["overlap_score"] = 0.0
        return result

    # --- Guard: generic quote ---
    if normalize(quote) in GENERIC_QUOTES:
        result["verdict"] = "unsupported"
        result["reason"] = f"Supporting quote is a generic placeholder: {quote!r}."
        result["overlap_score"] = 0.0
        return result

    # --- Check quote substantiveness ---
    if not quote_is_substantive(quote):
        result["verdict"] = "unsupported"
        result["reason"] = (
            f"Supporting quote is too short ({len(quote.split())} words); "
            f"minimum is {MIN_QUOTE_WORDS} words."
        )
        result["overlap_score"] = 0.0
        return result

    # --- Compute keyword overlap ---
    overlap = compute_overlap(claim, quote)
    result["overlap_score"] = round(overlap, 3)

    # --- Strict mode: require overlap >= 0.3 ---
    if strict and overlap < 0.3:
        result["verdict"] = "needs_review"
        result["reason"] = (
            f"Overlap score {overlap:.2f} is below 0.30 threshold in strict mode. "
            "Quote may not directly support the claim."
        )
        return result

    # --- Evidence tier check ---
    tier = str(entry.get("evidence_tier", "")).lower()
    if tier == "model-working-notes":
        result["verdict"] = "unsupported"
        result["reason"] = (
            "evidence_tier is 'model-working-notes'; model-generated text "
            "cannot be used as a primary citation."
        )
        return result

    # --- Passed all checks ---
    if overlap >= 0.3:
        result["verdict"] = "supported"
        result["reason"] = f"Quote is substantive and overlaps with claim (score: {overlap:.2f})."
    else:
        result["verdict"] = "needs_review"
        result["reason"] = (
            f"Quote is substantive but low keyword overlap (score: {overlap:.2f}). "
            "Manual review recommended."
        )

    return result


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list:
    """Load a JSONL file; return list of dicts. Raises on malformed lines."""
    entries = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"ERROR: malformed JSON on line {lineno}: {exc}", file=sys.stderr)
                sys.exit(2)
    return entries


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_summary(results: list, strict: bool) -> None:
    """Print a human-readable summary to stdout."""
    total = len(results)
    supported = sum(1 for r in results if r["verdict"] == "supported")
    unsupported = sum(1 for r in results if r["verdict"] == "unsupported")
    needs_review = sum(1 for r in results if r["verdict"] == "needs_review")

    mode = "strict" if strict else "standard"
    print(f"\n=== Citation Verifier Report ({mode} mode) ===")
    print(f"Total claims:    {total}")
    print(f"  Supported:     {supported}")
    print(f"  Unsupported:   {unsupported}")
    print(f"  Needs review:  {needs_review}")
    print()

    if unsupported or needs_review:
        print("--- Issues ---")
        for r in results:
            if r["verdict"] in ("unsupported", "needs_review"):
                ledger = f" [{r['ledger_id']}]" if r.get("ledger_id") else ""
                tier = f" (tier: {r['evidence_tier']})" if r.get("evidence_tier") else ""
                print(f"\n[{r['verdict'].upper()}]{ledger}{tier}")
                print(f"  Claim:  {r['claim'][:120]}")
                print(f"  URL:    {r['source_url'][:100]}")
                print(f"  Reason: {r['reason']}")
    else:
        print("All claims are supported.")


def write_report(results: list, output_path: Path) -> None:
    """Write results as JSONL to output_path."""
    with output_path.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nReport written to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Verify citations in a JSONL file of {claim, source_url, supporting_quote}.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--input", "-i",
        required=True,
        metavar="FILE",
        help="Path to input JSONL file.",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Optional path for JSONL report output.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Require keyword overlap >= 0.30 for 'supported' verdict.",
    )
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    entries = load_jsonl(input_path)
    if not entries:
        print("WARNING: input file is empty — nothing to verify.", file=sys.stderr)
        sys.exit(0)

    results = [verify_entry(entry, strict=args.strict) for entry in entries]

    print_summary(results, strict=args.strict)

    if args.output:
        write_report(results, Path(args.output))

    # Exit 1 if any claims are unsupported
    has_issues = any(r["verdict"] == "unsupported" for r in results)
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
