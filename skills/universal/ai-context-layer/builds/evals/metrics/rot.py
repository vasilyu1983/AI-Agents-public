"""Context-rot metric.

The needle-in-haystack pattern: each case has a question with a known
correct answer hidden inside a small block of relevant text. We pad the
prompt with increasing amounts of distractor text and measure how
instruction-following degrades.

Pass criteria (defaults; override per suite):
- pass rate at the lowest tier ≥ 0.95
- pass rate at each higher tier ≥ 0.85 × pass rate at the lowest tier
- degradation must be monotonic non-increasing across tiers (small
  bounce within ±0.05 tolerated)

A failing run usually means one of:
- F2 (distraction) — the model loses focus past a budget the assembly
  layer should have caught.
- F4 (confusion) — irrelevant content crowds the answer out.
- The compress verb is dropping load-bearing content.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RotResult:
    pass_rate_per_tier: dict[int, float]
    """Mapping of token-tier (approx prompt size) → pass rate in [0, 1]."""

    n_per_tier: dict[int, int]
    """Mapping of token-tier → number of cases evaluated at that tier."""

    failures: list[dict] = field(default_factory=list)
    """One record per failed case for human review."""

    def degradation(self) -> float:
        """Drop in pass rate from the smallest to the largest tier.
        Positive numbers mean degradation (worse at large context)."""
        if not self.pass_rate_per_tier:
            return 0.0
        tiers = sorted(self.pass_rate_per_tier)
        return self.pass_rate_per_tier[tiers[0]] - self.pass_rate_per_tier[tiers[-1]]

    def is_monotonic_non_increasing(self, tolerance: float = 0.05) -> bool:
        """True if pass rate never bounces up by more than `tolerance`
        as the tier grows. Small upward bounces are tolerated because
        the dataset is finite and noisy."""
        rates = [self.pass_rate_per_tier[t] for t in sorted(self.pass_rate_per_tier)]
        return all(rates[i + 1] <= rates[i] + tolerance for i in range(len(rates) - 1))


def pass_rate_per_tier(case_results: list[dict]) -> RotResult:
    """Roll a list of per-case results into a RotResult.

    Each case result is a dict with at least:
        {
            "tier": int,           # approx prompt token count
            "passed": bool,
            "case_id": str,
            "expected": str,       # for failure rendering
            "actual": str,
        }
    """
    tier_pass: dict[int, list[bool]] = {}
    failures: list[dict] = []
    for r in case_results:
        tier_pass.setdefault(r["tier"], []).append(bool(r["passed"]))
        if not r["passed"]:
            failures.append({
                "case_id": r.get("case_id"),
                "tier": r["tier"],
                "expected": r.get("expected"),
                "actual": r.get("actual"),
            })
    pr = {t: sum(v) / len(v) for t, v in tier_pass.items()}
    n = {t: len(v) for t, v in tier_pass.items()}
    return RotResult(pass_rate_per_tier=pr, n_per_tier=n, failures=failures)


def evaluate_rot(
    result: RotResult,
    *,
    floor: float = 0.95,
    relative_floor: float = 0.85,
    tolerance: float = 0.05,
) -> dict[str, bool | str]:
    """Apply the default pass criteria. Returns a dict suitable for an
    assert message."""
    if not result.pass_rate_per_tier:
        return {"ok": False, "reason": "no tiers evaluated"}
    tiers = sorted(result.pass_rate_per_tier)
    base = result.pass_rate_per_tier[tiers[0]]
    if base < floor:
        return {"ok": False, "reason": f"baseline tier {tiers[0]} failed: {base:.2f} < {floor}"}
    for t in tiers[1:]:
        rate = result.pass_rate_per_tier[t]
        if rate < relative_floor * base:
            return {
                "ok": False,
                "reason": (
                    f"tier {t} regressed below relative floor: "
                    f"{rate:.2f} < {relative_floor * base:.2f}"
                ),
            }
    if not result.is_monotonic_non_increasing(tolerance=tolerance):
        return {"ok": False, "reason": "non-monotonic degradation curve"}
    return {"ok": True, "reason": "ok"}
