#!/usr/bin/env python3
"""Deterministic regression tests for fail-closed Codex usage attribution."""

import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


MODULE = Path(__file__).with_name("codex-usage.py")
SPEC = importlib.util.spec_from_file_location("codex_usage", MODULE)
codex_usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(codex_usage)
# Arithmetic tests own their rates. They are deliberately fake (fixture model IDs)
# so no test can pass by matching a real published price.
SOL_MODEL = "fixture-sol"
TERRA_MODEL = "fixture-terra"
FIXTURE_PRICING_FILE = {
    "source_url": "https://example.invalid/pricing",
    "retrieved_at": "2000-01-01",
    "models": {
        "fixture/fixture": {"input_per_1m": 99.0, "output_per_1m": 99.0, "cache_read_per_1m": 99.0},
        "fixture/" + SOL_MODEL: {"input_per_1m": 5.0, "output_per_1m": 30.0,
                                 "cache_read_per_1m": 0.5, "cache_write_per_1m": 6.25,
                                 "source_url": "https://example.invalid/pricing#fixture-sol"},
        TERRA_MODEL: {"input_per_1m": 2.0, "output_per_1m": 12.0, "cache_read_per_1m": 0.2},
        "fixture-nocache": {"input_per_1m": 1.0, "output_per_1m": 1.0, "cache_read_per_1m": None},
        "<model-id>": {"input_per_1m": None, "output_per_1m": None},
    },
}
REAL_LOOKING_IDS = ("gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5", "o3", "gpt-4.1")


def usage(inp, out=0, cached=0, cache_write=0):
    return {"input_tokens": inp, "output_tokens": out,
            "cached_input_tokens": cached, "cache_write_input_tokens": cache_write,
            "reasoning_output_tokens": 0, "total_tokens": inp + out}


def context(model, **logged):
    """A turn_context with the key set real Codex logs carry (synthetic values).

    Real logs never carry service_tier or context_pricing_class; pass them as
    keyword arguments only to test a log that does.
    """
    return {"type": "turn_context", "payload": {
        "model": model, "effort": "medium", "approval_policy": "on-request",
        "cwd": "/synthetic/project", "sandbox_policy": {"type": "workspace-write"},
        **logged}}


def settings(**thread_settings):
    """A thread_settings_applied event (synthetic values). Codex writes service_tier
    here, and only when a tier is set; turn_context never carries it."""
    return {"timestamp": "2026-08-15T00:00:00Z", "type": "event_msg", "ordinal": 1, "payload": {
        "type": "thread_settings_applied", "thread_settings": {
            "model": SOL_MODEL, "cwd": "/synthetic/project", **thread_settings}}}


def token(last=None, total=None):
    return {"timestamp": "2026-08-15T00:00:00Z", "type": "event_msg", "payload": {
        "type": "token_count", "info": {
            "last_token_usage": last, "total_token_usage": total}}}


class CodexUsageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.rates = Path(tmp.name) / "rates.json"
        self.rates.write_text(json.dumps(FIXTURE_PRICING_FILE))
        table, retrieved = codex_usage.load_pricing_file(self.rates)
        for name, value in (("PRICING", table), ("PRICING_FILE", self.rates),
                            ("PRICING_RETRIEVED_AT", retrieved)):
            patch = mock.patch.object(codex_usage, name, value)
            patch.start()
            self.addCleanup(patch.stop)

    def parse(self, records):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in records))
            return list(codex_usage.parse_session_events(str(path)))

    def test_exact_lookup_does_not_match_shorter_model_prefix(self):
        result = codex_usage.attribute_cost(SOL_MODEL, 1_000_000, 0, 0,
                                            service_tier="standard",
                                            context_pricing_class="standard")
        self.assertEqual(result["costStatus"], "exact")
        self.assertEqual(result["costUSD"], 5.0)
        self.assertTrue(result["pricingSha256"])
        self.assertTrue(result["rateSource"].endswith(SOL_MODEL))
        self.assertEqual(result["pricingRetrievedAt"], "2000-01-01")

    def test_longer_unlisted_model_id_cannot_borrow_known_rate(self):
        result = codex_usage.attribute_cost(SOL_MODEL + "-unlisted", 1_000_000, 0, 0,
                                           service_tier="standard",
                                           context_pricing_class="standard")
        self.assertEqual(result["unpricedReason"], "unknown_model_id")
        self.assertIsNone(result["costUSD"])

    def test_pricing_file_maps_to_rates_and_skips_unfilled_rows(self):
        table = codex_usage.PRICING
        self.assertEqual(table[SOL_MODEL]["input"], 5.0)
        self.assertEqual(table[SOL_MODEL]["cache_write"], 6.25)
        self.assertNotIn("<model-id>", table)
        self.assertNotIn("cached", table["fixture-nocache"])

    def test_missing_cached_rate_is_unpriced_not_a_ratio_of_input(self):
        result = codex_usage.attribute_cost("fixture-nocache", 100, 0, 50,
                                            service_tier="standard",
                                            context_pricing_class="standard")
        self.assertEqual(result["unpricedReason"], "cached_rate_unavailable")
        self.assertIsNone(result["costUSD"])

    def test_unknown_and_unpriced_cache_write_fail_closed(self):
        unknown = codex_usage.attribute_cost("unpriced-test-model", 1, 0, 0,
                                              service_tier="standard",
                                              context_pricing_class="standard")
        self.assertEqual((unknown["costStatus"], unknown["unpricedReason"]),
                         ("unpriced", "unknown_model_id"))
        write = codex_usage.attribute_cost(TERRA_MODEL, 10, 0, 0, 1,
                                            service_tier="standard",
                                            context_pricing_class="standard")
        self.assertEqual(write["unpricedReason"], "cache_write_rate_unavailable")
        sol_write = codex_usage.attribute_cost(SOL_MODEL, 1_000_000, 0, 0, 1_000_000,
                                                service_tier="standard",
                                                context_pricing_class="standard")
        self.assertEqual(sol_write["costUSD"], 6.25)

    def test_model_switch_keeps_the_running_total(self):
        # Real logs: total_token_usage keeps growing across a model switch, so
        # the second model's delta is 150 - 100, not the whole 150 again.
        rows = self.parse([
            context(SOL_MODEL), token(None, usage(100, 10)),
            context(TERRA_MODEL), token(None, usage(150, 15)),
        ])
        self.assertEqual([(row["model"], row["input"], row["output"], row["usage_source"])
                          for row in rows],
                         [(SOL_MODEL, 100, 10, "total_delta"),
                          (TERRA_MODEL, 50, 5, "total_delta")])

    def test_repeat_straddling_a_model_switch_counts_once(self):
        rows = self.parse([context(SOL_MODEL), token(usage(100), usage(100)),
                           context(TERRA_MODEL), token(usage(100), usage(100))])
        self.assertEqual(sum(row["input"] for row in rows), 100)

    def test_total_reset_is_new_epoch_and_marked_estimated(self):
        rows = self.parse([context(SOL_MODEL), token(None, usage(100)),
                           token(None, usage(25))])
        self.assertEqual(rows[1]["input"], 25)
        self.assertEqual(rows[1]["usage_source"], "total_delta_reset")
        priced = codex_usage.attribute_cost(rows[1]["model"], rows[1]["input"], 0, 0,
                                            usage_source=rows[1]["usage_source"],
                                            service_tier="standard",
                                            context_pricing_class="standard")
        self.assertEqual(priced["costStatus"], "estimated")

    def test_last_usage_beats_cumulative_sum_trap(self):
        rows = self.parse([context(SOL_MODEL), token(usage(10), usage(10)),
                           token(usage(10), usage(20))])
        self.assertEqual(sum(row["input"] for row in rows), 20)
        self.assertNotEqual(sum((10, 20)), sum(row["input"] for row in rows))

    def test_resent_token_event_with_unchanged_total_counts_once(self):
        # Codex can re-emit a token_count event; the cumulative total does not
        # move, so no new tokens were billed and the repeat must not be summed.
        rows = self.parse([context(SOL_MODEL),
                           token(usage(100, 10), usage(100, 10)),
                           token(usage(100, 10), usage(100, 10)),
                           token(usage(50, 5), usage(150, 15))])
        self.assertEqual(sum(row["input"] for row in rows), 150)
        self.assertEqual(len(rows), 2)

    def run_main(self, records, *argv):
        """Run main() over one synthetic session; return (exit code, stdout, stderr)."""
        with tempfile.TemporaryDirectory() as directory:
            sessions = Path(directory) / "sessions"
            sessions.mkdir()
            (sessions / "rollout-synthetic.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in records))
            args = [str(self.rates) if a == "{rates}" else a for a in argv]
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(codex_usage, "SESSIONS_DIR", sessions), \
                 mock.patch.object(sys, "argv", ["codex-usage.py", *args]), \
                 redirect_stdout(out), redirect_stderr(err):
                try:
                    codex_usage.main()
                    code = 0
                except SystemExit as exit_info:
                    code = exit_info.code
            return code, out.getvalue(), err.getvalue()

    def test_aggregate_reports_price_exactly_as_traces(self):
        # Real-shaped log: no service_tier or context_pricing_class. Every report
        # must price the event the same way traces does, and say what it assumed.
        records = [context(SOL_MODEL), token(usage(1_000_000), usage(1_000_000))]
        code, out, _ = self.run_main(records, "traces", "--pricing", "{rates}")
        trace = json.loads(out)["traces"][0]
        self.assertEqual(code, 0)
        self.assertEqual((trace["costUSD"], trace["costStatus"]), (5.0, "estimated"))
        self.assertTrue(trace["assumedDefaults"])
        for command in ("daily", "monthly", "sessions", "models"):
            code, out, _ = self.run_main(records, command, "--pricing", "{rates}")
            self.assertEqual(code, 0, command)
            self.assertIn("Cost summary: $5.00", out, command)
            self.assertIn("Assumed service_tier=standard", out, command)
            self.assertIn("understated if a priority tier or long-context billing", out, command)
            code, out, _ = self.run_main(records, command, "--json", "--pricing", "{rates}")
            doc = json.loads(out)
            self.assertIn("understated", doc["costNote"], command)
            rows = doc[command].values() if command == "models" else doc[command]
            self.assertEqual([row["costUSD"] for row in rows], [trace["costUSD"]], command)
            self.assertTrue(doc["costComplete"], command)

    def test_unknown_model_under_pricing_exits_3_in_every_report(self):
        records = [context("fixture-mystery"), token(usage(1_000_000), usage(1_000_000))]
        for command in ("daily", "monthly", "sessions", "models", "traces"):
            code, out, err = self.run_main(records, command, "--pricing", "{rates}")
            self.assertEqual(code, codex_usage.UNPRICED_EXIT, command)
            self.assertNotIn("$5.00", out, command)
            self.assertIn("unpriced", out + err, command)

    def test_logged_non_standard_tier_stays_unpriced(self):
        records = [context(SOL_MODEL, service_tier="priority"),
                   token(usage(1_000_000), usage(1_000_000))]
        code, out, _ = self.run_main(records, "models", "--pricing", "{rates}")
        self.assertEqual(code, codex_usage.UNPRICED_EXIT)
        self.assertIn("ambiguous_service_tier", out)

    def test_tier_from_thread_settings_is_not_assumed_standard(self):
        # Codex logs the tier only in thread_settings_applied. Reading turn_context alone
        # priced a priority-tier run at the standard rate, understated and unflagged.
        records = [settings(service_tier="priority"), context(SOL_MODEL),
                   token(usage(1_000_000), usage(1_000_000))]
        code, out, _ = self.run_main(records, "models", "--pricing", "{rates}")
        self.assertEqual(code, codex_usage.UNPRICED_EXIT)
        self.assertIn("ambiguous_service_tier", out)

    def test_logged_default_tier_counts_as_standard_not_assumed(self):
        records = [settings(service_tier="default"), context(SOL_MODEL),
                   token(usage(1_000_000), usage(1_000_000))]
        code, out, _ = self.run_main(records, "traces", "--pricing", "{rates}")
        trace = json.loads(out)["traces"][0]
        self.assertEqual((code, trace["costUSD"], trace["costStatus"]), (0, 5.0, "estimated"))
        self.assertFalse(any("service_tier" in a for a in trace["assumedDefaults"]))

    def test_cost_summary_never_turns_unpriced_into_zero(self):
        self.assertEqual(codex_usage.fmt_cost_summary(0.0, 2), "unpriced")
        self.assertEqual(codex_usage.fmt_cost_summary(1.25, 1),
                         "$1.25 known subtotal; 1 unpriced row(s)")
        self.assertEqual(codex_usage.fmt_cost_summary(1.25, 0), "$1.25")


class CodexReferenceSnippet(unittest.TestCase):
    """The DIY snippet in references/coding-agent-usage-tracking.md follows the same rules."""

    def snippet(self):
        text = (Path(__file__).resolve().parent.parent / "references"
                / "coding-agent-usage-tracking.md").read_text(encoding="utf-8")
        match = re.search(r"### Codex — Daily Totals Across Sessions \(Python\).*?```python\n(.*?)```",
                          text, re.S)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_non_object_lines_are_skipped_and_model_switch_keeps_total(self):
        records = [context(SOL_MODEL), token(None, usage(100, 10)),
                   context(TERRA_MODEL), token(None, usage(150, 15))]
        with tempfile.TemporaryDirectory() as home:
            day = Path(home) / ".codex" / "sessions" / "2026" / "08" / "15"
            day.mkdir(parents=True)
            (day / "rollout-synthetic.jsonl").write_text(
                "[1, 2]\n5\n" + "".join(json.dumps(r) + "\n" for r in records))
            result = subprocess.run([sys.executable, "-B", "-c", self.snippet()],
                                    capture_output=True, text=True,
                                    env={**os.environ, "HOME": home})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "2026-08-15: in=150 out=15 cached=0 reasoning=0")

    def test_decrease_right_after_model_switch_is_a_new_epoch_in_script_and_snippet(self):
        # A switch alone keeps the running total, but a decrease still starts a
        # new epoch: B's 60 is its own usage, not 60 - 100.
        records = [context(SOL_MODEL), token(None, usage(100)),
                   context(TERRA_MODEL), token(None, usage(60))]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.jsonl"
            path.write_text("".join(json.dumps(r) + "\n" for r in records))
            rows = list(codex_usage.parse_session_events(str(path)))
        self.assertEqual([(row["model"], row["input"]) for row in rows],
                         [(SOL_MODEL, 100), (TERRA_MODEL, 60)])
        with tempfile.TemporaryDirectory() as home:
            day = Path(home) / ".codex" / "sessions" / "2026" / "08" / "15"
            day.mkdir(parents=True)
            (day / "rollout-synthetic.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in records))
            result = subprocess.run([sys.executable, "-B", "-c", self.snippet()],
                                    capture_output=True, text=True,
                                    env={**os.environ, "HOME": home})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "2026-08-15: in=160 out=0 cached=0 reasoning=0")
        self.assertEqual(sum(row["input"] for row in rows), 160)


