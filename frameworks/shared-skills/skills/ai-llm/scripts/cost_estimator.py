#!/usr/bin/env python3
"""
cost_estimator.py — LLM cost estimator across providers (stdlib-only).

Given a prompt file and token counts, emits per-provider cost in USD.
Token counts may be provided via flags or auto-estimated from a prompt file
using a simple whitespace/punctuation splitter (approx. 0.75 words per token).

Provider prices are embedded in the script (update as rates change). The
authoritative verification date is PRICE_TABLE_LAST_VERIFIED below — do not
restate it here, or the two drift. Estimates warn on stderr once the table is
older than PRICE_TABLE_STALE_AFTER_DAYS; pass --allow-stale-prices to suppress.

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

# Import the resolver from this skill's OWN _lib/. The skill is self-contained:
# it carries its own _lib/ and data/, so it works detached from the repo
# (public-repo clone, single-folder copy, plugin). resolve() first because
# skills deploy as symlinks, so a lexical path escapes into the deployment root.
_here = Path(__file__).resolve()
sys.path.insert(0, str(_here.parents[1] / "_lib"))
try:
    from resolve_versions import load_pricing, pricing_path
except ImportError:  # resolver missing — fall back to the embedded table
    load_pricing = None
    pricing_path = None


# ---------------------------------------------------------------------------
# Provider pricing table — USD per 1M tokens.
#
# The authoritative table is this skill's own data/model-pricing.json, read at
# runtime — the same file whether the skill runs from the repo or from
# ~/.claude, ~/.agents or ~/.codex. The dict below is a FALLBACK for when that
# file cannot be found — it is not the source of truth, so prefer editing the
# JSON. Both carry the same last-verified date and expire the same way.
# ---------------------------------------------------------------------------

PRICE_TABLE_LAST_VERIFIED = date.fromisoformat("2026-08-10")
PRICE_TABLE_STALE_AFTER_DAYS = 30

FALLBACK_PROVIDERS: dict[str, dict] = {
    "openai/gpt-5.6-sol": {
        "input_per_1m": 5.00,
        "output_per_1m": 30.00,
        "notes": "GPT-5.6 Sol (top tier, long-horizon/agentic/cyber-science; public since 2026-07-09)",
    },
    "openai/gpt-5.6-terra": {
        "input_per_1m": 2.00,
        "output_per_1m": 12.00,
        "notes": "GPT-5.6 Terra (balanced efficiency/capability)",
    },
    "openai/gpt-5.6-luna": {
        "input_per_1m": 0.20,
        "output_per_1m": 1.20,
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
        "notes": ("Claude Haiku 4.5 (fastest tier). $0.80/$4.00 is Haiku 3.5 "
                  "(retired) — do not confuse the two."),
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
}


def _load_providers() -> tuple[dict[str, dict], str]:
    """Return (pricing table, provenance label).

    Prefers the shared data file so every skill quotes identical numbers; falls
    back to the embedded dict when it cannot be located, rather than failing.
    """
    if load_pricing is None:
        return FALLBACK_PROVIDERS, "embedded fallback (resolver not importable)"

    doc = load_pricing(__file__)
    models = doc.get("models") if isinstance(doc, dict) else None
    if not isinstance(models, dict) or not models:
        return FALLBACK_PROVIDERS, "embedded fallback (shared table unavailable)"

    table = {
        key: entry for key, entry in models.items()
        if isinstance(entry, dict)
        and "input_per_1m" in entry and "output_per_1m" in entry
    }
    if not table:
        return FALLBACK_PROVIDERS, "embedded fallback (shared table unusable)"

    path = pricing_path(__file__) if pricing_path else None
    return table, f"shared: {path}" if path else "shared"


PROVIDERS, PRICING_SOURCE = _load_providers()


def _price_table_freshness() -> tuple[date, int]:
    """Return (last_verified, stale_after_days) for the table actually in use."""
    if load_pricing is not None and PRICING_SOURCE.startswith("shared"):
        doc = load_pricing(__file__)
        stamp = doc.get("last_verified")
        window = doc.get("stale_after_days")
        if isinstance(stamp, str):
            try:
                return (
                    date.fromisoformat(stamp),
                    window if isinstance(window, int) else PRICE_TABLE_STALE_AFTER_DAYS,
                )
            except ValueError:
                pass
    return PRICE_TABLE_LAST_VERIFIED, PRICE_TABLE_STALE_AFTER_DAYS


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
    # Date the table actually in use, not the module constant: when the shared
    # file is driving, its last_verified is the one that matters.
    verified, window = _price_table_freshness()
    price_table_age_days = (date.today() - verified).days
    price_table_stale = price_table_age_days > window
    if price_table_stale and not allow_stale_prices:
        print(
            f"[WARN] Provider prices are {price_table_age_days} days old "
            f"(last verified {verified.isoformat()}, source: {PRICING_SOURCE}); "
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
                        "price_table_last_verified": verified.isoformat(),
                        "price_table_age_days": price_table_age_days,
                        "price_table_stale": price_table_stale,
                        "price_table_source": PRICING_SOURCE,
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
        f"last verified {verified.isoformat()} "
        f"({price_table_age_days} days old) — {PRICING_SOURCE}"
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
