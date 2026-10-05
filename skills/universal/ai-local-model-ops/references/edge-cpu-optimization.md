# Edge and CPU Inference

Rules for running LLM inference on CPU-only machines, single-board computers, phones, and browsers. Quant-format choice lives in [quantization-format-table.md](quantization-format-table.md); memory and speed sizing in [model-sizing-matrix.md](model-sizing-matrix.md). Multi-user server deployment (containers, autoscaling, serverless) belongs to [../../ai-llm-inference/SKILL.md](../../ai-llm-inference/SKILL.md).

## Table of Contents

- [When CPU or Edge Inference Fits](#when-cpu-or-edge-inference-fits)
- [Stack Selection](#stack-selection)
- [Making Your Own GGUF](#making-your-own-gguf)
- [CPU Tuning](#cpu-tuning)
- [Device Classes](#device-classes)
- [Benchmark and Quality Gate](#benchmark-and-quality-gate)
- [Troubleshooting](#troubleshooting)
- [Primary Sources](#primary-sources)

## When CPU or Edge Inference Fits

- No GPU is available (edge devices, embedded systems, locked-down laptops).
- Traffic is low and latency-tolerant, so cheaper CPU capacity beats an idle GPU.
- Data must stay on the device.

**Expect a bandwidth ceiling.** CPU decode is memory-bandwidth-bound: tokens/sec ≲ memory bandwidth ÷ weight bytes read per token (see [model-sizing-matrix.md](model-sizing-matrix.md#throughput-decode-is-bandwidth-bound)). Low-bit quantization (4-bit class) is what makes CPU inference usable, and small models (nano to mid tier in [small-model-tier-table.md](small-model-tier-table.md)) are the realistic range. Do not plan real-time, high-throughput, or large-model workloads on CPU without measuring first.

## Stack Selection

| Stack | Pick it for | Format |
|-------|-------------|--------|
| llama.cpp (or Ollama / LM Studio on top of it) | General CPU inference, widest model coverage, ARM and x86 SIMD | GGUF |
| OpenVINO (via `optimum-intel`) | Intel CPUs, iGPUs and NPUs where Intel-specific kernels matter | OpenVINO IR (INT8/INT4 weight compression) |
| ONNX Runtime (via `optimum`) | One model artifact across Windows/Linux/macOS/ARM, cloud-to-edge consistency | ONNX (dynamic INT8 quantization) |
| MLC-LLM | Phones (iOS/Android GPU via Metal/Vulkan) and WebGPU | MLC-compiled model libraries |
| Transformers.js / WebGPU runtimes | In-browser inference with no install | ONNX weights; WebGPU with WASM fallback |

Export paths (replace `<hf-model-id>`; check each tool's `--help` for current options):

```bash
optimum-cli export openvino --model <hf-model-id> --task text-generation --weight-format int4 <out-dir>
optimum-cli export onnx --model <hf-model-id> --task text-generation-with-past <out-dir>
```

Install commands and package names for MLC-LLM and the browser runtimes change often — take them from the project docs, not from memory.

## Making Your Own GGUF

Prefer a pre-quantized GGUF from a maintained publisher when one exists. To make your own, conversion and quantization are two separate steps — the converter does **not** produce K-quants:

```bash
# 1. Convert HF safetensors to a full-precision GGUF (outtype f16 or bf16)
python convert_hf_to_gguf.py <hf-model-dir> --outtype f16 --outfile model-f16.gguf

# 2. Quantize to the target type
llama-quantize model-f16.gguf model-Q4_K_M.gguf Q4_K_M
```

Check `python convert_hf_to_gguf.py --help` and `llama-quantize --help` for the currently accepted types. Validate the quantized file against the full-precision one (see [Benchmark and Quality Gate](#benchmark-and-quality-gate)).

## CPU Tuning

- **Threads:** start at the number of physical cores, not hardware threads; oversubscription causes contention. `os.cpu_count() // 2` only approximates physical cores on 2-way SMT parts — read the real count (`lscpu`, `sysctl hw.physicalcpu`). Sweep a few values on your workload; for ONNX Runtime set `intra_op_num_threads` and keep `inter_op_num_threads` low.
- **SIMD:** confirm the CPU's vector extensions (AVX2, AVX-512, AMX on x86; NEON on ARM) with `lscpu | grep -i flags` or `sysctl -a | grep machdep.cpu.features`, and build llama.cpp for the host CPU. Build options (native CPU, BLAS, Metal, Vulkan, CUDA) are named in the llama.cpp build docs — take the current option names from there.
- **BLAS:** a BLAS backend (OpenBLAS, Intel MKL, Apple Accelerate) mainly speeds prompt processing; measure before and after rather than assuming a multiplier.
- **Memory residency:** lock the model in RAM (`use_mlock` / `--mlock`) when swapping would otherwise evict it; memory-map (`use_mmap`) for fast cold starts. Some sandboxes and serverless platforms forbid `mlock`. Huge pages can help large models on Linux.
- **Batch size:** a larger prompt batch (`n_batch`) speeds prefill up to memory limits; it does not raise single-stream decode speed.
- **Context:** reduce `n_ctx` to what you need — KV cache is often what pushes a small device over its RAM limit.

## Device Classes

- **Single-board computers (e.g. Raspberry Pi class, ARM Cortex-A):** nano or small tier at 4-bit class quant, short context (around 1k tokens), threads = cores. Treat 7B-class models as a stretch that needs measurement.
- **Phones:** MLC-LLM (Metal on iOS, Vulkan/OpenCL on Android) or the platform's own on-device runtimes; stay in the nano–small tier and budget for thermal throttling on sustained generation.
- **Browsers:** WebGPU where available, WASM fallback otherwise; model download size is the first UX cost — prefer nano/small models and cache the weights.
- **Laptops/desktops without a discrete GPU:** llama.cpp/Ollama with GGUF; unified-memory Apple Silicon behaves differently — see [model-sizing-matrix.md](model-sizing-matrix.md#hardware-specific-notes).

## Benchmark and Quality Gate

- Measure prompt-processing (prefill) and generation (decode) tokens/sec separately, with llama.cpp's benchmark tooling or the timing summary your runtime prints, on the target device at the real context length.
- Compare the quantized model with its full-precision baseline on your own task prompts: factual correctness, coherence, instruction following, and structured-output validity.

Checklist:

- [ ] Quant type chosen from the format table and validated against the FP16/BF16 baseline
- [ ] Threads tuned to physical cores and swept
- [ ] SIMD / BLAS / accelerator backend confirmed in the build
- [ ] Prompt batch size tested
- [ ] Memory residency set (mlock/mmap) where the platform allows
- [ ] Context window sized to fit RAM with the KV cache counted
- [ ] Prefill and decode tokens/sec measured on the target device
- [ ] Thermal behaviour checked under sustained load (phones, SBCs, fanless laptops)

## Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| Slow generation | Thread count too high or low; build not using the CPU's SIMD | Sweep threads; rebuild for the host CPU; use a smaller model or lower-bit quant |
| Model does not fit in RAM | Weights + KV at your context vs free RAM | Lower-bit quant (e.g. Q4 → Q3), shorter context, smaller model |
| Poor quality at 3–4 bit | Quant type (plain `Q4_0` vs K-quant) | Use a K-quant; move up to Q5_K_M / Q6_K for critical use |
| Crashes on ARM | Binary built without NEON or for the wrong target | Rebuild for the device; reduce batch size and context |

## Primary Sources

- llama.cpp: https://github.com/ggml-org/llama.cpp
- GGUF specification: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
- OpenVINO: https://docs.openvino.ai
- ONNX Runtime: https://onnxruntime.ai/docs/
- MLC-LLM: https://llm.mlc.ai/
