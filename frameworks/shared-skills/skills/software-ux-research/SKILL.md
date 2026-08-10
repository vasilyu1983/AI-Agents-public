---
name: software-ux-research
description: "Guides user research methods and research ops. Use when running interviews, usability tests, surveys, or A/B tests to de-risk product decisions."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-08-10
---

# Software UX Research

Use this skill to reduce product and design risk with evidence. It owns research method choice, study design, findings synthesis, and research operations. It does not own UI implementation.

## Quick Reference

| Need | Default | Output |
|------|---------|--------|
| discovery and JTBD | semi-structured interviews with 5-8 participants | opportunity brief |
| usability evaluation | moderated usability test with 5-7 participants | findings report with severity |
| quantification after qual insight | survey or analytics review | segment or pattern readout |
| causal change validation | controlled experiment or staged rollout | experiment brief |
| research ops and repository design | lightweight intake, taxonomy, and consent model | research-ops recommendation |
| accessibility or low-digital-literacy research | moderated sessions with adapted materials | risk and inclusion report |

## When to Use This Skill

Use this skill when the main question is:

- what user problem matters and for whom
- whether a concept, flow, or prototype is understandable and usable
- which research method is appropriate
- how to design a study and synthesize findings
- how to run research ops, repository, and consent workflows

Route elsewhere when the main task is:

| Need | Use Instead |
|------|-------------|
| UI design and interaction patterns | [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) |
| code-level accessibility remediation | [../software-accessibility/SKILL.md](../software-accessibility/SKILL.md) |
| accessibility testing automation and CI gates | [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md) |
| analytics instrumentation implementation | `marketing-product-analytics` and [../qa-observability/SKILL.md](../qa-observability/SKILL.md) |

## Defaults

- start from the decision to unblock
- choose the smallest method mix that can answer the question
- use qual for motives and friction, quant for scale and segmentation
- treat synthetic participants as hypothesis generation only
- require confidence level and evidence trail in every output
- current standards and regulatory claims must be verified before final advice

## Quality Lens

Consumer-grade research looks past task completion to whether the experience is efficient, considerate, and worth coming back to. Evaluate every research question and finding through four layers — methods that only cover the top layer will miss why people churn or never habit-form. See [references/consumer-experience-quality.md](references/consumer-experience-quality.md) for methods, instruments, and recipes.

| Layer | Question | Primary Methods |
|-------|----------|-----------------|
| Task | can users complete the job? | usability testing, task success, SEQ |
| Friction | what slows, frustrates, or shames them? | friction logging, diary studies, session replay paired with interview |
| Emotion | how does it feel — proud, calm, tense, ignored? | PrEmo, AttrakDiff, Microsoft Desirability Toolkit, micro-interviews |
| Meaning | does it earn a place in their life? does it cause harm? | JTBD Switch interviews, Continuous Discovery (OST), longitudinal/diary, retention cohorts |

A finding that names task pass-rate but not friction or emotion is incomplete. Discovery work without Meaning-layer questions tends to ship features people use once.

## Workflow

1. Define the decision and deadline.
2. Inventory existing evidence.
3. Choose the method and explain why weaker alternatives were rejected.
4. Produce one decision-ready output.
5. Tag confidence and data-handling constraints.

## ASCII Flow

```text
UX research task
  -> Define decision, audience, deadline, and risk
  -> Inventory existing evidence and data constraints
  -> Choose smallest method mix that answers the decision
  -> Run or design study with consent and evidence trail
  -> Synthesize findings with confidence level
  -> Deliver options, tradeoffs, and next decision
```

## Output Types

Default outputs:

- research plan
- study protocol
- findings report
- decision brief

Every substantial output should include:

- method justification
- confidence level
- evidence trail
- consent and data-handling note
- recommendation framed as options and tradeoffs

## Method Chooser

| Need | Primary Methods |
|------|-----------------|
| motives, needs, switching triggers | interviews, contextual inquiry, diary studies |
| usability and learnability | moderated usability testing, cognitive walkthroughs, heuristic review |
| scale, segments, or behavioral patterns | analytics review, surveys, feedback mining |
| causal effect | controlled experiment, staged rollout, preference test |

Use moderated testing by default when failure paths, assistive technology, or complex workflows matter.

## Stage Guidance

| Stage | Typical Research Focus |
|-------|------------------------|
| discovery | problem selection, JTBD, forces of progress |
| concept or MVP | concept comprehension, prototype usability, onboarding risk |
| launch | blocker identification, accessibility, and readiness |
| growth | retention, friction, and segment behavior |
| maturity | optimization, simplification, or feature retirement |

## Verification Checklist

Before delivering any research output:

