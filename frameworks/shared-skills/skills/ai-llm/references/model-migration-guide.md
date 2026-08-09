# Model Migration Guide

> Operational reference for migrating between LLM providers, model families, and API surfaces without breaking product contracts.

**Freshness anchor:** Treat model rankings, pricing, context limits, and feature parity as volatile. Verify current provider docs before executing a migration plan.

## Table of Contents

- [Migration Principles](#migration-principles)
- [Decision Tree](#decision-tree)
- [What to Inventory First](#what-to-inventory-first)
- [API Surface Comparison](#api-surface-comparison)
- [Prompt and Contract Adaptation](#prompt-and-contract-adaptation)
- [Evaluation and Rollout](#evaluation-and-rollout)
- [Migration Anti-Patterns](#migration-anti-patterns)

---

## Migration Principles

1. **Migrate contracts, not vibes.**
   Preserve output schema, tool-call expectations, safety rules, latency budgets, and audit requirements before optimizing prompt wording.
2. **Replay evals before touching production traffic.**
   A migration without a replayable eval suite is a risk event, not an upgrade.
3. **Assume provider-native behavior differs.**
   Structured outputs, tool calling, retries, streaming, and multimodal parsing often behave differently even when APIs look similar.
4. **Keep a rollback path warm.**
   Maintain dual-run or canary capability until the new path has passed real traffic checks.

---

## Decision Tree

```text
Considering model or provider migration
│
├── Why are you migrating?
│   ├── Cost reduction
│   │   ├── Same provider, smaller tier -> lowest risk
│   │   ├── Different provider, similar feature set -> medium risk
│   │   └── Open-weight / self-hosted -> high operational risk
│   │
│   ├── Quality improvement
│   │   ├── Same provider, higher tier -> low-to-medium risk
│   │   ├── Different provider, better task fit -> medium risk
│   │   └── Adapted/fine-tuned model -> high eval burden
│   │
│   ├── Feature requirement
│   │   ├── Better structured outputs / tools -> compare native contract support
│   │   ├── Better multimodal support -> compare preprocessing + billing model
│   │   └── Better agent/tool interoperability -> compare MCP/tool surfaces
│   │
│   └── Vendor diversification
│       ├── Add fallback provider -> abstraction layer + contract tests
│       └── Replace primary provider -> full migration workflow
│
└── Do you have replayable evals and rollback?
    ├── No -> build them first
    └── Yes -> continue
```

---

## What to Inventory First

Before migrating anything, record:

- Current model/provider, API family, SDK version, and auth path
- Prompt/system instructions and any provider-specific formatting assumptions
- Output schema, parser, validator, and downstream consumers
- Tool definitions, tool-choice behavior, retry policy, and timeout rules
- Multimodal inputs, file limits, and preprocessing pipeline
- Online SLOs: latency p50/p95/p99, error budget, cost ceiling
- Safety controls: refusals, moderation, policy enforcement, human-review gates
- Monitoring and dashboards tied to the current path

If any of the above are undocumented, document them before the migration begins.

---

## API Surface Comparison

Use this as a checklist, not as a static feature ranking table.

| Area | What to Compare | Why It Breaks Migrations |
|------|------------------|--------------------------|
| Core API family | Responses / messages / generate-content style surface | Request and response objects differ materially |
| Structured output | Native schema enforcement vs best-effort JSON | Downstream parsers may silently fail |
| Tool calling | Tool declaration shape, parallel calls, call forcing, retries | Agents break when call semantics differ |
| Streaming | Event types, ordering, partial outputs, tool events | Streaming clients often assume one provider's event model |
| Multimodal input | Image/audio/document ingestion and billing model | Cost and correctness can shift unexpectedly |
| Context handling | Context window policy, truncation behavior, cache semantics | Long prompts may degrade or fail differently |
| Safety | Refusal style, block behavior, moderation path | Policy behavior changes can look like regressions |
| Rate limits and quotas | Burst behavior, concurrency, retry headers | Throughput assumptions stop holding |

### Modern Provider Pattern (July 2026)

- **OpenAI-style stacks**: compare current Responses API behavior, tool surfaces, graders, and model-optimization paths. **The Assistants API (beta) is deprecated and sunsets 2026-08-26** — all `/v1/assistants`, `/v1/threads`, and related endpoints stop working that day with no extension. Any migration inventory that finds a live Assistants API integration must treat the Responses API + Conversations API migration as a hard deadline, not a backlog item.
- **Anthropic-style stacks**: compare Messages/tool-use behavior, prompt-caching semantics, and eval guidance. Anthropic's flagship tier now has two components: **Claude Fable 5** (GA since 2026-06-09, `claude-fable-5`, $10/$50 per MTok, 1M context, 128k output) with a safety-classifier fallback that routes <5% of high-risk sessions to **Claude Opus 4.8**; and **Claude Mythos 5** (research/Project Glasswing access only). Plan SLAs and migration contracts to hold across both Fable 5 and Opus 4.8 behaviors — a response contract that assumes Fable 5 only will be violated for sessions hitting the safety classifier. **Claude Opus 4.8** ($5/$25 per MTok) is the standalone flagship-tier model. **Claude Sonnet 5** (GA 2026-06-30, `claude-sonnet-5`) replaced Sonnet 4.6 as the current speed/intelligence-balance tier and carries time-boxed introductory pricing through 2026-08-31 — Sonnet 4.6 is now a legacy model, still served but not the migration target for new work.
- **Gemini-style stacks**: compare schema support, function calling, multimodal surfaces, and long-context behavior. Gemini 3.1 Pro and Gemini 3.5 Flash are Google's current frontier and speed tiers — verify exact context-window figures at ai.google.dev, since these have changed release to release.
- **Gateway/self-hosted stacks**: compare compatibility claims against actual contract tests, not marketing pages.

---

## Prompt and Contract Adaptation

### Rule 1: Preserve the Contract First

Keep these stable before you optimize prompt wording:

- Output schema and validation rules
- Required fields, enums, and null/missing behavior
- Allowed tools and tool-choice behavior
- Refusal and fallback behavior
- Citation or grounding requirements

### Rule 2: Remove Provider-Specific Prompt Folklore

Do not blindly copy:

- XML wrappers or special delimiters used only for one provider
- "Show your reasoning" directives that were compensating for an older model
- JSON-only hacks when the target provider has native schema enforcement
- Token-budget assumptions tied to an older context window

### Rule 3: Rebuild the Smallest Provider-Specific Layer

Isolate provider-specific logic behind adapters for:

- Request building
- Tool declaration and execution
- Structured-output parsing
- Streaming event handling
- Error mapping and retries

### Recommended Prompt Strategy

1. Start with the existing task intent and output contract.
2. Remove instructions that exist only to work around the old provider.
3. Add the target provider's native structured-output or tool features where appropriate.
4. Re-run evals.
5. Only then optimize wording for quality or cost.

---

## Evaluation and Rollout

### Minimum Eval Sets

| Eval Slice | Minimum | Purpose |
|------------|---------|---------|
| Golden set | 50-100 cases | Verify core behavior |
| Edge cases | 20-50 cases | Capture boundary failures |
| Adversarial cases | 20-30 cases | Check prompt/tool abuse and safety regressions |
| Structured-output cases | 25+ cases | Validate schema and parsing reliability |
| Tool-use cases | 25+ cases | Validate function/tool contracts |

### What to Measure

- Task success rate
- Structured-output success rate
- Tool-call correctness
- Latency p50/p95/p99
- Cost per successful outcome
- Safety regressions
- Human-calibrated quality score for subjective tasks

### Rollout Sequence

1. **Offline replay**
   Run the full eval suite against old and new paths.
2. **Shadow or dual run**
   Compare outputs without affecting users.
3. **Canary release**
   Start with a bounded traffic slice and aggressive rollback criteria.
4. **Staged promotion**
   Increase traffic only after metrics remain inside thresholds.
5. **Primary cutover**
   Keep rollback artifacts and the previous path ready until stability is proven.

### Rollback Triggers

- Structured-output failures above threshold
- Tool-call regression or invalid tool arguments
- Safety regression of any severity you do not accept
- Latency or cost budget breach
- Unexplained drop in user or human-review quality

---

## Migration Anti-Patterns

- **Blind prompt porting**: copying prompts between providers without revalidating contracts
- **Benchmark-first decisions**: switching models from public scores without replaying your own workload
- **No rollback**: removing the old path before the new one has survived canary traffic
- **Mixed migrations**: changing provider, prompt, parser, and tool contract in one release
- **Schema drift**: letting the downstream schema evolve silently during a provider swap
- **Unpriced migrations**: treating token prices as the only cost and ignoring retries, tools, and observability

---

## Practical Checklist

- [ ] Current behavior documented
- [ ] Target provider capabilities verified in current official docs
- [ ] Contract tests written for schema, tools, and streaming
- [ ] Eval suite replayed on old and new paths
- [ ] Canary and rollback criteria documented
- [ ] Metrics and dashboards compare old vs new paths directly
- [ ] Rollback artifacts retained until post-cutover stability is proven
