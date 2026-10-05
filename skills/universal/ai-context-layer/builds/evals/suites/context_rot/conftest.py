"""Env-gated fixtures for the context-rot suite.

Skips the suite cleanly when ANTHROPIC_API_KEY is missing. Adds a hard
cost guard via CONTEXT_ROT_MAX_TOKENS (default 200_000 tokens for the
whole run) so an accidental large dataset cannot rack up a bill.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
HERE = Path(__file__).resolve().parent
DATASET = HERE / "dataset.jsonl"


# No collection-level skip — the `llm` fixture below skips tests that
# need the API key, while pure-metric tests still run without credentials.


@pytest.fixture(scope="session")
def llm():
    if not ANTHROPIC_API_KEY:
        pytest.skip("ANTHROPIC_API_KEY not set")
    from reference_app.adapters.anthropic_llm import AnthropicLLM

    model = os.environ.get("CONTEXT_ROT_MODEL", "claude-haiku-4-5")
    return AnthropicLLM(model=model, temperature=0.0)


@pytest.fixture(scope="session")
def cases() -> list[dict]:
    return [json.loads(line) for line in DATASET.read_text().splitlines() if line.strip()]


@pytest.fixture(scope="session")
def token_budget() -> int:
    return int(os.environ.get("CONTEXT_ROT_MAX_TOKENS", "200000"))
