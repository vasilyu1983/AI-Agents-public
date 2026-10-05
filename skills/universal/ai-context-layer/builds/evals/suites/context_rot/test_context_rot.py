"""Context-rot regression test.

For each case in the dataset, build prompts at five token tiers (≈300,
2k, 8k, 32k, 96k tokens) by surrounding a single needle sentence with
varying amounts of distractor text. Ask the model the needle's question
at each tier. Score:

- pass = expected answer appears (case-insensitive substring) in the
  model's first sentence of response
- the suite as a whole passes only if `evaluate_rot` returns ok=True
  (see metrics/rot.py for the criteria)

A failure here means one of:
- The model's instruction-following is degrading at moderate context
- The compress verb is dropping load-bearing content
- The model has been swapped for a smaller one without updating the floor
"""

from __future__ import annotations

import random
from collections.abc import Iterable

import pytest

from evals.metrics import evaluate_rot, pass_rate_per_tier
from evals.reports import render_rot

# Token tiers ≈ chars/4 (matches AnthropicLLM.count_tokens approximation).
# Tiers chosen to span the typical "context rot kicks in" range; extend
# upward only if you've raised the model context window in app config.
TIERS = [300, 2_000, 8_000, 32_000, 96_000]

# Distractor sentences — neutral, parseable, no embedded questions.
_DISTRACTORS = [
    "The maintenance window opens at 02:00 UTC and closes at 04:00 UTC each Sunday.",
    "Quarterly cost reports are circulated to all department heads on the first Monday of each quarter.",
    "Standard meeting cadence is biweekly with an alternating focus on planning and retro.",
    "Documentation should follow the project style guide and pass the linter on every commit.",
    "External vendor reviews follow a structured intake form and a security questionnaire.",
    "Onboarding sessions cover access provisioning, code conventions, and the deployment pipeline.",
    "Incident response drills are scheduled quarterly and rotate across regional teams.",
    "The shared knowledge base is updated by the documentation working group each fortnight.",
    "Service-level objectives target 99.95% availability across the primary read path.",
    "Build pipelines run unit tests, type checks, and a security scan on every pull request.",
]


def _build_prompt(needle: str, target_tokens: int) -> str:
    """Build a prompt of approximately `target_tokens` tokens by padding
    around the needle. Needle is placed at ~60% depth — the empirical
    worst-case position for long-context recall."""
    rng = random.Random(target_tokens)
    target_chars = target_tokens * 4
    body_chars = max(0, target_chars - len(needle))
    pre_chars = int(body_chars * 0.6)
    post_chars = body_chars - pre_chars
    pre = _pad_to(rng, pre_chars)
    post = _pad_to(rng, post_chars)
    return f"{pre}\n\n{needle}\n\n{post}"


def _pad_to(rng: random.Random, target_chars: int) -> str:
    if target_chars <= 0:
        return ""
    out: list[str] = []
    total = 0
    while total < target_chars:
        s = rng.choice(_DISTRACTORS)
        out.append(s)
        total += len(s) + 1
    return " ".join(out)[:target_chars]


def _ask(llm, document: str, question: str, tokens_used: list[int]) -> str:
    system = (
        "You answer questions about the provided DOCUMENT. Use only the "
        "DOCUMENT, not outside knowledge. Reply with one short sentence."
    )
    user = f"DOCUMENT:\n{document}\n\nQUESTION: {question}\n\nANSWER:"
    tokens_used.append(len(document) // 4)
    return llm.complete(
        system=system,
        messages=[{"role": "user", "content": user}],
        max_tokens=80,
    )


def _passed(answer: str, expected: str) -> bool:
    return expected.lower() in (answer or "").lower()


def test_context_rot_does_not_regress(llm, cases, token_budget, capsys):
    """Run every case at every tier; assert the rot result clears the floor."""
    case_results: list[dict] = []
    tokens_used: list[int] = []
    for case in cases:
        for tier in TIERS:
            if sum(tokens_used) > token_budget:
                pytest.fail(
                    f"CONTEXT_ROT_MAX_TOKENS budget ({token_budget}) exhausted after "
                    f"{len(case_results)} case/tier runs; raise the budget or shrink "
                    "the dataset (a skip here would hide an unfinished sweep)"
                )
            doc = _build_prompt(case["needle"], tier)
            answer = _ask(llm, doc, case["question"], tokens_used)
            case_results.append({
                "case_id": case["case_id"],
                "tier": tier,
                "expected": case["expected"],
                "actual": answer,
                "passed": _passed(answer, case["expected"]),
            })

    result = pass_rate_per_tier(case_results)
    print("\n" + render_rot(result))
    verdict = evaluate_rot(result)
    assert verdict["ok"], verdict["reason"]


def test_token_estimate_matches_count_tokens(llm):
    """Sanity: the prompt builder's char/4 approximation should agree
    with the LLMClient.count_tokens approximation within a few percent.
    Catches a class of bug where the rot scaffolding silently overruns
    the budget."""
    sample = " ".join(_DISTRACTORS) * 50
    char_estimate = len(sample) // 4
    sdk_estimate = llm.count_tokens(sample)
    drift = abs(char_estimate - sdk_estimate) / max(char_estimate, 1)
    assert drift < 0.10, f"token-estimate drift {drift:.1%} > 10%; recalibrate"


def _last(it: Iterable[str]) -> str:
    last = ""
    for x in it:
        last = x
    return last
