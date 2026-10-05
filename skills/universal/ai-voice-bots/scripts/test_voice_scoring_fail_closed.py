"""Regression checks for incomplete voice-scoring input."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent


def run_script(name: str, lines: list[dict]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "input.jsonl"
        path.write_text("\n".join(json.dumps(line) for line in lines))
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), "--input", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )


class FailClosedScoringTests(unittest.TestCase):
    def test_latency_missing_total_cannot_pass_budget(self):
        result = run_script(
            "voice_latency_audit.py",
            [{"components": {"vad": {"start_ms": 0, "end_ms": 150}}}],
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("total_turn_ms", result.stderr)

    def test_quality_empty_input_cannot_report_zero_call_success(self):
        result = run_script("call_quality_scorer.py", [])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no calls", result.stderr)

    def test_quality_missing_outcome_is_rejected(self):
        result = run_script(
            "call_quality_scorer.py",
            [{"call_id": "synthetic-1", "turns": [{"role": "user", "content": "Hello"}]}],
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outcome", result.stderr)

    def test_complete_latency_and_call_inputs_succeed(self):
        latency = run_script(
            "voice_latency_audit.py",
            [{"total_turn_ms": 150, "components": {"vad": {"start_ms": 0, "end_ms": 150}}}],
        )
        quality = run_script(
            "call_quality_scorer.py",
            [{"call_id": "synthetic-1", "outcome": "resolved", "turns": [{"role": "user", "content": "Hello"}]}],
        )
        self.assertEqual(latency.returncode, 0, latency.stderr)
        self.assertEqual(quality.returncode, 0, quality.stderr)


if __name__ == "__main__":
    unittest.main()
