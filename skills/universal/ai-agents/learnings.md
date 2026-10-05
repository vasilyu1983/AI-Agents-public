# ai-agents — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Prior version cited an unverifiable '400,000+ Codex PRs in 2 months' stat and a stale '68% mini-swe-agent' figure (now >74%). Replaced with the cited adoption study arXiv:2601.18341; re-check benchmark numbers before quoting.
## Domain Knowledge

- [2026-07-11] MAST (arXiv:2503.13657) category split is not settled in this skill: 41.8/36.9/21.3 (System Design / Inter-Agent Misalignment / Task Verification) is often quoted as the original split, and summing the per-mode rates in a later arXiv revision reportedly gives 44.2/32.3/23.5. Neither is re-verified here; sum the per-mode table in the revision you cite before quoting. The venue is unverified.
- [2026-09-25] Correction: MAST v3 (Oct 2025) Figure 1 reports 44.0 / 32.15 / 23.85 over 1,642 traces, so the ~44/32/24 split above is the current paper. Quote with the version.
- [2026-07-11] CrewAI Flows added runtime checkpointing (CheckpointConfig + SqliteProvider, ~May 2026): checkpoints Flow-method/Crew-task boundaries only, not mid-ReAct tool loops. Don't promise exactly-once recovery without checking current docs.
## Open Questions

## Consolidated Principles

