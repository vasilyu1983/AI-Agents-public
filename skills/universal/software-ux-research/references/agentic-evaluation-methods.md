# Agentic Evaluation Methods (2026)

Research methods for evaluating **multi-turn, agentic products** — systems that act over time, use tools, and can be interrupted mid-task. Classic single-session usability testing measures the wrong surface for these products: it catches comprehension failures but misses steering, recovery, trust calibration, and cost surprise, which is where agentic products actually fail.

This file covers *how to study an agent*. For how to design one, see [../software-ui-ux-design/references/ai-automation-ux.md](../../software-ui-ux-design/references/ai-automation-ux.md). For AI used *inside* the research workflow (synthesis tools, AI moderators, synthetic users), see [ai-in-research.md](ai-in-research.md) — that is a different concern and the two should not be conflated.

**Last Updated**: August 2026

---

## Table of Contents

- [Why Single-Turn Methods Under-Measure Agents](#why-single-turn-methods-under-measure-agents)
- [Interruption and Steering Testing](#interruption-and-steering-testing)
- [Multi-Turn First-Person Evaluation (UX Evals)](#multi-turn-first-person-evaluation-ux-evals)
- [Trust Calibration and Over-Reliance](#trust-calibration-and-over-reliance)
- [Agent-Augmented Heuristic Evaluation](#agent-augmented-heuristic-evaluation)
- [Method Selection](#method-selection)
- [Anti-Patterns](#anti-patterns)
- [Sources](#sources)

---

## Why Single-Turn Methods Under-Measure Agents

The parent SKILL.md states that agentic products need multi-turn sessions because "single-turn studies miss most of the failure surface." Concretely, the missed surface is:

| Failure surface | Why single-turn misses it | Method that catches it |
|-----------------|--------------------------|------------------------|
| Steering failure | Requires the user to change their mind mid-task, which a scripted single task never prompts | Interruption testing |
| Recovery from wrong-but-plausible output | Needs the user to *notice* the error first, which often happens turns later | Multi-turn first-person eval |
| Trust miscalibration | Reliance patterns form over repeated exposure, not one interaction | Trust calibration instruments |
| Cost/effort surprise | Accrues across steps and retries | Longitudinal or diary study |
| Memory drift | Only visible across sessions | Longitudinal study |

A study design that runs one prompt and rates the answer measures answer quality. That is a model eval, not a UX study.

---

## Interruption and Steering Testing

**What it is.** A protocol that tests whether users can successfully change the goal *while the agent is working* — and whether the agent handles it. Zou et al. (2026) formalize three interruption types, which give you a ready-made task matrix.

| Interruption type | Participant instruction | What you observe |
|-------------------|------------------------|------------------|
| **Addition** | "While it's running, decide you also want X" | Can they add without losing completed work? Do they know how? |
| **Revision** | "Partway through, change your mind — you want Y not X" | Can they redirect? Does the agent re-plan or restart? |
| **Retraction** | "Decide you no longer want the X part" | Can they remove one requirement without cancelling everything? |

**Protocol.**

1. Give the participant a task long enough to have a middle (≥3 agent steps, ideally 30+ seconds of visible work).
2. Trigger the interruption at a controlled point — mid-execution, not between turns. Use a prompt card so timing is consistent across participants.
3. Observe: do they find an affordance at all, do they use the destructive option (stop/cancel) as a proxy, and what do they believe happened to prior work?
4. After the run, ask them to state what the agent kept and what it redid. Mismatch with reality is a finding, even if the task completed.

**Sample size.** Standard usability sizing applies (5–7 for pattern discovery), but run all three interruption types per participant — the types fail differently and retraction is usually the worst-supported.

**Why it matters as a research method, not just an engineering benchmark.** The original work is a model benchmark (InterruptBench, derived from WebArena-Lite), and all six LLM backbones tested struggled. That means the *model* limitation and the *interface* limitation are entangled: if users can't steer, you cannot tell from a completion metric whether the affordance was missing or the agent ignored it. Instrument both — log whether an interruption was expressed, and separately whether it was honored.

---

## Multi-Turn First-Person Evaluation (UX Evals)

**What it is.** Evaluation in which the same person who has the conversation with the agent also rates the experience, run at scale across many participants. It sits between two things you probably already do: automated evals (scaled, but the rater never used the product) and moderated usability tests (real experience, but n≈6).

**Why the first-person constraint matters.** A third-party rater reading a transcript cannot judge whether a response felt evasive, whether the wait was tolerable, or whether they would have trusted it enough to act. Those judgments require having been in the conversation. Transcript-rating produces plausible scores that decouple from lived experience.

**Protocol sketch.**

1. Recruit to your actual segment (not a research panel — see [consumer-recruiting-guide.md](consumer-recruiting-guide.md)).
2. Give a goal, not a script. Multi-turn realism requires the participant to pursue their own intent.
3. Rate *in-session*, per turn or per episode, while the experience is live — not in a post-hoc survey where recency and rationalization dominate.
4. Pair the quantitative rating with a short open response per low-rated turn. The rating tells you where; only the text tells you why.

**Confidence and limits.** The method is currently vendor-authored (Outset, with Microsoft Copilot UX research co-authorship) and has no independent replication that this scan could find. Treat it as a **promising protocol to pilot**, not a validated instrument — and specifically do not cite it as a replacement for moderated testing until you have run both on the same product and compared what each surfaced.

---

## Trust Calibration and Over-Reliance

The goal is **appropriate reliance**, not maximum trust. Both failure directions are real and they need different fixes:

| Failure | Behavior | Design implication |
|---------|----------|-------------------|
| **Over-reliance** | Accepts agent output without verification, including when wrong | Needs friction, confidence signals, or verification affordances |
| **Under-reliance** | Ignores or re-does correct agent output | Needs explainability and track-record signals |

**Measuring it.** Trust calibration is measured as *deviation from ideal reliance* — you need ground truth on which agent outputs were actually correct, then compare acceptance rates on correct versus incorrect output.

- **Acceptance rate on correct output** — under-reliance shows up as a low number here.
- **Acceptance rate on incorrect output** — over-reliance shows up as a high number here. This is the one that matters most and the one teams most often fail to measure, because it requires deliberately including wrong outputs in the study.
- **Verification behavior** — does the participant check sources, cross-check, or act directly? Observable in moderated sessions.

**Study design requirement.** You must seed known-incorrect agent outputs into the session, and you must disclose this in debrief. Without incorrect trials, you can measure acceptance but not calibration — an all-correct study makes blind acceptance look like good judgment.

---

## Agent-Augmented Heuristic Evaluation

Liu et al. (2026) re-tested Nielsen's ten heuristics against **computer-use agents** — agents that operate a GUI as a user would — and found that additive augmentations to interface design improve agent task completion, with human studies showing the changes "preserve the original interaction workflow without observable usability regressions."

**The research-relevant finding**: agent-friendly and human-friendly are not in tension here. That reframes a common product argument ("we'd have to degrade the UI to make it agent-navigable") as an empirical claim that this study contradicts, at least for additive changes.

**How to use it as a method.** When a product will be operated by both humans and agents, run heuristic evaluation twice against the same interface — once with the classic human lens, once asking whether each heuristic holds for a non-human operator (Is system status machine-readable, not only visible? Are affordances discoverable without hover? Is error recovery expressible as an action, not just legible as text?). Findings that appear in both passes are the highest-priority fixes.

**Evidence grade.** B — controlled environments (UI-Verse) with baselines and human studies. Specific sample sizes were not stated in the abstract; check the full paper before citing effect sizes.

---

## Method Selection

| Decision to unblock | Method | Typical n |
|--------------------|--------|-----------|
| Can users steer the agent when they change their mind? | Interruption testing (addition/revision/retraction) | 5–7 |
| Does the multi-turn experience hold up at scale? | Multi-turn first-person evaluation | 30+ |
| Do users trust the agent the right amount? | Trust calibration with seeded errors | 12–20 |
| Will both humans and agents be able to operate this UI? | Dual-lens heuristic evaluation | 3–5 evaluators |
| Does the agent earn a place in the workflow over time? | Diary / longitudinal study — see [evaluative-methods-guide.md](evaluative-methods-guide.md) §8 | 8–15 |
| Is a single response good? | Not a UX study. That is a model eval. | — |

---

## Anti-Patterns

- **Transcript-rating as a proxy for experience.** A rater who did not have the conversation cannot judge trust, patience, or perceived competence. Their scores will correlate with fluency instead.
- **Testing only the happy path on an agentic product.** The failure surface *is* the product; a study that never triggers an error, an interruption, or a wrong answer has measured the demo.
- **Measuring trust without seeded errors.** An all-correct study cannot distinguish good calibration from blind acceptance.
- **Reporting task completion for agentic tasks without reporting cost and elapsed time.** A task that completed after 6 minutes and four retries is not the same outcome as one that completed in 20 seconds, and completion rate alone hides the difference.
- **Treating a model eval as a UX finding.** Benchmarks like InterruptBench measure model capability. They tell you the ceiling, not whether your interface lets users reach it.
- **Letting an AI moderator run agentic discovery sessions.** Already an anti-pattern in the parent SKILL.md; multi-turn agentic work makes it worse, since leading follow-ups compound across turns.
- **Single-session studies for memory or personalization features.** Memory drift and preference learning are invisible inside one session by definition.

---

## Sources

- [arXiv:2604.00892](https://arxiv.org/abs/2604.00892) — Zou et al., "When Users Change Their Mind: Evaluating Interruptible Agents in Long-Horizon Web Navigation" (2026-04-01). InterruptBench; three interruption types; six LLM backbones; code and dataset public. Evidence grade B.
- [arXiv:2605.02729](https://arxiv.org/abs/2605.02729) — Liu, Wang, Li, Zhu, Shen, Wang, Abbasi, Zhang, Ji, "Augmenting Interface Usability Heuristics for Reliable Computer-Use Agents" (2026-05-04). UI-Verse controlled environments plus human studies. Evidence grade B.
- [arXiv:2606.20630](https://arxiv.org/abs/2606.20630) — Zhu, Wang, Xiao, Shen, "Design Principles for Human-Agent Interaction" (2026-05-28). 14 principles across four interaction stages, applied to nine agent systems. Position paper — argued and applied, not empirically validated. Evidence grade C.
- [Outset — "Introducing UX Evals"](https://outset.ai/resources/blog/introducing-ux-evals) (2026-01-22). Vendor-authored with Microsoft Copilot UXR co-authorship. No independent replication found. Evidence grade C.

*Thank you to arXiv for use of its open access interoperability.*

**Verification status**: all four sources above were fetched directly and their titles, authors, and dates confirmed on 2026-08-10. Claims about specific effect sizes and sample sizes were **not** verifiable from abstracts and are deliberately not stated here — check full texts before citing numbers.

---

## Related Resources

- [evaluative-methods-guide.md](evaluative-methods-guide.md) — Wizard of Oz, concierge, painted-door, diary/longitudinal, beta panels
- [ai-in-research.md](ai-in-research.md) — AI *inside* the research workflow; synthetic participants; AI moderators
- [usability-testing-guide.md](usability-testing-guide.md) — moderated testing fundamentals these protocols build on
- [consumer-recruiting-guide.md](consumer-recruiting-guide.md) — recruiting, screeners, and why panel-only sampling distorts behavior studies
- [../software-ui-ux-design/references/ai-automation-ux.md](../../software-ui-ux-design/references/ai-automation-ux.md) — the design-side counterpart: approval gates, interruption affordances, cost visibility
