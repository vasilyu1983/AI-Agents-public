#!/usr/bin/env python3
"""Generate research-blog and curator-newsletter URLs for topic scanning.

Emits per-domain site search URLs (Google site: queries) plus RSS feed
URLs where known. The scout walks both client-side.

Usage:
    python3 generate_blog_queries.py --topic "agent tool use" \\
        --domains anthropic.com openai.com deepmind.google research.google
    python3 generate_blog_queries.py --topic "RAG eval" --curators lilianweng raschka eugeneyan
"""

import argparse
import json
import sys
from datetime import date, timedelta
from urllib.parse import quote_plus

INDUSTRY_DOMAINS = {
    "anthropic.com": "Anthropic Research",
    "openai.com": "OpenAI Research",
    "deepmind.google": "Google DeepMind",
    "research.google": "Google Research",
    "ai.meta.com": "Meta AI Research",
    "microsoft.com/en-us/research": "Microsoft Research",
    "machinelearning.apple.com": "Apple ML Research",
    "huggingface.co/blog": "Hugging Face Blog",
}

CURATORS = {
    "lilianweng": {"name": "Lilian Weng", "url": "https://lilianweng.github.io/"},
    "raschka": {"name": "Sebastian Raschka", "url": "https://magazine.sebastianraschka.com/",
                "rss": "https://magazine.sebastianraschka.com/feed"},
    "eugeneyan": {"name": "Eugene Yan", "url": "https://eugeneyan.com/",
                  "rss": "https://eugeneyan.com/rss/"},
    "latentspace": {"name": "Latent Space", "url": "https://www.latent.space/",
                    "rss": "https://www.latent.space/feed"},
    "simonw": {"name": "Simon Willison", "url": "https://simonwillison.net/",
               "rss": "https://simonwillison.net/atom/everything/"},
    "thebatch": {"name": "The Batch", "url": "https://www.deeplearning.ai/the-batch/"},
    "importai": {"name": "Import AI", "url": "https://jack-clark.net/",
                 "rss": "https://jack-clark.net/feed/"},
    "chiphuyen": {"name": "Chip Huyen", "url": "https://huyenchip.com/"},
    "karpathy": {"name": "Andrej Karpathy", "url": "https://karpathy.github.io/"},
}


def parse_window(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("d") and s[:-1].isdigit():
        return int(s[:-1])
    raise argparse.ArgumentTypeError(f"Invalid window format: {s!r}")


def build_queries(topic: str, domains: list[str], curators: list[str], windows: list[int]) -> list[dict]:
    queries = []
    for days in windows:
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        for d in domains:
            label = INDUSTRY_DOMAINS.get(d, d)
            q = f'site:{d} {topic} after:{cutoff}'
            queries.append({
                "window": f"{days}d",
                "query_type": "industry_blog_google",
                "source_label": label,
                "domain": d,
                "url": f"https://www.google.com/search?q={quote_plus(q)}",
            })
    for key in curators:
        spec = CURATORS.get(key)
        if not spec:
            continue
        queries.append({
            "window": "all",
            "query_type": "curator_homepage",
            "source_label": spec["name"],
            "url": spec["url"],
            "client_filter": f'title or summary contains "{topic}"',
        })
        if "rss" in spec:
            queries.append({
                "window": "all",
                "query_type": "curator_rss",
                "source_label": spec["name"],
                "url": spec["rss"],
                "client_filter": f'title or summary contains "{topic}"',
            })
    return queries


def main():
    p = argparse.ArgumentParser(description="Generate blog and newsletter URLs")
    p.add_argument("--topic", required=True)
    p.add_argument("--domains", nargs="*", default=list(INDUSTRY_DOMAINS.keys()))
    p.add_argument("--curators", nargs="*", default=list(CURATORS.keys()))
    p.add_argument("--windows", nargs="+", default=["30d", "90d"])
    p.add_argument("--format", choices=["json", "tsv"], default="json")
    args = p.parse_args()
    windows = [parse_window(w) for w in args.windows]
    out = {
        "source": "blogs_and_curators",
        "topic": args.topic,
        "domains": args.domains,
        "curators": args.curators,
        "generated_at": date.today().isoformat(),
        "windows": args.windows,
        "queries": build_queries(args.topic, args.domains, args.curators, windows),
    }
    out["total_queries"] = len(out["queries"])
    if args.format == "json":
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        lines = ["window\tquery_type\tsource_label\turl"]
        for q in out["queries"]:
            lines.append(
                f'{q.get("window", "")}\t{q["query_type"]}\t{q.get("source_label", "")}\t{q["url"]}'
            )
        sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
