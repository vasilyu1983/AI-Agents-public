---
name: ai-llm
description: Production LLM engineering skill. Covers strategy selection (prompting vs RAG vs fine-tuning), dataset design, PEFT/LoRA, evaluation workflows, deployment handoff to inference serving, and lifecycle operations with cost/safety controls.
---

# LLM Development & Engineering — Complete Reference

Build, evaluate, and deploy LLM systems with **modern production standards**.

This skill covers the full LLM lifecycle:

- **Development**: Strategy selection, dataset design, instruction tuning, PEFT/LoRA fine-tuning
- **Evaluation**: Automated testing, LLM-as-judge, metrics, rollout gates
- **Deployment**: Serving handoff, latency/cost budgeting, reliability patterns (see `ai-llm-inference`)
- **Operations**: Quality monitoring, change management, incident response (see `ai-mlops`)
- **Safety**: Threat modeling, data governance, layered mitigations (NIST AI RMF: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)

**Modern Best Practices (January 2026)**:

- Treat the model as a **component** with contracts, budgets, and rollback plans (not "magic").
- Separate **core concepts** (tokenization, context, training vs adaptation) from **implementation choices** (providers, SDKs).
- Gate upgrades with repeatable evals and staged rollout; avoid blind model swaps.
- **Cost-aware engineering**: Measure cost per successful outcome, not just cost per token. Model selection is a cost-quality tradeoff decision.

