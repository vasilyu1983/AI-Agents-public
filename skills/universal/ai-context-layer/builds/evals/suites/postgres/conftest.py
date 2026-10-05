"""Env-gated fixtures for the Postgres suite.

Set POSTGRES_DSN to run these tests. Without it, the suite is skipped at
collection time so CI on machines without Postgres still passes the smoke
suite cleanly.

Each test gets a fresh transaction that rolls back on teardown — no test
leaves state behind.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

POSTGRES_DSN = os.environ.get("POSTGRES_DSN")
SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "reference_app"
    / "adapters"
    / "migrations"
    / "0001_initial.sql"
)


_HERE = Path(__file__).resolve().parent


def pytest_collection_modifyitems(config, items):
    """Skip only items inside this suite directory. `pytest_collection_modifyitems`
    is a session-level hook even when defined in a subdir conftest, so we must
    scope the skip ourselves or it will leak to sibling suites."""
    if POSTGRES_DSN:
        return
    skip = pytest.mark.skip(reason="POSTGRES_DSN not set; Postgres suite skipped")
    for item in items:
        try:
            item_path = Path(item.path).resolve()
        except AttributeError:
            item_path = Path(str(item.fspath)).resolve()
        if _HERE in item_path.parents or item_path == _HERE:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def _ensure_schema():
    if not POSTGRES_DSN:
        pytest.skip("POSTGRES_DSN not set")
    import psycopg
    with psycopg.connect(POSTGRES_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text())
        conn.commit()
    return True


@pytest.fixture
def conn(_ensure_schema):
    """Per-test connection wrapped in a savepoint that rolls back on teardown."""
    import psycopg
    with psycopg.connect(POSTGRES_DSN) as c:
        c.execute("BEGIN")
        try:
            yield c
        finally:
            c.rollback()
