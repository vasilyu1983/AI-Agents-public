# ai-context-layer — Learnings

## Patterns That Work

- [2026-06-28] Store a paused/retired surface as status:'paused' with stale:true edges instead of deleting it, so the hub records the contract still exists and the backend honors it while no live consumer remains.
- [2026-07-11] July 2026 audit: Anthropic's flagship lineup turned over twice in one quarter (Opus 4.8 May 28, then Claude Fable 5 / Mythos 5 / Sonnet 5 GA June 9–30), and minimum-cacheable-prompt-length now varies 512–4,096 tokens *within* the current Anthropic lineup alone — any skill content that states a single fixed token-budget or cache-prefix number per vendor (not per model) is already wrong; always add a per-model verify-live caveat instead of a hardcoded figure. Also corrected a stale citation: the Mem0/LOCOMO paper (arXiv:2504.19413) is April 2025 (ECAI 2025), not 2026 — the wrong year had propagated into both sources.json and agent-memory-benchmarks.md.
## Mistakes to Avoid

## Domain Knowledge

## Open Questions

## Consolidated Principles

