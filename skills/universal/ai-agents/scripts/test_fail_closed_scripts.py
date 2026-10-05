#!/usr/bin/env python3
"""Regression tests: the eval runner and Claude usage reporter fail closed."""

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

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load("agent_eval_runner", "agent_eval_runner.py")
claude_usage = load("claude_usage", "claude-usage.py")

# Arithmetic tests own their rates. They are deliberately fake (fixture model IDs,
# round numbers) so no test can pass by matching a real published price.
FIXTURE_PRICING = {
    "fixture-big": {"input": 5.0, "output": 25.0, "cache_read": 0.5, "cache_create": 6.25},
    "fixture-nocache": {"input": 2.0, "output": 10.0},
}
# The same rates in the user-facing --pricing file schema.
FIXTURE_PRICING_FILE = {
    "source_url": "https://example.invalid/pricing",
    "retrieved_at": "2000-01-01",
    "models": {
        "fixture/fixture-big": {"input_per_1m": 5.0, "output_per_1m": 25.0,
                                "cache_read_per_1m": 0.5, "cache_write_per_1m": 6.25},
        "fixture-nocache": {"input_per_1m": 2.0, "output_per_1m": 10.0,
                            "cache_read_per_1m": None, "cache_write_per_1m": None},
        "<model-id>": {"input_per_1m": None, "output_per_1m": None},
    },
}
# Real-looking IDs: with no --pricing none of them may ever get a cost.
REAL_LOOKING_IDS = ("claude-opus-4-8", "claude-sonnet-4-5", "claude-sonnet-4-6",
                    "claude-haiku-4-5", "claude-opus-4-7")


