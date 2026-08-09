# MoE and Expert Parallelism

Guidance for deploying Mixture-of-Experts (MoE) models — including DeepSeek-V3/V4, Qwen3-MoE, Kimi-K2, Mixtral — at production scale.

**Hedge note**: Active-parameter counts, model architecture details, and EPLB algorithm specifics change rapidly across model versions. Verify param counts and architecture details against the relevant model card before deploying.

## Table of Contents

- [When to Use This Reference](#when-to-use-this-reference)
- [Intake Question](#intake-question)
- [Decision-Flow Branch](#decision-flow-branch)
- [Runtime Support](#runtime-support)
- [Key Concepts](#key-concepts)
- [Operational Notes](#operational-notes)
- [Primary Sources](#primary-sources)

---

## When to Use This Reference

Use this reference when:

- The target model is a MoE architecture (DeepSeek-V3, Qwen3-MoE, Mixtral, Kimi-K2, or similar)
- You are choosing parallelism strategy across multiple GPUs or nodes
- You are investigating expert-load imbalance or all-to-all communication bottlenecks
- You are evaluating EP degree (how many GPUs share expert routing)

---

## Intake Question

**Is this a MoE model?**

Confirm before any parallelism design:
- Model architecture: dense transformer or MoE with routed experts?
- Number of total experts vs. active experts per token (e.g., DeepSeek-V3 activates a small subset of total experts per token — verify exact numbers in the model card)
- Expert routing strategy: top-K gating, auxiliary-loss-free balancing, or other?

---

## Decision-Flow Branch

```text
MoE model (DeepSeek-V3/V4, Qwen3-MoE, Kimi-K2, Mixtral)?
  |
  |- Yes
  |   |
  |   |- Assess EP degree
  |   |   How many GPUs should share routing for the expert layers?
  |   |   Higher EP degree reduces per-GPU memory but increases all-to-all communication.
  |   |   Tradeoff: EP degree × all-to-all cost vs. TP degree × activation communication cost.
  |   |
  |   |- Assess EPLB (Expert-Parallel Load Balancing)
  |   |   Load imbalance across experts is a common bottleneck.
  |   |   Does your runtime support EPLB to redistribute expert load dynamically?
  |   |   Check: vLLM EP docs, SGLang elastic EP (blog.sglang.ai, 2026-03-25)
  |   |
  |   |- Assess all-to-all topology
  |   |   Within-node: NVLink (low latency, prefer higher EP degree)
  |   |   Cross-node: InfiniBand / RoCE (higher latency, reduce EP degree or use TP instead)
  |   |   Hybrid: EP within node, TP across nodes is a common production pattern
  |   |
  |   `- Benchmark before locking in EP degree
  |       Token/s, TTFT, and expert utilization all vary by EP degree and traffic mix.
  |
  `- No -> use standard TP/PP/DP patterns (see references/parallelism-patterns.md)
```

---

## Runtime Support

### vLLM

vLLM documents expert parallelism as a distributed inference capability for MoE models including Mixtral, DeepSeek-V3, and Qwen-MoE (confirmed in docs navigation: docs.vllm.ai, 2026-05-17). Exact EP configuration flags (e.g., `--expert-parallel-size`): verify against current vLLM distributed serving docs at https://docs.vllm.ai/en/stable/serving/distributed_serving.html — the specific flag names are not confirmed via this reference and may change across versions.

### SGLang

SGLang has published work on elastic EP and partial-failure tolerance for DeepSeek MoE deployments (referenced as "Elastic EP in SGLang" blog post, 2026-03-25, at blog.sglang.ai). EPLB and EP configuration: verify at https://docs.sglang.io/ — current EP flag names and EPLB configuration are not confirmed via a stable docs URL in this reference.

### TensorRT-LLM

TensorRT-LLM supports MoE models including Mixtral. For expert parallelism configuration: see https://nvidia.github.io/TensorRT-LLM/ and the model-specific deployment guides.

---

## Key Concepts

**Expert Parallelism (EP)**: Each GPU in the EP group holds a subset of the expert weights. During the MoE layer, tokens are routed to the GPU that holds the relevant expert, with all-to-all communication to move activations.

**EPLB (Expert-Parallel Load Balancing)**: Redistributes expert assignments to prevent hot experts from becoming bottlenecks. Supported in some runtimes — verify before assuming availability.

**All-to-all topology**: The communication pattern where each GPU sends data to every other GPU in the EP group. Latency and bandwidth of the interconnect (NVLink vs. InfiniBand) determines the practical EP degree ceiling.

**EP vs TP tradeoff**: EP reduces per-GPU memory for MoE layers; TP reduces per-GPU memory for attention layers. Hybrid configurations (EP for expert layers, TP for attention) are common in production for very large MoE models.

---

## Operational Notes

- Expert load imbalance is a primary bottleneck: monitor per-expert utilization
- All-to-all communication scales with EP degree × token batch size: benchmark under realistic QPS
- Mixed EP+TP topologies are common — design before deploying, not after
- Cold-start latency for MoE models can be high due to weight size: account in autoscaling headroom

---

## Primary Sources

- vLLM distributed serving (MoE/EP): https://docs.vllm.ai/en/stable/serving/distributed_serving.html
- SGLang docs (EP, EPLB): https://docs.sglang.io/
- TensorRT-LLM MoE: https://nvidia.github.io/TensorRT-LLM/
- Mixtral / MoE architecture reference: https://arxiv.org/abs/2401.04088
