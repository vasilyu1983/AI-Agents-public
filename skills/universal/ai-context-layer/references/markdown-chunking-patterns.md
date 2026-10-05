# Markdown Chunking Patterns

## Table of Contents

- [The four rules](#the-four-rules)
- [Algorithm](#algorithm)
- [What to keep what to strip](#what-to-keep-what-to-strip)
- [Anchors that survive](#anchors-that-survive)

> Corpus-type-general chunking (PDF, table, sliding window, code) lives in
> [`../../ai-rag/references/chunking-patterns.md`](../../ai-rag/references/chunking-patterns.md).
> Decision page is
> [`../../ai-rag/references/chunking-strategies.md`](../../ai-rag/references/chunking-strategies.md).
> This file is markdown-specific — citation-stable anchors, ADR shape,
> frontmatter as metadata, git-anchored doc bodies.

Markdown is the dominant content format in modern context layers — ADRs,
runbooks, design notes, regulatory memos, READMEs. Naive
`split_by_n_chars(text, 1000)` destroys the structure that makes markdown
useful for retrieval. This reference codifies the chunking rules RA10 and
RA1 depend on.

For deep retrieval-eval coverage (chunking experiments, ablations, reranker
choice) defer to the `ai-rag` skill. This reference is the *interface* RA10
needs.

## The four rules

1. **Heading-aware split.** A chunk boundary is a heading boundary. Never
   split mid-section. The chunk's `chunk_anchor` is the heading path:
   `## Risk appetite > ### Crypto > #### Stablecoin sub-thresholds`.
2. **Code-block-atomic.** A fenced code block is one chunk or part of the
   parent section's chunk. Never split a code block. Preserve the language
   tag.
3. **Frontmatter is metadata, not content.** YAML/TOML frontmatter
   (`as_of`, `owner`, `last_verified`) is parsed and stored as columns on the
   chunk row, not embedded into the chunk text.
4. **Soft size cap, not a hard one.** Aim for ~600–1200 tokens per chunk; if
   a single section exceeds the cap, split *between paragraphs*, not mid-
   sentence, and tag the continuation with the same `chunk_anchor` plus
   `#part-2`, `#part-3`.

## Algorithm

```python
def emit_chunks(file_text: str, source_path: str, source_commit_sha: str):
    frontmatter, body = parse_frontmatter(file_text)
    sections = split_by_headings(body, max_depth=4)

    for sec in sections:
        if not sec.text.strip():
            continue                        # skip empty sections
        for piece in soft_split(sec.text, target_tokens=900, max_tokens=1400):
            yield Chunk(
                text          = piece.text,
                anchor        = sec.heading_path + piece.suffix,
                source_path   = source_path,
                commit_sha    = source_commit_sha,
                content_hash  = blake3(normalize(piece.text)),
                meta          = frontmatter,        # owner, as_of, etc.
            )
```

`soft_split` only fires when a section is too large; it splits at paragraph
boundaries and never inside a fenced code block.

## What to keep, what to strip

- **Keep.** Headings (the chunk's own heading path is included in the
  embedded text — improves recall on "find the section about X"), inline
  code, links (with text + URL preserved), tables in markdown form.
- **Strip.** HTML comments (`<!-- ... -->`) — they often carry stale notes.
  Footnote markers when the footnote is in a different chunk. Image data URIs.
- **Promote.** Frontmatter values to columns. `<!-- last_verified: 2026-05-01 -->`
  in a section header is promoted to a `last_verified` column on the chunk
  row. The convention used by `requirements-hub` and the
  `vendor-landscape.md` reference in this skill.

## Anchors that survive

`chunk_anchor` must round-trip to a working link:

```
repo://acme/requirements-hub@<sha>:business/cards/as-is/risk-appetite.md#crypto--stablecoin-sub-thresholds
```

GitHub renders headings as `#crypto--stablecoin-sub-thresholds`; match that
slugger so the link opens to the exact section a human reviewer would see.
Keep the slugger pinned — switching slug algorithms invalidates every anchor
and breaks audit trails (A13).

## Special markdown shapes

- **ADRs** — extract `Status`, `Context`, `Decision`, `Consequences` as
  separate chunks; the agent often wants only `Decision`.
- **Runbooks** — split per `## Step`. The first chunk that matches a query
  often contains the actual command.
- **Design docs with embedded diagrams** — Mermaid blocks are code blocks
  (atomic). Keep them with their containing section; the diagram is the
  answer for "show me the architecture."
- **Tables of acronyms / glossaries** — usually one chunk per file, not per
  row; the pairing matters more than the individual rows.

## Multi-file context

When chunks are recalled across files, ordering matters. Sort by
`(source_repo, source_path, chunk_anchor)` so a reviewer can read the
selected slice as a coherent document, not a shuffled hit list.

## Anti-patterns

- **Fixed-size character split.** Throws away structure for no gain.
- **Including frontmatter as text.** Pollutes embeddings with `as_of:`
  strings that recur identically across the corpus.
- **Splitting code blocks.** Halves a SQL or Python snippet and the agent
  cannot reuse it.
- **Slug instability.** Computing `chunk_anchor` differently across ingest
  runs invalidates citations.
- **Treating PR descriptions / chat threads as markdown content.** They are
  episodic. Extract atomic facts via the P2 / P6 path; do not embed the
  whole thread (A1).

## See also

- `git-anchored-ingestion.md` — what the ingest pipeline does with these
  chunks.
- `reference-architectures.md` → RA10.
- `retrieval-and-grounding.md` — how chunks are ranked and grounded.
- `ai-rag` skill — deep chunking and reranker evaluation.
