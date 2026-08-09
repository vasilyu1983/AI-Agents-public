#!/usr/bin/env python3
"""
Claude Code usage reporter — stdlib-only CLI tool.

Reads local Claude Code logs to produce token and cost reports
without any third-party dependencies.

Data sources:
  - ~/.claude/stats-cache.json  (pre-aggregated daily/model stats)
  - ~/.claude/projects/          (raw JSONL session logs)

Subcommands:
  daily    — Usage grouped by date
  monthly  — Monthly aggregated report
  sessions — Per-session detail
  models   — Per-model all-time totals

Usage:
  python scripts/claude-usage.py daily
  python scripts/claude-usage.py daily --since 2026-04-01 --until 2026-04-07
  python scripts/claude-usage.py monthly --json
  python scripts/claude-usage.py sessions --last 10
  python scripts/claude-usage.py models
"""

from __future__ import annotations

import argparse
import glob
import json
import os
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

# Approximate pricing per 1M tokens (April 2026 — update as needed)
PRICING = {
    "claude-opus-4-7":    {"input": 15.00, "output": 75.00, "cache_read": 1.50, "cache_create": 18.75},  # TODO verify post-launch (Opus 4.7 shipped 2026-04-16; tier assumed identical to 4.6 until Anthropic publishes otherwise)
    "claude-opus-4-6":    {"input": 15.00, "output": 75.00, "cache_read": 1.50, "cache_create": 18.75},
    "claude-opus-4-5":    {"input": 15.00, "output": 75.00, "cache_read": 1.50, "cache_create": 18.75},
    "claude-sonnet-4-6":  {"input": 3.00,  "output": 15.00, "cache_read": 0.30, "cache_create": 3.75},
    "claude-sonnet-4-5":  {"input": 3.00,  "output": 15.00, "cache_read": 0.30, "cache_create": 3.75},
    "claude-haiku-4-5":   {"input": 0.80,  "output": 4.00,  "cache_read": 0.08, "cache_create": 1.00},
}
DEFAULT_PRICING = {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_create": 3.75}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def estimate_cost(model: str, inp: int, out: int, cache_read: int, cache_create: int) -> float:
    """Estimate cost in USD from token counts."""
    # Match model to pricing — try exact, then prefix match
    prices = DEFAULT_PRICING
    for key, p in PRICING.items():
        if key in model:
            prices = p
            break
    return (
        inp * prices["input"] / 1_000_000
        + out * prices["output"] / 1_000_000
        + cache_read * prices["cache_read"] / 1_000_000
        + cache_create * prices["cache_create"] / 1_000_000
    )


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
    for path in glob.glob(str(PROJECTS_DIR / "*" / "*.jsonl")):
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
    return {
        "timestamp": rec.get("timestamp", ""),
        "session_id": rec.get("sessionId", ""),
        "model": msg.get("model", "unknown"),
        "input_tokens": usage.get("input_tokens", 0) or 0,
        "output_tokens": usage.get("output_tokens", 0) or 0,
        "cache_read": usage.get("cache_read_input_tokens", 0) or 0,
        "cache_create": usage.get("cache_creation_input_tokens", 0) or 0,
    }


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
            json.dump({"daily": rows_data}, sys.stdout, indent=2)
            print()
            return

        if not rows_data:
            print("No data in the specified date range.")
            return

        rows = [[r["date"], str(r["messages"]), str(r["sessions"]), str(r["tools"])]
                for r in rows_data]
        print_table(["Date", "Messages", "Sessions", "Tool Calls"], rows, {1, 2, 3})

        total_msg = sum(r["messages"] for r in rows_data)
        total_sess = sum(r["sessions"] for r in rows_data)
        total_tools = sum(r["tools"] for r in rows_data)
        print(f"\nTotal: {total_msg:,} messages, {total_sess:,} sessions, {total_tools:,} tool calls")
        return

    # Fallback: parse JSONL
    daily = defaultdict(lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0, "count": 0, "models": set()})
    for rec, _ in iter_jsonl_records():
        u = extract_usage(rec)
        if not u or not u["timestamp"]:
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
        d["models"].add(u["model"])

    if args.json:
        out = []
        for date in sorted(daily):
            d = daily[date]
            cost = estimate_cost("", d["input"], d["output"], d["cache_read"], d["cache_create"])
            out.append({"date": date, "inputTokens": d["input"], "outputTokens": d["output"],
                        "cacheReadTokens": d["cache_read"], "cacheCreateTokens": d["cache_create"],
                        "messages": d["count"], "costUSD": round(cost, 4),
                        "models": sorted(d["models"])})
        json.dump({"daily": out}, sys.stdout, indent=2)
        print()
        return

    rows = []
    total_cost = 0.0
    for date in sorted(daily):
        d = daily[date]
        cost = estimate_cost("", d["input"], d["output"], d["cache_read"], d["cache_create"])
        total_cost += cost
        rows.append([date, fmt_tokens(d["input"]), fmt_tokens(d["output"]),
                      fmt_tokens(d["cache_read"]), str(d["count"]), fmt_cost(cost)])

    if not rows:
        print("No data in the specified date range.")
        return

    print_table(["Date", "Input", "Output", "Cache Read", "Messages", "Est. Cost"],
                rows, {1, 2, 3, 4, 5})
    print(f"\nTotal estimated cost: {fmt_cost(total_cost)}")


