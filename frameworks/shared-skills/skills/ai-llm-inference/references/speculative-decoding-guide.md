# Speculative Decoding Guide

Production guidance for speculative decoding in modern inference stacks. Covers algorithm families, vLLM deployment, and measurement discipline.

**Speedup disclaimer**: All speedup ranges are academic-benchmark figures and are draft-acceptance-rate dependent. Acceptance rate varies by model family, traffic pattern, and sampling settings. Measure in production before committing to an architecture.

---

## Algorithm Families

### 1. EAGLE (Extrapolation Algorithm for Greater Language-model Efficiency)

**What it is**: A draft-head approach trained on the target model's feature representations. Predicts multiple tokens per step using a lightweight autoregressive head on top of target-model hidden states.

**Production status**: Production-standard across vLLM, SGLang, and TensorRT-LLM (~2–3×). **EAGLE-3** is now the deployed default rather than a research preview, and **P-EAGLE** (parallel draft generation, ~1.05–1.69× over vanilla EAGLE-3) landed in vLLM in 2026. Confirm the exact EAGLE variant and draft-head checkpoint your runtime version supports before deploying.

**vLLM availability**: Confirmed as "strong general-purpose model-based method" in vLLM speculative decoding docs. Qualitative gain: high at low QPS, medium-to-high at high QPS.
Source: https://docs.vllm.ai/en/stable/features/speculative_decoding/ (verified 2026-05-17)

**Speedup**: Academic benchmarks report 2–3× on chatbot/coding workloads. Draft-acceptance-dependent — measure in production.

**When to use**: General-purpose text generation, coding tasks, chat; target model must have a compatible EAGLE draft head available.

---

### 2. Multi-Token Prediction (MTP) / DeepSeek MTP

**What it is**: Native multi-token prediction heads trained into the base model itself (rather than a separate draft model). DeepSeek-V3 and related models ship with MTP heads natively.

**Production status**: Supported in vLLM as "MTP" (Multi-Token Prediction). vLLM docs note "best when the target model has native MTP support."
Source: https://docs.vllm.ai/en/stable/features/speculative_decoding/ (verified 2026-05-17)

**Speedup**: Workload-specific; gain is highest when native MTP heads are present and acceptance rate is high. Measure in production.

**When to use**: Models with native MTP heads (e.g., DeepSeek-V3). Do not apply generic draft-model speculative decoding to models without native heads — overhead will negate gains.

---

### 3. Draft Model (Separate Small Model)

**What it is**: A smaller model of the same family generates speculative tokens; the large target model verifies in parallel.

**Production status**: Fully supported in vLLM (listed as a primary method). Also supported in SGLang; verify current SGLang docs for server-side configuration.

**Speedup**: Academic benchmarks report 2–4× with well-matched draft/target pairs. Highly dependent on draft acceptance rate (target: >75% for meaningful gain).

**Key constraints**:
- Draft model must share the same tokenizer as the target model
- Domain mismatch between draft and target collapses acceptance rate
- Memory budget must account for both models running concurrently

---

### 4. Medusa

**What it is**: Multiple parallel prediction heads attached to the target model, each predicting a different future token position. All heads run in a single forward pass.

**Production status**: Medusa is a research-originated technique. vLLM lists an MLP-based speculative method; whether this maps exactly to Medusa depends on your vLLM version — verify at https://docs.vllm.ai/en/stable/features/speculative_decoding/ before deploying.

**Speedup**: Academic benchmarks report 2–3× on certain workloads. Tree-attention verification adds overhead; net gain is workload-specific — measure in production.

**When to use**: Workloads where a Medusa-trained model is available and where output distribution is compatible with parallel head prediction.

---

## Deployment Checklist

- [ ] Algorithm confirmed supported in your runtime version (verify primary docs)
- [ ] Draft model / draft head validated: same tokenizer, same domain
- [ ] Acceptance rate measured at realistic QPS and prompt distribution (>75% target)
- [ ] Latency measured under realistic concurrency (speculative decoding adds memory and compute pressure at high QPS)
- [ ] Memory budget accounts for draft model or extra heads alongside target model
- [ ] No regressions in output quality, structured-output validity, or schema compliance
- [ ] Rollback plan defined: can switch to standard decoding without redeploy

---

## Failure Modes

**Low acceptance rate (<70%)**:
- Draft model domain mismatch — choose a draft model from the same training distribution
- Reduce speculative window (number of draft tokens per step)
- Switch algorithm family (e.g., EAGLE draft head often outperforms generic small models)

**Output formatting regressions**:
- Speculative decoding can shift token probability in constrained decoding; test JSON/schema validity
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
