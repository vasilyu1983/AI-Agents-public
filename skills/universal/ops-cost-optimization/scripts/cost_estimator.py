#!/usr/bin/env python3
"""
cost_estimator.py — per-call LLM cost from token counts and a price file you supply (stdlib-only).

The script carries NO prices. Prices change without notice, so you pass a JSON
price file copied from the provider pricing pages on the day you run it, with
the date you checked them. The script refuses to run without one.
Pass --max-age-days N whenever the estimate feeds a decision (a budget, a
model choice, a quote): a price file whose "checked" date is more than N days
old then exits 2 instead of pricing with stale rates. There is no default, so
existing price files keep working; without the flag the age is only reported.
It prices standard input/output only: cache write/hit, batch, and long-context
tiers are not modelled, so price those requests separately.

Price file (--pricing; --prices is an accepted alias) shape:
    {
      "checked": "YYYY-MM-DD",                 # date you read the pricing pages (required)
      "source": "https://...",                 # optional, where the rates came from
      "models": {
        "vendor/model-id": {
          "input_per_1m": <number >= 0>,       # USD per 1M input tokens (required)
          "output_per_1m": <number >= 0>,      # USD per 1M output tokens (required)
          "notes": "..."                       # optional
        }
      }
    }

Usage:
    python cost_estimator.py --pricing prices.json --input-tokens 500 --output-tokens 200
    python cost_estimator.py --pricing prices.json --prompt-file prompt.txt --output-tokens 200
    python cost_estimator.py --pricing prices.json --input-tokens 1000 --output-tokens 500 --providers openai anthropic
    python cost_estimator.py --pricing prices.json --input-tokens 1000 --output-tokens 500 --json
    python cost_estimator.py --pricing prices.json --input-tokens 1000 --output-tokens 500 --max-age-days 7

Exit codes: 0 ok; 2 bad input (missing, unreadable or invalid price file, a model listed
twice, a non-finite price or estimate, token count <= 0, a future "checked" date, prices
older than --max-age-days, unreadable or empty prompt file, no provider matched the filter).
"""

import argparse
from datetime import date
import json
import math
import sys
from pathlib import Path


class InputError(ValueError):
    """Bad user input; reported on stderr with exit code 2."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    # json.loads would keep the last duplicate silently, pricing a model at whichever
    # copy-pasted row came second.
    seen: dict = {}
    for key, value in pairs:
        if key in seen:
            raise InputError(f"duplicate key {key!r}: each key may appear once per object "
                             "(for a model listed twice, keep one entry or give a second "
                             "price tier its own id)")
        seen[key] = value
    return seen


def load_prices(path: Path) -> tuple[dict[str, dict], date, str]:
    """Return (models, checked_date, source). Raise InputError on any defect."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except FileNotFoundError:
        raise InputError(f"price file not found: {path}")
    except (OSError, UnicodeDecodeError) as e:
        raise InputError(f"cannot read price file {path}: {e}")
    except InputError as e:
        raise InputError(f"price file {path}: {e}")
    except ValueError as e:  # JSONDecodeError, or an integer past the int-string digit limit
        raise InputError(f"price file {path} is not valid JSON: {e}")
    if not isinstance(doc, dict):
        raise InputError("price file must be a JSON object")

    checked_raw = doc.get("checked")
    if not isinstance(checked_raw, str):
        raise InputError('price file needs "checked": "YYYY-MM-DD" (the date you read the pricing pages)')
    try:
        checked = date.fromisoformat(checked_raw)
    except ValueError:
        raise InputError(f'"checked" is not an ISO date: {checked_raw!r}')

    models = doc.get("models")
    if not isinstance(models, dict) or not models:
        raise InputError('price file needs a non-empty "models" object')
    for key, entry in models.items():
        if not isinstance(entry, dict):
            raise InputError(f"model {key!r}: entry must be an object")
        for field in ("input_per_1m", "output_per_1m"):
            value = entry.get(field)
            try:
                finite = math.isfinite(value)
            except (TypeError, OverflowError):
                finite = False
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not finite or value < 0:
                raise InputError(f"model {key!r}: {field} must be a finite number >= 0, got {value!r}")
    return models, checked, str(doc.get("source", ""))


def estimate_tokens_from_text(text: str) -> int:
    """Very rough token estimator: ~4 chars per token. Use the provider tokenizer for budgets."""
    return len(text) // 4


