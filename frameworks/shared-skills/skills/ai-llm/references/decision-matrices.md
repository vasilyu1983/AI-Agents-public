# Decision Matrices

Quick reference tables for LLM system architecture, technology selection, and operational decisions.

---

## RAG Type Decision Matrix

Choose the right RAG architecture based on use case complexity and requirements.

| Use Case | RAG Type | When to Use | Technical Requirements | Checklist |
|----------|----------|-------------|----------------------|-----------|
| **Simple FAQ, low recall** | Naive RAG | - Small data (<10k docs)<br>- Simple retrieval<br>- Low accuracy requirements | - Vector DB<br>- Basic embedding model<br>- No reranking | [Basic RAG Checklist](#basic-rag-checklist) |
| **Docs >100k, complex** | Advanced RAG | - Large corpus<br>- Needs chunking optimization<br>- Reranking required<br>- Hybrid search | - Vector DB<br>- Cross-encoder reranker<br>- BM25 + semantic search<br>- Page-level chunking | [Advanced RAG Checklist](#advanced-rag-checklist) |
| **Multiple data, agents** | Modular RAG | - Cross-modal data<br>- Agentic workflows<br>- Dynamic knowledge base<br>- Multiple retrieval strategies | - Multi-index architecture<br>- Routing logic<br>- Contextual retrieval<br>- Agent orchestration | [Modular RAG Checklist](#modular-rag-checklist) |

### When to Use Each RAG Type

**Naive RAG** → **Advanced RAG** → **Modular RAG**

Upgrade when:
- Naive RAG: Accuracy <80%, users complaining about relevance
- Advanced RAG: Need multi-source retrieval, dynamic knowledge graphs
- Modular RAG: Complex workflows requiring agent orchestration

---

## Production Evaluation Table

Set targets and action thresholds for key production metrics.

| Metric | Target/Range | Tool Example | Measurement Method | Action if Fails |
|--------|--------------|--------------|-------------------|----------------|
| **Hallucination** | <3% | Faithfulness eval, Ragas | LLM-as-judge + human audit | Add RAG, filter outputs, improve grounding |
| **Latency (p95)** | <2s | LangSmith, W&B | Distributed tracing | Optimize prompt/model, cache, batch |
| **Latency (p99)** | <5s | LangSmith, W&B | Distributed tracing | Investigate tail latencies, add timeouts |
| **Cost per Request** | Budgeted | Inference dashboard | Token counting + pricing | Quantize, batch, prune context, smaller model |
| **Safety** | 0 critical | Output filter, logs | Automated content moderation | Escalate, block, alert, strengthen guardrails |
| **Accuracy/F1** | >90% | Golden test set | Automated eval suite | Improve prompts, add examples, fine-tune |
| **Groundedness** | >95% | Citation checking | Automated verification | Tighten retrieval, add reranking, filter chunks |
| **User Satisfaction** | >4/5 stars | User feedback | Thumbs up/down, surveys | Root cause analysis, A/B test improvements |
| **Tool Success Rate** | >95% | Tool execution logs | Success/failure tracking | Fix tool reliability, add retries, improve prompts |
| **Retrieval Recall** | >85% | RAG eval harness | Recall@K measurement | Improve chunking, tune embedding model, hybrid search |

### Metric Priorities by Use Case

| Use Case | Primary Metrics | Secondary Metrics |
|----------|----------------|-------------------|
| **Customer Support** | User satisfaction, accuracy, latency | Cost, safety |
| **Content Generation** | Quality, creativity, safety | Cost, latency |
| **Data Extraction** | Accuracy, recall, precision | Latency, cost |
| **Code Generation** | Correctness, safety | Latency, cost |
| **Search/RAG** | Recall, groundedness, hallucination | Latency, cost |

---

## Model Selection Matrix

Choose the right model based on task requirements and constraints.

| Use Case | Recommended Model Profile | Context Window | Cost | Latency | When to Use |
|----------|-------------------|----------------|------|---------|-------------|
| **Simple classification/extraction** | Value tier (small/fast) | Standard | $ | Fast | Low complexity, high volume |
| **Complex reasoning** | Premium tier (frontier/large) | Standard | $$$ | Slower | Critical accuracy, low volume |
| **Long context** | Long-context optimized | Large | $$ | Medium | Document analysis, large context |
| **Code generation** | Coding-strong balanced/premium | Standard | $$-$$$ | Medium | Software development |
| **Multimodal** | Vision/multimodal | Standard-Large | $$-$$$ | Medium | Image/video understanding |
| **Cost-sensitive** | Value tier + routing | Standard-Large | $ | Fast | High volume, budget constraints |
| **Self-hosted** | Open-weight models + tuned serving | Varies | Infra | Varies | Privacy, compliance, control |

### Cost Tiers

- **$** = lowest cost tier available
- **$$** = mid-tier cost
- **$$$** = highest cost tier (use selectively)

---

## Cost-Quality Tradeoff Matrix

Optimize model selection based on cost-quality requirements.

### Quality vs Cost Decision Grid

| Quality Requirement | Volume | Budget | Recommended Approach |
|---------------------|--------|--------|---------------------|
| Maximum (critical) | Low (<1k/day) | High | Premium model |
| Maximum (critical) | High (>10k/day) | Any | Fine-tune + balanced model |
| High (user-facing) | Medium | Medium | Balanced model |
| Acceptable (internal) | High | Low | Value model |
| Any | Any | Minimal | Tiered routing (cascade) |

### Model Tiering Strategy (Cascade Pattern)

Route requests by complexity to optimize cost without sacrificing quality:

| Complexity | Detection Method | Model Tier | Expected Cost |
|------------|-----------------|------------|---------------|
| Simple | Short input, classification, extraction | Value ($) | Low |
| Medium | Standard Q&A, summarization | Balanced ($$) | Medium |
| Complex | Multi-step reasoning, code generation | Premium ($$$) | High |

**Expected savings**: 40-60% vs always using premium model

### Prompt Caching ROI

| Scenario | Cache Hit Rate | Cost Reduction | Break-Even |
|----------|---------------|----------------|------------|
| Static system prompts | High | High | Usually immediate |
| RAG with stable context | Medium-High | Medium-High | Usually immediate |
| Multi-turn conversations | Medium | Medium | Often 2-3 turns |
| Dynamic prompts | Low | Low | Often not worth it |

### Fine-Tuning vs Prompting Cost Comparison

| Approach | Upfront Cost | Per-Request Cost | Break-Even | Best For |
|----------|-------------|------------------|-----------------|----------|
| **Prompt only** | Low | Higher (long prompts) | Immediate | Low volume, rapid iteration |
| **Few-shot** | Low | Medium | Immediate | Medium volume |
| **Fine-tuned** | Medium-high | Lower (short prompts) | Use ROI calculator | High volume, stable domain |
| **Hybrid** | Medium | Medium | Use ROI calculator | Balanced |

**Decision rule**: Fine-tune when monthly savings > amortized investment cost

---

## Technology Stack Selection

### Vector Database Selection

| Database | Best For | Scale | Cost | Key Features |
|----------|----------|-------|------|--------------|
| **Pinecone** | Production, managed | 100M+ vectors | $$$ | Fully managed, high performance |
| **Qdrant** | Self-hosted, flexible | 100M+ vectors | $ (self-hosted) | Open source, rich filtering |
| **Chroma** | Development, prototyping | <10M vectors | Free | Embedded, simple API |
| **Weaviate** | Hybrid search, modules | 100M+ vectors | $$ | GraphQL, built-in models |
| **Milvus** | Large scale, distributed | 1B+ vectors | $ (self-hosted) | Highly scalable, Kubernetes-native |
| **Elasticsearch** | Existing infra | 100M+ vectors | $$ | Full-text + vector, familiar |

**Selection criteria:**
- **Development/MVP:** Chroma (simple, embedded)
- **Production <10M vectors:** Qdrant (self-hosted) or Pinecone (managed)
- **Production >100M vectors:** Pinecone, Milvus, or Qdrant Cloud
- **Existing Elasticsearch:** Elasticsearch with vector search
- **Advanced filtering:** Qdrant or Weaviate

### Embedding Model Selection

| Model | Dimensions | Performance | Cost | Best For |
|-------|-----------|-------------|------|----------|
| **OpenAI text-embedding-3-small** | 1536 | Good | $ | General purpose, balanced |
| **OpenAI text-embedding-3-large** | 3072 | Excellent | $$ | High accuracy requirements |
| **Cohere embed-v3** | 1024 | Excellent | $$ | Multilingual, strong |
| **Voyage AI** | 1024-1536 | Excellent | $$ | Domain-specific (code, finance) |
| **BGE-large-en-v1.5** | 1024 | Good | Free (self-hosted) | Self-hosted, open source |
| **all-MiniLM-L6-v2** | 384 | Fair | Free (self-hosted) | Fast, lightweight |

**Selection criteria:**
- **Budget-conscious:** Self-hosted BGE or MiniLM
- **Best accuracy:** OpenAI large or Cohere
- **Multilingual:** Cohere embed-v3
- **Domain-specific:** Voyage AI or fine-tuned open source

### Framework Selection

| Framework | Best For | Complexity | Observability | Community |
|-----------|----------|-----------|--------------|-----------|
| **LangChain** | Quick prototyping, simple chains | Low-Medium | Good (LangSmith) | Largest |
| **LangGraph** | Production agents, state management | Medium-High | Excellent (LangSmith) | Growing |
| **LlamaIndex** | RAG-focused applications | Low-Medium | Good | Large |
| **Haystack** | Search-heavy applications | Medium | Good | Medium |
| **Anthropic Agent SDK** | Claude-specific agents | Medium | Excellent | New (2025) |
| **Custom (DIY)** | Maximum control, specific needs | High | DIY | N/A |

**Selection criteria:**
- **Simple RAG:** LlamaIndex or LangChain
- **Production agents:** LangGraph or Anthropic Agent SDK
- **Search-focused:** Haystack
- **Maximum control:** Custom implementation

---

## Inference Engine Selection Matrix (2026)

Choose the right inference engine based on workload characteristics and infrastructure.

| Engine | Best For | Throughput | TTFT | Setup Complexity | Key Feature |
|--------|----------|------------|------|------------------|-------------|
| **SGLang** | Agents, RAG, chat | High | Good | Low | KV-cache reuse optimizations |
| **vLLM** | High concurrency, general | High | Often best | Low | Broad ecosystem support |
| **TensorRT-LLM** | NVIDIA-optimized serving | Very high | Variable | High | Deep NVIDIA optimization |
| **LMDeploy** | General serving | High | Good | Medium | Alternative serving stack |
| **Ollama** | Local development | Moderate | Good | Very Low | GGUF support, easy setup |

### When to Use Each Engine

| Use Case | Recommended Engine | Reason |
|----------|-------------------|--------|
| **Agent workflows** | SGLang | RadixAttention reuses KV-cache across turns |
| **RAG with repeated prompts** | SGLang | Few-shot examples stay cached |
| **High-concurrency API** | vLLM | Best TTFT, proven at scale |
| **NVIDIA enterprise** | TensorRT-LLM | Maximum hardware utilization on supported NVIDIA stacks |
| **Quick prototyping** | Ollama | Simplest setup, local-first |
| **Production (general)** | vLLM or LMDeploy | Balanced performance and maintainability |

### Benchmarking Guidance

Benchmark on your real workload (prompt shapes, concurrency, output lengths, tool loops). Public benchmarks vary widely by GPU, model, quantization, and scheduling.

---

## Deployment Strategy Matrix

| Strategy | Use When | Complexity | Risk | Rollback Speed |
|----------|----------|-----------|------|----------------|
| **Direct Deployment** | Low-traffic, internal tools | Low | High | Slow (manual) |
| **Blue-Green** | Zero downtime required | Medium | Low | Fast (instant) |
| **Canary (5-10%)** | Production systems | Medium | Medium | Fast (automated) |
| **Shadow Mode** | High-risk changes | High | Very Low | N/A (no user impact) |
| **A/B Testing** | Measuring impact | High | Low | Medium (requires analysis) |
| **Feature Flags** | Gradual rollout, testing | Medium | Low | Fast (config change) |

### Recommended Strategy by System Maturity

| System Stage | Recommended Strategy | Justification |
|--------------|---------------------|---------------|
| **MVP/Development** | Direct deployment | Fast iteration, low traffic |
| **Beta/Staging** | Canary deployment | Test with real users, limited risk |
| **Production** | Canary + shadow mode | Validate before full rollout |
| **Mature Production** | A/B testing + canary | Measure impact, gradual rollout |

---

## Checklists

### Basic RAG Checklist

- [ ] Documents chunked (200-400 tokens)
- [ ] Embedding model selected
- [ ] Vector database configured
- [ ] Retrieval tested (top-k=5)
- [ ] Citation/source tracking
- [ ] Recall >70% on test set

### Advanced RAG Checklist

- [ ] Page-level chunking strategy
- [ ] Hybrid search (BM25 + vector)
- [ ] Cross-encoder reranking
- [ ] Metadata filtering
- [ ] Contextual retrieval (add context to chunks)
- [ ] Recall >85% on test set
- [ ] Groundedness >95%
- [ ] Hallucination <3%

### Modular RAG Checklist

- [ ] Multi-index architecture
- [ ] Query routing logic
- [ ] Agent orchestration
- [ ] Dynamic retrieval strategies
- [ ] Knowledge graph integration (if applicable)
- [ ] Cross-modal data handling
- [ ] Full observability (tracing, metrics)
- [ ] Recall >90% on test set

---

## Quick Decision Trees

### Should I Use RAG?

```
Do you need current/dynamic knowledge?
├─ Yes → Do you have >1000 documents?
│   ├─ Yes → Advanced RAG with hybrid search
│   └─ No → Basic RAG with vector search
└─ No → Use prompt engineering or fine-tuning
```

### Should I Fine-Tune?

```
Do you need custom behavior/style?
├─ Yes → Do you have >1000 examples?
│   ├─ Yes → Fine-tune (PEFT/LoRA recommended)
│   └─ No → Use few-shot prompting
└─ No → Use prompt engineering
```

### Should I Use Agents?

```
Do you need to take actions (API calls, tools)?
├─ Yes → How many tools?
│   ├─ 1-3 tools → Single agent with ReAct
│   └─ >3 tools or complex workflow → Multi-agent system
└─ No → Use RAG or prompt engineering
```

---

## Related Resources

- **[Cost Economics](cost-economics.md)** - Cost modeling, TCO, and ROI frameworks
- **[Fine-Tuning ROI Calculator](../assets/selection/fine-tuning-roi-calculator.md)** - Investment analysis template
- **[Project Planning Patterns](project-planning-patterns.md)** - Stack selection and architecture
- **[Production Checklists](production-checklists.md)** - Pre-deployment validation
- **[Common Design Patterns](common-design-patterns.md)** - Implementation patterns
- **[Anti-Patterns](anti-patterns.md)** - Common mistakes to avoid

---
