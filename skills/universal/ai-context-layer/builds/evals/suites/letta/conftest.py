"""Letta suite — gated on LETTA_BASE_URL + LETTA_AGENT_ID + the `letta_client` SDK.

The adapter is agent-bound, so the test needs a pre-created agent ID.
Provision one in your Letta deployment and export it as LETTA_AGENT_ID.
"""

from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
LETTA_BASE_URL = os.environ.get("LETTA_BASE_URL")
LETTA_AGENT_ID = os.environ.get("LETTA_AGENT_ID")
LETTA_TOKEN = os.environ.get("LETTA_TOKEN")

try:
    _letta_mod = import_module("letta_client")
    LETTA_AVAILABLE = True
except ImportError:
    _letta_mod = None
    LETTA_AVAILABLE = False


def pytest_collection_modifyitems(config, items):
    if LETTA_AVAILABLE and LETTA_BASE_URL and LETTA_AGENT_ID:
        return
    reason = "letta_client + LETTA_BASE_URL + LETTA_AGENT_ID required"
    skip = pytest.mark.skip(reason=f"{reason}; suite skipped")
    for item in items:
        try:
            item_path = Path(item.path).resolve()
        except AttributeError:
            item_path = Path(str(item.fspath)).resolve()
        if _HERE in item_path.parents or item_path == _HERE:
            item.add_marker(skip)


@pytest.fixture
def letta_client():
    if not (LETTA_AVAILABLE and LETTA_BASE_URL and LETTA_AGENT_ID):
        pytest.skip("Letta unavailable")
    return _letta_mod.Letta(base_url=LETTA_BASE_URL, token=LETTA_TOKEN)


@pytest.fixture
def letta_agent_id():
    return LETTA_AGENT_ID
