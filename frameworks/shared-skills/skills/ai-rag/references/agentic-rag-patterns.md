# Agentic RAG Patterns

Loop-based RAG architectures with autonomous reasoning, self-correction, and adaptive retrieval strategies.

**Status**: Production standard as of January 2026. Linear "naive RAG" pipelines are obsolete for complex use cases.

References:
- Agentic RAG Survey (https://arxiv.org/html/2501.09136v1)
- Building Agentic RAG with LangGraph (https://rahulkolekar.com/building-agentic-rag-systems-with-langgraph/)
- Top Agentic RAG Frameworks 2026 (https://research.aimultiple.com/agentic-rag/)

---

## Why Agentic RAG?

Traditional RAG is a **pipeline**: Retrieve → Augment → Generate.

Agentic RAG is a **loop**: The LLM acts as a reasoning engine with autonomy to:
- Decide **when** to retrieve (not always)
- Reformulate queries on poor results
- Perform multi-hop retrieval for complex questions
- Self-correct and verify answers
- Route to different retrieval strategies

---

## Architecture Comparison

```text
Traditional RAG (Linear Pipeline):
  Query → Retrieve → Pack Context → Generate → Response
  └─ Single pass, no feedback, brittle

Agentic RAG (Reasoning Loop):
  Query → [Agent Decision Loop]
           ├─ Need retrieval? → Retrieve → Evaluate relevance
           │                    └─ Poor results? → Reformulate → Retry
           ├─ Need decomposition? → Split into sub-queries → Aggregate
           ├─ Have enough context? → Generate → Verify citations
           │                         └─ Verification failed? → Re-retrieve
           └─ Sufficient confidence? → Response
```

---

## Core Patterns

### 1. Adaptive Retrieval

**Problem**: Not all queries need retrieval. Simple factual queries waste latency.

**Pattern**:
```text
Query Analysis:
  ├─ Factual, in training data → Direct answer (no retrieval)
  ├─ Recent/domain-specific → Full RAG pipeline
  ├─ Ambiguous → Clarify before retrieval
  └─ Multi-faceted → Decompose into sub-queries
```

**Implementation**:
- Classifier or LLM judge on query complexity
- Track retrieval decision in telemetry
- Measure retrieval skip rate vs answer quality

### 2. Self-Correcting Retrieval

**Problem**: First retrieval often returns near-misses or irrelevant results.

**Pattern**:
```text
Retrieval Loop:
  1. Initial query → Retrieve top-k
  2. Relevance check (reranker or LLM judge)
  3. If relevance < threshold:
     - Analyze why (too broad? wrong terminology?)
     - Reformulate query (expand, narrow, rephrase)
     - Re-retrieve with new query
  4. Max iterations = 3 (prevent infinite loops)
```

**Key Signals for Reformulation**:
- All results from same source (too narrow)
- High lexical overlap but low semantic match (wrong terminology)
- Results from wrong time period (add date filters)
- Results in wrong language (add language filter)

### 3. Multi-Hop Reasoning

**Problem**: Complex questions require information from multiple sources that must be combined.

**Pattern**:
```text
Multi-Hop Pipeline:
  1. Decompose: "What's the revenue impact of feature X?" →
     - Sub-Q1: "What is feature X?"
     - Sub-Q2: "When was feature X launched?"
     - Sub-Q3: "What were revenue numbers before/after launch?"
  2. Retrieve for each sub-query
  3. Synthesize: Combine evidence, resolve contradictions
  4. Generate: Answer with citations from multiple hops
```

**When to Use**:
- Comparison questions ("X vs Y")
- Causal questions ("Why did X happen?")
- Aggregation questions ("How many...", "What's the total...")
- Timeline questions ("What happened after X?")

### 4. Verification Loop

**Problem**: Generated answers may hallucinate or misattribute citations.

**Pattern**:
```text
Post-Generation Verification:
  1. Generate answer with inline citations [1], [2]
  2. Extract each claim + citation pair
  3. Verify: Does cited chunk support the claim?
     - If yes → Keep
     - If no → Flag for re-generation or removal
  4. Check coverage: All claims have citations?
  5. Fail if verification rate < threshold
```

**Verification Signals**:
- Citation points to chunk that doesn't contain claimed fact
- Citation chunk is about different entity/time period
- Claim extrapolates beyond source (opinion presented as fact)

---

## Decision Tree: When to Use Agentic RAG

```text
Should you use Agentic RAG?
  │
  ├─ Query complexity?
  │   ├─ Simple factual → Traditional RAG (lower latency)
  │   ├─ Multi-hop/comparative → Agentic (decomposition needed)
  │   └─ Ambiguous → Agentic (clarification + adaptive retrieval)
  │
  ├─ Corpus quality?
  │   ├─ High-quality, well-structured → Traditional may suffice
  │   └─ Noisy, overlapping, inconsistent → Agentic (self-correction)
  │
  ├─ Accuracy requirements?
  │   ├─ Approximate OK → Traditional (faster)
  │   └─ High stakes (legal, medical, financial) → Agentic (verification)
  │
  └─ Latency budget?
      ├─ <2s required → Traditional or hybrid
      └─ 5-10s acceptable → Full agentic loop
```

---

## Implementation Frameworks (2026)

| Framework | Strengths | Best For |
|-----------|-----------|----------|
| **LangGraph** | State machines, cycles, human-in-loop | Complex multi-step agents |
| **LlamaIndex Workflows** | Async, event-driven, retrieval-native | RAG-heavy applications |
| **CrewAI** | Multi-agent collaboration | Specialized agent teams |
| **AutoGen** | Conversational agents, code execution | Research, prototyping |
| **Haystack 2.x** | Pipeline + agent hybrid | Production systems |

### LangGraph Example Structure

```python
# Conceptual structure - not runnable code
graph = StateGraph(AgentState)

graph.add_node("analyze_query", analyze_complexity)
graph.add_node("retrieve", retrieval_node)
graph.add_node("evaluate_relevance", relevance_checker)
graph.add_node("reformulate", query_reformulator)
graph.add_node("generate", generation_node)
graph.add_node("verify", citation_verifier)

# Conditional edges for loops
graph.add_conditional_edges(
    "evaluate_relevance",
    should_reformulate,
    {"reformulate": "reformulate", "generate": "generate"}
)
graph.add_conditional_edges(
    "verify",
    verification_passed,
    {"pass": END, "fail": "retrieve"}  # Loop back on failure
)
```

---

## GEAR: Graph-Enhanced Agentic RAG

**Pattern**: Combine knowledge graphs with agentic retrieval for enterprise use cases.

```text
GEAR Architecture:
  1. Query → Entity extraction
  2. Graph lookup → Related entities, relationships
  3. Hybrid retrieval:
     - Graph traversal for structured facts
     - Vector search for unstructured context
  4. Agent decides: Graph-only, vector-only, or both?
  5. Synthesis with entity grounding
```

**Best For**:
- Enterprise knowledge bases with entity relationships
- Compliance/legal where relationships matter
- Product catalogs with hierarchies
- Technical documentation with cross-references

---

## Operational Considerations

### Latency Budget

| Pattern | Typical Latency | When Acceptable |
|---------|-----------------|-----------------|
| Traditional RAG | 1-2s | Real-time chat, simple queries |
| Single-loop agentic | 3-5s | Complex queries, async OK |
| Multi-hop agentic | 5-15s | Research, analysis, batch |

### Telemetry Requirements

Track per-request:
- Retrieval decision (skip/execute)
- Number of retrieval iterations
- Query reformulations applied
- Verification pass/fail rate
- Total latency breakdown by stage

### Cost Management

Agentic RAG uses more tokens:
- Query analysis: +500-1000 tokens
- Reformulation: +500 tokens per iteration
- Verification: +1000-2000 tokens
- **Budget 2-4x traditional RAG token cost**

### Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Infinite loops | Request timeout | Max iterations (3), circuit breaker |
| Over-retrieval | High latency, low quality | Relevance threshold tuning |
| Under-retrieval | Missing context | Lower skip threshold |
| Verification too strict | Low answer rate | Calibrate on eval set |

---

## Implementation Checklist

- [ ] Query classifier for adaptive retrieval (skip vs execute)
- [ ] Relevance evaluator (reranker or LLM judge)
- [ ] Query reformulation logic with max iterations
- [ ] Multi-hop decomposition for complex queries
- [ ] Post-generation verification with citation checking
- [ ] Telemetry: retrieval decisions, iterations, latency breakdown
- [ ] Cost tracking: tokens per request by stage
- [ ] Eval set with complexity labels (simple/multi-hop/ambiguous)
- [ ] Latency SLOs per complexity tier

---

## Anti-Patterns

- **Always retrieve**: Wastes latency on simple queries; add skip logic
- **No max iterations**: Can loop forever; cap at 3 iterations
- **Reformulate blindly**: Analyze why retrieval failed before changing query
- **Skip verification**: Hallucinations go undetected; always verify high-stakes answers
- **Single eval metric**: Measure retrieval quality AND generation quality separately

---

## Related Resources

- [Retrieval Patterns](retrieval-patterns.md) - Hybrid search, reranking
- [RAG Evaluation Guide](rag-evaluation-guide.md) - Metrics for agentic systems
- [RAG Troubleshooting](rag-troubleshooting.md) - Debugging retrieval loops
- [ai-agents skill](../../ai-agents/SKILL.md) - General agent architectures
