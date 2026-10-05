---
description: Data Analytics — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## Data Analytics

**Typical scenario**

Your team does not trust product metrics because instrumentation, SQL, and modeled outputs disagree.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "data-analytics"`.

Scenario: Diagnose why activation and retained-user metrics differ across dashboards after recent event and warehouse changes.

Required context:
- Event definitions for signup, activation, and retention
- Current KPI consumers and dashboards
- Known pain: teams do not trust the numbers

Instructions:
- data-analytics-engineer reviews model and semantic-layer contracts
- data-sql-optimizer reviews slow or suspicious SQL paths
- data-streaming-architect reviews event flow, freshness, and replay risks
- data-instrumentation-analyst reviews tracking quality and identity joins
- Synthesize one restoration plan focused on trust, not just performance
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn analytics_engineer, sql_optimizer, streaming_architect, and instrumentation_analyst in parallel.

Task: diagnose why activation and retained-user metrics disagree across dashboards.

Return:
- main source-of-truth issues
- where SQL, streaming, or tracking is breaking trust
- minimum fix plan to restore reliable metrics
```
