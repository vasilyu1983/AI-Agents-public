---
description: Generated team-to-members and member-to-teams inventory.
status: generated
---

# Team ↔ Member Matrix

This file is generated from `agents/teams/*/team.yaml` and the canonical Claude member filenames. Do not edit it manually.

Core membership and expansion candidates are reported separately: a candidate is available only after its team's expansion gate fires.

## Table of Contents

- [Summary](#summary)
- [Reuse Matrix](#reuse-matrix)
- [Team → Members](#team--members)
- [Member → Teams](#member--teams)
- [Regeneration](#regeneration)
- [Related References](#related-references)

## Summary

| Metric | Count |
|---|---:|
| Default teams | 7 |
| Opt-in teams | 1 |
| Teams (total) | 8 |
| Canonical members | 85 |
| Composed members (core or candidate) | 45 |
| Cross-cutting core members (2+ teams) | 1 |
| Single-team core specialists | 32 |
| Candidate-only members | 12 |
| Uncomposed members | 40 |

Core reuse density: **3%** (1 of 33 core-composed members appear in two or more teams).

## Reuse Matrix

Core members appearing in two or more teams, ordered by breadth and then member ID.

| Member | Core teams | Teams |
|---|---:|---|
| `dev-portfolio-mapper` | 2 | `dev-context-preparation`, `dev-migration-map` |

## Team → Members

| Team | Install | Core members | Expansion candidates |
|---|---|---|---|
| `ai-knowledge-bot-builder` | default | `ai-bot-builder-lead`, `ai-context-architect`, `ai-retrieval-architect`, `ai-agent-architect` | `ai-evals-observer`, `software-security-reviewer` |
| `dev-context-preparation` | default | `dev-portfolio-mapper`, `dev-repo-context-curator`, `dev-code-graph-builder`, `dev-context-packet-synthesizer` | — |
| `dev-feature-delivery` | default | `dev-feature-researcher`, `dev-feature-implementer`, `dev-feature-reviewer` | `software-security-reviewer`, `software-performance-reviewer`, `qa-test-reviewer`, `dev-build-fixer`, `dev-test-writer` |
| `dev-migration-map` | default | `dev-portfolio-mapper`, `dev-dependency-auditor`, `dev-migration-planner`, `ops-rollout-reviewer` | `software-risk-reviewer`, `qa-resilience-reviewer`, `data-architect` |
| `docs-knowledge` | default | `docs-codebase-architect`, `docs-ai-prd-writer`, `docs-notes-retrieval-curator`, `docs-quality-auditor` | — |
| `marketing-campaign` | opt-in | `startup-competitive-analyst`, `startup-review-miner`, `marketing-strategist`, `startup-product-marketing-strategist`, `marketing-email-automation-lead`, `marketing-paid-acquisition-strategist`, `marketing-creative-director`, `marketing-product-analytics-lead` | `marketing-seo-strategist`, `marketing-pr-communications-lead`, `marketing-creative-intel-analyst` |
| `product-surface` | default | `software-frontend-lead`, `software-ux-designer`, `software-accessibility-reviewer`, `software-localisation-reviewer` | `software-performance-reviewer`, `software-ios-specialist`, `software-android-specialist` |
| `software-code-review-board` | default | `software-security-reviewer`, `software-performance-reviewer`, `qa-test-reviewer` | `software-accessibility-reviewer`, `software-localisation-reviewer`, `software-billing-ops-reviewer` |

## Member → Teams

### Cross-cutting core members

See the [Reuse Matrix](#reuse-matrix).

### Single-team core specialists

#### ai

- `ai-agent-architect` → `ai-knowledge-bot-builder`
- `ai-bot-builder-lead` → `ai-knowledge-bot-builder`
- `ai-context-architect` → `ai-knowledge-bot-builder`
- `ai-retrieval-architect` → `ai-knowledge-bot-builder`

#### dev

- `dev-code-graph-builder` → `dev-context-preparation`
- `dev-context-packet-synthesizer` → `dev-context-preparation`
- `dev-dependency-auditor` → `dev-migration-map`
- `dev-feature-implementer` → `dev-feature-delivery`
- `dev-feature-researcher` → `dev-feature-delivery`
- `dev-feature-reviewer` → `dev-feature-delivery`
- `dev-migration-planner` → `dev-migration-map`
- `dev-repo-context-curator` → `dev-context-preparation`

#### docs

- `docs-ai-prd-writer` → `docs-knowledge`
- `docs-codebase-architect` → `docs-knowledge`
- `docs-notes-retrieval-curator` → `docs-knowledge`
- `docs-quality-auditor` → `docs-knowledge`

#### marketing

- `marketing-creative-director` → `marketing-campaign`
- `marketing-email-automation-lead` → `marketing-campaign`
- `marketing-paid-acquisition-strategist` → `marketing-campaign`
- `marketing-product-analytics-lead` → `marketing-campaign`
- `marketing-strategist` → `marketing-campaign`

#### ops

- `ops-rollout-reviewer` → `dev-migration-map`

#### qa

- `qa-test-reviewer` → `software-code-review-board`; candidate for `dev-feature-delivery`

#### software

- `software-accessibility-reviewer` → `product-surface`; candidate for `software-code-review-board`
- `software-frontend-lead` → `product-surface`
- `software-localisation-reviewer` → `product-surface`; candidate for `software-code-review-board`
- `software-performance-reviewer` → `software-code-review-board`; candidate for `dev-feature-delivery`, `product-surface`
- `software-security-reviewer` → `software-code-review-board`; candidate for `ai-knowledge-bot-builder`, `dev-feature-delivery`
- `software-ux-designer` → `product-surface`

#### startup

- `startup-competitive-analyst` → `marketing-campaign`
- `startup-product-marketing-strategist` → `marketing-campaign`
- `startup-review-miner` → `marketing-campaign`

### Candidate-only members

- `ai-evals-observer` → `ai-knowledge-bot-builder`
- `data-architect` → `dev-migration-map`
- `dev-build-fixer` → `dev-feature-delivery`
- `dev-test-writer` → `dev-feature-delivery`
- `marketing-creative-intel-analyst` → `marketing-campaign`
- `marketing-pr-communications-lead` → `marketing-campaign`
- `marketing-seo-strategist` → `marketing-campaign`
- `qa-resilience-reviewer` → `dev-migration-map`
- `software-android-specialist` → `product-surface`
- `software-billing-ops-reviewer` → `software-code-review-board`
- `software-ios-specialist` → `product-surface`
- `software-risk-reviewer` → `dev-migration-map`

### Uncomposed members

- `ai-data-scientist`
- `ai-forecasting-scientist`
- `ai-mlops-engineer`
- `ai-quantum-data-scientist`
- `data-analytics-engineer`
- `data-governance-privacy-lead`
- `data-instrumentation-analyst`
- `data-sql-optimizer`
- `data-streaming-architect`
- `dev-api-designer`
- `docs-runbook-auditor`
- `marketing-aeo-strategist`
- `marketing-ops-systems-lead`
- `marketing-partnerships-strategist`
- `marketing-prospect-discovery-analyst`
- `ops-cost-optimizer`
- `ops-incident-commander`
- `ops-platform-engineer`
- `ops-rollback-planner`
- `product-manager`
- `product-strategist`
- `product-user-researcher`
- `qa-debugger`
- `qa-mobile-release-reviewer`
- `qa-observability-lead`
- `software-appsec-pipeline-engineer`
- `software-mobile-architect`
- `software-payments-architect`
- `software-solution-architect`
- `startup-business-developer`
- `startup-compliance-readiness-lead`
- `startup-growth-execution-operator`
- `startup-growth-specialist`
- `startup-negotiator`
- `startup-operating-system-reviewer`
- `startup-painpoint-scout`
- `startup-people-ops-lead`
- `startup-pricing-advisor`
- `startup-revenue-ops-strategist`
- `startup-trend-analyst`

## Regeneration

```bash
python3 scripts/generate_team_member_matrix.py
python3 scripts/generate_team_member_matrix.py --check
```

The catalog integrity validator also runs the drift check.

## Related References

- [members-and-teams.md](members-and-teams.md) — canonical library structure and member-vs-variant rule
- [team-coverage.md](team-coverage.md) — domain coverage
- [team-scenarios.md](team-scenarios.md) — launch examples
- [team-diagrams.md](team-diagrams.md) — generated team diagrams
