---
name: ai-llm
description: "Guides the LLM lifecycle from strategy to deployment. Use when planning, comparing, fine-tuning, distilling, compressing, migrating, or operating LLM systems."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# LLM Engineering - Lifecycle Skill

**Modern Best Practices**: treat the model as a versioned component with contracts, eval gates, rollout controls, cost budgets, and explicit fallback paths. Prefer stable decision criteria over static "best model" lists, and verify volatile provider facts against current official docs before recommending a stack.

This skill is the **umbrella skill** for deciding how to build, adapt, evaluate, migrate, and operate LLM systems.

Use this skill for **architecture and lifecycle decisions**.
Use sibling skills for **implementation depth**.

No theory. No generic AI history. Focus on operational choices, tradeoffs, checklists, and reusable templates.

## ASCII Flow

```text
LLM product need
  |
  v
outcome contract
  task + users + quality + latency + cost + privacy/compliance
  |
  v
architecture choice
  prompt-only -> RAG -> tools/agents -> adaptation/fine-tuning -> hybrid
  |
  v
evaluation and rollout
  golden set + edge cases + canary + observability + rollback
  |
  v
operated model component
  versioned prompts/models/configs + fallbacks + governance
```

## When to Use This Skill

Activate this skill when the user asks for:

- Choosing between prompt-only, RAG, tool use, fine-tuning, or hybrid LLM architectures
- Selecting a provider, model tier, or deployment path for a production workload
- Planning or reviewing model/provider migrations
- Designing eval suites, graders, rollout gates, and regression policies
- Calculating cost, latency, and quality tradeoffs at the system level
- Defining LLM governance: data handling, safety boundaries, compliance, and rollback
- Building current recommendations that depend on provider/platform capabilities
- Creating a preflight plan for an LLM project before implementation begins

## Scope Boundaries (Use These Skills for Depth)

- **Choosing the approach first (classical ML vs LLM vs RAG vs fine-tune vs agent)** -> [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md)
- **Eval methodology: LLM-judge bias, framework choice, threshold calibration, reproducibility** -> [ai-evals](../ai-evals/SKILL.md)
- **Prompt design, structured outputs, prompt CI/CD** -> [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)
- **RAG design, chunking, retrieval, reranking** -> [ai-rag](../ai-rag/SKILL.md)
- **Agent architectures, MCP tools, multi-agent orchestration** -> [ai-agents](../ai-agents/SKILL.md)
- **Serving optimization, batching, routing, quantization** -> [ai-llm-inference](../ai-llm-inference/SKILL.md)
- **Deployment, monitoring, incident response, security depth** -> [ai-mlops](../ai-mlops/SKILL.md)
- **Hugging Face-specific LLM training workflows (TRL, SFT, DPO, GRPO)** -> use the `huggingface-skills:` plugin (external)
- **Build a transformer/GPT and BPE tokenizer from scratch (pre-training layer)** -> [ai-pretraining](../ai-pretraining/SKILL.md)
- **Multi-GPU pre-training: FSDP, DeepSpeed ZeRO, tensor/pipeline parallelism, reproduce GPT-2** -> [ai-distributed-training](../ai-distributed-training/SKILL.md)
- **Scaling laws, Chinchilla compute-optimal sizing, token/param budget** -> [ai-scaling-laws](../ai-scaling-laws/SKILL.md)
- **Web-scale + synthetic pre-training corpus curation and data ablations** -> [ai-data-curation-pretraining](../ai-data-curation-pretraining/SKILL.md)
- **Post-training depth: RLHF/PPO, DPO, GRPO, RLVR, reward modeling, alignment, and reasoning-model training** -> [ai-post-training](../ai-post-training/SKILL.md)

## Default Workflow

1. **Clarify the outcome**: task, users, required quality, latency budget, cost ceiling, privacy/compliance constraints.
2. **Pick the simplest architecture that can work**: prompt-only -> RAG -> tool use/agent -> adaptation/fine-tuning -> hybrid.
3. **Define the contract first**: input shape, output contract, allowed tools, retrieval boundaries, failure modes.
4. **Choose the adaptation path**: prompting, retrieval, adapters/SFT, preference optimization, or a combination.
5. **Design evaluation before rollout**: golden set, edge cases, adversarial cases, format validation, online checks.
6. **Plan deployment controls**: versioning, canarying, observability, rollback, degraded mode.

## Decision Tree: Architecture and Adaptation

```text
Starting an LLM project
    │
    ├─ Is the task mostly instruction following with stable inputs?
    │   └─ Start prompt-only with explicit contracts and evals
    │
    ├─ Do you need current or private knowledge?
    │   └─ Add retrieval (RAG) before considering fine-tuning
    │
    ├─ Do you need external actions or tool use?
    │   └─ Add bounded tool use or an agent workflow
    │
    ├─ Does the system still fail in a repeated, stable way after prompt/RAG/tool fixes?
    │   └─ Consider adapters/SFT or preference optimization
    │
    └─ Do you need multiple capabilities together?
        └─ Build a hybrid system, but keep each layer independently testable
```

