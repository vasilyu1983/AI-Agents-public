#!/usr/bin/env python3
"""Regression checks for malformed relationship parts in PPTX inspection."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from pptx_ooxml_inspect import main


REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


class PptxRelationshipValidationTests(unittest.TestCase):
    def test_malformed_relationships_fail_without_success_payload(self) -> None:
        malformed_parts = {
            "empty": b"",
            "wrong_root": b"<notRelationships />",
            "missing_target": (
                f'<Relationships xmlns="{REL_NS}">'
                '<Relationship Id="rId1" Type="slide" />'
                "</Relationships>"
            ).encode(),
        }

        for name, relationships in malformed_parts.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp_dir:
                deck = Path(temp_dir) / "broken.pptx"
                with zipfile.ZipFile(deck, "w") as package:
                    package.writestr("ppt/presentation.xml", b"<presentation />")
                    package.writestr("ppt/_rels/presentation.xml.rels", relationships)

                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    status = main([str(deck), "--json"])

                self.assertEqual(status, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn("relationship", stderr.getvalue().lower())

    def test_broken_target_gate_and_report_only_remain_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            deck = Path(temp_dir) / "broken-target.pptx"
            relationships = (
                f'<Relationships xmlns="{REL_NS}">'
                '<Relationship Id="rId1" Type="slide" Target="slides/missing.xml" />'
                "</Relationships>"
            )
            with zipfile.ZipFile(deck, "w") as package:
                package.writestr("ppt/presentation.xml", b"<presentation />")
                package.writestr("ppt/_rels/presentation.xml.rels", relationships)

            for options, expected in (([], 1), (["--report-only"], 0)):
                with self.subTest(options=options):
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        status = main([str(deck), "--json", *options])
                    self.assertEqual(status, expected)
                    self.assertIn('"broken_internal_targets": 1', stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
