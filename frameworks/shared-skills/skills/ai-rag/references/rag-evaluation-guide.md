# RAG Evaluation Guide

Comprehensive framework for validating RAG system quality with modern metrics and best practices.

---

## Overview

RAG evaluation requires measuring both retrieval quality and generation quality. This guide provides a complete workflow for systematic RAG validation.

---

## Evaluation Workflow

### Step 1: Define Tasks

Identify what your RAG system needs to accomplish:

- **Q&A** - Answering factual questions
- **Summarization** - Condensing document content
- **Extraction** - Pulling specific information
- **Decision support** - Providing evidence for decisions
- **Comparison** - Analyzing differences between entities
- **Trend analysis** - Identifying patterns over time

### Step 2: Prepare Test Set

Create a balanced evaluation dataset:

- **Size:** 20–200 queries (minimum 50 recommended)
- **Coverage:** Balanced across question types
- **Difficulty:** Mix of easy, medium, hard queries
- **Edge cases:** Include unanswerable questions
- **Ground truth:** Human-verified answers when possible

**Test Set Quality Checklist:**

- [ ] Queries representative of real user needs
- [ ] Balanced across difficulty levels
- [ ] Includes edge cases (unanswerable, ambiguous)
- [ ] Ground truth answers verified
- [ ] Test set isolated from training data

### Step 3: Measure RAG-Specific Metrics

#### Retrieval Metrics

**Recall@K** - Fraction of relevant docs in top-K results
```
Recall@K = (Relevant docs in top-K) / (Total relevant docs)
```

**Precision@K** - Fraction of retrieved docs that are relevant
```
Precision@K = (Relevant docs in top-K) / K
```

**nDCG (Normalized Discounted Cumulative Gain)** - Ranking quality
- Accounts for position of relevant docs
- Higher score = better ranking

**Mean Reciprocal Rank (MRR)** - Position of first relevant doc
```
MRR = 1 / (Position of first relevant doc)
```

#### Generation Metrics

**Groundedness** - How well output ties to retrieved context
- Measure: % of claims supported by context
- Tools: RAGAS faithfulness score, TruLens groundedness

**Answer Relevance** - Does output address the query?
- Semantic similarity to question
- Coverage of query aspects

**Context Precision** - Are retrieved chunks relevant to query?
- Measure quality of retrieval for specific query

**Context Recall** - Is all necessary info retrieved?
- Check if context contains all info needed for ground truth

**Hallucination Rate** - % of outputs containing unsupported claims
- Critical for production systems
- Target: <5% for most applications

**Verbosity** - Output length appropriateness
- Too short: missing details
- Too long: inefficient, potential filler

**Instruction Following** - Does output match format requirements?
- Citations included when required
- Structure matches specification

#### End-to-End Metrics

**Solve Rate** - % of queries answered correctly
- Primary business metric
- Combines retrieval + generation quality

**Latency** - Time from query to response
- P50, P95, P99 percentiles
- Target: <2s for interactive systems

**Cost per Query** - Token usage + compute cost
- Important for production viability
- Track over time as system evolves

### Step 4: Compare Variants

Systematically test configuration changes:

**Chunking Experiments:**
- [ ] Page-level vs semantic vs fixed-size
- [ ] Chunk size variations (256, 512, 1024 tokens)
- [ ] Overlap percentages (0%, 10%, 20%)

**Index Parameters:**
- [ ] Vector index types (HNSW, IVF, Flat)
- [ ] ef_search / nprobe values
- [ ] Distance metrics (cosine, L2, dot product)

**Embedding Models:**
- [ ] Model size (small, base, large)
- [ ] Domain-specific vs general-purpose
- [ ] Multilingual vs single-language

**Rerankers:**
- [ ] No reranking vs cross-encoder
- [ ] Different reranker models
- [ ] Reranker K values (top 10, 20, 50)

**Retrieval Strategies:**
- [ ] Vector-only vs hybrid (BM25+vector)
- [ ] Different fusion methods (RRF, weighted sum)
- [ ] K values (5, 10, 20)

---

## Modern Evaluation Tools (2026)

### RAGAS (Retrieval-Augmented Generation Assessment)

**Metrics provided:**
- Faithfulness (groundedness)
- Answer relevance
- Context precision
- Context recall
- Context utilization

**When to use:** Comprehensive RAG evaluation, industry-standard metrics

**Strengths:** Incorporates latest research into RAG metrics. Metrics have become the benchmark for RAG quality assessment in the ecosystem.

**Limitations:** Metrics are not self-explaining, making it harder to debug unsatisfactory results.

### DeepEval (Confident AI)

**2026 Update:** DeepEval has emerged as a leading framework with debuggable metrics.

