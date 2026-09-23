#!/usr/bin/env python3
"""Tests for the finite-trace FCFS queue simulator."""

from __future__ import annotations

import importlib.util
import io
import json
import math
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_DIR = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("queue_trace_simulator", SCRIPT_DIR / "queue_trace_simulator.py")
assert spec and spec.loader
simulator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = simulator
spec.loader.exec_module(simulator)


def jobs(rows):
    return [simulator.TraceJob(str(index + 1), arrival, service, index) for index, (arrival, service) in enumerate(rows)]


class QueueTraceSimulatorTests(unittest.TestCase):
    def test_single_server_hand_trace(self) -> None:
        report = simulator.simulate(jobs([(0, 3), (1, 2), (2, 1)]), 1)
        self.assertEqual([job["start_time"] for job in report["jobs"]], [0.0, 3.0, 5.0])
        self.assertEqual([job["waiting_time"] for job in report["jobs"]], [0.0, 2.0, 3.0])
        self.assertEqual([job["response_time"] for job in report["jobs"]], [3.0, 4.0, 4.0])
        self.assertEqual(report["summary"]["max_queue_length"], 2)
        self.assertEqual(report["measurement"]["queue_time_integral"], 5.0)
        self.assertEqual(report["measurement"]["busy_time"], 6.0)
        self.assertEqual(report["measurement"]["utilization"], 1.0)

    def test_multi_server_ties_use_lowest_available_server_id(self) -> None:
        report = simulator.simulate(jobs([(0, 4), (0, 2), (0, 1)]), 2)
        self.assertEqual(
            [(job["server_id"], job["start_time"], job["completion_time"]) for job in report["jobs"]],
            [(0, 0.0, 4.0), (1, 0.0, 2.0), (1, 2.0, 3.0)],
        )
        self.assertEqual(report["summary"]["max_queue_length"], 1)
        self.assertAlmostEqual(report["measurement"]["utilization"], 7 / 8)

    def test_release_at_arrival_time_causes_zero_wait(self) -> None:
        report = simulator.simulate(jobs([(0, 2), (2, 1), (5, 0)]), 1)
        self.assertEqual([job["waiting_time"] for job in report["jobs"]], [0.0, 0.0, 0.0])
        self.assertEqual(report["summary"]["jobs_waited"], 0)
        self.assertAlmostEqual(report["measurement"]["utilization"], 3 / 5)

    def test_measurement_window_clips_busy_and_queue_integrals(self) -> None:
        report = simulator.simulate(jobs([(0, 3), (1, 2), (2, 1)]), 1, 1, 4)
        self.assertEqual(report["measurement"]["duration"], 3.0)
        self.assertEqual(report["measurement"]["capacity_time"], 3.0)
        self.assertEqual(report["measurement"]["busy_time"], 3.0)
        self.assertEqual(report["measurement"]["queue_time_integral"], 4.0)
        self.assertEqual(report["measurement"]["queue_length_at_end"], 1)
        self.assertEqual(report["measurement"]["in_service_at_end"], 1)
        self.assertEqual(report["measurement"]["unfinished_jobs_at_end"], 2)

    def test_single_zero_service_job_has_defined_degenerate_interval(self) -> None:
        report = simulator.simulate(jobs([(0, 0)]), 3)
        self.assertEqual(report["measurement"]["duration"], 0.0)
        self.assertEqual(report["measurement"]["busy_time"], 0.0)
        self.assertIsNone(report["measurement"]["utilization"])
        json.dumps(report, allow_nan=False)

    def test_zero_service_ties_do_not_block_following_jobs(self) -> None:
        report = simulator.simulate(jobs([(0, 0), (0, 0), (0, 1)]), 1)
        self.assertEqual([job["start_time"] for job in report["jobs"]], [0.0, 0.0, 0.0])
        self.assertEqual([job["server_id"] for job in report["jobs"]], [0, 0, 0])

    def test_rejects_invalid_server_counts_and_values(self) -> None:
        for value in (0, -1, 1.0, True):
            with self.subTest(value=value), self.assertRaises(simulator.InputError):
                simulator.simulate(jobs([(0, 1)]), value)
        for value in (-1, math.nan, math.inf, True):
            with self.subTest(value=value), self.assertRaises(simulator.InputError):
                simulator.finite_nonnegative(value, "value")
        with self.assertRaises(simulator.InputError):
            simulator.finite_nonnegative(10**400, "value")

    def test_rejects_nonfinite_derived_completion_and_aggregates(self) -> None:
        extreme = jobs([(0, 1e308), (0, 1e308)])
        with self.assertRaisesRegex(simulator.InputError, "derived completion_time"):
            simulator.simulate(extreme, 1)
        with self.assertRaisesRegex(simulator.InputError, "derived busy_time"):
            simulator.simulate(extreme, 2)

    def test_rejects_out_of_order_arrivals_and_bad_window(self) -> None:
        with self.assertRaises(simulator.InputError):
            simulator.simulate(jobs([(1, 1), (0, 1)]), 1)
        with self.assertRaises(simulator.InputError):
            simulator.simulate(jobs([(0, 1)]), 1, 2, 1)

    def test_csv_validation_rejects_nonfinite_negative_and_duplicate_ids(self) -> None:
        cases = (
            "arrival_time,service_time\n0,nan\n",
            "arrival_time,service_time\n-1,1\n",
            "job_id,arrival_time,service_time\na,0,1\na,1,1\n",
            "arrival_time,service_time\n1,1\n0,1\n",
        )
        with TemporaryDirectory() as temp_dir:
            for index, content in enumerate(cases):
                path = Path(temp_dir) / f"bad-{index}.csv"
                path.write_text(content, encoding="utf-8")
                with self.subTest(index=index), self.assertRaises(simulator.InputError):
                    simulator.load_trace(path)

    def test_csv_validation_rejects_empty_trace_and_missing_columns(self) -> None:
        cases = ("arrival_time,service_time\n", "arrival_time\n0\n", "")
        with TemporaryDirectory() as temp_dir:
            for index, content in enumerate(cases):
                path = Path(temp_dir) / f"bad-shape-{index}.csv"
                path.write_text(content, encoding="utf-8")
                with self.subTest(index=index), self.assertRaises(simulator.InputError):
                    simulator.load_trace(path)

    def test_cli_emits_json_and_summary_only_omits_jobs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.csv"
            path.write_text("job_id,arrival_time,service_time\na,0,2\nb,1,1\n", encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = simulator.main(["--input", str(path), "--servers", "1", "--summary-only"])
        self.assertEqual(code, 0)
        report = json.loads(output.getvalue())
        self.assertNotIn("jobs", report)
        self.assertEqual(report["summary"]["waiting_time"]["p50"], 0.5)

    def test_cli_reports_invalid_input_without_traceback(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.csv"
            path.write_text("arrival_time,service_time\n0,inf\n", encoding="utf-8")
            error = io.StringIO()
            with redirect_stderr(error):
                code = simulator.main(["--input", str(path), "--servers", "1"])
        self.assertEqual(code, 2)
        self.assertIn("finite nonnegative", error.getvalue())

    def test_cli_reports_overflow_and_invalid_utf8_without_traceback(self) -> None:
        with TemporaryDirectory() as temp_dir:
            overflow_path = Path(temp_dir) / "overflow.csv"
            overflow_path.write_text(
                "arrival_time,service_time\n0,1e308\n0,1e308\n",
                encoding="utf-8",
            )
            invalid_utf8_path = Path(temp_dir) / "invalid.csv"
            invalid_utf8_path.write_bytes(b"arrival_time,service_time\n0,\xff\n")
            for args, expected in (
                (["--input", str(overflow_path), "--servers", "1"], "derived completion_time"),
                (["--input", str(overflow_path), "--servers", "2"], "derived busy_time"),
                (["--input", str(invalid_utf8_path), "--servers", "1"], "valid UTF-8 CSV"),
            ):
                error = io.StringIO()
                with self.subTest(args=args), redirect_stderr(error):
                    code = simulator.main(args)
                self.assertEqual(code, 2)
                self.assertIn(expected, error.getvalue())
                self.assertNotIn("Traceback", error.getvalue())


if __name__ == "__main__":
    unittest.main()
