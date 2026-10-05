# Speculative Decoding Guide

Production guidance for speculative decoding in modern inference stacks. Covers algorithm families, vLLM deployment, and measurement discipline.

Speedup depends on acceptance rate, model pair, traffic pattern, and sampling settings. Measure on representative traffic before committing to an architecture.

## Contents

- [Algorithm Families](#algorithm-families)
- [Deployment Checklist](#deployment-checklist)
- [Failure Modes](#failure-modes)
- [Primary Sources](#primary-sources)

---

## Algorithm Families

### 1. EAGLE (Extrapolation Algorithm for Greater Language-model Efficiency)

**What it is**: A draft-head approach trained on the target model's feature representations. Predicts multiple tokens per step using a lightweight autoregressive head on top of target-model hidden states.

**Production status**: Check the installed runtime's documentation for supported EAGLE variants and compatible draft-head checkpoints before deployment.

**vLLM availability**: Confirmed as "strong general-purpose model-based method" in vLLM speculative decoding docs. Qualitative gain: high at low QPS, medium-to-high at high QPS.
Source: https://docs.vllm.ai/en/stable/features/speculative_decoding/ (verified 2026-05-17)

**Speedup**: Draft-acceptance-dependent; measure on representative traffic.

**When to use**: General-purpose text generation, coding tasks, chat; target model must have a compatible EAGLE draft head available.

---

### 2. Multi-Token Prediction (MTP) / DeepSeek MTP

**What it is**: Native multi-token prediction heads trained into the base model itself (rather than a separate draft model). DeepSeek-V3 and related models ship with MTP heads natively.

**Production status**: Supported in vLLM as "MTP" (Multi-Token Prediction). vLLM docs note "best when the target model has native MTP support."
Source: https://docs.vllm.ai/en/stable/features/speculative_decoding/ (verified 2026-05-17)

**Speedup**: Workload-specific; gain is highest when native MTP heads are present and acceptance rate is high. Measure in production.

**When to use**: Models that ship native MTP heads — check the model card. A model without native heads is not excluded from speculative decoding: use an EAGLE draft head (§1) or a separate draft model (§3) instead.

---

### 3. Draft Model (Separate Small Model)

**What it is**: A much smaller compatible model generates speculative tokens; the large target model verifies them in one parallel forward pass. This is the general method for a target model with no native MTP heads or trained EAGLE head.

**Production status**: Fully supported in vLLM (listed as a primary method). Also supported in SGLang; verify current SGLang docs for server-side configuration.

**Speedup**: Depends on draft acceptance rate, draft cost, and concurrency; measure on representative traffic.

**What drives the speedup** (Leviathan et al., arXiv 2211.17192, Eq. 1 and Thm 3.8): with per-token acceptance rate α, γ draft tokens per step, and draft-to-target cost ratio c,

```
expected tokens per target pass  E = (1 − α^(γ+1)) / (1 − α)
walltime speedup                   = (1 − α^(γ+1)) / ((1 − α)(γ·c + 1))
```

Speedup rises with α and falls with c. A draft that is not much cheaper than the target (c close to 1) gives no gain even at high α, so pick the smallest draft that keeps α high, and tune γ against the measured α.

**Key constraints**:
- Draft model must be much smaller and faster than the target (low c)
- Start with a shared tokenizer/vocabulary. For a different tokenizer, check whether the installed runtime supports cross-vocabulary drafting and validate acceptance and output quality; [vLLM documents a Token-Level Intersection option](https://docs.vllm.ai/en/stable/features/speculative_decoding/#cross-vocabulary-draft-models-tli).
- Domain mismatch between draft and target collapses acceptance rate
- Memory budget must account for both models running concurrently

---

### 4. Medusa

**What it is**: Multiple parallel prediction heads attached to the target model, each predicting a different future token position. All heads run in a single forward pass.

**Production status**: Medusa is a research-originated technique. vLLM lists an MLP-based speculative method; whether this maps exactly to Medusa depends on your vLLM version — verify at https://docs.vllm.ai/en/stable/features/speculative_decoding/ before deploying.

**Speedup**: Tree-attention verification adds overhead; measure net gain on representative traffic.

**When to use**: Workloads where a Medusa-trained model is available and where output distribution is compatible with parallel head prediction.

---

## Deployment Checklist

- [ ] Algorithm confirmed supported in your runtime version (verify primary docs)
- [ ] Draft model / draft head validated for vocabulary compatibility, domain fit, and measured acceptance
- [ ] Acceptance rate measured at realistic QPS and prompt distribution
- [ ] Latency measured under realistic concurrency (speculative decoding adds memory and compute pressure at high QPS)
- [ ] Memory budget accounts for draft model or extra heads alongside target model
- [ ] No regressions in output quality, structured-output validity, or schema compliance
- [ ] Rollback plan defined: can switch to standard decoding without redeploy

---

## Failure Modes

**Low acceptance rate**:
- Draft model domain mismatch — choose a draft model from the same training distribution
- Reduce speculative window (number of draft tokens per step)
- Switch algorithm family (e.g., EAGLE draft head often outperforms generic small models)

**Output formatting regressions**:
- Verify that the selected runtime's constrained-output path preserves target-model behavior; test JSON/schema validity and compare with standard decoding
- Reduce draft window or use stricter verification

**Throughput degradation at high QPS**:
- Memory pressure from running draft model concurrently degrades batching headroom
- Speculative decoding benefit inverts under high-QPS batching: measure before enabling in high-concurrency deployments

---

## Primary Sources

- vLLM Speculative Decoding: https://docs.vllm.ai/en/stable/features/speculative_decoding/ (verified 2026-05-17)
- EAGLE paper: https://arxiv.org/abs/2401.15077
- Medusa paper: https://arxiv.org/abs/2401.10774
- DeepSeek-V3 (MTP): https://arxiv.org/abs/2412.19437
