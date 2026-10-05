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
  python scripts/codex-usage.py traces --pricing my-rates.json

Cost needs rates you supply: pass --pricing <file.json> (schema in
../assets/pricing-template.json) filled in from the provider's pricing page.
No rates ship with this script because published rates change. Without
--pricing the token report runs as normal and cost is reported as unpriced;
no cost figure is printed. With --pricing, attribution is fail-closed: an
unknown model, a logged non-standard service tier or context band, or a missing
cache rate is reported as unpriced with a reason, never at a guessed rate, and
the script exits 3 (the same rule as claude-usage.py).

Every report prices per logged event, carrying each event's model, tier and
context class, then sums; daily, monthly, sessions and models therefore match
traces. Codex logs the service tier only in thread_settings_applied events, and
only when a tier is set ("default" is the standard tier); it never logs the
long-context pricing class. When either is absent the script assumes the
standard tier and the base (standard) context class, marks those costs
`estimated`, and says so in the output. If a priority tier went unlogged or
a run passed a long-context threshold, these costs are too low.

Exit codes: 0 = report complete (or tokens only, without --pricing); 1 = no data;
2 = unreadable --pricing file; 3 = report printed with --pricing but at least one
event is unpriced, so any cost total is a known subtotal only.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
SESSIONS_DIR = CODEX_HOME / "sessions"

# ---------------------------------------------------------------------------
# Pricing — user-supplied only.
#
# No rates are embedded: a built-in table goes stale within weeks and then
# prints confident wrong numbers. The user passes --pricing with rates copied
# from the provider's pricing page (USD per 1M tokens); without it, cost is
# reported as unpriced.
# ---------------------------------------------------------------------------

PRICING_PAGE = "https://developers.openai.com/api/docs/pricing"
NO_PRICING_MESSAGE = (
    "Cost: unpriced (no rates supplied). Pass --pricing <file.json> with rates from "
    f"the provider's pricing page ({PRICING_PAGE}); schema: assets/pricing-template.json."
)

# Filled by main() from --pricing. Empty means "no rates supplied".
PRICING: dict = {}
PRICING_FILE: Path | None = None
PRICING_RETRIEVED_AT: str | None = None
UNPRICED_EXIT = 3
# Assumed when the log does not carry the field (real Codex logs never do).
DEFAULT_SERVICE_TIER = "standard"

DEFAULT_CONTEXT_PRICING_CLASS = "standard"


def logged_tier(value):
    """Codex logs the standard tier as "default"; other values pass through."""
    return DEFAULT_SERVICE_TIER if value == "default" else value


class PricingError(ValueError):
    """The --pricing file is missing, unreadable, or malformed."""


def _rate(entry: dict, field: str, model: str) -> float | None:
    value = entry.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise PricingError(f"{model}: {field} must be a non-negative number or null")
    return float(value)


