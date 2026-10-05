# ai-distributed-training — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] Rubin NVL72 entered production ~June 2026 (Blackwell now mainstream, not newest); Muon confirmed by primary sources for DeepSeek-V4 (2606.19348) and GLM-5 (2602.15763), not just Kimi K2.
- [2026-09-25] Audit correction: FSDP1 has no deprecation notice in the PyTorch 2.11 or 2.14 docs (only `FSDP.state_dict_type()` is marked as being deprecated), so the skill now says "prefer FSDP2, check the release notes". The Muon "1.3–1.5×" figure had no source; the skill now cites Moonlight (~2×) and Wen et al. 2509.02046 (1.4× at 0.1B falling to 1.1× at 1.2B). The 380 GB activation example assumed no FlashAttention (36.5 GB with it). Hardware-tier dates were replaced by a lookup step.
## Open Questions

## Consolidated Principles

