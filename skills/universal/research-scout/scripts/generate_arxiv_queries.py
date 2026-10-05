#!/usr/bin/env python3
"""Generate arXiv API query URLs for a topic + categories + time windows.

Stdlib only. Outputs JSON or TSV ready to feed into the scout workflow.

arXiv API: https://info.arxiv.org/help/api/index.html
Each window is applied server-side as a `submittedDate:[... TO ...]` range
(GMT, to the minute), so 30d/90d/365d queries return different result sets.
Each query carries a pagination plan: read `opensearch:totalResults`, report
coverage as fetched/total, and narrow the query instead of paging past
`--max-pages`. A first page is never "the top of the window".

Attribution required for downstream outputs:
    "Thank you to arXiv for use of its open access interoperability."

Usage:
    python3 generate_arxiv_queries.py --topic "agent tool use" \\
        --categories cs.AI cs.CL cs.LG --windows 30d 90d 365d
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode

BASE_URL = "https://export.arxiv.org/api/query"
# arXiv returns at most 2000 results per call (user manual, "max_results").
MAX_PAGE_SIZE = 2000


def parse_window(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("d") and s[:-1].isdigit():
        return int(s[:-1])
    raise argparse.ArgumentTypeError(f"Invalid window format: {s!r}")


def build_search_query(topic: str, categories: list[str], extra_terms: list[str]) -> str:
    cat_clause = " OR ".join(f"cat:{c}" for c in categories)
    topic_terms = topic.split()
    if len(topic_terms) > 1:
        topic_clause = f'"{topic}"'
    else:
        topic_clause = topic
    parts = [f"({cat_clause})", f"abs:{topic_clause}"]
    for term in extra_terms:
        parts.append(f'abs:"{term}"' if " " in term else f"abs:{term}")
    return " AND ".join(parts)


def window_range(days: int, today: date) -> tuple[str, str]:
    """Return the arXiv submittedDate bounds (YYYYMMDDTTTT, GMT) for a window."""
    start = today - timedelta(days=days)
    return start.strftime("%Y%m%d") + "0000", today.strftime("%Y%m%d") + "2359"


def with_window(search_query: str, days: int, today: date) -> str:
    lo, hi = window_range(days, today)
    return f"({search_query}) AND submittedDate:[{lo} TO {hi}]"


def pagination_plan(max_results: int, max_pages: int) -> dict:
    return {
        "page_size": max_results,
        "max_pages": max_pages,
        "next_page": f"repeat the URL with start += {max_results}, >=3s apart",
        "stop_when": "start >= opensearch:totalResults or a page returns no entries",
        "coverage": "report fetched/opensearch:totalResults for every query",
        "if_total_exceeds": (
            f"{max_results * max_pages}: narrow the query (fewer categories, more "
            "specific terms, shorter window) instead of paging further; never call "
            "a partial fetch the top of the window"
        ),
    }


def build_query_url(search_query: str, max_results: int = 50, sort_by: str = "submittedDate",
                    sort_order: str = "descending", start: int = 0) -> str:
    params = {
        "search_query": search_query,
        "sortBy": sort_by,
        "sortOrder": sort_order,
        "start": start,
        "max_results": max_results,
    }
    return f"{BASE_URL}?{urlencode(params, safe=':+')}"


def build_queries(topic: str, categories: list[str], windows: list[int],
                  max_results: int, max_pages: int = 4,
                  today: date | None = None) -> list[dict]:
    today = today or datetime.now(timezone.utc).date()
    plan = pagination_plan(max_results, max_pages)
    queries = []
    for days in windows:
        lo, hi = window_range(days, today)
        framings = [("topic_recent", [])] + [
            (f"shape_{t}", [t]) for t in ["method", "framework", "evaluation", "benchmark"]
        ]
        for query_type, extra in framings:
            sq = with_window(build_search_query(topic, categories, extra), days, today)
            queries.append({
                "window": f"{days}d",
                "window_submitted": f"{lo} TO {hi} GMT",
                "query_type": query_type,
                "search_query": sq,
                "url": build_query_url(sq, max_results=max_results),
                "pagination": plan,
            })
    return queries


def main():
    p = argparse.ArgumentParser(description="Generate arXiv API query URLs")
    p.add_argument("--topic", required=True)
    p.add_argument("--categories", nargs="+", default=["cs.AI", "cs.CL", "cs.LG"])
    p.add_argument("--windows", nargs="+", default=["30d", "90d", "365d"])
    p.add_argument("--max-results", type=int, default=50,
                   help=f"Page size, 1-{MAX_PAGE_SIZE} (arXiv per-call cap)")
    p.add_argument("--max-pages", type=int, default=4,
                   help="Pages to fetch per query before narrowing it instead")
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    args = p.parse_args()

    if not 1 <= args.max_results <= MAX_PAGE_SIZE:
        p.error(f"--max-results must be 1-{MAX_PAGE_SIZE}")
    if args.max_pages < 1:
        p.error("--max-pages must be >= 1")
    try:
        windows = [parse_window(w) for w in args.windows]
    except argparse.ArgumentTypeError as exc:
        p.error(str(exc))
    out = {
        "source": "arxiv",
        "topic": args.topic,
        "categories": args.categories,
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "windows": args.windows,
        "attribution": "Thank you to arXiv for use of its open access interoperability.",
        "queries": build_queries(args.topic, args.categories, windows, args.max_results,
                                 args.max_pages),
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
