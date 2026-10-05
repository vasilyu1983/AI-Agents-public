---
description: Context Engineering — extracted from monolith for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## Context Engineering

**Typical scenario**

You want a reusable context packet before review, migration, or implementation across one or more repos.

**Claude prompt**

```text
Create an agent team using the installed `dev-context-preparation` members.

Scenario: Prepare reusable context for reviewing authentication changes across the api, web, and worker repos.

Required context:
- Target repos: api, web, worker
- Focus area: login, session refresh, token verification, and audit logging

Instructions:
- dev-portfolio-mapper inventories the repos and normalizes shared context
- dev-repo-context-curator identifies the best hot, warm, and cold context sources
- dev-code-graph-builder refreshes repo graphs and query reports where needed
- dev-context-packet-synthesizer produces one compact packet for downstream engineering teams
- Build durable artifacts, not chat-only summaries
- Return artifact paths, stale areas, and the single packet a downstream team should consume first
- Clean up the team when done
```

**Codex prompt**

```text
Run the installed context_engineering members as a staged context-building flow.

Goal: create a reusable context packet for authentication changes across api, web, and worker repos.

Sequence:
- portfolio_mapper: inventory repos and normalize portfolio-level metadata
- repo_context_curator: identify hot/warm/cold context sources and existing instructions
- code_graph_builder: refresh or validate graphs and query reports for the relevant repos
- context_packet_synthesizer: produce one compact packet for downstream implementation and review workers

Return:
- artifact paths created or refreshed
- gaps or stale evidence
- the exact packet downstream workers should read first
```
