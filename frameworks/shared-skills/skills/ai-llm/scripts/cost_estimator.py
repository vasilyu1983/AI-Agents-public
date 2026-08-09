#!/usr/bin/env python3
"""
cost_estimator.py — LLM cost estimator across providers (stdlib-only).

Given a prompt file and token counts, emits per-provider cost in USD.
Token counts may be provided via flags or auto-estimated from a prompt file
using a simple whitespace/punctuation splitter (approx. 0.75 words per token).

Provider prices are embedded in the script (update as rates change).
Price table last verified: 2026-04-12. Treat estimates as stale after 30 days
unless you have refreshed prices from provider pricing pages.

Usage:
    # Estimate from token counts directly
    python cost_estimator.py --input-tokens 500 --output-tokens 200

    # Estimate from a prompt file (auto-counts input tokens) + output count
    python cost_estimator.py --prompt-file prompt.txt --output-tokens 200

    # Filter to specific providers
    python cost_estimator.py --input-tokens 1000 --output-tokens 500 --providers openai anthropic

    # Output JSON
    python cost_estimator.py --input-tokens 1000 --output-tokens 500 --json

    python cost_estimator.py --help
"""

import argparse
from datetime import date
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Provider pricing table — USD per 1M tokens
# Update these when provider pricing changes.
# ---------------------------------------------------------------------------

PRICE_TABLE_LAST_VERIFIED = date.fromisoformat("2026-07-11")
PRICE_TABLE_STALE_AFTER_DAYS = 30

PROVIDERS: dict[str, dict] = {
    "openai/gpt-5.6-sol": {
        "input_per_1m": 5.00,
        "output_per_1m": 30.00,
        "notes": "GPT-5.6 Sol (top tier, long-horizon/agentic/cyber-science; public since 2026-07-09)",
    },
    "openai/gpt-5.6-terra": {
        "input_per_1m": 2.50,
        "output_per_1m": 15.00,
        "notes": "GPT-5.6 Terra (balanced efficiency/capability)",
    },
    "openai/gpt-5.6-luna": {
        "input_per_1m": 1.00,
        "output_per_1m": 6.00,
        "notes": "GPT-5.6 Luna (speed/cost tier)",
    },
    "anthropic/claude-fable-5": {
        "input_per_1m": 10.00,
        "output_per_1m": 50.00,
        "notes": "Claude Fable 5 (GA 2026-06-09); <5% of high-risk sessions fall back to Opus 4.8 billing",
    },
    "anthropic/claude-opus-4-8": {
        "input_per_1m": 5.00,
        "output_per_1m": 25.00,
        "notes": "Claude Opus 4.8 (standalone flagship)",
    },
    "anthropic/claude-sonnet-5": {
        "input_per_1m": 3.00,
        "output_per_1m": 15.00,
        "notes": "Claude Sonnet 5 (GA 2026-06-30); intro price $2/$10 through 2026-08-31 — confirm which rate applies",
    },
    "anthropic/claude-haiku-4-5": {
        "input_per_1m": 1.00,
        "output_per_1m": 5.00,
        "notes": "Claude Haiku 4.5 (fastest tier)",
    },
    "google/gemini-3.1-pro": {
        "input_per_1m": 2.00,
        "output_per_1m": 12.00,
        "notes": "Gemini 3.1 Pro, <=200k ctx (doubles above 200k); third-party aggregator figures — verify at ai.google.dev/gemini-api/docs/pricing",
    },
    "google/gemini-3.5-flash": {
        "input_per_1m": 1.50,
        "output_per_1m": 9.00,
        "notes": "Gemini 3.5 Flash (GA 2026-05-19); third-party aggregator figures — verify at ai.google.dev/gemini-api/docs/pricing",
    },
    "mistral/mistral-large": {
        "input_per_1m": 2.00,
        "output_per_1m": 6.00,
        "notes": "Mistral Large 2 (unverified this cycle — confirm at mistral.ai before use)",
    },
    "mistral/mistral-small": {
        "input_per_1m": 0.10,
        "output_per_1m": 0.30,
        "notes": "Mistral Small 3 (unverified this cycle — confirm at mistral.ai before use)",
    },
    "groq/llama-4-scout": {
        "input_per_1m": 0.11,
        "output_per_1m": 0.34,
        "notes": "Llama 4 Scout on Groq (unverified this cycle — confirm at groq.com before use)",
    },
    "together/qwen3-235b": {
        "input_per_1m": 0.90,
        "output_per_1m": 0.90,
        "notes": "Qwen3-235B-A22B on Together AI (unverified this cycle — confirm at together.ai before use)",
    },
}


