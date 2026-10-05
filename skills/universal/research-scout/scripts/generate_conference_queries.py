#!/usr/bin/env python3
"""Generate conference-proceedings URLs by venue and year.

Each venue has its own URL pattern; this script emits seed URLs that the
scout walks client-side. Full venue map in references/conference-proceedings-strategy.md.

Usage:
    python3 generate_conference_queries.py --conference neurips --year 2025 --topic "agents"
    python3 generate_conference_queries.py --conference acl --year 2025
"""

import argparse
import json
import sys
from datetime import date

VENUES = {
    "neurips": {
        "name": "NeurIPS",
        "proceedings": "https://proceedings.neurips.cc/paper_files/paper/{year}",
        "openreview": "https://openreview.net/group?id=NeurIPS.cc/{year}/Conference",
    },
    "icml": {
        "name": "ICML",
        "proceedings": "https://proceedings.mlr.press/",
        "note": "ICML uses PMLR; locate the year's volume on the index page.",
    },
    "iclr": {
        "name": "ICLR",
        "openreview": "https://openreview.net/group?id=ICLR.cc/{year}/Conference",
    },
    "acl": {
        "name": "ACL",
        "anthology": "https://aclanthology.org/events/acl-{year}/",
    },
    "emnlp": {
        "name": "EMNLP",
        "anthology": "https://aclanthology.org/events/emnlp-{year}/",
    },
    "naacl": {
        "name": "NAACL",
        "anthology": "https://aclanthology.org/events/naacl-{year}/",
    },
    "kdd": {
        "name": "KDD",
        "acm": "https://dl.acm.org/doi/proceedings/10.1145/{kdd_doi_year}",
        "note": "KDD DOI year may differ from event year; confirm on dl.acm.org.",
    },
    "icse": {
        "name": "ICSE",
        "acm": "https://dl.acm.org/conference/icse",
    },
    "fse": {
        "name": "FSE",
        "acm": "https://dl.acm.org/conference/fse",
    },
    "cvpr": {
        "name": "CVPR",
        "cvf": "https://openaccess.thecvf.com/CVPR{year}",
    },
    "iccv": {
        "name": "ICCV",
        "cvf": "https://openaccess.thecvf.com/ICCV{year}",
    },
    "eccv": {
        "name": "ECCV",
        "cvf": "https://www.ecva.net/papers.php",
        "note": "ECCV proceedings hosted on ecva.net; year filter applied client-side.",
    },
}


def build_queries(conference: str, year: int, topic: str | None) -> list[dict]:
    spec = VENUES[conference]
    queries = []
    for key, val in spec.items():
        if key in ("name", "note"):
            continue
        url = val.format(year=year, kdd_doi_year=year) if "{" in val else val
        queries.append({
            "query_type": key,
            "venue": spec["name"],
            "year": year,
            "url": url,
            "client_filter": f'title or abstract contains "{topic}"' if topic else None,
        })
    if "note" in spec:
        queries.append({"query_type": "note", "venue": spec["name"], "url": "", "note": spec["note"]})
    return queries


def main():
    p = argparse.ArgumentParser(description="Generate conference proceedings URLs")
    p.add_argument("--conference", required=True, choices=sorted(VENUES.keys()))
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--topic", help="Optional topic for client-side filter")
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    args = p.parse_args()
    out = {
        "source": "conference",
        "conference": args.conference,
        "year": args.year,
        "topic": args.topic,
        "generated_at": date.today().isoformat(),
        "queries": build_queries(args.conference, args.year, args.topic),
    }
    out["total_queries"] = len(out["queries"])
    if args.format == "json":
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        lines = ["venue\tquery_type\turl"]
        for q in out["queries"]:
            lines.append(f'{q.get("venue", "")}\t{q["query_type"]}\t{q["url"]}')
        sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
