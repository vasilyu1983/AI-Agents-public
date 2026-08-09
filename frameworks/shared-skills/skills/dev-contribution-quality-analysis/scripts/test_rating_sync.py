#!/usr/bin/env python3
"""
Sync test: assert that compute-code-rating.py is byte-identical across both copies.

The D2 headline rating (`code_loc x (1 + a*dCC + b*novelty)`) must produce identical
results from the same CSV input in both skills. The copies exist because the counterpart is a project-scoped skill and may not
be cross-linked from a domain skill; vendoring the script is what keeps the two
legal and equal.

The counterpart lives outside this skill and is not present in every checkout
(it is excluded from public distributions). Its path is discovered at runtime,
and the cross-copy comparison is skipped when it is absent.

Run as:
  python3 scripts/test_rating_sync.py
  python3 -m pytest scripts/test_rating_sync.py

Fails loud with a unified diff if either copy drifts from the other.
"""
from __future__ import annotations

import difflib
import sys
import unittest
from pathlib import Path

# Resolve paths relative to this file so the test is runnable from any cwd.
_SKILLS_ROOT = Path(__file__).resolve().parent.parent.parent  # .../skills/
_COPIES = {
    "dev-contribution-quality-analysis": (
        _SKILLS_ROOT / "dev-contribution-quality-analysis" / "scripts" / "compute-code-rating.py"
    ),
}

# Project-scoped counterparts that vendor the same script. Absent in public
# checkouts; discovered by glob so no confidential skill name is hardcoded.
for _candidate in sorted(_SKILLS_ROOT.glob("*/scripts/compute-code-rating.py")):
    _name = _candidate.parent.parent.name
    if _name != "dev-contribution-quality-analysis":
        _COPIES[_name] = _candidate


class TestRatingSync(unittest.TestCase):
    def test_all_copies_exist(self) -> None:
        for skill, path in _COPIES.items():
            self.assertTrue(
                path.exists(),
                f"compute-code-rating.py missing in {skill}: expected {path}",
            )

    def test_copies_are_byte_identical(self) -> None:
        if len(_COPIES) < 2:
            self.skipTest(
                "only one copy present (project-scoped counterpart not in this checkout)"
            )
        texts = {}
        for skill, path in _COPIES.items():
            if path.exists():
                texts[skill] = path.read_text(encoding="utf-8")

        skills = list(texts.keys())
        reference_skill = skills[0]
        reference_text = texts[reference_skill]
        reference_lines = reference_text.splitlines(keepends=True)

        all_identical = True
        for other_skill in skills[1:]:
            other_text = texts[other_skill]
            if other_text != reference_text:
                all_identical = False
                other_lines = other_text.splitlines(keepends=True)
                diff = "".join(
                    difflib.unified_diff(
                        reference_lines,
                        other_lines,
                        fromfile=f"{reference_skill}/scripts/compute-code-rating.py",
                        tofile=f"{other_skill}/scripts/compute-code-rating.py",
                    )
                )
                print(
                    f"\nDRIFT DETECTED between {reference_skill} and {other_skill}:\n{diff}",
                    file=sys.stderr,
                )

        self.assertTrue(
            all_identical,
            "compute-code-rating.py copies have drifted — see diff above. "
            "Edit both copies together and re-run this test.",
        )


if __name__ == "__main__":
    unittest.main()
