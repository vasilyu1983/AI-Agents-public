# Adaptation And Packaging

Use this file when the user wants to go beyond "run a model locally" without jumping straight to full platform engineering.

## Lightweight Adaptation

- Use Unsloth-style workflows when the goal is fast adapter or lightweight fine-tuning iteration on constrained hardware.
- Use LLaMA-Factory when the goal is breadth without code — its Gradio WebUI (LLaMA Board) covers SFT/DPO/KTO/ORPO and 2–8-bit QLoRA across 100+ models including VLMs. For framework tradeoffs see `ai-llm` → fine-tuning-recipes.md, "Fine-tuning framework selection".
- Do not start new work on torchtune — its development wound down in 2025 (a migration, not abandonment: the successor lane moved through torchforge toward torchtitan and is still shifting). Treat the PyTorch-native fine-tuning lane as unstable until it settles.
- Keep adaptation evals small but real. A local benchmark without task-level quality checks is not enough — see `ai-evals` for harness setup and metric interpretation.

## Packaging Rule

- Use portable packaging such as llamafile when demos, offline sharing, or low-friction distribution matter.
- Keep runtime choice, model artifact, and prompt/eval version recorded together so demos remain reproducible.

## Handoff Rule

- Stay in this skill while the problem is local runtime choice, portability, or constrained adaptation.
- Hand off to `ai-llm-inference` for serving design and to `ai-llm` for broader training strategy.
