# Catalog Page Template — Compiled Truth + Timeline

> **Source**: Adapted from [garrytan/gbrain](https://github.com/garrytan/gbrain) at commit `adb02b7826a010700efc968b18df8aaf17d8ffa1`. License: MIT. Extracted 2026-04-13.

Canonical shape for `catalog/<repo>.md` pages (and, by extension, any compiled-layer page that synthesizes durable facts about a single entity). Every page has exactly two zones separated by a horizontal rule (`---`):

- **Above the line — Compiled Truth**: current synthesis. Rewritten whenever new evidence changes the state of play. Read the top, know the state in 30 seconds.
- **Below the line — Timeline**: append-only evidence log. Every fact in the Compiled Truth section traces back to an entry here. Entries are never rewritten — only new entries are appended.

## When to Use This Template

- Catalog pages in a portfolio hub (`catalog/<repo>.md`)
- Concept notes that synthesize across multiple repos (`concepts/<topic>.md`)
- Architecture decision records that need both a current-state summary and an audit trail
- Any page where the question "what is true *now*?" and the question "how did we get here?" have different answers

## Template (Repo Catalog Page)

```markdown
---
type: repo_catalog
repo_id: payments-ledger
title: payments-ledger — Payments Ledger Service
tags: [payments, postgres, kafka, dotnet]
last_compiled: 2026-04-13
last_verified: 2026-04-13
---

## Executive Summary

One paragraph. What this repo does, who owns it, why it exists. If a reader only reads this, they should know whether to keep reading.

## State

- **Runtime**: .NET 9, deployed as a Kubernetes service
- **Storage**: PostgreSQL 16 (primary), Redis (cache)
- **Messaging**: Kafka producer + consumer for `payments.*` topics
- **Owner**: Payments Platform team
- **Status**: Active

## Capabilities

- Double-entry ledger with immutable journal
- Idempotent settlement API
- Event streaming to downstream reconciliation

## Interfaces

- HTTP: `POST /v2/journal/entries`, `GET /v2/accounts/{id}/balance`
- Kafka topics published: `payments.journal.v1`, `payments.settlement.v1`
- Kafka topics consumed: `payments.command.v1`

## Open Threads

Items in flight. Removed from this section when resolved (and the resolution is appended to the Timeline below).

- [ ] Migration from legacy `payments-ledger.v1` endpoints — target Q2
- [ ] Decision pending on partitioning strategy for archive tables

## See Also

- [payments](payments.md) — upstream producer of settlement commands
- [sc.reconciliation](sc.reconciliation.md) — downstream consumer
- [concepts/double-entry-ledger](../concepts/double-entry-ledger.md)

## Evidence Coverage

- Profile: `verified` (scanned 2026-04-13)
- API contract: `verified` (openapi parsed)
- Messaging topology: `subset-verified` (producer confirmed, consumer inference-based)
- Storage: `verified` (from DbContext)

---

## Timeline

- **2026-04-13** — Catalog page regenerated from profile scan. No structural changes; cache layer added to State section. [Source: scripts/build_artifact_set.py, 2026-04-13 09:12 UTC]
- **2026-04-10** — Added Redis cache for account-balance lookups. Resolved open thread "cache layer decision". [Source: PR payments-ledger#412, 2026-04-10 14:30 UTC]
- **2026-03-28** — Upgraded to .NET 9. Runtime field updated above. [Source: Dockerfile diff, payments-ledger@9a3b2c1, 2026-03-28 11:00 UTC]
- **2026-03-15** — Initial profile scan. Repo classified as `service`, language `.NET`, confidence 0.92. [Source: scripts/scan_repo.py, 2026-03-15 08:00 UTC]
```

## Rules of the Template

1. **Above-line rewrites, below-line appends**. When new evidence arrives, update the Compiled Truth section in place — but *never* edit or delete a Timeline entry. The Timeline is the audit trail; if an earlier entry turned out to be wrong, add a new entry correcting it rather than modifying the old one.
2. **Every Compiled Truth claim has a Timeline citation**. If a State field exists above the line but no Timeline entry below the line supports it, the claim is unverified — flag it during freshness checks.
3. **Open Threads move, not disappear**. When an open thread is resolved, *remove it from the Open Threads list* and *append the resolution to the Timeline* with the same day's date. The fact that it existed is preserved in the log.
4. **Source format is strict**: `[Source: <who/what>, <date> <time> <tz>]`. Who = script name, PR number, human name, tool output, etc. The format lets you grep for unattributed claims.
5. **`last_compiled` vs `last_verified`**: `last_compiled` is when the page was last regenerated from profile data. `last_verified` is when a human or trusted script last confirmed the Compiled Truth still matches reality. They can differ; use `last_verified` for freshness-check exit gates.

## Why Two Zones

- *"What's the current state?"* is a one-screen read when the synthesis is pre-computed above the line. No one has to scroll through 200 timeline entries and assemble the answer in their head.
- *"How did we get here?"* is a full audit trail when the evidence log is below the line and never rewritten.
- *"Why do I believe this?"* traces from a Compiled Truth claim to its supporting Timeline entries via the source citation.

A single append-only log fails the first question. A single rewriteable summary fails the second and third. The two-zone split is how both questions can be cheap to answer at once.

## Generation vs Hand-Editing

The Compiled Truth section *can* be human-edited, but the sustainable pattern is to generate it from the structured profile JSON plus the Timeline. That way:

- Profile scan updates (language, dependencies, manifests) flow automatically into the State fields above the line.
- Human commentary (Assessment, Why it matters, Strategic notes) is the part humans actually spend time on.
- Freshness checks can compare generated Compiled Truth against the last-known snapshot and flag anything that drifted without a Timeline entry explaining why.

Do not let Compiled Truth become an ungrounded prose summary written from memory. If a claim can't be traced to profile JSON, graph edges, or a Timeline entry, it doesn't belong above the line.

## Related

- [references/hub-design-patterns.md](../references/hub-design-patterns.md) — Why compiled pages should be generated, not hand-written
- [references/hub-operations-playbook.md](../references/hub-operations-playbook.md) — How to wire this template into the build pipeline
- [references/hub-freshness-checking.md](../references/hub-freshness-checking.md) — Drift detection that respects the above-line / below-line split
