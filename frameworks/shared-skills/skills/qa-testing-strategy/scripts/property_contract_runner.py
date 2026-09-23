#!/usr/bin/env python3
"""Run a portable property and metamorphic test contract with deterministic replay."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import random
import shlex
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Mapping


REQUIRED_CALLABLES = (
    "generate",
    "evaluate",
    "check_properties",
    "transformations",
    "check_relation",
)


class AdapterError(ValueError):
    """The contract adapter does not implement the documented protocol."""


def load_adapter(path: Path) -> ModuleType:
    if not path.is_file():
        raise AdapterError(f"contract file does not exist: {path}")
    spec = importlib.util.spec_from_file_location("property_contract_adapter", path)
    if spec is None or spec.loader is None:
        raise AdapterError(f"cannot load contract: {path}")
    module = importlib.util.module_from_spec(spec)
    previous_module = sys.modules.get(spec.name)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        for name in REQUIRED_CALLABLES:
            if not callable(getattr(module, name, None)):
                raise AdapterError(f"contract must define callable {name}()")
        oracles = getattr(module, "ORACLES", None)
        if not isinstance(oracles, Mapping) or not oracles:
            raise AdapterError("contract must define a non-empty ORACLES mapping")
        for name, rationale in oracles.items():
            if not isinstance(name, str) or not name.strip():
                raise AdapterError("ORACLES names must be non-empty strings")
            if not isinstance(rationale, str) or not rationale.strip():
                raise AdapterError(f"ORACLES[{name!r}] must explain the independent oracle")
    except Exception:
        if previous_module is None:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = previous_module
        raise
    return module


def json_safe(value: Any, label: str) -> Any:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise AdapterError(f"{label} must be finite, JSON-serializable data: {exc}") from exc
    return value


def isolated_copy(value: Any, label: str) -> Any:
    try:
        return copy.deepcopy(value)
    except Exception as exc:
        raise AdapterError(f"{label} must support defensive copying: {exc}") from exc


def case_snapshot(value: Any, label: str) -> Any:
    snapshot = isolated_copy(value, label)
    return json_safe(snapshot, label)


def normalize_checks(
    checks: Iterable[Mapping[str, Any]], oracles: Mapping[str, str], label: str
) -> list[dict[str, Any]]:
    try:
        items = list(checks)
    except TypeError as exc:
        raise AdapterError(f"{label} must return an iterable of check mappings") from exc
    if not items:
        raise AdapterError(f"{label} must return at least one check")

    normalized = []
    for check in items:
        if not isinstance(check, Mapping):
            raise AdapterError(f"{label} returned a non-mapping check")
        name = check.get("name")
        ok = check.get("ok")
        detail = check.get("detail", "")
        if not isinstance(name, str) or name not in oracles:
            raise AdapterError(f"check name {name!r} has no entry in ORACLES")
        if type(ok) is not bool:
            raise AdapterError(f"check {name!r} must use a boolean ok value")
        if not isinstance(detail, str):
            raise AdapterError(f"check {name!r} detail must be a string")
        normalized.append({"name": name, "ok": ok, "detail": detail})
    return normalized


def normalize_transformations(items: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    try:
        transformations = list(items)
    except TypeError as exc:
        raise AdapterError("transformations() must return an iterable of mappings") from exc
    if not transformations:
        raise AdapterError("transformations() must return at least one follow-up case")
    normalized = []
    for item in transformations:
        if not isinstance(item, Mapping):
            raise AdapterError("transformations() returned a non-mapping item")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip() or "case" not in item:
            raise AdapterError("each transformation needs a non-empty name and a case")
        normalized.append({"name": name, "case": case_snapshot(item["case"], "follow-up case")})
    return normalized


def replay_command(args: argparse.Namespace, case_index: int) -> str:
    parts = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--contract",
        str(args.contract.resolve()),
        "--seed",
        str(args.seed),
        "--case-index",
        str(case_index),
        "--json",
    ]
    if args.mutation:
        parts.extend(["--mutation", args.mutation])
    return shlex.join(parts)


def failure_result(
    args: argparse.Namespace,
    *,
    case_index: int,
    cases_run: int,
    checks_run: int,
    phase: str,
    name: str,
    oracle: str,
    detail: str,
    case: Any,
    follow_up: Any = None,
    transformation: str | None = None,
) -> dict[str, Any]:
    return {
        "status": "fail",
        "contract": str(args.contract.resolve()),
        "seed": args.seed,
        "cases_requested": 1 if args.case_index is not None else args.cases,
        "cases_run": cases_run,
        "checks_run": checks_run,
        "failure": {
            "case_index": case_index,
            "phase": phase,
            "name": name,
            "oracle": oracle,
            "detail": detail,
            "case": case,
            "transformation": transformation,
            "follow_up": follow_up,
        },
        "replay_command": replay_command(args, case_index),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    adapter = load_adapter(args.contract.resolve())
    oracles: Mapping[str, str] = dict(adapter.ORACLES)
    if args.mutation:
        configure = getattr(adapter, "configure_mutation", None)
        if not callable(configure):
            raise AdapterError("--mutation requires adapter.configure_mutation(name)")
        configure(args.mutation)

    rng = random.Random(args.seed)
    target_indexes = (
        {args.case_index} if args.case_index is not None else set(range(args.cases))
    )
    generation_limit = args.case_index + 1 if args.case_index is not None else args.cases
    cases_run = 0
    checks_run = 0

    for case_index in range(generation_limit):
        case = case_snapshot(adapter.generate(rng), "generated case")
        if case_index not in target_indexes:
            continue
        cases_run += 1
        try:
            result = isolated_copy(
                adapter.evaluate(isolated_copy(case, "generated case")),
                "evaluation result",
            )
            checks = normalize_checks(
                adapter.check_properties(
                    isolated_copy(case, "generated case"),
                    isolated_copy(result, "evaluation result"),
                ),
                oracles,
                "check_properties()",
            )
        except AdapterError:
            raise
        except Exception as exc:  # A valid generated input crashing is a test failure.
            return failure_result(
                args,
                case_index=case_index,
                cases_run=cases_run,
                checks_run=checks_run,
                phase="property",
                name="execution_without_exception",
                oracle="Every generated case is in-domain and must execute without exception.",
                detail=f"{type(exc).__name__}: {exc}",
                case=case,
            )
        for check in checks:
            checks_run += 1
            if not check["ok"]:
                return failure_result(
                    args,
                    case_index=case_index,
                    cases_run=cases_run,
                    checks_run=checks_run,
                    phase="property",
                    name=check["name"],
                    oracle=oracles[check["name"]],
                    detail=check["detail"],
                    case=case,
                )

        transformations = normalize_transformations(
            adapter.transformations(isolated_copy(case, "generated case"))
        )
        for transformation in transformations:
            follow_case = transformation["case"]
            try:
                follow_result = isolated_copy(
                    adapter.evaluate(isolated_copy(follow_case, "follow-up case")),
                    "follow-up evaluation result",
                )
                relation_checks = normalize_checks(
                    adapter.check_relation(
                        transformation["name"],
                        isolated_copy(case, "generated case"),
                        isolated_copy(result, "evaluation result"),
                        isolated_copy(follow_case, "follow-up case"),
                        isolated_copy(follow_result, "follow-up evaluation result"),
                    ),
                    oracles,
                    "check_relation()",
                )
            except AdapterError:
                raise
            except Exception as exc:
                return failure_result(
                    args,
                    case_index=case_index,
                    cases_run=cases_run,
                    checks_run=checks_run,
                    phase="metamorphic",
                    name="execution_without_exception",
                    oracle="Every generated follow-up is in-domain and must execute without exception.",
                    detail=f"{type(exc).__name__}: {exc}",
                    case=case,
                    follow_up=follow_case,
                    transformation=transformation["name"],
                )
            for check in relation_checks:
                checks_run += 1
                if not check["ok"]:
                    return failure_result(
                        args,
                        case_index=case_index,
                        cases_run=cases_run,
                        checks_run=checks_run,
                        phase="metamorphic",
                        name=check["name"],
                        oracle=oracles[check["name"]],
                        detail=check["detail"],
                        case=case,
                        follow_up=follow_case,
                        transformation=transformation["name"],
                    )

    return {
        "status": "pass",
        "contract": str(args.contract.resolve()),
        "seed": args.seed,
        "cases_requested": 1 if args.case_index is not None else args.cases,
        "cases_run": cases_run,
        "checks_run": checks_run,
        "failure": None,
        "replay_command": None,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run named property and metamorphic oracles against a Python adapter."
    )
    parser.add_argument("--contract", required=True, type=Path, help="adapter Python file")
    parser.add_argument("--seed", type=int, default=20260908)
    parser.add_argument("--cases", type=int, default=100)
    parser.add_argument("--case-index", type=int)
    parser.add_argument("--mutation", help="optional adapter negative-control mutation")
    parser.add_argument("--json", action="store_true", help="emit one JSON object")
    args = parser.parse_args(argv)
    if args.cases < 1:
        parser.error("--cases must be at least 1")
    if args.case_index is not None and args.case_index < 0:
        parser.error("--case-index must be zero or greater")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        result = {
            "status": "error",
            "contract": str(args.contract.resolve()),
            "seed": args.seed,
            "error": f"{type(exc).__name__}: {exc}",
        }
        exit_code = 2
    else:
        exit_code = 0 if result["status"] == "pass" else 1

    if args.json:
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    elif exit_code == 0:
        print(
            f"PASS: {result['cases_run']} cases, {result['checks_run']} checks "
            f"(seed {result['seed']})"
        )
    elif exit_code == 1:
        failure = result["failure"]
        print(f"FAIL: {failure['phase']} check {failure['name']} — {failure['detail']}")
        print(f"Replay: {result['replay_command']}")
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
