"""Env-gated fixtures for the mode-collapse suite.

Same gating shape as context_rot: skip cleanly without ANTHROPIC_API_KEY,
and bound total token spend with MODE_COLLAPSE_MAX_TOKENS.
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

    model = os.environ.get("MODE_COLLAPSE_MODEL", "claude-haiku-4-5")
    # Slight temperature so within-prompt variance > 0; cross-prompt
    # variance is the actually-interesting signal.
    return AnthropicLLM(model=model, temperature=0.4)


@pytest.fixture(scope="session")
def prompts() -> list[dict]:
    return [json.loads(line) for line in DATASET.read_text().splitlines() if line.strip()]


@pytest.fixture(scope="session")
def similarity_floor() -> float:
    return float(os.environ.get("MODE_COLLAPSE_FLOOR", "0.4"))