class EvalRunnerFailsClosed(unittest.TestCase):
    def run_lines(self, lines, mode="substring"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.jsonl"
            path.write_text("\n".join(lines) + "\n")
            report = Path(directory) / "report.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = runner.run(path, report, mode, verbose=False)
            return code, json.loads(report.read_text())

    def test_record_without_fields_fails(self):
        code, report = self.run_lines(['{"foo": 1}'])
        self.assertEqual((code, report["passed"]), (1, 0))

    def test_empty_expected_cannot_match_everything(self):
        code, report = self.run_lines(['{"task": "t", "expected": "", "actual": "anything"}'])
        self.assertEqual((code, report["passed"]), (1, 0))

    def test_unknown_record_mode_fails_instead_of_defaulting(self):
        code, report = self.run_lines(['{"expected": "x", "actual": "xyz", "mode": "bogus"}'])
        self.assertEqual(code, 1)
        self.assertIn("unknown mode", report["results"][0]["reason"])

    def test_malformed_line_stays_in_denominator(self):
        code, report = self.run_lines(['{"expected": "a", "actual": "a"}', '{broken'])
        self.assertEqual((code, report["total"], report["passed"]), (1, 2, 1))

    def test_json_array_is_invalid_record_not_traceback(self):
        code, report = self.run_lines(["[1, 2]"])
        self.assertEqual(code, 1)
        self.assertIn("expected a JSON object", report["results"][0]["reason"])

    def test_nonempty_mode_needs_no_expected(self):
        code, _ = self.run_lines(['{"actual": "x", "mode": "nonempty"}'])
        self.assertEqual(code, 0)

    def test_valid_substring_record_still_passes(self):
        code, _ = self.run_lines(['{"expected": "Brief", "actual": "a brief note"}'])
        self.assertEqual(code, 0)

    def test_unknown_cli_mode_exits_2(self):
        result = subprocess.run(
            [sys.executable, str(HERE / "agent_eval_runner.py"), "--input", "x.jsonl",
             "--mode", "bogus"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


def record(model, input_tokens, message_id=None, request_id=None, **usage):
    """A synthetic assistant log line with the real record shape."""
    message = {"model": model, "usage": {"input_tokens": input_tokens, "output_tokens": 0, **usage}}
    if message_id:
        message["id"] = message_id
    rec = {"timestamp": "2026-01-01T00:00:00Z", "sessionId": "s", "message": message}
    if request_id:
        rec["requestId"] = request_id
    return rec


def run_claude(records, argv, stats=None, rates=FIXTURE_PRICING_FILE, extra_files=None):
    """Run claude-usage main() over synthetic logs; return (exit code, stdout, stderr).

    extra_files maps a path under the project directory to its records, for
    example the subagent transcripts Claude Code writes at s/subagents/*.jsonl.
    """
    with tempfile.TemporaryDirectory() as directory:
        projects = Path(directory) / "projects" / "p"
        projects.mkdir(parents=True)
        (projects / "s.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
        for relative, extra in (extra_files or {}).items():
            (projects / relative).parent.mkdir(parents=True, exist_ok=True)
            (projects / relative).write_text("".join(json.dumps(r) + "\n" for r in extra))
        stats_path = Path(directory) / "stats-cache.json"
        if stats is not None:
            stats_path.write_text(json.dumps(stats))
        rates_path = Path(directory) / "rates.json"
        rates_path.write_text(json.dumps(rates))
        args = [a.replace("{rates}", str(rates_path)) for a in argv]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(claude_usage, "PROJECTS_DIR", Path(directory) / "projects"), \
             mock.patch.object(claude_usage, "STATS_CACHE", stats_path), \
             mock.patch.object(sys, "argv", ["claude-usage.py", *args]), \
             redirect_stdout(out), redirect_stderr(err):
            try:
                claude_usage.main()
                code = 0
            except SystemExit as exit_info:
                code = exit_info.code
        return code, out.getvalue(), err.getvalue()


class ClaudeUsageFailsClosed(unittest.TestCase):
    def setUp(self):
        patch = mock.patch.object(claude_usage, "PRICING", FIXTURE_PRICING)
        patch.start()
        self.addCleanup(patch.stop)

    def test_unknown_model_is_unpriced_not_default_rate(self):
        self.assertEqual(claude_usage.attribute_cost("fixture-mystery", 1_000_000, 0, 0, 0),
                         (None, "unknown_model_id"))

    def test_longer_id_cannot_borrow_listed_rate(self):
        cost, reason = claude_usage.attribute_cost("fixture-big-plus", 1_000_000, 0, 0, 0)
        self.assertEqual((cost, reason), (None, "unknown_model_id"))

    def test_snapshot_suffix_maps_to_base_id(self):
        cost, reason = claude_usage.attribute_cost("fixture-big-20260101", 1_000_000, 0, 0, 0)
        self.assertEqual((cost, reason), (5.0, None))

    def test_missing_cache_rate_is_unpriced_not_free(self):
        _, reason = claude_usage.attribute_cost("fixture-nocache", 10, 0, 5, 0)
        self.assertEqual(reason, "cache_read_rate_unavailable")

    def test_bucket_prices_each_model_and_withholds_incomplete_total(self):
        tokens = {"input": 1_000_000, "output": 0, "cache_read": 0, "cache_create": 0}
        priced = claude_usage.price_bucket({"fixture-big": dict(tokens),
                                            "fixture-mystery": dict(tokens)})
        self.assertIsNone(priced["costUSD"])
        self.assertEqual(priced["knownCostUSD"], 5.0)
        self.assertEqual(priced["unpricedModels"], {"fixture-mystery": "unknown_model_id"})

    def run_main(self, models, *extra):
        """Run main() over a synthetic log; return (exit code, stdout, stderr)."""
        records = [record(model, 1_000_000, f"msg_{i}") for i, model in enumerate(models)]
        return run_claude(records, extra)

    def test_daily_and_monthly_exit_3_when_a_model_is_unpriced(self):
        for command in ("daily", "monthly"):
            code, out, _ = self.run_main(("fixture-big", "fixture-mystery"),
                                         command, "--pricing", "{rates}")
            self.assertEqual(code, claude_usage.UNPRICED_EXIT)
            self.assertIn("Known cost subtotal: $5.00", out)

    def test_pricing_file_schema_maps_to_rates(self):
        with tempfile.TemporaryDirectory() as directory:
            rates = Path(directory) / "rates.json"
            rates.write_text(json.dumps(FIXTURE_PRICING_FILE))
            table = claude_usage.load_pricing_file(rates)
        self.assertEqual(table, FIXTURE_PRICING)

    def test_unreadable_pricing_file_exits_2(self):
        code, out, err = self.run_main(("fixture-big",), "daily", "--pricing", "/nonexistent/rates.json")
        self.assertEqual(code, 2)
        self.assertNotIn("$", out)

    def test_unfilled_template_is_rejected_not_priced_at_zero(self):
        template = HERE.parent / "assets" / "pricing-template.json"
        code, out, _ = self.run_main(("fixture-big",), "daily", "--pricing", str(template))
        self.assertEqual(code, 2)
        self.assertNotIn("$", out)


class ClaudeUsageCountsEachResponseOnce(unittest.TestCase):
    """Claude Code writes one line per content block; each repeats the response's usage."""

    def monthly(self, records, rates=FIXTURE_PRICING_FILE):
        code, out, err = run_claude(records, ("monthly", "--json", "--pricing", "{rates}"), rates=rates)
        return code, json.loads(out)["monthly"][0], err

    def test_duplicate_content_block_lines_count_once(self):
        # One response (thinking + text blocks) logged as two lines.
        lines = [record("fixture-big", 1_000_000, "msg_1", "req_1"),
                 record("fixture-big", 1_000_000, "msg_1", "req_1")]
        code, row, _ = self.monthly(lines)
        self.assertEqual(code, 0)
        self.assertEqual((row["inputTokens"], row["messages"], row["costUSD"]), (1_000_000, 1, 5.0))

    def test_subagent_transcripts_are_read_and_shared_responses_count_once(self):
        # Subagent responses live only in <session>/subagents/*.jsonl; missing
        # them undercounts agent-heavy work. A response present in both files
        # must still count once.
        main = [record("fixture-big", 1_000_000, "msg_1", "req_1")]
        subagent = [record("fixture-big", 1_000_000, "msg_2", "req_2"),
                    record("fixture-big", 1_000_000, "msg_1", "req_1")]
        code, out, _ = run_claude(main, ("monthly", "--json", "--pricing", "{rates}"),
                                  extra_files={"s/subagents/agent-a.jsonl": subagent})
        row = json.loads(out)["monthly"][0]
        self.assertEqual(code, 0)
        self.assertEqual((row["inputTokens"], row["messages"], row["costUSD"]), (2_000_000, 2, 10.0))

    def test_distinct_responses_and_lines_without_id_still_sum(self):
        lines = [record("fixture-big", 1_000_000, "msg_1", "req_1"),
                 record("fixture-big", 1_000_000, "msg_2", "req_2"),
                 record("fixture-big", 1_000_000), record("fixture-big", 1_000_000)]
        _, row, _ = self.monthly(lines)
        self.assertEqual(row["inputTokens"], 4_000_000)


def streamed(output_tokens, stop_reason, message_id="msg_1", request_id="req_1"):
    """One copy of a response: a mid-stream partial (stop_reason None) or the final record."""
    rec = record("fixture-big", 0, message_id, request_id, output_tokens=output_tokens)
    rec["message"]["stop_reason"] = stop_reason
    return rec


class ClaudeUsageKeepsTheMostCompleteCopy(unittest.TestCase):
    """A response's copies differ: a line written mid-stream has partial counters."""

    def test_final_record_wins_across_files_whatever_the_path_order(self):
        # The final record is in agent-a.jsonl and a streaming partial of the same
        # response in agent-b.jsonl, which sorts later. Path order must not decide.
        code, out, _ = run_claude([], ("monthly", "--json"), extra_files={
            "s/subagents/agent-a.jsonl": [streamed(500, "end_turn")],
            "s/subagents/agent-b.jsonl": [streamed(3, None)]})
        row = json.loads(out)["monthly"][0]
        self.assertEqual(code, 0)
        self.assertEqual((row["outputTokens"], row["messages"]), (500, 1))

    def test_sessions_fallback_puts_subagent_records_under_the_parent_session(self):
        # Without session-meta, sessions sums the logs by sessionId; a subagent
        # file carries its parent's sessionId, so it is not a session of its own.
        main = [record("fixture-big", 1_000_000, "msg_1", "req_1")]
        subagent = [record("fixture-big", 2_000_000, "msg_2", "req_2")]
        with tempfile.TemporaryDirectory() as empty_home, \
             mock.patch.object(claude_usage, "CLAUDE_DIR", Path(empty_home)):
            code, out, _ = run_claude(main, ("sessions", "--json"),
                                      extra_files={"s/subagents/agent-a.jsonl": subagent})
        sessions = json.loads(out)["sessions"]
        self.assertEqual(code, 0)
        self.assertEqual([(x["session_id"], x["input_tokens"], x["messages"]) for x in sessions],
                         [("s...", 3_000_000, 2)])


class ClaudeReferenceSnippet(unittest.TestCase):
    """The Claude DIY snippet in references/coding-agent-usage-tracking.md follows the same rules."""

    def run_snippet(self, files):
        text = (HERE.parent / "references" / "coding-agent-usage-tracking.md").read_text(encoding="utf-8")
        match = re.search(r"### Claude Code — Quick Session Summary \(Python\).*?```python\n(.*?)```",
                          text, re.S)
        self.assertIsNotNone(match)
        with tempfile.TemporaryDirectory() as home:
            for relative, content in files.items():
                path = Path(home) / ".claude" / "projects" / "p" / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            return subprocess.run([sys.executable, "-B", "-c", match.group(1)],
                                  capture_output=True, text=True,
                                  env={**os.environ, "HOME": home})

    @staticmethod
    def lines(*records):
        return "".join(json.dumps(r) + "\n" for r in records)

    def test_keeps_final_record_over_earlier_partial_and_skips_non_objects(self):
        result = self.run_snippet({
            "s.jsonl": "[1, 2]\n5\n" + self.lines(streamed(7, "end_turn", "msg_2", "req_2")),
            "s/subagents/agent-a.jsonl": self.lines(streamed(3, None), streamed(500, "tool_use"))})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(),
                         "fixture-big: in=0 out=507 cache_read=0 cache_create=0")

    def test_first_line_is_not_kept_when_it_is_a_streaming_partial(self):
        result = self.run_snippet({"s.jsonl": self.lines(streamed(3, None), streamed(500, "end_turn"))})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(" out=500 ", result.stdout)


class ClaudeUsageSeparatesCacheWriteTtl(unittest.TestCase):
    """5-minute and 1-hour cache writes are billed at different rates."""

    def one_hour_write(self):
        return record("fixture-big", 0, "msg_1", "req_1",
                      cache_creation_input_tokens=2_000_000,
                      cache_creation={"ephemeral_5m_input_tokens": 1_000_000,
                                      "ephemeral_1h_input_tokens": 1_000_000})

    def test_1h_writes_without_1h_rate_are_unpriced_not_5m_rate(self):
        code, out, _ = run_claude([self.one_hour_write()], ("monthly", "--pricing", "{rates}"))
        self.assertEqual(code, claude_usage.UNPRICED_EXIT)
        self.assertIn("cache_write_1h_rate_unavailable", out)
        self.assertNotIn("$12.50", out)  # both halves at the 5m rate

    def test_1h_writes_count_when_only_the_breakdown_is_logged(self):
        # No cache_creation_input_tokens: the breakdown alone sets the total,
        # so 1-hour writes are neither dropped to $0 nor left out of the tokens.
        line = record("fixture-big", 0, "msg_1", "req_1",
                      cache_creation={"ephemeral_5m_input_tokens": 0,
                                      "ephemeral_1h_input_tokens": 1_000_000})
        code, out, _ = run_claude([line], ("monthly", "--json", "--pricing", "{rates}"))
        self.assertEqual(code, claude_usage.UNPRICED_EXIT)  # no 1h rate in the file
        self.assertEqual(json.loads(out)["monthly"][0]["cacheCreateTokens"], 1_000_000)
        rates = json.loads(json.dumps(FIXTURE_PRICING_FILE))
        rates["models"]["fixture/fixture-big"]["cache_write_1h_per_1m"] = 10.0
        code, out, _ = run_claude([line], ("monthly", "--json", "--pricing", "{rates}"), rates=rates)
        self.assertEqual((code, json.loads(out)["monthly"][0]["costUSD"]), (0, 10.0))

    def test_models_pricing_uses_logs_where_the_ttl_split_exists(self):
        # stats-cache.json cannot split cache writes by TTL, so under --pricing
        # `models` prices from the JSONL logs instead of marking every model unpriced.
        stats = {"modelUsage": {"fixture-big": {"inputTokens": 0, "outputTokens": 0,
                                                "cacheReadInputTokens": 0,
                                                "cacheCreationInputTokens": 2_000_000}}}
        rates = json.loads(json.dumps(FIXTURE_PRICING_FILE))
        rates["models"]["fixture/fixture-big"]["cache_write_1h_per_1m"] = 10.0
        code, out, _ = run_claude([self.one_hour_write()], ("models", "--json", "--pricing", "{rates}"),
                                  stats=stats, rates=rates)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["models"]["fixture-big"]["costUSD"], 16.25)
        code, out, _ = run_claude([self.one_hour_write()], ("models", "--pricing", "{rates}"),
                                  stats=stats, rates=rates)
        self.assertEqual(code, 0)
        self.assertIn("Total estimated cost: $16.25", out)
        # Without --pricing, token counts still come from stats-cache.json.
        code, out, _ = run_claude([], ("models", "--json"), stats=stats)
        self.assertEqual((code, json.loads(out)["models"]), (0, stats["modelUsage"]))

    def test_1h_writes_use_their_own_rate(self):
        rates = json.loads(json.dumps(FIXTURE_PRICING_FILE))
        rates["models"]["fixture/fixture-big"]["cache_write_1h_per_1m"] = 10.0
        code, out, _ = run_claude([self.one_hour_write()], ("monthly", "--json", "--pricing", "{rates}"),
                                  rates=rates)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["monthly"][0]["costUSD"], 16.25)  # 6.25 + 10.00


class ClaudeUsageNeverIgnoresPricing(unittest.TestCase):
    STATS = {"dailyActivity": [{"date": "2026-01-01", "messageCount": 3,
                                "sessionCount": 1, "toolCallCount": 2}],
             "modelUsage": {"fixture-mystery": {"inputTokens": 1_000_000, "outputTokens": 0,
                                                "cacheReadInputTokens": 0,
                                                "cacheCreationInputTokens": 0}}}

    def test_daily_from_stats_cache_says_cost_unavailable(self):
        for argv in (("daily", "--pricing", "{rates}"), ("daily", "--json", "--pricing", "{rates}")):
            code, out, err = run_claude([], argv, stats=self.STATS)
            self.assertEqual(code, claude_usage.UNPRICED_EXIT, argv)
            self.assertIn("unavailable from stats-cache", err, argv)

    def test_daily_from_stats_cache_without_pricing_is_unchanged(self):
        code, _, _ = run_claude([], ("daily",), stats=self.STATS)
        self.assertEqual(code, 0)

    def test_models_json_exits_like_plain_text(self):
        for model, expected in (("fixture-mystery", claude_usage.UNPRICED_EXIT), ("fixture-big", 0)):
            records = [record(model, 1_000_000, "msg_1", "req_1")]
            plain, _, _ = run_claude(records, ("models", "--pricing", "{rates}"), stats=self.STATS)
            as_json, out, _ = run_claude(records, ("models", "--json", "--pricing", "{rates}"),
                                         stats=self.STATS)
            self.assertEqual((plain, as_json), (expected, expected))
        self.assertEqual(json.loads(out)["models"]["fixture-big"]["costUSD"], 5.0)


class ClaudeUsageWithoutPricing(unittest.TestCase):
    """No --pricing: tokens are reported, and no cost figure appears anywhere."""

    def test_no_rate_is_built_in(self):
        # A freshly imported module must know no rates: fails if a fallback price
        # table is reintroduced for any real model ID.
        fresh = load("claude_usage_fresh", "claude-usage.py")
        self.assertEqual(fresh.PRICING, {})
        for model in REAL_LOOKING_IDS:
            self.assertEqual(fresh.attribute_cost(model, 1_000_000, 1_000_000, 0, 0),
                             (None, "unknown_model_id"), model)

    def test_reports_tokens_but_prints_no_cost(self):
        for command in ("daily", "monthly"):
            code, out, err = ClaudeUsageFailsClosed.run_main(self, REAL_LOOKING_IDS, command)
            self.assertEqual(code, 0)
            self.assertIn("5,000,000", out)  # five models x 1M input tokens
            self.assertNotIn("$", out + err)
            self.assertNotIn("Est. Cost", out)
            self.assertIn("--pricing", err)
            self.assertIn("unpriced", err)

    def test_json_has_null_cost_and_incomplete_flag(self):
        code, out, _ = ClaudeUsageFailsClosed.run_main(self, REAL_LOOKING_IDS, "daily", "--json")
        self.assertEqual(code, 0)
        doc = json.loads(out)
        self.assertFalse(doc["costComplete"])
        self.assertTrue(all(row["costUSD"] is None for row in doc["daily"]))


if __name__ == "__main__":
    unittest.main()
