# Architecture Patterns

Use this skill when the problem is bigger than retrieval alone.

## Canonical Layers

1. **Entity/Profile Layer**
- Stable records for user, org, account, brand, and domain objects.
- The system of record stays in operational stores.

2. **Memory Layer**
- Derived facts, preferences, action history, and outcome summaries.
- Memory must carry provenance, confidence, and retention metadata.

3. **Retrieval/Grounding Layer**
- Domain corpora, sites, files, and broad knowledge sources.
- Retrieval must return evidence IDs, freshness, and source metadata.

4. **Relationship/Graph Layer**
- Explicit entity-to-entity links, dependencies, influence paths, and ownership maps.
- Add this only when traversal changes the quality of answers or actions.

5. **Context Assembly Layer**
- Per-surface bundle builder that decides what is always present, what is fetched on demand, and what is excluded by policy.

6. **Feedback Layer**
- Corrections, action outcomes, and reuse scoring that improve derived memory without overwriting operational truth.

## Default Decision Rules

- **User and org state**: prefer tools, APIs, or SQL.
- **Domain corpus**: prefer hybrid retrieval with grounding.
- **Persistent personalization**: prefer structured memory, not raw chat logs.
- **Entity relationships**: prefer graph only when relationship traversal is genuinely needed.
- **Surface adaptation**: always build a context assembly layer instead of one giant prompt.

## Anti-Patterns

- Treating the vector index as the source of truth.
- Treating chat history as durable memory.
- Building GraphRAG before proving that SQL or hybrid search is insufficient.
- Mixing tenant-scoped data and global knowledge without explicit isolation.
- Sending internal state directly to the model instead of projecting a bounded derived context.
