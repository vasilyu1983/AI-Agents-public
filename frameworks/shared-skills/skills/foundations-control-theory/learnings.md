# foundations-control-theory — Raw Learnings

Append-only. Consolidated periodically into `learnings.consolidated.md` via `agents-skills-feedback-loop/scripts/consolidate.py`.

- 2026-07-11: Deep audit (July 2026 pass) verified all 15 arXiv/DOI citations in `data/sources.json` by fetching each paper directly; found one real citation error — the ISS/agentic-control paper (arXiv:2605.03034) was attributed to "Iyer et al." but the actual first author is Prinos (Prinos, Brush, Denton, Wang, Knox, Antani, Foltz, Villaseñor); corrected in SKILL.md and sources.json. Also found two papers cited in `12-deepc-behavioral.md` (Daráš et al. 2026 arXiv:2604.00524; de Jong et al. 2025 arXiv:2512.14535) that were missing from the structured `data/sources.json` source list — added them. Lesson: when a reference file cites a paper inline, always cross-check it exists in `data/sources.json` too, since drift between the two is where fabricated or misattributed citations hide longest.
