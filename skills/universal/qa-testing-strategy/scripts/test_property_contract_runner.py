#!/usr/bin/env python3
"""Regression tests for the reusable property/metamorphic contract runner."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNNER = HERE / "property_contract_runner.py"
EXAMPLE = HERE.parent / "assets" / "property_contract_example.py"


def invoke_contract(contract: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--contract",
            str(contract),
            "--seed",
            "20260908",
            "--cases",
            "120",
            "--json",
            *extra,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def invoke(*extra: str) -> subprocess.CompletedProcess[str]:
    return invoke_contract(EXAMPLE, *extra)


BASE_ADAPTER = """
ORACLES = {"p": "Result equals an independent sort", "r": "Reversal preserves sorting"}
def generate(rng):
    return [rng.randint(-9, 9) for _ in range(5)]
def evaluate(case):
    return sorted(case)
def check_properties(case, result):
    return [{"name": "p", "ok": result == sorted(case), "detail": "wrong sort"}]
def transformations(case):
    return [{"name": "reverse", "case": list(reversed(case))}]
def check_relation(name, case, result, follow, follow_result):
    return [{"name": "r", "ok": result == follow_result, "detail": "order changed result"}]
"""


class PropertyContractRunnerTests(unittest.TestCase):
    def run_fixture(self, source: str, *extra: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "adapter.py"
            path.write_text(textwrap.dedent(source), encoding="utf-8")
            return invoke_contract(path, *extra)

    def test_known_correct_contract_passes(self) -> None:
        completed = invoke()
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["cases_run"], 120)
        self.assertGreaterEqual(payload["checks_run"], 240)

    def test_negative_control_mutations_are_caught_and_replay(self) -> None:
        expected_names = {
            "calculator-add-unit": "calculator_exact_product",
            "parser-drop-last-field": "parser_matches_declared_fields",
            "parser-space-sensitive": "parser_representation_equivalence",
            "serialization-stringify-scalars": "serialization_round_trip",
        }
        for mutation, check_name in expected_names.items():
            with self.subTest(mutation=mutation):
                completed = invoke("--mutation", mutation)
                self.assertEqual(completed.returncode, 1, completed.stderr or completed.stdout)
                payload = json.loads(completed.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertEqual(payload["failure"]["name"], check_name)
                self.assertIn("--case-index", payload["replay_command"])

                replay = subprocess.run(
                    shlex.split(payload["replay_command"]),
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(replay.returncode, 1, replay.stderr or replay.stdout)
                replay_payload = json.loads(replay.stdout)
                self.assertEqual(replay_payload["failure"]["case"], payload["failure"]["case"])
                self.assertEqual(replay_payload["failure"]["name"], check_name)

    def test_invalid_adapter_option_exits_two(self) -> None:
        completed = invoke("--mutation", "unknown")
        self.assertEqual(completed.returncode, 2, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("unknown mutation", payload["error"])

    def test_mutating_target_cannot_erase_oracle_input_or_failure_artifact(self) -> None:
        completed = self.run_fixture(
            BASE_ADAPTER + "\ndef evaluate(case):\n    case.clear()\n    return []\n"
        )
        self.assertEqual(completed.returncode, 1, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["failure"]["name"], "p")
        self.assertEqual(payload["failure"]["case"], [-2, -3, 2, -5, -3])

    def test_shared_result_buffer_is_snapshotted_before_follow_up(self) -> None:
        completed = self.run_fixture(
            BASE_ADAPTER.replace(
                "return [rng.randint(-9, 9) for _ in range(5)]", "return [1, 2, 3]"
            )
            + """
_buffer = []
def evaluate(case):
    _buffer.clear()
    _buffer.extend(case)
    return _buffer
"""
        )
        self.assertEqual(completed.returncode, 1, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["failure"]["name"], "r")
        self.assertEqual(payload["failure"]["phase"], "metamorphic")

    def test_oracle_callbacks_cannot_rewrite_failure_artifacts(self) -> None:
        completed = self.run_fixture(
            BASE_ADAPTER
            + """
def check_properties(case, result):
    case.clear()
    return [{"name": "p", "ok": True}]
def transformations(case):
    follow = list(reversed(case))
    case.clear()
    return [{"name": "reverse", "case": follow}]
def check_relation(name, case, result, follow, follow_result):
    case.clear()
    follow.clear()
    return [{"name": "r", "ok": False, "detail": "forced relation failure"}]
"""
        )
        self.assertEqual(completed.returncode, 1, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["failure"]["case"], [-2, -3, 2, -5, -3])
        self.assertEqual(payload["failure"]["follow_up"], [-3, -5, 2, -3, -2])

    def test_mutation_then_exception_emits_strict_json_with_original_case(self) -> None:
        completed = self.run_fixture(
            BASE_ADAPTER
            + """
def evaluate(case):
    case.append(float("nan"))
    raise RuntimeError("failure")
