#!/usr/bin/env python3
"""Deterministic regression tests for fail-closed Codex usage attribution."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("codex-usage.py")
SPEC = importlib.util.spec_from_file_location("codex_usage", MODULE)
codex_usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(codex_usage)
SOL_MODEL = next(model for model in codex_usage.PRICING if model.endswith("-sol"))
TERRA_MODEL = next(model for model in codex_usage.PRICING if model.endswith("-terra"))


def usage(inp, out=0, cached=0, cache_write=0):
    return {"input_tokens": inp, "output_tokens": out,
            "cached_input_tokens": cached, "cache_write_input_tokens": cache_write,
            "reasoning_output_tokens": 0, "total_tokens": inp + out}


def context(model, tier="standard", context_class="standard"):
    return {"type": "turn_context", "payload": {
        "model": model, "service_tier": tier,
        "context_pricing_class": context_class}}


def token(last=None, total=None):
    return {"timestamp": "2026-08-15T00:00:00Z", "type": "event_msg", "payload": {
        "type": "token_count", "info": {
            "last_token_usage": last, "total_token_usage": total}}}


class CodexUsageTests(unittest.TestCase):
    def parse(self, records):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in records))
            return list(codex_usage.parse_session_events(str(path)))

    def test_exact_lookup_does_not_match_gpt5_prefix(self):
        result = codex_usage.attribute_cost(SOL_MODEL, 1_000_000, 0, 0,
                                            service_tier="standard",
                                            context_pricing_class="standard")
        self.assertEqual(result["costStatus"], "exact")
        self.assertEqual(result["costUSD"], 5.0)
        self.assertTrue(result["pricingSha256"])
        self.assertTrue(result["rateSource"].endswith(SOL_MODEL))

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

    def test_model_change_resets_total_delta_epoch(self):
        rows = self.parse([
            context(SOL_MODEL), token(None, usage(100)),
            context(TERRA_MODEL), token(None, usage(30)),
        ])
        self.assertEqual([(row["model"], row["input"], row["usage_source"]) for row in rows],
                         [(SOL_MODEL, 100, "total_delta"),
                          (TERRA_MODEL, 30, "total_delta")])

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

    def test_cost_summary_never_turns_unpriced_into_zero(self):
        self.assertEqual(codex_usage.fmt_cost_summary(0.0, 2), "unpriced")
        self.assertEqual(codex_usage.fmt_cost_summary(1.25, 1),
                         "$1.25 known subtotal; 1 unpriced row(s)")
        self.assertEqual(codex_usage.fmt_cost_summary(1.25, 0), "$1.25")


if __name__ == "__main__":
    unittest.main()
