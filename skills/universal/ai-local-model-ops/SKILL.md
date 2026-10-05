---
name: ai-local-model-ops
description: "Runs local and self-hosted LLMs with Ollama, LM Studio, MLX, llama.cpp, and Open WebUI. Use when choosing GGUF quants, sizing VRAM, or running models privately."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-09-25
---

# Local Model Operations

Use this skill to choose and operate local or self-hosted LLM workflows when privacy, offline access, or low-friction experimentation matter more than large-cluster serving.

This skill covers:

- local runtime choice for laptops, workstations, and small self-hosted setups
- team-facing local or private chat surfaces
- single-binary or minimal-dependency model packaging
- lightweight adaptation paths before full training or cluster-scale serving
- evaluation and escalation rules before a local stack becomes a product dependency

## Quick Reference

| Need | Default path | Notes |
|------|--------------|-------|
| Run a local model quickly | Ollama | Lowest-friction day-0 local runtime for experiments and private workflows |
| Share a self-hosted chat UI | Open WebUI | Best fit when a team needs a ChatGPT-like local or private interface |
| Ship a no-install demo or portable binary | llamafile | Useful for single-file distribution and low-ops delivery |
| Apple Silicon on-device inference at framework level | MLX (mlx-lm) | Primary path for Metal-native inference and LoRA fine-tune on Mac; verify at https://github.com/ml-explore/mlx-lm |
| GUI model browser and switcher (non-technical users) | LM Studio | Supports GGUF and MLX; good for rapid model comparisons |
| Windows / enterprise SDK-first local inference | Microsoft Foundry Local | Curated Microsoft catalog; SDK + REST; verify at https://learn.microsoft.com/en-us/ai/foundry-local |
| CPU-only box, single-board computer, phone, or browser | llama.cpp (GGUF), OpenVINO, ONNX Runtime, MLC-LLM | See [references/edge-cpu-optimization.md](references/edge-cpu-optimization.md); decode speed is bandwidth-bound, so stay small |
| Fine-tune or adapt cheaply | Unsloth + `../ai-llm/SKILL.md` | Good for lightweight adaptation, not a substitute for full training ops |
| Optimize throughput or production serving | `../ai-llm-inference/SKILL.md` | Use this skill for local ops; use `ai-llm-inference` for deeper serving engineering |

See [references/desktop-runtime-landscape.md](references/desktop-runtime-landscape.md) for a detailed Ollama / LM Studio / Foundry Local comparison.

## Local vs Hosted API: Judgment, Not Reflex

Do not default to "local" just because privacy or cost was mentioned once. Decide with a real eval set and a real cost model:

