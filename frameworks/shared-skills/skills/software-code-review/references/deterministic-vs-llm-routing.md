# Deterministic-vs-LLM Routing for AI-Assisted Review

`automation-tools.md`'s Recommendation Framework answers a team-level question — which tool to adopt, in what order. This file answers a narrower, per-diff question: once a review tool exists, which parts of "does this file get reviewed, and how" should be decided by plain pattern-matching instead of a model call. Use it when building, configuring, or evaluating an AI review integration, not as review-execution guidance for a human reviewer.

**Attribution**: Patterns from [alibaba/open-code-review](https://github.com/alibaba/open-code-review), commit `f44821d9aa0993e8e3cf90ae3fe12e733e045b15`, `pages/src/content/docs/en/architecture.md` and `pages/src/content/docs/en/review-rules.md`. Apache-2.0. Extracted 2026-08-09. Recorded in `docs/research/2026-08-09-skill-code-review-career-scan.md`. Concepts extracted and rewritten below; no upstream text copied verbatim.

## Table of Contents

- [Gate Before You Generate](#gate-before-you-generate)
- [Size-Gated Planning Pass](#size-gated-planning-pass)
- [Self-Refutation Pass on the Output](#self-refutation-pass-on-the-output)
- [Composing With Existing Guidance](#composing-with-existing-guidance)

## Gate Before You Generate

Before any file reaches an LLM call, run it through a small, ordered, inspectable filter — every decision in the filter should be answerable by a human reading the rule, with no model involved:

1. **Binary files** — drop.
2. **User-defined exclude patterns** — drop. Highest precedence: an explicit exclude always wins over an explicit include.
3. **User-defined include patterns** — if defined and matched, keep the file immediately and skip the remaining default-pattern checks below.
4. **Unsupported extension** — drop if the file type isn't in your reviewable-extension allowlist.
5. **Default noise patterns** — drop generated/test-glob matches your defaults already exclude (e.g. `**/*_test.go`, `**/*.test.{js,ts,tsx}`, `**/__tests__/**`) unless a user include already saved the file at step 3.

Two design details worth keeping if you build or configure something similar:

- **Expose the filter as a standalone, zero-cost command.** A `--preview`-style flag that runs the full gate chain and reports what would be included/excluded, without spending a single model token, lets a team debug and tune its filter rules cheaply, and gives reviewers a place to check "why didn't this file get reviewed" without re-running the whole pipeline.
- **Precedence order matters more than the individual rules.** User-exclude beating user-include beating extension-allowlist beating default-noise-patterns is the specific ordering that lets a team override a bad default (via include) while still being able to force-drop a false-positive-prone file (via exclude) even if it would otherwise match. Copying the rules without the precedence order reproduces the bugs, not the design.

This is a different layer from `automation-tools.md`'s Recommendation Framework (native controls → deterministic scanners → AI bot → merge queue/stacking), which sequences *tool adoption* for a team. This gate operates *inside* whichever AI review tool is already adopted, deciding per-diff what reaches the model at all. The two compose: adopt tools per the Recommendation Framework, then apply this gate inside the AI-review step once it exists.

Treat rule *selection* (which checklist or ruleset applies to a surviving file) as a second, equally deterministic step — a simple extension-to-ruleset lookup table, not a model decision. If your team maintains per-language or per-framework review rule docs, resolve which one applies by glob match before the file enters any LLM loop, the same way you'd resolve which linter config applies.

## Size-Gated Planning Pass

For files that clear the gate above, a second deterministic decision worth calibrating explicitly: does this diff need an extra planning/reasoning pass before the main review runs, or does it go straight into the review loop?

One reference calibration point: gate on total changed lines (insertions + deletions) per file, with the model skipping a separate planning call below the threshold and making exactly one extra read-only planning call (tools stripped, so the model can only produce a checklist, not act) at or above it. Alibaba's own number for their context is **50 changed lines** — present that as their calibration point for their codebase and review volume, not a universal threshold. Tune the actual number against your own diff-size distribution and false-negative rate; a team with mostly small config-file diffs and a team with mostly large service-layer diffs will land on different numbers.

This is a different axis from the existing rubber-stamp-detection heuristic in `SKILL.md` and the 200-400 LOC pacing data in [large-pr-review-strategies.md](large-pr-review-strategies.md): those size figures flag when a *human* reviewer's approval speed looks suspicious for the diff size. This threshold instead gates whether the *AI reviewer's own process* gets an extra reasoning phase before generating comments — a process-shape decision, not a suspicion heuristic. Keep them conceptually separate: a diff can be small enough to skip AI planning while still being exactly the size a human should slow down and read carefully, and vice versa.

## Self-Refutation Pass on the Output

Once the main review pass finishes generating findings, consider a second, independent LLM call whose only job is to re-check those findings against the diff and remove ones that are provably wrong — not a retry of generation, and not a confidence score attached at generation time, but a distinct pass that receives the full diff plus the accumulated findings and is asked to falsify them.

Design details that matter if you build this:

- **It runs after generation, over the output, not during.** The generating pass should not be asked to self-critique inline; a separate call with only the diff and the finding list as input has less anchoring toward the finding's own framing.
- **Fail open, not closed.** If the self-refutation call itself errors, log it and keep the original findings rather than discarding them — the fallback on a broken false-positive filter should be "human sees the unfiltered list," not "human sees nothing."
- **This does not replace human verification.** `SKILL.md`'s AI-Assisted Review Rules already state that AI findings are advisory until confirmed and that benchmark/security/framework claims need live verification. A self-refutation pass reduces obvious false positives before a human looks at them; it is not a substitute for the human check, and a finding surviving this pass is not thereby "verified."

This is a distinct mechanic from the `adversarial-review-protocol.md` stripped-context handoff: that protocol governs how a *second, independently-launched reviewer* (fresh context, adversarial framing, human-facing precedence buckets for reconciling findings) checks a *human/orchestrator's decision*. This section is narrower — one AI pass filtering its own prior pass's output for provable errors before a human ever sees the list. Use the adversarial protocol for "is this decision actually right"; use this for "did the AI reviewer just hallucinate a comment that doesn't match the diff."

## Composing With Existing Guidance

- Apply the pre-review gate (this file) before `automation-tools.md`'s Recommendation Framework tools ever see a diff.
- Apply the size-gated planning pass as a refinement inside whatever AI review step already exists — it is orthogonal to the human-facing 200-400 LOC guidance in [large-pr-review-strategies.md](large-pr-review-strategies.md).
- Apply the self-refutation pass before findings reach a human reviewer, then apply `SKILL.md`'s AI-Assisted Review Rules and, for higher-stakes decisions, [adversarial-review-protocol.md](adversarial-review-protocol.md) on top.
