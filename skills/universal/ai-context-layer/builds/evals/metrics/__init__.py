"""Eval metrics for context-layer regression detection.

Two failure-mode-keyed modules:

- `rot.py` — context rot: pass-rate degradation as token count grows.
- `variance.py` — mode collapse: response variance across diverse prompts.

Metrics are deliberately simple and inspectable. A test that fails should
make the cause obvious from the rollup, not require a debugger.
"""

from .rot import RotResult, evaluate_rot, pass_rate_per_tier
from .variance import VarianceResult, cross_prompt_variance, jaccard_distance

__all__ = [
    "RotResult",
    "VarianceResult",
    "cross_prompt_variance",
    "evaluate_rot",
    "jaccard_distance",
    "pass_rate_per_tier",
]