class CodexUsageWithoutPricing(unittest.TestCase):
    """No --pricing: tokens are reported, and no cost figure appears anywhere."""

    def test_no_rate_is_built_in(self):
        # A freshly imported module must know no rates: fails if a fallback price
        # table is reintroduced for any real model ID.
        spec = importlib.util.spec_from_file_location("codex_usage_fresh", MODULE)
        fresh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fresh)
        self.assertEqual(fresh.PRICING, {})
        for model in REAL_LOOKING_IDS:
            result = fresh.attribute_cost(model, 1_000_000, 1_000_000, 0,
                                          service_tier="standard",
                                          context_pricing_class="standard")
            self.assertIsNone(result["costUSD"], model)
            self.assertEqual(result["unpricedReason"], "no_rates_supplied")

    def test_models_report_prints_tokens_but_no_cost(self):
        records = [context("gpt-5.6-sol"), token(usage(1_234_567, 10), usage(1_234_567, 10))]
        with tempfile.TemporaryDirectory() as directory:
            sessions = Path(directory) / "sessions"
            sessions.mkdir()
            (sessions / "s.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(codex_usage, "SESSIONS_DIR", sessions), \
                 mock.patch.object(sys, "argv", ["codex-usage.py", "models"]), \
                 redirect_stdout(out), redirect_stderr(err):
                codex_usage.main()
        self.assertIn("1,234,567", out.getvalue())
        self.assertNotIn("$", out.getvalue() + err.getvalue())
        self.assertNotIn("Est. Cost", out.getvalue())
        self.assertIn("--pricing", err.getvalue())


if __name__ == "__main__":
    unittest.main()
