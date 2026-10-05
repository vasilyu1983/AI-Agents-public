#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "generate_team_member_matrix.py"
spec = importlib.util.spec_from_file_location("team_member_matrix", MODULE_PATH)
assert spec and spec.loader
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)


class TeamMemberMatrixTests(unittest.TestCase):
    def test_catalog_separates_core_candidates_and_uncomposed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = root / "members"
            teams = root / "teams"
            members.mkdir()
            for name in ("core", "candidate", "unused"):
                (members / f"{name}.md").write_text(f"# {name}\n", encoding="utf-8")
            team_dir = teams / "example"
            team_dir.mkdir(parents=True)
            (team_dir / "team.yaml").write_text(
                "---\nname: example\nfamily: test\nmembers:\n  - core\n"
                "expansion_gate:\n  candidate_specialists:\n  - candidate\ninstall: opt-in\n",
                encoding="utf-8",
            )

            canonical, catalog = matrix.load_catalog(members, teams)
            rendered = matrix.render_matrix(canonical, catalog)

        self.assertIn("| Candidate-only members | 1 |", rendered)
        self.assertIn("| Uncomposed members | 1 |", rendered)
        self.assertIn("| `example` | opt-in | `core` | `candidate` |", rendered)

    def test_unknown_member_fails_catalog_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            members = root / "members"
            teams = root / "teams" / "example"
            members.mkdir()
            teams.mkdir(parents=True)
            (members / "known.md").write_text("# known\n", encoding="utf-8")
            (teams / "team.yaml").write_text(
                "name: example\nfamily: test\nmembers:\n  - missing\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unknown members: missing"):
                matrix.load_catalog(members, root / "teams")


if __name__ == "__main__":
    unittest.main()
