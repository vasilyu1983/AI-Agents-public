# Small-Model Tier Table

Capability and footprint tiers for small open-weight instruct models suitable for local inference. Tiers are defined by parameter count, so they survive new releases; the current checkpoint in each tier is a lookup, not a fact to remember.

**Lookup step:** before recommending a model, read the current release's model card for total parameters, context window, licence, and modality, and check that your runtime (Ollama library, LM Studio, MLX community conversions) supports that exact release. Pin the tag you tested.

---

## Table of Contents

- [Tier Definitions](#tier-definitions)
- [Family Traits](#family-traits)
- [Comparison Heuristic](#comparison-heuristic)
- [Anti-Patterns](#anti-patterns)

## Tier Definitions

Weights footprint = total params × bpw / 8 (see [model-sizing-matrix.md](model-sizing-matrix.md#sizing-formula)); the column below uses Q4_K_M at ~4.8 bpw and excludes KV cache and runtime overhead.

| Tier | Total params | Weights at Q4_K_M | Primary capability fit |
|------|--------------|-------------------|------------------------|
| Nano | ≤1B | ≤ ~0.6 GB | Edge / on-device; simple classification, completion, tiny chat |
| Small | 1–4B | ~0.6–2.4 GB | General chat, basic reasoning, code assist on constrained hardware |
| Mid | 5–9B | ~3.0–5.4 GB | Solid general instruct, function calling, moderate coding |
| Upper-mid | 10–15B | ~6.0–9.0 GB | Stronger reasoning, tool use, long-context summarization |

**Small MoE option:** a small-active MoE (for example ~30B total with a few billion active) runs at roughly mid-tier speed but needs memory for its **total** parameters — ~18 GB of weights at Q4_K_M for 30B total — so it belongs on a 24 GB+ machine, not a phone or 8–16 GB laptop.

**Vendor QAT / native low-bit releases:** when a family ships quantization-aware-trained or native low-bit weights, size from the published file (BF16 weights are 2 bytes per parameter, so a 12B BF16 checkpoint is ~24 GB before KV cache), and compare it with a community quant on your eval set.

---

## Family Traits

Family tendencies shift between releases — treat these as a shortlist to evaluate, not a verdict. Verify on the current model card.

| Family | Tends to be chosen for | Watch for | Primary source |
|--------|------------------------|-----------|----------------|
| Gemma (Google) | Multimodal input at small scale; on-device / Android variants | Check which modalities and runtimes the specific release supports | https://ai.google.dev/gemma/docs/releases |
| Phi (Microsoft) | Reasoning, STEM and structured output relative to size; Windows / Foundry Local catalog | Heavily synthetic training data — test on your real, messy inputs; context windows may be shorter than peers | https://huggingface.co/microsoft |
| Qwen (Alibaba) | Multilingual coverage, function calling at small footprint, thinking-mode toggles | New point releases may lag in GGUF/Ollama support | https://huggingface.co/Qwen |
| Ministral / small Mistral (Mistral AI) | EU-provenance preference, permissive licensing, tool use, European languages | Confirm the licence per checkpoint | https://mistral.ai/news |
| Reasoning distills (e.g. DeepSeek R1-distill) | Visible reasoning-trace style at 7–32B | Distillations of a much larger model — not equivalent to the teacher; measure the gap | https://huggingface.co/deepseek-ai |

---

## Comparison Heuristic

```
Primary language is non-English?
└── Qwen-class (broad multilingual coverage) — verify your language on your eval set

Strong reasoning / STEM / structured output with tiny footprint?
└── Phi-class

Multimodal (image + text) at small scale?
└── Gemma-class

General-purpose local chat, tool use, code?
└── Any mid-tier candidate from several families; measure on your eval set
```

---

## Anti-Patterns

- Picking a model family by benchmark leaderboard position without running the actual tasks you care about locally.
- Locking to a specific point-release version number in documentation (releases move fast; pin to the tag you tested, hedge everything else).
- Assuming the smallest models handle long-context tasks — context windows at <4B are often shorter; verify current specs.
- Conflating "Nano fits on-device" with "Nano is production-ready" — evaluate quality before shipping.
- Sizing a MoE by its active parameters — memory follows total parameters.