- [ ] Decision the study was designed to unblock is named explicitly
- [ ] Method justified: weaker alternatives were considered and rejected with reasons
- [ ] Participants match the target segment — not convenience, panel-only, or CS rolodex
- [ ] Sample size appropriate to method: ≥5 for usability, ≥8 for discovery interviews, power-calculated for experiments
- [ ] Confidence level and evidence trail stated in the output
- [ ] Synthetic participants labeled as hypothesis generation only — not cited as evidence
- [ ] AI-assisted analysis audited (≥10-15% of AI tags verified against human coding)
- [ ] Consent obtained; recordings, transcripts, and participant identity stored separately
- [ ] EU/UK participant data: DPA in place before sending to AI-processing vendor; EU AI Act high-risk (Annex III) deployer obligations postponed from 2026-08-02 to 2027-12-02 under the Digital Omnibus — the European Parliament (16 June 2026) and Council (29 June 2026) have both given final approval; the act enters into force shortly after Official Journal publication (verify the exact effective date before citing it as settled law)
- [ ] Disconfirming evidence documented, not only confirming clips
- [ ] Agentic products: study ran multi-turn, exercised at least one interruption, and included seeded incorrect outputs if trust was measured

## Research Ops Rules

- capture the decision, audience, segment, and evidence links in intake
- use one taxonomy across studies and atomic insights
- separate participant identity from notes and recordings
- redact broad-share artifacts
- let non-researchers run only templated studies with review guardrails

## AI and Accessibility Notes

For AI-powered product research (the *thing being studied* is AI-driven):

- test trust calibration, failure recovery, explainability, tool-use disclosure, and approval gating
- separate wrong output from unclear output and non-recoverable failure
- run multi-turn sessions for agentic products — single-turn studies miss most of the failure surface
- test steering explicitly: users change their mind mid-task, and addition/revision/retraction fail differently
- measure trust calibration against seeded *incorrect* outputs; an all-correct study cannot distinguish good judgment from blind acceptance
- see [references/ai-in-research.md](references/ai-in-research.md) for the full dimension list and method mapping, and [references/agentic-evaluation-methods.md](references/agentic-evaluation-methods.md) for the multi-turn protocols

For AI *in the research workflow* (synthesis tools, AI moderators, synthetic users):

- treat synthetic users as hypothesis generation only (NN/g position), never as evidence
- start analysis from human-coded seed sample, then let AI extend; audit at least 10–15% of AI tags
- AI moderators are appropriate only when the protocol is structured enough for a junior human to follow
- inventory every AI tool that processes participant data for EU AI Act enforcement (high-risk deployer obligations postponed to 2 December 2027 under the Digital Omnibus, now approved by Parliament and Council as of June 2026 — verify current in-force date)

For accessibility-sensitive research:

- recruit assistive-technology users when accessibility is in scope
- distinguish accessibility usability findings from formal conformance findings

## Known Traps

- Starting with a preferred method before naming the actual decision the study needs to unblock.
- Recruiting convenience participants whose context, literacy, or workflow is too far from the target segment.
- Treating generated summaries, AI note clustering, or synthetic participants as evidence instead of support material.
- Mixing discovery, usability, and causal-validation questions into one study and getting ambiguous output from all three.
- Reporting severity or confidence without tying it to sample quality, task coverage, and evidence strength.
- Storing recordings, transcripts, and participant identity with weaker controls than the sensitivity of the study requires.
- Sending EU/UK participant recordings to a non-EU AI vendor (Dovetail, Marvin, Looppanel, or any foundation-model-backed service) without a current DPA and explicit AI processing disclosure in consent — Chapter V GDPR transfer rules apply now, and EU AI Act high-risk deployer obligations follow (postponed from 2 August 2026 to 2 December 2027 under the Digital Omnibus, approved by Parliament and Council in June 2026 — verify the current in-force date before relying on it).
- Recruiting only from professional research panels (Prolific, UserTesting panel) for behavior studies, then generalising to product users — panel respondents are experienced participants whose behavior systematically diverges from first-time real users.

## Common Anti-Patterns

- Running surveys to answer `why` questions that need observed behavior or interviews.
- Treating five usability sessions as statistically representative rather than as directional evidence about failure patterns.
- Converting every insight into a roadmap request instead of separating evidence, interpretation, and action options.
- Using heuristic review as a replacement for user research when task comprehension or domain literacy is the core risk.
- Repeating studies without a repository, taxonomy, or decision log, so the team relearns the same lesson every quarter.
- Democratising research as cover for cutting researcher headcount: non-researchers run uncontrolled studies, cherry-pick confirming insights, and quality silently degrades. Templated studies with reviewer guardrails are the supported pattern; "anyone can run any study" is not.
- Letting an AI moderator handle generative or first-time discovery work — leading prompts produce leading follow-ups at scale.
- Confirmation bias in moderation: the moderator unconsciously seeks confirming clips and discounts disconfirming ones. Mitigation: code clips before discussing, require double-coder agreement on findings above severity 2, and explicitly document disconfirming evidence in every report.
- Decision-by-quote / champion-user-as-segment: shipping a feature because one passionate user wanted it. Single-N evidence is hypothesis, not finding.
- Post-hoc segmentation hunting: slicing experiment results by 20 segments until one is significant. Pre-register segmentation analysis before the experiment reads out, or apply a correction (Bonferroni, FDR) when segments are exploratory.
- Satisfaction theater: surveys conducted to put a number on a slide rather than to inform a decision. If the survey result would not change anything, do not run it.
- Power-gaming experimentation: extending experiments until significance appears, hiding losing variants, or changing the primary metric mid-experiment to ship a desired outcome. Each of these invalidates the result.
- Rating agent transcripts instead of having raters use the agent. Someone who did not have the conversation cannot judge trust, patience, or perceived competence — their scores track fluency instead. Multi-turn evaluation requires first-person experience.
- Measuring trust in an AI product using only correct outputs. Without seeded errors you can measure acceptance, but you cannot distinguish good calibration from blind acceptance — and over-reliance is the failure that matters.
- Reporting task completion for agentic tasks without elapsed time and cost. A task that completed after six minutes and four retries is not the same outcome as one that took twenty seconds; completion rate alone hides it.
- Citing a model benchmark as a UX finding. Benchmarks tell you the capability ceiling, not whether your interface lets users reach it.
- Recruiting the customer-success rolodex as a research panel: those users are atypically engaged, vocal, and cooperative. Generalizing from them is a top-of-funnel research failure — find disengaged, lapsed, and never-converted users too.

