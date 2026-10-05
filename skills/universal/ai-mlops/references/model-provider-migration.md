# Model and Provider Migration

How to move an LLM-backed system to a different model, model version, provider, or API surface
without breaking its product contracts. Rollout mechanics (shadow, canary, rollback) are in
[deployment-lifecycle.md](deployment-lifecycle.md) and
[online-evaluation-patterns.md](online-evaluation-patterns.md); this file covers what is
specific to a model or provider swap.

Model rankings, prices, context limits, feature parity, and deprecation dates change often.
Read the current provider docs, model cards, and deprecation pages before planning a migration;
do not plan from remembered values.

## Table of Contents

- [Principles](#principles)
- [Decision Tree: Risk by Migration Reason](#decision-tree-risk-by-migration-reason)
- [Inventory Before You Start](#inventory-before-you-start)
- [API Surface Comparison](#api-surface-comparison)
- [Contract and Prompt Adaptation](#contract-and-prompt-adaptation)
- [Evaluation and Rollout](#evaluation-and-rollout)
- [Anti-Patterns](#anti-patterns)
- [Checklist](#checklist)

## Principles

1. **Migrate contracts, not prompt wording.** Preserve output schema, tool-call expectations,
   safety rules, latency budgets, and audit requirements before optimizing wording.
2. **Replay evals before touching production traffic.** A migration with no replayable eval
   suite is a risk event, not an upgrade.
3. **Assume provider-native behavior differs.** Structured output, tool calling, retries,
   streaming, and multimodal parsing behave differently even when the APIs look alike.
4. **Keep the old path warm.** Keep dual-run or canary capability until the new path has
   survived real traffic.
5. **Treat a provider sunset as a deadline.** When the inventory finds an integration on a
   deprecated API or model, schedule the migration against the provider's published shutdown
   date; it is not backlog.
6. **Your contract must hold for every model that can answer.** Some providers route a share of
   requests to a different model (for example a safety fallback) or change the model behind an
   alias. Check the provider docs for routing and alias behavior, and test the contract against
   each model that can serve the request.

## Decision Tree: Risk by Migration Reason

```text
Why migrate?
├─ Cost reduction
│   ├─ Same provider, smaller tier            -> lowest risk
│   ├─ Different provider, similar features   -> medium risk
│   └─ Open-weight / self-hosted              -> high operational risk (you now own serving)
├─ Quality improvement
│   ├─ Same provider, higher tier             -> low-to-medium risk
│   ├─ Different provider, better task fit    -> medium risk
│   └─ Adapted / fine-tuned model             -> high eval burden
├─ Feature requirement (structured output, tools, multimodal, MCP/tool interop)
│   └─ Compare native contract support first, then preprocessing and billing model
└─ Vendor diversification
    ├─ Add a fallback provider                -> abstraction layer + contract tests
    └─ Replace the primary provider           -> full workflow below

Replayable evals and a rollback path in place?  No -> build them first.  Yes -> continue.
```

For the self-hosted vs API cost breakeven, use
[ops-cost-optimization](../../ops-cost-optimization/SKILL.md).

## Inventory Before You Start

Record, and document anything that is undocumented, before changing anything:

- Current model, provider, API family, SDK version, and auth path
- System instructions and any provider-specific formatting assumptions
- Output schema, parser, validator, and every downstream consumer
- Tool definitions, tool-choice behavior, retry policy, and timeouts
- Multimodal inputs, file limits, and the preprocessing pipeline
- SLOs: latency p50/p95/p99, error budget, cost ceiling
- Safety controls: refusal behavior, moderation, policy enforcement, human-review gates
- Dashboards and alerts tied to the current path

## API Surface Comparison

Use as a checklist, not a feature ranking.

| Area | Compare | Why it breaks migrations |
|---|---|---|
| Core API family | Request/response object shape | Objects differ materially between providers |
| Structured output | Native schema enforcement vs best-effort JSON; supported schema keywords and limits | Downstream parsers fail silently |
| Tool calling | Declaration shape, parallel calls, forced calls, compatibility with reasoning modes | Agents break when call semantics differ |
| Streaming | Event types, ordering, partial output, tool events | Clients assume one provider's event model |
| Multimodal input | Ingestion paths and billing model | Cost and correctness shift unexpectedly |
| Context handling | Window, truncation behavior, cache semantics and minimum cacheable length | Long prompts degrade or fail differently |
| Safety | Refusal style, block behavior, moderation path | Policy changes look like quality regressions |
| Rate limits and quotas | Burst, concurrency, retry headers | Throughput assumptions stop holding |

Gateways and "compatible" endpoints: verify every compatibility claim with your own contract
tests, not the vendor's page.

## Contract and Prompt Adaptation

1. **Hold the contract fixed first:** output schema and validation rules; required fields,
   enums, and null handling; allowed tools and tool-choice behavior; refusal and fallback
   behavior; citation or grounding requirements.
2. **Remove provider-specific folklore:** delimiters or wrappers used for one provider only;
   "show your reasoning" instructions that compensated for an older model; JSON-only hacks when
   the target enforces schemas natively; token budgets tied to an old context window.
3. **Isolate the provider-specific layer** behind adapters for request building, tool
   declaration and execution, structured-output parsing, streaming events, and error mapping
   and retries.
4. **Order of work:** keep task intent and contract → strip old-provider workarounds → adopt the
   target's native structured-output or tool features → re-run evals → only then tune wording
   for quality or cost.

## Evaluation and Rollout

**Eval slices** (size each so a regression at your rollback threshold is detectable; see
[ai-evals](../../ai-evals/SKILL.md) for sample sizing): golden set of core behavior, edge
cases, adversarial and tool-abuse cases, structured-output cases, tool-use cases.

**Measure on old and new paths:** task success rate, structured-output success rate, tool-call
correctness, latency p50/p95/p99, cost per *successful* outcome (retries, tool calls, and
observability included, not token price alone), safety regressions, and a human-calibrated
quality score for subjective tasks.

**Rollout sequence:** offline replay of the full suite on both paths → shadow or dual run →
canary on a bounded slice with aggressive rollback criteria → staged promotion while metrics
stay inside thresholds → primary cutover, with the old path and rollback artifacts kept until
stability is proven.

**Rollback triggers** (set the thresholds before the canary):

- Structured-output failures above threshold
- Tool-call regressions or invalid tool arguments
- Any safety regression of a severity you do not accept
- Latency or cost budget breach
- Unexplained drop in user or human-review quality

## Anti-Patterns

- **Blind prompt porting** — copying prompts across providers without revalidating contracts
- **Benchmark-first decisions** — switching on public scores without replaying your workload
- **No rollback** — removing the old path before the new one survives canary traffic
- **Mixed migrations** — changing provider, prompt, parser, and tool contract in one release
- **Schema drift** — letting the downstream schema change silently during the swap
- **Token-price-only costing** — ignoring retries, tool calls, and observability cost

## Checklist

- [ ] Current behavior inventoried and documented
- [ ] Target capabilities, limits, and deprecation schedule checked in current provider docs
- [ ] Contract tests for schema, tools, and streaming
- [ ] Eval suite replayed on old and new paths
- [ ] Contract tested against every model the provider can route the request to
- [ ] Canary and rollback criteria written down before the canary
- [ ] Dashboards compare old and new paths side by side
- [ ] Rollback artifacts kept until post-cutover stability is proven
