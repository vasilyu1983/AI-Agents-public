# RAG Patterns

*Purpose: Operational structures and decision rules for Retrieval-Augmented Generation.*

## Contents
- Retrieval contract
- Context relevance pattern
- RAG answer pattern
- RAG failure modes
- Evidence-first reasoning
- RAG summarization patterns
- Ranking + filtering patterns
- Multi-document RAG pattern
- Structured output with RAG
- Anti-patterns
- Decision table
- Agentic RAG patterns
- Quick pattern library

---

# 1. Retrieval Contract

## 1.1 Input Contract
RAG workflows must define:

- user_query  
- retrieved_context (array of chunks)  
- metadata (IDs, scores, source info)

Example:
```

{
  "user_query": "...",
  "retrieved_context": [
    {"id": "chunk-1", "text": "..."},
    {"id": "chunk-2", "text": "..."}
  ]
}

```

Checklist:
- [ ] Query isolated  
- [ ] Chunks stable and ID’d  
- [ ] No mixing raw + processed context  

---

# 2. Context Relevance Pattern

## 2.1 Rules
```

Use retrieved_context ONLY if text directly supports the answer.
If not supported → state explicitly.
Never infer beyond given evidence.

```

Checklist:
- [ ] Binary relevance (yes/no)  
- [ ] No weighted speculation  
- [ ] Evidence extracted before answering  

---

## 2.2 Evidence Extraction Structure
```

Relevant Evidence:

- [[chunk-2]] "Exact quoted span"
- [[chunk-4]] "Exact quoted span"

```

Checklist:
- [ ] Direct text quotes  
- [ ] Only from retrieved chunks  
- [ ] IDs match input metadata  

---

# 3. RAG Answer Pattern

## 3.1 Structure
```

Answer:
{{final_answer}}

Sources:

- [[chunk-1]]
- [[chunk-3]]

```

Rules:
- Answer must align with cited evidence  
- No hallucinated citations  
- No extra prose after the answer block  

Checklist:
- [ ] Evidence precedes synthesis  
- [ ] Citations exact  
- [ ] Missing info acknowledged  

---

# 4. RAG Failure Modes

## 4.1 Missing Information
```

The retrieved context does not contain evidence for the answer.

```

## 4.2 Contradictory Evidence
```

Retrieved context contains conflicting statements.
Return both and avoid synthesis.

```

## 4.3 Low-Quality Retrieval
```

Chunks irrelevant to the query.
Provide "No relevant evidence found."

```

Checklist:
- [ ] No forced answers  
- [ ] Conflicts surfaced verbatim  
- [ ] No invented resolution  

---

# 5. Evidence-First Reasoning

## 5.1 Workflow
1. Identify relevant chunks  
2. Extract verbatim evidence  
3. Summarize evidence  
4. Compose final answer  
5. Cite chunks  

## 5.2 Constraints
- No reasoning visible  
- No combining mismatched chunks  
- No multi-hop inference unless supported  

---

# 6. RAG Summarization Patterns

## 6.1 Chunk-to-Chunk Summary
```

Summaries:

- [[chunk-2]] → "summary"
- [[chunk-4]] → "summary"

```

Checklist:
- [ ] Preserve meaning  
- [ ] No deletion of dissenting details  
- [ ] No synthesis across chunks  

---

## 6.2 Global Summary Pattern
```

Global Summary:
"integrated summary here"

```

Rules:
- Include only facts appearing in at least one chunk  
- Mark contradictions  

---

# 7. Ranking + Filtering Patterns

## 7.1 Ranking Structure
```

Ranked Context:

1. [[chunk-3]] score 0.87
2. [[chunk-1]] score 0.74
3. [[chunk-4]] score 0.52

```

Checklist:
- [ ] Numeric scores preserved  
- [ ] Relative order maintained  

---

## 7.2 Filtering Rules

**Include chunk when:**
- Contains direct evidence  
- Contains definition or term required by query  
- Clarifies ambiguous phrasing  

**Exclude chunk when:**
- Purely tangential  
- Does not alter answer  
- Duplicates better chunk  

---

# 8. Multi-Document RAG Pattern

## 8.1 Namespace Structure
```

retrieved_context = [
  {"id": "docA-1", "text": "..."},
  {"id": "docB-3", "text": "..."}
]

```

Rule:
- IDs must include document scope  

Checklist:
- [ ] Namespaces stable  
- [ ] No cross-document blending  

---

# 9. Structured Output with RAG

## 9.1 Schema Pattern
```

Return ONLY this JSON object:

{
  "answer": "string",
  "evidence": [
    {"chunk": "chunk-id", "quote": "span"}
  ],
  "missing_info": "string|null"
}

```

---

## 9.2 Error-Fallback Rules
- If evidence absent → `"missing_info": "No evidence found"`  
- If conflicting → `"missing_info": "Conflicting evidence"`  

