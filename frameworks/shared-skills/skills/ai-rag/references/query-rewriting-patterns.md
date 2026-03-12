# Query Rewriting & Expansion Patterns

Operational patterns for improving retrieval through query understanding and expansion.

---

## When to Use Query Rewriting

Use LLM-based query rewriting when:

- Queries are ambiguous or under-specified
- Users use different terminology than documents
- Need synonym expansion
- Multi-step or complex queries
- Retrieval recall is low despite good indexing

---

## Pattern 1: Clarification Rewriting

**Use when:** Queries lack specificity

### Example

```text
Original: "revenue growth"
Rewritten: "quarterly revenue growth rates for tech companies 2023-2024"
```

### LLM Prompt Pattern

```text
Rewrite the following query to be more specific and detailed:
<query>
{{user_query}}
</query>

Consider:
- Time period if relevant
- Domain/industry context
- Specific metrics or entities
```

**Checklist**
- [ ] Rewriter adds missing context without changing intent
- [ ] No drift into unrelated domains
- [ ] Validated on eval set (recall@k improvement)

---

## Pattern 2: Keyword Expansion

**Use when:** Documents use synonyms or variations

### Steps

1. Generate synonyms and related terms
2. Expand query with OR clauses
3. Weight original terms higher

### LLM Prompt Pattern

```text
Expand this query with synonyms and related terms:
<query>
{{user_query}}
</query>

Return a list of 3-5 alternative phrasings and related keywords.
Format: one per line
```

**Checklist**
- [ ] Synonyms domain-appropriate
- [ ] Expansion improves recall without noise
- [ ] Tested on keyword-heavy queries

---

## Pattern 3: Semantic Rewriting

**Use when:** Need to match document phrasing

### Example

```text
User query: "How do I fix login issues?"
Rewritten: "troubleshooting authentication failures user login problems"
```

### LLM Prompt Pattern

```text
Rewrite this query to match technical documentation style:
<query>
{{user_query}}
</query>

Use formal terminology and technical vocabulary that would appear in documentation.
```

**Checklist**
- [ ] Rewriting preserves user intent
- [ ] Matches document vocabulary
- [ ] Evaluated with nDCG@k

---

## Pattern 4: Multi-Step Query Decomposition

**Use when:** Complex queries require multiple retrievals

### Example

```text
Original: "Compare AWS Lambda pricing with Google Cloud Functions for Python workloads"
Decomposed:
1. "AWS Lambda pricing Python functions"
2. "Google Cloud Functions pricing Python"
3. "serverless function cost comparison AWS GCP"
```

### Implementation

```python
def decompose_query(complex_query):
    prompt = f"""Break down this complex query into 2-4 simpler sub-queries:
<query>
{complex_query}
</query>

Return as numbered list."""

    sub_queries = llm.complete(prompt).split('\n')
    return [q.strip() for q in sub_queries if q.strip()]

# Retrieve separately and merge
results = []
for sub_q in decompose_query(user_query):
    results.extend(retrieve(sub_q, k=5))

# Deduplicate and rerank
final_results = rerank(deduplicate(results))
```

**Checklist**
- [ ] Decomposition preserves all aspects of original query
- [ ] Sub-queries cover complementary information
- [ ] Results merged without duplication

---

## Pattern 5: Query Rewrite + Original Combination

**Best practice:** Don't discard original query

### Hybrid Strategy

```python
def hybrid_query_rewrite(user_query):
    rewritten = llm_rewrite(user_query)

    # Retrieve with both
    original_results = retrieve(user_query, k=10)
    rewritten_results = retrieve(rewritten, k=10)

    # Weighted fusion
    combined = []
    for doc in original_results:
        doc['score'] *= 1.5  # Boost original query matches
        combined.append(doc)

    for doc in rewritten_results:
        if doc['id'] not in [d['id'] for d in combined]:
            combined.append(doc)

    return sorted(combined, key=lambda x: x['score'], reverse=True)[:10]
```

**Checklist**
- [ ] Original query results weighted higher
- [ ] Rewritten query adds recall
- [ ] Fusion strategy tested on eval set

---

## Evaluation Metrics

Track these metrics before/after query rewriting:

- **Recall@K**: Are more relevant docs retrieved?
- **nDCG@K**: Are top results more relevant?
- **Query diversity**: Does rewriting maintain query intent?
- **Latency**: Rewriting overhead acceptable?

---

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Rewritten queries too broad | Over-expansion | Add constraints to rewrite prompt |
| Domain drift | LLM adds unrelated context | Provide domain examples in prompt |
| Loss of specificity | Paraphrasing removes key terms | Preserve named entities and numbers |
| Latency too high | Rewriting every query | Cache common query rewrites |

---

## Query Rewriting Quality Checklist

- [ ] Rewriter improves recall@k by ≥10%
- [ ] No drift into irrelevant domains
- [ ] Multi-step queries tested
- [ ] Logs tracked for regressions
- [ ] Latency within budget (<200ms)
- [ ] Original query preserved in hybrid strategy
