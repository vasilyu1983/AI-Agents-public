# Adaptation And Packaging

Use this file when the user wants to go beyond "run a model locally" without jumping straight to full platform engineering.

## Lightweight Adaptation

- Use Unsloth-style workflows when the goal is fast adapter or lightweight fine-tuning iteration on constrained hardware.
- Keep adaptation evals small but real. A local benchmark without task-level quality checks is not enough.

## Packaging Rule

- Use portable packaging such as llamafile when demos, offline sharing, or low-friction distribution matter.
- Keep runtime choice, model artifact, and prompt/eval version recorded together so demos remain reproducible.

## Handoff Rule

- Stay in this skill while the problem is local runtime choice, portability, or constrained adaptation.
- Hand off to `ai-llm-inference` for serving design and to `ai-llm` for broader training strategy.
