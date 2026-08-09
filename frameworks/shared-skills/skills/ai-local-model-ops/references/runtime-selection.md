# Runtime Selection

Use this file when the user needs help choosing a local-model operating mode.

## Fastest Path

- Use Ollama for the fastest route from zero to a working local model.
- Use Open WebUI when multiple people need a persistent chat surface on top of local or self-hosted models.
- Use llamafile when portability and low installation friction matter more than ecosystem breadth.
- Use MLX when the machine is Apple Silicon and the goal is on-device inference or fine-tuning at the framework level (not just daemon + model).

## Selection Rule

| Need | Best fit |
|------|----------|
| Quick local experimentation | Ollama |
| Self-hosted conversational UI | Open WebUI |
| Portable executable distribution | llamafile |
| Lightweight adaptation on constrained hardware | Unsloth |
| Apple Silicon on-device inference / fine-tune at the framework level | MLX |
| GUI-driven desktop runtime (non-technical users, easy model switcher) | LM Studio |
| SDK / programmatic local model calls from Windows or Linux dev machine | Microsoft Foundry Local |

See [desktop-runtime-landscape.md](desktop-runtime-landscape.md) for a detailed comparison of Ollama, LM Studio, and Microsoft Foundry Local.

## Do Not Overextend

- If the stack needs scale, routing, advanced observability, or production SLOs, move to `ai-llm-inference` or `ai-mlops`.
- If the real problem is app UX rather than runtime setup, move to `software-ai-integration`.
