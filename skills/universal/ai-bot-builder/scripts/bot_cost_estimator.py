#!/usr/bin/env python3
"""Per-conversation cost estimator for AI bots.

Estimates the cost of running a bot conversation given model selection,
average turn count, tokens per turn, and tool call frequency.

Usage:
    python3 bot_cost_estimator.py --pricing rates.json --model my-model --avg-turns 8
    python3 bot_cost_estimator.py --pricing rates.json --model my-model --tool-calls 3 --volume 10000
    python3 bot_cost_estimator.py --pricing rates.json --compare-all

Rates are never built in: published model prices change within weeks, so an
embedded table prints confident wrong numbers. Copy the rates for the models
you are comparing from each provider's pricing page into a --pricing file
(schema: ../assets/pricing-template.json). The dated price file of
ops-cost-optimization's cost_estimator.py ({"checked", "models": {id:
{"input_per_1m", "output_per_1m"}}}, optional cache_read_per_1m and
cache_write_per_1m) is also accepted, so one file can feed both estimators.
Without --pricing the script prints no estimate and exits 2.

Input checks match ops-cost-optimization's cost_estimator.py: a key listed twice
in one object, a NaN, Infinity or negative rate, or a non-finite estimate exits
2. In the dated format every model id is priced, "_"-prefixed ones included;
only the alias map skips "_" note keys and "<" template rows. Pass
--max-age-days N whenever the estimate feeds a decision: a dated file whose
"checked" date is more than N days old then exits 2 (an alias map has no date,
so it exits 2 too). Costs are carried unrounded into the monthly and annual
projections and rounded to 6 decimal places only for output.
"""

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path


NO_PRICING_MESSAGE = (
    "Error: no rates supplied, so no cost is estimated. Pass --pricing <file.json> with "
    "rates from each provider's pricing page; schema: assets/pricing-template.json."
)


DATED_FIELDS = {
    "input_per_1m": "input_per_million",
    "output_per_1m": "output_per_million",
    "cache_read_per_1m": "cache_read_per_million",
    "cache_write_per_1m": "cache_write_per_million",
}


def _reject_duplicate_keys(pairs):
    # Same rule as ops-cost-optimization's cost_estimator.py: json.loads would keep
    # the last duplicate silently, pricing a model at whichever row came second.
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key {key!r}: each key may appear once per object")
        seen[key] = value
    return seen


def from_dated_price_file(doc: dict, path: Path, max_age_days=None) -> dict:
    """Convert the dated price file of ops-cost-optimization's cost_estimator.py
    ({"checked": "YYYY-MM-DD", "models": {id: {"input_per_1m": ...}}}) to this
    script's alias map, so one file serves both estimators. Exits 2 on a bad
    date or on prices older than max_age_days."""
    checked = doc.get("checked")
    try:
        checked_date = date.fromisoformat(checked) if isinstance(checked, str) else None
    except ValueError:
        checked_date = None
    if checked_date is None or checked_date > date.today():
        print(f"Error: --pricing file {path} needs \"checked\" as a past or current YYYY-MM-DD date, "
              f"got {checked!r}", file=sys.stderr)
        sys.exit(2)
    models = doc["models"]
    if not isinstance(models, dict):
        print(f"Error: --pricing file {path}: \"models\" must be an object keyed by model", file=sys.stderr)
        sys.exit(2)
    age_days = (date.today() - checked_date).days
    if max_age_days is not None and age_days > max_age_days:
        print(f"Error: prices in {path} were checked {checked_date.isoformat()}, {age_days} days ago, "
              f"over --max-age-days {max_age_days}: re-read the provider pricing pages, update the "
              "rates and \"checked\", then rerun", file=sys.stderr)
        sys.exit(2)
    print(f"Prices checked {checked_date.isoformat()} ({age_days} days ago)", file=sys.stderr)
    converted = {}
    for model_id, entry in models.items():
        if not isinstance(entry, dict):
            converted[model_id] = entry  # rejected with the usual message below
            continue
        converted[model_id] = {"display_name": model_id,
                               **{DATED_FIELDS.get(k, k): v for k, v in entry.items()}}
    return converted


