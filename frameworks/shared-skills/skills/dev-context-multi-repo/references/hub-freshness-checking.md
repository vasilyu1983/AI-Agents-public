# Hub Freshness Checking

How to detect when a documentation hub is stale relative to its source repositories, and what to do about it.

## Table of Contents

- [When to Run Freshness Checks](#when-to-run-freshness-checks)
- [Quick Start](#quick-start)
- [How Auto-Mapping Works](#how-auto-mapping-works)
- [Explicit Mapping Configuration](#explicit-mapping-configuration)
- [Change Detection Categories](#change-detection-categories)

## When to Run Freshness Checks

| Trigger | Why |
|---------|-----|
| After pulling/fetching source repos | Catch changes before they accumulate |
| Before planning sessions or architecture reviews | Ensure decisions use current data |
| On a CI/CD schedule (nightly or weekly) | Automated drift detection |
| Before publishing hub updates externally | Verify nothing was missed |
| After a release or deployment wave | Source repos change rapidly during releases |

## Quick Start

```bash
# Basic: auto-detect baseline from hub's last_verified dates
check_hub_freshness.sh ~/repos/platform ~/repos/platform/requirements-hub

# Explicit date range
check_hub_freshness.sh ~/repos ~/docs-hub --since 2026-03-01

# JSON output for CI pipelines
check_hub_freshness.sh ~/repos ~/docs-hub --json --out freshness.json

# With explicit mapping file
check_hub_freshness.sh ~/repos ~/docs-hub --mapping hub-mapping.json --verbose
```

## How Auto-Mapping Works

Without `--mapping`, the script greps hub markdown files for repo names. It tries:

1. **Exact name** — the directory name of the repo (e.g., `payments-ledger`)
2. **Lowercase** — case-insensitive match
3. **Dot-to-hyphen** — `payments.ledger` also matches `payments-ledger`

This works well when hub docs naturally reference source repos by name. For hubs that use different terminology, use explicit mapping.

## Explicit Mapping Configuration

Create a JSON file following `assets/hub-mapping-template.json`:

```json
{
  "hub_root": ".",
  "last_verified_pattern": "last_verified:\\s*(\\d{4}-\\d{2}-\\d{2})",
  "mappings": [
    {
      "repo_pattern": "payments-ledger*",
      "hub_docs": ["payments-ledger/README.md", "overview/data-catalog.md"],
      "change_weight": "critical"
    },
    {
      "repo_pattern": "payments*",
      "hub_docs": ["incomings/**/*.md", "overview/process-catalog.md"],
      "change_weight": "critical"
    },
    {
      "repo_pattern": "web*",
      "hub_docs": ["channels/web-app.md"],
      "change_weight": "standard"
    }
  ]
}
```

`repo_pattern` supports shell glob matching (fnmatch). `change_weight` is informational — the script uses commit-level change categories for priority.

## Change Detection Categories

The script classifies changed files by pattern:

| Category | Patterns | Priority Impact |
|----------|----------|-----------------|
| SCHEMA | Migrations, DbContext, MongoRegistry, .sql | P1 — data model changes likely invalidate docs |
| API | Controllers, routes, openapi/swagger, .proto | P1 — interface changes break contract docs |
| MESSAGING | Consumer/Producer/Handler classes, kafka/rabbit configs | P2 — event flow changes need doc updates |
| CONFIG | appsettings, csproj, package.json, docker-compose | P3 — operational changes, lower doc impact |
| INFRA | Dockerfile, k8s YAML, CI/CD configs, terraform | P3 — infrastructure changes |
| OTHER | Everything else | P4 — tests, minor code, internal docs |

Multiple categories can apply to the same repo if different types of files changed.

## Interpreting the Report

### Markdown Report

The markdown table is sorted by priority. Focus on:

1. **P1 repos first** — their hub docs likely contain outdated data models, API contracts, or interface descriptions
2. **P2 repos** — messaging and event flow docs may be inaccurate
3. **Affected Hub Docs column** — tells you exactly which hub files to re-verify
4. **Commit count** — high commit counts suggest significant rework, not just patches

### JSON Report

The JSON output is designed for CI/CD integration:

```bash
# Check if updates needed (exit code 1)
if ! check_hub_freshness.sh ~/repos ~/hub --json --out /tmp/freshness.json; then
  # Parse P1 count
  p1_count=$(python3 -c "import json; d=json.load(open('/tmp/freshness.json')); print(sum(1 for c in d['changes'] if c['priority']=='P1'))")
  if [ "$p1_count" -gt 0 ]; then
    echo "ALERT: $p1_count repos have P1 (schema/API) changes affecting the hub"
    # Create ticket, send notification, etc.
  fi
fi
```

## CI/CD Integration

### Nightly Check (GitLab CI)

```yaml
hub-freshness:
  stage: verify
  schedule:
    cron: '0 6 * * *'  # 6 AM daily
  script:
    - ./scripts/check_hub_freshness.sh $REPOS_ROOT $HUB_ROOT --json --out freshness.json
  artifacts:
    paths: [freshness.json]
    when: always
  allow_failure: true  # Don't block pipelines
```

### GitHub Action

```yaml
- name: Check hub freshness
  run: |
    chmod +x scripts/check_hub_freshness.sh
    scripts/check_hub_freshness.sh repos/ docs-hub/ --json --out freshness.json || true
    if jq -e '.updates_needed' freshness.json; then
      echo "::warning::Hub docs need updating — see freshness.json"
    fi
```

## Extending Change Categories

To add domain-specific patterns, modify the pattern variables at the top of `check_hub_freshness.sh`:

```bash
# Example: add GraphQL schema detection
API_PATTERNS='Controller.*\.cs|/routes/|openapi|swagger|\.proto$|\.graphql$|schema\.gql$'

# Example: add Prisma schema detection
SCHEMA_PATTERNS='Migrations/|DbContext\.cs|MongoRegistry\.cs|\.sql$|InitSchema|schema\.prisma'
```

## Relationship to Other Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `check_hub_freshness.sh` | Git-commit-aware hub staleness detection | After repo pulls, before planning |
| `report_drift.py` | Profile-level staleness (mtime-based) | After scanning, to detect stale profiles |
| `qa-docs-coverage` skill | Doc quality gates, freshness metadata, link checking | During doc reviews and PR checks |

`check_hub_freshness.sh` complements `report_drift.py` — the former checks source repos against hub docs, the latter checks profiles against source repos. Together they cover the full chain: source → profile → hub doc.

## Nightly Compounding Loop (The Dream Cycle)

<!-- Source: github.com/garrytan/gbrain@adb02b7826a010700efc968b18df8aaf17d8ffa1 (MIT), extracted 2026-04-13 -->

Drift detection reports what's stale; the compounding loop *repairs* it. Running the loop nightly is what turns a hub from a snapshot into an asset that gets more useful over time.

### The Four Passes

A nightly job walks the hub and runs four passes, each writing a structured report:

1. **Entity sweep** — scan all catalog and concept pages for unlinked mentions of other entities in the hub. When a page mentions `payments-ledger` but has no backlink edge to `catalog/payments-ledger.md`, add the missing link. Output: `reports/entity-sweep-YYYY-MM-DD.json` listing added backlinks.
2. **Citation audit** — flag facts in Compiled Truth sections that lack a Timeline entry with `[Source: …]` attribution. Do not auto-fix — queue for human review. Output: `reports/citation-audit-YYYY-MM-DD.md` with flagged claims per page.
3. **Memory consolidation** — find near-duplicate entries (two Timeline entries within a day describing the same event from slightly different angles; two Open Threads that describe the same in-flight work). Merge duplicates, preserve both source citations. Output: `reports/consolidation-YYYY-MM-DD.md`.
4. **Resolved-thread migration** — any Open Thread item closed in the last 24 hours gets moved into the Timeline with its resolution appended as a new entry. This keeps the Open Threads list short and preserves the resolution history.

### Recommended Cadence

| Job | Cron | Runtime budget |
|-----|------|----------------|
| Entity sweep | Nightly, 02:00 local | < 5 min for 100 repos |
| Citation audit | Nightly, 02:15 local | < 10 min for 100 repos |
| Memory consolidation | Nightly, 02:30 local | < 15 min for 100 repos |
| Resolved-thread migration | Nightly, 02:45 local | < 2 min for 100 repos |

Run during a quiet window so the compute cost is invisible. Output JSON reports go into `reports/` so the next planning session can read them as Level 1 context input.

### Why Nightly and Not On-Demand

On-demand feels faster but produces two failure modes: either the loop runs so rarely that drift accumulates, or developers trigger it manually and forget. A cron job running while everyone is asleep compounds quietly — the key insight from the source material is that "the brain compounds overnight," and the compounding only happens if the loop runs without human intervention.

### When Not to Run It

- **First week of a new hub**: the loop is most valuable once there are enough entities and pages for backlinks to matter. For a 5-repo hub with 30 pages, skip the nightly loop and run it weekly instead.
- **Hubs under active refactoring**: if the directory schema is changing, the entity sweep will thrash. Pause the loop for the duration of the refactor, then run it once to resynchronize.

## Contradiction Categories

<!-- Source: github.com/MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), extracted 2026-04-13 -->

Drift reports are more useful when they classify *what kind* of drift. Three categories cover most real-world contradictions in a multi-repo knowledge hub:

| Category | Meaning | Example | Signal |
|----------|---------|---------|--------|
| **Attribution conflict** | The wrong entity is credited for a fact | Catalog page says "payments owns the settlement topic" but profile scan shows `payments-ledger` as the producer | Profile vs hub-page disagreement |
| **Temporal error** | A date, duration, tenure, or version claim is wrong | Catalog says "runs .NET 8" but manifest scan finds `.NET 9` | Fact changed in source; hub not updated |
| **Stale information** | Once-true fact has been superseded | "Kafka topic `payments.journal.v1` is the active producer" when the repo has migrated to `v2` | Newer entries exist but older claim was never removed |

### Detection Hints

- **Attribution conflicts** surface from the graph: when an edge in `graphs/knowledge-graph.json` contradicts a claim in a catalog page's Compiled Truth section, flag it. This is the highest-confidence category because the graph is built from structured profile data.
- **Temporal errors** surface from manifest diffs: when `profiles/<repo>.json` has a newer language/framework version than what the catalog page's State section says, flag the State field and link to the profile entry.
- **Stale information** is the hardest to detect automatically because it requires noticing that a *newer* claim exists without the *older* claim being retracted. Default detector: scan Timeline entries for contradictory pairs within the same page, preferring the later entry's claim over the earlier one's.

### Reporting Format

Contradictions should feed into `reports/drift.json` alongside the existing change-category output from `check_hub_freshness.sh`:

```json
{
  "contradictions": [
    {
      "category": "attribution_conflict",
      "page": "catalog/payments.md",
      "claim": "owns the settlement topic",
      "evidence_against": "graphs/knowledge-graph.json:payments-ledger publishes_to payments.settlement.v1",
      "severity": "high",
      "suggested_fix": "Update State section to reflect payments-ledger as producer; move old claim to Timeline with correction"
    }
  ]
}
```

Do not auto-fix contradictions. The fix requires judgment about *which* claim is correct (sometimes the source scan is wrong, not the hub page). Queue them for human review during the next freshness pass.
