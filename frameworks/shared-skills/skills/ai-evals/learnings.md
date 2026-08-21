# ai-evals — Learnings

## Patterns That Work

- [2026-06-10] Classify baseline failures into named families (grader false-positive vs routing vs real model failure) before tuning; non-overlapping edit families let a plain run-diff attribute lift per edit without CIs.
- [2026-06-06] For quality tuning, optimize answer-pass as auditor-clean AND intent-satisfied; clean-rate alone can hide wrong-answer regressions after safety fixes.
- [2026-06-06] After a prompt or routing patch, recapture only affected cohorts for speed, then render a full report from the active corpus before claiming a matrix-wide result.
## Mistakes to Avoid

- [2026-08-14] Benchmark comparison must fail when current or baseline task-mode keys are missing, because denominator drift can hide a routing regression.
- [2026-07-08] Fail-closed judge defaults invert on planted-bad TNR gates (which expect 'fail') — a dead judge looks calibrated. Use a third 'error' state satisfying neither gate, and calibrate both directions (TNR + planted-good TPR).
- [2026-06-10] ~40% of a first paid baseline's 'model failures' were grader phrase-list brittleness — store rawReply so grader fixes re-grade offline instantly, no recapture spend.
- [2026-06-06] For prompt-tree evals, canonical fingerprints must cover every routed prompt branch being tuned; a single known-time canonical prompt missed unknown-birth-time prompt edits and let stale captures look current.
- [2026-06-05] For tier-aware prompt evals, render the canonical prompt with the same tier being hashed; adding tier text to hash material while rendering a default prompt lets paid/free prompt drift escape stale-corpus detection.
## Domain Knowledge

- [2026-07-11] Web-verification pass (July 2026): all `data/sources.json` arXiv
  citations spot-checked (2306.05685, 2404.18796, 2405.01535, 2404.04475, and
  the 2026-06-04 MDP-GRPO entry 2606.06058) matched real authors/titles/claims —
  no fabrications found. promptfoo's OpenAI acquisition (Mar 9, 2026) and
  DeepEval v4.0.0 (May 8, 2026) both confirmed current. OTel GenAI semantic
  conventions did move to a dedicated `semantic-conventions-genai` repo in
  2026 — added a pointer in framework-integration.md. One passage in
  safety-redteam-eval.md pinned specific model names/versions (a real, verified
  provider architecture) inside evergreen guidance — generalized it to
  vendor-neutral language per the skill's no-model-version-pin rule, since the
  pattern (classifier-gated fallback routing) outlives any specific model pair.

## Open Questions

## Consolidated Principles

