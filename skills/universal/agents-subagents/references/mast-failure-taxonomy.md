---
description: MAST taxonomy mapping — 14 multi-agent failure modes across 3 categories, mapped to existing skill traps and per-mode mitigations.
last_verified: 2026-09-16
status: stable
---

# MAST Failure Taxonomy — Cross-Reference

MAST (Multi-Agent System Failure Taxonomy) is the canonical framework for classifying failures in LLM-based multi-agent systems. Source: Cemri, Pan, Yang et al., NeurIPS 2025 (Datasets & Benchmarks Track) — [arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657), repo [github.com/multi-agent-systems-failure-taxonomy/MAST](https://github.com/multi-agent-systems-failure-taxonomy/MAST). The v3 paper (October 2025) reports "1642 annotated execution traces" from 7 frameworks and inter-annotator κ = 0.88.

**Failure distribution (v3, Figure 1, 1,642 traces):**
- **Specification & Design (FC1)** — 44.0%
- **Inter-Agent Misalignment (FC2)** — 32.15%
- **Task Verification (FC3)** — 23.85%

Earlier versions and secondary write-ups quote other splits (for example 41.8 / 36.9 / 21.3); re-read the current paper version before quoting a figure.

System-level design choices dominate. Single-agent quality is *not* the bottleneck.

This file is a **mapping table**, not a re-derivation. For operator tactics on each mode, follow the link to the existing skill artifact.

## Contents

- [FC1 — Specification & Design Issues (5 modes)](#fc1--specification--design-issues)
- [FC2 — Inter-Agent Misalignment (6 modes)](#fc2--inter-agent-misalignment)
- [FC3 — Task Verification (3 modes)](#fc3--task-verification)
- [Coverage Gaps](#coverage-gaps)
- [How to Use This Table](#how-to-use-this-table)

---

## FC1 — Specification & Design Issues

| # | MAST Mode | What it looks like | Mitigation in this skill |
|---|-----------|--------------------|--------------------------|
| 1.1 | Disobey task specification | Agent ignores the brief's hard constraints | [`initial-prompt-contract.md`](initial-prompt-contract.md) — owned files, do-not-touch list |
| 1.2 | Disobey role specification | Agent acts outside its declared role (reviewer edits files, researcher runs commands) | [`agent-tools.md`](agent-tools.md) — minimal tool allow-list per role |
| 1.3 | Step repetition | Same step re-run with no new information | [`subagent-interruption-recovery.md`](subagent-interruption-recovery.md) + `maxTurns` bound in agent file |
| 1.4 | Loss of conversation history | Worker drops earlier context mid-run | [`context-first-protocol.md`](context-first-protocol.md#fresh-context-principle) — fresh-context brief, not transcript |
| 1.5 | Unaware of termination conditions | Worker doesn't know when to stop | [`initial-prompt-contract.md`](initial-prompt-contract.md) §"Rules" (verification field) + explicit deliverable contract |

## FC2 — Inter-Agent Misalignment

| # | MAST Mode | What it looks like | Mitigation in this skill |
|---|-----------|--------------------|--------------------------|
| 2.1 | Conversation reset | Agent forgets prior turn output | Foreground execution + persistent task list (`agent-teams` shared task layer) |
| 2.2 | Fail to ask for clarification | Agent fabricates instead of asking | [`clarification-questions-protocol.md`](clarification-questions-protocol.md) — anti-slop gate |
| 2.3 | Task derailment | Agent drifts to adjacent problem | [`traps-and-antipatterns.md`](traps-and-antipatterns.md) §"Known Traps" (orthogonal edits) + scope discipline |
| 2.4 | Information withholding | Agent omits findings other agents need | [`context-first-protocol.md`](context-first-protocol.md) + Shapley scoring [§4](../../foundations-team-theory/assets/templates/team-theory/04-shapley-contribution.md) |
| 2.5 | Ignore other agent input | Member produces analysis as if alone | Belief briefs [team-theory §1](../../foundations-team-theory/assets/templates/team-theory/01-econ-belief-driven.md) — explicit cross-member dependencies |
| 2.6 | Reasoning-action mismatch | Agent's chain-of-thought says X, action does Y | Reasoning-tree audit [team-theory §13](../../foundations-team-theory/assets/templates/team-theory/13-reasoning-tree-audit.md) |

## FC3 — Task Verification

| # | MAST Mode | What it looks like | Mitigation in this skill |
|---|-----------|--------------------|--------------------------|
| 3.1 | Premature termination | Agent declares done before deliverable is complete | Verification command + artifact list in [`initial-prompt-contract.md`](initial-prompt-contract.md) |
| 3.2 | No or incomplete verification | No evidence that output meets criteria | [`runtime-smoke-tests.md`](runtime-smoke-tests.md) + evaluator-optimizer in [`harness-patterns.md`](harness-patterns.md) |
| 3.3 | Incorrect verification | Verification step is wrong or rubber-stamps output | Heterogeneous verifier (different model + clean context) + Purple Team overlay [`purple-team-pattern.md`](purple-team-pattern.md) |

---

## Coverage Gaps

The following MAST modes need stronger first-class artifacts in this skill:

- **FC2.6 reasoning-action mismatch** — currently only addressed inside debate flows. For solo subagent runs, no explicit check. Candidate: a lightweight `verify_action_matches_reasoning` checklist for any write-capable single subagent.
- **FC3.3 incorrect verification** — Purple Team overlay covers the high-stakes case, but the everyday case (one subagent verifies another) lacks a concrete diff-the-verifier protocol. Candidate: heterogeneous-verifier rule (different model family, fresh context, no shared skills with the implementer).

These are **active gaps**, not stable patterns. Treat as work-in-progress.

---

## How to Use This Table

1. **Postmortem mode**: when a team run fails, classify the failure into one of the 14 modes, then jump to the linked mitigation. Most mitigations are already wired into existing artifacts; the failure usually means the artifact wasn't applied, not that it's missing.
2. **Pre-launch mode**: for high-stakes runs, walk the FC2 column and verify each mitigation is active in the launch prompt (belief briefs, clarification gate, reasoning-tree audit at synthesis).
3. **Skill-design mode**: when extending this skill, target the **3 columns × 14 rows** as the coverage matrix. New traps should map to a MAST cell or be flagged as a 15th+ failure mode with primary-source backing.

For the operator-facing failure-mode tip sheet (durable list, written for fast reading during a launch), see [`traps-and-antipatterns.md`](traps-and-antipatterns.md). This file is the **structured cross-reference**; the traps file is the **scannable checklist**.

---

## Source

- Cemri M., Pan M.Z., Yang S., et al. "Why Do Multi-Agent LLM Systems Fail?" NeurIPS 2025, Datasets & Benchmarks Track ([proceedings PDF](https://proceedings.neurips.cc/paper_files/paper/2025/file/b1041e52d3be19f0a9bc491657488e4a-Paper-Datasets_and_Benchmarks_Track.pdf)). [arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657)
- MAST repo + dataset: [github.com/multi-agent-systems-failure-taxonomy/MAST](https://github.com/multi-agent-systems-failure-taxonomy/MAST)
