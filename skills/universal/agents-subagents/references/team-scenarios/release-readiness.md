---
description: Release Readiness — extracted from monolith for progressive disclosure.
last_verified: 2026-08-26
status: stable
---

## Release Readiness

**Typical scenario**

You want a release gate before a risky cutover or high-impact merge.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "release-readiness"`.

Scenario: Evaluate whether this release candidate is ready for tonight's production window.

Required context:
- Release scope
- Verification evidence
- Rollback path
- Optional context: graphs/code-graph.json, reports/query-*.md, runbooks, release notes

Instructions:
- qa-test-reviewer checks coverage, edge cases, and validation evidence
- docs-runbook-auditor checks runbooks, release notes, and operator clarity
- software-performance-reviewer checks likely regressions and hot-path risk
- ops-rollback-planner checks rollback path, blast radius, and contingency steps
- Run checks in parallel, then synthesize a go/no-go recommendation in the parent thread
- Include blockers, soft risks, and exact pre-release actions
- Clean up the team when done
```

**Codex prompt**

```text
Spawn generic role-brief workers for testing, runbooks, performance, and rollback planning in parallel.

Task: assess whether the current release candidate is ready for tonight's production window.

Context:
- use release notes, verification evidence, and rollback path as primary context
- use graph/query artifacts if present

Each worker should return:
- blockers
- non-blocking risks
- the single most important action before release

After all workers finish, synthesize a go/no-go call with the rationale.
```

**Debate-first variant**

Use debate for true go/no-go decisions when the team is split on shipping versus delaying by one window.
