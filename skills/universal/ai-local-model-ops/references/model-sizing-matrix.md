# Model Sizing

How to decide whether an open-weight model fits a local machine, and how fast it will run, from numbers you look up for the exact checkpoint and quant you plan to use. Model families and releases change too fast for a per-model table; the formula does not.

## Table of Contents

- [Sizing Formula](#sizing-formula)
- [Where the Inputs Come From](#where-the-inputs-come-from)
- [Worked Examples](#worked-examples)
- [Memory Classes](#memory-classes)
- [Throughput: Decode Is Bandwidth-Bound](#throughput-decode-is-bandwidth-bound)
- [Model-Choice Rules That Do Not Depend on the Release](#model-choice-rules-that-do-not-depend-on-the-release)
- [Hardware-specific notes](#hardware-specific-notes)
- [Selection Heuristic](#selection-heuristic)
- [Local vs API: The Real Tradeoff](#local-vs-api-the-real-tradeoff)
- [Local Training Is a Different Feasibility Question](#local-training-is-a-different-feasibility-question)

---

## Sizing Formula

```text
memory needed ≈ weights + KV cache + runtime overhead

weights (GB)   ≈ total_params (billions) × bits_per_weight / 8
KV cache (B)   ≈ 2 × n_layers × n_kv_heads × head_dim × bytes_per_elem × context_tokens × concurrent_sequences
overhead       = compute buffers, driver/runtime context, OS share — measure it; do not assume zero
```

- **MoE models: use TOTAL parameters for memory.** Every expert must be resident (in VRAM, unified memory, or — with expert offload — system RAM). Active parameters set per-token compute and bandwidth, not the memory footprint. A "17B active / 109B total" model needs memory for 109B.
- **KV cache:** use `num_key_value_heads` from `config.json`, not the attention-head count — grouped-query attention shrinks KV by `n_heads / n_kv_heads`. Full derivation and KV quantization options: [../../ai-llm-inference/references/kv-cache-optimization.md](../../ai-llm-inference/references/kv-cache-optimization.md). KV grows linearly with context, so an advertised million-token window is not a local capacity claim; compute KV at the context you will actually run.
- **Expert offload** (llama.cpp keeps some or all MoE expert tensors in system RAM while attention/shared weights stay on the GPU) changes *where* the total lives, not *how much* there is: RAM + VRAM together must still hold the whole model. Check `llama-server --help` for the current offload flags.

## Where the Inputs Come From

| Input | Look it up at | Notes |
|-------|---------------|-------|
| total params | model card, or `config.json` + safetensors index `total_size` | For MoE, the card usually states both total and active — use total |
| bits per weight | the exact quant file you will download: `file_bytes × 8 / params` | Effective bpw of K-quants is model-dependent and often higher than the nominal figure; see [quantization-format-table.md](quantization-format-table.md) |
| weights directly | the GGUF / safetensors file sizes in the repo listing | The most reliable number — prefer it over any formula |
| `n_layers`, `n_kv_heads`, `head_dim` | `config.json` | Needed for KV cache |
| usable memory | GPU VRAM; on Apple Silicon, the share of unified memory the GPU may wire on your macOS version | Unified memory is not 100% GPU-addressable by default — check before promising a fit |

Vendor-native low-bit releases (QAT checkpoints, MXFP4-style releases) ship at their own precision: size them from the published file, not from `params × 16 / 8`. BF16/FP16 is 2 bytes per parameter.

## Worked Examples

Illustrative configurations — read your model's real values from its card and `config.json`.

| Case | Arithmetic | Result |
|------|-----------|--------|
| MoE, 109B total / 17B active, Q4_K_M (~4.8 bpw) | 109 × 4.8 / 8 | **≈ 65.4 GB weights** — not the ~10 GB the active parameters alone would suggest |
| MoE, 400B total, Q4_K_M | 400 × 4.8 / 8 | ≈ 240 GB weights — multi-GPU or heavy CPU offload territory |
| Dense 70B, Q4_K_M | 70 × 4.8 / 8 | ≈ 42 GB weights |
| KV for a 70B GQA config (80 layers, 8 KV heads, head_dim 128, FP16) | 2 × 80 × 8 × 128 × 2 | 327,680 B/token (320 KiB); 8k context ≈ 2.5 GiB; 32k ≈ 10 GiB per sequence |
| Dense 8B, Q4_K_M vs Q8_0 | 8 × 4.8 / 8 vs 8 × 8.5 / 8 | ≈ 4.8 GB vs ≈ 8.5 GB |

So "can I run a 70B-class model on my Mac?" becomes: ~42 GB weights + KV at your context + overhead, compared with the GPU-usable share of unified memory — not a yes/no from a model-name table.

## Memory Classes

Largest total parameter count whose **weights** fit while leaving 20% of usable memory for KV cache and overhead: `max_params (B) ≈ usable_GB × 0.8 × 8 / bpw`.

| Usable memory | Q4_K_M (~4.8 bpw) | Q8_0 (~8.5 bpw) |
|---------------|-------------------|-----------------|
| 16 GB | ~21B | ~12B |
| 24 GB | ~32B | ~18B |
| 32 GB | ~43B | ~24B |
| 48 GB | ~64B | ~36B |
| 64 GB | ~85B | ~48B |
| 80 GB | ~107B | ~60B |
| 128 GB | ~171B | ~96B |
| 192 GB | ~256B | ~145B |

Long contexts or several concurrent sequences can need more than the 20% reserve — compute the KV term instead of trusting the reserve. MoE rows use total parameters.

## Throughput: Decode Is Bandwidth-Bound

At batch size 1, each generated token reads the weights it uses once, so an upper bound is:

```text
decode tokens/sec ≲ memory bandwidth (GB/s) ÷ bytes read per token
bytes read per token ≈ dense: all weight bytes;  MoE: active-parameter bytes (+ shared layers)
```

Illustration with a hypothetical 400 GB/s machine: dense 70B at Q4_K_M (≈ 42 GB) → at most ~9.5 tok/s; a 17B-active MoE at Q4_K_M (≈ 10.2 GB read per token) → at most ~39 tok/s, while still needing memory for all its total parameters. Real numbers land below the bound. Prefill (prompt processing) is compute-bound and scales differently. Look up your machine's memory bandwidth and measure with llama.cpp's benchmark tooling or your runtime's timing output before quoting speeds.

## Model-Choice Rules That Do Not Depend on the Release

- **"Open-weight" does not mean "runs on your laptop."** Frontier-scale open MoE releases run to hundreds of billions of total parameters; at Q4 they need hundreds of GB. Realistic paths are multi-GPU, heavy CPU+GPU offload on a high-RAM host (slow but functional), or aggressive sub-4-bit dynamic quants — verify quality on your eval set before trusting those.
- **Distilled small models are not the teacher.** A small model fine-tuned on a large model's reasoning traces inherits the style, not the capability. Do not present its output as equivalent to the full model; measure the gap on your task.
- **New architectures lag in local runtimes.** GGUF conversions and Ollama/LM Studio support for a new architecture can trail the official release; conversions of complex MoE routing can also trail the original on quality. Confirm runtime support and compare against the original before recommending a fresh release.
- **Check the chat template / response format.** Some releases use a model-specific response format; confirm your runtime supports it before deploying.
- **Check the licence on the model card** before redistributing or shipping — licences differ across and within families.
- **Look up, don't recall:** current checkpoint names, parameter counts, context windows and quant availability come from the model card and the repo file listing (e.g. https://huggingface.co, https://ollama.com/library) at decision time.

---

## Hardware-specific notes

### Apple Silicon (unified memory)

**Inference paths:**
- **Ollama / llama.cpp (GGUF):** Simplest daemon-based path. Uses Metal automatically. Best for most local-use cases.
- **LM Studio:** GUI frontend over llama.cpp/MLX. Supports both GGUF and MLX model formats natively — pick MLX models from HuggingFace for best Metal throughput.
- **MLX (Apple's framework):** Framework-level Python library targeting Apple Silicon Metal. Use MLX when you need: (a) LoRA fine-tuning on-device, (b) custom generation pipelines, (c) model-level control not exposed by daemon runtimes. Quantization and LoRA adapters are supported natively. Verify current release and model support at https://github.com/ml-explore/mlx-lm.

**Unified memory advantage:** RAM and VRAM share the same pool — no PCIe copy between them. Once the weights fit, context length is the main constraint because KV cache scales linearly with sequence length; KV-cache quantization (e.g. Q8_0 KV) roughly halves that term.

### Discrete GPUs (consumer and datacenter)

- If the weights do not fit in VRAM, llama.cpp can offload layers or experts to CPU/RAM — slower, but functional.
- Flash Attention helps long-context throughput; pair it with KV-cache quantization (see [quantization-format-table.md](quantization-format-table.md#kv-cache-quantization)).
- FP8 support and throughput differ by GPU generation and SKU; check the datasheet and your runtime's FP8 support before choosing FP8 over GGUF K-quants.
- Single-card production serving (vLLM, TensorRT-LLM, BF16/FP8 on datacenter GPUs) is serving engineering — hand off to [../../ai-llm-inference/SKILL.md](../../ai-llm-inference/SKILL.md).

---

## Selection Heuristic

1. Start with the largest model whose weights fit with 20% of usable memory left for KV cache and overhead (see [Memory Classes](#memory-classes)); compute KV explicitly for long contexts.
2. Prefer Q4_K_M over Q5_K_M unless you measure a meaningful quality gap on your eval set.
3. Use Q8_0 only if memory permits — quality is near-lossless but needs ~1.8× the memory of Q4_K_M (8.5 vs 4.8 bpw).
4. For MoE models, size memory by **total** parameters; active parameters only predict speed.
5. If throughput is the bottleneck on a datacenter GPU with enough memory, serve at FP8 or BF16 before quantizing further.

See `references/quantization-format-table.md` for format details.

---

## Local vs API: The Real Tradeoff

The honest comparison is rarely "quality" in isolation — it's total cost of ownership against the constraint that actually matters.

**Local wins when:**
- Data cannot leave the premises (regulatory, contractual, or trust reasons) — this is the strongest and most common real justification.
- Offline or air-gapped operation is a hard requirement, not a nice-to-have.
- Request volume is high and steady enough that a local GPU or Apple Silicon workstation amortizes below API cost within months — do the arithmetic on your actual token volume and current hardware and API prices, not a vendor's marketing comparison.
- The local model meets the measured latency requirement with enough memory headroom for the real context and concurrency.
- A locally runnable model meets the task's measured quality bar on representative requests.

**API (hosted frontier) wins when:**
- The task needs frontier-tier reasoning, long-context coherence, or tool-use reliability that open-weight models at a size you can actually run locally do not match on your eval set — check this per task, especially for multi-step agentic work.
- Traffic is spiky or low-volume — an always-on local GPU is dead capital between bursts; pay-per-token is cheaper below a threshold that depends on your GPU cost and utilization.
- You need a context window far beyond what fits in local memory once the KV cache is counted.
- Engineering time for local ops (driver issues, quant regressions, model updates, capacity planning) costs more than the API bill would.

**The trap to avoid in both directions:** "Local" is not automatically cheaper (hardware, power, and your own ops time are real costs) and "hosted API" is not automatically higher quality on your specific task (a well-evaluated small local model can beat a poorly-prompted frontier model on a narrow job). Decide with a real eval set and a real cost model, not vibes or vendor benchmarks.

---

## Local Training Is a Different Feasibility Question

Everything above this section sizes **inference**. Do not carry those conclusions across to training or on-device adaptation: a device that runs a model comfortably may be nowhere near able to train or fine-tune it. Training amplifies every constraint dimension at once, and the amplification factors are not uniform — energy moves roughly an order of magnitude more than compute does.

Reddi, [*Machine Learning Systems at Scale*, Edge Intelligence, Table 2](https://mlsysbook.ai/vol2/edge_intelligence/edge_intelligence.html), gives planning ranges for how training amplifies on-device inference constraints:

| Constraint dimension | Inference | Training amplification |
|----------------------|-----------|------------------------|
| Memory Footprint | Model weights + single activation map | Weights + full activation cache + gradients + optimizer state — 4–12× increase; forces aggressive compression |
| Compute Operations | Forward pass only | Forward + backward + weight update — "2-3× increase; limits model complexity" |
| Memory Bandwidth | Sequential weight reads | Bidirectional data flow for gradients — "5-10× increase; creates bottlenecks" |
| Energy per Sample | Single inference operation | Multiple gradient steps with convergence — "10-50× increase; requires opportunistic scheduling" |

**Conditions on these numbers — do not quote them stripped of these:**

- The textbook states the factors "assume standard backpropagation without optimizations like gradient checkpointing." Gradient checkpointing explicitly trades compute for memory, so it moves the memory and compute figures in opposite directions; mixed-precision training reduces the bandwidth figure. A stack using either is not described by this table.
- These are **order-of-magnitude planning figures** — Table 2 does not identify a single measured model, hardware, or batch size behind each range. Treat them as a sizing prior that tells you which constraint binds first, not as a benchmark result. Measure on your actual model and device before committing to a training deployment.

**The durable point, independent of the exact multipliers:** local *inference* feasibility does not imply local *training* feasibility, and the binding constraint can change between the two. Inference needs weights and KV cache to fit; training adds activations, gradients, and optimizer state. On battery-powered or passively cooled devices, measure memory, power, and sustained temperature before planning on-demand adaptation.

For practical local adaptation, this is the argument for parameter-efficient methods: LoRA/QLoRA-style adapters shrink the gradient and optimizer-state share of the memory footprint, which is the component the table shows growing. See `references/adaptation-and-packaging.md` for the adaptation and packaging path.
