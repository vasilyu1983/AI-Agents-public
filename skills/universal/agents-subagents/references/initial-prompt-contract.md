---
description: Eight-field launch-prompt contract and Goal/Constraints/Owned-files handoff template.
last_verified: 2026-09-16
status: stable
---

# Initial Prompt Contract

## Table of Contents

- [Contract Fields](#contract-fields)
- [Handoff Template](#handoff-template)
- [Rules](#rules)
- [Retrieval Follow-Ups](#retrieval-follow-ups)

When `agents-subagents` recommends a team, member, or debate flow, it should also prepare the first launch prompt. Use this file as the authoritative contract.

## Contract Fields

Every launch prompt should include:

1. **Goal** — what decision, review, implementation, or diagnosis is needed.
2. **Required context** — the must-have business, repo, diff, incident, or product inputs.
3. **Optional context** — `docs/` artifacts, graphs, reports, logs, metrics, or market inputs.
4. **Member ownership** — who owns which lens or deliverable.
5. **Execution mode** — parallel, staged, or hybrid.
6. **Debate rule** — whether members should argue after independent reads.
7. **Synthesis owner** — who writes the final recommendation, or whether the parent thread synthesizes.
8. **Cleanup expectation** — whether the parent thread, lead, or runtime should close the team or worker set after synthesis.

Reusable short-form and full-form launch prompts: [team-prompt-patterns.md](team-prompt-patterns.md). Scenario-to-team examples: [team-scenarios.md](team-scenarios.md).

For firm-specific legal/regulatory matters, `Required context` must include any matching
`project-*` family records. The lead supplies them as source material; general legal
members do not self-link to project skills. If the matter concerns a client with its own
project family, route through that client's `project-<client>-router` first and attach the
relevant `project-<client>-*` context or corporate-memory records before asking a general
`legal-*` member for a conclusion.

## Handoff Template

Every delegated brief should be explicit and bounded.

```text
Goal:
Constraints:
Owned files:
Read-only context:
Do-not-touch:
Deliverable:
Verification:
```

## Rules

- Give owned files whenever possible.
- Pass file paths, not whole modules.
- State the output shape up front.
- Say "review-only" explicitly when applicable.
- Require sources for research tasks.

## Retrieval Follow-Ups

A retrieval or research worker sees only its brief; the parent holds the purpose behind it. Close that gap in a bounded loop:

1. Put the objective (the decision the answer feeds) in the brief, not only the query.
2. Judge each return against that objective before accepting it.
3. If it falls short, send a follow-up naming the specific gap; the worker goes back to the source, not to its earlier summary.
4. Cap follow-ups at a small number set in local policy. At the cap, stop and either accept the answer with its gaps stated or re-plan the brief. Do not keep asking the same worker.
