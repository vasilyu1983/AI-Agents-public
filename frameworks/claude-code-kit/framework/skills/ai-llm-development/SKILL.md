---
name: ai-llm-development
description: >
  Operational patterns, templates, and decision rules for LLM development (modern best practices):
  strategy selection (prompting vs PEFT/LoRA vs RAG), dataset design and formatting, instruction tuning,
  and evaluation workflows. Leans on specialized skills for prompts, RAG, agents, inference, and safety.
---

# LLM Development – Production Skill Hub

**Modern Best Practices**: PEFT/LoRA fine-tuning, combined approaches (fine-tuning + prompting + RAG), continuous evaluation, and CI/CD integration for prompt versioning.

This skill provides **actionable workflows** for developing LLM-powered systems with focus on execution, not theory.

---

## When to Use This Skill

Claude should invoke this skill when the user asks for **LLM development**, including:

- "Help me design an instruction dataset / SFT corpus."
- "Format my dataset for fine-tuning."
- "Create an evaluation set for my model."
- "Build a data transformation pipeline for SFT."
- "Choose prompting vs tuning vs RAG for this use case."
- "Set up PEFT/LoRA fine-tuning."
- "Implement RLHF or DPO alignment."
- "Build evaluation framework with LLM-as-judge."

---

## Scope Boundaries (Use These Skills for Depth)

- **Prompt design / structured outputs** → [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)
- **Retrieval / RAG** → [ai-llm-rag-engineering](../ai-llm-rag-engineering/SKILL.md)
- **Search tuning (BM25/HNSW/hybrid)** → [ai-llm-search-retrieval](../ai-llm-search-retrieval/SKILL.md)
- **Serving, optimization, quantization** → [ai-llm-ops-inference](../ai-llm-ops-inference/SKILL.md)
- **Security, safety, policy, governance** → [ai-ml-ops-security](../ai-ml-ops-security/SKILL.md)
- **Deployment, APIs** → [ai-ml-ops-production](../ai-ml-ops-production/SKILL.md)

---

## Quick Reference

| Task | Tool/Framework | Command/Pattern | When to Use |
|------|----------------|-----------------|-------------|
| Prompt iteration | Claude/GPT + CI/CD | Version control + automated tests | MVPs, internal tools, fast iteration needed |
| Fine-tuning (efficient) | PEFT/LoRA | `peft.LoraConfig(r=8, lora_alpha=16)` | Production with sufficient data, highest performance |
| Dataset formatting | JSON/JSONL | Instruction/Chat/Transform formats | Preparing SFT data, consistent structure |
| Evaluation | eval frameworks | LangSmith, W&B, custom rubrics | Comparing prompts/models, quality validation |
| RLHF/alignment | DPO/ORPO | Preference data + policy optimization | Safety requirements, tone control |

---

## Decision Tree: LLM Development Strategy

```text
Need LLM-powered feature: [Strategy Selection]
    ├─ MVP/Prototype?
    │   └─ Prompt Engineering → Fast deployment, minimal setup
    │
    ├─ Production + Sufficient Data?
    │   ├─ Static knowledge? → Fine-Tuning (PEFT/LoRA) → Highest performance
    │   └─ Dynamic knowledge? → RAG → Current information access
    │
    ├─ Cold-start (No Data)?
    │   └─ Few-shot Prompting → No persona needed, best results
    │
    └─ Best Results?
        └─ Hybrid (Fine-tuning + Prompting + RAG) → Optimal outcomes
```

**Key Insight**: Combining techniques yields best results. PEFT/LoRA is now standard for efficient fine-tuning.

---

## Modern Best Practices (2024-2025)

### PEFT/LoRA (Now Standard)

- Minimizes trainable parameters while improving performance
- LoRA rank 8-32, alpha 16-64
- 4-bit quantization (QLoRA) for VRAM savings
- Save adapters separately for efficient deployment

### Iteration-First Prompting

- Start simple, refine iteratively
- CI/CD integration with automated tests
- Version control with systematic tracking
- Clear, concise prompts with reasoning steps

### Combined Approaches

- Fine-tuned model + prompt engineering + RAG = best results
- Layer techniques based on use case
- Evaluate each component separately

### Continuous Evaluation

- LLM-as-judge for scalability
- Regression suites in CI/CD
- Production monitoring and drift detection
- A/B testing framework

---

## Navigation: Resources (Best Practices & Operational Guides)

Operational guides with checklists, patterns, and actionable workflows:

### Core Development Patterns

- **Prompt Engineering Patterns** - [resources/prompt-engineering-patterns.md](resources/prompt-engineering-patterns.md)
  - 12 production-tested prompt patterns (Instruction, Few-Shot, JSON, Multi-Step, etc.)
  - Modern iteration-first workflow with CI/CD integration
  - Failure mode debugging guide
  - Prompt library structure and version control

- **Fine-Tuning Recipes** - [resources/fine-tuning-recipes.md](resources/fine-tuning-recipes.md)
  - Strategy selection matrix (Prompting vs Fine-tuning vs RAG)
  - SFT workflow with PEFT/LoRA (modern standard)
  - Instruction tuning and dataset composition
  - Safety requirements and validation
  - Production feedback loops

- **Dataset Formatting Guide** - [resources/dataset-formatting-guide.md](resources/dataset-formatting-guide.md)
  - Instruction, chat, and transformation formats
  - Dataset hygiene rules and quality control
  - Deduplication and validation workflows

- **Evaluation Rubrics** - [resources/evaluation-rubrics.md](resources/evaluation-rubrics.md)
  - 6-dimension evaluation framework (Correctness, Completeness, Format, Clarity, Conciseness, Safety)
  - LLM-as-judge setup and validation
  - A/B testing methodology with statistical significance
  - Regression testing and CI/CD integration
  - Production monitoring metrics

