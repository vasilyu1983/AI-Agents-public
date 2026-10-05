"""Mode-collapse metric.

Two signals:

- **Within-prompt variance**: same prompt run N times. With temperature=0
  this should be ~0. With temperature>0 it should be > 0. A within-prompt
  variance of 0 at temperature>0 is a config bug, not mode collapse.

- **Cross-prompt variance**: structurally different prompts. Their
  responses should be structurally different. If two unrelated prompts
  produce highly similar responses, that is the mode-collapse signal.

We use Jaccard distance over token sets as the cheap, transparent metric.
Embedding-based metrics catch more subtle collapse but require an
embedding provider; not worth the dep for a smoke-grade suite.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import combinations


@dataclass
class VarianceResult:
    cross_prompt_pairs: int
    cross_prompt_mean_distance: float
    """Average Jaccard distance across distinct prompt pairs. 0 = identical
    responses; 1 = no token overlap."""

    cross_prompt_min_distance: float
    """Minimum Jaccard distance across distinct prompt pairs — the
    closest-twins signal. Mode collapse usually shows here first."""

    flagged_pairs: list[tuple[str, str, float]] = field(default_factory=list)
    """Prompt pairs whose responses are too similar (below the floor)."""


def jaccard_distance(a: str, b: str) -> float:
    """1 − |A ∩ B| / |A ∪ B| over normalized word sets. Two empty inputs
    are identical, so the distance is 0.0: an LLM that returns "" for
    every prompt must trip the similarity floor, not pass as "diverse"."""
    sa, sb = _tokens(a), _tokens(b)
    union = sa | sb
    if not union:
        return 0.0
    return 1.0 - len(sa & sb) / len(union)


def cross_prompt_variance(
    prompt_to_response: dict[str, str],
    *,
    similarity_floor: float = 0.4,
) -> VarianceResult:
    """Compute pairwise Jaccard distances across distinct prompts.

    `similarity_floor` is the minimum acceptable distance — pairs below
    it are flagged. 0.4 is a permissive default; tighten as the dataset
    gets larger and more diverse.
    """
    items = list(prompt_to_response.items())
    distances: list[float] = []
    flagged: list[tuple[str, str, float]] = []
    for (p1, r1), (p2, r2) in combinations(items, 2):
        d = jaccard_distance(r1, r2)
        distances.append(d)
        if d < similarity_floor:
            flagged.append((p1, p2, d))
    if not distances:
        return VarianceResult(0, 0.0, 0.0, [])
    return VarianceResult(
        cross_prompt_pairs=len(distances),
        cross_prompt_mean_distance=sum(distances) / len(distances),
        cross_prompt_min_distance=min(distances),
        flagged_pairs=flagged,
    )


_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall((text or "").lower()))
