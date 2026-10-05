# Quality Metrics and Dashboards

Quality signal definitions, release-readiness gating, and metric anti-patterns. Dashboard plumbing (collectors, Grafana/Datadog setup) is deliberately out of scope: emit JUnit XML from CI and chart the metrics below in whatever tool the team already runs.

## Contents

- [Core Quality Metrics](#core-quality-metrics)
- [Test Suite Health Metrics](#test-suite-health-metrics)
- [Release Readiness: Hard Gates Before Scoring](#release-readiness-hard-gates-before-scoring)
- [Operationalising Mutation Coverage](#operationalising-mutation-coverage)
- [Metric Anti-Patterns](#metric-anti-patterns)
- [Related Resources](#related-resources)

---

## Core Quality Metrics

### Primary Quality Indicators

| Metric | Formula | Target | Collection Source |
|--------|---------|--------|-------------------|
| **Defect Escape Rate** | Prod bugs / total bugs found | <10% | Defect tracker (Jira, Linear) |
| **Mean Time to Detect (MTTD)** | Avg time from defect introduction to detection | <24 hours | Git blame + bug report timestamps |
| **Test Pass Rate** | Passing tests / total tests | >98% | CI test reporters |
| **Flake Rate** | Runs whose outcome changed on the same commit with no code change (fail then pass) / total runs; track per test as well as suite-wide | <=1% weekly (practitioner default) | CI analytics, history-based flake detection |
| **Code Coverage (delta)** | Coverage change on PR | +/- 0% (no decrease) | Coverage tools (Istanbul, JaCoCo) |
| **Coverage Trend** | Coverage over time | Increasing or stable | Coverage history |

### Defect Escape Rate Calculation

```python
def defect_escape_rate(
    bugs_in_prod: int,
    bugs_in_staging: int,
    bugs_in_dev: int,
    bugs_in_code_review: int
) -> dict:
    """Calculate defect escape rate and detection distribution."""
    total = bugs_in_prod + bugs_in_staging + bugs_in_dev + bugs_in_code_review
    if total == 0:
        return {"escape_rate": 0, "distribution": {}}

    return {
        "escape_rate": f"{(bugs_in_prod / total) * 100:.1f}%",
        "distribution": {
            "code_review": f"{(bugs_in_code_review / total) * 100:.1f}%",
            "development": f"{(bugs_in_dev / total) * 100:.1f}%",
            "staging": f"{(bugs_in_staging / total) * 100:.1f}%",
            "production": f"{(bugs_in_prod / total) * 100:.1f}%",
        },
        "total_bugs": total,
        "assessment": "GOOD" if bugs_in_prod / total < 0.10 else "NEEDS_IMPROVEMENT",
    }

# Example
result = defect_escape_rate(
    bugs_in_prod=3,
    bugs_in_staging=12,
    bugs_in_dev=25,
    bugs_in_code_review=10
)
# escape_rate: 6.0%, assessment: GOOD
```

### Mean Time to Detect

```python
from datetime import datetime, timedelta

def calculate_mttd(defects: list[dict]) -> timedelta:
    """Calculate mean time to detect from defect records.

    Each defect has:
      - introduced_at: datetime (commit timestamp)
      - detected_at: datetime (bug report / test failure timestamp)
    """
    detection_times = []
    for defect in defects:
        introduced = datetime.fromisoformat(defect["introduced_at"])
        detected = datetime.fromisoformat(defect["detected_at"])
        detection_times.append(detected - introduced)

    if not detection_times:
        return timedelta(0)

    total_seconds = sum(dt.total_seconds() for dt in detection_times)
    avg_seconds = total_seconds / len(detection_times)
    return timedelta(seconds=avg_seconds)
```

---

## Test Suite Health Metrics

| Metric | Formula | Target | Why It Matters |
|--------|---------|--------|----------------|
| **Suite Execution Time** | Wall-clock time for full suite | <15 min (E2E), <5 min (unit) | Developer feedback speed |
| **Suite Stability** | Runs with 0 flakes / total runs | >95% | Trust in CI signal |
| **Test Count Trend** | Tests added vs removed per sprint | Net positive | Coverage growth |
| **Slowest Tests (P95)** | 95th percentile test duration | <30s (E2E), <1s (unit) | CI pipeline bottlenecks |
| **Quarantined Test Count** | Tests in quarantine | Decreasing trend | Tech debt indicator |
| **Disabled Test Count** | Skipped / disabled tests | <5% of total | Hidden coverage gaps |

---

## Release Readiness: Hard Gates Before Scoring

A weighted readiness score is compensatory: strong signals offset weak ones. That is acceptable for residual signals and wrong for blocking ones. The previous version of this recipe weighted `security_clean` at 0.15, so a release with a failing security scan and every other signal at 100 scored 85 and returned SHIP.

Rule: evaluate non-compensatory hard gates first and return BLOCK on any failure before a score is computed. A weighted score must never offset a hard gate. Missing hard-gate input counts as failing (fail closed).

| Hard gate (BLOCK if not exactly `true`) | Meaning |
|---|---|
| `security_clean` | No unresolved critical/high findings from the security scan on this build |
| `critical_e2e_pass` | Every critical-journey E2E passed on this build (rerun-pass counts as flake debt, not a pass) |
| `no_open_p0` | No open P0 defects against the release |

Residual signals (test pass rate, E2E pass rate, flake rate, performance, staging soak) are then weighted; ≥ 85 SHIP, 70–84 HOLD, < 70 BLOCK. The weights are defaults, not benchmarks: calibrate them, and check that no single residual failure can still yield SHIP (a failed performance check scores 80 → HOLD with the shipped weights).

Runnable implementation with known-bad-input tests:

```bash
python3 scripts/release_readiness.py metrics.json        # exit 0 SHIP, 1 HOLD/BLOCK, 2 invalid input
python3 scripts/test_release_readiness.py                # security fail, E2E fail, open P0, missing input -> never SHIP
```

See [`scripts/release_readiness.py`](../scripts/release_readiness.py).

---

## Operationalising Mutation Coverage

Tooling, versions, configuration and CI recipes (Stryker, PIT, mutmut, cosmic-ray) live in [qa-refactoring/references/mutation-testing.md](../../qa-refactoring/references/mutation-testing.md). This skill owns only the gate policy:

- Gate AI-authored and changed code on mutation score of the diff, not line coverage. Line coverage shows what executed; mutation score shows what was asserted.
- Scope PR runs to changed files (incremental mode) and give the job a time budget; run full-codebase mutation nightly before enforcing repo-wide thresholds.
- Use the threshold bands in the owner file. Critical paths (auth, payments, domain rules, migrations) warrant a higher break threshold than glue or infrastructure code; skip mutation testing where the cost exceeds the risk.
- Triage surviving mutants before raising thresholds. Equivalent mutants cannot be killed; mark them in the tool's ignore config instead of chasing 100%.
- Mutation-guided LLM test generation is the evidence base for this gate: Meta's ACH (arXiv [2501.12862](https://arxiv.org/abs/2501.12862), FSE 2025 Industry) generates targeted mutants, asks an LLM for tests that kill them, and filters equivalent mutants with an LLM detector (precision 0.79 / recall 0.47 before pre-processing, 0.95 / 0.96 with it); engineers accepted 73% of its tests.

---

## Metric Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| **Vanity metrics** (total test count) | More tests does not equal more quality | Track defect escape rate, not test count |
| **Goodhart's Law** (gaming coverage) | Writing tests to hit % target, not to find bugs | Measure mutation score or defect escape rate |
| **Averaging flake rate** | Hides badly flaky individual tests | Track per-test flake rate, fix top offenders |
| **100% coverage mandate** | Diminishing returns at high coverage (practitioner heuristic; no single threshold is evidence-based) | Risk-weighted coverage targets by module |
| **Test count as productivity** | Incentivizes trivial tests | Track bugs found per test, not tests written |
| **Monthly reporting only** | Too slow for actionable feedback | Daily automated dashboards + weekly review |
| **Ignoring test duration** | Slow feedback loops reduce developer velocity | Track and budget suite execution time |

### Goodhart's Law in Practice

```text
BAD: "Our coverage is 95%!"
  → But 30% of tests assert nothing meaningful
  → Mutation testing reveals only 60% mutation kill rate
  → Defects still escape to production

GOOD: "Our mutation kill rate is 78% on critical paths"
  → Tests actually catch real bugs
  → Coverage is a secondary indicator
  → Defect escape rate is primary measure
```

---


---

## Related Resources

- [operational-playbook.md](operational-playbook.md) -- CI/CD pipeline quality gates and merge-queue flake economics
- [test-impact-analysis.md](test-impact-analysis.md) -- flaky-test tooling and quarantine
- [SKILL.md](../SKILL.md) -- parent testing strategy skill
- [DORA Metrics](https://dora.dev/guides/dora-metrics-four-keys/)
