# Adversarial Review Protocol: Stripped-Context Handoff

**Attribution**: Pattern from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), commit `7676817`, `skills/doubt-driven-development/SKILL.md`. MIT license. Recorded 2026-08-09 in `docs/research/2026-08-09-skill-addyosmani-agent-skills-scan.md`.

**Relationship to `agents-subagents`**: the round cap and escalation-at-the-cap mechanics for a review-fix loop already live in [`agents-subagents/references/control-theory-applied.md` § P4a](../../agents-subagents/references/control-theory-applied.md). This file does not restate P4a — it covers what P4a does not: how to select and package the thing handed to the reviewer so the review itself isn't biased, and how to reconcile what comes back. Use P4a for "when does the loop stop and what happens at the cap." Use this file for "what does the reviewer actually receive, and how are its findings triaged."

## When to Trigger

Before a non-trivial decision stands as final, not for every change. Trigger on:

- Branching logic with more than one plausible interpretation of the requirement.
- A change that crosses a module or service boundary.
- A property the compiler/type system cannot verify (an invariant, an ordering guarantee, a concurrency assumption).
- Irreversible blast radius (data migration, public API shape, safeguarding-relevant logic, anything expensive to undo post-merge).

Skip it for mechanical, single-interpretation changes — the protocol's cost (a second review pass) should be spent where a wrong call is expensive, not on every diff.

## The Handoff: Never Pass the Claim

The orchestrator (the agent that just made the decision) first states the **CLAIM** explicitly to itself — "this migration is safe under concurrent writes because the backfill runs inside the same transaction as the NOT NULL constraint." That CLAIM is then deliberately **not** included in what the reviewer receives.

What the reviewer gets instead:

- **ARTIFACT** — the actual code, config, or diff under review.
- **CONTRACT** — the requirement or invariant the artifact is supposed to satisfy, stated as a checkable property, not as a defense of the approach taken.

Stripped of the orchestrator's own reasoning, the reviewer cannot anchor on "the author already thinks this is fine" — anchoring bias is the specific failure mode this avoids. A reviewer handed the CLAIM alongside the artifact tends to look for confirmation; a reviewer handed only the artifact and the contract has nothing to confirm and must independently derive whether the artifact satisfies the contract.

This is a sharper version of "get a second opinion": the general principle says seek review; this mechanic says the second opinion is worthless if it was primed with the first opinion's conclusion.

## The Reviewer's Instructions

Launch the reviewer in a fresh context (no memory of the orchestrator's session) with an explicitly adversarial framing — find what is wrong with this artifact against this contract; do **not** validate it. A reviewer told to "check this over" defaults to a confirmation posture; a reviewer told to find what's wrong defaults to an adversarial one. The instruction should name the adversarial posture directly rather than relying on "be thorough."

## Reconciling Findings: Fixed Precedence, Re-Read, Never Rubber-Stamp

The orchestrator does not accept or dismiss reviewer findings by reading the reviewer's verdict alone. Each finding is reconciled by re-reading the actual artifact text the finding refers to, then classified into exactly one of four buckets, in this precedence order:

1. **Contract misread** — the reviewer misunderstood the CONTRACT (not the artifact). The finding is invalid; note why and move on. This bucket is checked first because a finding built on a wrong premise cannot be valid regardless of what it says about the code.
2. **Valid and actionable** — the artifact fails the contract in a way that must be fixed before the finding is closed.
3. **Valid trade-off** — the finding correctly identifies a real property of the artifact, but the property is an accepted trade-off, not a defect (e.g., the reviewer flags a synchronous call that is intentionally synchronous for a documented reason). Record the trade-off explicitly rather than silently discarding the finding.
4. **Noise** — the finding is a style or preference comment with no correctness, contract, or trade-off content.

Precedence matters because a finding can look like bucket 2 or 4 on the surface while actually being bucket 1 — checking contract-misread first prevents both false rejections (dismissing a real issue as noise) and false fixes (patching code to satisfy a contract the reviewer misunderstood, not the actual one). Findings are never rubber-stamped into a bucket from the reviewer's own framing; the orchestrator's re-read of the artifact is the source of truth for classification.

## Cross-Model Escalation and Tool-Use Guardrails

On every interactive review cycle, offer cross-model escalation (routing the review to a different model architecture, not just a fresh context on the same model) explicitly — do not silently skip it. A review that never varies the model architecture is still vulnerable to shared blind spots between the orchestrator and reviewer; silently skipping the offer removes the human's chance to catch that.

If the review step invokes an external CLI (a linter, a second agent binary, a scanner), require: a PATH check that the binary exists, a working-binary smoke test before relying on its output, and explicit per-call user authorization — do not assume a previously-authorized tool stays authorized for every subsequent call.

## Composing with P4a

Use this file to decide *what* the reviewer receives and *how* findings are triaged on each cycle. Use P4a's round-cap table and mandatory per-finding adjudication (reviewer-wrong / real-but-not-load-bearing / real-and-load-bearing) for *when the loop stops* and what happens at the cap. The two are sequential within a cycle: this file's reconciliation buckets (1–4 above) run each cycle; P4a's adjudication buckets run only once, at the cap, over whatever is still open. Do not merge the two bucket sets — they answer different questions (per-cycle triage vs. cap-time disposition) and collapsing them loses the "contract misread" category, which has no equivalent in P4a's three-bucket adjudication.