# ---------------------------------------------------------------------------
# Subcommand: monthly
# ---------------------------------------------------------------------------

def cmd_monthly(args):
    """Monthly aggregated report from JSONL data."""
    monthly = defaultdict(lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0, "count": 0})

    for rec, _ in iter_jsonl_records():
        u = extract_usage(rec)
        if not u or not u["timestamp"]:
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

    if args.json:
        out = []
        for month in sorted(monthly):
            m = monthly[month]
            cost = estimate_cost("", m["input"], m["output"], m["cache_read"], m["cache_create"])
            out.append({"month": month, "inputTokens": m["input"], "outputTokens": m["output"],
                        "cacheReadTokens": m["cache_read"], "cacheCreateTokens": m["cache_create"],
                        "messages": m["count"], "costUSD": round(cost, 4)})
        json.dump({"monthly": out}, sys.stdout, indent=2)
        print()
        return

    rows = []
    total_cost = 0.0
    for month in sorted(monthly):
        m = monthly[month]
        cost = estimate_cost("", m["input"], m["output"], m["cache_read"], m["cache_create"])
        total_cost += cost
        rows.append([month, fmt_tokens(m["input"]), fmt_tokens(m["output"]),
                      fmt_tokens(m["cache_read"]), str(m["count"]), fmt_cost(cost)])

    if not rows:
        print("No data in the specified date range.")
        return

    print_table(["Month", "Input", "Output", "Cache Read", "Messages", "Est. Cost"],
                rows, {1, 2, 3, 4, 5})
    print(f"\nTotal estimated cost: {fmt_cost(total_cost)}")


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
        for rec, fpath in iter_jsonl_records():
            u = extract_usage(rec)
            if not u:
                continue
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
    """Per-model all-time usage from stats-cache.json."""
    stats = load_stats_cache()
    model_usage = stats.get("modelUsage", {})

    if not model_usage:
        print("No model usage data found in stats-cache.json.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        json.dump({"models": model_usage}, sys.stdout, indent=2)
        print()
        return

    rows = []
    total_cost = 0.0
    for model, u in sorted(model_usage.items()):
        inp = u.get("inputTokens", 0)
        out = u.get("outputTokens", 0)
        cr = u.get("cacheReadInputTokens", 0)
        cc = u.get("cacheCreationInputTokens", 0)
        cost = estimate_cost(model, inp, out, cr, cc)
        total_cost += cost
        rows.append([model, fmt_tokens(inp), fmt_tokens(out), fmt_tokens(cr), fmt_tokens(cc), fmt_cost(cost)])

    print_table(["Model", "Input", "Output", "Cache Read", "Cache Create", "Est. Cost"],
                rows, {1, 2, 3, 4, 5})
    print(f"\nTotal estimated cost: {fmt_cost(total_cost)}")
    print(f"Total sessions: {stats.get('totalSessions', '?')}")
    print(f"Total messages: {stats.get('totalMessages', '?')}")


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
    p_models.set_defaults(func=cmd_models)

    args = parser.parse_args()

    # Normalize date args
    if hasattr(args, "since") and args.since:
        args.since = parse_date(args.since)
    if hasattr(args, "until") and args.until:
        args.until = parse_date(args.until)

    args.func(args)


if __name__ == "__main__":
    main()
