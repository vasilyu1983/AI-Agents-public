# AI-Curated Wiki Pattern (Ganim / Karpathy)

A second legitimate operating mode beyond the [three-layer default](../SKILL.md#three-layer-operating-memory-pattern): **the AI owns the curated layer entirely**, the human only ever appends to a junk-drawer source folder, and AI rebuilds the curated layer on demand. Use this variant when the user is a solo operator capturing source material faster than they can hand-organize it.

Sources:
- Corey Ganim, *Karpathy's Second Brain clearly explained* (2026-04-06)
- Andrej Karpathy, *LLM Knowledge Bases* (2026-04-02)
- AI Edge, *How to Give Claude Perfect Memory* (2026-04-22)

---

## Table of Contents

- [Folder Layout](#folder-layout)
- [Key Invariants](#key-invariants)
- [Compounding Loop](#compounding-loop)
- [Monthly Health Check (non-negotiable)](#monthly-health-check-non-negotiable)
- [Scale Heuristic](#scale-heuristic)
- [Image-Aware Ingest](#image-aware-ingest)
- [LLM-Callable Search Tool](#llm-callable-search-tool)
- [Tooling Stance](#tooling-stance)
- [Snapshot the AI-Owned Layer](#snapshot-the-ai-owned-layer)
- [When to Use This Variant vs the Three-Layer Default](#when-to-use-this-variant-vs-the-three-layer-default)
- [Do Not Mix the Two Variants](#do-not-mix-the-two-variants)

## Folder Layout

```text
project/
  raw/        # human-append only — articles, screenshots, transcripts, meeting notes, bookmarks
  wiki/       # AI-rewritten — one .md per topic, INDEX.md, [[wikilinks]], summary-first
  outputs/    # AI-generated answers, reports, briefings against the wiki
  CLAUDE.md   # or AGENTS.md — schema file: KB focus, wiki rules, what to do on new raw sources
```

## Key Invariants

- **`raw/` is append-only by the human.** Never reorganized by hand. Never edited by AI.
- **`wiki/` is AI-owned.** Human-edited changes will be overwritten on the next rebuild. Fix errors via the prompt or `raw/`, not wiki files.
- **`outputs/` is generated artifact storage.** Saving good outputs back into `raw/` compounds knowledge over time.
- **`CLAUDE.md` / `AGENTS.md` carries the schema.** Topic focus, wiki rules (one `.md` per topic, mandatory `INDEX.md`, `[[wikilink]]` format, summary-first paragraphs), what to do when new raw sources arrive.

## Compounding Loop

1. **Dump.** Human pastes anything into `raw/` — articles, screenshots, transcripts, bookmarks. No naming discipline required.
2. **Compile.** Prompt: *"Read everything in `raw/`. Compile a wiki in `wiki/` following the rules in CLAUDE.md. Create INDEX.md first, then one `.md` per major topic. Link related topics. Summarize every source."*
3. **Query.** Ask questions against the wiki: gap analysis, cross-source comparison, briefings, contradiction detection.
4. **Save back.** Store good outputs in `outputs/` — fold them back via `raw/` to make them wiki-grade.

## Monthly Health Check (non-negotiable)

Without a health check, AI errors compound: the next answer builds on the previous mistake, and errors become load-bearing. Run monthly:

> *"Review the entire `wiki/` directory. Flag contradictions between articles. Find topics mentioned but never explained. List claims not backed by a source in `raw/`. Suggest 3 new articles to fill gaps."*

Skip it and the wiki silently rots into a confident hallucination.

## Scale Heuristic

At **~100 articles / ~400K words**, no vector RAG is needed. The LLM agent auto-maintains `INDEX.md` and short per-article summaries, and reads only the relevant articles per query. Treat this as the "don't reach for vector infrastructure yet" threshold.

- Below it: the compile loop + index file beats embeddings on both latency and grounding fidelity.
- Above it: retrieval architecture starts to matter — route to [`../../ai-rag/SKILL.md`](../../ai-rag/SKILL.md).

This is why the Ganim invariants work without a vector store: the AI-owned `wiki/` is itself the retrieval index. The summary-first-paragraph rule and `INDEX.md` are not stylistic — they are the substitute for an embedding index at this scale.

## Image-Aware Ingest

Two ingest patterns worth adopting verbatim (from Karpathy):

- **Web Clipper → `raw/`**: Obsidian Web Clipper extension converts web articles to `.md` with structure preserved. Replaces ad-hoc copy-paste.
- **Image-hotkey**: downloads all images referenced by the clipped article into `raw/images/` at clip time. Without this, articles become text-only by accident and visual claims silently disappear.

For non-Obsidian users: any clip-to-markdown + image-mirror pipeline works (`monolith`, `pandoc --extract-media`, or a small `<img>`-walking script). The pattern is *capture images at ingest time*, not *fetch on demand* — original sources rot.

## LLM-Callable Search Tool

Beyond `INDEX.md`, expose the wiki as a CLI the LLM invokes as a tool during larger queries:

- A web UI serves the human.
- A **CLI** lets the LLM run sub-queries (`search "X"`, `list-articles topic=Y`) without consuming context on the full wiki.

Even a 20-line `grep`-based script is enough at first; the contract matters more than the implementation. Anti-pattern: building a search UI for humans only and forcing the LLM to read the whole `INDEX.md` on every query.

## Tooling Stance

Plain `.md` files + schema file + AI beats any plugin stack for this use case. Obsidian still works fine as a *viewer* (renders wikilinks, navigates `INDEX.md`) but is not required to author or maintain the KB. Do not steer users toward heavy tool selection when the folder layout above is sufficient.

## Snapshot the AI-Owned Layer

`wiki/` is regenerable from `raw/`, but two failure modes break that guarantee:
- (a) The AI compounding loop silently overwrites a correct entry (model drift, bad prompt, hallucinated source).
- (b) A `raw/` source gets deleted or rewritten between rebuilds, so the next rebuild cannot reproduce the previous `wiki/`.

**Mitigation — point-in-time snapshots:**

- After any major compounding-loop run (weekly minimum): copy `wiki/` to a sibling `wiki-snapshots/YYYY-MM-DD/` outside the AI's write scope.
- Keep snapshots read-only. Do not include them in the agent's file-write allowlist.
- Pair snapshots with the monthly health-check prompt — the health check flags contradictions; the snapshot lets you roll back.
- Six months of weekly snapshots is the floor. Markdown diffs compress well; do not prune aggressively.

This is specific to layers where an AI agent has write authority over its own memory — not generic backup hygiene.

## When to Use This Variant vs the Three-Layer Default

| Use AI-curated variant when… | Use three-layer default when… |
|---|---|
| Solo operator capturing source faster than organizing it | Team or individual maintaining a long-lived canonical notebook |
| Human will not hand-edit notes — wants AI to do all curation | Human values hand-curated phrasing, decisions, and structural choices |
| Topic is research/intel — source material churns rapidly | Topic is operational memory — durable decisions and process notes |
| Acceptable to rebuild `wiki/` periodically from raw sources | Canonical notes are themselves the artifact you care about |

## Do Not Mix the Two Variants

If the human starts hand-editing `wiki/`, the AI-curated invariant breaks: rebuilds overwrite human changes. Pick one mode per project. If both are needed, run two separate projects and link between them at the index level only.
