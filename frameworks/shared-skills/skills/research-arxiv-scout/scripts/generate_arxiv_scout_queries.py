#!/usr/bin/env python3
"""Generate arXiv API query URLs from a config.yaml skill key or an ad-hoc topic.

Stdlib only (no pyyaml) to preserve the skill's `compatibility: Portable core`
contract. Emits JSON or TSV ready to feed into the triage workflow.

Differs from ../../research-scout/scripts/generate_arxiv_queries.py: that one is
topic-driven for cross-source scans; this one resolves categories, keywords, and
time windows from `config.yaml` `category_mappings`, which is what this skill owns.

arXiv API: https://info.arxiv.org/help/api/index.html
Rate limit (enforced since Feb 2026): 1 request / 3s, single connection.
On HTTP 429 back off exponentially (30s -> 60s -> 120s); never tight-retry.
See references/arxiv-api-guide.md#rate-limiting-enforced-as-of-2026.

Attribution required for downstream outputs:
    "Thank you to arXiv for use of its open access interoperability."

Usage:
    python3 generate_arxiv_scout_queries.py --skill ai-agents
    python3 generate_arxiv_scout_queries.py --skill killer-feature-retention
    python3 generate_arxiv_scout_queries.py --topic "agent memory" \\
        --categories cs.AI cs.CL --windows 30d 90d
    python3 generate_arxiv_scout_queries.py --list-skills
"""

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

BASE_URL = "http://export.arxiv.org/api/query"
ATTRIBUTION = "Thank you to arXiv for use of its open access interoperability."
MIN_REQUEST_GAP_SECONDS = 3
DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


def load_category_mappings(config_path: Path) -> dict:
    """Minimal parser for the `category_mappings:` block of config.yaml.

    Handles exactly the shape this skill's config uses: two-space-indented keys,
    each with `categories: [...]`, `keywords: [...]`, `time_window_months: N`.
    Deliberately not a general YAML parser -- it fails loud on an unexpected shape
    rather than silently returning partial mappings.
    """
    if not config_path.exists():
        raise SystemExit(f"ERROR: config not found: {config_path}")

    text = config_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    try:
        start = next(i for i, l in enumerate(lines) if l.rstrip() == "category_mappings:")
    except StopIteration:
        raise SystemExit(f"ERROR: no `category_mappings:` block in {config_path}")

    mappings: dict[str, dict] = {}
    current: str | None = None
    # Flow sequences may wrap across lines, e.g.
    #     keywords: ["a", "b",
    #                "c"]
    # so we accumulate until the closing bracket instead of requiring it inline.
    pending_field: str | None = None
    pending_raw = ""

    def flush(field: str, raw: str) -> None:
        assert current is not None
        mappings[current][field] = [
            v.strip().strip('"').strip("'") for v in raw.split(",") if v.strip()
        ]

    for line in lines[start + 1:]:
        if pending_field:
            pending_raw += " " + line.strip()
            if "]" in line:
                flush(pending_field, pending_raw.split("]", 1)[0])
                pending_field, pending_raw = None, ""
            continue
        if line.strip() == "" or line.lstrip().startswith("#"):
            continue
        # A non-indented, non-list line ends the block.
        if not line.startswith(" ") and not line.startswith("-"):
            break
        m_key = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
        if m_key:
            current = m_key.group(1)
            mappings[current] = {"categories": [], "keywords": [], "time_window_months": None}
            continue
        if current is None:
            continue
        m_open = re.match(r"^\s+(categories|keywords):\s*\[(.*)$", line)
        if m_open:
            field, rest = m_open.group(1), m_open.group(2)
            if "]" in rest:
                flush(field, rest.split("]", 1)[0])
            else:
                pending_field, pending_raw = field, rest
            continue
        m_int = re.match(r"^\s+time_window_months:\s*(\d+)\s*$", line)
        if m_int:
            mappings[current]["time_window_months"] = int(m_int.group(1))

    if pending_field:
        raise SystemExit(
            f"ERROR: unterminated `{pending_field}:` list in {config_path} "
            f"(missing closing `]`)")

    if not mappings:
        raise SystemExit(f"ERROR: parsed `category_mappings:` but found no keys in {config_path}")
    return mappings


