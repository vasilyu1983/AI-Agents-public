"""Example adapter for property_contract_runner.py; uses only the standard library."""

from __future__ import annotations

import json
import random
from decimal import Decimal
from typing import Any


ORACLES = {
    "calculator_exact_product": (
        "Decimal multiplication is the executable business specification for a unit price "
        "times a positive integer quantity."
    ),
    "calculator_quantity_scaling": (
        "Multiplying quantity by k must multiply the unrounded line total by the same k."
    ),
    "parser_matches_declared_fields": (
        "The generated expected mapping is independent of the parser under test."
    ),
    "parser_representation_equivalence": (
        "Reordering unique keys and changing insignificant spaces preserves config meaning."
    ),
    "serialization_round_trip": (
        "JSON's supported scalar, list, and object values must survive encode then decode."
    ),
    "serialization_key_order_equivalence": (
        "Object key insertion order does not change the decoded JSON value."
    ),
}

_MUTATION: str | None = None
_CONFIG_KEYS = ("host", "mode", "region", "retries", "label", "token_hint")
_CONFIG_VALUES = ("", "prod", "eu-west", "0", "3", "hello world", "UPPER")


def configure_mutation(name: str) -> None:
    allowed = {
        "calculator-add-unit",
        "parser-drop-last-field",
        "parser-space-sensitive",
        "serialization-stringify-scalars",
    }
    if name not in allowed:
        raise ValueError(f"unknown mutation {name!r}; choose one of {sorted(allowed)}")
    global _MUTATION
    _MUTATION = name


def _json_value(rng: random.Random, depth: int = 0) -> Any:
    scalars = [None, True, False, rng.randint(-1000, 1000), f"text {rng.randint(0, 99)}"]
    if depth >= 2:
        return rng.choice(scalars)
    choice = rng.randrange(3)
    if choice == 0:
        return rng.choice(scalars)
    if choice == 1:
        return [_json_value(rng, depth + 1) for _ in range(rng.randint(0, 4))]
    keys = rng.sample(_CONFIG_KEYS, rng.randint(0, 4))
    return {key: _json_value(rng, depth + 1) for key in keys}


def generate(rng: random.Random) -> dict[str, Any]:
    kind = rng.choice(("calculator", "config_parser", "serialization"))
    if kind == "calculator":
        # Cents include fractional prices below 1.00; quantity is a separate unit count.
        unit_cents = rng.randint(1, 99_999)
        quantity = rng.randint(1, 100)
        return {
            "kind": kind,
            "unit_price": f"{Decimal(unit_cents) / 100:.2f}",
            "quantity": quantity,
            "scale": rng.randint(2, 5),
        }
    if kind == "config_parser":
        keys = rng.sample(_CONFIG_KEYS, rng.randint(1, len(_CONFIG_KEYS)))
        fields = {key: rng.choice(_CONFIG_VALUES) for key in keys}
        lines = [f"{key}={value}" for key, value in fields.items()]
        return {"kind": kind, "fields": fields, "text": "\n".join(lines)}
    keys = rng.sample(_CONFIG_KEYS, rng.randint(1, 4))
    value = {key: _json_value(rng, 1) for key in keys}
    return {"kind": kind, "value": value}


def _parse_config(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    lines = text.splitlines()
    if _MUTATION == "parser-drop-last-field":
        lines = lines[:-1]
    for line in lines:
        key, value = line.split("=", 1)
        if _MUTATION == "parser-space-sensitive":
            parsed[key] = value
        else:
            parsed[key.strip()] = value.strip()
    return parsed


def _stringify_scalars(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _stringify_scalars(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_stringify_scalars(item) for item in value]
    return str(value)


def evaluate(case: dict[str, Any]) -> Any:
    if case["kind"] == "calculator":
        total = Decimal(case["unit_price"]) * case["quantity"]
        if _MUTATION == "calculator-add-unit":
            total += Decimal(case["unit_price"])
        return f"{total:.2f}"
    if case["kind"] == "config_parser":
        return _parse_config(case["text"])
    decoded = json.loads(json.dumps(case["value"], ensure_ascii=False, allow_nan=False))
    if _MUTATION == "serialization-stringify-scalars":
        decoded = _stringify_scalars(decoded)
    return decoded


def check_properties(case: dict[str, Any], result: Any) -> list[dict[str, Any]]:
    if case["kind"] == "calculator":
        expected = Decimal(case["unit_price"]) * case["quantity"]
        return [{
            "name": "calculator_exact_product",
            "ok": Decimal(result) == expected,
            "detail": f"expected {expected:.2f}, got {result}",
        }]
    if case["kind"] == "config_parser":
        return [{
            "name": "parser_matches_declared_fields",
            "ok": result == case["fields"],
            "detail": f"expected {case['fields']!r}, got {result!r}",
        }]
    return [{
        "name": "serialization_round_trip",
        "ok": result == case["value"],
        "detail": f"expected {case['value']!r}, got {result!r}",
    }]


def transformations(case: dict[str, Any]) -> list[dict[str, Any]]:
    if case["kind"] == "calculator":
        follow = dict(case)
        follow["quantity"] *= case["scale"]
        return [{"name": "scale_quantity", "case": follow}]
    if case["kind"] == "config_parser":
        lines = [f"  {key} = {value}  " for key, value in reversed(case["fields"].items())]
        follow = dict(case)
        follow["text"] = "\n".join(lines)
        return [{"name": "reorder_and_space", "case": follow}]
    value = dict(reversed(case["value"].items()))
    follow = {"kind": "serialization", "value": value}
    return [{"name": "reorder_object_keys", "case": follow}]


def check_relation(
    name: str,
    source_case: dict[str, Any],
    source_result: Any,
    follow_case: dict[str, Any],
    follow_result: Any,
) -> list[dict[str, Any]]:
    if name == "scale_quantity":
        expected = Decimal(source_result) * source_case["scale"]
        return [{
            "name": "calculator_quantity_scaling",
            "ok": Decimal(follow_result) == expected,
            "detail": f"expected scaled total {expected:.2f}, got {follow_result}",
        }]
    if name == "reorder_and_space":
        return [{
            "name": "parser_representation_equivalence",
            "ok": follow_result == source_result,
            "detail": f"source {source_result!r}, follow-up {follow_result!r}",
        }]
    if name == "reorder_object_keys":
        return [{
            "name": "serialization_key_order_equivalence",
            "ok": follow_result == source_result,
            "detail": f"source {source_result!r}, follow-up {follow_result!r}",
        }]
    raise ValueError(f"unknown transformation {name!r}")
