#!/usr/bin/env python3
"""Tests for the vendored design-database scripts and contrast_check.py.

Run from this directory: python3 -m unittest test_scripts -v
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import contrast_check  # noqa: E402
from core import DATA_DIR, search  # noqa: E402
from design_system import DesignSystemGenerator, generate_design_system  # noqa: E402

# Text-on-surface pairs in data/colors.csv (header names). Muted Foreground is
# secondary text and is used on both the muted surface and the page background.
PALETTE_TEXT_PAIRS = [
    ("On Primary", "Primary"),
    ("On Secondary", "Secondary"),
    ("On Accent", "Accent"),
    ("Foreground", "Background"),
    ("Card Foreground", "Card"),
    ("Muted Foreground", "Muted"),
    ("Muted Foreground", "Background"),
    ("On Destructive", "Destructive"),
]


def run(script: str, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script), *args],
        input=stdin, capture_output=True, text=True, cwd=SCRIPT_DIR,
    )


class ContrastRatioTests(unittest.TestCase):
    def test_black_on_white_is_21(self):
        self.assertAlmostEqual(contrast_check.contrast_ratio("#000", "#fff"), 21.0, places=6)

    def test_short_hex_expands(self):
        self.assertAlmostEqual(contrast_check.contrast_ratio("#000", "#fff"),
                               contrast_check.contrast_ratio("#000000", "#FFFFFF"))

    def test_bad_hex_is_value_error_with_message(self):
        with self.assertRaises(ValueError) as cm:
            contrast_check.contrast_ratio("#GGGGGG", "#fff")
        self.assertIn("bad hex color", str(cm.exception))

    def test_alpha_foreground_is_composited_over_background(self):
        # 50% black over white renders as mid grey: ratio must sit well
        # below opaque black's 21:1 and above 1:1.
        ratio = contrast_check.contrast_ratio("#00000080", "#FFFFFF")
        self.assertLess(ratio, 6.0)
        self.assertGreater(ratio, 3.0)
        # Fully opaque alpha equals the 6-digit form.
        self.assertAlmostEqual(contrast_check.contrast_ratio("#000000FF", "#FFFFFF"), 21.0, places=6)

    def test_alpha_background_is_refused(self):
        with self.assertRaises(ValueError) as cm:
            contrast_check.contrast_ratio("#000000", "#FFFFFF80")
        self.assertIn("translucent background", str(cm.exception))


class ContrastCliTests(unittest.TestCase):
    def test_pair_pass_exits_0(self):
        r = run("contrast_check.py", "#000000", "#FFFFFF")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("21.00:1", r.stdout)

    def test_pair_fail_exits_1(self):
        r = run("contrast_check.py", "#D97706", "#F8FAFC")
        self.assertEqual(r.returncode, 1)

    def test_bad_hex_is_usage_error_not_traceback(self):
        r = run("contrast_check.py", "#GGG", "#fff")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("bad hex color", r.stderr)

    def test_stdin_empty_input_does_not_pass(self):
        r = run("contrast_check.py", "--stdin", stdin="")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no colour pairs checked", r.stderr)

    def test_stdin_malformed_line_does_not_pass(self):
        r = run("contrast_check.py", "--stdin", stdin="garbage\n#fff\n")
        self.assertEqual(r.returncode, 2)
        self.assertIn("line 1", r.stderr)

    def test_stdin_blank_lines_are_ignored_but_pairs_checked(self):
        r = run("contrast_check.py", "--stdin", stdin="\n#000 #fff label here\n\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("[label here]", r.stdout)

    def test_stdin_bad_hex_is_usage_error(self):
        r = run("contrast_check.py", "--stdin", stdin="#ZZZ #fff\n")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)

    def test_cross_product_reports_every_pair(self):
        r = run("contrast_check.py", "--tokens", "#000,#fff", "--surfaces", "#fff")
        self.assertEqual(r.returncode, 1)  # white on white fails
        self.assertEqual(r.stdout.count(":1 "), 2)


class SearchTests(unittest.TestCase):
    def test_core_search_returns_results(self):
        result = search("fintech dashboard", domain="style", max_results=2)
        self.assertNotIn("error", result)
        self.assertGreater(result["count"], 0)
        self.assertLessEqual(result["count"], 2)

    def test_cli_empty_query_is_rejected(self):
        for q in ("", "   "):
            r = run("search.py", q, "--design-system")
            self.assertEqual(r.returncode, 2, q)
            self.assertIn("empty query", r.stderr)

    def test_cli_query_exits_0(self):
        r = run("search.py", "saas dashboard", "-n", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Search Results", r.stdout)


class DesignSystemTests(unittest.TestCase):
    def test_generate_without_persist_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            out = generate_design_system("SaaS dashboard", "Proj", "markdown", output_dir=td)
            self.assertIn("Proj", out)
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_persist_writes_only_under_output_dir(self):
        with tempfile.TemporaryDirectory() as td:
            generate_design_system("SaaS dashboard", "My Project", "designmd",
                                   persist=True, page="dashboard", output_dir=td)
            base = Path(td)
            self.assertTrue((base / "design-system" / "my-project" / "MASTER.md").is_file())
            self.assertTrue((base / "design-system" / "my-project" / "pages" / "dashboard.md").is_file())
            self.assertTrue((base / "DESIGN.md").is_file())
            self.assertFalse((SCRIPT_DIR / "DESIGN.md").exists())

    def test_trust_finance_dashboard_is_light_first(self):
        # A trust-oriented finance dashboard must not be steered into a style
        # whose light mode is "not-recommended"; dark stays an option.
        ds = DesignSystemGenerator().generate("fintech dashboard trustworthy")
        self.assertNotEqual(ds["style"]["light_mode"], "not-recommended", ds["style"]["name"])
        self.assertEqual(ds["style"]["dark_mode"], "supported")
        self.assertNotIn("Light mode default", ds["anti_patterns"])


class PaletteContrastTests(unittest.TestCase):
    def test_every_palette_text_pair_passes_aa(self):
        import csv
        failures = []
        with open(DATA_DIR / "colors.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                for fg, bg in PALETTE_TEXT_PAIRS:
                    ratio = contrast_check.contrast_ratio(row[fg], row[bg])
                    if ratio < 4.5:
                        failures.append(f"row {row['No']} {row['Product Type']}: "
                                        f"{fg} {row[fg]} on {bg} {row[bg]} = {ratio:.2f}:1")
        self.assertEqual(failures, [], "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