def compute_cost(input_tokens: int, output_tokens: int, provider_key: str, pricing: dict) -> dict:
    try:
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
        total_cost = input_cost + output_cost
    except OverflowError:
        raise InputError(f"model {provider_key!r}: estimate is not finite")
    if not all(math.isfinite(cost) for cost in (input_cost, output_cost, total_cost)):
        raise InputError(f"model {provider_key!r}: estimate is not finite")
    return {
        "provider": provider_key,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "notes": pricing.get("notes", ""),
    }


def run(input_tokens: int, output_tokens: int, prices_path: Path,
        provider_filter: list[str] | None, as_json: bool,
        max_age_days: int | None = None) -> int:
    if input_tokens <= 0 or output_tokens <= 0:
        raise InputError(f"token counts must be > 0 (input={input_tokens}, output={output_tokens})")
    if max_age_days is not None and max_age_days < 0:
        raise InputError(f"--max-age-days must be >= 0, got {max_age_days}")

    models, checked, source = load_prices(prices_path)
    age_days = (date.today() - checked).days
    if age_days < 0:
        raise InputError(f'"checked" date {checked.isoformat()} is in the future')
    if max_age_days is not None and age_days > max_age_days:
        raise InputError(
            f'prices in {prices_path} were checked {checked.isoformat()}, {age_days} days ago, '
            f"over --max-age-days {max_age_days}: re-read the provider pricing pages, update the "
            'rates and "checked", then rerun')

    selected = {
        k: v for k, v in models.items()
        if not provider_filter or any(f.lower() in k.lower() for f in provider_filter)
    }
    if not selected:
        raise InputError(f"no models matched filter: {provider_filter}")

    rows = sorted(
        (compute_cost(input_tokens, output_tokens, k, v) for k, v in selected.items()),
        key=lambda r: r["total_cost_usd"],
    )

    if as_json:
        print(json.dumps({
            "metadata": {"prices_checked": checked.isoformat(), "prices_age_days": age_days,
                         "prices_source": source or str(prices_path)},
            "estimates": rows,
        }, indent=2))
        return 0

    print(f"\nCost estimate — input: {input_tokens:,} tokens  output: {output_tokens:,} tokens")
    print(f"Prices checked {checked.isoformat()} ({age_days} days ago) — {source or prices_path}\n")
    header = f"{'Model':<35} {'Total USD':>12} {'Input USD':>12} {'Output USD':>12}  Notes"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(f"{row['provider']:<35} ${row['total_cost_usd']:>11.6f} "
              f"${row['input_cost_usd']:>11.6f} ${row['output_cost_usd']:>11.6f}  {row['notes']}")
    print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Per-call LLM cost from token counts and a dated price file (USD).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    tok_group = parser.add_mutually_exclusive_group(required=True)
    tok_group.add_argument("--input-tokens", type=int, help="Number of input tokens (> 0)")
    tok_group.add_argument("--prompt-file", type=Path, help="Prompt text file (rough auto-count)")
    parser.add_argument("--output-tokens", type=int, required=True, help="Number of output tokens (> 0)")
    parser.add_argument("--pricing", "--prices", dest="pricing", type=Path, required=True,
                        help="JSON price file copied from the provider pricing pages, with a 'checked' date "
                             "(--prices is an accepted alias)")
    parser.add_argument("--providers", nargs="+", metavar="PROVIDER",
                        help="Filter models by substring (e.g. openai anthropic). Default: all.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    parser.add_argument("--max-age-days", type=int, metavar="N",
                        help="Exit 2 if the price file's 'checked' date is more than N days old. "
                             "Set it when the estimate feeds a decision. Default: no limit.")
    args = parser.parse_args()

    try:
        if args.prompt_file:
            try:
                text = args.prompt_file.read_text(encoding="utf-8", errors="replace")
            except FileNotFoundError:
                raise InputError(f"prompt file not found: {args.prompt_file}")
            except OSError as e:
                raise InputError(f"cannot read prompt file {args.prompt_file}: {e}")
            input_tokens = estimate_tokens_from_text(text)
            if input_tokens <= 0:
                raise InputError(f"prompt file is empty or too short to estimate: {args.prompt_file}")
            print(f"[INFO] Auto-estimated {input_tokens} input tokens from {args.prompt_file}", file=sys.stderr)
        else:
            input_tokens = args.input_tokens
        sys.exit(run(input_tokens, args.output_tokens, args.pricing, args.providers, args.as_json,
                     args.max_age_days))
    except InputError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
