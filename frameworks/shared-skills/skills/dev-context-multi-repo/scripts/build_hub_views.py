#!/usr/bin/env python3
"""Generate markdown catalog pages from JSON repo profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render_profile(data: dict) -> str:
    return f"""# {data['repo_name']}

## Snapshot

- Repo: `{data['repo_name']}`
- Status: `{data['status']}`
- Kind: `{data['repo_kind']}`
- Languages: {", ".join(data.get('languages', [])) or "unknown"}
- Frameworks: {", ".join(data.get('frameworks', [])) or "unknown"}
- Architecture: `{data['architecture_style']}`
- Confidence: `{data['confidence_score']}`

## Purpose

{data['summary']}

## Interfaces

- {", ".join(data.get('interfaces_exposed', [])) or "none detected"}

## Integrations

- {", ".join(data.get('integrates_with', [])) or "none detected"}

## Risks

- {", ".join(data.get('risk_flags', [])) or "none"}

## Evidence

{chr(10).join(f"- `{item['path']}`: {item.get('reason', 'evidence')}" for item in data.get('evidence', []))}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles_dir")
    parser.add_argument("--out", help="Output directory for markdown catalog pages")
    args = parser.parse_args()

    profiles_dir = Path(args.profiles_dir)
    out_dir = Path(args.out) if args.out else profiles_dir.parent / "catalog"
    out_dir.mkdir(parents=True, exist_ok=True)

    for profile_path in sorted(profiles_dir.glob("*.json")):
        data = json.loads(profile_path.read_text())
        slug = profile_path.stem
        (out_dir / f"{slug}.md").write_text(render_profile(data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
