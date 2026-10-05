"""Mode-collapse regression test.

Run a small set of structurally diverse prompts once each, then compute
pairwise Jaccard distances over their responses. If two unrelated
prompts produce highly similar responses, the model (or the surrounding
context layer) is collapsing — flag the pair.

This is a *cross-prompt* check. Within-prompt collapse (same prompt, N
runs, identical output) is mostly a temperature config issue and is not
the mode-collapse signal we care about for context-layer regressions.

A failing run usually means:
- A26 has slipped through — the memory layer is re-ingesting model
  outputs as "preferences" and the agent is converging on one tone.
- The system prompt is over-specifying style and squeezing out content
  variance.
- The model itself was downgraded; revisit the floor.
"""

from __future__ import annotations

import pytest

from evals.metrics import cross_prompt_variance
from evals.reports import render_mode_collapse


SYSTEM = (
    "You are a helpful assistant. Answer concisely. Do not use a fixed "
    "structure or template — let the form follow the question."
)


def _ask(llm, prompt: str) -> str:
    return llm.complete(
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
    )


def test_responses_stay_diverse_across_prompts(llm, prompts, similarity_floor, capsys):
    responses: dict[str, str] = {}
    for case in prompts:
        responses[case["prompt"]] = _ask(llm, case["prompt"])

    result = cross_prompt_variance(responses, similarity_floor=similarity_floor)
    print("\n" + render_mode_collapse(result))

    assert result.cross_prompt_pairs > 0, "no pairs evaluated; dataset too small?"
    assert result.cross_prompt_min_distance >= similarity_floor, (
        f"cross-prompt min distance {result.cross_prompt_min_distance:.2f} below "
        f"floor {similarity_floor:.2f} — likely mode collapse. "
        f"Flagged pairs: {len(result.flagged_pairs)}"
    )


def test_jaccard_metric_smoke():
    """Sanity: identical strings → 0, disjoint strings → 1.
    Catches a class of bug where the metric returns the wrong sense."""
    from evals.metrics import jaccard_distance

    assert jaccard_distance("hello world", "hello world") == 0.0
    assert jaccard_distance("alpha beta", "gamma delta") == 1.0
    # Empty/empty is identical (0.0) so an all-empty response set fails the floor.
    assert jaccard_distance("", "") == 0.0
    assert jaccard_distance("", "alpha") == 1.0


def test_all_empty_responses_fail_the_floor():
    """Fail closed: a stub that answers "" everywhere must be flagged, not pass."""
    result = cross_prompt_variance({"p1": "", "p2": "", "p3": ""}, similarity_floor=0.4)
    assert result.cross_prompt_pairs == 3
    assert result.cross_prompt_min_distance == 0.0
    assert len(result.flagged_pairs) == 3
