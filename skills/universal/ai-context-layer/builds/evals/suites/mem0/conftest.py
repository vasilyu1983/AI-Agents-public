"""Mem0 suite — gated on MEM0_API_KEY and the `mem0ai` SDK.

The hosted Mem0 service is the simplest path; for self-hosted, set
MEM0_API_KEY to anything truthy and override the client construction.
"""

from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
MEM0_API_KEY = os.environ.get("MEM0_API_KEY")

try:
    _mem0_mod = import_module("mem0")
    MEM0_AVAILABLE = True
except ImportError:
    _mem0_mod = None
    MEM0_AVAILABLE = False


def pytest_collection_modifyitems(config, items):
    if MEM0_AVAILABLE and MEM0_API_KEY:
        return
    reason = (
        "MEM0_API_KEY not set" if MEM0_AVAILABLE else "mem0 SDK not installed"
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
def mem0_client():
    if not (MEM0_AVAILABLE and MEM0_API_KEY):
        pytest.skip("Mem0 unavailable")
    # MemoryClient is the hosted client; swap for `Memory()` if self-hosting.
    return _mem0_mod.MemoryClient(api_key=MEM0_API_KEY)
