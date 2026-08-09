#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
GRAPH_BUILDER = SCRIPT_DIR / "build_skill_graph.py"


def write_skill(root: Path, name: str, metadata_block: str = "") -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    frontmatter = [
        "---",
        f"name: {name}",
        'description: "Creates a temporary skill fixture for graph tests. Use when validating graph relationships."',
    ]
    if metadata_block:
        frontmatter.extend(metadata_block.rstrip().splitlines())
    frontmatter.append("---")
    body = "\n".join(frontmatter) + f"""

# {name}

## Quick Reference

| Task | Action |
|------|--------|
| Validate graph | Run the graph builder |

## Workflow

1. Validate the graph.

## Navigation

- `SKILL.md`

## Fact-Checking

- Reconfirm graph edges before trust.
"""
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")


class BuildSkillGraphTests(unittest.TestCase):
    def run_builder(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GRAPH_BUILDER), str(root), *extra_args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_json_output_contains_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "router-startup")
            write_skill(
                root,
                "startup-idea-validation",
                """metadata:
  graph:
    routes_from: [router-startup]
    feeds: [startup-gtm-strategy]
""",
            )
            write_skill(root, "startup-gtm-strategy")

            result = self.run_builder(root, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["skills_with_graph_metadata"], 1)
            self.assertEqual(payload["edge_count"], 2)
            self.assertEqual(payload["errors"], [])

    def test_unknown_edge_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "startup-idea-validation",
                """metadata:
  graph:
    composes:
      - missing-skill
""",
            )

            result = self.run_builder(root, "--check")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing-skill", result.stdout)


if __name__ == "__main__":
    unittest.main()