- Local tends to win on data residency or offline requirements, steady traffic that amortizes hardware cost, latency-sensitive tasks proven faster on the target machine, and narrow tasks where a locally runnable model meets the measured quality bar.
- Hosted API tends to win on frontier-tier reasoning or long-context needs that no locally-runnable model size covers yet, spiky/low-volume traffic, or when local ops overhead (drivers, quant regressions, capacity planning) would cost more engineering time than the API bill.
- Frontier-scale open-weight models (MoE releases with hundreds of billions of total parameters) do not fit on a single consumer GPU or a single 80 GB card at usable quant — "open-weight" does not mean "runs on your laptop." Run the sizing formula before promising local feasibility.
- Local *inference* feasibility does not imply local *training* or fine-tuning feasibility. Training amplifies memory, bandwidth, and especially energy per sample well beyond inference, so the binding constraint often shifts from VRAM capacity to thermal/power budget. See [references/model-sizing-matrix.md](references/model-sizing-matrix.md#local-training-is-a-different-feasibility-question) before promising on-device adaptation.

See [references/model-sizing-matrix.md](references/model-sizing-matrix.md#local-vs-api-the-real-tradeoff) for the full tradeoff and the sizing formula.

## Default Workflow

1. Define the real constraint first: privacy, offline use, cost ceiling, hardware ceiling, or demo portability.
2. Pick the runtime or UI layer that matches that constraint.
3. Pin model IDs, quantization choice, and prompt/eval set before broader rollout.
4. Decide whether the stack is only for local use or will become part of a product or team workflow.
5. If it needs stronger serving, routing, or monitoring, hand off to the adjacent skills instead of stretching a local-first setup too far.

## Operational Rules

- Keep model IDs and quantization choices explicit and versioned.
- Treat local and self-hosted endpoints as sensitive services, not casual defaults for internet exposure.
- Measure quality on a small real eval set before swapping local models into a user-facing workflow.
- Separate runtime selection from product integration. Running a model locally is not the same thing as shipping a good AI feature.

## Hardware-Fit Gate

Size before you download: weights ≈ total params × bits-per-weight / 8, plus KV cache at your real context, plus runtime overhead. MoE models need memory for their **total** parameters; active parameters only predict speed. Take params from the model card and bpw from the actual quant file, then compare with usable memory (on Apple Silicon, the GPU-addressable share of unified memory). Formula, worked examples, and memory classes: [references/model-sizing-matrix.md](references/model-sizing-matrix.md).

Test the exact model artifact, quantization, context distribution, concurrency, and tool or schema contract on the target machine. Record peak resident memory, prompt and generation throughput, p95 time to first token, sustained temperature or throttling behavior, output-quality regressions, and recovery after cancellation. Approve local operation only when the full workload fits with headroom and a named fallback exists for overload or unsupported requests. A one-prompt demo is discovery evidence, not a capacity result.

## Known Traps

- Treating a laptop prototype as proof that a workflow is production-ready. Latency, uptime, auth, and observability requirements change immediately once real users appear.
- Leaving model IDs, quant levels, and system prompts implicit. Local stacks drift quickly when operators rely on tags like `latest`.
- Exposing Ollama, Open WebUI, or ad hoc reverse proxies without an explicit threat model and access controls. Ollama binds to loopback by default and its API has no auth; binding `0.0.0.0` must be a deliberate choice behind an authenticating proxy, firewall, or VPN. Check `ollama serve --help` and the Ollama FAQ for current defaults rather than recalling them.
- Assuming a polished chat UI solves governance. UI convenience does not replace logging, retention policy, or approval paths.
- Using lightweight local adaptation as a substitute for evaluation discipline. Faster iteration is useful only if the eval loop is real.
- Using deprecated vLLM engine features or flags from old tutorials — use the current engine and check the vLLM docs for current flags.
- Citing vendor speedup figures (e.g., Microsoft Foundry Local vs cloud) as neutral benchmarks — always measure on your own workload.
- Assuming speculative decoding helps at high concurrency — the benefit is concentrated at batch size 1.
- Sizing an MoE model by its active parameters — every expert has to be resident somewhere (VRAM, unified memory, or offloaded to RAM).
- Running NPU inference without confirming the accelerator is being used — fallback to CPU/GPU is silent in some runtimes.

## Common Anti-Patterns

- Installing several local runtimes at once before deciding which constraint actually matters: privacy, portability, cost ceiling, or offline access.
- Treating local models as drop-in replacements for hosted models without rechecking tool use, structured outputs, and long-context behavior.
- Shipping a team workflow on consumer hardware with no capacity envelope, backup path, or restart procedure.
- Using "local" as the only justification for a stack choice when a small self-hosted or managed setup would be operationally safer.

## Escalation Boundaries

Use adjacent skills when:

- you need cluster-scale serving or throughput tuning -> [ai-llm-inference](../ai-llm-inference/SKILL.md)
- you need full fine-tuning strategy, dataset design, or evaluation -> [ai-llm](../ai-llm/SKILL.md)
- you need product UX, streaming chat, or structured output in an app -> [software-ai-integration](../software-ai-integration/SKILL.md)
- you need deployment, monitoring, or operational governance -> [ai-mlops](../ai-mlops/SKILL.md)

## Navigation

**References**
- [references/runtime-selection.md](references/runtime-selection.md) - runtime, UI, and packaging choice rules
- [references/desktop-runtime-landscape.md](references/desktop-runtime-landscape.md) - Ollama vs LM Studio vs Microsoft Foundry Local: detailed comparison, decision heuristic, anti-patterns
- [references/adaptation-and-packaging.md](references/adaptation-and-packaging.md) - lightweight adaptation, portable delivery, and evaluation handoff rules
- [references/model-sizing-matrix.md](references/model-sizing-matrix.md) - sizing formula (weights + KV + overhead; MoE by total params), memory classes, bandwidth-bound decode speed, Apple Silicon and discrete-GPU notes, local vs API, why local training feasibility differs from local inference feasibility
- [references/quantization-format-table.md](references/quantization-format-table.md) - GGUF Q4_K_M/Q5_K_M/Q8_0, AWQ, GPTQ, FP8, EXL2; KV-cache quantization; speculative decoding; NPU/accelerator tier; decision tree
- [references/small-model-tier-table.md](references/small-model-tier-table.md) - small-model tiers by parameter count with footprints, family traits, selection heuristic (look up the current release)
- [references/edge-cpu-optimization.md](references/edge-cpu-optimization.md) - CPU-only, single-board, phone, and browser inference: stack choice, making your own GGUF, CPU tuning, benchmark and quality gate
- [data/sources.json](data/sources.json) - local-model tooling sources from the curated repo list

**Templates**
- [assets/templates/ollama-setup-recipe.md](assets/templates/ollama-setup-recipe.md) - end-to-end Ollama install, model pull, OpenAI-compatible API usage, Modelfile pinning
- [assets/templates/openwebui-deployment-recipe.md](assets/templates/openwebui-deployment-recipe.md) - Docker / Compose deployment of Open WebUI over Ollama, env vars, reverse proxy, upgrades

**Related Skills**
- [../ai-llm-inference/SKILL.md](../ai-llm-inference/SKILL.md) - serving, quantization, routing, and throughput tuning
- [../ai-llm/SKILL.md](../ai-llm/SKILL.md) - full LLM lifecycle and fine-tuning strategy
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md) - deployment, monitoring, and governance
- [../software-ai-integration/SKILL.md](../software-ai-integration/SKILL.md) - product integration and AI UX

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