def parse_window(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("d") and s[:-1].isdigit():
        return int(s[:-1])
    if s.endswith("m") and s[:-1].isdigit():
        return int(s[:-1]) * 30
    raise argparse.ArgumentTypeError(f"Invalid window format: {s!r} (expected e.g. 30d or 6m)")


def build_search_query(topic: str | None, categories: list[str],
                       extra_terms: list[str]) -> str:
    """Build an arXiv `search_query`. A None topic yields a category+keyword query.

    Passing None matters for synthetic topics: ANDing `abs:"killer feature retention"`
    into every keyword query would gut recall exactly as the standalone phrase query
    did. The category set plus the curated keyword is the real query.
    """
    cat_clause = " OR ".join(f"cat:{c}" for c in categories)
    parts = [f"({cat_clause})"]
    if topic:
        parts.append(f'abs:"{topic}"' if " " in topic.strip() else f"abs:{topic}")
    for term in extra_terms:
        parts.append(f'abs:"{term}"' if " " in term else f"abs:{term}")
    return " AND ".join(parts)


def build_query_url(search_query: str, max_results: int = 50,
                    sort_by: str = "submittedDate", sort_order: str = "descending",
                    start: int = 0) -> str:
    params = {
        "search_query": search_query,
        "sortBy": sort_by,
        "sortOrder": sort_order,
        "start": start,
        "max_results": max_results,
    }
    return f"{BASE_URL}?{urlencode(params, safe=':+')}"


def build_queries(topic: str, categories: list[str], keywords: list[str],
                  windows: list[int], max_results: int,
                  include_topic_query: bool = True) -> list[dict]:
    """One broad topic query per window, plus one query per config keyword.

    Keyword queries are the reason to use this generator over the research-scout
    one: config.yaml keywords are curated per skill domain, so they beat generic
    method-shape framings for recall inside a known category set.

    `include_topic_query` is False when the topic was synthesised from a skill key
    that is not itself a searchable phrase (e.g. `killer-feature-retention` ->
    `abs:"killer feature retention"` matches ~nothing). Emitting that query would
    return HTTP 200 with zero results, which reads as "no papers exist" rather
    than "the query was malformed" -- a silent failure, so we omit it instead.
    """
    # A topic we are not searching on must not be ANDed into keyword queries either.
    search_topic = topic if include_topic_query else None
    queries = []
    for days in windows:
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        if include_topic_query:
            sq = build_search_query(topic, categories, [])
            queries.append({
                "window": f"{days}d",
                "query_type": "topic_recent",
                "search_query": sq,
                "url": build_query_url(sq, max_results=max_results),
                "client_filter": f"published >= {cutoff}",
            })
        for kw in keywords:
            sq2 = build_search_query(search_topic, categories, [kw])
            queries.append({
                "window": f"{days}d",
                "query_type": f"keyword_{kw.replace(' ', '_')}",
                "search_query": sq2,
                "url": build_query_url(sq2, max_results=max_results),
                "client_filter": f"published >= {cutoff}",
            })
    return queries


def main():
    p = argparse.ArgumentParser(
        description="Generate arXiv API query URLs from config.yaml or an ad-hoc topic")
    p.add_argument("--skill", help="config.yaml category_mappings key (e.g. ai-agents)")
    p.add_argument("--topic", help="Ad-hoc topic when --skill is not used")
    p.add_argument("--categories", nargs="+",
                   help="Override categories (default: from config, or cs.AI cs.CL cs.LG)")
    p.add_argument("--keywords", nargs="+", help="Override keywords (default: from config)")
    p.add_argument("--windows", nargs="+",
                   help="Override windows, e.g. 30d 90d 6m (default: from config time_window_months)")
    p.add_argument("--max-results", type=int, default=50)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    p.add_argument("--list-skills", action="store_true",
                   help="List available config.yaml category_mappings keys and exit")
    args = p.parse_args()

    if args.list_skills:
        for key, cfg in sorted(load_category_mappings(args.config).items()):
            cats = ",".join(cfg["categories"])
            print(f"{key}\t{cats}\t{cfg['time_window_months']}mo")
        return

    if not args.skill and not args.topic:
        p.error("one of --skill or --topic is required (or use --list-skills)")

    topic = args.topic
    categories = args.categories
    keywords = args.keywords
    windows = args.windows
    resolved_from = "cli"
    # A topic synthesised from a skill key is a label, not a search phrase.
    synthetic_topic = False

    if args.skill:
        mappings = load_category_mappings(args.config)
        if args.skill not in mappings:
            available = ", ".join(sorted(mappings))
            raise SystemExit(
                f"ERROR: unknown skill key {args.skill!r}.\nAvailable keys: {available}")
        cfg = mappings[args.skill]
        resolved_from = f"config.yaml:{args.skill}"
        if not topic:
            topic = args.skill.replace("-", " ")
            synthetic_topic = True
        categories = categories or cfg["categories"]
        keywords = keywords if keywords is not None else cfg["keywords"]
        if not windows and cfg["time_window_months"]:
            windows = [f"{cfg['time_window_months']}m"]

    categories = categories or ["cs.AI", "cs.CL", "cs.LG"]
    keywords = keywords if keywords is not None else []
    windows = windows or ["30d", "90d"]
    try:
        window_days = [parse_window(w) for w in windows]
    except argparse.ArgumentTypeError as exc:
        raise SystemExit(f"ERROR: {exc}")

    # Drop the broad topic query only when keywords can carry the search instead.
    # With neither, we would emit zero queries and exit 0 -- a silent no-op.
    include_topic_query = not synthetic_topic or not keywords
    if synthetic_topic and not keywords:
        print(
            f"WARNING: skill key {args.skill!r} has no config keywords; falling back to a "
            f'literal phrase search on abs:"{topic}", which is likely to return few or no '
            "results. Pass --topic or --keywords for a usable query.",
            file=sys.stderr,
        )

    out = {
        "source": "arxiv",
        "skill_key": args.skill,
        "resolved_from": resolved_from,
        "topic": topic,
        "categories": categories,
        "keywords": keywords,
        "generated_at": date.today().isoformat(),
        "windows": windows,
        "attribution": ATTRIBUTION,
        "rate_limit_note": (
            f"Enforced since Feb 2026: >={MIN_REQUEST_GAP_SECONDS}s between requests, "
            "single connection. On HTTP 429 back off 30s -> 60s -> 120s. "
            "See references/arxiv-api-guide.md#rate-limiting-enforced-as-of-2026."
        ),
        "topic_query_included": include_topic_query,
        "queries": build_queries(topic, categories, keywords, window_days,
                                 args.max_results, include_topic_query),
    }
    out["total_queries"] = len(out["queries"])
    out["estimated_min_runtime_seconds"] = out["total_queries"] * MIN_REQUEST_GAP_SECONDS

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
