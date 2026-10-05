#!/usr/bin/env python3
"""Generate Hugging Face Papers URLs for a time window.

Emits the HTML pages (per-day list, trending) plus the JSON endpoints the
site itself uses: /api/daily_papers (optionally ?date=YYYY-MM-DD) and
/api/papers/search?q=. HF does not document these endpoints, so the scout
must confirm each returns HTTP 200 JSON on first use and fall back to the
HTML pages if not. huggingface.co/papers.rss and papers?date=trending are
dead (404 / 400) and are no longer emitted.

Usage:
    python3 generate_hf_papers_queries.py --topic "agent tool use" --windows 30d 90d
"""

import argparse
import json
import sys
from datetime import date, timedelta
from urllib.parse import quote_plus

DAILY_URL = "https://huggingface.co/papers?date={iso}"
DAILY_API_URL = "https://huggingface.co/api/daily_papers?date={iso}"
TRENDING_URL = "https://huggingface.co/papers/trending"
SEARCH_API_URL = "https://huggingface.co/api/papers/search?q={q}"


def parse_window(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("d") and s[:-1].isdigit():
        return int(s[:-1])
    raise argparse.ArgumentTypeError(f"Invalid window format: {s!r}")


def build_queries(topic: str, windows: list[int]) -> list[dict]:
    verify = "undocumented JSON endpoint: confirm HTTP 200 JSON on first use, else use the HTML pages"
    queries = [
        {"query_type": "trending", "window": "all", "url": TRENDING_URL,
         "client_filter": f'title or abstract contains "{topic}"'},
        {"query_type": "search_api", "window": "all",
         "url": SEARCH_API_URL.format(q=quote_plus(topic)), "note": verify},
    ]
    today = date.today()
    max_days = max(windows) if windows else 30
    for offset in range(max_days):
        d = today - timedelta(days=offset)
        queries.append({
            "query_type": "daily",
            "window": f"day-{offset}",
            "url": DAILY_URL.format(iso=d.isoformat()),
            "api_url": DAILY_API_URL.format(iso=d.isoformat()),
            "date": d.isoformat(),
            "client_filter": f'title or abstract contains "{topic}"',
            "note": verify,
        })
    return queries


def main():
    p = argparse.ArgumentParser(description="Generate HF Papers page and JSON URLs")
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
