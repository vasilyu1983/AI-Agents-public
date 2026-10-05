"""Supermemory suite — gated on SUPERMEMORY_API_KEY + SUPERMEMORY_BASE_URL + httpx."""

from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
SUPERMEMORY_API_KEY = os.environ.get("SUPERMEMORY_API_KEY")
SUPERMEMORY_BASE_URL = os.environ.get(
    "SUPERMEMORY_BASE_URL", "https://api.supermemory.ai"
)

try:
    _httpx = import_module("httpx")
    HTTPX_AVAILABLE = True
except ImportError:
    _httpx = None
    HTTPX_AVAILABLE = False


def pytest_collection_modifyitems(config, items):
    if HTTPX_AVAILABLE and SUPERMEMORY_API_KEY:
        return
    reason = (
        "SUPERMEMORY_API_KEY not set"
        if HTTPX_AVAILABLE
        else "httpx not installed"
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
def http_client():
    if not (HTTPX_AVAILABLE and SUPERMEMORY_API_KEY):
        pytest.skip("Supermemory unavailable")
    with _httpx.Client(timeout=30.0) as client:
        yield client


@pytest.fixture
def supermemory_config():
    return {"base_url": SUPERMEMORY_BASE_URL, "api_key": SUPERMEMORY_API_KEY}
