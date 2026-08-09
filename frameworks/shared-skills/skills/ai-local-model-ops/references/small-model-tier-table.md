# Small-Model Tier Table

Capability and footprint tiers for small open-weight instruct models suitable for local inference, as of July 2026.

**Version caveat:** Point-release version numbers (e.g., Gemma 3.1, Phi-4.2, Qwen 2.6) change frequently. The tiers and capability descriptions below are durable; verify the current release at the primary sources before recommending a specific version tag to users.

---

## Table of Contents

- [Tier Definitions](#tier-definitions)
- [Gemma-Class (Google)](#gemma-class-google)
- [Phi-Class (Microsoft)](#phi-class-microsoft)
- [Qwen-Class (Alibaba)](#qwen-class-alibaba)
- [Ministral-Class (Mistral AI)](#ministral-class-mistral-ai)
- [DeepSeek-R1-Distill-Class](#deepseek-r1-distill-class)
- [Comparison Heuristic](#comparison-heuristic)
- [Anti-Patterns](#anti-patterns)

## Tier Definitions

| Tier | Active params | Typical VRAM / RAM (Q4_K_M) | Primary capability fit |
|------|--------------|----------------------------|----------------------|
| Nano | ≤1B | <1 GB | Edge / on-device; simple classification, completion, tiny chat |
| Small | 1–4B | 1–3 GB | General chat, basic reasoning, code assist on constrained hardware |
| Mid | 5–9B | 3–6 GB | Solid general instruct, function calling, moderate coding |
| Upper-mid | 10–15B | 6–10 GB | Strong reasoning, tool use, long-context summarization |

---

## Gemma-Class (Google)

Reference: https://ai.google.dev/gemma/docs/releases (verify current release)

| Tier | Size | Notes |
|------|------|-------|
| Nano | Gemma 3 1B (verify current tag) | [Previous generation] Multimodal-capable at tiny size; strong for its footprint |
| Small | Gemma 3 4B | [Previous generation] Good instruction following; vision variant available |
| Mid | Gemma 3 9B | [Previous generation] Top of the Gemma 3 small family; competitive with 7–9B peers |
| Upper-mid | Gemma 4 12B (April 2, 2026; Apache 2.0) | Encoder-free multimodal: text, image, audio, video input. 16 GB unified memory minimum. QAT weights (June 5, 2026) cut memory ~72% vs BF16. `ollama pull gemma4`; LM Studio supported. Replaces Gemma 3 9B as the recommended Gemma mid-tier for new projects. |

**Gemma 3n (on-device/phone):** A separate Gemma 3 branch optimized for mobile and edge deployment. Verify current model card and supported runtimes before recommending for on-device Android use.

**When to pick Gemma-class:**
- Multimodal local inference at small scale (image + text, and with Gemma 4: audio/video input too).
- Google TPU/JAX ecosystem familiarity; Gemma models are well-supported in transformers and via GGUF.
- Privacy-sensitive Android / on-device deployment (Gemma is designed for on-device use; use Gemma 3n for phone-class hardware).

**Footprint at Q4_K_M (Gemma 3):** 1B ≈ <1 GB, 4B ≈ 3 GB, 9B ≈ 5.5 GB.
**Footprint for Gemma 4 12B:** BF16 requires ~16 GB unified memory; QAT weights (June 2026) reduce memory ~72% — verify current size at https://ai.google.dev/gemma/docs/releases before quoting figures.

---

## Phi-Class (Microsoft)

Reference: https://huggingface.co/microsoft (filter by "phi"; verify current release)

| Tier | Size | Notes |
|------|------|-------|
| Small | Phi-3.5 mini / Phi-4-mini (3–4B range; verify current) | Punches above weight on reasoning; excellent for structured output |
| Mid | Phi-4 (14B range; verify current) | Strong at STEM reasoning and code; smaller context than Llama peers |

**When to pick Phi-class:**
- Tasks that are reasoning-heavy or STEM-heavy relative to model size.
- Windows / Azure ecosystem (Microsoft first-party support, available in Foundry Local catalog).
- When a 4B-class model needs to do structured JSON output reliably.

**Watch for:** Phi models are trained on synthetic data; distribution shift on real-world messy inputs is a known risk. Evaluate on your actual data before committing.

---

## Qwen-Class (Alibaba)

Reference: https://huggingface.co/Qwen (verify current release)

| Tier | Size | Notes |
|------|------|-------|
| Nano | Qwen3 0.6B (verify) | Fits on-device; basic completions |
| Small | Qwen3 1.7B, 4B (verify) | Strong multilingual; function calling from small size |
| Mid | Qwen3 7B, 8B (verify) | Excellent multilingual + code; competitive with Llama 3.1 8B |
| Upper-mid | Qwen3 14B (verify) | Strong reasoning; thinking-mode variant available |

**When to pick Qwen-class:**
- Multilingual tasks (Qwen has the broadest language coverage in this size range).
- Function calling or tool use at small footprint — Qwen models have strong structured-output training.
- Thinking / chain-of-thought variants: Qwen offers "thinking mode" toggles at multiple sizes.

**MoE option:** Qwen3-30B-A3B (30B total / ~3B active per token) fits on a 36 GB M3 Mac at Q4_K_M and delivers upper-mid quality at mid-tier inference cost. See `model-sizing-matrix.md`.

**Newer releases:** Qwen3.5 (Feb 2026) and Qwen3.6 (April 2026) have shipped since Qwen3; the 3.6 dense-27B variant is aimed squarely at single-consumer-GPU agentic coding. Tier boundaries above still apply by parameter count — verify GGUF/Ollama support for the specific point release before recommending it, since community quantizations for a new architecture can lag by weeks.

---

## Ministral-Class (Mistral AI)

Reference: https://mistral.ai/news (verify current release)

| Tier | Size | Notes |
|------|------|-------|
| Small | Ministral 3B | Edge-oriented; Apache 2.0 |
| Mid | Ministral 8B, Mistral 3 14B (dense) | Strong general instruct; part of the Mistral 3 family alongside the much larger Mistral Large 3 MoE |

**When to pick Ministral-class:**
- European-hosted / EU-jurisdiction preference for model provenance.
- Function calling and structured output at small footprint — Mistral's small models are trained with tool-use in mind.
- Need a permissively licensed (Apache 2.0) small model with strong multilingual European-language coverage.

---

## DeepSeek-R1-Distill-Class

Reference: https://huggingface.co/deepseek-ai (verify current release)

| Tier | Size | Notes |
|------|------|-------|
| Mid | DeepSeek-R1-Distill-Qwen-7B | Reasoning-style output (chain-of-thought traces) distilled from R1 onto a Qwen base; not equivalent to full R1 |
| Upper-mid | DeepSeek-R1-Distill-Qwen-14B, -32B | Best local approximation of R1-style reasoning; still meaningfully behind full R1/V3 on hard tasks |

**When to pick DeepSeek-distill-class:**
- The task benefits from visible chain-of-thought / reasoning-trace style output and a 7–32B footprint is acceptable.
- MIT-licensed weights are a requirement.

**Watch for:** These are distillations, not the frontier DeepSeek model. Do not present distill output quality as equivalent to hosted DeepSeek-R1/V3 API responses — evaluate the gap on your own task before committing.

---

## Comparison Heuristic

```
Primary language is non-English?
└── Qwen-class (broadest multilingual coverage)

Strong reasoning / STEM / structured output with tiny footprint?
└── Phi-class (punches above weight on these benchmarks)

Multimodal (image + text) at small scale?
└── Gemma-class

General-purpose local chat, tool use, code?
└── Any mid-tier from all three families; measure on your eval set
```

---

## Anti-Patterns

- Picking a model family by benchmark leaderboard position without running the actual tasks you care about locally.
- Locking to a specific point-release version number in documentation (releases move fast; pin to the tag you tested, hedge everything else).
- Assuming the smallest Phi or Qwen model will handle long-context tasks — context windows at <4B are often shorter; verify current specs.
- Conflating "Nano fits on-device" with "Nano is production-ready" — evaluate quality before shipping.