Checklist:
- [ ] One root object  
- [ ] Evidence array typed  
- [ ] No extra keys  

---

# 10. Anti-Patterns

Avoid:
- Using context summaries as factual evidence  
- Inferential chain beyond retrieved content  
- Hybrid reasoning from memory + retrieval  
- Guessing missing entries  
- Over-long narrative outputs  

---

# 11. Decision Table

| Scenario | Apply Pattern | Notes |
|----------|---------------|-------|
| Direct factual Q | Context relevance | Evidence must support claim |
| Ambiguous Q | Evidence extraction | Show all interpretations |
| Missing data | Failure mode | No guessing |
| Conflicting chunks | Conflict handling | Return both sides |
| Structured output | JSON schema RAG | Deterministic |

---

# 12. Agentic RAG Patterns (2025)

*Based on: [Agentic RAG Survey](https://arxiv.org/abs/2501.09136)*

Traditional RAG is constrained by static workflows. **Agentic RAG** embeds autonomous agents into the pipeline for adaptive, multi-step reasoning.

## 12.1 When to Use Agentic RAG

Use Agentic RAG when:

- Query requires **multi-hop reasoning** across documents
- Retrieval quality varies and needs **adaptive refinement**
- Task involves **complex decision-making** with retrieval
- System must **self-correct** retrieval failures

Use Traditional RAG when:

- Single-hop factual lookup
- Fixed, high-quality corpus
- Latency-critical applications
- Simple Q&A without reasoning chains

## 12.2 Agentic RAG Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│  AGENT ORCHESTRATOR                 │
│  - Query analysis                   │
│  - Strategy selection               │
│  - Tool/retriever routing           │
└─────────────────────────────────────┘
    │
    ├──▶ [Retriever Agent] ──▶ Vector DB
    │         │
    │         ▼
    │    Quality Check
    │         │
    │    ◄────┘ (re-retrieve if low quality)
    │
    ├──▶ [Reasoning Agent] ──▶ Multi-hop synthesis
    │
    ├──▶ [Verification Agent] ──▶ Fact-check claims
    │
    └──▶ [Response Agent] ──▶ Final answer
```

## 12.3 Key Agentic Patterns

### RAG-Fusion

([arXiv:2506.00054](https://arxiv.org/html/2506.00054v1))

- Generate multiple query reformulations
- Retrieve for each reformulation
- Combine via reciprocal rank fusion (RRF)
- Improves recall on ambiguous queries

### KRAGEN (Graph-of-Thoughts)

- Decompose complex queries into subproblems
- Retrieve relevant subgraphs per subproblem
- Guide multi-hop reasoning with graph structure

### Adaptive Retrieval

- Agent decides when to retrieve vs. use cached context
- Quality scoring triggers re-retrieval
- Prevents unnecessary retrieval calls

## 12.4 Agentic RAG Prompt Structure

```
You are a RAG agent with access to retrieval tools.

For each query:
1. ANALYZE: Determine if retrieval is needed
2. PLAN: Identify retrieval strategy (single/multi-hop/fusion)
3. RETRIEVE: Call retrieval tool with optimized query
4. EVALUATE: Score retrieved context relevance (0-1)
5. DECIDE: If score < 0.7, reformulate and re-retrieve (max 2 retries)
6. SYNTHESIZE: Generate answer from high-quality context only
7. VERIFY: Check claims against source chunks

Tools available:
- search(query: str) → chunks[]
- verify(claim: str, chunks[]) → bool

Output format:
{
  "retrieval_strategy": "single|multi_hop|fusion",
  "retrieval_attempts": number,
  "quality_score": 0.0-1.0,
  "answer": "string",
  "sources": ["chunk-id"],
  "verification_status": "verified|partial|unverified"
}
```

## 12.5 Best Practices (Research-Based)

From [Enhancing RAG: Best Practices](https://arxiv.org/abs/2501.07391):

| Parameter | Recommendation | Impact |
|-----------|----------------|--------|
| Chunk size | 256-512 tokens | Balance context vs. precision |
| Overlap | 10-20% | Preserve cross-boundary context |
| Top-k retrieval | 3-5 chunks | More isn't always better |
| Query expansion | BM25 + semantic | Hybrid outperforms single method |
| Focus Mode | Sentence-level | Higher precision for factual Q&A |

**Quality Indicators**:

- Retrieval latency < 200ms for interactive use
- Relevance score threshold: 0.7 minimum
- Re-retrieval budget: max 2 attempts
- Context window utilization: 60-80% optimal

---

# 13. Quick Pattern Library

**Evidence-only answer**
```

Answer: based only on evidence  
Sources: [[chunk-1]]

```

**Citation-required answer**
```

Use only cited evidence. No unsupported claims.

```

**RAG classification**
```

Classify based on chunk evidence. If unclear → "unknown".

```

**RAG rewrite**
```

Rewrite using ONLY retrieved text. No new facts.

```