def estimate_tokens_from_text(text: str) -> int:
    """Very rough token estimator: ~4 chars per token (common heuristic)."""
    return max(1, len(text) // 4)


def compute_cost(input_tokens: int, output_tokens: int, provider_key: str, pricing: dict) -> dict:
    input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
    total = input_cost + output_cost
    return {
        "provider": provider_key,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total, 6),
        "notes": pricing.get("notes", ""),
    }


def run(
    input_tokens: int,
    output_tokens: int,
    provider_filter: list[str] | None,
    as_json: bool,
    allow_stale_prices: bool,
) -> int:
    price_table_age_days = (date.today() - PRICE_TABLE_LAST_VERIFIED).days
    price_table_stale = price_table_age_days > PRICE_TABLE_STALE_AFTER_DAYS
    if price_table_stale and not allow_stale_prices:
        print(
            "[WARN] Embedded provider prices are "
            f"{price_table_age_days} days old "
            f"(last verified {PRICE_TABLE_LAST_VERIFIED.isoformat()}); "
            "verify live provider pricing before using this for budgets.",
            file=sys.stderr,
        )

    selected = {
        k: v
        for k, v in PROVIDERS.items()
        if not provider_filter
        or any(f.lower() in k.lower() for f in provider_filter)
    }

    if not selected:
        print(f"[ERROR] No providers matched filter: {provider_filter}", file=sys.stderr)
        return 2

    rows = [compute_cost(input_tokens, output_tokens, k, v) for k, v in selected.items()]
    rows.sort(key=lambda r: r["total_cost_usd"])

    if as_json:
        print(
            json.dumps(
                {
                    "metadata": {
                        "price_table_last_verified": PRICE_TABLE_LAST_VERIFIED.isoformat(),
                        "price_table_age_days": price_table_age_days,
                        "price_table_stale": price_table_stale,
                    },
                    "estimates": rows,
                },
                indent=2,
            )
        )
        return 0

    print(f"\nCost estimate — input: {input_tokens:,} tokens  output: {output_tokens:,} tokens\n")
    print(
        "Price table: "
        f"last verified {PRICE_TABLE_LAST_VERIFIED.isoformat()} "
        f"({price_table_age_days} days old)"
    )
    print()
    header = f"{'Provider':<35} {'Total USD':>12} {'Input USD':>12} {'Output USD':>12}  Notes"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['provider']:<35} "
            f"${row['total_cost_usd']:>11.6f} "
            f"${row['input_cost_usd']:>11.6f} "
            f"${row['output_cost_usd']:>11.6f}  {row['notes']}"
        )
    print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LLM cost estimator across providers (USD).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    tok_group = parser.add_mutually_exclusive_group(required=True)
    tok_group.add_argument("--input-tokens", type=int, help="Number of input tokens")
    tok_group.add_argument("--prompt-file", type=Path, help="Prompt text file (auto-counts tokens)")

    parser.add_argument("--output-tokens", type=int, required=True, help="Number of output tokens")
    parser.add_argument(
        "--providers",
        nargs="+",
        metavar="PROVIDER",
        help="Filter providers by substring (e.g. openai anthropic). Default: all.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    parser.add_argument(
        "--allow-stale-prices",
        action="store_true",
        help="Suppress stale-price warning when using the embedded pricing table.",
    )
    args = parser.parse_args()

    if args.prompt_file:
        try:
            text = args.prompt_file.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            print(f"[ERROR] Prompt file not found: {args.prompt_file}", file=sys.stderr)
            sys.exit(2)
        input_tokens = estimate_tokens_from_text(text)
        print(f"[INFO] Auto-estimated {input_tokens} input tokens from {args.prompt_file}")
    else:
        input_tokens = args.input_tokens

    sys.exit(
        run(
            input_tokens,
            args.output_tokens,
            args.providers,
            args.as_json,
            args.allow_stale_prices,
        )
    )


if __name__ == "__main__":
    main()
