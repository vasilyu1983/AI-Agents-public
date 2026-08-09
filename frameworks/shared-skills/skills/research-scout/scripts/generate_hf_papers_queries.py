#!/usr/bin/env python3
"""Generate Hugging Face Papers daily-list URLs for a time window.

HF Papers does not expose a search API; this script emits the per-day
URLs (and trending / RSS endpoints) that the scout walks client-side.

Usage:
    python3 generate_hf_papers_queries.py --topic "agent tool use" --windows 30d 90d
"""

import argparse
import json
import sys
from datetime import date, timedelta

DAILY_URL = "https://huggingface.co/papers?date={iso}"
TRENDING_URL = "https://huggingface.co/papers?date=trending"
RSS_URL = "https://huggingface.co/papers.rss"


def parse_window(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("d") and s[:-1].isdigit():
        return int(s[:-1])
    raise argparse.ArgumentTypeError(f"Invalid window format: {s!r}")


def build_queries(topic: str, windows: list[int]) -> list[dict]:
    queries = [
        {"query_type": "trending", "window": "all", "url": TRENDING_URL,
         "client_filter": f'title or abstract contains "{topic}"'},
        {"query_type": "rss", "window": "all", "url": RSS_URL,
         "client_filter": f'title or summary contains "{topic}"'},
    ]
    today = date.today()
    max_days = max(windows) if windows else 30
    for offset in range(max_days):
        d = today - timedelta(days=offset)
        queries.append({
            "query_type": "daily",
            "window": f"day-{offset}",
            "url": DAILY_URL.format(iso=d.isoformat()),
            "date": d.isoformat(),
            "client_filter": f'title or abstract contains "{topic}"',
        })
    return queries


def main():
    p = argparse.ArgumentParser(description="Generate HF Papers daily-list URLs")
    p.add_argument("--topic", required=True)
    p.add_argument("--windows", nargs="+", default=["30d", "90d"])
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    args = p.parse_args()
    windows = [parse_window(w) for w in args.windows]
    out = {
        "source": "hf_papers",
        "topic": args.topic,
        "generated_at": date.today().isoformat(),
        "windows": args.windows,
        "queries": build_queries(args.topic, windows),
    }
    out["total_queries"] = len(out["queries"])
    if args.format == "json":
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        lines = ["window\tquery_type\turl"]
        for q in out["queries"]:
            lines.append(f'{q["window"]}\t{q["query_type"]}\t{q["url"]}')
        sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
