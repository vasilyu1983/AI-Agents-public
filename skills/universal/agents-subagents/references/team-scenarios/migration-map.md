---
description: Migration Map — extracted from monolith for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## Migration Map

**Typical scenario**

You need a migration sequence that spans multiple repos or a framework/platform transition.

**Claude prompt**

```text
Create an agent team using the installed `dev-migration-map` members.

Scenario: Plan a migration from a legacy REST client layer to a typed internal SDK across three repos without breaking current integrations.

Required context:
- Migration goal, timeline, and compatibility constraints
- Optional artifacts if present: profiles/*.json, graphs/system-edges.json, graphs/code-graph.json

Instructions:
- dev-portfolio-mapper identifies affected repos and boundaries
- dev-dependency-auditor maps package and call-site dependencies
- dev-migration-planner proposes the migration sequence and cutover model
- ops-rollout-reviewer checks testability, rollout safety, and rollback constraints
- Keep the workflow staged with parallel discovery where it helps
- Return a migration plan with phases, dependency breakpoints, and rollback options
- Clean up the team when done
```

**Codex prompt**

```text
Run the installed migration_map members with staged orchestration.

Goal: migrate from the legacy REST client layer to a typed internal SDK across three repos without breaking current integrations.

Sequence:
- portfolio_mapper and dependency_auditor can analyze in parallel first
- migration_planner synthesizes the sequence after those outputs arrive
- rollout_reviewer validates rollout, rollback, and test strategy

Final output:
- phased migration plan
- dependency hotspots
- compatibility strategy
- rollback and validation gates
```

**Debate-first variant**

Use debate when there is a real dispute between "big bang cutover after adapter layer" and "long dual-stack compatibility window."
