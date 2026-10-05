"""Cognee suite — gated on COGNEE_LLM_API_KEY and the `cognee` SDK.

Cognee runs locally but needs an LLM provider key for `cognify` to
extract the knowledge graph.
"""

from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
COGNEE_LLM_API_KEY = os.environ.get("COGNEE_LLM_API_KEY") or os.environ.get(
    "OPENAI_API_KEY"
)

try:
    _cognee_mod = import_module("cognee")
    COGNEE_AVAILABLE = True
except ImportError:
    _cognee_mod = None
    COGNEE_AVAILABLE = False


def pytest_collection_modifyitems(config, items):
    if COGNEE_AVAILABLE and COGNEE_LLM_API_KEY:
        return
    reason = (
        "COGNEE_LLM_API_KEY (or OPENAI_API_KEY) not set"
        if COGNEE_AVAILABLE
        else "cognee SDK not installed"
    )
    skip = pytest.mark.skip(reason=f"{reason}; suite skipped")
    for item in items:
        try:
            item_path = Path(item.path).resolve()
        except AttributeError:
            item_path = Path(str(item.fspath)).resolve()
        if _HERE in item_path.parents or item_path == _HERE:
            item.add_marker(skip)


@pytest.fixture
def cognee_module():
    if not (COGNEE_AVAILABLE and COGNEE_LLM_API_KEY):
        pytest.skip("Cognee unavailable")
    return _cognee_mod
