#!/usr/bin/env python3
"""
Claude Code usage reporter — stdlib-only CLI tool.

Reads local Claude Code logs to produce token and cost reports
without any third-party dependencies.

Data sources:
  - ~/.claude/stats-cache.json  (pre-aggregated daily/model stats)
  - ~/.claude/projects/          (raw JSONL session logs, read recursively so
                                  <session>/subagents/*.jsonl is included)

Subcommands:
  daily    — Usage grouped by date
  monthly  — Monthly aggregated report
  sessions — Per-session detail
  models   — Per-model all-time totals (stats-cache.json; from the JSONL logs
             under --pricing, since only they split cache writes by TTL)

Usage:
  python scripts/claude-usage.py daily
  python scripts/claude-usage.py daily --pricing my-rates.json
  python scripts/claude-usage.py daily --since 2026-04-01 --until 2026-04-07
  python scripts/claude-usage.py monthly --json
  python scripts/claude-usage.py sessions --last 10
  python scripts/claude-usage.py models

Cost needs rates you supply: pass --pricing <file.json> (schema in
../assets/pricing-template.json) filled in from the provider's pricing page.
No rates ship with this script because published rates change. Without
--pricing the token report runs as normal and cost is reported as unpriced;
no cost figure is printed.

With --pricing, cost is fail-closed: a model is priced only when its exact ID
(optionally with a trailing -YYYYMMDD snapshot suffix) is in your file and every
cache rate its tokens need is set. 1-hour cache writes need their own
cache_write_1h_per_1m rate; they are never priced at the 5-minute rate. Anything
else is reported as `unpriced` with a reason, never at a default rate.

One API response is counted once: log lines are deduplicated on
(message.id, requestId) before summing, across session and subagent files,
keeping the most complete copy (stop_reason set, else the largest output count).

Exit codes: 0 = report complete (or tokens only, without --pricing); 1 = no data;
2 = unreadable --pricing file; 3 = report printed with --pricing but at least one
model is unpriced, or the data source holds no priceable tokens (the stats-cache
`daily` path), so any cost total is a known subtotal only.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_env_dir = os.environ.get("CLAUDE_CONFIG_DIR", "")
if _env_dir and Path(_env_dir).is_dir():
    CLAUDE_DIR = Path(_env_dir)
elif (Path.home() / ".config" / "claude").is_dir():
    CLAUDE_DIR = Path.home() / ".config" / "claude"
else:
    CLAUDE_DIR = Path.home() / ".claude"

STATS_CACHE = CLAUDE_DIR / "stats-cache.json"
PROJECTS_DIR = CLAUDE_DIR / "projects"

# ---------------------------------------------------------------------------
# Pricing — user-supplied only.
#
# No rates are embedded: a built-in table goes stale within weeks and then
# prints confident wrong numbers. The user passes --pricing with rates copied
# from https://claude.com/pricing (USD per 1M tokens); without it, cost is
# reported as unpriced.
# ---------------------------------------------------------------------------

PRICING_PAGE = "https://claude.com/pricing"
NO_PRICING_MESSAGE = (
    "Cost: unpriced (no rates supplied). Pass --pricing <file.json> with rates from "
    f"the provider's pricing page ({PRICING_PAGE}); schema: assets/pricing-template.json."
)
UNPRICED_EXIT = 3
STATS_CACHE_NO_COST_MESSAGE = (
    "Cost: unavailable from stats-cache.json (it has no per-day token counts), so "
    "--pricing was not applied to `daily`. Use `monthly --pricing` for cost from the JSONL logs."
)

# Filled by main() from --pricing. Empty means "no rates supplied".
PRICING: dict = {}


class PricingError(ValueError):
    """The --pricing file is missing, unreadable, or malformed."""


def _rate(entry: dict, field: str, model: str) -> float | None:
    value = entry.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise PricingError(f"{model}: {field} must be a non-negative number or null")
    return float(value)


def load_pricing_file(path: str | Path) -> dict:
    """Parse a user pricing file into
    {model_id: {input, output, cache_read?, cache_create?, cache_create_1h?}}.

    Schema: {"models": {"<model-id>": {"input_per_1m": n, "output_per_1m": n,
    "cache_read_per_1m": n|null, "cache_write_per_1m": n|null,
    "cache_write_1h_per_1m": n|null}}}. cache_write_per_1m is the 5-minute write
    rate; cache_write_1h_per_1m (optional) is the 1-hour write rate. A "vendor/"
    prefix on the ID is dropped. Rows whose input or output rate is null are
    skipped (unfilled template rows), so those models stay unpriced. A null cache
    rate stays missing, so rows that used that cache are reported unpriced, not free.
    """
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise PricingError(f"cannot read --pricing file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PricingError(f"--pricing file {path} is not valid JSON: {exc}") from exc
    models = doc.get("models") if isinstance(doc, dict) else None
    if not isinstance(models, dict):
        raise PricingError(f"--pricing file {path} has no \"models\" object")
    table = {}
    for key, entry in models.items():
        if not isinstance(entry, dict) or key.startswith("<"):
            continue
        model = key.split("/", 1)[-1]
        inp = _rate(entry, "input_per_1m", model)
        out = _rate(entry, "output_per_1m", model)
        if inp is None or out is None:
            continue
        row = {"input": inp, "output": out}
        cache_read = _rate(entry, "cache_read_per_1m", model)
        cache_write = _rate(entry, "cache_write_per_1m", model)
        cache_write_1h = _rate(entry, "cache_write_1h_per_1m", model)
        if cache_read is not None:
            row["cache_read"] = cache_read
        if cache_write is not None:
            row["cache_create"] = cache_write
        if cache_write_1h is not None:
            row["cache_create_1h"] = cache_write_1h
        table[model] = row
    return table


def pricing_supplied() -> bool:
    return bool(PRICING)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SNAPSHOT_SUFFIX = re.compile(r"-\d{8}$")


def lookup_prices(model: str) -> dict | None:
    """Exact model-ID lookup; a -YYYYMMDD snapshot suffix maps to its base ID.

    No substring or prefix matching: a longer or newer ID must never borrow a
    listed model's rate.
    """
    if model in PRICING:
        return PRICING[model]
    base = _SNAPSHOT_SUFFIX.sub("", model)
    return PRICING.get(base) if base != model else None


def attribute_cost(model: str, inp: int, out: int, cache_read: int,
                   cache_create: int, cache_create_1h: int = 0) -> tuple[float | None, str | None]:
    """Return (cost_usd, None) when priceable, else (None, unpriced_reason).

    cache_create is all cache-write tokens; cache_create_1h is the part written
    with the 1-hour TTL. The rest is priced at the 5-minute write rate, and the
    1-hour part only at its own rate: never at the 5-minute one.
    """
    if not (inp or out or cache_read or cache_create):
        return 0.0, None
    prices = lookup_prices(model)
    if prices is None:
        return None, "unknown_model_id"
    cache_create_5m = cache_create - cache_create_1h
    if cache_read and "cache_read" not in prices:
        return None, "cache_read_rate_unavailable"
    if cache_create_5m and "cache_create" not in prices:
        return None, "cache_write_rate_unavailable"
    if cache_create_1h and "cache_create_1h" not in prices:
        return None, "cache_write_1h_rate_unavailable"
    return (
        inp * prices["input"] / 1_000_000
        + out * prices["output"] / 1_000_000
        + cache_read * prices.get("cache_read", 0) / 1_000_000
        + cache_create_5m * prices.get("cache_create", 0) / 1_000_000
        + cache_create_1h * prices.get("cache_create_1h", 0) / 1_000_000
    ), None


def estimate_cost(model: str, inp: int, out: int, cache_read: int, cache_create: int) -> float | None:
    """Compatibility helper: the cost, or None when the model is unpriced."""
    return attribute_cost(model, inp, out, cache_read, cache_create)[0]


def price_bucket(per_model: dict) -> dict:
    """Price a {model: token counts} bucket model by model, failing closed."""
    known = 0.0
    unpriced = {}
    for model, t in sorted(per_model.items()):
        cost, reason = attribute_cost(model, t["input"], t["output"],
                                      t["cache_read"], t["cache_create"],
                                      t.get("cache_create_1h", 0))
        if reason:
            unpriced[model] = reason
        else:
            known += cost
    return {"costUSD": None if unpriced else round(known, 4),
            "knownCostUSD": round(known, 4), "unpricedModels": unpriced}


def fmt_bucket_cost(priced: dict) -> str:
    if not priced["unpricedModels"]:
        return fmt_cost(priced["knownCostUSD"])
    return f"{fmt_cost(priced['knownCostUSD'])}+unpriced"


def fmt_cost_summary(known_total: float, unpriced: dict) -> str:
    """Do not render an incomplete aggregation as a complete total."""
    if not unpriced:
        return f"Total estimated cost: {fmt_cost(known_total)}"
    detail = ", ".join(f"{m} ({r})" for m, r in sorted(unpriced.items()))
    return (f"Known cost subtotal: {fmt_cost(known_total)}; "
            f"unpriced model(s): {detail}")


def _new_tokens() -> dict:
    return {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0, "cache_create_1h": 0}


def _add_tokens(bucket: dict, u: dict) -> None:
    bucket["input"] += u["input_tokens"]
    bucket["output"] += u["output_tokens"]
    bucket["cache_read"] += u["cache_read"]
    bucket["cache_create"] += u["cache_create"]
    bucket["cache_create_1h"] += u["cache_create_1h"]


def parse_date(s: str) -> str:
    """Normalize date string to YYYY-MM-DD."""
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
    """Format token count with commas."""
    return f"{n:,}"


def fmt_cost(c: float) -> str:
    return f"${c:.2f}"


def print_table(headers: list[str], rows: list[list[str]], right_align: set[int] | None = None):
    """Print a simple ASCII table."""
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
# Data loading — stats-cache.json (fast path)
# ---------------------------------------------------------------------------

def load_stats_cache() -> dict:
    if not STATS_CACHE.exists():
        return {}
    return json.loads(STATS_CACHE.read_text())


# ---------------------------------------------------------------------------
# Data loading — raw JSONL (detailed path)
# ---------------------------------------------------------------------------

def iter_jsonl_records():
    """Yield parsed records from all Claude Code JSONL session files."""
    if not PROJECTS_DIR.is_dir():
        return
    # Recursive: subagent transcripts live at <project>/<session>/subagents/*.jsonl
    # (and deeper for workflows) and hold most of the responses.
    pattern = str(PROJECTS_DIR / "*" / "**" / "*.jsonl")
    for path in sorted(glob.glob(pattern, recursive=True)):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    if isinstance(rec, dict):
                        yield rec, path
                except json.JSONDecodeError:
                    continue


def extract_usage(rec: dict) -> dict | None:
    """Extract token usage from an assistant message record."""
    msg = rec.get("message")
    if not isinstance(msg, dict):
        return None
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return None
    cache_create = usage.get("cache_creation_input_tokens", 0) or 0
    # usage.cache_creation splits writes by TTL. Without that breakdown the API
    # default (5-minute) TTL applies, so the whole write counts as 5-minute.
    # With it, the total is at least the two parts, so 1-hour tokens are never
    # dropped when cache_creation_input_tokens is absent.
    breakdown = usage.get("cache_creation")
    cache_create_1h = 0
    if isinstance(breakdown, dict):
        cache_create_1h = breakdown.get("ephemeral_1h_input_tokens", 0) or 0
        cache_create_5m = breakdown.get("ephemeral_5m_input_tokens", 0) or 0
        cache_create = max(cache_create, cache_create_1h + cache_create_5m)
    return {
        "timestamp": rec.get("timestamp", ""),
        "session_id": rec.get("sessionId", ""),
        "message_id": msg.get("id"),
        "request_id": rec.get("requestId"),
        "model": msg.get("model", "unknown"),
        "stop_reason": msg.get("stop_reason"),
        "input_tokens": usage.get("input_tokens", 0) or 0,
        "output_tokens": usage.get("output_tokens", 0) or 0,
        "cache_read": usage.get("cache_read_input_tokens", 0) or 0,
        "cache_create": cache_create,
        "cache_create_1h": cache_create_1h,
    }


def iter_usage():
    """Yield (usage, path) once per API response, not once per log line.

    Claude Code writes one JSONL line per content block (thinking, text,
    tool_use) of a response, and every line repeats that response's message.id,
    requestId and usage, so summing lines counts one response two or three
    times. Records are keyed on (message.id, requestId) across all files, since
    a resumed session or a subagent transcript can hold a copy of the same
    response. The copies are not always identical: a line written while the
    response was still streaming carries partial counters (a few output tokens,
    no stop_reason). So the most complete copy is kept, by content rather than
    by line or file order: one with a stop_reason beats one without, and
    otherwise the larger output_tokens wins; on a tie the first copy stays. A
    record without message.id cannot be matched to its siblings and is counted
    as its own response.
    """
    kept = {}
    for n, (rec, path) in enumerate(iter_jsonl_records()):
        u = extract_usage(rec)
        if not u:
            continue
        key = (u["message_id"], u["request_id"]) if u["message_id"] else ("line", n)
        rank = (u["stop_reason"] is not None, u["output_tokens"])
        if key not in kept or rank > kept[key][0]:
            kept[key] = (rank, u, path)
    for _, u, path in kept.values():
        yield u, path


# ---------------------------------------------------------------------------
# Subcommand: daily
# ---------------------------------------------------------------------------

def cmd_daily(args):
    """Daily usage report."""
    stats = load_stats_cache()
    daily_list = stats.get("dailyActivity", [])
    model_tokens = stats.get("dailyModelTokens", {})

    if not daily_list and not PROJECTS_DIR.is_dir():
        print(f"No data found. Checked: {STATS_CACHE} and {PROJECTS_DIR}", file=sys.stderr)
        sys.exit(1)

    # If stats-cache has daily data, use it (fast path)
    if daily_list:
        rows_data = []
        for entry in sorted(daily_list, key=lambda e: e.get("date", "")):
            date = entry.get("date", "")
            if not in_range(date, args.since, args.until):
                continue
            rows_data.append({
                "date": date,
                "messages": entry.get("messageCount", 0),
                "sessions": entry.get("sessionCount", 0),
                "tools": entry.get("toolCallCount", 0),
            })

        if args.json:
            doc = {"daily": rows_data}
            if pricing_supplied():
                doc.update(costComplete=False, costStatus="unavailable_from_stats_cache")
            json.dump(doc, sys.stdout, indent=2)
            print()
        elif not rows_data:
            print("No data in the specified date range.")
        else:
            rows = [[r["date"], str(r["messages"]), str(r["sessions"]), str(r["tools"])]
                    for r in rows_data]
            print_table(["Date", "Messages", "Sessions", "Tool Calls"], rows, {1, 2, 3})

            total_msg = sum(r["messages"] for r in rows_data)
            total_sess = sum(r["sessions"] for r in rows_data)
            total_tools = sum(r["tools"] for r in rows_data)
            print(f"\nTotal: {total_msg:,} messages, {total_sess:,} sessions, {total_tools:,} tool calls")
        if pricing_supplied():
            # stats-cache.json holds activity counts, not per-day token counts,
            # so --pricing has nothing to price here. Say so; never drop it silently.
            print(STATS_CACHE_NO_COST_MESSAGE, file=sys.stderr)
            sys.exit(UNPRICED_EXIT)
        return

    # Fallback: parse JSONL
    daily = defaultdict(lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0, "count": 0,
                                 "per_model": defaultdict(_new_tokens)})
    for u, _ in iter_usage():
        if not u["timestamp"]:
            continue
        date = u["timestamp"][:10]
        if not in_range(date, args.since, args.until):
            continue
        d = daily[date]
        d["input"] += u["input_tokens"]
        d["output"] += u["output_tokens"]
        d["cache_read"] += u["cache_read"]
        d["cache_create"] += u["cache_create"]
        d["count"] += 1
        _add_tokens(d["per_model"][u["model"]], u)

    return _report_buckets(daily, "date", "daily", "Date", args)


def _report_buckets(buckets: dict, key_name: str, json_key: str, label: str, args) -> int:
    """Print a per-period report priced per model; return the unpriced count.

    Without --pricing, only token counts are reported: no cost column, no total.
    """
    if not pricing_supplied():
        out, rows = [], []
        for key in sorted(buckets):
            b = buckets[key]
            out.append({key_name: key, "inputTokens": b["input"], "outputTokens": b["output"],
                        "cacheReadTokens": b["cache_read"], "cacheCreateTokens": b["cache_create"],
                        "messages": b["count"], "costUSD": None, "models": sorted(b["per_model"])})
            rows.append([key, fmt_tokens(b["input"]), fmt_tokens(b["output"]),
                         fmt_tokens(b["cache_read"]), str(b["count"])])
        if args.json:
            json.dump({json_key: out, "costComplete": False, "costStatus": "unpriced_no_rates"},
                      sys.stdout, indent=2)
            print()
        elif not rows:
            print("No data in the specified date range.")
        else:
            print_table([label, "Input", "Output", "Cache Read", "Messages"], rows, {1, 2, 3, 4})
        return 0

    all_unpriced = {}
    known_total = 0.0
    out, rows = [], []
    for key in sorted(buckets):
        b = buckets[key]
        priced = price_bucket(b["per_model"])
        all_unpriced.update(priced["unpricedModels"])
        known_total += priced["knownCostUSD"]
        out.append({key_name: key, "inputTokens": b["input"], "outputTokens": b["output"],
                    "cacheReadTokens": b["cache_read"], "cacheCreateTokens": b["cache_create"],
                    "messages": b["count"], **priced, "models": sorted(b["per_model"])})
        rows.append([key, fmt_tokens(b["input"]), fmt_tokens(b["output"]),
                     fmt_tokens(b["cache_read"]), str(b["count"]), fmt_bucket_cost(priced)])

    if args.json:
        json.dump({json_key: out, "costComplete": not all_unpriced}, sys.stdout, indent=2)
        print()
        return len(all_unpriced)

    if not rows:
        print("No data in the specified date range.")
        return 0

    print_table([label, "Input", "Output", "Cache Read", "Messages", "Est. Cost"],
                rows, {1, 2, 3, 4, 5})
    print(f"\n{fmt_cost_summary(known_total, all_unpriced)}")
    return len(all_unpriced)


# ---------------------------------------------------------------------------
# Subcommand: monthly
# ---------------------------------------------------------------------------

def cmd_monthly(args):
    """Monthly aggregated report from JSONL data."""
    monthly = defaultdict(lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0, "count": 0,
                                   "per_model": defaultdict(_new_tokens)})

    for u, _ in iter_usage():
        if not u["timestamp"]:
            continue
        date = u["timestamp"][:10]
        if not in_range(date, args.since, args.until):
            continue
        month = date[:7]
        m = monthly[month]
        m["input"] += u["input_tokens"]
        m["output"] += u["output_tokens"]
        m["cache_read"] += u["cache_read"]
        m["cache_create"] += u["cache_create"]
        m["count"] += 1
        _add_tokens(m["per_model"][u["model"]], u)

    return _report_buckets(monthly, "month", "monthly", "Month", args)


# ---------------------------------------------------------------------------
# Subcommand: sessions
# ---------------------------------------------------------------------------

def cmd_sessions(args):
    """Per-session usage report."""
    session_meta_dir = CLAUDE_DIR / "usage-data" / "session-meta"
    sessions = []

    if session_meta_dir.is_dir():
        for path in sorted(session_meta_dir.glob("*.json")):
            try:
                meta = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            start = meta.get("start_time", "")
            date = start[:10] if start else ""
            if not in_range(date, args.since, args.until):
                continue
            sessions.append({
                "session_id": meta.get("session_id", path.stem),
                "date": date,
                "duration_min": meta.get("duration_minutes", 0),
                "messages": meta.get("user_message_count", 0) + meta.get("assistant_message_count", 0),
                "input_tokens": meta.get("input_tokens", 0),
                "output_tokens": meta.get("output_tokens", 0),
                "tools": sum(meta.get("tool_counts", {}).values()),
                "project": meta.get("project_path", ""),
            })
    else:
        # Fallback: aggregate from JSONL
        sess_data = defaultdict(lambda: {"input": 0, "output": 0, "count": 0, "first_ts": "", "last_ts": ""})
        for u, fpath in iter_usage():
            sid = u["session_id"] or os.path.basename(fpath).replace(".jsonl", "")
            date = u["timestamp"][:10]
            if not in_range(date, args.since, args.until):
                continue
            s = sess_data[sid]
            s["input"] += u["input_tokens"]
            s["output"] += u["output_tokens"]
            s["count"] += 1
            if not s["first_ts"] or u["timestamp"] < s["first_ts"]:
                s["first_ts"] = u["timestamp"]
            if not s["last_ts"] or u["timestamp"] > s["last_ts"]:
                s["last_ts"] = u["timestamp"]

        for sid, s in sess_data.items():
            sessions.append({
                "session_id": sid[:12] + "...",
                "date": s["first_ts"][:10],
                "duration_min": 0,
                "messages": s["count"],
                "input_tokens": s["input"],
                "output_tokens": s["output"],
                "tools": 0,
                "project": "",
            })

    sessions.sort(key=lambda s: s["date"], reverse=True)
    if args.last:
        sessions = sessions[:args.last]

    if args.json:
        json.dump({"sessions": sessions}, sys.stdout, indent=2)
        print()
        return

    if not sessions:
        print("No sessions found in the specified date range.")
        return

    rows = []
    for s in sessions:
        rows.append([
            s["date"],
            s["session_id"][:16],
            str(s["messages"]),
            fmt_tokens(s["input_tokens"]),
            fmt_tokens(s["output_tokens"]),
            str(s["tools"]),
            f"{s['duration_min']}m" if s["duration_min"] else "-",
        ])

    print_table(["Date", "Session", "Messages", "Input", "Output", "Tools", "Duration"],
                rows, {2, 3, 4, 5, 6})
    print(f"\nShowing {len(sessions)} session(s)")


# ---------------------------------------------------------------------------
# Subcommand: models
# ---------------------------------------------------------------------------

def cmd_models(args):
    """Per-model all-time usage: stats-cache.json for tokens, the JSONL logs for cost."""
    if pricing_supplied():
        # stats-cache.json does not split 5-minute from 1-hour cache writes, which
        # are billed at different rates; the JSONL logs do.
        return _models_from_logs(args)
    stats = load_stats_cache()
    model_usage = stats.get("modelUsage", {})

    if not model_usage:
        print("No model usage data found in stats-cache.json.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for model, u in sorted(model_usage.items()):
        rows.append([model, fmt_tokens(u.get("inputTokens", 0)), fmt_tokens(u.get("outputTokens", 0)),
                     fmt_tokens(u.get("cacheReadInputTokens", 0)),
                     fmt_tokens(u.get("cacheCreationInputTokens", 0))])

    if args.json:
        doc = {"models": model_usage, "costComplete": False, "costStatus": "unpriced_no_rates"}
        json.dump(doc, sys.stdout, indent=2)
        print()
        return 0

    print_table(["Model", "Input", "Output", "Cache Read", "Cache Create"], rows, {1, 2, 3, 4})
    print(f"Total sessions: {stats.get('totalSessions', '?')}")
    print(f"Total messages: {stats.get('totalMessages', '?')}")
    return 0


def _models_from_logs(args) -> int:
    """Per-model totals and cost from the JSONL logs; return the unpriced count."""
    per_model = defaultdict(lambda: {**_new_tokens(), "count": 0})
    for u, _ in iter_usage():
        _add_tokens(per_model[u["model"]], u)
        per_model[u["model"]]["count"] += 1

    if not per_model:
        print(f"No usage records found in {PROJECTS_DIR}.", file=sys.stderr)
        sys.exit(1)

    rows = []
    total_cost = 0.0
    unpriced = {}
    doc_models = {}
    for model, t in sorted(per_model.items()):
        cost, reason = attribute_cost(model, t["input"], t["output"], t["cache_read"],
                                      t["cache_create"], t["cache_create_1h"])
        if reason:
            unpriced[model] = reason
        else:
            total_cost += cost
        doc_models[model] = {"inputTokens": t["input"], "outputTokens": t["output"],
                             "cacheReadInputTokens": t["cache_read"],
                             "cacheCreationInputTokens": t["cache_create"],
                             "cacheCreation1hInputTokens": t["cache_create_1h"],
                             "messages": t["count"],
                             "costUSD": None if reason else round(cost, 4),
                             "unpricedReason": reason}
        rows.append([model, fmt_tokens(t["input"]), fmt_tokens(t["output"]),
                     fmt_tokens(t["cache_read"]), fmt_tokens(t["cache_create"]), str(t["count"]),
                     f"unpriced ({reason})" if reason else fmt_cost(cost)])

    if args.json:
        json.dump({"models": doc_models, "source": "jsonl_logs",
                   "knownCostUSD": round(total_cost, 4), "costComplete": not unpriced},
                  sys.stdout, indent=2)
        print()
        return len(unpriced)

    print_table(["Model", "Input", "Output", "Cache Read", "Cache Create", "Messages", "Est. Cost"],
                rows, {1, 2, 3, 4, 5, 6})
    print(f"\n{fmt_cost_summary(total_cost, unpriced)}")
    print("Source: JSONL logs (stats-cache.json does not split cache writes by TTL).")
    return len(unpriced)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Claude Code usage reporter — reads local logs, no dependencies required.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Shared args
    def add_common(p):
        p.add_argument("--since", "-s", help="Filter from date (YYYY-MM-DD)")
        p.add_argument("--until", "-u", help="Filter until date (YYYY-MM-DD)")
        p.add_argument("--json", "-j", action="store_true", help="Output as JSON")
        add_pricing(p)

    def add_pricing(p):
        p.add_argument("--pricing", metavar="FILE",
                       help="JSON rates (USD per 1M tokens) from the provider's pricing page; "
                            "see assets/pricing-template.json. Without it, cost is unpriced.")

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
    p_models.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    add_pricing(p_models)
    p_models.set_defaults(func=cmd_models)

    args = parser.parse_args()

    # Normalize date args
    if hasattr(args, "since") and args.since:
        args.since = parse_date(args.since)
    if hasattr(args, "until") and args.until:
        args.until = parse_date(args.until)

    global PRICING
    if args.pricing:
        try:
            PRICING = load_pricing_file(args.pricing)
        except PricingError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        if not PRICING:
            print(f"Error: --pricing file {args.pricing} has no model with both input and "
                  "output rates filled in.", file=sys.stderr)
            sys.exit(2)
    else:
        PRICING = {}

    unpriced = args.func(args)
    if not pricing_supplied():
        print(NO_PRICING_MESSAGE, file=sys.stderr)
    elif unpriced:
        print(f"[WARN] {unpriced} model(s) unpriced; cost totals above are incomplete. "
              "Add their exact rates to your --pricing file.", file=sys.stderr)
        sys.exit(UNPRICED_EXIT)


if __name__ == "__main__":
    main()