## Quick Reference

| Decision Area | Default Move | Promote Complexity When | Avoid |
|---------------|--------------|--------------------------|-------|
| Architecture selection | Start prompt-only | Missing knowledge, repeated failures, or external actions are required | Jumping straight to fine-tuning |
| Retrieval | Add hybrid retrieval + citations | Corpus is large, fresh, or access-controlled | Treating RAG as a fix for poor instructions |
| Fine-tuning | Use only for stable repeated behavior gaps | You have quality data, stable tasks, and eval coverage | Tuning for information that should live in retrieval |
| Model selection | Rank by quality, latency, cost, privacy, and supportability | User constraints are strict or multi-provider fallback is needed | Picking a model from benchmarks alone |
| Migration | Preserve contracts, then replay evals | API surface or reliability requirements changed | Blind prompt copy-paste between providers |
| Rollout | Canary + compare + rollback plan | Production traffic is material or high risk | Single-shot model swaps |

## Known Traps

- escalating to fine-tuning when the real issue is retrieval, tool grounding, or weak output contracts
- migrating providers by copying prompts only and ignoring schema, tool-call, safety, and retry differences
- choosing models from leaderboard screenshots without checking latency, quotas, privacy, or supportability
- shipping fallback models or silent reroutes that produce different behavior with no contract tests
- treating judge-model scores as ground truth instead of one input in a calibrated eval program
- budgeting off introductory/launch pricing without checking the expiry date — providers frequently run time-boxed discounts on a newly released tier (verify the current pricing page for an end date, not just the headline number)
- building or maintaining an integration on a provider's deprecated beta surface (e.g., an API family with a published sunset date) without a migration plan already in motion

## Common Anti-Patterns

- benchmark-first architecture selection
- rollout without a slice-based regression set and rollback trigger
- prompt and model changes shipped together so regressions cannot be attributed
- "cost optimization" that lowers success rate and raises cost per successful task
- provider-specific capabilities hardcoded into durable strategy docs without freshness checks

## Core Principles

### 1. Contracts Before Cleverness

- Define inputs, outputs, schemas, tool boundaries, and refusal behavior before optimizing prompts or models.
- Prefer provider-native structured output and tool contracts when available, with application-side validation as the source of truth.
- Treat prompt text as one part of the contract, not the contract itself.

### 2. Prefer Stable Guidance Over Static Rankings

- Model rankings, pricing, quotas, context limits, and framework momentum are volatile.
- Keep stable decision criteria in the skill; verify current winners with current docs, release notes, and pricing pages.
- When the user asks for "best" or "latest", search current official sources before making a recommendation.

### 3. Reasoning Is Model-Specific

- Do **not** default to prompting for full visible chain-of-thought.
- Prefer internal reasoning with a concise final answer or brief justification.
- Ask for explicit visible steps only when the task is educational, audit-oriented, mathematical, or the user explicitly wants the steps shown.

### 4. Evals Are Release Gates

- Every prompt, model, retrieval, or tool change should be testable against a versioned eval set.
- Judge models and graders are useful, but they are not ground truth; keep a human-calibrated subset.
- Track regressions by slice, not only by a global average.

### 5. Cost Is Per Successful Outcome

- Measure cost per successful task, not just cost per token.
- Budget for retries, failures, tool calls, retrieval, and observability overhead.
- Add routing, caching, and output limits early when economics matter.

## Current-Facts Protocol (Required for Volatile-Fact Questions)

Use this protocol whenever the user asks about current providers, models, frameworks, prices, or regulations.

### Trigger Conditions

- "What is the best model/framework right now?"
- "Is this still current in 2026?"
- "What should I use for structured outputs / RAG / agents / fine-tuning?"
- "Which provider is cheapest / fastest / best for X?"
- "Can I still use this API / framework / model?"

### Verification Steps

1. Confirm user constraints: latency, quality floor, cost ceiling, compliance/privacy, hosting model, toolchain.
2. Check at least **two official or primary sources** from [data/sources.json](data/sources.json).
3. Prefer release notes, pricing pages, API docs, and deprecation pages over blogs or benchmark roundups.
4. Report what is stable vs what is volatile.

### What to Report

