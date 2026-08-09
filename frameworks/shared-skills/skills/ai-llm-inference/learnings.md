# ai-llm-inference — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Audit found fabricated-precision facts: a KV-cache example was arithmetically wrong (80GB vs actual 100GB); an FA-3 table cited invented TFLOPs vs the paper's real 75%/740 TFLOPs. Re-derive math, diff cited numbers vs sources.
## Domain Knowledge

- [2026-07-11] vLLM's W4A4 NVFP4 recipe (llm-compressor) needs Blackwell (SM100+) for full activation quantization; older GPUs silently fall back to weight-only under the same recipe.
## Open Questions

## Consolidated Principles

