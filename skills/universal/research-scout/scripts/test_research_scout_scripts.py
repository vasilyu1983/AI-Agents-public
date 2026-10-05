"""Gate and window contracts for the research-scout scripts. Stdlib only, no network.

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_arxiv_queries as gaq  # noqa: E402
import generate_hf_papers_queries as ghf  # noqa: E402
import generate_semantic_scholar_queries as gs2  # noqa: E402

AGG = HERE / "aggregate_research_ideas.py"
ASSET = HERE.parent / "assets" / "research-findings.tsv"

HEADER = ["source_url", "source_type", "source_context", "paper_id", "origin_id",
          "cluster_id", "title", "authors", "posted_at", "observed_at", "method_family",
          "idea_summary", "evidence_grade", "reproducibility", "lift", "applicability",
          "trap_tags", "shape_tags", "quote", "window", "claim_type"]


def row(**over):
    base = dict(source_url="https://arxiv.org/abs/0000.00001", source_type="arxiv",
                source_context="arxiv:cs.AI", paper_id="0000.00001", origin_id="study-a",
                cluster_id="m1", title="t", authors="a", posted_at="2026-01-01",
                observed_at="2026-01-02", method_family="f", idea_summary="an idea",
                evidence_grade="B", reproducibility="code+benchmarks", lift="low",
                applicability="4", trap_tags="", shape_tags="prompting-pattern",
                quote='"q"', window="30d", claim_type="relative-gain")
    base.update(over)
    return base


class AggregateGateTests(unittest.TestCase):
    def run_agg(self, rows, header=HEADER, extra=()):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "in.tsv", Path(d) / "out.tsv"
            with open(src, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=header, delimiter="\t", extrasaction="ignore")
                w.writeheader()
                for r in rows:
                    w.writerow(r)
            run = subprocess.run([sys.executable, str(AGG), str(src), "--output", str(out), *extra],
                                 capture_output=True, text=True)
            scored = []
            if out.exists():
                with open(out, newline="", encoding="utf-8") as f:
                    scored = list(csv.DictReader(f, delimiter="\t"))
            return run, {r["source_url"]: r for r in scored}

    # S1: corroboration counts independent origins, not channels.
    def test_same_origin_on_two_channels_is_not_corroborated(self):
        run, out = self.run_agg([
            row(),
            row(source_url="https://blog.example/post", source_type="curator_newsletter",
                paper_id="blog-1", origin_id="study-a"),
        ])
        self.assertEqual(run.returncode, 0, run.stderr)
        for r in out.values():
            self.assertEqual(r["corroboration"], "no")
            self.assertEqual(r["gate_status"], "validate")

    def test_two_independent_origins_promote(self):
        run, out = self.run_agg([
            row(),
            row(source_url="https://arxiv.org/abs/0000.00002", paper_id="0000.00002",
                origin_id="study-b"),
        ])
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(all(r["gate_status"] == "promote" for r in out.values()))
        self.assertTrue(all(r["origin_count"] == "2" for r in out.values()))

    def test_blank_cluster_id_never_corroborates(self):
        run, out = self.run_agg([
            row(cluster_id=""),
            row(source_url="https://arxiv.org/abs/0000.00002", paper_id="0000.00002",
                origin_id="study-b", cluster_id=""),
        ])
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(all(r["gate_status"] == "validate" for r in out.values()))

    # S2: two trap tags cap at validate even when neither is a cap trap.
    def test_two_non_cap_traps_cap_at_validate(self):
        traps = "cherry-picked-baselines,benchmark-overfit"
        run, out = self.run_agg([
            row(trap_tags=traps),
            row(source_url="https://arxiv.org/abs/0000.00002", paper_id="0000.00002",
                origin_id="study-b", trap_tags=traps),
        ])
        self.assertEqual(run.returncode, 0, run.stderr)
        for r in out.values():
            self.assertEqual(r["gate_status"], "validate")
            self.assertIn("2 traps", r["gate_reason"])

    # S3: the aggregator fails closed on a broken contract.
    def test_missing_required_columns_exit_1_without_output(self):
        run, out = self.run_agg([row()], header=["source_url", "title", "idea_summary"])
        self.assertEqual(run.returncode, 1)
        self.assertIn("Missing required columns", run.stderr)
        self.assertEqual(out, {})

    def test_blank_evidence_grade_is_not_defaulted(self):
        run, out = self.run_agg([row(evidence_grade="")])
        self.assertEqual(run.returncode, 1)
        self.assertIn("invalid evidence_grade", run.stderr)
        self.assertEqual(out, {})

    def test_out_of_range_applicability_rejected(self):
        run, _ = self.run_agg([row(applicability="99")])
        self.assertEqual(run.returncode, 1)
        self.assertIn("applicability must be an integer 1-5", run.stderr)

    def test_out_of_range_default_applicability_rejected(self):
        run, _ = self.run_agg([row()], extra=("--default-applicability", "9"))
        self.assertEqual(run.returncode, 2)

    # S4: tag columns are vocabulary-checked; the hard-kill gate keys on exact slugs.
    def test_numeric_or_misspelled_trap_tag_fails_closed(self):
        for bad in ("11", "proprietary_component"):
            with self.subTest(trap=bad):
                run, out = self.run_agg([row(trap_tags=bad)])
                self.assertEqual(run.returncode, 1, run.stdout)
                self.assertIn("unknown trap_tags", run.stderr)
                self.assertEqual(out, {})

    def test_hard_kill_slug_kills_even_when_corroborated(self):
        run, out = self.run_agg([
            row(trap_tags="proprietary-component"),
            row(source_url="https://arxiv.org/abs/0000.00002", paper_id="0000.00002",
                origin_id="study-b", trap_tags="proprietary-component"),
        ])
        self.assertEqual(run.returncode, 0, run.stderr)
        for r in out.values():
            self.assertEqual(r["gate_status"], "kill")
            self.assertIn("hard-kill trap", r["gate_reason"])

    def test_unknown_shape_tag_and_retired_source_type_rejected(self):
        run, _ = self.run_agg([row(shape_tags="prompting_pattern")])
        self.assertEqual(run.returncode, 1)
        self.assertIn("unknown shape_tags", run.stderr)
        run, _ = self.run_agg([row(source_type="papers_with_code")])
        self.assertEqual(run.returncode, 1)
        self.assertIn("invalid source_type", run.stderr)

    def test_shipped_asset_validates(self):
        with tempfile.TemporaryDirectory() as d:
            run = subprocess.run([sys.executable, str(AGG), str(ASSET), "--output",
                                  str(Path(d) / "o.tsv")], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)


class ArxivWindowTests(unittest.TestCase):
    # Z1: windows are applied server-side, so each window yields a different URL.
    def test_windows_are_server_side_and_distinct(self):
        today = date(2026, 9, 25)
        qs = gaq.build_queries("agent memory", ["cs.AI"], [30, 90, 365], 50, today=today)
        urls = {w: {q["url"] for q in qs if q["window"] == f"{w}d"} for w in (30, 90, 365)}
        self.assertTrue(urls[30].isdisjoint(urls[90]))
        self.assertTrue(urls[90].isdisjoint(urls[365]))
        self.assertTrue(all("submittedDate" in q["search_query"] for q in qs))
        self.assertIn("submittedDate:[202608260000 TO 202609252359]", qs[0]["search_query"])

    def test_pagination_plan_reads_total_results(self):
        q = gaq.build_queries("x", ["cs.AI"], [30], 50, max_pages=2, today=date(2026, 1, 31))[0]
        self.assertIn("opensearch:totalResults", q["pagination"]["stop_when"])
        self.assertTrue(q["pagination"]["if_total_exceeds"].startswith("100:"))

    def test_page_size_above_arxiv_cap_rejected(self):
        run = subprocess.run([sys.executable, str(HERE / "generate_arxiv_queries.py"),
                              "--topic", "x", "--max-results", "5000"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)


class BlogCuratorTests(unittest.TestCase):
    BLOG = HERE / "generate_blog_queries.py"

    def run_blog(self, *curators):
        return subprocess.run([sys.executable, str(self.BLOG), "--topic", "t", "--domains",
                               "--curators", *curators], capture_output=True, text=True)

    # Z6: an unknown curator key is a usage error, not a silent zero-query run.
    def test_unknown_curator_exits_2_and_lists_valid_keys(self):
        run = self.run_blog("interconnects", "bogus")
        self.assertEqual(run.returncode, 2, run.stdout)
        self.assertIn("bogus", run.stderr)
        self.assertIn("lilianweng", run.stderr)
        self.assertEqual(run.stdout, "")

    # Z7: every curator SKILL.md advertises has a generator entry.
    def test_advertised_curators_have_entries(self):
        run = self.run_blog("interconnects", "davis")
        self.assertEqual(run.returncode, 0, run.stderr)
        out = json.loads(run.stdout)
        urls = {q["url"] for q in out["queries"]}
        self.assertIn("https://www.interconnects.ai/", urls)
        self.assertIn("https://www.interconnects.ai/feed", urls)
        self.assertIn("https://dblalock.substack.com/", urls)
        self.assertIn("https://dblalock.substack.com/feed", urls)


class DeadSourceShimTests(unittest.TestCase):
    # Z8: the Papers with Code shim is fail-loud: replacement URLs plus a non-zero exit.
    def test_papers_with_code_shim_exits_3(self):
        run = subprocess.run([sys.executable, str(HERE / "generate_papers_with_code_queries.py"),
                              "--topic", "t"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 3, run.stderr)
        self.assertIn("DEAD SOURCE", run.stderr)
        out = json.loads(run.stdout)
        self.assertFalse(any("paperswithcode.com" in q["url"] for q in out["queries"]))


class SourceUrlTests(unittest.TestCase):
    # Z4: the S2 citations field is `intents` (plural); `intent` returns HTTP 400.
    def test_semantic_scholar_citations_template_uses_intents(self):
        cites = [q for q in gs2.build_queries("t", [365], 5, False)
                 if q["query_type"] == "citations_template"]
        self.assertEqual(len(cites), 1)
        fields = cites[0]["url"].split("fields=")[1].split("&")[0].split(",")
        self.assertIn("intents", fields)
        self.assertNotIn("intent", fields)

    # Z5: dead HF endpoints (papers.rss 404, ?date=trending 400) are never emitted.
    def test_hf_generator_emits_live_endpoints_only(self):
        urls = [q["url"] for q in ghf.build_queries("t", [2])]
        urls += [q["api_url"] for q in ghf.build_queries("t", [2]) if "api_url" in q]
        for dead in ("papers.rss", "date=trending"):
            self.assertFalse(any(dead in u for u in urls), dead)
        self.assertIn("https://huggingface.co/papers/trending", urls)
        self.assertTrue(any("/api/daily_papers?date=" in u for u in urls))
        self.assertTrue(any("/api/papers/search?q=" in u for u in urls))


if __name__ == "__main__":
    unittest.main()
