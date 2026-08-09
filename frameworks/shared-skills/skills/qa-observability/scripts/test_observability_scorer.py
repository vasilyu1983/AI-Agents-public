#!/usr/bin/env python3
"""Unit tests for observability_scorer.py."""

from __future__ import annotations

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"


def load_module():
    spec = importlib.util.spec_from_file_location("observability_scorer", SCRIPT_DIR / "observability_scorer.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


observability_scorer = load_module()


class ObservabilityScorerTests(unittest.TestCase):
    def test_compute_maturity_returns_all_dimensions(self) -> None:
        profile = observability_scorer.load_profile(DATA_DIR / "sample-observability-profile.json")
        result = observability_scorer.compute_maturity(profile)

        self.assertEqual(len(result.dimension_results), len(observability_scorer.DIMENSIONS))
        self.assertIn(result.maturity_level, {"FOUNDATIONAL", "DEVELOPING", "PROFICIENT", "ADVANCED"})

    def test_compute_slo_status_flags_budget_exhaustion(self) -> None:
        slo = observability_scorer.SLOEntry(
            name="api-availability",
            service="checkout-api",
            metric_type="availability",
            target_pct=99.9,
            window_days=30,
            current_availability_pct=99.0,
            good_events=990,
            total_events=1000,
            raw={},
        )

        result = observability_scorer.compute_slo_status(slo)

        self.assertEqual(result.status, observability_scorer.SLO_STATUS_EXHAUSTED)
        self.assertGreater(result.burn_rate, 1.0)

    def test_report_writes_markdown(self) -> None:
        output_buffer = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "observability-report.md"
            args = SimpleNamespace(
                input=str(DATA_DIR / "sample-observability-profile.json"),
                slos=str(DATA_DIR / "sample-slo-data.json"),
                output=str(output_path),
            )
            with redirect_stdout(output_buffer):
                exit_code = observability_scorer.cmd_report(args)

            report_text = output_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertIn("# Observability Readiness Report", report_text)
        self.assertIn("## 4. Prioritised Improvement Plan", report_text)
        self.assertIn("Report written to", output_buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
