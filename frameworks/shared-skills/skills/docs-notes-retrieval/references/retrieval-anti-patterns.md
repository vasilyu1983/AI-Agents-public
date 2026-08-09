# Retrieval Anti-Patterns

Nine anti-patterns that consistently degrade note-vault retrieval quality. Format: what it is / why it fails / fix.

## Table of Contents

1. [Blind chunking at token boundaries](#1-blind-chunking-at-token-boundaries)
2. [Ignoring wikilink topology](#2-ignoring-wikilink-topology)
3. [Keyword-only search on large vaults](#3-keyword-only-search-on-large-vaults)
4. [Packaging draft or abandoned notes](#4-packaging-draft-or-abandoned-notes)
5. [Including attachment files as unparsed blobs](#5-including-attachment-files-as-unparsed-blobs)
6. [Collapsing all three memory layers into one pool](#6-collapsing-all-three-memory-layers-into-one-pool)
7. [Omitting mtime from pack attribution](#7-omitting-mtime-from-pack-attribution)
8. [Re-ranking by embedding similarity alone on a personal vault](#8-re-ranking-by-embedding-similarity-alone-on-a-personal-vault)
9. [Defaulting to semantic search when the task needs exact-phrase citation](#9-defaulting-to-semantic-search-when-the-task-needs-exact-phrase-citation)

---

## 1. Blind chunking at token boundaries

**What it is:** Splitting note content at a fixed character or token count without regard to sentence, paragraph, or heading boundaries. Common when porting generic RAG chunkers to a note vault.

**Why it fails:** Chunks cut across sentences and ideas, severing the semantic unit the note author intended. Retrieval returns fragments that are syntactically broken or contextually opaque. Attribution and wikilink context are lost mid-sentence.

**Fix:** Chunk at natural boundaries — blank lines (paragraphs), `##` headings, or full notes. If a fixed-size chunk is required by an embedding model's limit, pad to the nearest paragraph boundary, not the token limit. Always attach note-level metadata to every chunk.

---

## 2. Ignoring wikilink topology

**What it is:** Treating each note as an isolated document and ignoring `[[wikilinks]]`, backlinks, and the graph structure of the vault.

**Why it fails:** In Obsidian-style vaults, meaning lives in relationships. A sparse note that links to five others only makes sense with its neighborhood. Ignoring topology produces retrieval results that are technically present but semantically thin.

**Fix:** After retrieving a note, check its outbound wikilinks. For sparse notes (< 150 words), include a one-paragraph excerpt from each linked note. Use orphan detection (`scan_vault.py orphans`) to identify notes that are disconnected by design — retrieve those differently or skip them.

---

## 3. Keyword-only search on large vaults

**What it is:** Using plain substring or `grep`-style keyword matching as the sole retrieval mechanism across a vault with hundreds or thousands of notes.

**Why it fails:** High recall, catastrophic precision. Common generic terms like "meeting", "project", or "next steps" match hundreds of notes. The context pack bloats, budget is exhausted by low-signal notes, and the actual target notes may be omitted.

**Fix:** Layer retrieval signals: keyword match narrows the candidate set, then re-rank by (a) recency, (b) inbound link count (hub notes), (c) frontmatter `status: active`. For vaults > 500 notes, add a lightweight vector index (`sqlite-vec` or similar) rather than relying on keyword alone.

---

## 4. Packaging draft or abandoned notes

**What it is:** Including notes with `status: draft`, `status: abandoned`, or without a `status` field in the same retrieval pool as canonical notes.

**Why it fails:** Draft notes contain speculative, incomplete, or contradicted content. When an agent cites a draft as settled fact, downstream outputs are unreliable. Abandoned notes may describe plans that were explicitly rejected.

**Fix:** Filter by `status` frontmatter before packing. Default behavior: exclude notes where `status` is `draft`, `abandoned`, `wip`, or missing and word count < 50. Expose the filter as a flag (`--include-drafts`) for workflows that explicitly need draft content.

---

## 5. Including attachment files as unparsed blobs

**What it is:** Adding paths to attached PDFs, images, audio transcripts, or other non-markdown files to the context pack without parsing them into text first.

**Why it fails:** Binary files are unreadable by the model as raw bytes. Even text-adjacent formats (PDF, DOCX) require parsing before inclusion. Naively including attachment paths wastes budget on unrenderable content and may expose file system internals.

**Fix:** Keep a strict whitelist: only `.md` files enter the pack directly. If an attachment is relevant, check for a paired `.md` summary note (common Obsidian pattern for PDFs). If no summary exists, either skip the attachment or run a text-extraction step first and create a transient summary note.

---

## 6. Collapsing all three memory layers into one pool

**What it is:** Mixing session-orientation files, canonical knowledge notes, and raw ingest artifacts (transcripts, export dumps) into a single retrieval corpus.

**Why it fails:** Each layer has different reliability, staleness, and authority levels. A transcript from last week and a canonical architecture decision record are not equivalent sources. Agents that cannot distinguish them will cite transcripts as policy and treat raw captures as ground truth.

**Fix:** Apply the three-layer model before retrieval: (1) session memory, (2) canonical notes, (3) ingest artifacts. Query canonical notes first. Promote ingest artifacts only when explicitly looking for raw evidence. Never mix layer-3 content into a pack that is framed as authoritative knowledge.

---

## 7. Omitting mtime from pack attribution

**What it is:** Including note content without surfacing the last-modified timestamp in the context pack.

**Why it fails:** Notes go stale. A decision note from 18 months ago may have been superseded by a newer note the retrieval system did not find. Without mtime, the agent cannot reason about freshness and will present outdated guidance as current.

**Fix:** Always include `mtime` in the per-note attribution line immediately after the section heading. Format as ISO-8601 UTC. Optionally add a staleness warning for notes not modified in > 180 days: `> ⚠️ Last modified 2024-10-01 — verify before relying on this note.`

---

## 8. Re-ranking by embedding similarity alone on a personal vault

**What it is:** Using cosine similarity against a query embedding as the only ranking signal, discarding structural signals like inbound-link count, recency, and frontmatter metadata.

**Why it fails:** Personal vaults have high lexical overlap — similar phrasing appears everywhere. Embedding similarity is excellent at surface-level match but misses the author's own hierarchy signals. Hub notes (maps of content, index notes) are often the most authoritative but have low topical density, so they rank poorly on embedding similarity alone.

**Fix:** Use embedding similarity as one signal in a weighted blend: `score = 0.5 * embed_sim + 0.3 * recency_decay + 0.2 * inbound_link_count_log`. Run `scan_vault.py inventory` to pre-compute inbound link counts; compute `recency_decay = 1 / (1 + days_since_mtime / 30)`. Adjust weights for the vault's style.

---

## 9. Defaulting to semantic search when the task needs exact-phrase citation

**What it is:** Reaching for a vector index or embedding re-ranker as the default retrieval mechanism for a personal or team note vault, on the assumption that "semantic" is strictly an upgrade over keyword/full-text search.

**Why it fails:** Embeddings retrieve by meaning, not by exact wording — they will happily surface a paraphrase when the downstream task needs the note that contains a specific decision title, exact date, project code name, or verbatim quote. For citation-integrity work (an agent quoting a decision back to a user, or attributing a claim to a specific note), a semantically-similar-but-wrong note is worse than no result, because it looks correct. Vector indexes also add operational cost (embedding pipeline, re-index on edit, extra dependency) that is unjustified for vaults small enough that `grep`/keyword search already has near-100% recall.

**Fix:** Default to full-text/keyword/path search first. Reach for embeddings only when keyword search demonstrably under-recalls on conceptual queries — in practice, past a few hundred notes or when users ask "what did I conclude about X" rather than "find the note titled X." When embeddings are added, keep exact-match search as a parallel path rather than replacing it, and never let an agent cite a note it found only through semantic similarity without opening and verifying the actual quoted text.