- **Stable recommendation criteria**: why a category or approach fits
- **Current platform reality**: API family, supported features, structured output/tooling path, pricing/deprecation caveats
- **Migration risk**: what breaks if the user changes provider/model
- **Fallback option**: second-best path if the preferred option changes

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/prompt_eval_runner.py` | Run a regression JSONL suite (input/expected_substring/expected_schema) and report pass rate. Validates pre-collected outputs — does not call any LLM API. |
| `scripts/cost_estimator.py` | Estimate USD cost across providers from token counts or a prompt file. Provider pricing table embedded; update when rates change. |

## Navigation: Core References

- **[Production Checklists](references/production-checklists.md)** - preflight, rollout, and operational validation
- **[Decision Matrices](references/decision-matrices.md)** - architecture, retrieval, embeddings, frameworks, deployment, MoE vs dense, and distributed training parallelism
- **[Post-Training 2026](references/post-training.md)** - 2026 post-training stack: GRPO, DAPO, GSPO (MoE), RLVR, SimPO, KTO vs PPO/DPO; decision tree and comparison table. Reasoning-model training (RLVR, GRPO, thinking-budget-as-a-dial) and test-time compute scaling are covered here and in [Advanced LLM Patterns](references/advanced-llm-patterns.md); for full alignment/reward-modeling depth see [ai-post-training](../ai-post-training/SKILL.md).
- **[Project Planning Patterns](references/project-planning-patterns.md)** - milestone planning, stack selection, and pipeline design
- **[Model Migration Guide](references/model-migration-guide.md)** - contract-first migration, eval replay, canaries, and rollback
- **[Evaluation Patterns](references/eval-patterns.md)** - offline/online evaluation, lm-eval-harness standard, judge-model calibration, traceability
- **[Cost Economics](references/cost-economics.md)** - TCO, budget guardrails, and ROI framing
- **[Fine-Tuning Recipes](references/fine-tuning-recipes.md)** - SFT, LoRA, mid-training/annealing, over-training regime, and the 2026 post-training stack pointer
- **[Advanced LLM Patterns](references/advanced-llm-patterns.md)** - RLHF loop, pretraining path, test-time compute scaling, and model compression: quantization, pruning, and **knowledge distillation** (teacher soft labels -> student training -> validation). This skill owns the distillation *recipe*; `ai-architecture-advisor` owns the prior decision of whether to distil at all, and `ai-pretraining` explicitly delegates distillation here.
- **[Structured Output Patterns](references/structured-output-patterns.md)** - provider-native schema enforcement and validation fallbacks
- **[Multimodal Patterns](references/multimodal-patterns.md)** - vision/audio/document workflows with explicit freshness caveats
- **[Anti-Patterns](references/anti-patterns.md)** - failure modes to detect early

## Templates

Use templates as starting points, not as drop-in truth for current providers:

- **[Model Selection Matrix](assets/selection/model-selection-matrix.md)** - documented decision record for model/provider choice
- **[Fine-Tuning ROI Calculator](assets/selection/fine-tuning-roi-calculator.md)** - break-even analysis for adaptation investments
- **[Multi-Metric Evaluation](assets/evaluation/template-multi-metric.md)** - release-gate evaluation scaffold
- **[LLM Deployment](assets/deployment/template-llm-deployment.md)** - rollout and monitoring scaffold
- **[Data Quality](assets/data-pipelines/template-data-quality.md)** - dedupe, PII, and quality checks for LLM data pipelines
- **[Basic RAG](assets/rag-pipelines/template-basic-rag.md)** - vendor-neutral baseline retrieval flow
- **[Advanced RAG](assets/rag-pipelines/template-advanced-rag.md)** - hybrid retrieval and reranking
- **[Reasoning Prompt](assets/prompt-engineering/template-cot.md)** - internal-reasoning-first prompt scaffold
- **[ReAct](assets/prompt-engineering/template-react.md)** - tool-using reasoning/action scaffold
- **[Reflection Agent](assets/agentic-workflows/template-reflection.md)** - self-critique workflow
- **[Multi-Agent](assets/agentic-workflows/template-multi-agent.md)** - manager-worker orchestration skeleton

## Shared Utilities (Centralized Patterns)

- [../software-clean-code-standard/references/llm-utilities.md](../software-clean-code-standard/references/llm-utilities.md) - token counting, streaming, cost estimation
- [../software-clean-code-standard/references/error-handling.md](../software-clean-code-standard/references/error-handling.md) - typed errors, correlation IDs, problem details
- [../software-clean-code-standard/references/resilience-utilities.md](../software-clean-code-standard/references/resilience-utilities.md) - retries, circuit breakers, backoff
- [../software-clean-code-standard/references/logging-utilities.md](../software-clean-code-standard/references/logging-utilities.md) - structured logs and trace correlation
- [../software-clean-code-standard/references/observability-utilities.md](../software-clean-code-standard/references/observability-utilities.md) - telemetry and dashboards
- [../software-clean-code-standard/references/config-validation.md](../software-clean-code-standard/references/config-validation.md) - schema validation and secrets handling
- [../software-clean-code-standard/references/testing-utilities.md](../software-clean-code-standard/references/testing-utilities.md) - fixtures, mocking, and test harness patterns
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) - canonical clean-code rule IDs

## External Sources

See **[data/sources.json](data/sources.json)** for curated primary sources across:

- Official provider docs, pricing, and API guides
- Model adaptation and training references
- Retrieval and agent frameworks
- Evaluation and observability tooling
- Security, governance, and protocol standards

## Fact-Checking Rule

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify volatile external facts before final answers.
- Prefer official docs, standards, release notes, and pricing pages.
- If you cannot verify, say so explicitly and present the guidance as a dated assumption instead of a fact.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

