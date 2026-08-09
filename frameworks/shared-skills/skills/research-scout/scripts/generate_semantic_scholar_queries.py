#!/usr/bin/env python3
"""Generate Semantic Scholar API query URLs.

Public API; rate limit ~1 req/sec without key, ~10 req/sec with key.
Docs: https://api.semanticscholar.org/

Usage:
    python3 generate_semantic_scholar_queries.py --topic "RAG evaluation" \\
        --min-citations 5 --windows 365d 1095d
"""

import argparse
import json
import sys
from datetime import date, timedelta
from urllib.parse import urlencode

SEARCH_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
PAPER_BASE = "https://api.semanticscholar.org/graph/v1/paper/{id}"
CITATIONS_BASE = "https://api.semanticscholar.org/graph/v1/paper/{id}/citations"
RECS_BASE = "https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{id}"

DEFAULT_FIELDS = "title,authors,year,citationCount,influentialCitationCount,externalIds,url,abstract"


def parse_window(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("d") and s[:-1].isdigit():
        return int(s[:-1])
    raise argparse.ArgumentTypeError(f"Invalid window format: {s!r}")


def build_search_url(query: str, year_from: int | None, fields: str,
                     limit: int = 50, offset: int = 0) -> str:
    params = {"query": query, "limit": limit, "offset": offset, "fields": fields}
    if year_from is not None:
        params["year"] = f"{year_from}-"
    return f"{SEARCH_BASE}?{urlencode(params)}"


def build_queries(topic: str, windows: list[int], min_citations: int,
                  influential_only: bool) -> list[dict]:
    queries = []
    today = date.today()
    for days in windows:
        year_from = (today - timedelta(days=days)).year
        queries.append({
            "window": f"{days}d",
            "query_type": "topic_search",
            "url": build_search_url(topic, year_from=year_from, fields=DEFAULT_FIELDS),
            "client_filter": (
                f"citationCount >= {min_citations}" +
                (" AND influentialCitationCount >= 3" if influential_only else "")
            ),
        })
    queries.append({
        "window": "all",
        "query_type": "paper_lookup_template",
        "url": PAPER_BASE.format(id="{S2_OR_DOI_OR_ARXIV_ID}"),
        "note": "Substitute paper ID; use after finding a candidate elsewhere.",
    })
    queries.append({
        "window": "all",
        "query_type": "citations_template",
        "url": CITATIONS_BASE.format(id="{paperId}") + f"?fields=title,year,citationCount,intent&limit=100",
        "note": "Substitute paperId to walk the citing graph.",
    })
    queries.append({
        "window": "all",
        "query_type": "recommendations_template",
        "url": RECS_BASE.format(id="{paperId}") + "?limit=20",
        "note": "Substitute paperId for related-papers recommendations.",
    })
    return queries


def main():
    p = argparse.ArgumentParser(description="Generate Semantic Scholar API URLs")
    p.add_argument("--topic", required=True)
    p.add_argument("--windows", nargs="+", default=["365d", "1095d"])
    p.add_argument("--min-citations", type=int, default=5)
    p.add_argument("--influential-only", action="store_true",
                   help="Suggest filtering for influentialCitationCount >= 3")
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    args = p.parse_args()
    windows = [parse_window(w) for w in args.windows]
    out = {
        "source": "semantic_scholar",
        "topic": args.topic,
        "generated_at": date.today().isoformat(),
        "windows": args.windows,
        "queries": build_queries(args.topic, windows, args.min_citations, args.influential_only),
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
