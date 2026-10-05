"""LangGraph Store suite — runs without external credentials.

Uses LangGraph's `InMemoryStore` if `langgraph` is importable. If the
package is absent, the suite is skipped at collection time so smoke and
sibling suites still run cleanly.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent

try:
    _store_mod = import_module("langgraph.store.memory")
    LANGGRAPH_AVAILABLE = True
except ImportError:
    _store_mod = None
    LANGGRAPH_AVAILABLE = False


def pytest_collection_modifyitems(config, items):
    if LANGGRAPH_AVAILABLE:
        return
    skip = pytest.mark.skip(reason="langgraph not installed; suite skipped")
    for item in items:
        try:
            item_path = Path(item.path).resolve()
        except AttributeError:
            item_path = Path(str(item.fspath)).resolve()
        if _HERE in item_path.parents or item_path == _HERE:
            item.add_marker(skip)


@pytest.fixture
def store():
    if not LANGGRAPH_AVAILABLE:
        pytest.skip("langgraph not installed")
    return _store_mod.InMemoryStore()
