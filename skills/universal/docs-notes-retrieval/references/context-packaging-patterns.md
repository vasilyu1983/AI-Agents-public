# Context Packaging Patterns

Use this file when packaging notes for LLM context, retrieval systems, or agent workflows.

## Table of Contents

- [Chunk Strategies](#chunk-strategies)
- [Token-Budgeting Heuristics](#token-budgeting-heuristics)
- [Ordering: Relevance vs Recency](#ordering-relevance-vs-recency)
- [Frontmatter as Structured Metadata](#frontmatter-as-structured-metadata)
- [Deduplication](#deduplication)
- [Attribution Format for Downstream Agents](#attribution-format-for-downstream-agents)
- [Including Wikilink Neighborhood](#including-wikilink-neighborhood)
- [Common Ordering of Sections in a Pack](#common-ordering-of-sections-in-a-pack)

---

## Chunk Strategies

Chunking determines how note content is divided before inclusion in a context window. Choose based on note length, query type, and budget.

### Whole-note chunks

Include the full note body as one unit.

**Best for:** Short vaults, interview-style notes, maps of content, atomic notes.

**Trade-offs:**
- Preserves full note coherence and inter-sentence context.
- Wastes budget on large notes when only one section is relevant.
- Best default for vaults where individual notes are ≤500 words.

### Heading-level chunks (split at H2)

Split each note at `##` boundaries. Each chunk carries its parent note's metadata.

**Best for:** Long reference notes, decision logs, meeting notes with structured sections.

**Trade-offs:**
- Retrieves only the relevant heading block, saving budget.
- Loses context from sibling headings — include the intro (pre-H2 text) in every chunk if possible.
- Works poorly on notes without consistent heading structure.

### Paragraph chunks (split on blank lines)

Split at paragraph boundaries (two or more consecutive blank lines).

**Best for:** Diary-style notes, unstructured prose vaults, narrative journals.

**Trade-offs:**
- Maximum granularity; fits more unique content into budget.
- Paragraphs in isolation are often too terse without surrounding context.
- Attach note title and frontmatter to every chunk to restore grounding.

### Strategy selection heuristic

| Vault style | Structure | Recommended strategy |
|-------------|-----------|----------------------|
| Atomic / Zettelkasten | One claim or decision per note | `whole` |
| Structured reference docs | Clear task headings | `heading` |
| Journal / log | Multiple dated entries or long prose | `paragraph` |
| Mixed | Varies by note | Test `heading` and retain context from the intro |

---

## Token-Budgeting Heuristics

The bundled script uses a character budget for selected sections, not a model token budget; the footer adds a little more. Use the target model's tokenizer or counting API to verify the final pack before sending it.

### Practical budgeting

Check the current model's published context limit when preparing a pack. Count the complete prompt, including instructions and conversation, with its tokenizer or API; reserve room for the response. Reduce irrelevant notes before increasing the budget.

### Budget allocation across notes

1. Leave room for the pack header, metadata, and footer.
2. Sort notes by relevance or recency before filling.
3. Fill greedily: include a full note if it fits, skip otherwise (do not partial-include unless using heading/paragraph strategy).
4. Report omitted note count in the pack footer so downstream agents know what was left out.

---

## Ordering: Relevance vs Recency

**Relevance-first (default):** Order by keyword hit density in note title + body. Ensures the most topically dense notes appear early in the context window, where attention weight is highest for most models.

**Recency-first:** Order by `mtime` descending. Better for workflows where the freshest notes dominate (e.g., daily log review, sprint retrospectives).

**Hybrid:** Relevance within a recency window — e.g., filter to notes modified in the last 30 days, then sort by keyword density within that set.

---

## Frontmatter as Structured Metadata

Frontmatter carries signal that body text does not. Always include it — but render it as readable metadata, not raw YAML.

Recommended rendering format:

```
> **Source:** `Projects/Alpha.md` | **Modified:** 2026-04-27T09:00:00Z
> **Tags:** project, alpha, planning | **Status:** active
```

Fields worth surfacing per note:
- `title` / `aliases`
- `tags`
- `status` (draft / active / archived)
- `created` / `updated`
- `project` or `area` if the vault uses PARA

Do not include large binary frontmatter fields (base64, embedded image data) — filter before packing.

---

## Deduplication

Deduplication prevents the same content from burning multiple budget slots.

### Exact duplicates

Hash each note body (e.g., `hashlib.md5(body.encode()).hexdigest()`). Drop notes with duplicate hashes and log them.

### Near-duplicates

Flag notes with identical title stems but different paths. Common in vaults with daily notes templates — keep the newest and annotate.

### Chunk-level deduplication

When using heading or paragraph strategies, a wikilink `[[Shared Note]]` may cause the same chunk to appear in multiple included notes. Track included chunks by (path, chunk-index) pair and skip repeats.

---

## Attribution Format for Downstream Agents

Attribution enables agents to cite sources, re-fetch notes, and build backlinks.

Minimum required per section:
```
> **Source:** `<relative/path/to/note.md>` | **Modified:** <ISO-8601 mtime>
```

Extended attribution (for agent workflows):
```
> **Source:** `<path>` | **Title:** <title> | **Modified:** <mtime>
> **Tags:** <tags> | **Vault:** <vault-root-name>
```

Place attribution immediately after the section heading, before body text. This ensures it appears in every chunk regardless of where the chunk starts.

---

## Including Wikilink Neighborhood

A sparse note gains context from its linked neighbors. Include neighborhoods when:
- Target note is < 100 words.
- Target note is a map-of-content hub note (links out to many others).
- The query is conceptual rather than fact-retrieval.

Neighborhood inclusion pattern:
1. Collect all `[[wikilink]]` targets from the note.
2. Resolve each target to a vault path.
3. Include a short excerpt (first 2–3 paragraphs) of each linked note as a sub-section.
4. Mark sub-sections as `> _Linked note excerpt: [title]_` to distinguish them from primary content.

Budget impact: each linked note excerpt adds ~200–500 chars. Cap neighborhood depth at 1 hop to avoid combinatorial expansion.

---

## Common Ordering of Sections in a Pack

Recommended pack structure for agent consumption:

1. **Pack header** — generated timestamp, vault name, query, note count, budget stats.
2. **Most relevant notes** — ordered by relevance or recency.
3. **Neighborhood excerpts** — if included, immediately after each primary note.
4. **Pack footer** — count of omitted notes, truncation notice, char/token estimate.

Keep the header under 500 chars. Agents and models often scan the beginning of context for orientation — a bloated header wastes attention budget.