def load_pricing_file(path: str | Path) -> tuple[dict, str | None]:
    """Parse a user pricing file; return ({model_id: rates}, retrieved_at).

    Schema: {"source_url": str, "retrieved_at": "YYYY-MM-DD", "models":
    {"<model-id>": {"input_per_1m": n, "output_per_1m": n, "cache_read_per_1m":
    n|null, "cache_write_per_1m": n|null}}}. A "vendor/" prefix on the ID is
    dropped. Rows with a null input or output rate are skipped (unfilled template
    rows). A null cache rate stays missing: usage that needs it is unpriced,
    never charged at an assumed ratio of the input rate.
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
        row = {"input": inp, "output": out,
               "rate_source": entry.get("source_url") or doc.get("source_url"),
               "rate_verified_at": entry.get("retrieved_at") or doc.get("retrieved_at")}
        cached = _rate(entry, "cache_read_per_1m", model)
        cache_write = _rate(entry, "cache_write_per_1m", model)
        if cached is not None:
            row["cached"] = cached
        if cache_write is not None:
            row["cache_write"] = cache_write
        table[model] = row
    retrieved = doc.get("retrieved_at")
    return table, retrieved if isinstance(retrieved, str) else None


def pricing_supplied() -> bool:
    return bool(PRICING)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pricing_provenance() -> dict:
    """Return bounded, reproducible provenance; never emit session content."""
    digest = None
    if PRICING_FILE is not None:
        try:
            digest = hashlib.sha256(Path(PRICING_FILE).read_bytes()).hexdigest()
        except OSError:
            pass
    return {
        "pricingSource": str(PRICING_FILE) if PRICING_FILE is not None else None,
        "pricingRetrievedAt": PRICING_RETRIEVED_AT,
        "pricingSha256": digest,
    }


def attribute_cost(model: str, inp: int, out: int, cached: int,
                   cache_write: int = 0, *, usage_source: str = "last",
                   service_tier: str | None = None,
                   context_pricing_class: str | None = None) -> dict:
    """Fail-closed cost attribution for one logged request.

    The local log records the service tier only when one is set, and never the
    pricing-context band. None means "not logged": the documented defaults are assumed, listed in
    `assumedDefaults`, and the cost is `estimated`, never `exact`. A logged
    value other than standard stays unpriced. `last` is a request counter; a
    reconstructed cumulative delta is estimated. Reasoning is deliberately
    absent: it is included in output_tokens.
    """
    provenance = pricing_provenance()
    prices = PRICING.get(model)
    assumed = []
    if service_tier is None:
        service_tier = DEFAULT_SERVICE_TIER
        assumed.append(f"service_tier={DEFAULT_SERVICE_TIER}")
    if context_pricing_class is None:
        context_pricing_class = DEFAULT_CONTEXT_PRICING_CLASS
        assumed.append(f"context_pricing_class={DEFAULT_CONTEXT_PRICING_CLASS}")
    result = {
        "model": model,
        "usageSource": usage_source,
        "costUSD": None,
        "costStatus": "unpriced",
        "unpricedReason": None,
        "assumedDefaults": assumed,
        **provenance,
    }
    if not PRICING:
        result["unpricedReason"] = "no_rates_supplied"
        return result
    if prices is None:
        result["unpricedReason"] = "unknown_model_id"
        return result
    result["rateSource"] = prices.get("rate_source")
    result["rateVerifiedAt"] = prices.get("rate_verified_at")
    if service_tier != "standard":
        result["unpricedReason"] = "ambiguous_service_tier"
        return result
    if context_pricing_class != "standard":
        result["unpricedReason"] = "ambiguous_long_context_pricing"
        return result
    if cached and "cached" not in prices:
        result["unpricedReason"] = "cached_rate_unavailable"
        return result
    if cache_write and "cache_write" not in prices:
        result["unpricedReason"] = "cache_write_rate_unavailable"
        return result
    non_cached = max(0, inp - cached - cache_write)
    result["costUSD"] = (
        non_cached * prices["input"] / 1_000_000
        + cached * prices.get("cached", 0) / 1_000_000
        + cache_write * prices.get("cache_write", 0) / 1_000_000
        + out * prices["output"] / 1_000_000
    )
    result["costStatus"] = "exact" if usage_source == "last" and not assumed else "estimated"
    return result


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
    return "unpriced" if c is None else f"${c:.2f}"


def new_cost() -> dict:
    """Per-bucket cost accumulator, filled event by event from attribution."""
    return {"known": 0.0, "unpriced": 0, "reasons": defaultdict(int), "assumed": 0}


def add_cost(acc: dict, attribution: dict) -> None:
    if attribution["costUSD"] is None:
        acc["unpriced"] += 1
        acc["reasons"][attribution["unpricedReason"]] += 1
    else:
        acc["known"] += attribution["costUSD"]
        acc["assumed"] += bool(attribution["assumedDefaults"])


def merge_cost(total: dict, acc: dict) -> None:
    total["known"] += acc["known"]
    total["unpriced"] += acc["unpriced"]
    total["assumed"] += acc["assumed"]
    for reason, n in acc["reasons"].items():
        total["reasons"][reason] += n


def cost_json(acc: dict) -> dict:
    """JSON cost fields: costUSD only when every event in the bucket is priced."""
    if not pricing_supplied():
        return {"costUSD": None}
    return {"costUSD": None if acc["unpriced"] else round(acc["known"], 4),
            "knownCostUSD": round(acc["known"], 4), "unpricedEvents": acc["unpriced"],
            "unpricedReasons": dict(acc["reasons"]), "assumedDefaultEvents": acc["assumed"]}


def fmt_bucket_cost(acc: dict) -> str:
    if not acc["unpriced"]:
        return fmt_cost(acc["known"])
    if acc["known"] == 0:
        return "unpriced"
    return f"{fmt_cost(acc['known'])}+unpriced"


def assumption_note(assumed: int) -> str | None:
    if not assumed:
        return None
    return (f"Assumed service_tier={DEFAULT_SERVICE_TIER} and "
            f"context_pricing_class={DEFAULT_CONTEXT_PRICING_CLASS} for {assumed} "
            "priced event(s): Codex logs do not record them. These costs are estimates, "
            "and they are understated if a priority tier or long-context billing applied.")


def print_cost_report(headers: list, rows: list, right: set, total: dict) -> None:
    """Print the table; without --pricing drop the cost column and the summary."""
    if not pricing_supplied():
        print_table(headers[:-1], [row[:-1] for row in rows], {i for i in right if i < len(headers) - 1})
        return
    print_table(headers, rows, right)
    unpriced_rows = sum(1 for row in rows if row[-1].endswith("unpriced"))
    print(f"\nCost summary: {fmt_cost_summary(total['known'], unpriced_rows)}")
    if total["reasons"]:
        detail = ", ".join(f"{r} ({n} event(s))" for r, n in sorted(total["reasons"].items()))
        print(f"Unpriced: {detail}")
    note = assumption_note(total["assumed"])
    if note:
        print(note)


def json_summary(total: dict) -> dict:
    if not pricing_supplied():
        return {"costComplete": False, "costStatus": "unpriced_no_rates"}
    summary = {"knownCostUSD": round(total["known"], 4), "costComplete": not total["unpriced"],
               "unpricedReasons": dict(total["reasons"]),
               "assumedDefaults": {"service_tier": DEFAULT_SERVICE_TIER,
                                   "context_pricing_class": DEFAULT_CONTEXT_PRICING_CLASS,
                                   "events": total["assumed"]}}
    note = assumption_note(total["assumed"])
    if note:
        summary["costNote"] = note
    return summary


def fmt_cost_summary(priced_total: float, unpriced_rows: int) -> str:
    """Do not render an incomplete aggregation as a $0.00 total."""
    if not unpriced_rows:
        return fmt_cost(priced_total)
    if priced_total == 0:
        return "unpriced"
    return f"${priced_total:.2f} known subtotal; {unpriced_rows} unpriced row(s)"


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
    service_tier = None
    context_pricing_class = None
    prev_totals = {"input_tokens": 0, "cached_input_tokens": 0,
                   "cache_write_input_tokens": 0, "output_tokens": 0,
                   "reasoning_output_tokens": 0}
    have_prev_total = False

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
                # A model switch does not restart total_token_usage: in real
                # logs the running total keeps growing across it. Only a
                # decrease starts a new epoch (handled below).
                if model:
                    current_model = model
                # Only a key that is present replaces a tier logged earlier.
                if "service_tier" in payload:
                    service_tier = logged_tier(payload["service_tier"])
                context_pricing_class = payload.get("context_pricing_class")

            # Codex logs the tier in thread_settings_applied, and only when one is set;
            # each event is a full snapshot, so a missing key means "not logged".
            if rec_type == "event_msg" and payload.get("type") == "thread_settings_applied":
                thread_settings = payload.get("thread_settings")
                if isinstance(thread_settings, dict):
                    service_tier = logged_tier(thread_settings.get("service_tier"))

            # Extract token usage from event_msg with token_count
            if rec_type == "event_msg" and payload.get("type") == "token_count":
                info = payload.get("info")
                if not isinstance(info, dict):
                    continue

                timestamp = rec.get("timestamp", "")

                # Prefer last_token_usage (per-turn delta)
                last = info.get("last_token_usage")
                total = info.get("total_token_usage")
                if isinstance(last, dict):
                    if isinstance(total, dict):
                        raw = {key: total.get(key, 0) or 0 for key in prev_totals}
                        # Codex re-emits a token_count event without a new
                        # request; an unchanged cumulative total means nothing
                        # new was billed, so its last_token_usage is a repeat.
                        if have_prev_total and raw == prev_totals:
                            continue
                    yield {
                        "timestamp": timestamp,
                        "model": current_model,
                        "input": last.get("input_tokens", 0) or 0,
                        "output": last.get("output_tokens", 0) or 0,
                        "cached": last.get("cached_input_tokens", 0) or 0,
                        "cache_write": last.get("cache_write_input_tokens", 0) or 0,
                        "reasoning": last.get("reasoning_output_tokens", 0) or 0,
                        "usage_source": "last",
                        "service_tier": service_tier,
                        "context_pricing_class": context_pricing_class,
                    }
                    if isinstance(total, dict):
                        prev_totals = raw
                        have_prev_total = True
                    continue

                # Fallback: compute delta from cumulative total_token_usage
                if isinstance(total, dict):
                    raw = {key: total.get(key, 0) or 0 for key in prev_totals}
                    reset = any(raw[key] < prev_totals[key] for key in prev_totals)
                    base = {key: 0 for key in prev_totals} if reset else prev_totals
                    inp = raw["input_tokens"] - base["input_tokens"]
                    out = raw["output_tokens"] - base["output_tokens"]
                    cached = raw["cached_input_tokens"] - base["cached_input_tokens"]
                    reasoning = raw["reasoning_output_tokens"] - base["reasoning_output_tokens"]
                    cache_write = raw.get("cache_write_input_tokens", 0) - base.get("cache_write_input_tokens", 0)

                    if inp > 0 or out > 0:
                        yield {
                            "timestamp": timestamp,
                            "model": current_model,
                            "input": max(0, inp),
                            "output": max(0, out),
                            "cached": max(0, cached),
                            "cache_write": max(0, cache_write),
                            "reasoning": max(0, reasoning),
                            "usage_source": "total_delta_reset" if reset else "total_delta",
                            "service_tier": service_tier,
                            "context_pricing_class": context_pricing_class,
                        }

                    prev_totals = raw
                    have_prev_total = True


def iter_all_events(since: str | None = None, until: str | None = None):
    """Yield all token usage events across all sessions, optionally filtered by date."""
    for path, session_id in iter_session_files():
        for event in parse_session_events(path):
            date = event["timestamp"][:10]
            if not in_range(date, since, until):
                continue
            event["session_id"] = session_id
            event["attribution"] = attribute_cost(
                event["model"], event["input"], event["output"], event["cached"],
                event.get("cache_write", 0), usage_source=event["usage_source"],
                service_tier=event.get("service_tier"),
                context_pricing_class=event.get("context_pricing_class"),
            )
            yield event


# ---------------------------------------------------------------------------
# Aggregation: every report sums per-event attribution, so each event is priced
# with its own model, tier and context class, exactly as `traces` prices it.
# ---------------------------------------------------------------------------

def aggregate(args, key_fn) -> tuple[dict, dict]:
    """Return ({key: bucket}, total cost accumulator); exit 1 when there is no data."""
    buckets = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "reasoning": 0,
                                   "turns": 0, "models": set(), "first_ts": "", "last_ts": "",
                                   "model": "unknown", "cost": new_cost()})
    for ev in iter_all_events(args.since, args.until):
        b = buckets[key_fn(ev)]
        b["input"] += ev["input"]
        b["output"] += ev["output"]
        b["cached"] += ev["cached"]
        b["reasoning"] += ev["reasoning"]
        b["turns"] += 1
        b["models"].add(ev["model"])
        b["model"] = ev["model"]
        if not b["first_ts"] or ev["timestamp"] < b["first_ts"]:
            b["first_ts"] = ev["timestamp"]
        if not b["last_ts"] or ev["timestamp"] > b["last_ts"]:
            b["last_ts"] = ev["timestamp"]
        add_cost(b["cost"], ev["attribution"])

    if not buckets:
        print(f"No data found. Checked: {SESSIONS_DIR}", file=sys.stderr)
        sys.exit(1)
    total = new_cost()
    for b in buckets.values():
        merge_cost(total, b["cost"])
    return buckets, total


def token_json(b: dict) -> dict:
    return {"inputTokens": b["input"], "outputTokens": b["output"],
            "cachedInputTokens": b["cached"], "reasoningOutputTokens": b["reasoning"],
            "turns": b["turns"]}


def token_cells(b: dict) -> list:
    return [fmt_tokens(b["input"]), fmt_tokens(b["output"]), fmt_tokens(b["cached"]),
            fmt_tokens(b["reasoning"]), str(b["turns"])]


def period_report(args, key_fn, key_name: str, label: str) -> int:
    buckets, total = aggregate(args, key_fn)
    if args.json:
        out = [{key_name: key, **token_json(buckets[key]), **cost_json(buckets[key]["cost"]),
                "models": sorted(buckets[key]["models"])} for key in sorted(buckets)]
        json.dump({{"date": "daily", "month": "monthly"}[key_name]: out, **json_summary(total)},
                  sys.stdout, indent=2)
        print()
        return total["unpriced"]
    rows = [[key, *token_cells(buckets[key]), fmt_bucket_cost(buckets[key]["cost"])]
            for key in sorted(buckets)]
    print_cost_report([label, "Input", "Output", "Cached", "Reasoning", "Turns", "Est. Cost"],
                      rows, {1, 2, 3, 4, 5, 6}, total)
    return total["unpriced"]


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_daily(args):
    return period_report(args, lambda ev: ev["timestamp"][:10], "date", "Date")


def cmd_monthly(args):
    return period_report(args, lambda ev: ev["timestamp"][:7], "month", "Month")


def cmd_sessions(args):
    sess, total = aggregate(args, lambda ev: ev["session_id"])
    # Sort by most recent first
    sorted_sessions = sorted(sess.items(), key=lambda kv: kv[1]["last_ts"], reverse=True)
    if args.last:
        sorted_sessions = sorted_sessions[:args.last]
    shown = new_cost()
    for _, s in sorted_sessions:
        merge_cost(shown, s["cost"])

    if args.json:
        out = [{"sessionId": sid, "date": s["first_ts"][:10], "model": s["model"],
                "models": sorted(s["models"]), "inputTokens": s["input"],
                "outputTokens": s["output"], "cachedInputTokens": s["cached"],
                "turns": s["turns"], **cost_json(s["cost"])}
               for sid, s in sorted_sessions]
        json.dump({"sessions": out, **json_summary(shown)}, sys.stdout, indent=2)
        print()
        return shown["unpriced"]

    rows = []
    for sid, s in sorted_sessions:
        # Truncate session ID for display
        short_id = sid[:30] + "..." if len(sid) > 33 else sid
        rows.append([s["first_ts"][:10], short_id, s["model"],
                     fmt_tokens(s["input"]), fmt_tokens(s["output"]),
                     str(s["turns"]), fmt_bucket_cost(s["cost"])])

    print_cost_report(["Date", "Session", "Model", "Input", "Output", "Turns", "Est. Cost"],
                      rows, {3, 4, 5, 6}, shown)
    print(f"Showing {len(sorted_sessions)} session(s)")
    return shown["unpriced"]


def cmd_models(args):
    models, total = aggregate(args, lambda ev: ev["model"])
    if args.json:
        out = {model: {**token_json(m), **cost_json(m["cost"])}
               for model, m in sorted(models.items())}
        json.dump({"models": out, **json_summary(total)}, sys.stdout, indent=2)
        print()
        return total["unpriced"]

    rows = [[model, *token_cells(m), fmt_bucket_cost(m["cost"])]
            for model, m in sorted(models.items())]
    print_cost_report(["Model", "Input", "Output", "Cached", "Reasoning", "Turns", "Est. Cost"],
                      rows, {1, 2, 3, 4, 5, 6}, total)
    return total["unpriced"]


def cmd_traces(args):
    """Emit bounded per-request accounting rows, never transcript payloads."""
    rows = []
    unpriced = assumed = 0
    for ev in iter_all_events(args.since, args.until):
        a = ev["attribution"]
        unpriced += a["costUSD"] is None
        assumed += a["costUSD"] is not None and bool(a["assumedDefaults"])
        rows.append({
            "sessionId": ev["session_id"], "timestamp": ev["timestamp"],
            "model": ev["model"], "inputTokens": ev["input"],
            "cachedInputTokens": ev["cached"], "cacheWriteInputTokens": ev.get("cache_write", 0),
            "outputTokens": ev["output"], "usageSource": ev["usage_source"],
            "costUSD": a["costUSD"], "costStatus": a["costStatus"],
            "unpricedReason": a["unpricedReason"], "assumedDefaults": a["assumedDefaults"],
            "pricingSource": a["pricingSource"],
            "pricingRetrievedAt": a["pricingRetrievedAt"], "pricingSha256": a["pricingSha256"],
            "rateSource": a.get("rateSource"), "rateVerifiedAt": a.get("rateVerifiedAt"),
        })
    doc = {"traces": rows}
    note = assumption_note(assumed)
    if note:
        doc["costNote"] = note
    json.dump(doc, sys.stdout, indent=2)
    print()
    return unpriced


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
    add_common(p_models)
    p_models.set_defaults(func=cmd_models)

    p_traces = sub.add_parser("traces", help="Per-request bounded cost-attribution JSON")
    add_common(p_traces)
    p_traces.set_defaults(func=cmd_traces)

    args = parser.parse_args()

    if hasattr(args, "since") and args.since:
        args.since = parse_date(args.since)
    if hasattr(args, "until") and args.until:
        args.until = parse_date(args.until)

    global PRICING, PRICING_FILE, PRICING_RETRIEVED_AT
    if args.pricing:
        try:
            PRICING, PRICING_RETRIEVED_AT = load_pricing_file(args.pricing)
        except PricingError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        if not PRICING:
            print(f"Error: --pricing file {args.pricing} has no model with both input and "
                  "output rates filled in.", file=sys.stderr)
            sys.exit(2)
        PRICING_FILE = Path(args.pricing)

    unpriced = args.func(args)
    if not pricing_supplied():
        print(NO_PRICING_MESSAGE, file=sys.stderr)
    elif unpriced:
        print(f"[WARN] {unpriced} event(s) unpriced; cost totals above are incomplete. "
              "Add their exact model IDs and rates to your --pricing file.", file=sys.stderr)
        sys.exit(UNPRICED_EXIT)


if __name__ == "__main__":
    main()