"""
        )
        self.assertEqual(completed.returncode, 1, completed.stderr or completed.stdout)
        self.assertNotIn("NaN", completed.stdout)
        payload = json.loads(completed.stdout, parse_constant=lambda value: self.fail(value))
        self.assertEqual(payload["failure"]["case"], [-2, -3, 2, -5, -3])

    def test_adapter_with_postponed_dataclass_annotations_loads(self) -> None:
        completed = self.run_fixture(
            """
from __future__ import annotations
from dataclasses import dataclass
@dataclass
class Output:
    value: int
"""
            + BASE_ADAPTER
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_follow_up_exception_is_a_stable_contract_failure(self) -> None:
        completed = self.run_fixture(
            BASE_ADAPTER.replace(
                "return [rng.randint(-9, 9) for _ in range(5)]", "return [1, 2, 3]"
            )
            + """
def evaluate(case):
    if case == [3, 2, 1]:
        case.append(float("nan"))
        raise RuntimeError("follow-up failed")
    return sorted(case)
"""
        )
        self.assertEqual(completed.returncode, 1, completed.stderr or completed.stdout)
        self.assertNotIn("NaN", completed.stdout)
        payload = json.loads(completed.stdout, parse_constant=lambda value: self.fail(value))
        self.assertEqual(payload["failure"]["phase"], "metamorphic")
        self.assertEqual(payload["failure"]["case"], [1, 2, 3])
        self.assertEqual(payload["failure"]["follow_up"], [3, 2, 1])

    def test_noncopyable_result_fails_closed(self) -> None:
        completed = self.run_fixture(
            BASE_ADAPTER
            + """
class NonCopyable:
    def __deepcopy__(self, memo):
        raise TypeError("cannot copy")
def evaluate(case):
    return NonCopyable()
"""
        )
        self.assertEqual(completed.returncode, 2, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("must support defensive copying", payload["error"])

    def test_malformed_contract_branches_fail_closed(self) -> None:
        fixtures = {
            "empty oracles": BASE_ADAPTER.replace(
                'ORACLES = {"p": "Result equals an independent sort", "r": "Reversal preserves sorting"}',
                "ORACLES = {}",
            ),
            "blank oracle rationale": BASE_ADAPTER.replace(
                '"Result equals an independent sort"', '""'
            ),
            "non-string oracle name": BASE_ADAPTER.replace(
                'ORACLES = {"p": "Result equals an independent sort", "r": "Reversal preserves sorting"}',
                'ORACLES = {1: "Result equals an independent sort", "r": "Reversal preserves sorting"}',
            ),
            "empty properties": BASE_ADAPTER.replace(
                'return [{"name": "p", "ok": result == sorted(case), "detail": "wrong sort"}]',
                "return []",
            ),
            "string boolean": BASE_ADAPTER.replace(
                '"ok": result == sorted(case)', '"ok": "false"'
            ),
            "nonmapping property check": BASE_ADAPTER.replace(
                'return [{"name": "p", "ok": result == sorted(case), "detail": "wrong sort"}]',
                "return [False]",
            ),
            "unknown property check": BASE_ADAPTER.replace(
                '"name": "p"', '"name": "unknown"'
            ),
            "invalid check detail": BASE_ADAPTER.replace(
                '"detail": "wrong sort"', '"detail": 7'
            ),
            "noniterable properties": BASE_ADAPTER.replace(
                'return [{"name": "p", "ok": result == sorted(case), "detail": "wrong sort"}]',
                "return None",
            ),
            "empty transformations": BASE_ADAPTER.replace(
                'return [{"name": "reverse", "case": list(reversed(case))}]',
                "return []",
            ),
            "malformed transformation": BASE_ADAPTER.replace(
                'return [{"name": "reverse", "case": list(reversed(case))}]',
                'return [{"name": "reverse"}]',
            ),
            "noniterable transformations": BASE_ADAPTER.replace(
                'return [{"name": "reverse", "case": list(reversed(case))}]',
                "return None",
            ),
            "empty relation checks": BASE_ADAPTER.replace(
                'return [{"name": "r", "ok": result == follow_result, "detail": "order changed result"}]',
                "return []",
            ),
            "noniterable relation checks": BASE_ADAPTER.replace(
                'return [{"name": "r", "ok": result == follow_result, "detail": "order changed result"}]',
                "return None",
            ),
            "nonfinite source": BASE_ADAPTER.replace(
                "return [rng.randint(-9, 9) for _ in range(5)]", 'return [float("nan")]'
            ),
            "nonfinite follow-up": BASE_ADAPTER.replace(
                'return [{"name": "reverse", "case": list(reversed(case))}]',
                'return [{"name": "reverse", "case": [float("inf")]}]',
            ),
        }
        for name, source in fixtures.items():
            with self.subTest(name=name):
                completed = self.run_fixture(source)
                self.assertEqual(completed.returncode, 2, completed.stderr or completed.stdout)
                self.assertEqual(json.loads(completed.stdout)["status"], "error")


if __name__ == "__main__":
    unittest.main()
