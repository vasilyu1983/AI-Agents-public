# ai-agents — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Prior version cited an unverifiable '400,000+ Codex PRs in 2 months' stat and a stale '68% mini-swe-agent' figure (now >74%). Replaced with the cited adoption study arXiv:2601.18341; re-check benchmark numbers before quoting.
## Domain Knowledge

- [2026-07-11] MAST (arXiv:2503.13657, NeurIPS 2025) original split: System Design ~41.8%, Inter-Agent Misalignment ~36.9%, Task Verification ~21.3%. A repeated 44.2/32.3/23.5 figure is a different analysis — verify before quoting.
- [2026-07-11] CrewAI Flows added runtime checkpointing (CheckpointConfig + SqliteProvider, ~May 2026): checkpoints Flow-method/Crew-task boundaries only, not mid-ReAct tool loops. Don't promise exactly-once recovery without checking current docs.
## Open Questions

## Consolidated Principles

