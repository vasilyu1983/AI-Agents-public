#!/usr/bin/env python3
"""Generate arXiv API query URLs for a topic + categories + time windows.

Stdlib only. Outputs JSON or TSV ready to feed into the scout workflow.

arXiv API: https://info.arxiv.org/help/api/index.html
Attribution required for downstream outputs:
    "Thank you to arXiv for use of its open access interoperability."

Usage:
    python3 generate_arxiv_queries.py --topic "agent tool use" \\
        --categories cs.AI cs.CL cs.LG --windows 30d 90d 365d
"""

import argparse
import json
import sys
from datetime import date, timedelta
from urllib.parse import urlencode

BASE_URL = "http://export.arxiv.org/api/query"


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
                  max_results: int) -> list[dict]:
    queries = []
    for days in windows:
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        sq = build_search_query(topic, categories, [])
        queries.append({
            "window": f"{days}d",
            "query_type": "topic_recent",
            "search_query": sq,
            "url": build_query_url(sq, max_results=max_results),
            "client_filter": f"submittedDate >= {cutoff}",
        })
        # Method-shape framings
        for shape_term in ["method", "framework", "evaluation", "benchmark"]:
            sq2 = build_search_query(topic, categories, [shape_term])
            queries.append({
                "window": f"{days}d",
                "query_type": f"shape_{shape_term}",
                "search_query": sq2,
                "url": build_query_url(sq2, max_results=max_results),
                "client_filter": f"submittedDate >= {cutoff}",
            })
    return queries


def main():
    p = argparse.ArgumentParser(description="Generate arXiv API query URLs")
    p.add_argument("--topic", required=True)
    p.add_argument("--categories", nargs="+", default=["cs.AI", "cs.CL", "cs.LG"])
    p.add_argument("--windows", nargs="+", default=["30d", "90d", "365d"])
    p.add_argument("--max-results", type=int, default=50)
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    args = p.parse_args()

    windows = [parse_window(w) for w in args.windows]
    out = {
        "source": "arxiv",
        "topic": args.topic,
        "categories": args.categories,
        "generated_at": date.today().isoformat(),
        "windows": args.windows,
        "attribution": "Thank you to arXiv for use of its open access interoperability.",
        "queries": build_queries(args.topic, args.categories, windows, args.max_results),
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
