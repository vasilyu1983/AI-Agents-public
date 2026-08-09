# Obsidian And Local Vaults

Use this file when the user has an Obsidian-style vault or another local markdown knowledge base.

## Table of Contents

- [Inventory First](#inventory-first)
- [Preserve Note Semantics](#preserve-note-semantics)
- [Canonical Notes Versus Ingest Folders](#canonical-notes-versus-ingest-folders)
- [Three-Layer Shape](#three-layer-shape)
- [Operating Memory Loop](#operating-memory-loop)
- [Naming And Linking Patterns](#naming-and-linking-patterns)
- [Write-Back Routing Rule](#write-back-routing-rule)
- [Write-Access Recovery](#write-access-recovery)
- [Vault Bootstrap Prompts](#vault-bootstrap-prompts)
- [Privacy Rule](#privacy-rule)

## Inventory First

Before designing retrieval, check:

- frontmatter keys
- alias conventions
- wikilink usage
- tag conventions
- task syntax
- attachment folders
- private vs shared note areas

## Preserve Note Semantics

- Keep path, title, aliases, tags, and timestamps as first-class metadata.
- Preserve wikilinks and backlinks. They are often more valuable than embeddings for note navigation.
- Do not flatten meeting notes, reference notes, tasks, and evergreen notes into one undifferentiated pool.

## Canonical Notes Versus Ingest Folders

For operating-memory workflows, separate the stable knowledge base from the raw feed that updates it.

- Canonical layer: home note, memory note, project pages, client pages, decision logs, action trackers, reusable templates
- Ingest layer: transcripts, meeting dumps, exported docs, raw summaries, or temporary scratch notes

Treat the canonical layer as the place the agent should trust first. Treat the ingest layer as evidence that still needs routing and summarization.

## Three-Layer Shape

When notes are part of an agent memory system, use three layers:

- session memory: one small orientation note or repo memory file for the always-loaded layer
- canonical graph: durable notes, home pages, decision logs, and project pages
- ingest pipeline: transcripts, recordings, exports, and scratch captures awaiting routing

Each layer solves a different problem. Do not ask the ingest layer to behave like curated knowledge.

## Operating Memory Loop

For a practical Obsidian workflow, the minimum useful shape is:

- one memory or onboarding note that explains the system and naming conventions
- one home note that links to the core work areas
- stable destination notes for actions, decisions, and project or client state
- templates for recurring note types so write-back stays consistent

This lets an agent read stable context, inspect fresh artifacts, and then update the right canonical destinations instead of creating more disconnected notes.

## Naming And Linking Patterns

For retrieval-heavy vaults:

- prefer titles that read like claims, decisions, or questions, not vague buckets
- use home notes or maps of content to expose the topology of the vault
- write wikilinks so they carry meaning in the sentence around them, not just path-like references

Examples:

- Better: `memory graphs beat giant memory files`
- Better: `hybrid retrieval beats pure semantic search for note vaults`
- Worse: `memory-notes`
- Worse: `retrieval-stuff`

Good titles and links improve retrieval even before embeddings or search ranking help.

## Write-Back Routing Rule

If the user explicitly wants synchronized notes:

- write summaries to summary destinations
- write decisions to a decision log
- write actions to one task tracker or project page
- link back to the raw artifact instead of copying everything into canonical notes

Do not let every transcript become a top-level note the agent treats as equal to curated notes.

## Write-Access Recovery

When an agent has write access to the vault (Claude Code, Cowork, or any tool that
edits `.md` files in place), expect occasional incorrect overwrites of memory or
canonical notes. Keep a periodic, date-stamped snapshot of the vault in a directory
the agent cannot read or write — weekly is the common cadence — so a corrupted note
can be restored without losing the rest of the session work.

This is overwrite recovery against the *agent itself*, not a durability backup.
Cloud sync, Obsidian's file-recovery plugin, and git history inside the vault do
not protect against an agent rewriting a note through its expected write path.

## Vault Bootstrap Prompts

Public starter prompts that build a wiki-style memory vault from a single instruction:

- Karpathy "LLM Wiki" gist —
  https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f — deliberately
  general-purpose template (not Claude- or Obsidian-specific) for an LLM that
  incrementally builds an interlinked markdown wiki from raw sources, with a
  three-part split of raw sources, generated wiki, and schema docs. Useful as a
  starting point for the canonical-graph layer when ingesting existing notes or
  exports.

Treat starter prompts as a scaffold, not a finished memory architecture. They
produce the layout; the three-layer separation (session / canonical / ingest) and
write-back routing rules above still apply.

## Privacy Rule

- Default to read-only local access.
- Exclude private journals, archives, and secrets by explicit allowlist or denylist before indexing.
- Treat synced vaults as potentially mixed-sensitivity corpora until proven otherwise.
