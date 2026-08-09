#!/usr/bin/env python3
"""DEAD SOURCE shim — Papers with Code was shut down by Meta in July 2025.

paperswithcode.com now 301-redirects to Hugging Face Trending Papers. This
script no longer emits paperswithcode.com URLs (they all redirect away).
Instead it fails loud and emits the live-replacement reproducibility-signal
URLs so callers and the workflow do not silently query a dead source.

Backward-compatible CLI (same flags as before) so SKILL.md examples still run.

Usage:
    python3 generate_papers_with_code_queries.py --topic "speculative decoding"
    python3 generate_papers_with_code_queries.py --task language-modelling
"""

import argparse
import json
import sys
from datetime import date
from urllib.parse import urlencode

ARCHIVE_URL = "https://github.com/paperswithcode/paperswithcode-data"
HF_PAPERS_SEARCH = "https://huggingface.co/papers?{params}"
HF_TRENDING = "https://huggingface.co/papers?date=trending"


def build_queries(topic: str | None, task_slugs: list[str], method_slugs: list[str]) -> list[dict]:
    queries = [{
        "query_type": "dead_source_archive",
        "url": ARCHIVE_URL,
        "note": "Papers with Code shut down July 2025. Frozen pre-2025 data only; "
                "not a current reproducibility signal.",
    }]
    if topic:
        queries.append({
            "query_type": "hf_papers_topic_search",
            "url": HF_PAPERS_SEARCH.format(params=urlencode({"q": topic})),
            "note": "Live replacement: HF Papers search. Cross-check linked "
                    "models/datasets/Spaces as the code signal.",
        })
    queries.append({
        "query_type": "hf_trending",
        "url": HF_TRENDING,
        "note": "Live replacement for the SOTA/cresting view.",
    })
    for slug in task_slugs + method_slugs:
        queries.append({
            "query_type": "github_repo_signal",
            "url": f"https://github.com/search?q={slug}&type=repositories&s=stars&o=desc",
            "note": f"Delegate deep repo inspection to research-git for '{slug}'. "
                    "Active maintenance + independent reimplementations = the "
                    "reproducibility signal that PwC used to provide.",
        })
    return queries


def main():
    p = argparse.ArgumentParser(description="DEAD: Papers with Code URL generator (now a fail-loud replacement shim)")
    p.add_argument("--topic", help="Free-text search topic")
    p.add_argument("--task", action="append", default=[],
                   help="Task slug. Repeatable. (Redirected to GitHub repo signal.)")
    p.add_argument("--method", action="append", default=[],
                   help="Method slug. Repeatable. (Redirected to GitHub repo signal.)")
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    args = p.parse_args()
    if not (args.topic or args.task or args.method):
        p.error("Provide at least one of --topic, --task, --method")
    sys.stderr.write(
        "WARNING: Papers with Code is a DEAD SOURCE (Meta shutdown, July 2025). "
        "Emitting live-replacement URLs (HF Papers + GitHub via research-git) "
        "instead of dead paperswithcode.com links. "
        "See references/papers-with-code-strategy.md.\n"
    )
    out = {
        "source": "papers_with_code_DEAD_replacement",
        "status": "dead_source_shutdown_2025-07",
        "topic": args.topic,
        "tasks": args.task,
        "methods": args.method,
        "generated_at": date.today().isoformat(),
        "queries": build_queries(args.topic, args.task, args.method),
    }
    out["total_queries"] = len(out["queries"])
    if args.format == "json":
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        lines = ["query_type\turl\tnote"]
        for q in out["queries"]:
            lines.append(f'{q["query_type"]}\t{q["url"]}\t{q.get("note", "")}')
        sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
