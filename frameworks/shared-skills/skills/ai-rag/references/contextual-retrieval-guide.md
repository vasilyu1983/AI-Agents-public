# Chunk Context Augmentation (Contextual Retrieval)

Chunk context augmentation adds a lightweight, generated "header" to each chunk before indexing. This can improve retrieval for entities/time periods that are not explicit inside isolated chunks.

Reference (popularized): Anthropic "Contextual Retrieval" (https://www.anthropic.com/news/contextual-retrieval).

---

## When to Use

- Multi-entity corpora where chunks frequently omit the subject (company/product/user).
- Documents with temporal structure (quarters, versions, dates) where chunk-local text is ambiguous.
- Large reports/manuals where headings carry meaning that chunks lose.

Avoid when:
- Your corpus already has strong structure-aware metadata (titles, headings, section paths) and retrieval is good.
- You cannot validate the impact with an evaluation set.

---

## Core Idea

Store two representations:
- **Raw chunk** (for citations and display)
- **Augmented chunk** = generated context + raw chunk (for embedding / indexing)

The generated context should be:
- short (a few sentences)
- factual (derived only from the parent document/section)
- stable (deterministic prompt + constrained output)

---

## Implementation Pattern (Pseudocode)

```text
for each document:
  parse → structured sections (title/headings/page)
  for each chunk:
    metadata_context = {title, heading_path, page, section_id}
    generated_context = LLM(document_context + metadata_context + chunk_text)
    augmented_text = generated_context + "\n\n" + chunk_text
    embed/index augmented_text with metadata pointing to raw chunk
```

---

## Validation Protocol (REQUIRED)

- Hold out a retrieval test set (queries + expected sources).
- Compare **baseline vs augmented**:
  - recall@k / nDCG
  - empty-result rate
  - latency and index size changes
- If you also use reranking, test:
  - baseline retrieval + rerank
  - augmented retrieval + rerank

---

## Failure Modes (AVOID)

- Hallucinated context that introduces incorrect entities/times.
- Context that includes sensitive data that should not be indexed or cached.
- Overly long context that bloats embeddings and increases latency/cost.

Mitigations:
- Use strict prompts + output length caps.
- Validate context format; reject empty or non-compliant outputs.
- Log and sample augmented chunks for review.