### Advanced Patterns

- **Advanced LLM Patterns** - [resources/advanced-llm-patterns.md](resources/advanced-llm-patterns.md)
  - RLHF / DPO / ORPO alignment workflows
  - Pretraining path (tokenizer → corpus → schedule)
  - Task-specific tuning (classification, embeddings, multimodal)
  - Context engineering best practices
  - Production monitoring and observability
  - Synthetic data generation
  - Model compression and distillation
  - Multi-task learning

Each resource includes:
- Execution-ready checklists
- Copy-paste templates
- "What can go wrong" scenarios
- Validation criteria

---

## Navigation: Templates (Copy-Paste Ready)

Production templates organized by use case:

### Prompt Templates

- [Task Prompt](templates/prompts/template-task.md) - General-purpose structured LLM task
- [JSON-Only Prompt](templates/prompts/template-json.md) - Strict JSON output enforcement
- [Transformation Prompt](templates/prompts/template-transform.md) - Classification, extraction, rewriting
- [System Role Prompt](templates/prompts/template-system-role.md) - Assistant behavior and policy

### Fine-Tuning Templates

- [SFT Dataset](templates/fine-tuning/template-sft-dataset.jsonl) - Supervised fine-tuning format (JSONL)
- [Instruction Dataset](templates/fine-tuning/template-instruction.jsonl) - Instruction tuning format with chat messages
- [Training Configuration](templates/fine-tuning/template-config.md) - Hyperparameters, PEFT/LoRA settings

### Evaluation Templates

- [Evaluation Set](templates/eval/template-eval-set.md) - Test suite structure for prompt and model quality

---

## Related Skills

This skill focuses on **LLM development** (prompting, fine-tuning, datasets). For related workflows:

**LLM Engineering & Production:**
→ [ai-llm-engineering](../ai-llm-engineering/SKILL.md)

- Comprehensive LLMOps lifecycle (data, training, deployment, monitoring)
- RAG pipelines (page-level chunking, hybrid retrieval)
- Agentic orchestration (reflection, multi-agent)
- Production evaluation frameworks

**Prompt Engineering Fundamentals:**
→ [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)

- Core prompting techniques (few-shot, chain-of-thought, ReAct)
- Prompt design patterns and best practices
- Structured prompting for agents

**RAG (Retrieval-Augmented Generation):**
→ [ai-llm-rag-engineering](../ai-llm-rag-engineering/SKILL.md)

- Chunking strategies (basic, code, long-doc)
- Context packing and grounding patterns
- Hybrid search and reranking
- RAG evaluation frameworks

**Search & Retrieval:**
→ [ai-llm-search-retrieval](../ai-llm-search-retrieval/SKILL.md)

- BM25 tuning and vector search patterns
- Hybrid fusion (RRF, weighted)
- Query rewriting and ranking pipelines

**LLM Inference & Optimization:**
→ [ai-llm-ops-inference](../ai-llm-ops-inference/SKILL.md)

- vLLM, TensorRT-LLM, DeepSpeed configurations
- Quantization (GPTQ, AWQ, GGUF)
- Batching, caching, speculative decoding
- Serving architectures for high throughput

**Production Deployment:**
→ [ai-ml-ops-production](../ai-ml-ops-production/SKILL.md)

- API service deployment patterns
- Monitoring and drift detection
- Data ingestion pipelines (dlt)
- Batch processing workflows

**Security & Safety:**
→ [ai-ml-ops-security](../ai-ml-ops-security/SKILL.md)

- Prompt injection mitigation
- Jailbreak defense strategies
- Privacy protection (PII handling, anonymization)
- Guardrail configurations and output filtering

**Use Case Decision:**

- **Building/refining prompts or fine-tuning datasets** → Use this skill (ai-llm-development)
- **Production LLM systems with RAG/agents** → Use ai-llm-engineering
- **Optimizing inference performance** → Use ai-llm-ops-inference
- **Implementing RAG** → Use ai-llm-rag-engineering
- **Security & compliance** → Use ai-ml-ops-security

---

## External Resources

See [data/sources.json](data/sources.json) for 55+ curated resources including:

- **LLM Platforms**: OpenAI, Anthropic Claude, Google Gemini, Cohere, Together AI
- **Open-Source Models**: Hugging Face Hub, Llama, Mistral, Qwen, Phi
- **Fine-Tuning**: Transformers, PEFT, LoRA/QLoRA, Axolotl, LLaMA-Factory
- **Prompt Engineering**: Anthropic Prompt Library, OpenAI guides, LangChain Hub
- **Evaluation**: EleutherAI LM Eval, HELM, OpenAI Evals, LangSmith, PromptFoo
- **Data Preparation**: Hugging Face Datasets, Common Crawl, The Pile, RedPajama
- **Quantization**: bitsandbytes, GPTQ, AWQ, GGUF
- **Synthetic Data**: Distilabel, Argilla, LLM Blender
- **Benchmarks**: MMLU, HumanEval, BigBench, Open LLM Leaderboard, AlpacaEval, MT-Bench

---

## Usage Notes for Claude

- **Modern Standards**: Default to PEFT/LoRA for fine-tuning, iteration-first for prompting, continuous evaluation
- Use resources for detailed operational guidance
- Use templates when the user asks for **structured artifacts**
- Reference `data/sources.json` for authoritative documentation links
- Never include theoretical explanations; only operational steps

**Key Modern Migrations**:
- Full fine-tuning → PEFT/LoRA (parameter-efficient)
- One-shot prompting → Iterative refinement + CI/CD
- Manual evaluation → Automated + LLM-as-judge + regression suites
- Prompting OR fine-tuning → Combined approaches (hybrid)

---
