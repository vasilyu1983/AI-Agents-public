# Contextual Retrieval

LLM-prepended per-chunk context summary at index time. The single highest-lift
retrieval improvement of 2024–2026 for chunked corpora where chunks lose
meaning when isolated from the surrounding document.

Source: Anthropic, "Introducing Contextual Retrieval" (Sep 2024). Reported
**~35% reduction in retrieval failure rate** with contextual embeddings alone,
**~49%** combined with contextual BM25, **~67%** combined with reranking.

## Table of Contents

- [The Pattern](#the-pattern)
- [When To Use](#when-to-use)
- [When To Skip](#when-to-skip)
- [Prompt Template](#prompt-template)
- [Storage](#storage)
- [Cost And Caching](#cost-and-caching)
- [Anti-Patterns](#anti-patterns)
- [Composition](#composition)

## The Pattern

For each chunk, before embedding:

1. Send the **full document** + **the specific chunk** to a small/fast LLM
2. Ask for a 50–100 token summary that situates the chunk inside the document
3. Prepend the summary to the chunk text
4. Embed the prepended text; store both prepended and original
5. At query time, retrieve against the contextualized embeddings; show the
   original (or both) to the generator

This is an **index-time** pattern. Never run contextualization at query time —
it would defeat the purpose and explode cost.

## When To Use

- Document chunks that read out-of-context as ambiguous (e.g. "the second
  factor was 12% higher" — higher than what?)
- Long documents where a single chunk loses parent-section meaning
- Compliance/policy chunks where clause numbers reference earlier sections
- Support KB articles where the topic is implied by the title, not the body
- Any corpus where chunks are < 800 tokens and the document is > 5000 tokens

## When To Skip

- Code chunks: `source_repo + path + symbol_name` is already context
- Self-contained reference data (definitions, lookup tables, structured
  records, tabular rows)
- Very small corpora (< 1000 chunks) where the LLM cost dominates
- Chunks already > 1500 tokens — they carry their own context
- Real-time corpora where re-ingest latency matters more than retrieval lift

## Prompt Template

```text
<document>
{{whole_document}}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{{chunk_content}}
</chunk>

Please give a short succinct context to situate this chunk within the overall
document for the purposes of improving search retrieval of the chunk. Answer
only with the succinct context and nothing else.
```

Target output length: 50–100 tokens. The summary should answer "what is this
chunk about, and where does it sit in the document?"

For a compliance corpus, extend with: *"Include the governing authority,
clause/section number, and any effective-date qualifier."*

For a code corpus, extend with: *"Include the module purpose, the symbol's
role in the module, and any cross-file dependency this chunk relies on."*

## Storage

Add to `chunks` (already supported in `001_schema.sql`):

```sql
-- chunks.contextual_summary TEXT  -- the 50-100 token LLM summary
-- chunks.content            TEXT  -- original chunk text (display + citation)
```

Embedding policy: embed `contextual_summary || E'\n\n' || content`. Store the
original `content` separately so the generator and the citation surface see
the unmodified chunk.

If you change the contextualization model or prompt, treat it like an
embedding-model migration: bump `model_id`, write new embeddings as new rows,
do not overwrite.

## Cost And Caching

Per-chunk cost = 1 small-LLM call. For a 100k-chunk corpus at Claude Haiku
4.5 pricing this is ≈ \$5–\$20 depending on document length.

**Prompt caching is critical.** Pass the whole document as the cached prefix
and the per-chunk question as the suffix. With Anthropic prompt caching
this is ~10x cheaper than naive per-chunk calls. Equivalent caching exists on
other providers; verify per the active model.

If the corpus is too large for full-document context (book-length material),
fall back to **section-level context** (chapter or H2 section) rather than
the whole book. Keep one level of zoom-out, not zero.

## Anti-Patterns

- **Contextualizing at query time** — destroys the cost model and adds
  100ms+ latency per query for zero retrieval benefit. Index-time only.
- **Replacing the original chunk with the summary** — the generator now sees
  a paraphrase instead of the source. Always keep `content` raw and prepend.
- **Skipping prompt caching** — turns a \$20 ingest into a \$200 ingest with
  no quality gain.
- **Using a large model for contextualization** — Haiku-class models are the
  right tool. Reserve Opus/GPT-5-class for the generator, not for index-time
  summaries.
- **Re-running contextualization for unchanged chunks** — gate on
  `content_hash`. If the chunk didn't change, the summary didn't either.
- **Mixing contextualized and non-contextualized chunks in the same index**
  without a flag — retrieval scores are no longer comparable. Either
  contextualize all or none in a given `model_id` cohort.

## Composition

Contextual Retrieval composes additively with the rest of the v1 stack:

| Layer | Lift (vs vector-only baseline) |
|---|---|
| Hybrid (vector + BM25/tsvector) via RRF | ~10–15% |
| Hybrid + Contextual Retrieval | ~30–40% |
| Hybrid + Contextual + Cross-encoder rerank | ~50–67% |

Numbers are illustrative — measure on your eval set before claiming a
specific delta. The ordering (rerank > contextual > hybrid > vector-only) is
robust across reported benchmarks; the magnitudes are not.

For the rerank layer, see `reranking-recipe.md`. For per-corpus eval gates
that should detect contextualization regressions, see `eval-by-corpus-type.md`.
