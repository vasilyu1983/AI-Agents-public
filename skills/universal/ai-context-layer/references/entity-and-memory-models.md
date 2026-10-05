# Entity And Memory Models

## Table of Contents

- [Entity Profiles](#entity-profiles)
- [Memory Model](#memory-model)
- [Required Fields For Learned Memory](#required-fields-for-learned-memory)
- [Self-Editing Memory (Letta/MemGPT Pattern)](#self-editing-memory-lettamemgpt-pattern)
- [Memory Provenance And Source Trust](#memory-provenance-and-source-trust)
- [Rules](#rules)

## Entity Profiles

Every app context layer should start with explicit entities:

- user
- organization or customer account
- brand or product
- domain or site
- surface or channel

Each entity should have:

- stable ID
- owner scope
- source of truth
- update path
- ACL boundary

## Memory Model

Use at least three memory classes:

1. **Profile memory**
- durable preferences, settings, declared facts

2. **Behavioral memory**
- actions taken, routes visited, repeated choices, saved workflows

3. **Outcome memory**
- whether recommendations were executed, helped, ignored, or failed

## Required Fields For Learned Memory

- `id`
- `entity_id`
- `entity_type`
- `memory_type`
- `value`
- `source`
- `confidence`
- `created_at`
- `updated_at`
- `expires_at` or `ttl`
- `owner_scope`
- `consent_basis` when relevant

## Self-Editing Memory (Letta/MemGPT Pattern)

Some agents need to maintain and update their own memory as they work:

- **Core memory**: a bounded block of structured context that is always in the model's context window. The agent reads and writes it directly. Analogous to RAM — fast, small, always visible.
- **Archival memory**: a larger store that the agent pages in on demand via tool calls. Analogous to disk — unlimited but requires explicit retrieval.
- **Self-editing**: the model edits its own core memory block after each interaction, deciding what to retain, update, or archive. This enables long-running agents with persistent persona and evolving knowledge.

Use self-editing memory when:

- The agent runs across many sessions with the same user or entity.
- Preferences and learned facts must persist and evolve without external orchestration.
- The agent needs to manage its own context window efficiently.

Prefer simpler structured memory (profile/behavioral/outcome classes above) when:

- Memory updates are orchestrated by the application, not the model.
- The memory model is well-defined upfront and does not evolve dynamically.
- Audit and compliance require that memory changes are application-controlled.

## Memory Provenance And Source Trust

The `source` and `confidence` fields above are only useful if `source` carries a
*type*, not just an identifier. Anti-patterns A13 (provenance as optional metadata)
and A14 (no confidence model) say the fields must exist; this section says how to
rank and evolve them.

### Source-trust hierarchy

Rank each contributing source by type before it influences consolidation or
inference weighting:

1. **Bootstrapped data** — pre-loaded from an internal system of record (CRM,
   billing, account service). Highest trust, and the standard fix for cold start:
   initialize a new user's memories from it rather than opening with an empty
   profile. Still subject to P1 — bootstrapping *seeds* derived memory, it does not
   move operational truth into it.
2. **User input** — split it. Explicitly provided (form field, settings toggle,
   direct statement) is high-trust. Implicitly extracted from conversation is
   materially lower-trust and must be marked as inferred (see Rules below).
3. **Tool output** — data returned by an external tool call. Generating durable
   memories from tool output is discouraged: such memories are brittle and go stale
   as soon as the underlying system changes. Tool results belong in short-term
   caching, not the memory store.

When sources contradict, resolve by this hierarchy first, then by recency, then by
corroboration count — not by whichever row was written last.

### Many-to-many lineage

Consolidation makes the source-to-memory mapping many-to-many: one memory can blend
several sources, and one source can be segmented into several memories. Model the
lineage as an explicit edge set, not a single `source` scalar.

The consequence is a deletion rule. When a user revokes access to one data source,
deleting every memory that source ever *touched* is over-aggressive — it destroys
memories that other, still-valid sources also support. The precise fix is to
**regenerate the affected memories from the remaining valid sources**. It is more
expensive computationally, and it is the behavior a GDPR erasure or consent-withdrawal
request actually requires.

### Confidence as an evolving score

Confidence is a state, not a write-time constant:

- rises on corroboration — independent trusted sources agreeing on the same claim;
- decays with age as the memory goes stale;
- drops when contradictory information arrives;
- below a floor, the memory is archived, pruned, or excluded from citation.

At inference time, inject the confidence score into the prompt alongside the memory
so the model can weigh reliability itself instead of treating every retrieved row as
equally true. Confidence is internal reasoning scaffolding: do not surface these
scores to the end user (see `context-assembly.md` §Anti-patterns).

<!-- Source: Milam & Gulli, "Context Engineering: Sessions, Memory" (Google, Nov 2025), pp. 49-52 -->

## Rules

- Rank contributing sources by type (bootstrapped > explicit user input > inferred
  user input; tool output not a memory source) before weighting or resolving conflicts.
- On source revocation, regenerate affected memories from remaining valid sources
  rather than deleting every memory the source touched.
- Never overwrite operational truth with a model-inferred memory.
- Never store private context without an owner scope.
- Keep deletion and expiry explicit.
- Prefer compact structured memory over raw transcript replay.
- Mark inferred memories separately from user-declared memories.
- When using self-editing memory, enforce edit-auditing so the model cannot silently overwrite critical facts.