**For detailed patterns:** See [Resources](#resources-best-practices--operational-patterns) and [Templates](#templates-copy-paste-ready) sections below.

---

## Quick Reference

| Task | Tool/Framework | Command/Pattern | When to Use |
|------|----------------|-----------------|-------------|
| Choose architecture | Prompt vs RAG vs fine-tune | Start simple; add retrieval/adaptation only if needed | New products and migrations |
| Model selection | Scoring matrix | Quality/latency/cost/privacy/license weighting | Provider changes and procurement |
| **Cost optimization** | Tiered models + caching | Cascade routing, prompt caching, budget guardrails | Cost-sensitive production |
| **Fine-tuning ROI** | ROI calculator | Break-even analysis, TCO comparison | Investment decisions |
| Prompt contracts | Structured output + constraints | JSON schema, max tokens, refusal rules | Reliability and integration |
| RAG integration | Hybrid retrieval + grounding | Retrieve → rerank → pack → cite → verify | Fresh/large corpora, traceability |
| Fine-tuning | PEFT/LoRA (when justified) | Small targeted datasets + regression suite | Stable domains, repeated tasks |
| Evaluation | Offline + online | Golden sets + A/B + canary + monitoring | Prevent regressions and drift |

---

## Decision Tree: LLM System Architecture

```text
Building LLM application: [Architecture Selection]
    ├─ Need current knowledge?
    │   ├─ Simple Q&A? → Basic RAG (page-level chunking + hybrid retrieval)
    │   └─ Complex retrieval? → Advanced RAG (reranking + contextual retrieval)
    │
    ├─ Need tool use / actions?
    │   ├─ Single task? → Simple agent (ReAct pattern)
    │   └─ Multi-step workflow? → Multi-agent (LangGraph, CrewAI)
    │
    ├─ Static behavior sufficient?
    │   ├─ Quick MVP? → Prompt engineering (CI/CD integrated)
    │   └─ Production quality? → Fine-tuning (PEFT/LoRA)
    │
    └─ Best results?
        └─ Hybrid (RAG + Fine-tuning + Agents) → Comprehensive solution
```

**See [Decision Matrices](references/decision-matrices.md) for detailed selection criteria.**

---

## Cost-Quality Decision Framework

LLM costs are dominated by token costs (60-80% of TCO). Model selection is fundamentally a **cost-quality tradeoff**.

### Model Tier Strategy

| Tier | Models | Cost | Use For |
|------|--------|------|---------|
| **Value** | Haiku, GPT-4o-mini, Gemini Flash | <$1/1M tokens | High-volume, simple tasks |
| **Balanced** | Sonnet, GPT-4o | $3-15/1M tokens | Production workloads |
| **Premium** | Opus 4.5 | $15-75/1M tokens | Maximum quality, complex reasoning |

### Cost Optimization Levers

1. **Model tiering**: Route simple requests to cheaper models (40-60% savings)
2. **Prompt caching**: Reuse static context (90% input cost reduction with Anthropic)
3. **Prompt optimization**: Compress examples and instructions (20-40% token reduction)
4. **Output limits**: Set appropriate max_tokens (prevents runaway costs)

### When to Fine-Tune (ROI-Based)

Fine-tuning investment ($15k-100k typical) pays off when:
- **Volume justifies it**: >10k requests/month provides meaningful cost savings
- **Domain is stable**: Requirements unchanged for >6 months
- **Data exists**: >1,000 quality training examples available
- **Break-even achievable**: <12 months to recover investment

**See [Cost Economics](references/cost-economics.md) for TCO modeling and [Fine-Tuning ROI Calculator](assets/selection/fine-tuning-roi-calculator.md) for investment analysis.**

---

## Core Concepts (Vendor-Agnostic)

- **Model classes**: encoder-only, decoder-only, encoder-decoder, multimodal; choose based on task and latency.
- **Tokenization & limits**: context window, max output, and prompt/template overhead drive both cost and tail latency.
- **Adaptation options**: prompting → retrieval → adapters (LoRA) → full fine-tune; choose by stability and ROI (LoRA: https://arxiv.org/abs/2106.09685).
- **Evaluation**: metrics must map to user value; report uncertainty and slice performance, not only global averages.
- **Governance**: data retention, residency, licensing, and auditability are product requirements (EU AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj; NIST GenAI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf).

## Implementation Practices (Tooling Examples)

- Use a **provider abstraction** (gateway/router) to enable fallbacks and staged upgrades.
- Instrument requests with tokens, latency, and error classes (OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- Maintain **prompt/model registries** with versioning, changelogs, and rollback criteria.

## Do / Avoid

**Do**
- Do pin model + prompt versions in production, and re-run evals before any change.
- Do enforce budgets at the boundary: max tokens, max tools, max retries, max cost.
- Do plan for degraded modes (smaller model, cached answers, “unable to answer”).

**Avoid**
- Avoid model sprawl (unowned variants with no eval coverage).
- Avoid blind upgrades based on anecdotal quality; require measured impact.
- Avoid training on production logs without consent, governance, and leakage controls.

## When to Use This Skill

Claude should invoke this skill when the user asks about:

- LLM preflight/project checklists, production best practices, or data pipelines
- Building or deploying RAG, agentic, or prompt-based LLM apps
- Prompt design, chain-of-thought (CoT), ReAct, or template patterns
- Troubleshooting LLM hallucination, bias, retrieval issues, or production failures
- Evaluating LLMs: benchmarks, multi-metric eval, or rollout/monitoring
- LLMOps: deployment, rollback, scaling, resource optimization
- Technology stack selection (models, vector DBs, frameworks)
- Production deployment strategies and operational patterns

---

## Scope Boundaries (Use These Skills for Depth)

- **Prompt design & CI/CD** → [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)
- **RAG pipelines & chunking** → [ai-rag](../ai-rag/SKILL.md)
- **Search tuning (BM25, HNSW, hybrid)** → [ai-rag](../ai-rag/SKILL.md)
- **Agent architectures & tools** → [ai-agents](../ai-agents/SKILL.md)
- **Serving optimization/quantization** → [ai-llm-inference](../ai-llm-inference/SKILL.md)
- **Production deployment/monitoring** → [ai-mlops](../ai-mlops/SKILL.md)
- **Security/guardrails** → [ai-mlops](../ai-mlops/SKILL.md)

---

## Resources (Best Practices & Operational Patterns)

Comprehensive operational guides with checklists, patterns, and decision frameworks:

### Core Operational Patterns

- **[Cost Economics & Decision Frameworks](references/cost-economics.md)** - Cost modeling, unit economics, TCO analysis
  - Token cost quick reference (January 2026 pricing)
  - Cost-quality tradeoff framework and decision matrix
  - Total Cost of Ownership (TCO) calculation
  - Fine-tuning ROI framework and break-even analysis
  - Prompt caching economics
  - Cost monitoring and budget guardrails

- **[Project Planning Patterns](references/project-planning-patterns.md)** - Stack selection, FTI pipeline, performance budgeting
  - AI engineering stack selection matrix
  - Feature/Training/Inference (FTI) pipeline blueprint
  - Performance budgeting and goodput gates
  - Progressive complexity (prompt → RAG → fine-tune → hybrid)

- **[Production Checklists](references/production-checklists.md)** - Pre-deployment validation and operational checklists
  - LLM lifecycle checklist (modern production standards)
  - Data & training, RAG pipeline, deployment & serving
  - Safety/guardrails, evaluation, agentic systems
  - Reliability & data infrastructure (DDIA-grade)
  - Weekly production tasks

- **[Common Design Patterns](references/common-design-patterns.md)** - Copy-paste ready implementation examples
  - Chain-of-Thought (CoT) prompting
  - ReAct (Reason + Act) pattern
  - RAG pipeline (minimal to advanced)
  - Agentic planning loop
  - Self-reflection and multi-agent collaboration

- **[Decision Matrices](references/decision-matrices.md)** - Quick reference tables for selection
  - RAG type decision matrix (naive → advanced → modular)
  - Production evaluation table with targets and actions
  - Model selection matrix (GPT-4, Claude, Gemini, self-hosted)
  - Vector database, embedding model, framework selection
  - Deployment strategy matrix

- **[Anti-Patterns](references/anti-patterns.md)** - Common mistakes and prevention strategies
  - Data leakage, prompt dilution, RAG context overload
  - Agentic runaway, over-engineering, ignoring evaluation
  - Hard-coded prompts, missing observability
  - Detection methods and prevention code examples

### Domain-Specific Patterns

- **[LLMOps Best Practices](references/llmops-best-practices.md)** - Operational lifecycle and deployment patterns
- **[Evaluation Patterns](references/eval-patterns.md)** - Testing, metrics, and quality validation
- **[Prompt Engineering Patterns](references/prompt-engineering-patterns.md)** - Quick reference (canonical skill: [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md))
- **[Agentic Patterns](references/agentic-patterns.md)** - Quick reference (canonical skill: [ai-agents](../ai-agents/SKILL.md))
- **[RAG Best Practices](references/rag-best-practices.md)** - Quick reference (canonical skill: [ai-rag](../ai-rag/SKILL.md))

**Note:** Each resource file includes preflight/validation checklists, copy-paste reference tables, inline templates, anti-patterns, and decision matrices.

---

## Templates (Copy-Paste Ready)

Production templates by use case and technology:

### Selection & Governance

- **[Model Selection Matrix](assets/selection/model-selection-matrix.md)** - Documented selection, scoring, licensing, and governance
- **[Fine-Tuning ROI Calculator](assets/selection/fine-tuning-roi-calculator.md)** - Investment analysis, break-even, go/no-go decisions

### RAG Pipelines

- **[Basic RAG](assets/rag-pipelines/template-basic-rag.md)** - Simple retrieval-augmented generation
- **[Advanced RAG](assets/rag-pipelines/template-advanced-rag.md)** - Hybrid retrieval, reranking, contextual embeddings

### Prompt Engineering

- **[Chain-of-Thought](assets/prompt-engineering/template-cot.md)** - Step-by-step reasoning pattern
- **[ReAct](assets/prompt-engineering/template-react.md)** - Reason + Act for tool use

### Agentic Workflows

- **[Reflection Agent](assets/agentic-workflows/template-reflection.md)** - Self-critique and improvement
- **[Multi-Agent](assets/agentic-workflows/template-multi-agent.md)** - Manager-worker orchestration

### Data Pipelines

- **[Data Quality](assets/data-pipelines/template-data-quality.md)** - Validation, deduplication, PII detection

### Deployment

- **[LLM Deployment](assets/deployment/template-llm-deployment.md)** - Production deployment with monitoring

### Evaluation

- **[Multi-Metric Evaluation](assets/evaluation/template-multi-metric.md)** - Comprehensive testing suite

---

## Shared Utilities (Centralized patterns — extract, don't duplicate)

- [../software-clean-code-standard/utilities/llm-utilities.md](../software-clean-code-standard/utilities/llm-utilities.md) — Token counting, streaming, cost estimation
- [../software-clean-code-standard/utilities/error-handling.md](../software-clean-code-standard/utilities/error-handling.md) — Effect Result types, correlation IDs
- [../software-clean-code-standard/utilities/resilience-utilities.md](../software-clean-code-standard/utilities/resilience-utilities.md) — p-retry v6, circuit breaker for LLM API calls
- [../software-clean-code-standard/utilities/logging-utilities.md](../software-clean-code-standard/utilities/logging-utilities.md) — pino v9 + OpenTelemetry integration
- [../software-clean-code-standard/utilities/observability-utilities.md](../software-clean-code-standard/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics
- [../software-clean-code-standard/utilities/config-validation.md](../software-clean-code-standard/utilities/config-validation.md) — Zod 3.24+, secrets management for API keys
- [../software-clean-code-standard/utilities/testing-utilities.md](../software-clean-code-standard/utilities/testing-utilities.md) — Test factories, fixtures, mocks
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) — Canonical clean code rules (`CC-*`) for citation

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about LLM development, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best LLM model for [use case]?"
- "What should I use for [RAG/fine-tuning/agents]?"
- "What's the latest in LLM development?"
- "Current best practices for [prompting/evaluation/deployment]?"
- "Is [model/framework] still relevant in 2026?"
- "[Model A] vs [Model B]?" or "[Framework A] vs [Framework B]?"
- "Best vector database for [use case]?"
- "What agent framework should I use?"

### Required Searches

1. Search: `"LLM best practices 2026"`
2. Search: `"[specific model/framework] vs alternatives 2026"`
3. Search: `"LLM development trends January 2026"`
4. Search: `"[RAG/agents/fine-tuning] new releases 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What models/frameworks are popular NOW (not 6 months ago)
- **Emerging trends**: New models, frameworks, or techniques gaining traction
- **Deprecated/declining**: Models/frameworks losing relevance or support
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with fresh search)

- Latest frontier models (GPT-4.5, Claude 4, Gemini 2.x, Llama 4)
- Agent frameworks (LangGraph, CrewAI, AutoGen, Semantic Kernel)
- Vector databases (Pinecone, Qdrant, Weaviate, pgvector)
- RAG techniques (contextual retrieval, agentic RAG, graph RAG)
- Inference engines (vLLM, TensorRT-LLM, SGLang)
- Evaluation frameworks (RAGAS, DeepEval, Braintrust)

---

## Related Skills

This skill integrates with complementary Claude Code skills:

### Core Dependencies

- **[ai-rag](../ai-rag/SKILL.md)** - Retrieval pipelines: chunking, hybrid search, reranking, evaluation
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** - Systematic prompt design, evaluation, testing, and optimization
- **[ai-agents](../ai-agents/SKILL.md)** - Agent architectures, tool use, multi-agent systems, autonomous workflows

### Production & Operations

- **[ai-llm-inference](../ai-llm-inference/SKILL.md)** - Production serving, quantization, batching, GPU optimization
- **[ai-mlops](../ai-mlops/SKILL.md)** - Deployment, monitoring, incident response, security, and governance

---

## External Resources

See **[data/sources.json](data/sources.json)** for 50+ curated authoritative sources:

- **Official LLM platform docs** - OpenAI, Anthropic, Gemini, Mistral, Azure OpenAI, AWS Bedrock
- **Open-source models and frameworks** - HuggingFace Transformers, open-weight models, PEFT/LoRA, distributed training/inference stacks
- **RAG frameworks and vector DBs** - LlamaIndex, LangChain 1.2+, LangGraph, LangGraph Studio v2, Haystack, Pinecone, Qdrant, Chroma
- **Agent frameworks (examples)** - LangGraph, Semantic Kernel, AutoGen, CrewAI
- **RAG innovations (examples)** - Graph-based retrieval, hybrid retrieval, online evaluation loops
- **Prompt engineering** - Anthropic Prompt Library, Prompt Engineering Guide, CoT/ReAct patterns
- **Evaluation and monitoring** - OpenAI Evals, HELM, Anthropic Evals, LangSmith, W&B, Arize Phoenix
- **Production deployment** - Model gateways/routers, self-hosted serving, managed endpoints

---

## Usage

### For New Projects

1. Start with **[Production Checklists](references/production-checklists.md)** - Validate all pre-deployment requirements
2. Use **[Decision Matrices](references/decision-matrices.md)** - Select technology stack
3. Reference **[Project Planning Patterns](references/project-planning-patterns.md)** - Design FTI pipeline
4. Implement with **[Common Design Patterns](references/common-design-patterns.md)** - Copy-paste code examples
5. Avoid **[Anti-Patterns](references/anti-patterns.md)** - Learn from common mistakes

### For Troubleshooting

1. Check **[Anti-Patterns](references/anti-patterns.md)** - Identify failure modes and mitigations
2. Use **[Decision Matrices](references/decision-matrices.md)** - Evaluate if architecture fits use case
3. Reference **[Common Design Patterns](references/common-design-patterns.md)** - Verify implementation correctness

### For Ongoing Operations

1. Follow **[Production Checklists](references/production-checklists.md)** - Weekly operational tasks
2. Integrate **[Evaluation Patterns](references/eval-patterns.md)** - Continuous quality monitoring
3. Apply **[LLMOps Best Practices](references/llmops-best-practices.md)** - Deployment and rollback procedures

---

## Navigation Summary

**Quick Decisions:** [Decision Matrices](references/decision-matrices.md)
**Pre-Deployment:** [Production Checklists](references/production-checklists.md)
**Planning:** [Project Planning Patterns](references/project-planning-patterns.md)
**Implementation:** [Common Design Patterns](references/common-design-patterns.md)
**Troubleshooting:** [Anti-Patterns](references/anti-patterns.md)

**Domain Depth:** [LLMOps](references/llmops-best-practices.md) | [Evaluation](references/eval-patterns.md) | [Prompts](references/prompt-engineering-patterns.md) | [Agents](references/agentic-patterns.md) | [RAG](references/rag-best-practices.md)

**Templates:** [assets/](assets/) - Copy-paste ready production code

**Sources:** [data/sources.json](data/sources.json) - Authoritative documentation links

---
