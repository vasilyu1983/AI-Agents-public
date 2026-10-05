# MoE and Expert Parallelism

Guidance for deploying Mixture-of-Experts (MoE) models — including DeepSeek-V3/V4, Qwen3-MoE, Kimi-K2, Mixtral — at production scale.

**Hedge note**: Active-parameter counts, model architecture details, and EPLB algorithm specifics change rapidly across model versions. Verify param counts and architecture details against the relevant model card before deploying.

## Table of Contents

- [When to Use This Reference](#when-to-use-this-reference)
- [Intake Question](#intake-question)
- [Decision-Flow Branch](#decision-flow-branch)
- [Runtime Support](#runtime-support)
- [Key Concepts](#key-concepts)
- [Routing Health Metrics](#routing-health-metrics)
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
- Expert **granularity**: many narrow experts or few wide ones? This is not a neutral choice at serve time — see the granularity/all-to-all coupling below

### Model sizing reference (verify before deploying)

**Read the two numbers separately.** Total parameters are the *memory and interconnect* bill — every weight must be resident and reachable, which sets GPU count, EP degree, and all-to-all pressure. Active parameters are the *FLOPs* bill. Vendor headlines quote whichever flatters the claim: "13B active" sells the compute story while 284B total still has to fit somewhere. A dense-vs-MoE claim is meaningless until you name the comparison basis — **iso-active-FLOPs** (favours MoE, ignores its memory), **iso-total-params** (favours dense, ignores MoE's cheaper per-token compute), or **iso-latency / iso-cost at a fixed SLO** (the only basis that answers a serving question, because it prices memory, FLOPs, and all-to-all together).

**DeepSeek-V4** (preview announced 2026-04-24 on DeepSeek's API docs). DeepSeek's own release note states the two variants verbatim as **"1.6T total / 49B active params"** (V4-Pro) and **"284B total / 13B active params"** (V4-Flash). The V4-Flash model card repeats "DeepSeek-V4-Flash with 284B parameters (13B activated)" but does **not** state routed/shared expert counts — read those from the model card's `config.json` before sizing EP degree, not from this table.

Per-model routed/shared expert counts (DeepSeek-V3, Kimi-K2, Qwen3-MoE) are a build-time fact and live in one place: the table in [architecture-limitations-and-workarounds.md §5](../../ai-pretraining/references/architecture-limitations-and-workarounds.md#5-mlp--ffn-and-mixture-of-experts). For EP sizing only two of those numbers matter: expert count (sets the EP degrees that keep experts whole) and top-k (sets all-to-all volume, below).

---

## Decision-Flow Branch

```text
MoE model (config.json lists routed experts)?
  |
  |- Yes
  |   |
  |   |- Precision and memory BEFORE parallelism
  |   |   Settle weight precision first (references/quantization-patterns.md; note its
  |   |   NVFP4 finding that MoE models including Qwen3-235B-A22B recover unusually well).
  |   |   Then size KV cache at target max-context x max-concurrency
  |   |   (references/kv-cache-optimization.md).
  |   |   Precision decides whether you need 8 GPUs at all -- do not tune EP degree
  |   |   against a BF16 footprint you were never going to deploy.
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

As of 2026-08-29. Flag names churn between releases, so the table records a verdict per capability and leaves exact flags to the linked docs.

| Runtime | EP for MoE | EPLB / expert re-layout | Verdict | Where to confirm flags |
|---|---|---|---|---|
| **vLLM** | documented (Mixtral, DeepSeek-V3, Qwen-MoE named in docs) | not documented as a shipped feature in this reference's check | use for EP; benchmark EP degree yourself | https://docs.vllm.ai/en/stable/serving/distributed_serving.html |
| **SGLang** | documented; elastic EP / partial-failure tolerance published (blog.sglang.ai, 2026-03-25) | EPLB configuration referenced in SGLang material; no stable docs URL confirmed here | strongest public DeepSeek-MoE serving story; verify EPLB flags before relying on it | https://docs.sglang.io/ |
| **TensorRT-LLM** | supported (Mixtral and model-specific guides) | unknown as of 2026-08-29 | use where the model has an NVIDIA deployment guide | https://nvidia.github.io/TensorRT-LLM/ |

## Key Concepts

**Expert Parallelism (EP)**: Each GPU in the EP group holds a subset of the expert weights. During the MoE layer, tokens are routed to the GPU that holds the relevant expert, with all-to-all communication to move activations.

**Sizing all-to-all before you book the cluster.** The volume is closed-form, so estimate it rather than discovering it in a benchmark. Per MoE layer, dispatch plus combine each move one hidden vector per (token, selected expert):

```text
bytes_per_moe_layer ≈ 2 · tokens_in_batch · top_k · d_model · dtype_bytes
total ≈ bytes_per_moe_layer · num_moe_layers · (e−1)/e      # e = EP degree
```

The `(e−1)/e` factor is the share that actually crosses the wire — roughly `1/e` of destinations are already local. Worked example: 4096 tokens, top-8, `d_model` 7168, bf16 → **≈ 0.94 GB per MoE layer**, of which ≈ 0.82 GB crosses the wire at EP degree 8. Multiply by MoE layer count, divide by achievable interconnect bandwidth, and compare the result against your TTFT budget before choosing EP degree.

**EPLB (Expert-Parallel Load Balancing)**: Redistributes expert assignments to prevent hot experts from becoming bottlenecks. Supported in some runtimes — verify before assuming availability.

**Load-adaptive expert re-layout (LAER-MoE)**: A stronger form of the same idea — rather than only reassigning which GPU serves which expert, re-lay-out the expert *parameters* themselves in response to observed load. LAER-MoE ([arXiv 2602.11686](https://arxiv.org/abs/2602.11686), ASPLOS 2026) introduces **Fully Sharded Expert Parallel (FSEP)**, which shards expert parameters across all devices and restores partial experts on demand via all-to-all, so expert placement can be reallocated to match actual routing load; it pairs this with fine-grained communication scheduling and joint placement/token-routing planning. The authors report "up to 1.69x acceleration compared to the current state-of-the-art training systems" on an A100 cluster.

**Scope caveat**: LAER-MoE is evaluated on MoE **training**, not serving. The load-imbalance mechanism it targets is the same one that bites at inference, and the re-layout idea generalizes, but the reported speedup is a training number — do not quote it as an inference result. As of Aug 2026, treat FSEP-style re-layout as a direction to watch in serving runtimes rather than a shipped serving feature; check your runtime's docs.

**Granularity ↔ all-to-all cost coupling**: The Aug 2026 MoE survey ([arXiv 2608.08650](https://arxiv.org/abs/2608.08650)) treats expert granularity, topology, routing freedom, load-balancing scope, and execution structure as five *coupled* dimensions rather than independent knobs. The serving consequence: finer-grained experts (the 128 → 256 → 384 trend at constant top-8) do not change active FLOPs much, but they do change the routing and all-to-all profile — more, smaller messages against the same interconnect. A model that looks cheap on active-parameter count can still be all-to-all-bound. Benchmark EP degree against the actual expert count, not against active-parameter count.

**All-to-all topology**: The communication pattern where each GPU sends data to every other GPU in the EP group. Latency and bandwidth of the interconnect (NVLink vs. InfiniBand) determines the practical EP degree ceiling.

**EP vs TP tradeoff**: EP reduces per-GPU memory for MoE layers; TP reduces per-GPU memory for attention layers. Hybrid configurations (EP for expert layers, TP for attention) are common in production for very large MoE models.

---

## Routing Health Metrics

"Monitor expert utilization" is not a metric. These are, with the balancing fix each one moves.

| Metric | Definition | Moved by |
|---|---|---|
| Per-expert token share | fraction of routed tokens landing on expert *i* | all three |
| Load CV | std/mean of per-expert load across experts — one scalar for "how lumpy" | aux loss, bias-based |
| **MaxVio** | maximal violation of load balance | aux loss, bias-based |
| Normalised routing entropy | entropy of the token-share distribution ÷ log(num_experts); 1.0 = uniform, → 0 = collapse | aux loss, bias-based |
| Token drop rate | tokens dropped because an expert hit its capacity factor (only meaningful when a capacity factor is set) | aux loss, bias-based, EPLB |
| Per-GPU load skew | max/mean load across EP ranks after expert placement | **EPLB only** |

**MaxVio** comes from DeepSeek's *"Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts"* ([arXiv 2408.15664](https://arxiv.org/abs/2408.15664)): the maximum over experts of `(Load_i − mean_Load) / mean_Load` — the worst expert's overload relative to perfectly balanced load. The paper separates `MaxVio_global` (counted over the whole validation set) from `MaxVio_batch` (per batch) and averages across layers for a model-wide figure. At serve time the batch-scoped form is the operational one: it decides whether *this* forward pass stalls on one rank.

**Which fix moves what.** Aux loss and bias-based balancing act on the *router*, so they move token share, CV, MaxVio, and entropy. EPLB acts on *placement* — it reassigns experts to GPUs and leaves routing untouched — so it moves per-GPU load skew and drop rate while MaxVio stays put. Reading a flat MaxVio as evidence EPLB failed is a category error.

**Measurement window**: per-step values are noisy and will trip any threshold occasionally — alert on a rolling window (tens to hundreds of steps), keep per-step for post-hoc debugging only.

**Heuristic thresholds** (rules of thumb, not measured constants — calibrate on your own traffic): any expert's token share > 3× uniform (`3/num_experts`) for N consecutive steps → collapse warning; normalised routing entropy trending down over hours at stable traffic → routing drift, re-check before it becomes collapse; non-zero token drop rate at steady state → capacity factor too tight or load skewed, fix the balance before raising the factor.

---

## Operational Notes

- Expert load imbalance is a primary bottleneck: monitor per-expert utilization
- All-to-all communication scales with EP degree × token batch size: benchmark under realistic QPS
- Mixed EP+TP topologies are common — design before deploying, not after
- Cold-start latency for MoE models can be high due to weight size: account in autoscaling headroom
- **Quality regression gate.** Routing changes, EPLB enablement, expert pruning, and EP-topology changes are all capable of moving output quality, not just throughput — expert pruning most obviously, but a re-layout that changes which tokens hit which expert can too. After any of them, run the task eval suite *and* schema-valid rate against the pre-change baseline, not just tokens/s and TTFT. Name the rollback trigger before the change ships; a workable default (rule of thumb, calibrate on your own eval variance) is: revert if schema-valid rate drops more than 1 point absolute, or any task-eval score drops more than 2 points absolute, against baseline.

---

## Primary Sources

- vLLM distributed serving (MoE/EP): https://docs.vllm.ai/en/stable/serving/distributed_serving.html
- SGLang docs (EP, EPLB): https://docs.sglang.io/
- TensorRT-LLM MoE: https://nvidia.github.io/TensorRT-LLM/
- Mixtral / MoE architecture reference: https://arxiv.org/abs/2401.04088
- MoE architecture survey — routing, topology, load balancing, expert parallelism (Li, Aug 2026): https://arxiv.org/abs/2608.08650
- LAER-MoE: Load-Adaptive Expert Re-layout for Efficient Mixture-of-Experts Training (ASPLOS 2026): https://arxiv.org/abs/2602.11686
- DeepSeek-V4 preview release note (parameter counts, 2026-04-24): https://api-docs.deepseek.com/news/news260424/
- DeepSeek-V4-Flash model card: https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash
