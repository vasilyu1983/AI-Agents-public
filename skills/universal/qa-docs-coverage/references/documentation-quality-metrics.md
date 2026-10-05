# Documentation Quality Metrics

KPIs, scoring rubrics, and dashboards for measuring documentation quality, coverage, and freshness. Turns doc health from a gut feeling into data.

## Contents

- [Coverage Metrics](#coverage-metrics)
- [Freshness Metrics](#freshness-metrics)
- [Quality Scoring Rubrics](#quality-scoring-rubrics)
- [Readability Metrics](#readability-metrics)
- [User Feedback and Dashboards](#user-feedback-and-dashboards)
- [SLOs for Documentation](#slos-for-documentation)
- [Automated Quality Scanning](#automated-quality-scanning)
- [Prioritization Framework for Doc Debt](#prioritization-framework-for-doc-debt)
- [Related Resources](#related-resources)

---

## Coverage Metrics

Coverage measures what percentage of your system has corresponding documentation.

### Core Coverage Dimensions

| Metric | Formula | Target |
|--------|---------|--------|
| Endpoint coverage | Documented endpoints / Total endpoints | 95% |
| Service coverage | Services with docs / Total services | 100% |
| Runbook coverage | Services with runbooks / Total services | 90% |
| Config coverage | Documented env vars / Total env vars | 85% |
| Event coverage | Documented events / Total events | 90% |
| Error code coverage | Documented errors / Total error codes | 80% |

### Automated Coverage Calculation

```python
"""
Calculate documentation coverage across multiple dimensions.
Outputs a structured report for dashboard consumption.
"""
import json
import yaml
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class CoverageResult:
    dimension: str
    total: int
    documented: int
    coverage_pct: float
    gaps: list

def calculate_endpoint_coverage(spec_path: str, routes_dir: str) -> CoverageResult:
    """Compare documented endpoints against discovered routes."""
    # Load documented endpoints from OpenAPI spec
    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    documented = set()
    for path, methods in spec.get("paths", {}).items():
        for method in methods:
            if method in ("get", "post", "put", "patch", "delete"):
                documented.add(f"{method.upper()} {path}")

    # Discover routes from code (example: Express.js pattern)
    result = subprocess.run(
        ["grep", "-rn", r"router\.\(get\|post\|put\|delete\)", routes_dir],
        capture_output=True, text=True
    )
    discovered = set()
    for line in result.stdout.strip().split("\n"):
        if line:
            # Parse route from grep output
            parts = line.split("router.")
            if len(parts) > 1:
                discovered.add(parts[1].split("(")[0].upper())

    gaps = list(discovered - documented)

    return CoverageResult(
        dimension="endpoints",
        total=len(discovered),
        documented=len(documented & discovered),
        coverage_pct=round(len(documented & discovered) / max(len(discovered), 1) * 100, 1),
        gaps=gaps,
    )

def calculate_service_coverage(services_dir: str, docs_dir: str) -> CoverageResult:
    """Check which services have corresponding documentation."""
    services = [d.name for d in Path(services_dir).iterdir() if d.is_dir()]
    documented = [d.name for d in Path(docs_dir).iterdir() if d.is_dir()]

    gaps = [s for s in services if s not in documented]

    return CoverageResult(
        dimension="services",
        total=len(services),
        documented=len(services) - len(gaps),
        coverage_pct=round((len(services) - len(gaps)) / max(len(services), 1) * 100, 1),
        gaps=gaps,
    )

def generate_coverage_report(results: list[CoverageResult]) -> dict:
    """Generate a structured coverage report."""
    return {
        "timestamp": "2026-01-15T10:00:00Z",
        "overall_coverage": round(
            sum(r.coverage_pct for r in results) / len(results), 1
        ),
        "dimensions": [asdict(r) for r in results],
        "critical_gaps": [
            gap
            for r in results
            if r.coverage_pct < 80
            for gap in r.gaps
        ],
    }
```

### Coverage Tracking Over Time

```bash
#!/bin/bash
# track-coverage.sh: Record coverage snapshot for trend analysis

DATE=$(date +%Y-%m-%d)
OUTPUT="metrics/coverage-${DATE}.json"

# Count documented vs total endpoints
TOTAL_ENDPOINTS=$(grep -c "router\.\(get\|post\|put\|delete\)" src/routes/*.ts)
DOCUMENTED_ENDPOINTS=$(yq eval '.paths | length' docs/openapi.yaml)

# Count services with runbooks
TOTAL_SERVICES=$(ls -d services/*/ | wc -l | tr -d ' ')
SERVICES_WITH_RUNBOOKS=$(find services -name "runbooks" -type d | wc -l | tr -d ' ')

# Count documented env vars
TOTAL_ENV_VARS=$(grep -c "process.env\." src/**/*.ts 2>/dev/null || echo 0)
DOCUMENTED_ENV_VARS=$(grep -c "^|" docs/configuration.md 2>/dev/null || echo 0)

cat > "$OUTPUT" << EOF
{
  "date": "$DATE",
  "endpoints": { "total": $TOTAL_ENDPOINTS, "documented": $DOCUMENTED_ENDPOINTS },
  "services": { "total": $TOTAL_SERVICES, "with_runbooks": $SERVICES_WITH_RUNBOOKS },
  "env_vars": { "total": $TOTAL_ENV_VARS, "documented": $DOCUMENTED_ENV_VARS }
}
EOF

echo "Coverage snapshot saved: $OUTPUT"
```

---

## Freshness Metrics

Freshness measures how current documentation is relative to the code it describes.

### Docs-to-Code Age Delta

```python
"""
Calculate the age delta between documentation files
and the code they document.
"""
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def get_last_modified(file_path: str) -> datetime:
    """Get last git commit date for a file."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%aI", "--", file_path],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        return datetime.fromisoformat(result.stdout.strip())
    return datetime.min.replace(tzinfo=timezone.utc)

def calculate_freshness(doc_code_pairs: list[tuple[str, str]]) -> list[dict]:
    """
    Calculate freshness for doc/code pairs.

    Args:
        doc_code_pairs: List of (doc_path, code_path) tuples
    """
    results = []
    for doc_path, code_path in doc_code_pairs:
        doc_date = get_last_modified(doc_path)
        code_date = get_last_modified(code_path)
        delta_days = (code_date - doc_date).days

        status = "fresh"
        if delta_days > 90:
            status = "stale"
        elif delta_days > 30:
            status = "aging"

        results.append({
            "doc": doc_path,
            "code": code_path,
            "doc_last_updated": doc_date.isoformat(),
            "code_last_updated": code_date.isoformat(),
            "delta_days": max(delta_days, 0),
            "status": status,
        })

    return sorted(results, key=lambda r: r["delta_days"], reverse=True)

# Example usage
pairs = [
    ("docs/api/users.md", "src/routes/users.ts"),
    ("docs/api/orders.md", "src/routes/orders.ts"),
    ("docs/architecture.md", "src/"),
]

for result in calculate_freshness(pairs):
    print(f"[{result['status'].upper():6s}] {result['delta_days']:4d}d  {result['doc']}")
```

### Freshness Thresholds

Canonical thresholds for this skill are P1: 30 days / P2: 60 days / P3: 90 days — see
[freshness-tracking.md](freshness-tracking.md#freshness-metadata-standards) and
`scripts/docs_freshness_report.py`. Use those, not a separate age-delta band, so a report from
this skill and a report from the freshness script never disagree about what "stale" means.

---

## Quality Scoring Rubrics

Score individual documents on a standardized rubric.

### Document Quality Scorecard

| Dimension | Weight | 0 (Missing) | 1 (Poor) | 2 (Adequate) | 3 (Good) | 4 (Excellent) |
|-----------|--------|-------------|-----------|---------------|-----------|---------------|
| **Accuracy** | 30% | Known errors | Partially accurate | Mostly accurate | Accurate, minor gaps | Verified against code |
| **Completeness** | 25% | Stub only | Major gaps | Core content present | Comprehensive | Complete with edge cases |
| **Currency** | 20% | > 1 year old | > 6 months | > 3 months | < 3 months | Updated with last code change |
| **Clarity** | 15% | Unreadable | Confusing structure | Readable | Well-organized | Clear, with examples |
| **Findability** | 10% | No index entry | Hard to find | Indexed | Indexed + cross-linked | Searchable, tagged, linked |

### Scoring Calculation

```python
"""
Calculate documentation quality score for a single document.
"""

RUBRIC_WEIGHTS = {
    "accuracy": 0.30,
    "completeness": 0.25,
    "currency": 0.20,
    "clarity": 0.15,
    "findability": 0.10,
}

def score_document(scores: dict[str, int]) -> dict:
    """
    Score a document against the quality rubric.

    Args:
        scores: Dict of dimension -> score (0-4)

    Returns:
        Dict with weighted score and grade
    """
    weighted_total = sum(
        scores.get(dim, 0) * weight
        for dim, weight in RUBRIC_WEIGHTS.items()
    )

    max_possible = sum(4 * w for w in RUBRIC_WEIGHTS.values())
    normalized = round(weighted_total / max_possible * 100, 1)

    grade = "F"
    if normalized >= 90:
        grade = "A"
    elif normalized >= 80:
        grade = "B"
    elif normalized >= 70:
        grade = "C"
    elif normalized >= 60:
        grade = "D"

    return {
        "raw_scores": scores,
        "weighted_score": round(weighted_total, 2),
        "normalized_pct": normalized,
        "grade": grade,
        "lowest_dimension": min(scores, key=scores.get),
    }

# Example
result = score_document({
    "accuracy": 3,
    "completeness": 2,
    "currency": 4,
    "clarity": 3,
    "findability": 2,
})
print(f"Grade: {result['grade']} ({result['normalized_pct']}%)")
print(f"Weakest area: {result['lowest_dimension']}")
```

---

## Readability Metrics

Use an existing library (`textstat` in Python, or an equivalent in your stack) for Flesch-Kincaid
grade level and Reading Ease rather than a hand-rolled syllable counter — the formulas are
standard, and a maintained library handles edge cases a quick implementation misses.

Readability targets are heuristics, not sourced benchmarks; verify against your own reader
feedback before enforcing a numeric gate:

| Doc Type | Grade Level | Reading Ease | Rationale |
|----------|------------|--------------|-----------|
| Runbooks | 6-8 | 60-80 | Must be understood under stress |
| Tutorials | 6-10 | 50-70 | Aimed at learners |
| API Reference | 8-12 | 40-60 | Technical but structured |
| Architecture Docs | 10-14 | 30-50 | Complex topics, expert audience |

---

## User Feedback and Dashboards

Track helpfulness rate, feedback volume, and top-unhelpful pages from whatever feedback
mechanism your docs platform already offers (most hosted docs tools ship one), and wire the
coverage, freshness, and quality-score numbers above into your existing dashboard tool. The
widget code and dashboard JSON needed to do this are generic front-end and observability work,
not documentation-specific judgment — skip re-deriving them here.

---

## SLOs for Documentation

Treat coverage, freshness, and quality-score SLO targets as illustrative starting points to
calibrate against your own repo's history, not sourced benchmarks — none of "95% endpoint
coverage," "100% Tier-1 runbook coverage," or ">=75/100 quality score" is backed by a published
source. Anchor the freshness SLO to the canonical P1/P2/P3 = 30/60/90-day thresholds above rather
than a separate "no doc > 180 days" figure, so this SLO and the freshness gate never disagree.
Wire an error-budget policy (staged actions as the budget burns) once you have real numbers to
calibrate against, following the shape in [qa-observability](../../qa-observability/SKILL.md) if
one is needed.

---

## Automated Quality Scanning

### CI Pipeline for Doc Quality

Use the [CI gate design and workflow](cicd-integration.md#github-actions-example). Add a coverage ratchet only when a repository has a real coverage inventory, a recorded baseline, and a maintained checker; this skill does not ship the `measure-coverage.py` or `validate-code-blocks.py` commands that the old example invoked.

### Quality Scanning Tools

| Tool | What It Checks | Integration |
|------|---------------|-------------|
| **lychee** (current stable — verify at github.com/lycheeverse/lychee/releases) | Broken links | GitHub Action, CLI |
| **markdownlint-cli2** (current stable — verify at github.com/DavidAnson/markdownlint-cli2/releases) | Markdown formatting | GitHub Action, npm |
| **cspell** | Spelling errors | GitHub Action, npm |
| **vale** (moved from errata-ai/vale to vale-cli/vale; confirm current release before pinning) | Style and tone consistency; supports LSP and custom Views for YAML/JSON/TOML scoping | GitHub Action, CLI |
| **interrogate** / **docstr-coverage** | Python docstring presence (not quality) | CI, pre-commit |
| **textlint** | Custom writing rules | npm |
| **alex** | Inclusive language | npm |

---

## Prioritization Framework for Doc Debt

### Doc Debt Priority Matrix

| Impact | High Traffic | Medium Traffic | Low Traffic |
|--------|:-----------:|:--------------:|:-----------:|
| **Stale + Inaccurate** | P0 - Fix now | P1 - This sprint | P2 - Next sprint |
| **Stale + Accurate** | P2 - Next sprint | P3 - Backlog | P4 - Opportunistic |
| **Missing (critical path)** | P0 - Fix now | P1 - This sprint | P2 - Next sprint |
| **Missing (edge case)** | P2 - Next sprint | P3 - Backlog | P4 - Opportunistic |
| **Style/formatting only** | P3 - Backlog | P4 - Opportunistic | P5 - Skip |

### Doc Debt Tracking

```python
"""
Score and prioritize documentation debt items.
Higher score = higher priority.
"""

def calculate_doc_debt_priority(
    traffic_percentile: int,       # 0-100, page view percentile
    staleness_days: int,           # Days since last update
    is_inaccurate: bool,           # Known inaccuracies
    is_missing: bool,              # Doc doesn't exist yet
    is_critical_path: bool,        # On a critical user journey
    incident_mentions: int,        # Times referenced in incidents
) -> dict:
    score = 0

    # Traffic weight (0-30)
    score += min(traffic_percentile * 0.3, 30)

    # Staleness weight (0-25)
    if staleness_days > 180:
        score += 25
    elif staleness_days > 90:
        score += 15
    elif staleness_days > 30:
        score += 5

    # Accuracy weight (0-25)
    if is_inaccurate:
        score += 25
    if is_missing:
        score += 20

    # Critical path weight (0-10)
    if is_critical_path:
        score += 10

    # Incident correlation (0-10)
    score += min(incident_mentions * 5, 10)

    priority = "P4"
    if score >= 70:
        priority = "P0"
    elif score >= 50:
        priority = "P1"
    elif score >= 30:
        priority = "P2"
    elif score >= 15:
        priority = "P3"

    return {"score": round(score, 1), "priority": priority}
```

---

## Related Resources

- [API Docs Validation](api-docs-validation.md) - Validating API documentation accuracy
- [Runbook Testing](runbook-testing.md) - Testing operational runbooks
- [Freshness Tracking](freshness-tracking.md) - Detecting stale documentation
- [Priority Framework](priority-framework.md) - Prioritizing documentation work
- [CI/CD Integration](cicd-integration.md) - Automation pipeline patterns
- [SKILL.md](../SKILL.md) - Parent skill overview