def load_pricing_file(path: Path, max_age_days=None) -> dict:
    """Return {alias: entry} from a --pricing file, or exit 2 when it is unusable.

    In the alias map, keys starting with "_" (notes) or "<" (unfilled template
    rows) are skipped; the dated format prices every model id, as ops does.
    Every remaining entry needs finite, non-negative input_per_million and
    output_per_million; cache rates are optional and may be null.
    """
    if not path.is_file():
        # Fail closed: the caller asked for specific rates.
        print(f"Error: --pricing file not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, ValueError) as exc:  # ValueError covers JSONDecodeError
        print(f"Error: cannot read --pricing file {path}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(doc, dict):
        print(f"Error: --pricing file {path} must be a JSON object keyed by model", file=sys.stderr)
        sys.exit(2)
    dated = "checked" in doc and "models" in doc
    if dated:
        doc = from_dated_price_file(doc, path, max_age_days)
    elif max_age_days is not None:
        print(f"Error: --max-age-days needs a dated price file (\"checked\" plus \"models\"); "
              f"{path} has no \"checked\" date", file=sys.stderr)
        sys.exit(2)
    pricing = {}
    for alias, entry in doc.items():
        if not dated and alias.startswith(("_", "<")):
            continue
        if not isinstance(entry, dict):
            print(f"Error: pricing entry '{alias}' must be an object", file=sys.stderr)
            sys.exit(2)
        for field in ("input_per_million", "output_per_million",
                      "cache_read_per_million", "cache_write_per_million"):
            value = entry.get(field)
            required = field in ("input_per_million", "output_per_million")
            if value is None and not required:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)) \
                    or not math.isfinite(value) or value < 0:
                print(f"Error: pricing entry '{alias}' needs {field} as a finite non-negative number "
                      "(fill it in from the provider's pricing page)", file=sys.stderr)
                sys.exit(2)
        pricing[alias] = entry
    if not pricing:
        print(f"Error: --pricing file {path} has no filled-in model entries", file=sys.stderr)
        sys.exit(2)
    return pricing


DEFAULT_SYSTEM_PROMPT_TOKENS = 800
DEFAULT_INPUT_TOKENS_PER_TURN = 150   # User message + context
DEFAULT_OUTPUT_TOKENS_PER_TURN = 300  # Bot response
DEFAULT_TOOL_CALL_OVERHEAD = 200      # Extra tokens per tool call (input + output)


