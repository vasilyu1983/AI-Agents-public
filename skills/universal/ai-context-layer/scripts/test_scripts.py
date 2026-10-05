#!/usr/bin/env python3
"""Regression tests for score_context_layer.py and check_sources.py.

Run from this directory: python3 -B -m pytest -q -p no:cacheprovider
or: python3 -m unittest test_scripts
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_sources  # noqa: E402
import score_context_layer as scorer  # noqa: E402

SCORECARD_MD = HERE.parent / "assets" / "eval" / "context-layer-scorecard.md"
SOURCES_JSON = HERE.parent / "data" / "sources.json"


def _write(tmp: Path, name: str, rows: list[dict] | str) -> Path:
    path = tmp / name
    if isinstance(rows, str):
        path.write_text(rows, encoding="utf-8")
    else:
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


def _full_rows(score: int = 2) -> list[dict]:
    return [
        {"category": cat, "item": item, "score": score}
        for cat, items in scorer.SCORECARD.items()
        for item in items
    ]


def _markdown_rows() -> list[dict]:
    """Rows written exactly as the markdown scorecard spells them (arrows, dashes, backticks)."""
    rows: list[dict] = []
    category = None
    for line in SCORECARD_MD.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            category = line[3:].strip()
            continue
        if category == "Interpretation" or category is None:
            continue
        if line.startswith("- "):
            rows.append({"category": category, "item": line[2:].strip(), "score": 1})
    return rows


class ScorerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_full_assessment_scores_and_exits_zero(self) -> None:
        path = _write(self.tmp, "full.jsonl", _full_rows(2))
        self.assertEqual(scorer.main([str(path)]), 0)

    def test_markdown_scorecard_wording_matches_every_item(self) -> None:
        # Old code required byte-identical strings, so rows copied from the markdown
        # scorecard ("->" vs "→", "<=" vs "≤") were silently dropped as MISSING.
        rows = _markdown_rows()
        expected = sum(len(items) for items in scorer.SCORECARD.values())
        self.assertEqual(len(rows), expected, "scorecard asset item count drifted from the script")
        scored, errors = scorer.score_rows(rows)
        self.assertEqual(errors, [])
        self.assertEqual(len(scored), expected)

    def test_unknown_item_fails_closed(self) -> None:
        rows = _full_rows(2)
        rows[0]["item"] = "This item does not exist"
        path = _write(self.tmp, "unknown.jsonl", rows)
        self.assertEqual(scorer.main([str(path)]), 1)

    def test_missing_items_fail_unless_allow_partial(self) -> None:
        rows = _full_rows(2)[:10]
        path = _write(self.tmp, "partial.jsonl", rows)
        self.assertEqual(scorer.main([str(path)]), 1)
        self.assertEqual(scorer.main([str(path), "--allow-partial"]), 0)

    def test_empty_and_invalid_input_exit_two(self) -> None:
        empty = _write(self.tmp, "empty.jsonl", "\n\n")
        self.assertEqual(scorer.main([str(empty)]), 2)
        broken = _write(self.tmp, "broken.jsonl", '{"category": "Memory"\n')
        self.assertEqual(scorer.main([str(broken)]), 2)
        self.assertEqual(scorer.main([str(self.tmp / "nope.jsonl")]), 2)

    def test_bad_score_values_rejected(self) -> None:
        rows = _full_rows(2)
        rows[3]["score"] = 3
        rows[4]["score"] = True  # bool is an int subclass; must not pass as 1
        path = _write(self.tmp, "bad.jsonl", rows)
        self.assertEqual(scorer.main([str(path)]), 1)

    def test_duplicate_item_rejected(self) -> None:
        rows = _full_rows(2) + [_full_rows(0)[0]]
        path = _write(self.tmp, "dup.jsonl", rows)
        self.assertEqual(scorer.main([str(path)]), 1)

    def test_bands_cover_max_score_without_gaps(self) -> None:
        max_score = sum(len(v) for v in scorer.SCORECARD.values()) * 2
        self.assertEqual(scorer.BANDS[-1][1], max_score)
        for (_, high, _), (low, _, _) in zip(scorer.BANDS, scorer.BANDS[1:]):
            self.assertEqual(low, high + 1)
        interp = SCORECARD_MD.read_text(encoding="utf-8")
        self.assertIn(f"Max score: {max_score}.", interp)


class CheckSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _valid(self) -> dict:
        return {
            "metadata": {
                "skill": "x", "last_updated": "2026-01-01", "total_sources": 1,
                "description": "d", "version": "1",
            },
            "categories": {"c": [{
                "name": "n", "url": "https://example.org/x", "type": "docs",
                "relevance": "r", "update_frequency": "u", "access": "open",
                "add_as_web_search": False,
            }]},
        }

    def test_real_catalog_validates(self) -> None:
        self.assertEqual(check_sources.main([str(SOURCES_JSON)]), 0)

    def test_default_path_is_skill_local(self) -> None:
        self.assertEqual(check_sources.main([]), 0)

    def test_empty_catalog_fails(self) -> None:
        doc = self._valid()
        doc["categories"] = {}
        doc["metadata"]["total_sources"] = 0
        path = _write(self.tmp, "empty.json", json.dumps(doc))
        self.assertEqual(check_sources.main([str(path)]), 1)

    def test_invalid_json_exits_two(self) -> None:
        path = _write(self.tmp, "bad.json", "{not json")
        self.assertEqual(check_sources.main([str(path)]), 2)
        lst = _write(self.tmp, "list.json", "[]")
        self.assertEqual(check_sources.main([str(lst)]), 1)

    def test_count_mismatch_and_http_fail(self) -> None:
        doc = self._valid()
        doc["metadata"]["total_sources"] = 2
        path = _write(self.tmp, "count.json", json.dumps(doc))
        self.assertEqual(check_sources.main([str(path)]), 1)
        doc = self._valid()
        doc["categories"]["c"][0]["url"] = "http://example.org/x"
        path = _write(self.tmp, "http.json", json.dumps(doc))
        self.assertEqual(check_sources.main([str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
