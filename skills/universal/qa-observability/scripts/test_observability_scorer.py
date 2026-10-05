#!/usr/bin/env python3
"""Unit tests for observability_scorer.py."""

from __future__ import annotations

import importlib.util
import io
import os
import json
import subprocess

import pytest
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"


def load_module():
    spec = importlib.util.spec_from_file_location("observability_scorer", Path(os.environ.get("OBSERVABILITY_SCORER_SCRIPT", SCRIPT_DIR / "observability_scorer.py")))
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

    def test_slo_status_uses_event_counts_over_stale_percentage(self) -> None:
        # 1,440 failures of 2,157,780 is 99.933% (budget 2,157 events), so the
        # budget is NOT exhausted even though the stored percentage says 99.85.
        slo = observability_scorer.SLOEntry(
            name="orders-availability",
            service="orders-api",
            metric_type="availability",
            target_pct=99.9,
            window_days=30,
            current_availability_pct=99.85,
            good_events=2156340,
            total_events=2157780,
            raw={},
        )

        result = observability_scorer.compute_slo_status(slo)

        self.assertGreater(result.remaining_budget_events, 0)
        self.assertNotEqual(result.status, observability_scorer.SLO_STATUS_EXHAUSTED)
        self.assertAlmostEqual(result.burn_rate, 1440 / 2157.78, places=3)

    def test_sample_slo_data_is_internally_consistent(self) -> None:
        # Exhausted status and remaining budget events must never disagree.
        for slo in observability_scorer.load_slos(DATA_DIR / "sample-slo-data.json"):
            result = observability_scorer.compute_slo_status(slo)
            exhausted = result.status == observability_scorer.SLO_STATUS_EXHAUSTED
            self.assertEqual(exhausted, result.remaining_budget_events == 0, slo.name)

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


def valid_slo():
    return dict(name="availability", service="orders", target_pct=99.9, window_days=30,
                good_events=9995, total_events=10000)


@pytest.mark.parametrize("changes", [
    {"target_pct": None}, {"target_pct": 10**400}, {"target_pct": 100}, {"target_pct": -1},
    {"target_pct": float("nan")}, {"window_days": 0}, {"window_days": 1.5},
    {"total_events": 0, "good_events": 0}, {"total_events": -1},
    {"good_events": 10001}, {"good_events": -1}, {"good_events": 0.5},
    {"total_events": True}, {"current_availability_pct": float("inf")},
    {"current_availability_pct": 101}, {"name": ""},
])
def test_invalid_slo_is_rejected(changes):
    with pytest.raises(ValueError):
        observability_scorer.SLOEntry.from_dict({**valid_slo(), **changes})


@pytest.mark.parametrize("missing", ["target_pct", "window_days", "good_events", "total_events"])
def test_missing_slo_fields_are_rejected(missing):
    data = valid_slo()
    data.pop(missing)
    with pytest.raises(ValueError):
        observability_scorer.SLOEntry.from_dict(data)


@pytest.mark.parametrize("data", [{}, {"service_name": "x"},
    {"service_name": "x", "signals": []},
    {"service_name": "x", "signals": {}, "environment": None},
    {"service_name": "x", "signals": {"metrics": {"score": 21}}},
    {"service_name": "x", "signals": {"metrics": {"score": -1}}},
    {"service_name": "x", "signals": {"metrics": {"score": True}}},
    {"service_name": "x", "signals": {"metrics": {"score": 1.5}}},
    {"service_name": "x", "signals": {"metrics": {}}},
    {"service_name": "x", "signals": {"typo": {"score": 5}}},
])
def test_invalid_profile_is_rejected(data):
    with pytest.raises(ValueError):
        observability_scorer.ObservabilityProfile.from_dict(data)


def test_exact_budget_boundary_is_exhausted():
    slo = observability_scorer.SLOEntry.from_dict({**valid_slo(), "target_pct": 99.5,
                                                 "good_events": 9950})
    result = observability_scorer.compute_slo_status(slo)
    assert result.status == "BUDGET_EXHAUSTED"
    assert result.consumed_pct == 100
    assert result.remaining_budget_events == 0


def test_percentage_only_has_unknown_event_budget():
    data = valid_slo()
    data.pop("total_events")
    data.pop("good_events")
    data["current_availability_pct"] = 99.95
    result = observability_scorer.compute_slo_status(observability_scorer.SLOEntry.from_dict(data))
    assert result.remaining_budget_events is None
    assert result.consumed_pct == 50


@pytest.mark.parametrize("payload", ["[", "[NaN]", "[]", "[{}]", '[{"target_pct": Infinity}]'])
def test_cli_fails_without_health_output_or_traceback(tmp_path, payload):
    path = tmp_path / "invalid.json"
    path.write_text(payload)
    script = os.environ.get("OBSERVABILITY_SCORER_SCRIPT", SCRIPT_DIR / "observability_scorer.py")
    result = subprocess.run([sys.executable, str(script), "slo", "--input", str(path)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "ERROR:" in result.stderr
    assert "Traceback" not in result.stderr
    assert "HEALTHY" not in result.stdout


def test_report_does_not_equate_self_scores_with_runtime_coverage(tmp_path):
    data = json.loads((DATA_DIR / "sample-observability-profile.json").read_text())
    for key, maximum in observability_scorer.DIMENSION_MAX.items():
        data["signals"][key] = {"score": maximum}
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(data))
    output = tmp_path / "report.md"
    observability_scorer.cmd_report(SimpleNamespace(input=str(path), slos=None, output=str(output)))
    text = output.read_text()
    assert "not prove runtime coverage" in text
    assert "All core signals are present and well-configured" not in text


def test_cli_huge_number_is_an_error_without_traceback(tmp_path):
    path = tmp_path / "huge.json"
    path.write_text(json.dumps({**valid_slo(), "target_pct": 10**400}))
    # An array is required, so preserve the SLO shape when running the CLI.
    path.write_text("[" + path.read_text() + "]")
    script = os.environ.get("OBSERVABILITY_SCORER_SCRIPT", SCRIPT_DIR / "observability_scorer.py")
    result = subprocess.run([sys.executable, str(script), "slo", "--input", str(path)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "ERROR:" in result.stderr
    assert "Traceback" not in result.stderr
