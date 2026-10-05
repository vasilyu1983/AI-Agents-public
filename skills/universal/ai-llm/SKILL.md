---
name: ai-llm
description: "Adapts LLMs: SFT dataset loss masking, LoRA and QLoRA, full FT vs PEFT, distillation, pruning, tokenizer fragmentation. Use when fine-tuning or compressing a model."
compatibility: Portable core. Works on Claude Code and Codex.
version: "2.3"
last_validated: 2026-09-26
---

# LLM Adaptation

Change a model's weights so it does a task better: supervised fine-tuning (SFT), parameter-efficient fine-tuning (PEFT: LoRA, QLoRA, DoRA), full fine-tuning, distillation and compression recovery, plus the dataset and tokenizer work that decides whether any of it succeeds.

Deciding *whether* to adapt at all (prompt vs thinking vs RAG vs fine-tune vs post-train) is not this skill. Use the single build ladder in [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md#llm-lane-prompt---thinking---rag---fine-tune---post-train-agent-is-a-separate-axis) first, and come here once it says "fine-tune" or "distill".

## When to Use This Skill

- Configuring LoRA or QLoRA: rank, alpha, alpha convention, target modules, learning rate
- Choosing full fine-tuning vs PEFT, or escalating when LoRA plateaus
- Building an SFT dataset: chat templates, prompt-token loss masking, packing, contamination control
- Distilling a large teacher into a smaller student, or recovering quality after pruning
- Diagnosing tokenizer fragmentation, fertility, or glitch tokens on a subset of inputs
- Deciding whether a fine-tune pays back (break-even on volume and stability)

## Scope Boundaries

| Need | Go to |
|---|---|
| Which approach at all; model and provider choice; MoE vs dense | [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md) |
| Preference and RL post-training: RLHF/PPO, DPO, GRPO, RLVR, reward models | [ai-post-training](../ai-post-training/SKILL.md) |
| Eval design, judge calibration, thresholds, benchmark harnesses | [ai-evals](../ai-evals/SKILL.md) |
| Prompts, structured outputs, schema enforcement | [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md) |
| Context assembly and memory | [ai-context-layer](../ai-context-layer/SKILL.md) |
| RAG and agents | [ai-rag](../ai-rag/SKILL.md), [ai-agents](../ai-agents/SKILL.md) |
| Serving, quantization formats, pruning runtime support | [ai-llm-inference](../ai-llm-inference/SKILL.md) |
| Local runs and GGUF packaging | [ai-local-model-ops](../ai-local-model-ops/SKILL.md) |
| Deployment, rollout, monitoring, model/provider migration | [ai-mlops](../ai-mlops/SKILL.md) |
| API cost model, caching, self-host breakeven | [ops-cost-optimization](../ops-cost-optimization/references/ai-api-cost-guide.md) |
| Pretraining, tokenizer building, scaling laws | [ai-pretraining](../ai-pretraining/SKILL.md), [ai-scaling-laws](../ai-scaling-laws/SKILL.md) |
| Multi-GPU parallelism | [ai-distributed-training](../ai-distributed-training/SKILL.md) |
| Hugging Face TRL trainer specifics | the `huggingface-skills:` plugin (external) |

## Default Workflow

1. **Confirm the gap is behavior, not knowledge or reasoning.** Missing facts belong in retrieval and multi-step logic in the thinking budget (see the advisor ladder). Fine-tune for a stable behavior, format, or style gap that survives prompt and RAG fixes.
2. **Build the eval before the dataset.** Hold out a task set by slice, capture a same-seed baseline of the untuned model, and add an out-of-domain forgetting set.
3. **Build the dataset.** Group duplicate and near-duplicate source examples, then assign whole groups to train or eval before augmentation or synthetic generation; check for residual overlap. Apply the model's own chat template, and use the same template at train and at serve (generation prompt and end-of-turn token included): render one example through the training pipeline and through the serving engine and diff the token IDs, because a mismatch raises no error and looks like a fine-tune that did nothing ([§5E](references/dataset-formatting-guide.md#e-chat-sft-loss-on-assistant-turns-packing-stays-inside-examples)). Compute loss on assistant tokens only (`ignore_index=-100` on prompt tokens). Packing must not let attention or loss cross example boundaries. See [dataset-formatting-guide.md](references/dataset-formatting-guide.md).
4. **Start with PEFT.** LoRA or QLoRA on all linear layers; record rank, alpha, alpha convention, target modules, and effective batch (micro × accumulation × world size). Trainable share = Σ r·(d_in + d_out) over adapted matrices ÷ total parameters; compute it for your model instead of quoting a percentage.
5. **Escalate only on evidence.** If LoRA plateaus on a hard, far-from-pretraining domain, follow the escalation order in [fine-tuning-recipes.md](references/fine-tuning-recipes.md#when-full-fine-tuning-instead) and keep the forgetting eval.
6. **Distillation step.** Before any teacher call, confirm the teacher's terms permit training a competing model, and record the licence. Then pick the supervision signal your access gives you (logits, generated text, or rationales) per [advanced-llm-patterns.md](references/advanced-llm-patterns.md#knowledge-distillation-workflow).
7. **Gate the release.** Run the gate on the exact serving artifact and configuration: test the adapter loaded separately if that is how it will serve, or test the merged and quantized artifact if that is the deployment path. A delta that appears only after quantization is not the fine-tune's ([merge and quantize](references/fine-tuning-recipes.md#lora-configuration)). Pick the release checkpoint on the task and forgetting slices; validation loss only ranks checkpoints for early stopping. Compare against the baseline by slice, schema-valid and tool-call rates, and the forgetting set. Hand deployment to [ai-mlops](../ai-mlops/SKILL.md).

## Quick Reference

| Decision | Default | Change when | Avoid |
|---|---|---|---|
| Method | LoRA/QLoRA, all-linear targets | Plateau on a hard domain after rank and DoRA tries → GaLore, then full FT | Jumping to rank 256 |
| Memory | QLoRA when the base does not fit in BF16 | Base fits → plain LoRA | Sizing MoE by active params (all experts load) |
| Multi-GPU | Data parallel when the frozen base fits one GPU | Base does not fit → FSDP / ZeRO-3 ([memory model](../ai-distributed-training/references/fsdp-vs-zero.md#memory-model-comparison)) | Sharding by reflex |
| Loss | Assistant tokens only | Pretraining-style continued training on raw text | Training on system and user tokens |
| Distillation | Sequence KD from teacher outputs | Logit access → soft-label KD; reasoning traces → trace KD | Any teacher whose terms forbid training a competitor |
| Payback | Use the ROI calculator | Volume is high and the domain is stable | Fine-tuning for knowledge that changes |

## Known Traps

- fine-tuning for information that should live in retrieval, or for a reasoning gap that a larger thinking budget closes
- quoting a LoRA parameter percentage instead of computing Σ r·(d_in + d_out) for the actual model
- computing loss on prompt tokens, or packing examples so attention crosses boundaries
- splitting near-duplicate source examples across train/eval, or augmenting before assigning source groups to a split
- distilling from a hosted model whose terms forbid training a competing model
- gating a compressed or tuned model on perplexity; reasoning, schema-valid, and tool-call slices break first
- treating a too-good eval score as success instead of a leakage alarm
- sizing an MoE fine-tune by active parameters, or ignoring router drift toward a few experts

Trainer features, supported losses, and framework maintenance status change often.
1. Check the trainer's own docs for supported methods and losses before promising one (for example, whether a preference loss is built in).
2. Check the model card and `config.json` for architecture facts (layers, hidden size, KV heads, MoE experts) instead of recalling them.
3. Check a framework's repository status before starting new work on it; some fine-tuning libraries have wound down.

## Scripts

This skill ships no scripts. The per-call cost estimator is in [ops-cost-optimization](../ops-cost-optimization/SKILL.md) (`scripts/cost_estimator.py`), and the offline prompt regression runner is in [ai-evals](../ai-evals/SKILL.md) (`scripts/prompt_eval_runner.py`).

## Navigation: References

- **[Fine-Tuning Recipes](references/fine-tuning-recipes.md)**: SFT, instruction tuning, LoRA/QLoRA configuration, PEFT method family, full-FT escalation, multi-GPU and MoE notes, safety data, mid-training, data feedback loops, contamination control
- **[Dataset Formatting Guide](references/dataset-formatting-guide.md)**: instruction, chat, and transformation formats; dataset hygiene; loss masking (`ignore_index=-100`, first EOS unmasked); packing inside example boundaries. `ai-pretraining` delegates SFT formatting here.
- **[Adaptation Patterns](references/advanced-llm-patterns.md)**: task-specific tuning, synthetic data, knowledge distillation (logit, sequence, on-policy, rationale, prune-then-distill, reasoning-trace) with the teacher licence gate, compression checklist, multi-task learning. `ai-architecture-advisor` owns whether to distill; `ai-pretraining` delegates distillation here.
- **[Tokenizer Diagnostics](references/tokenizer-diagnostics.md)**: fertility and parity, glitch and undertrained tokens, domain fragmentation, number tokenization, typo brittleness. Building a BPE tokenizer is [ai-pretraining](../ai-pretraining/references/bpe-tokenizer.md).
- **[Multimodal Patterns](references/multimodal-patterns.md)**: vision, audio, and document workflows. Outside the adaptation scope; kept here until it has an owner.

Moved out of this skill: post-training → [ai-post-training](../ai-post-training/SKILL.md); eval patterns → [ai-evals](../ai-evals/SKILL.md); cost economics → [ai-api-cost-guide](../ops-cost-optimization/references/ai-api-cost-guide.md); deployment, migration, and monitoring → [ai-mlops](../ai-mlops/SKILL.md); the build ladder and model selection → [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md).

## Templates

- **[Fine-Tuning Config](assets/fine-tuning/template-config.md)**: reproducible SFT/LoRA config record
- **[SFT Chat Dataset](assets/fine-tuning/template-sft-dataset.jsonl)** and **[Instruction Dataset](assets/fine-tuning/template-instruction.jsonl)**: minimal record shapes
- **[Data Quality](assets/data-pipelines/template-data-quality.md)**: dedupe, PII, and quality checks for training data
- **[Fine-Tuning ROI Calculator](assets/selection/fine-tuning-roi-calculator.md)**: break-even analysis for an adaptation investment

## External Sources

See [data/sources.json](data/sources.json) for the papers and docs behind the recipes (LoRA, QLoRA, DoRA, rsLoRA, IA³, LoRA-vs-full-FT, distillation) and provider lookup pages for current-fact checks.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