**Metrics provided:**
- Faithfulness with **LLM judge reasoning** (debuggable)
- Answer relevance
- Contextual precision/recall
- Hallucination detection
- Toxicity and bias detection
- 14+ pre-built RAG metrics

**Key differentiator:** Unlike RAGAS, DeepEval's metrics include the LLM judge's reasoning. You can inspect judgments to understand why a score is a certain way.

**When to use:** CI/CD integration, debugging eval failures, "Pytest for LLMs"

```python
# Conceptual example - DeepEval
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

metric = FaithfulnessMetric(threshold=0.7)
test_case = LLMTestCase(
    input="What is RAG?",
    actual_output="RAG retrieves documents...",
    retrieval_context=["RAG paper excerpt..."]
)
metric.measure(test_case)
# Access reasoning: metric.reason shows why score is X
```

### TruLens (Snowflake)

**Metrics provided:**
- Groundedness
- Answer relevance
- Context relevance
- Custom feedback functions
- RAG Triad (comprehensive assessment)

**When to use:** Production monitoring, agentic workflow tracing, LangChain/LlamaIndex integration

**Strengths:** Deep integration with RAG frameworks. Helps create guardrails and context filters based on evaluation.

### Lynx (Hallucination Detection)

**2026 Update:** Lynx is an open-source hallucination detection model that outperforms RAGAS Faithfulness, especially in long-context cases.

**When to use:**
- Long-context RAG (>8K tokens)
- High-stakes domains (legal, medical, financial)
- When RAGAS Faithfulness gives false positives/negatives

**Benchmark results:** HaluBench hallucination evaluation shows Lynx significantly outperforms RAGAS Faithfulness on complex documents.

**Integration:** Can be used alongside RAGAS/DeepEval as a specialized hallucination checker.

### BEIR (Benchmark for IR)

**Purpose:** Standardized retrieval benchmarks across 18 diverse datasets

**When to use:** Comparing retrieval methods against baselines, zero-shot evaluation

### Emerging Benchmarks (2026)

| Benchmark | Purpose | Use Case |
|-----------|---------|----------|
| **FRAMES** | Long-context retrieval | Testing retrieval over large documents |
| **LONG2RAG** | Long-context generation | Evaluating answer quality with extended context |
| **HaluBench** | Hallucination detection | Comparing faithfulness metrics |
| **RAGBench** | End-to-end RAG | Comprehensive system evaluation |

---

## Tool Comparison Matrix

| Tool | Debuggability | CI/CD | Production | Hallucination | Long-Context |
|------|---------------|-------|------------|---------------|--------------|
| **RAGAS** | Low | Yes | Moderate | Basic | Limited |
| **DeepEval** | High | Excellent | Moderate | Good | Good |
| **TruLens** | Moderate | Yes | Excellent | Good | Good |
| **Lynx** | Moderate | Yes | Good | Excellent | Excellent |

**Recommendation:** Use DeepEval for development/CI (debuggable metrics), TruLens for production monitoring, and add Lynx for high-stakes hallucination detection.

---

## Evaluation Best Practices

### A/B Testing Protocol

1. Define baseline configuration
2. Change ONE variable at a time
3. Run on full test set
4. Measure statistical significance
5. Document results before next change

### Regression Testing

- Save evaluation results for each version
- Re-run tests on code/config changes
- Alert on metric degradation
- Track improvements over time

### Sliced Evaluation

Break down metrics by dimension:
- Query type (factual, opinion, comparison)
- Document type (PDF, web, database)
- Query complexity (simple, multi-hop)
- Language (for multilingual systems)

### Human Evaluation

Complement automated metrics with human review:
- Sample 50-100 outputs per variant
- Rate on 1-5 scale for quality
- Identify failure patterns
- Update test set with edge cases

---

## Evaluation Checklist

- [ ] Retrieval quality measured (recall@k, nDCG)
- [ ] Generation quality measured (groundedness, relevance)
- [ ] Hallucination rate tracked
- [ ] Decision made with statistical evidence
- [ ] Results documented for future reference
- [ ] Regression tests in place
- [ ] A/B testing protocol followed
- [ ] Sliced evaluation performed
- [ ] Human evaluation conducted (for major changes)

---

## Implementation Templates

See [assets/eval/](../assets/eval/) for:
- [RAG Evaluation Template](../assets/eval/template-rag-eval.md)
- [RAG Test Set Format](../assets/eval/template-rag-testset.jsonl)

---

## Related Resources

- [Retrieval Patterns](retrieval-patterns.md) - Improving retrieval quality
- [Grounding Checklists](grounding-checklists.md) - Reducing hallucinations
- [RAG Troubleshooting](rag-troubleshooting.md) - Fixing low-quality results
- [Advanced RAG Patterns](advanced-rag-patterns.md) - Production telemetry and monitoring
