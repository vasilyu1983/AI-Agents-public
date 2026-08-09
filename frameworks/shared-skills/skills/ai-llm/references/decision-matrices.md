# Decision Matrices

Quick reference tables for LLM system architecture, technology selection, and operational decisions.

## Table of Contents

- [RAG Type Decision Matrix](#rag-type-decision-matrix)
- [Production Evaluation Table](#production-evaluation-table)
- [Model Selection Matrix](#model-selection-matrix)
- [Technology Stack Selection](#technology-stack-selection)
- [Inference Engine Selection Matrix (2026)](#inference-engine-selection-matrix-2026)

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

> **July 2026 Anthropic flagship note**: Anthropic's highest tier now includes **Claude Fable 5** (`claude-fable-5`, $10/$50 per MTok, 1M context, 128k output, GA since 2026-06-09) and **Claude Mythos 5** (research/Project Glasswing only). Fable 5 includes a safety-classifier fallback: <5% of high-risk sessions are served by **Claude Opus 4.8** instead. Migration and SLA design must account for this fallback — response-contract assumptions that hold for Fable 5 must also hold for Opus 4.8. Claude Opus 4.8 ($5/$25 per MTok) remains the standalone flagship for workloads that do not require Fable-level capability. **Claude Sonnet 5** (`claude-sonnet-5`, GA 2026-06-30) replaced Sonnet 4.6 as the current speed/intelligence-balance tier — list price $3/$15 per MTok, with introductory pricing of $2/$10 through 2026-08-31 (verify the pricing page has not reverted before budgeting off the low number). Gemini 3.1 Pro (large context) and Gemini 3.5 Flash are Google's current frontier options — verify exact context limits at ai.google.dev before citing a number. On the OpenAI side, **GPT-5.6** (Luna/Terra/Sol tiers) is the current public flagship family as of 2026-07-09; Sol targets long-horizon agentic/cyber/science work. Treat all figures above as a dated snapshot, not a durable ranking.

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

## MoE vs Dense Architecture Decision

Choose between Mixture-of-Experts (MoE) and dense models when selecting a base model or planning a training run.

### Core Tradeoff

MoE models activate only a subset of parameters per token ("active parameters"), giving higher effective capacity at the same training FLOP budget — but at the cost of routing infrastructure and higher memory footprint for the full parameter set.

| Dimension | Dense | MoE |
|-----------|-------|-----|
| **Active params at inference** | All params | Small fraction (e.g., 1/8 of total) |
| **Total params in memory** | = active | Much larger than active |
| **Training efficiency** | Straightforward | More complex (routing, load balancing, expert collapse risk) |
| **Inference memory** | Proportional to model size | Must load all experts even when only a few activate per token |
| **Throughput (high batch)** | Good | Can be higher per FLOP |
| **Serving complexity** | Low | Higher: expert parallelism, load balancing across GPUs |
| **Fine-tuning** | Straightforward | Harder: expert routing may shift; some experts may be underused |

### Decision Node: When to Choose MoE

```text
Do you control the model architecture (training from scratch or selecting open weights)?
├─ No (using a hosted API or fixed checkpoint) → choice is made; skip this decision
└─ Yes
    ├─ Is inference memory the primary constraint?
    │   └─ If yes → Dense is often safer: MoE requires loading all experts
    ├─ Is throughput at scale the primary goal with ample GPU memory?
    │   └─ If yes → MoE may give better quality-per-FLOP at high batch sizes
    ├─ Do you need to fine-tune the model?
    │   └─ If yes → Dense: MoE fine-tuning is more complex and less well-supported in open tools
    ├─ Is serving infrastructure simple (single GPU, edge)?
    │   └─ If yes → Dense: MoE expert parallelism adds significant ops burden
    └─ Large-scale training with distributed infra and no fine-tuning planned?
        └─ MoE is viable; requires expert parallelism (EP) support in your training stack
```

### Key MoE Risks

- **Expert collapse**: some experts receive most of the routing load while others receive none; mitigated by auxiliary load-balancing loss (verify your framework supports this).
- **Memory vs compute mismatch**: MoE gives compute savings but not memory savings; all parameters must be loaded.
- **Routing overhead**: top-k routing adds latency; at very small batch sizes the routing overhead can dominate.
- **Load balancing across GPUs**: in distributed serving, experts must be spread across GPUs (expert parallelism); verify support in your inference engine — see [ai-llm-inference: moe-expert-parallelism](../../ai-llm-inference/references/moe-expert-parallelism.md).

---

## Distributed Training Decision Matrix

Choose the right parallelism strategy based on model scale and hardware configuration.

### Parallelism Strategies

| Strategy | What It Does | When to Use | Memory Benefit | Communication Cost |
|----------|-------------|-------------|----------------|-------------------|
| **Data Parallelism (DP)** | Each GPU holds full model; data is split across GPUs | Small-to-medium models that fit on one GPU | None (model duplicated) | Gradient all-reduce per step |
| **Tensor Parallelism (TP)** | Splits individual weight matrices across GPUs | Model too large for one GPU; prefer within a node (NVLink) | Proportional to TP degree | High (all-reduce within each layer) |
| **Pipeline Parallelism (PP)** | Assigns different layers to different GPUs | Very deep models; acceptable micro-batch latency | Proportional to PP degree | Activation send/recv between stages |
| **Expert Parallelism (EP)** | Distributes MoE experts across GPUs | MoE models only | Proportional to EP degree | Routing communication per token |
| **FSDP (Fully Sharded DP)** | Shards model params, grads, and optimizer state across GPUs | Any scale; strong default for PyTorch/HF stack | Full shard benefit | All-gather before each forward/backward |
| **ZeRO Stage 1/2/3** | Shards optimizer state (1), + grads (2), + params (3) | Any scale; strong default for DeepSpeed stack | Increases with stage | All-gather at ZeRO-3; overlapped |

### Recommended Combinations by Model Scale

| Model Scale | Recommended Strategy | Notes |
|-------------|---------------------|-------|
| ≤7B params, multi-GPU node | FSDP or ZeRO-2 + DP | Sufficient for most PEFT/LoRA runs |
| 7–70B, multi-GPU | FSDP + DP, or ZeRO-3 | ZeRO-3 reduces peak memory further; adds all-gather overhead |
| 70B+, multi-node | TP within node + PP across nodes + DP, or FSDP + DP | TP is NVLink-sensitive; cross-node TP is expensive |
| MoE (any scale) | EP + DP (or TP + EP + DP for very large) | EP is required to spread experts; verify engine support |
| Full pretraining (100B+) | TP + PP + DP (3D parallelism) | Megatron-LM or FSDP+SP; requires careful micro-batch tuning |

### Decision Rules

- **Default for fine-tuning (PEFT/LoRA)**: FSDP or ZeRO-2/3 — best tooling support in Hugging Face ecosystem.
- **Default for full fine-tuning / pretraining at scale**: 3D parallelism (TP + PP + DP) via Megatron-LM or equivalent; ZeRO-3 for DeepSpeed stacks.
- **Avoid TP across nodes** unless you have high-bandwidth interconnect (InfiniBand HDR/NDR); cross-node TP is bandwidth-limited and often slower than PP.
- **Pipeline PP bubble overhead**: PP introduces idle time ("bubble") between micro-batches; minimize with interleaved scheduling and larger global batch sizes.
- **Verify current framework support** before committing: FSDP, ZeRO, and EP implementations evolve rapidly. Check PyTorch FSDP2 (PyTorch 2.x), DeepSpeed, and vLLM/SGLang docs for current status.

---

## Related Resources

- **[Cost Economics](cost-economics.md)** - Cost modeling, TCO, and ROI frameworks
- **[Fine-Tuning ROI Calculator](../assets/selection/fine-tuning-roi-calculator.md)** - Investment analysis template
- **[Project Planning Patterns](project-planning-patterns.md)** - Stack selection and architecture
- **[Production Checklists](production-checklists.md)** - Pre-deployment validation
- **[Common Design Patterns](common-design-patterns.md)** - Implementation patterns
- **[Anti-Patterns](anti-patterns.md)** - Common mistakes to avoid
- **[Post-Training 2026](post-training.md)** - 2026 post-training algorithm decision tree
- **[ai-llm-inference: MoE Expert Parallelism](../../ai-llm-inference/references/moe-expert-parallelism.md)** - MoE serving depth

---
