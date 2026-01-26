---
name: ai-prompt-engineering
description: "Operational prompt engineering for production LLM apps: structured outputs (JSON/schema), deterministic extractors, RAG grounding/citations, tool/agent workflows, prompt safety (injection/exfiltration), and prompt evaluation/regression testing. Use when designing, debugging, or standardizing prompts for Codex CLI, Claude Code, and OpenAI/Anthropic/Gemini APIs."
---

# Prompt Engineering — Operational Skill

**Modern Best Practices (January 2026)**: versioned prompts, explicit output contracts, regression tests, and safety threat modeling for tool/RAG prompts (OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/).

This skill provides **operational guidance** for building production-ready prompts across standard tasks, RAG workflows, agent orchestration, structured outputs, hidden reasoning, and multi-step planning.

All content is **operational**, not theoretical. Focus on patterns, checklists, and copy-paste templates.

## Quick Start (60 seconds)

1. Pick a pattern from the decision tree (structured output, extractor, RAG, tools/agent, rewrite, classification).
2. Start from a template in `assets/` and fill in `TASK`, `INPUT`, `RULES`, and `OUTPUT FORMAT`.
3. Add guardrails: instruction/data separation, “no invented details”, missing → `null`/explicit missing.
4. Add validation: JSON parse check, schema check, citations check, post-tool checks.
5. Add evals: 10–20 cases while iterating, 50–200 before release, plus adversarial injection cases.

## Model Notes (2026)

This skill includes Claude Code + Codex CLI optimizations:

- **Action directives**: Frame for implementation, not suggestions
- **Parallel tool execution**: Independent tool calls can run simultaneously
- **Long-horizon task management**: State tracking, incremental progress, context compaction resilience
- **Positive framing**: Describe desired behavior rather than prohibitions
- **Style matching**: Prompt formatting influences output style
- **Domain-specific patterns**: Specialized guidance for frontend, research, and agentic coding
- **Style-adversarial resilience**: Stress-test refusals with poetic/role-play rewrites; normalize or decline stylized harmful asks before tool use

Prefer “brief justification” over requesting chain-of-thought. When using private reasoning patterns, instruct: think internally; output only the final answer.

## Quick Reference

| Task | Pattern to Use | Key Components | When to Use |
|------|----------------|----------------|-------------|
| **Machine-parseable output** | Structured Output | JSON schema, "JSON-only" directive, no prose | API integrations, data extraction |
| **Field extraction** | Deterministic Extractor | Exact schema, missing->null, no transformations | Form data, invoice parsing |
| **Use retrieved context** | RAG Workflow | Context relevance check, chunk citations, explicit missing info | Knowledge bases, documentation search |
| **Internal reasoning** | Hidden Chain-of-Thought | Internal reasoning, final answer only | Classification, complex decisions |
| **Tool-using agent** | Tool/Agent Planner | Plan-then-act, one tool per turn | Multi-step workflows, API calls |
| **Text transformation** | Rewrite + Constrain | Style rules, meaning preservation, format spec | Content adaptation, summarization |
| **Classification** | Decision Tree | Ordered branches, mutually exclusive, JSON result | Routing, categorization, triage |

---

## Decision Tree: Choosing the Right Pattern

```text
User needs: [Prompt Type]
  |-- Output must be machine-readable?
  |     |-- Extract specific fields only? -> **Deterministic Extractor Pattern**
  |     `-- Generate structured data? -> **Structured Output Pattern (JSON)**
  |
  |-- Use external knowledge?
  |     `-- Retrieved context must be cited? -> **RAG Workflow Pattern**
  |
  |-- Requires reasoning but hide process?
  |     `-- Classification or decision task? -> **Hidden Chain-of-Thought Pattern**
  |
  |-- Needs to call external tools/APIs?
  |     `-- Multi-step workflow? -> **Tool/Agent Planner Pattern**
  |
  |-- Transform existing text?
  |     `-- Style/format constraints? -> **Rewrite + Constrain Pattern**
  |
  `-- Classify or route to categories?
        `-- Mutually exclusive rules? -> **Decision Tree Pattern**
```

---

## Copy/Paste: Minimal Prompt Skeletons

### 1) Generic "output contract" skeleton

```text
TASK:
{{one_sentence_task}}

INPUT:
{{input_data}}

RULES:
- Follow TASK exactly.
- Use only INPUT (and tool outputs if tools are allowed).
- No invented details. Missing required info -> say what is missing.
- Keep reasoning hidden.
- Follow OUTPUT FORMAT exactly.

OUTPUT FORMAT:
{{schema_or_format_spec}}
```

### 2) Tool/agent skeleton (deterministic)

```text
AVAILABLE TOOLS:
{{tool_signatures_or_names}}

