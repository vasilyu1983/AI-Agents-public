# Multi-Source Wiki Ingestion (P7 Pipeline)

## Table of Contents

- [When to use this](#when-to-use-this)
- [The pipeline (six stages)](#the-pipeline-six-stages)
- [Idempotency contract](#idempotency-contract)
- [Supersede vs overwrite contract](#supersede-vs-overwrite-contract)
- [Contradiction queue](#contradiction-queue)
- [Source-type cookbook](#source-type-cookbook)
- [Anti-pattern catalog](#anti-pattern-catalog)
- [Recipes](#recipes)
- [Composition with other patterns](#composition-with-other-patterns)
- [Reference implementations](#reference-implementations)
- [Failure modes](#failure-modes)
- [Check](#check)

**Purpose.** Source-agnostic pipeline for taking ANY structured source (events,
tickets, messages, commits, calendar items, audit logs) and producing idempotent
edits to a P7 LLM Wiki. Covers the write path only. Pair with
`knowledge-compilation-and-wiki-pattern.md` (page model, supersede contract,
confidence model) and `patterns-catalog.md` (P-catalog placement). Read path:
`../../ai-rag/references/wiki-grounded-retrieval.md`.

## When to use this

Use when ALL hold:

- ≥2 source systems feed the same entity graph (person, repo, project, customer, control).
- Supersede + provenance required, not just bulk re-ingest.
- Re-running ingestion must be idempotent (same input → same wiki state).
- Reviewers must trace any wiki claim to a source event with a stable id.

Do **not** use when: a single source, append-only, no entity resolution needed
(use `git-anchored-ingestion.md`), or the "wiki" is a vector store with no page
model and no typed extraction (anti-pattern A16).

## The pipeline (six stages)

```text
source → extractor → entity resolver → reconciler → page writer → run log
                   ↘ contradiction queue
                   ↘ supersede records
```

### 1. Source

Contract: typed, identifiable, replayable. Required fields: `source_episode_id`
(stable across re-pulls), `source_system`, `pulled_at`, `source_event_ts`
(from the source — canonical time for ordering), `payload`.

Sources must be replayable from any point. Destructive consumption (pop-from-queue)
is forbidden — mirror to an append-only log before ingestion if the upstream
system does not support replay.

### 2. Extractor

Pure function: source payload → typed entities + relations + atomic facts.
Every emitted item carries `source_episode_id`, `extraction_confidence`,
`extractor_version`.

Pin extractor version. Non-deterministic extractors (LLM calls without fixed
model + seed) break replay safety. Skipping extraction entirely and embedding
raw text is anti-pattern A16 — the most common reason a P7 wiki degrades into
an indexed document store.

### 3. Entity resolver

Each source carries its own id space (`chat_user_id`, `code_user_id`,
`ticket_account_id`, `calendar_email`). The resolver maps source ids →
`canonical_entity_id` via:

1. Direct lookup in the identity-bridge table.
2. Deterministic match: verified email or org-issued id.
3. Ambiguous — no deterministic match → escalate to reconciler. Do NOT
   auto-merge on embedding similarity or name string match.

**Identity-bridge table schema:**

```sql
CREATE TABLE identity_bridge (
  id            uuid PRIMARY KEY,
  canonical_id  text NOT NULL,
  source_system text NOT NULL,
  source_id     text NOT NULL,
  confidence    numeric(3,2) NOT NULL,
  bridge_method text NOT NULL,      -- direct | verified_email | org_id | manual
  bridged_at    timestamptz NOT NULL,
  superseded_by uuid REFERENCES identity_bridge(id)
);
CREATE UNIQUE INDEX uq_bridge ON identity_bridge (source_system, source_id)
  WHERE superseded_by IS NULL;
```

Bridge table mutations are their own audited event; they never happen inside
an ingest transaction.

### 4. Reconciler

For each extracted item with a resolved entity:

```python
match = lookup(entity_id, fact_type, existing_facts)
if match is None:                         → NEW: emit page-create or fact-append
elif agrees(item, match):                 → UPDATE: reinforce (bump confidence, append source)
elif structurally_exclusive(item, match): → CONTRADICTION: → queue, do NOT write
else:                                     → SUPERSEDE: close match window, insert item
```

Sort on `source_event_ts` before reconcile, never on `pulled_at`. Auto-resolution
by "most recent wins" is anti-pattern (see catalog); all structural conflicts
route to the contradiction queue.

### 5. Page writer

Idempotent and atomic per page (one transaction, one write). Writes both the
page diff and a structured supersede/contradiction sidecar. Updates the page
header on every write.

```json
{
  "page_id":              "<stable entity page id>",
  "write_type":           "create | update | supersede | contradiction_flagged",
  "last_source_event_id": "<most recent source_episode_id in this write>",
  "supersede_records":    [{ "old_fact_id": "...", "new_fact_id": "...", "reason": "..." }],
  "contradiction_refs":   ["<contradiction_id>"],
  "page_markdown_diff":   "<unified diff>",
  "written_at":           "<ISO-8601>"
}
```

The `last_source_event_id` guard prevents double-writes on replay. Emitting
unstructured markdown only — no sidecar — is anti-pattern (catalog row 9).

### 6. Run log

Append-only. One row per run per source. Required columns:
`run_id | started_at | source_system | episode_window_start | episode_window_end |
extracted_count | new_count | update_count | supersede_count | contradiction_count |
page_write_count | run_duration_ms | status (running|ok|failed|rolled_back) | error_detail`.

Every page write traces to a `run_id`; every `run_id` traces to episode ids.
Without this, "why did this page change last Tuesday" has no answer.

## Idempotency contract

Three invariants, all required:

1. **Replay safety.** Re-running ingestion over any source window produces the
   same wiki state. Achieved by `source_episode_id` deduplication at the
   extractor and `last_source_event_id` guard at the page writer.
2. **Order independence within a window.** Sort on `source_event_ts`, not
   `pulled_at`, before reconcile.
3. **Source-failure isolation.** Failure in one source must not corrupt pages
   from another. Per-source transactions + per-source dead-letter queue.

## Supersede vs overwrite contract

Never overwrite a fact row. When new evidence displaces an old claim: close the
old row's validity window (`valid_to = now`, `superseded_by = new_row_id`);
insert the new row.

Multi-source twist: when two sources contradict each other and both remain
authoritative (neither is stale), do not pick a winner heuristically. Emit to
the contradiction queue. A reviewer resolves with a rationale; that rationale
becomes the supersede record's `reason` field. The resolution rationale is the
only record of why the wiki chose one value over another — omitting it means the
next re-ingest cannot distinguish a legitimate resolution from a data error.

## Contradiction queue

**What enters:** structural conflicts the reconciler cannot auto-resolve.
**What exits:** a supersede record with `resolved_by` and `resolution_rationale`.

```sql
CREATE TABLE contradiction_queue (
  contradiction_id      uuid PRIMARY KEY,
  entity_id             text NOT NULL,
  fact_type             text NOT NULL,
  conflicting_fact_ids  text[] NOT NULL,
  source_episode_ids    text[] NOT NULL,
  detected_at           timestamptz NOT NULL,
  severity              text NOT NULL,   -- blocking | advisory
  resolution_state      text NOT NULL,   -- open | resolved | dismissed
  resolved_by           text,
  resolved_at           timestamptz,
  resolution_rationale  text
);
```

`severity = "blocking"` prevents the entity page from being served downstream
until resolved. An unbounded queue signals identity-bridge gaps or reconciler
rules that are too tight — investigate the pattern, do not loosen rules in bulk.

## Source-type cookbook

| Source type | Stable id | Supersede triggers | Entity resolution field | Notes |
|---|---|---|---|---|
| Event log | `event_id` | actor state change | `actor_id` | Idempotent by construction; aggregations compute downstream |
| Ticket | `ticket_key + last_modified` | status, assignee, scope change | `assignee_id`, `reporter_id` | Each status transition is a fact row, not an overwrite |
| Message | `message_id` or `thread_id + sequence` | none (append-only) | `sender_id` | Metadata only; content extraction is a separate stage with its own lawful basis |
| Commit | `commit_sha` | none (sha is content hash) | `author_email` | See `git-anchored-ingestion.md` for tombstone-not-delete treatment |
| Calendar | `meeting_id + occurrence_id` | RSVP, time, cancellation | `organizer_email` | Recurring meetings need both ids; cancelled occurrence closes time-window fact, entity stays |

## Anti-pattern catalog

| Anti-pattern | Consequence | Corrective recipe |
|---|---|---|
| Pull-then-overwrite the page | Audit trail lost; as-of queries break | Supersede records; close validity window, insert new row |
| Entity resolution by embedding similarity or name string | Silent wrong-merges undetectable until audit | Stable-id bridge only; escalate ambiguous to reconciler |
| One extractor for all sources | Cross-source blast radius; debugging requires re-running everything | One extractor per source; one transaction per source |
| Skip the run log | Cannot explain why a page changed | Append-only run log; every write traces to `run_id` → episode id |
| Confidence increments on re-pull | High-confidence facts from a single source pulled N times | Confidence based on independent source count, not pull count |
| Auto-resolve contradictions by "most recent" | Quiet wrong answers when the older source is correct | Contradiction queue; explicit rationale on every resolution |
| Mix metadata and content extraction in one stage | Purpose creep, over-collection, lawful-basis confusion | Separate stages with separate lawful-basis checks |
| Bridge identities by name string match | Name-collision merges (two "John Smith"s merged) | Verified-email or org-issued-id bridges only |
| Page writer emits unstructured markdown only | Supersede sidecars lost in prose; tooling cannot query them | Structured diff + sidecar JSON; render markdown from structured form |

## Recipes

### R1 — Standing up the pipeline for two sources

1. Define shared entity types; agree on `canonical_entity_id` format (stable,
   opaque, not derived from source ids).
2. Create the identity-bridge table. Populate known mappings manually before
   running any extraction.
3. Write one extractor per source; validate typed output against a sample window.
4. Stand up the reconciler with conservative rules: all disagreements route to
   contradiction queue; no auto-resolution.
5. Stand up the page writer and run log; write to a staging wiki first.
6. Run a bounded backfill (7–30 days). Resolve contradiction queue manually,
   each with an explicit rationale.
7. Verify: every page claim traces to `source_episode_id`; run log shows
   expected counts; no unresolved blocking contradictions.
8. Promote to production. Do not widen auto-resolution rules to clear the queue.

### R2 — Adding a third source to a running wiki

1. Resolve all open contradiction queue items before starting.
2. Add the new source's id space to the identity-bridge table before running
   extraction; unresolved ids from the new source must not reach the reconciler.
3. Run the new extractor against a staging wiki in read-only reconcile mode
   (compute dispositions, do not write). A high CONTRADICTION rate signals
   identity-bridging gaps — fix bridges, do not loosen reconciler rules.
4. When contradiction rate is consistent with existing sources, promote.

### R3 — Backfill / re-ingest

1. Pause live ingestion. Snapshot current wiki state.
2. Re-run from the earliest replay point. The `source_episode_id` deduplication
   guard skips already-processed episodes; only genuinely new or changed episodes
   produce page writes.
3. Diff post-backfill wiki against snapshot. Review all new supersede records.
4. Resolve any new contradiction queue items before unpausing.
5. Unpause. Confirm run log shows no gap in `episode_window_end`.

## Composition with other patterns

- **P2 (Structured memory)** — shares the same extractor output for the
  LLM-served machine surface; write paths diverge at the reconciler.
- **P4 (Temporal knowledge graph)** — P7 pages cite P4 facts; they share
  `source_episode_id`s. Wiki is the human view; graph is the machine view.
- **P7 (LLM Wiki)** — this pipeline is P7's write path. See
  `knowledge-compilation-and-wiki-pattern.md` for page model and confidence decay.
- **P8 (Evidence-bearing retrieval)** — reads the wiki; synthesis pages this
  pipeline produces are the primary surface P8 hits before falling back to raw
  retrieval. See `../../ai-rag/references/wiki-grounded-retrieval.md`.
- **Collector architecture** — the source stage composes with the collector
  pattern (admin-API export, bot-as-participant, or endpoint), chosen per source
  by lawful basis and coverage; see `company-brain-assembly.md` Phase 1.

## Reference implementations

- **Karpathy LLM Wiki v2 writeup (2026-04)** — three-layer pattern (raw
  sources → wiki pages → typed schema), confidence decay, ingest-extract-reconcile
  pipeline. This reference extends the reconcile stage with multi-source entity
  resolution and an explicit contradiction queue.
- **SamurAIGPT/llm-wiki-agent** — open-source reference for the ingest pipeline
  and `graph.html` inspection UI. The episode-id discipline in this reference
  follows the same conventions.
- **Ar9av/obsidian-wiki** — reference targeting Obsidian as the storage and
  review surface; the page writer maps to Obsidian note writes with frontmatter
  provenance blocks.

## Failure modes

- **Replay produces different wiki state** — extractor is non-deterministic
  (LLM classification without pinned model/seed). Fix: deterministic code for
  classification; pin extractor version.
- **Contradiction queue grows unbounded** — reconciler rules too strict, or
  entity resolution producing false-distinct entities. Fix: audit identity-bridge
  gaps before considering rule changes.
- **Pages accumulate many small supersede records** — extractor granularity too
  fine. Fix: extract at coarsest stable grain (status transitions, not every
  field edit).
- **Identity-bridge backfill breaks existing pages** — bridge rows mutated in
  place, retroactively changing canonical ids. Fix: treat bridge rows as
  immutable; use `superseded_by` chain.
- **Source rate-limit during backfill** — large replay window hits API limits
  mid-flight. Fix: windowed replay with checkpoint commits; dead-letter queue
  per window.
- **Run log too large to inspect** — rotate into cold storage by month; maintain
  a summary index keyed by `(source_system, date, status)`.
- **Schema drift in source not detected** — upstream renames a field; extractor
  silently emits nulls. Fix: extractor schema contract test in CI; alert on
  null-rate spike.
- **Content extracted instead of metadata** — message extractor pulls body text
  because it is in the payload. Fix: content extraction gate in the extractor
  contract; separate lawful-basis check required.

## Check

The ingestion pipeline is working if:

- Any wiki claim traces from the page through a fact row to a `source_episode_id`
  and from there to the raw source event.
- Re-running ingestion over the same episode window produces identical wiki state
  (verified by diffing page exports).
- The contradiction queue drains; new items resolve within a defined SLO rather
  than accumulating.
- Confidence reflects independent source count, not pull count; a fact re-ingested
  fifty times from one source does not reach high confidence.
- The run log answers "why did this page change on date X" without inspecting the
  source systems.
- Adding a new source requires only a new extractor and identity-bridge entries —
  no changes to the reconciler, page writer, or run log.
- No content fields appear in extractor output for message or calendar sources
  without an explicit lawful-basis record in the run log.
