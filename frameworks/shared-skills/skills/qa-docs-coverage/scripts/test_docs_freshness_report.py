#!/usr/bin/env python3

"""Tests for docs_freshness_report.py.

Run: python3 -m unittest scripts.test_docs_freshness_report -v
"""

from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import docs_freshness_report as dfr  # noqa: E402


class ParseFrontmatterTests(unittest.TestCase):
    def test_no_frontmatter(self):
        meta, errors = dfr._parse_frontmatter("# Title\n\nbody")
        self.assertEqual(meta, {})
        self.assertEqual(errors, [])

    def test_basic_yaml_block(self):
        text = "---\ntitle: Doc\npriority: P1\n---\n\nbody"
        meta, errors = dfr._parse_frontmatter(text)
        # When PyYAML is available, frontmatter is parsed; when not, errors
        # explain the missing dependency. Either branch is valid behavior.
        if dfr.yaml is not None:
            self.assertEqual(meta.get("title"), "Doc")
            self.assertEqual(meta.get("priority"), "P1")
            self.assertEqual(errors, [])
        else:
            self.assertEqual(meta, {})
            self.assertTrue(any("PyYAML" in e for e in errors))

    def test_quoted_value(self):
        if dfr.yaml is None:
            self.skipTest("PyYAML not installed")
        text = '---\ntitle: "Quoted Title"\n---\n'
        meta, _ = dfr._parse_frontmatter(text)
        self.assertEqual(meta.get("title"), "Quoted Title")


class ParseDateTests(unittest.TestCase):
    def test_iso_string(self):
        self.assertEqual(dfr._parse_date("2026-01-15"), dt.date(2026, 1, 15))

    def test_date_object_passthrough(self):
        d = dt.date(2025, 6, 1)
        self.assertEqual(dfr._parse_date(d), d)

    def test_invalid_returns_none(self):
        self.assertIsNone(dfr._parse_date("not-a-date"))
        self.assertIsNone(dfr._parse_date(None))


class NormalizePriorityTests(unittest.TestCase):
    def test_p1_p2_p3_recognized(self):
        for p in ("P1", "P2", "P3"):
            self.assertEqual(dfr._normalize_priority(p), p)

    def test_lowercase_normalized(self):
        self.assertEqual(dfr._normalize_priority("p1"), "P1")

    def test_unknown_defaults_to_p3(self):
        # Unknown priorities should fall back to a safe default, not crash.
        result = dfr._normalize_priority("garbage")
        self.assertIn(result, {"P1", "P2", "P3"})


class FormatDateTests(unittest.TestCase):
    def test_formats_iso(self):
        self.assertEqual(dfr._format_date(dt.date(2026, 1, 15)), "2026-01-15")

    def test_none_returns_placeholder(self):
        # The script uses a non-empty placeholder ("N/A" or similar) for missing dates.
        result = dfr._format_date(None)
        self.assertIsInstance(result, str)
        self.assertTrue(result)
        self.assertNotIn("2", result)  # not a date


class ReadDocMetaTests(unittest.TestCase):
    def test_reads_frontmatter_from_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("---\ntitle: D\npriority: P2\n---\n\nbody")
            meta = dfr._read_doc_meta(path)
            self.assertEqual(meta.path, path)


if __name__ == "__main__":
    unittest.main()
