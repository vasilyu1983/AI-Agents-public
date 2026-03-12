# Documentation Quality Metrics

KPIs, scoring rubrics, and dashboards for measuring documentation quality, coverage, and freshness. Turns doc health from a gut feeling into data.

## Contents

- [Coverage Metrics](#coverage-metrics)
- [Freshness Metrics](#freshness-metrics)
- [Quality Scoring Rubrics](#quality-scoring-rubrics)
- [Readability Metrics](#readability-metrics)
- [User Feedback Collection](#user-feedback-collection)
- [Documentation Health Dashboards](#documentation-health-dashboards)
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

| Status | Age Delta | Action |
|--------|-----------|--------|
| **Fresh** | < 30 days | No action |
| **Aging** | 30-90 days | Flag for review in next sprint |
| **Stale** | 90-180 days | Prioritize update, add to sprint |
| **Critical** | > 180 days | Immediate review, may be dangerously wrong |

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

### Flesch-Kincaid for Technical Docs

```python
"""
Calculate readability metrics for documentation.
Technical docs should target grade level 8-12.
"""
import re
import math

def count_syllables(word: str) -> int:
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    return max(count, 1)

def flesch_kincaid_grade(text: str) -> dict:
    """Calculate Flesch-Kincaid grade level and reading ease."""
    # Strip code blocks (they skew readability scores)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', 'CODE', text)

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b[a-zA-Z]+\b', text)

    if not sentences or not words:
        return {"grade_level": 0, "reading_ease": 0}

    total_syllables = sum(count_syllables(w) for w in words)
    avg_sentence_length = len(words) / len(sentences)
    avg_syllables_per_word = total_syllables / len(words)

    grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
    ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word

    return {
        "grade_level": round(grade, 1),
        "reading_ease": round(ease, 1),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(avg_sentence_length, 1),
    }

# Target ranges for technical documentation
READABILITY_TARGETS = {
    "api_reference": {"grade": (8, 12), "ease": (40, 60)},
    "tutorial": {"grade": (6, 10), "ease": (50, 70)},
    "runbook": {"grade": (6, 8), "ease": (60, 80)},
    "architecture": {"grade": (10, 14), "ease": (30, 50)},
}
```

### Readability Targets by Doc Type

| Doc Type | Grade Level | Reading Ease | Rationale |
|----------|------------|--------------|-----------|
| Runbooks | 6-8 | 60-80 | Must be understood under stress |
| Tutorials | 6-10 | 50-70 | Aimed at learners |
| API Reference | 8-12 | 40-60 | Technical but structured |
| Architecture Docs | 10-14 | 30-50 | Complex topics, expert audience |

---

## User Feedback Collection

### In-Doc Feedback Widget

```javascript
// Minimal doc feedback component
// Embed at bottom of each documentation page

function DocFeedback({ pageId, pageTitle }) {
  const [rating, setRating] = useState(null);
  const [feedback, setFeedback] = useState("");

  const submitFeedback = async () => {
    await fetch("/api/doc-feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        page_id: pageId,
        page_title: pageTitle,
        rating,          // "helpful" | "not_helpful"
        feedback,        // Free text
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
      }),
    });
  };

  return (
    <div className="doc-feedback">
      <p>Was this page helpful?</p>
      <button onClick={() => { setRating("helpful"); submitFeedback(); }}>
        Yes
      </button>
      <button onClick={() => { setRating("not_helpful"); submitFeedback(); }}>
        No
      </button>
      {rating === "not_helpful" && (
        <textarea
          placeholder="What was missing or incorrect?"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          onBlur={submitFeedback}
        />
      )}
    </div>
  );
}
```

### Feedback Metrics to Track

| Metric | Formula | Target |
|--------|---------|--------|
| Helpfulness rate | Helpful votes / Total votes | > 80% |
| Feedback volume | Feedback submissions per week | Increasing trend |
| Issue resolution time | Time from feedback to doc fix | < 5 business days |
| Top unhelpful pages | Pages with lowest helpfulness | Prioritize for rewrite |

---

## Documentation Health Dashboards

### Dashboard Panels (Grafana)

```json
{
  "dashboard": {
    "title": "Documentation Health",
    "panels": [
      {
        "title": "Overall Coverage",
        "type": "gauge",
        "targets": [
          { "expr": "doc_coverage_pct{dimension='endpoints'}" },
          { "expr": "doc_coverage_pct{dimension='services'}" },
          { "expr": "doc_coverage_pct{dimension='runbooks'}" }
        ],
        "thresholds": [
          { "value": 70, "color": "red" },
          { "value": 85, "color": "yellow" },
          { "value": 95, "color": "green" }
        ]
      },
      {
        "title": "Freshness Distribution",
        "type": "piechart",
        "targets": [
          { "expr": "count(doc_age_days < 30)", "legendFormat": "Fresh" },
          { "expr": "count(doc_age_days >= 30 and doc_age_days < 90)", "legendFormat": "Aging" },
          { "expr": "count(doc_age_days >= 90)", "legendFormat": "Stale" }
        ]
      },
      {
        "title": "Quality Score Trend",
        "type": "timeseries",
        "targets": [
          { "expr": "avg(doc_quality_score)", "legendFormat": "Avg Quality" }
        ]
      },
      {
        "title": "Top 10 Stale Documents",
        "type": "table",
        "targets": [
          { "expr": "topk(10, doc_age_days)" }
        ]
      }
    ]
  }
}
```

### Dashboard Layout

```
+---------------------------+---------------------------+
| Overall Coverage (gauge)  | Freshness Distribution    |
| Endpoints: 94%            |  [pie chart]              |
| Services: 100%            |  Fresh: 65%               |
| Runbooks: 85%             |  Aging: 25%               |
|                           |  Stale: 10%               |
+---------------------------+---------------------------+
| Quality Score Trend       | User Feedback Rate        |
|  [line chart over 90d]    |  Helpful: 82%             |
|  Avg: 78/100              |  Not helpful: 18%         |
+---------------------------+---------------------------+
| Top 10 Stale Documents    | Coverage Gaps             |
|  [table: doc, age, owner] |  [table: component, type] |
+---------------------------+---------------------------+
```

---

## SLOs for Documentation

### Recommended Documentation SLOs

| SLO | Target | Window | Measurement |
|-----|--------|--------|-------------|
| Endpoint coverage | >= 95% | Rolling 30 days | CI coverage check |
| Runbook coverage (Tier 1) | 100% | Rolling 30 days | Runbook inventory scan |
| Freshness (no doc > 180 days stale) | 100% | Rolling 30 days | Git age delta |
| Quality score average | >= 75/100 | Rolling 90 days | Quarterly audit |
| User helpfulness rating | >= 80% | Rolling 30 days | Feedback widget |
| Broken link rate | < 1% | Rolling 7 days | CI link checker |
| Doc review SLA (new service) | Docs within 2 sprints | Per service launch | Tracking ticket |

### Error Budget for Documentation

```yaml
documentation_slos:
  - name: endpoint-coverage
    target: 0.95
    window: 30d
    measurement: documented_endpoints / total_endpoints
    error_budget_policy:
      - threshold: 50%
        action: "Flag in sprint planning"
      - threshold: 25%
        action: "Documentation sprint required"
      - threshold: 0%
        action: "Block new service launches until coverage restored"

  - name: freshness
    target: 1.0  # No docs older than 180 days
    window: 30d
    measurement: fresh_docs / total_docs
    error_budget_policy:
      - threshold: 50%
        action: "Assign stale docs to owners"
      - threshold: 0%
        action: "Dedicated doc refresh sprint"
```

---

## Automated Quality Scanning

### CI Pipeline for Doc Quality

```yaml
# .github/workflows/doc-quality.yaml
name: Documentation Quality Gate

on:
  pull_request:
    paths:
      - "docs/**"
      - "*.md"

jobs:
  quality-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check broken links
        uses: lycheeverse/lychee-action@v1
        with:
          args: --verbose --no-progress "docs/**/*.md"
          fail: true

      - name: Lint markdown
        uses: DavidAnson/markdownlint-cli2-action@v16
        with:
          globs: "docs/**/*.md"

      - name: Check spelling
        uses: streetsidesoftware/cspell-action@v6
        with:
          files: "docs/**/*.md"

      - name: Validate code examples
        run: |
          # Extract and syntax-check code blocks
          python scripts/validate-code-blocks.py docs/

      - name: Coverage ratchet check
        run: |
          # Ensure coverage doesn't decrease
          CURRENT=$(python scripts/measure-coverage.py)
          BASELINE=$(cat metrics/coverage-baseline.txt)
          if [ "$CURRENT" -lt "$BASELINE" ]; then
            echo "::error::Documentation coverage decreased from $BASELINE% to $CURRENT%"
            exit 1
          fi
```

### Quality Scanning Tools

| Tool | What It Checks | Integration |
|------|---------------|-------------|
| **lychee** | Broken links | GitHub Action, CLI |
| **markdownlint** | Markdown formatting | GitHub Action, npm |
| **cspell** | Spelling errors | GitHub Action, npm |
| **vale** | Style and tone consistency | GitHub Action, CLI |
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

- [API Docs Validation](./api-docs-validation.md) - Validating API documentation accuracy
- [Runbook Testing](./runbook-testing.md) - Testing operational runbooks
- [Freshness Tracking](./freshness-tracking.md) - Detecting stale documentation
- [Priority Framework](./priority-framework.md) - Prioritizing documentation work
- [CI/CD Integration](./cicd-integration.md) - Automation pipeline patterns
- [SKILL.md](../SKILL.md) - Parent skill overview