def estimate_conversation_cost(
    model: str,
    avg_turns: int,
    input_tokens_per_turn: int,
    output_tokens_per_turn: int,
    system_prompt_tokens: int,
    tool_calls_per_conversation: int,
    tool_call_overhead: int,
    pricing: dict,
    use_cache: bool = False,
) -> dict:
    """Estimate the cost of a single conversation.

    With --cache, each turn's prompt is split into what an earlier turn wrote
    to the cache (billed at cache_read) and what is new (billed at
    cache_write); see the comment in the turn loop. Caching is modelled only
    when both cache rates are supplied; otherwise the conversation is billed
    uncached and labelled so, rather than assuming a cache rate. Not modelled:
    a provider's minimum cacheable prefix length and cache expiry between turns.
    """

    if model not in pricing:
        print(f"Error: Unknown model '{model}'. Available: {', '.join(pricing.keys())}", file=sys.stderr)
        sys.exit(1)

    model_pricing = pricing[model]
    input_rate = model_pricing["input_per_million"] / 1_000_000
    output_rate = model_pricing["output_per_million"] / 1_000_000
    _cache_read = model_pricing.get("cache_read_per_million")
    _cache_write = model_pricing.get("cache_write_per_million")
    cache_read_rate = _cache_read / 1_000_000 if _cache_read is not None else None
    cache_write_rate = _cache_write / 1_000_000 if _cache_write is not None else None
    caching_active = use_cache and cache_read_rate is not None and cache_write_rate is not None

    # Token calculation
    # Each turn: system prompt + growing conversation history (the cacheable
    # prefix) + new user message (never cached). History grows: each prior
    # turn adds input + output tokens to the prefix.

    total_input_tokens = 0
    total_output_tokens = 0
    input_cost = 0.0
    cache_read_cost = 0.0
    cache_write_cost = 0.0

    for turn in range(1, avg_turns + 1):
        prefix_tokens = system_prompt_tokens + (turn - 1) * (input_tokens_per_turn + output_tokens_per_turn)
        turn_input = prefix_tokens + input_tokens_per_turn
        turn_output = output_tokens_per_turn

        total_input_tokens += turn_input
        total_output_tokens += turn_output

        if caching_active:
            # Cache breakpoint at the end of each request, so a turn can only
            # read what an earlier turn wrote:
            #   turn 1 writes its whole prompt, S + i.
            #   turn t >= 2 reads turn t-1's prompt, S + (t-2)(i+o) + i, and
            #   writes the new tail, o (turn t-1's reply) + i (this message).
            # Read + write = turn_input on every turn, so no input token is billed
            # twice or dropped. (The previous version read S + (t-1)(i+o) from
            # turn 2 on, including history it never wrote.)
            if turn == 1:
                cache_write_cost += turn_input * cache_write_rate
            else:
                cached = system_prompt_tokens + (turn - 2) * (input_tokens_per_turn + output_tokens_per_turn) \
                    + input_tokens_per_turn
                cache_read_cost += cached * cache_read_rate
                cache_write_cost += (turn_input - cached) * cache_write_rate
        else:
            input_cost += turn_input * input_rate

    # Tool call overhead (never cached: distinct per conversation)
    tool_input = tool_calls_per_conversation * tool_call_overhead
    tool_output = tool_calls_per_conversation * (tool_call_overhead // 2)
    total_input_tokens += tool_input
    total_output_tokens += tool_output
    input_cost += tool_input * input_rate

    output_cost = total_output_tokens * output_rate
    total_cost = input_cost + cache_read_cost + cache_write_cost + output_cost
    if not math.isfinite(total_cost):
        print(f"Error: model '{model}': estimate is not finite", file=sys.stderr)
        sys.exit(2)

    result = {
        "model": model,
        "display_name": model_pricing.get("display_name", model),
        "avg_turns": avg_turns,
        "cache_applied": caching_active,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "cost_per_conversation": round(total_cost, 6),
        # Unrounded, for projections; removed before output.
        "_exact_cost": total_cost,
    }
    if caching_active:
        result["cache_read_cost"] = round(cache_read_cost, 6)
        result["cache_write_cost"] = round(cache_write_cost, 6)
    elif use_cache:
        result["cache_note"] = "cache read/write rates not both supplied; billed uncached"
    return result


def main():
    parser = argparse.ArgumentParser(description="Estimate per-conversation bot costs.")
    parser.add_argument("--model", help="Model key from the --pricing file (required unless --compare-all)")
    parser.add_argument("--avg-turns", type=int, default=8, help="Average turns per conversation (default: 8)")
    parser.add_argument("--input-tokens", type=int, default=DEFAULT_INPUT_TOKENS_PER_TURN, help="Avg input tokens per turn")
    parser.add_argument("--output-tokens", type=int, default=DEFAULT_OUTPUT_TOKENS_PER_TURN, help="Avg output tokens per turn")
    parser.add_argument("--system-tokens", type=int, default=DEFAULT_SYSTEM_PROMPT_TOKENS, help="System prompt tokens")
    parser.add_argument("--tool-calls", type=int, default=2, help="Avg tool calls per conversation (default: 2)")
    parser.add_argument("--tool-overhead", type=int, default=DEFAULT_TOOL_CALL_OVERHEAD, help="Token overhead per tool call")
    parser.add_argument("--volume", type=int, default=None, help="Monthly conversation volume for projections")
    parser.add_argument("--pricing", default=None,
                        help="Required for any estimate: JSON rates per 1M tokens from the provider's "
                             "pricing page (schema: assets/pricing-template.json)")
    parser.add_argument("--compare-all", action="store_true", help="Compare cost across all models in --pricing")
    parser.add_argument(
        "--cache",
        action="store_true",
        help="Bill each turn's prompt as a cache read of the previous turn's prompt plus a cache "
        "write of the new tokens (turn 1 writes its whole prompt); billed uncached for models "
        "whose --pricing entry lacks either cache rate",
    )
    parser.add_argument("--max-age-days", type=int, metavar="N", default=None,
                        help="Exit 2 if the dated price file's 'checked' date is more than N days old. "
                             "Set it when the estimate feeds a decision. Default: no limit.")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()
    if args.max_age_days is not None and args.max_age_days < 0:
        parser.error("--max-age-days must not be negative")
    if args.avg_turns < 1:
        parser.error("--avg-turns must be at least 1")
    for flag in ("input_tokens", "output_tokens", "system_tokens", "tool_calls", "tool_overhead"):
        if getattr(args, flag) < 0:
            parser.error(f"--{flag.replace('_', '-')} must not be negative")
    if args.volume is not None and args.volume < 0:
        parser.error("--volume must not be negative")

    if not args.compare_all and not args.model:
        parser.error("--model is required unless --compare-all is given")
    if not args.pricing:
        print(NO_PRICING_MESSAGE, file=sys.stderr)
        sys.exit(2)
    pricing = load_pricing_file(Path(args.pricing), args.max_age_days)

    if args.compare_all:
        models = list(pricing.keys())
    else:
        models = [args.model]

    results = []
    for model in models:
        estimate = estimate_conversation_cost(
            model=model,
            avg_turns=args.avg_turns,
            input_tokens_per_turn=args.input_tokens,
            output_tokens_per_turn=args.output_tokens,
            system_prompt_tokens=args.system_tokens,
            tool_calls_per_conversation=args.tool_calls,
            tool_call_overhead=args.tool_overhead,
            pricing=pricing,
            use_cache=args.cache,
        )

        exact = estimate.pop("_exact_cost")
        if args.volume:
            monthly = exact * args.volume
            if not math.isfinite(monthly * 12):
                print(f"Error: model '{model}': projection is not finite", file=sys.stderr)
                sys.exit(2)
            estimate["monthly_volume"] = args.volume
            estimate["monthly_cost"] = round(monthly, 6)
            estimate["annual_cost"] = round(monthly * 12, 6)

        results.append(estimate)

    # Output
    output_data = results if len(results) > 1 else results[0]
    output_json = json.dumps(output_data, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Results written to {args.output}")
    else:
        print(output_json)

    # Print summary table to stderr
    print("\n--- Cost Estimate ---", file=sys.stderr)
    print(f"{'Model':<25} {'$/conv':>12} {'Tokens':>10}", file=sys.stderr)
    print("-" * 49, file=sys.stderr)
    for r in results:
        print(f"{r['display_name']:<25} ${r['cost_per_conversation']:>10.6f} {r['total_tokens']:>10,}", file=sys.stderr)

    if args.volume:
        print(f"\nMonthly volume: {args.volume:,}", file=sys.stderr)
        for r in results:
            print(f"  {r['display_name']}: ${r['monthly_cost']:,.2f}/mo, ${r['annual_cost']:,.2f}/yr", file=sys.stderr)


if __name__ == "__main__":
    main()
