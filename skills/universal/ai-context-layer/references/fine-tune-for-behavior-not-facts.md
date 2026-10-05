# Fine-Tune for Behavior, Not Facts

The single most useful rule for fine-tuning: **fine-tune for form, not for facts.** Teams keep violating it and shipping stale models.

This file is the context-layer perspective on fine-tuning — *what fine-tuning does for the context brain*, not *how to fine-tune* (that lives in `ai-llm/references/fine-tuning-recipes.md`). Read both.

---

## Table of Contents

- [The rule](#the-rule)
- [What fine-tune does well](#what-fine-tune-does-well)
- [What fine-tune does badly](#what-fine-tune-does-badly)
- [Architecture](#architecture)
- [Decision table](#decision-table)
- [Patterns](#patterns)
- [Anti-patterns](#anti-patterns)
- [Composition](#composition)
- [Related](#related)

---

## The rule

**Behavior:** persona, tone, output format, refusal style, structured-output shape, domain vocabulary preferences, response framing, JSON schema adherence, language register. These are *form*. Fine-tune learns them well, retains them across queries, and removes the need to re-specify every prompt.

**Facts:** what your refund policy says, your current pricing, the new API endpoint shipped yesterday, who the on-call engineer is. These are *facts*. They change. Fine-tune locks them in weights the moment training stops. The model becomes stale the day after training and gets worse over time without anyone noticing.

The corollary: **never fine-tune to inject facts.** Facts go in retrieval (RAG, H1–H7) or preload (CAG / long-context, I1–I2). Behavior is what fine-tune is for.

---

## What fine-tune does well

- **Consistent persona/voice.** Customer support tone, brand voice, technical-writing style. Reliably reproduced without re-specifying in every prompt.
- **Structured output adherence.** JSON schema, function-call signatures, deterministic format under pressure. Fine-tuned models recover from format drift faster than prompted ones.
- **Refusal patterns.** Domain-specific refusals (compliance language, safety responses) without re-prompting.
- **Domain vocabulary calibration.** Preferring "client" over "customer", "incident" over "issue" — the small token-level preferences a prompt can teach but won't reinforce reliably across long conversations.
- **Compression of long system prompts.** A 3000-token system prompt repeated every turn can sometimes be compressed into the fine-tuned base, saving cost and freeing context room for facts.

When done for these reasons, fine-tune is permanent value — it doesn't decay as long as the base model is stable.

---

## What fine-tune does badly

- **Current facts.** Stale the moment training ends. The pricing page you trained on last quarter is wrong now.
- **Anything that changes weekly or faster.** Re-training cadence cannot keep up.
- **Specific entity knowledge** (your customers, your products by SKU, your team members). Use retrieval or preload.
- **Schema you're still iterating on.** Fine-tune locks the schema. If the schema is still moving, you'll re-train constantly.
- **"Teaching the model your domain."** This is almost always a mistake. What teams mean by "domain knowledge" is usually facts (use RAG) or vocabulary (use a system prompt or short fine-tune).

If you find yourself fine-tuning more than ~quarterly, you are probably fine-tuning facts. Reconsider.

---

## Architecture

```text
                ┌──────────────────────────────────┐
                │  Fine-tuned base model           │
                │  - persona                       │
                │  - output schema                 │
                │  - refusal style                 │
                │  - domain vocabulary             │
                │  re-train: quarterly             │
                └────────────────┬─────────────────┘
                                 │
                  facts / context layer ↓
                                 │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
   Preload (CAG / LC)     Retrieve (RAG)       Session memory
   stable evergreen       volatile facts       per-user state
   (handbook, glossary)   (current pricing,    (preferences,
                          recent tickets)       history)
```

The fine-tuned layer is the **bottom of the stack** — every query sees it. The context layer above (preload + retrieve + session memory) is the part that changes per query. The bottom is stable; the top is fresh.

---

## Decision table

| Decision | Default | Upgrade when |
|---|---|---|
| Fine-tune method | LoRA / PEFT for cost; SFT on small task data | Full SFT when you have ≥10K high-quality task examples and persistent value |
| Base model selection | Latest stable in your provider family | Consider lifecycle — fine-tuning a model that's deprecated in 6 months is wasted |
| Training data | Behavior examples (input/output pairs that demonstrate desired form) | Never include facts you don't want to inject |
| Re-train cadence | Quarterly, or when base model updates | Monthly only if behavior drift is measurable |
| Eval set | Form-focused: schema adherence, persona consistency, refusal correctness | Facts-correctness eval belongs in RAG/CAG eval, not here |
| Refusal data | Include 5–15% refusal examples | Always include or model learns to over-comply |
| Composition | Fine-tune base + RAG layer + CAG layer (RA-CB-1) | Hybrid is the default in production; rare to fine-tune alone |
| Cost ceiling | Training cost + eval cost + re-train cadence × N years | If it doesn't justify ≥2 years of value, use prompt engineering |
| Inference path | Through provider's fine-tune deployment | Self-host only if compliance demands it (see `ai-local-model-ops`) |

---

## Patterns

### P-FT-1 — Form-only training data

Every training example demonstrates *how* to answer, not *what* the answer is. If you can substitute the entity (company, product, person) for another and the example still teaches the same behavior, it's form. If substituting breaks the lesson, it's facts — don't fine-tune it.

### P-FT-2 — Refusal calibration

Include refusal examples explicitly: out-of-scope queries, harmful requests, queries that should escalate. Without these, fine-tuning reduces refusal rates (model becomes "more helpful" in the wrong direction).

### P-FT-3 — Schema adherence training

For structured-output use cases (JSON, function calls, fixed templates), 50–500 schema-adherent examples sharply reduce format drift compared to prompting alone. This is the highest-ROI fine-tune use case for production agents.

### P-FT-4 — Persona pinning over long conversations

System prompts decay over long conversations (model forgets the persona). Fine-tuning the persona into weights makes it persistent without re-specifying. Especially valuable for voice bots and long support sessions.

### P-FT-5 — Composed with CAG for stable corpora

Fine-tune for persona + CAG for handbook = the "ChatGPT-with-our-policies" pattern. CAG carries the corpus; fine-tune carries the voice. Together they obviate most RAG systems for small-corpus support bots.

### P-FT-6 — Re-train economics check

Before any fine-tune project, compute: training cost + eval cost + re-train cadence × years of expected use vs equivalent prompt-engineering effort. If the math doesn't show ≥3× value over prompting, don't fine-tune. The base model will get better and erode your edge.

---

## Anti-patterns

- **A-FT-1 — Fine-tune to "teach the domain".** Almost always means fine-tuning facts. Stale-by-default. Use RAG/CAG.
- **A-FT-2 — Fine-tune to fix one prompt failure.** Prompt engineering is cheaper, faster, and reversible. Try it first.
- **A-FT-3 — Fine-tune without an eval set.** Without form-focused eval (schema adherence, persona consistency, refusal correctness), you can't tell if training helped or hurt.
- **A-FT-4 — Fine-tune on the latest model, ignore lifecycle.** Provider deprecates the base in 9 months; you re-train or migrate. Plan the lifecycle before training.
- **A-FT-5 — Training data that mixes form and facts.** Examples that demonstrate behavior *and* contain specific facts inject both. Strip facts from training data; substitute placeholders.
- **A-FT-6 — Fine-tune alone, no retrieval/preload layer.** Stale-facts trap. Production answer is always composition (RA-CB-1).
- **A-FT-7 — Skipping refusal examples.** Fine-tuning without refusal data erodes safety calibration. Include them deliberately.

---

## Composition

Fine-tune is one layer of [RA-CB-1 in retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md#ra-cb-1--composed-context-brain). It sits **under** the context-assembly layer, not next to it.

- **With CAG ([cache-augmented-generation.md](cache-augmented-generation.md)):** P-FT-5 — voice + corpus. Common for small-corpus support bots.
- **With long-context-first ([long-context-first-architecture.md](long-context-first-architecture.md)):** Same shape as P-FT-5, larger corpus.
- **With RAG (H1–H7):** Voice in weights, facts in retrieval. The production default.
- **With managed-memory ([managed-memory-boundaries.md](managed-memory-boundaries.md)):** Persona is stable across users; memory is per-user. They are orthogonal layers.

---

## Related

- [retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md) — Decision rubric
- [cache-augmented-generation.md](cache-augmented-generation.md) — Common composition partner
- [long-context-first-architecture.md](long-context-first-architecture.md) — Common composition partner
- `ai-llm/references/fine-tuning-recipes.md` — SFT, DPO, GRPO, LoRA mechanics
- `huggingface-skills:` plugin (external) — TRL-based training pipeline (SFT/DPO/GRPO on HF Jobs)
- `ai-local-model-ops` — Self-host considerations for fine-tuned weights
- `ai-prompt-engineering` — The cheaper-first alternative to most fine-tune requests
- `ai-mlops` — Model lifecycle, drift, evaluation in production
