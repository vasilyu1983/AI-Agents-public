"""Human-readable rollup for the failure-mode-keyed eval suites.

Plain text on purpose — these reports show up in CI logs and pytest
captures, not in a UI. Optimize for grep, not for color.
"""

from __future__ import annotations

from ..metrics import RotResult, VarianceResult


def render_rot(result: RotResult, max_failures: int = 5) -> str:
    lines = ["[context-rot rollup]"]
    for tier in sorted(result.pass_rate_per_tier):
        rate = result.pass_rate_per_tier[tier]
        n = result.n_per_tier[tier]
        bar = "#" * int(rate * 20)
        lines.append(f"  tier ~{tier:>6} tok  {rate:>5.1%}  ({n}) {bar}")
    lines.append(f"  degradation (lowest → highest): {result.degradation():+.2%}")
    if result.failures:
        lines.append(f"  {len(result.failures)} failed cases (showing up to {max_failures}):")
        for f in result.failures[:max_failures]:
            lines.append(
                f"    - case={f['case_id']} tier={f['tier']} "
                f"expected={_short(f.get('expected'))!r} actual={_short(f.get('actual'))!r}"
            )
    return "\n".join(lines)


def render_mode_collapse(result: VarianceResult, max_pairs: int = 5) -> str:
    lines = ["[mode-collapse rollup]"]
    lines.append(f"  cross-prompt pairs evaluated: {result.cross_prompt_pairs}")
    lines.append(f"  mean Jaccard distance:         {result.cross_prompt_mean_distance:.3f}")
    lines.append(f"  min  Jaccard distance:         {result.cross_prompt_min_distance:.3f}")
    if result.flagged_pairs:
        lines.append(
            f"  {len(result.flagged_pairs)} flagged pairs (too similar; showing up to {max_pairs}):"
        )
        for p1, p2, d in result.flagged_pairs[:max_pairs]:
            lines.append(f"    - d={d:.2f}  '{_short(p1, 60)}'  ↔  '{_short(p2, 60)}'")
    return "\n".join(lines)


def _short(text, n: int = 80) -> str:
    text = "" if text is None else str(text)
    return text if len(text) <= n else text[: n - 1] + "…"
