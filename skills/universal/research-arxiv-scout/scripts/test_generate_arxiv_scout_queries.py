"""Window and pagination contract for the arXiv scout query generator. No network.

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_arxiv_scout_queries as g  # noqa: E402

SCRIPT = HERE / "generate_arxiv_scout_queries.py"


class WindowTests(unittest.TestCase):
    # Z1: a 30d and a 365d scan must not emit the same URLs.
    def test_windows_are_server_side_and_distinct(self):
        qs = g.build_queries("agent memory", ["cs.AI"], ["memory"], [30, 365], 50,
                             today=date(2026, 9, 25))
        by_window = {w: {q["url"] for q in qs if q["window"] == w} for w in ("30d", "365d")}
        self.assertTrue(by_window["30d"].isdisjoint(by_window["365d"]))
        self.assertTrue(all("submittedDate:[" in q["search_query"] for q in qs))
        self.assertIn("20250925", qs[-1]["search_query"])

    # X5: every query tells the fetcher to read totalResults and report coverage.
    def test_pagination_plan_requires_coverage(self):
        q = g.build_queries("x", ["cs.AI"], [], [30], 50, today=date(2026, 9, 25))[0]
        plan = q["pagination"]
        self.assertIn("opensearch:totalResults", plan["coverage"])
        self.assertIn("narrow the query", plan["if_total_exceeds"])
        # X6: field scans use the primary category.
        self.assertIn("arxiv:primary_category", plan["field_filter"])

    def test_skill_key_output_has_windows(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--skill", "ai-agents",
                              "--windows", "30d", "365d"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        out = json.loads(run.stdout)
        windows = {q["window_submitted"] for q in out["queries"]}
        self.assertEqual(len(windows), 2)

    def test_page_size_above_arxiv_cap_rejected(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--topic", "x",
                              "--max-results", "5000"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("--max-results must be 1-2000", run.stderr)

    def test_missing_mapping_field_fails_instead_of_emitting_fallback_query(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.yaml"
            config.write_text(
                'category_mappings:\n  sample:\n    categories: ["cs.AI"]\n'
                '    time_window_months: 6\n', encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--skill", "sample", "--config", str(config)],
                capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("keywords", run.stderr)

    def test_zero_day_window_rejected(self):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--topic", "agents", "--windows", "0d"],
            capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("Invalid window", run.stderr)

    # A malformed category matches nothing, so the scan would look empty instead of failing.
    def test_malformed_category_rejected(self):
        for bad in ("cS.AI", "not.acat", "cs.", "cs.ai"):
            with self.subTest(category=bad):
                run = subprocess.run(
                    [sys.executable, str(SCRIPT), "--topic", "agents", "--categories", bad],
                    capture_output=True, text=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("well-formed arXiv category", run.stderr)

    def test_configured_and_multi_archive_categories_accepted(self):
        for good in ("cs.AI", "stat.ML", "q-bio.NC", "cond-mat.mes-hall", "quant-ph"):
            g.check_category(good)
        for cfg in g.load_category_mappings(g.DEFAULT_CONFIG).values():
            for cat in cfg["categories"]:
                g.check_category(cat)


if __name__ == "__main__":
    unittest.main()