## Navigation

**References**

- [references/usability-testing-guide.md](references/usability-testing-guide.md)
- [references/survey-design-guide.md](references/survey-design-guide.md)
- [references/ux-audit-framework.md](references/ux-audit-framework.md)
- [references/priority-based-ux-audit.md](references/priority-based-ux-audit.md) — priority-ordered audit dimensions (accessibility → data display), evidence-tied severity model, queryable guideline grounding
- [references/ux-metrics-framework.md](references/ux-metrics-framework.md)
- [references/research-repository-management.md](references/research-repository-management.md)
- [references/ab-testing-implementation.md](references/ab-testing-implementation.md)
- [references/non-technical-user-research.md](references/non-technical-user-research.md)
- [references/ai-in-research.md](references/ai-in-research.md)
- [references/agentic-evaluation-methods.md](references/agentic-evaluation-methods.md) — evaluating multi-turn agentic products: interruption/steering testing, multi-turn first-person evaluation, trust calibration with seeded errors, agent-augmented heuristic evaluation
- [references/consumer-experience-quality.md](references/consumer-experience-quality.md) — Continuous Discovery, JTBD Switch, friction logging, emotion measurement, diary studies, competitive UX benchmarking, opportunity sizing, JTBD outcome statements, watch parties, embedding models
- [references/ia-testing-guide.md](references/ia-testing-guide.md) — card sort (open/closed/hybrid), tree testing, first-click testing, 5-second testing
- [references/evaluative-methods-guide.md](references/evaluative-methods-guide.md) — Wizard of Oz, concierge, painted-door, fake-door/smoke, conjoint, MaxDiff, Kano, beta panels
- [references/consumer-recruiting-guide.md](references/consumer-recruiting-guide.md) — sources, screeners, incentive ethics, kids/teens (COPPA, ICO Children's Code, GDPR Art. 8), Hawthorne, accessibility recruiting, churned-user recruiting
- [references/research-frameworks.md](references/research-frameworks.md) — choosing a research method (discovery vs evaluative, method-selection matrix)
- [references/customer-journey-mapping.md](references/customer-journey-mapping.md) — journey maps, service blueprints, experience mapping
- [references/competitive-ux-analysis.md](references/competitive-ux-analysis.md) — competitive UX teardowns and benchmarking
- [references/review-mining-playbook.md](references/review-mining-playbook.md) — mining app-store/forum reviews for pain points and switching triggers
- [references/pain-point-extraction.md](references/pain-point-extraction.md) — extracting and prioritizing pain points from qualitative data
- [references/feedback-tools-guide.md](references/feedback-tools-guide.md) — in-product feedback, survey, and voice-of-customer tooling
- [references/demographic-research-methods.md](references/demographic-research-methods.md) — research methods adapted by age group and demographic
- [references/remote-research-patterns.md](references/remote-research-patterns.md) — remote and unmoderated research methods and operations
- [references/evaluative-research-loop.md](references/evaluative-research-loop.md) — evaluative loop for prototype-parity polishing
- [references/bigtech-feedback-patterns.md](references/bigtech-feedback-patterns.md) — feedback and research patterns from BigTech and unicorns
- [data/sources.json](data/sources.json)

**Assets**

- [assets/research-plan-template.md](assets/research-plan-template.md)
- [assets/testing/usability-test-plan.md](assets/testing/usability-test-plan.md)
- [assets/testing/usability-testing-checklist.md](assets/testing/usability-testing-checklist.md)
- [assets/audits/heuristic-evaluation-template.md](assets/audits/heuristic-evaluation-template.md)
- [assets/audits/ux-audit-report-template.md](assets/audits/ux-audit-report-template.md)
- [assets/metrics/ux-metrics-dashboard.md](assets/metrics/ux-metrics-dashboard.md)

## Related Skills

- [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md)
- [../software-accessibility/SKILL.md](../software-accessibility/SKILL.md)
- [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md)
- `marketing-product-analytics`

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current standards, legal deadlines, and external research-method claims before final advice.
- Prefer ISO, W3C, regulator, and primary-method sources over summaries.
- If live verification is unavailable, mark external claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

