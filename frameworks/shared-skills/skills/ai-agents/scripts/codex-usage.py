#!/usr/bin/env python3
"""
Codex CLI usage reporter — stdlib-only CLI tool.

Reads local OpenAI Codex CLI session logs to produce token and cost reports
without any third-party dependencies.

Data source: ~/.codex/sessions/ (override with CODEX_HOME env var)

Subcommands:
  daily    — Usage grouped by date
  monthly  — Monthly aggregated report
  sessions — Per-session detail
  models   — Per-model all-time totals

Usage:
  python scripts/codex-usage.py daily
  python scripts/codex-usage.py daily --since 2026-04-01 --until 2026-04-07
  python scripts/codex-usage.py monthly --json
  python scripts/codex-usage.py sessions --last 10
  python scripts/codex-usage.py models
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
SESSIONS_DIR = CODEX_HOME / "sessions"

# ---------------------------------------------------------------------------
# Pricing table — USD per 1M tokens.
#
# Model IDs here are deliberately pinned and historical: replaying old sessions
# must price them at the rates that applied then, so retired IDs stay in the
# table. What rots is not the IDs but the *rates*, so the table expires loudly
# instead of being silently trusted. Bump PRICE_TABLE_LAST_VERIFIED when you
# re-check https://openai.com/api/pricing/; add new IDs without removing old
# ones. Unknown IDs fall through to DEFAULT_PRICING, which under-reports newer
# top-tier models — add them here rather than relying on the default.
#
# GPT-5.6 input/output rates mirror ai-llm/scripts/cost_estimator.py. The
# GPT-5.6 `cached` values are read off the price page (0.1x input). The older
# gpt-5/o3/o4-mini rows keep the 0.25x-of-input figures they were entered with,
# which is why the ratio is not uniform down the table.
# ---------------------------------------------------------------------------

# Import the resolver from this skill's OWN _lib/. The skill is self-contained:
# it carries its own _lib/ and data/, so it works detached from the repo
# (public-repo clone, single-folder copy, plugin). resolve() first because
# skills deploy as symlinks, so a lexical path escapes into the deployment root.
_here = Path(__file__).resolve()
sys.path.insert(0, str(_here.parents[1] / "_lib"))
try:
    from resolve_versions import load_pricing, pricing_path
except ImportError:  # resolver missing — use the embedded fallback
    load_pricing = None
    pricing_path = None

PRICE_TABLE_LAST_VERIFIED = date.fromisoformat("2026-08-10")
PRICE_TABLE_STALE_AFTER_DAYS = 30

FALLBACK_PRICING = {
    # Current tiers verified against developers.openai.com/api/docs/pricing on
    # 2026-08-10. Cached input is 0.1x base input, not the 0.25x assumed here
    # previously. The rows below this block are retired rates kept for replay.
    "gpt-5.6-sol":   {"input": 5.00, "output": 30.00, "cached": 0.50},
    "gpt-5.6-terra": {"input": 2.00, "output": 12.00, "cached": 0.20},
    "gpt-5.6-luna":  {"input": 0.20, "output": 1.20, "cached": 0.02},
    "gpt-5.5":   {"input": 2.00, "output": 8.00, "cached": 0.50},
    "gpt-5":     {"input": 2.00, "output": 8.00, "cached": 0.50},
    "gpt-5.4":   {"input": 2.00, "output": 8.00, "cached": 0.50},
    "gpt-4.1":   {"input": 2.00, "output": 8.00, "cached": 0.50},
    "o3":        {"input": 2.00, "output": 8.00, "cached": 0.50},
    "o4-mini":   {"input": 1.10, "output": 4.40, "cached": 0.275},
    "codex-mini": {"input": 1.50, "output": 6.00, "cached": 0.375},
}
DEFAULT_PRICING = {"input": 2.00, "output": 8.00, "cached": 0.50}


def _load_pricing() -> tuple[dict, str, date]:
    """Return (pricing, provenance, last_verified), preferring the shared table.

    Adapts the shared schema (`*_per_1m`) into this script's field names rather
    than renaming either side.
    """
    if load_pricing is None:
        return FALLBACK_PRICING, "embedded fallback (resolver not importable)", PRICE_TABLE_LAST_VERIFIED

    doc = load_pricing(__file__)
    models = doc.get("models") if isinstance(doc, dict) else None
    if not isinstance(models, dict):
        return FALLBACK_PRICING, "embedded fallback (shared table unavailable)", PRICE_TABLE_LAST_VERIFIED

    table = {}
    for key, entry in models.items():
        if not isinstance(entry, dict) or entry.get("vendor") != "openai":
            continue
        if "input_per_1m" not in entry or "output_per_1m" not in entry:
            continue
        table[key.split("/", 1)[-1]] = {
            "input": entry["input_per_1m"],
            "output": entry["output_per_1m"],
            # 0.1x input is the published cached-input ratio for current OpenAI
            # tiers; used only when the shared table carries no explicit column.
            "cached": entry.get("cache_read_per_1m", entry["input_per_1m"] * 0.10),
        }
    if not table:
        return FALLBACK_PRICING, "embedded fallback (no openai rows)", PRICE_TABLE_LAST_VERIFIED

    verified = PRICE_TABLE_LAST_VERIFIED
    stamp = doc.get("last_verified")
    if isinstance(stamp, str):
        try:
            verified = date.fromisoformat(stamp)
        except ValueError:
            pass
    path = pricing_path(__file__) if pricing_path else None
    return table, f"shared: {path}" if path else "shared", verified


PRICING, PRICING_SOURCE, PRICING_VERIFIED = _load_pricing()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def warn_if_price_table_stale() -> None:
    """Warn once if the embedded pricing table is older than the staleness window.

    Called from main() rather than estimate_cost() because the reports call
    estimate_cost per row; warning there would repeat the notice for every line.
    """
    age_days = (date.today() - PRICING_VERIFIED).days
    if age_days > PRICE_TABLE_STALE_AFTER_DAYS:
        print(
            f"[WARN] Pricing is {age_days} days old "
            f"(last verified {PRICING_VERIFIED.isoformat()}, source: {PRICING_SOURCE}); "
            "costs below are estimates — verify at https://openai.com/api/pricing/.",
            file=sys.stderr,
        )


def estimate_cost(model: str, inp: int, out: int, cached: int) -> float:
    """Estimate cost in USD from token counts."""
    prices = DEFAULT_PRICING
    for key, p in PRICING.items():
        if key in (model or ""):
            prices = p
            break
    # Non-cached input = total input minus cached portion
    non_cached = max(0, inp - cached)
    return (
        non_cached * prices["input"] / 1_000_000
        + out * prices["output"] / 1_000_000
        + cached * prices["cached"] / 1_000_000
    )


def parse_date(s: str) -> str:
    s = s.replace("/", "-").strip()
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return s[:10]


def in_range(date_str: str, since: str | None, until: str | None) -> bool:
    if since and date_str < since:
        return False
    if until and date_str > until:
        return False
    return True


def fmt_tokens(n: int) -> str:
    return f"{n:,}"


def fmt_cost(c: float) -> str:
    return f"${c:.2f}"


def print_table(headers: list[str], rows: list[list[str]], right_align: set[int] | None = None):
    right_align = right_align or set()
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells):
        parts = []
        for i, cell in enumerate(cells):
            if i in right_align:
                parts.append(cell.rjust(widths[i]))
            else:
                parts.append(cell.ljust(widths[i]))
        return "  ".join(parts)

    print(fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt_row(row))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def iter_session_files():
    """Yield (path, session_id) for all Codex JSONL session files."""
    if not SESSIONS_DIR.is_dir():
        return
    for path in sorted(glob.glob(str(SESSIONS_DIR / "**" / "*.jsonl"), recursive=True)):
        # Session ID from filename: rollout-{timestamp}-{uuid}.jsonl
        basename = os.path.basename(path).replace(".jsonl", "")
        yield path, basename


def parse_session_events(path: str):
    """
    Parse a Codex session JSONL file.

    Yields dicts with token usage per turn. Handles:
    - null last_token_usage (falls back to total_token_usage delta)
    - Missing model metadata (falls back to 'unknown')
    - Non-dict payloads
    """
    current_model = "unknown"
    prev_totals = {"input_tokens": 0, "cached_input_tokens": 0,
                   "output_tokens": 0, "reasoning_output_tokens": 0}

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue

            rec_type = rec.get("type")
            payload = rec.get("payload")
            if not isinstance(payload, dict):
                continue

            # Extract model from turn_context
            if rec_type == "turn_context":
                model = payload.get("model")
                if model:
                    current_model = model

            # Extract token usage from event_msg with token_count
            if rec_type == "event_msg" and payload.get("type") == "token_count":
                info = payload.get("info")
                if not isinstance(info, dict):
                    continue

                timestamp = rec.get("timestamp", "")

                # Prefer last_token_usage (per-turn delta)
                last = info.get("last_token_usage")
                if isinstance(last, dict) and last.get("input_tokens"):
                    yield {
                        "timestamp": timestamp,
                        "model": current_model,
                        "input": last.get("input_tokens", 0) or 0,
                        "output": last.get("output_tokens", 0) or 0,
                        "cached": last.get("cached_input_tokens", 0) or 0,
                        "reasoning": last.get("reasoning_output_tokens", 0) or 0,
                    }
                    # Update prev_totals from total if available
                    total = info.get("total_token_usage")
                    if isinstance(total, dict):
                        prev_totals = {
                            "input_tokens": total.get("input_tokens", 0) or 0,
                            "cached_input_tokens": total.get("cached_input_tokens", 0) or 0,
                            "output_tokens": total.get("output_tokens", 0) or 0,
                            "reasoning_output_tokens": total.get("reasoning_output_tokens", 0) or 0,
                        }
                    continue

                # Fallback: compute delta from cumulative total_token_usage
                total = info.get("total_token_usage")
                if isinstance(total, dict):
                    inp = (total.get("input_tokens", 0) or 0) - prev_totals["input_tokens"]
                    out = (total.get("output_tokens", 0) or 0) - prev_totals["output_tokens"]
                    cached = (total.get("cached_input_tokens", 0) or 0) - prev_totals["cached_input_tokens"]
                    reasoning = (total.get("reasoning_output_tokens", 0) or 0) - prev_totals["reasoning_output_tokens"]

                    if inp > 0 or out > 0:
                        yield {
                            "timestamp": timestamp,
                            "model": current_model,
                            "input": max(0, inp),
                            "output": max(0, out),
                            "cached": max(0, cached),
                            "reasoning": max(0, reasoning),
                        }

                    prev_totals = {
                        "input_tokens": total.get("input_tokens", 0) or 0,
                        "cached_input_tokens": total.get("cached_input_tokens", 0) or 0,
                        "output_tokens": total.get("output_tokens", 0) or 0,
                        "reasoning_output_tokens": total.get("reasoning_output_tokens", 0) or 0,
                    }


def iter_all_events(since: str | None = None, until: str | None = None):
    """Yield all token usage events across all sessions, optionally filtered by date."""
    for path, session_id in iter_session_files():
        for event in parse_session_events(path):
            date = event["timestamp"][:10]
            if not in_range(date, since, until):
                continue
            event["session_id"] = session_id
            yield event


# ---------------------------------------------------------------------------
# Subcommand: daily
# ---------------------------------------------------------------------------

def cmd_daily(args):
    daily = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "reasoning": 0, "turns": 0, "models": set()})

    for ev in iter_all_events(args.since, args.until):
        date = ev["timestamp"][:10]
        d = daily[date]
        d["input"] += ev["input"]
        d["output"] += ev["output"]
        d["cached"] += ev["cached"]
        d["reasoning"] += ev["reasoning"]
        d["turns"] += 1
        d["models"].add(ev["model"])

    if not daily:
        print(f"No data found. Checked: {SESSIONS_DIR}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        out = []
        for date in sorted(daily):
            d = daily[date]
            cost = estimate_cost("", d["input"], d["output"], d["cached"])
            out.append({"date": date, "inputTokens": d["input"], "outputTokens": d["output"],
                        "cachedInputTokens": d["cached"], "reasoningOutputTokens": d["reasoning"],
                        "turns": d["turns"], "costUSD": round(cost, 4),
                        "models": sorted(d["models"])})
        json.dump({"daily": out}, sys.stdout, indent=2)
        print()
        return

    rows = []
    total_cost = 0.0
    for date in sorted(daily):
        d = daily[date]
        cost = estimate_cost("", d["input"], d["output"], d["cached"])
        total_cost += cost
        rows.append([date, fmt_tokens(d["input"]), fmt_tokens(d["output"]),
                      fmt_tokens(d["cached"]), fmt_tokens(d["reasoning"]),
                      str(d["turns"]), fmt_cost(cost)])

    print_table(["Date", "Input", "Output", "Cached", "Reasoning", "Turns", "Est. Cost"],
                rows, {1, 2, 3, 4, 5, 6})
    print(f"\nTotal estimated cost: {fmt_cost(total_cost)}")


# ---------------------------------------------------------------------------
# Subcommand: monthly
# ---------------------------------------------------------------------------

def cmd_monthly(args):
    monthly = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "reasoning": 0, "turns": 0})

    for ev in iter_all_events(args.since, args.until):
        month = ev["timestamp"][:7]
        m = monthly[month]
        m["input"] += ev["input"]
        m["output"] += ev["output"]
        m["cached"] += ev["cached"]
        m["reasoning"] += ev["reasoning"]
        m["turns"] += 1

    if not monthly:
        print(f"No data found. Checked: {SESSIONS_DIR}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        out = []
        for month in sorted(monthly):
            m = monthly[month]
            cost = estimate_cost("", m["input"], m["output"], m["cached"])
            out.append({"month": month, "inputTokens": m["input"], "outputTokens": m["output"],
                        "cachedInputTokens": m["cached"], "reasoningOutputTokens": m["reasoning"],
                        "turns": m["turns"], "costUSD": round(cost, 4)})
        json.dump({"monthly": out}, sys.stdout, indent=2)
        print()
        return

    rows = []
    total_cost = 0.0
    for month in sorted(monthly):
        m = monthly[month]
        cost = estimate_cost("", m["input"], m["output"], m["cached"])
        total_cost += cost
        rows.append([month, fmt_tokens(m["input"]), fmt_tokens(m["output"]),
                      fmt_tokens(m["cached"]), fmt_tokens(m["reasoning"]),
                      str(m["turns"]), fmt_cost(cost)])

    print_table(["Month", "Input", "Output", "Cached", "Reasoning", "Turns", "Est. Cost"],
                rows, {1, 2, 3, 4, 5, 6})
    print(f"\nTotal estimated cost: {fmt_cost(total_cost)}")


# ---------------------------------------------------------------------------
# Subcommand: sessions
# ---------------------------------------------------------------------------

def cmd_sessions(args):
    sess = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "reasoning": 0,
                                "turns": 0, "first_ts": "", "last_ts": "", "model": "unknown"})

    for ev in iter_all_events(args.since, args.until):
        sid = ev["session_id"]
        s = sess[sid]
        s["input"] += ev["input"]
        s["output"] += ev["output"]
        s["cached"] += ev["cached"]
        s["reasoning"] += ev["reasoning"]
        s["turns"] += 1
        s["model"] = ev["model"]
        if not s["first_ts"] or ev["timestamp"] < s["first_ts"]:
            s["first_ts"] = ev["timestamp"]
        if not s["last_ts"] or ev["timestamp"] > s["last_ts"]:
            s["last_ts"] = ev["timestamp"]

    if not sess:
        print(f"No data found. Checked: {SESSIONS_DIR}", file=sys.stderr)
        sys.exit(1)

    # Sort by most recent first
    sorted_sessions = sorted(sess.items(), key=lambda kv: kv[1]["last_ts"], reverse=True)
    if args.last:
        sorted_sessions = sorted_sessions[:args.last]

    if args.json:
        out = []
        for sid, s in sorted_sessions:
            cost = estimate_cost(s["model"], s["input"], s["output"], s["cached"])
            out.append({"sessionId": sid, "date": s["first_ts"][:10],
                        "model": s["model"], "inputTokens": s["input"],
                        "outputTokens": s["output"], "cachedInputTokens": s["cached"],
                        "turns": s["turns"], "costUSD": round(cost, 4)})
        json.dump({"sessions": out}, sys.stdout, indent=2)
        print()
        return

    rows = []
    total_cost = 0.0
    for sid, s in sorted_sessions:
        cost = estimate_cost(s["model"], s["input"], s["output"], s["cached"])
        total_cost += cost
        # Truncate session ID for display
        short_id = sid[:30] + "..." if len(sid) > 33 else sid
        rows.append([s["first_ts"][:10], short_id, s["model"],
                      fmt_tokens(s["input"]), fmt_tokens(s["output"]),
                      str(s["turns"]), fmt_cost(cost)])

    print_table(["Date", "Session", "Model", "Input", "Output", "Turns", "Est. Cost"],
                rows, {3, 4, 5, 6})
    print(f"\nTotal estimated cost: {fmt_cost(total_cost)}")
    print(f"Showing {len(sorted_sessions)} session(s)")


# ---------------------------------------------------------------------------
# Subcommand: models
# ---------------------------------------------------------------------------

def cmd_models(args):
    models = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "reasoning": 0, "turns": 0})

    for ev in iter_all_events(args.since, args.until):
        m = models[ev["model"]]
        m["input"] += ev["input"]
        m["output"] += ev["output"]
        m["cached"] += ev["cached"]
        m["reasoning"] += ev["reasoning"]
        m["turns"] += 1

    if not models:
        print(f"No data found. Checked: {SESSIONS_DIR}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        out = {}
        for model, m in sorted(models.items()):
            cost = estimate_cost(model, m["input"], m["output"], m["cached"])
            out[model] = {"inputTokens": m["input"], "outputTokens": m["output"],
                          "cachedInputTokens": m["cached"], "reasoningOutputTokens": m["reasoning"],
                          "turns": m["turns"], "costUSD": round(cost, 4)}
        json.dump({"models": out}, sys.stdout, indent=2)
        print()
        return

    rows = []
    total_cost = 0.0
    for model, m in sorted(models.items()):
        cost = estimate_cost(model, m["input"], m["output"], m["cached"])
        total_cost += cost
        rows.append([model, fmt_tokens(m["input"]), fmt_tokens(m["output"]),
                      fmt_tokens(m["cached"]), fmt_tokens(m["reasoning"]),
                      str(m["turns"]), fmt_cost(cost)])

    print_table(["Model", "Input", "Output", "Cached", "Reasoning", "Turns", "Est. Cost"],
                rows, {1, 2, 3, 4, 5, 6})
    print(f"\nTotal estimated cost: {fmt_cost(total_cost)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Codex CLI usage reporter — reads local session logs, no dependencies required.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p):
        p.add_argument("--since", "-s", help="Filter from date (YYYY-MM-DD)")
        p.add_argument("--until", "-u", help="Filter until date (YYYY-MM-DD)")
        p.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    p_daily = sub.add_parser("daily", help="Usage grouped by date")
    add_common(p_daily)
    p_daily.set_defaults(func=cmd_daily)

    p_monthly = sub.add_parser("monthly", help="Monthly aggregated report")
    add_common(p_monthly)
    p_monthly.set_defaults(func=cmd_monthly)

    p_sessions = sub.add_parser("sessions", help="Per-session detail")
    add_common(p_sessions)
    p_sessions.add_argument("--last", "-n", type=int, help="Show only the N most recent sessions")
    p_sessions.set_defaults(func=cmd_sessions)

    p_models = sub.add_parser("models", help="Per-model all-time totals")
    add_common(p_models)
    p_models.set_defaults(func=cmd_models)

    args = parser.parse_args()

    if hasattr(args, "since") and args.since:
        args.since = parse_date(args.since)
    if hasattr(args, "until") and args.until:
        args.until = parse_date(args.until)

    warn_if_price_table_stale()
    args.func(args)


if __name__ == "__main__":
    main()