WORKFLOW:
- Make a short plan.
- Call tools only when required to complete the task.
- Validate tool outputs before using them.
- If the environment supports parallel tool calls, run independent calls in parallel.
```

### 3) RAG skeleton (grounded)

```text
RETRIEVED CONTEXT:
{{chunks_with_ids}}

RULES:
- Use only retrieved context for factual claims.
- Cite chunk ids for each claim.
- If evidence is missing, say what is missing.
```

---

## Operational Checklists

Use these references when validating or debugging prompts:

- `frameworks/shared-skills/skills/ai-prompt-engineering/references/quality-checklists.md`
- `frameworks/shared-skills/skills/ai-prompt-engineering/references/production-guidelines.md`

## Context Engineering (2026)

True expertise in prompting extends beyond writing instructions to shaping the entire context in which the model operates. Context engineering encompasses:

- **Conversation history**: What prior turns inform the current response
- **Retrieved context (RAG)**: External knowledge injected into the prompt
- **Structured inputs**: JSON schemas, system/user message separation
- **Tool outputs**: Results from previous tool calls that shape next steps

### Context Engineering vs Prompt Engineering

| Aspect | Prompt Engineering | Context Engineering |
|--------|-------------------|---------------------|
| Focus | Instruction text | Full input pipeline |
| Scope | Single prompt | RAG + history + tools |
| Optimization | Word choice, structure | Information architecture |
| Goal | Clear instructions | Optimal context window |

### Key Context Engineering Patterns

**1. Context Prioritization**: Place most relevant information first; models attend more strongly to early context.

**2. Context Compression**: Summarize history, truncate tool outputs, select most relevant RAG chunks.

**3. Context Separation**: Use clear delimiters (`<system>`, `<user>`, `<context>`) to separate instruction types.

**4. Dynamic Context**: Adjust context based on task complexity - simple tasks need less context, complex tasks need more.

---

## Core Concepts vs Implementation Practices

### Core Concepts (Vendor-Agnostic)

- **Prompt contract**: inputs, allowed tools, output schema, max tokens, and refusal rules.
- **Context engineering**: conversation history, RAG context, tool outputs, and structured inputs shape model behavior.
- **Determinism controls**: temperature/top_p, constrained decoding/structured outputs, and strict formatting.
- **Cost & latency budgets**: prompt length and max output drive tokens and tail latency; enforce hard limits and measure p95/p99.
- **Evaluation**: golden sets + regression gates + A/B + post-deploy monitoring.
- **Security**: prompt injection, data exfiltration, and tool misuse are primary threats (OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/).

### Implementation Practices (Model/Platform-Specific)

- Use model-specific structured output features when available; keep a schema validator as the source of truth.
- Align tracing/metrics with OpenTelemetry GenAI semantic conventions (https://opentelemetry.io/docs/specs/semconv/gen-ai/).

## Do / Avoid

**Do**
- Do keep prompts small and modular; centralize shared fragments (policies, schemas, style).
- Do add a prompt eval harness and block merges on regressions.
- Do prefer "brief justification" over requesting chain-of-thought; treat hidden reasoning as model-internal.

**Avoid**
- Avoid prompt sprawl (many near-duplicates with no owner or tests).
- Avoid brittle multi-step chains without intermediate validation.
- Avoid mixing policy and product copy in the same prompt (harder to audit and update).

## Navigation: Core Patterns

- **[Core Patterns](references/core-patterns.md)** - 7 production-grade prompt patterns
  - Structured Output (JSON), Deterministic Extractor, RAG Workflow
  - Hidden Chain-of-Thought, Tool/Agent Planner, Rewrite + Constrain, Decision Tree
  - Each pattern includes structure template and validation checklist

## Navigation: Best Practices

- **[Best Practices (Core)](references/best-practices-core.md)** - Foundation rules for production-grade prompts
  - System instruction design, output contract specification, action directives
  - Context handling, error recovery, positive framing, style matching, style-adversarial red teaming
  - Anti-patterns, Claude 4+ specific optimizations

- **[Production Guidelines](references/production-guidelines.md)** - Deployment and operational guidance
  - Evaluation & testing (Prompt CI/CD), model parameters, few-shot selection
  - Safety & guardrails, conversation memory, context compaction resilience
  - Answer engineering, decomposition, multilingual/multimodal, benchmarking
  - **CI/CD Tools** (2026): Promptfoo, DeepEval integration patterns
  - **Security** (2026): PromptGuard 4-layer defense, Microsoft Prompt Shields, taint tracking

- **[Quality Checklists](references/quality-checklists.md)** - Validation checklists before deployment
  - Prompt QA, JSON validation, agent workflow checks
  - RAG workflow, safety & security, performance optimization
  - Testing coverage, anti-patterns, quality score rubric

- **[Domain-Specific Patterns](references/domain-specific-patterns.md)** - Claude 4+ optimized patterns for specialized domains
  - Frontend/visual code: Creativity encouragement, design variations, micro-interactions
  - Research tasks: Success criteria, verification, hypothesis tracking
  - Agentic coding: No speculation rule, principled implementation, investigation patterns
  - Cross-domain best practices and quality modifiers

## Navigation: Specialized Patterns

- **[RAG Patterns](references/rag-patterns.md)** - Retrieval-augmented generation workflows
  - Context grounding, chunk citation, missing information handling

- **[Agent and Tool Patterns](references/agent-patterns.md)** - Tool use and agent orchestration
  - Plan-then-act workflows, tool calling, multi-step reasoning, generate-verify-revise chains
  - **Multi-Agent Orchestration** (2026): centralized, handoff, federated patterns; plan-and-execute (90% cost reduction)

- **[Extraction Patterns](references/extraction-patterns.md)** - Deterministic field extraction
  - Schema-based extraction, null handling, no hallucinations

- **[Reasoning Patterns (Hidden CoT)](references/reasoning-patterns.md)** - Internal reasoning without visible output
  - Hidden reasoning, final answer only, classification workflows
  - **Extended Thinking API** (Claude 4+): budget management, think tool, multishot patterns

- **[Additional Patterns](references/additional-patterns.md)** - Extended prompt engineering techniques
  - Advanced patterns, edge cases, optimization strategies

---

## Navigation: Templates

Templates are copy-paste ready and organized by complexity:

### Quick Templates

- **[Quick Template](assets/quick/template-quick.md)** - Fast, minimal prompt structure

### Standard Templates

- **[Standard Template](assets/standard/template-standard.md)** - Production-grade operational prompt
- **[Agent Template](assets/standard/template-agent.md)** - Tool-using agent with planning
- **[RAG Template](assets/standard/template-rag.md)** - Retrieval-augmented generation
- **[Chain-of-Thought Template](assets/standard/template-cot.md)** - Hidden reasoning pattern
- **[JSON Extractor Template](assets/standard/template-json-extractor.md)** - Deterministic field extraction
- **[Prompt Evaluation Template](assets/eval/prompt-eval-template.md)** - Regression tests, A/B testing, rollout gates

---

## External Resources

External references are listed in [data/sources.json](data/sources.json):

- Official documentation (OpenAI, Anthropic, Google)
- LLM frameworks (LangChain, LlamaIndex)
- Vector databases (Pinecone, Weaviate, FAISS)
- Evaluation tools (OpenAI Evals, HELM)
- Safety guides and standards
- RAG and retrieval resources

---

## Freshness Rule (2026)

When asked for “latest” prompting recommendations, prefer provider docs and standards from `data/sources.json`. If web search is unavailable, state the constraint and avoid overconfident “current best” claims.

---

## Related Skills

This skill provides foundational prompt engineering patterns. For specialized implementations:

**AI/LLM Skills**:

- [AI Agents Development](../ai-agents/SKILL.md) - Production agent patterns, MCP integration, orchestration
- [AI LLM Engineering](../ai-llm/SKILL.md) - LLM application architecture and deployment
- [AI LLM RAG Engineering](../ai-rag/SKILL.md) - Advanced RAG pipelines and chunking strategies
- [AI LLM Search & Retrieval](../ai-rag/SKILL.md) - Search optimization, hybrid retrieval, reranking
- [AI LLM Development](../ai-llm/SKILL.md) - Fine-tuning, evaluation, dataset creation

**Software Development Skills**:

- [Software Architecture Design](../software-architecture-design/SKILL.md) - System design patterns
- [Software Backend](../software-backend/SKILL.md) - Backend implementation
- [Foundation API Design](../dev-api-design/SKILL.md) - API design and contracts

---

## Usage Notes

**For Claude Code**:

- Reference this skill when building prompts for agents, commands, or integrations
- Use Quick Reference table for fast pattern lookup
- Follow Decision Tree to select appropriate pattern
- Validate outputs with Quality Checklists before deployment
- Use templates as starting points, customize for specific use cases

**For Codex CLI**:

- Use the same patterns and templates; adapt tool-use wording to the local tool interface
- For long-horizon tasks, track progress explicitly (a step list/plan) and update it as work completes
- Run independent reads/searches in parallel when the environment supports it; keep writes/edits serialized
- **AGENTS.md Integration**: Place project-specific prompt guidance in AGENTS.md files at global (~/.codex/AGENTS.md), project-level (./AGENTS.md), or subdirectory scope for layered instructions
- **Reasoning Effort**: Use `medium` for interactive coding (default), `high`/`xhigh` for complex autonomous multi-hour tasks
