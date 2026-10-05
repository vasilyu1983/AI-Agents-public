---
name: software-ux-research
description: "Guides user research and research ops. Use when running interviews, usability tests, surveys, or synthesis to de-risk product decisions; not experiments or review mining."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-08-10
---

# Software UX Research

Use this skill to reduce product and design risk with evidence. It owns research method choice, study design, findings synthesis, and research operations. It does not own UI implementation.

## Quick Reference

| Need | Default | Output |
|------|---------|--------|
| discovery and JTBD | semi-structured interviews with a predeclared segment, saturation, and budget stop rule | opportunity brief |
| usability evaluation | moderated tests covering each critical task and user group; iterate in small rounds | findings report with severity |
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
| experiment design, instrumentation, and readout statistics | `marketing-product-analytics`; research-side decision in [references/ab-testing-implementation.md](references/ab-testing-implementation.md) |
| review, app-store, and complaint mining for pain points | `research-review-mining` |
| persona or synthetic-user browser testing of a built product | [../qa-persona-testing/SKILL.md](../qa-persona-testing/SKILL.md) |
| PMF surveys, idea validation, demand tests before a product exists | `startup-idea-validation` and [../product-management/SKILL.md](../product-management/SKILL.md) |
| heuristic checklists, UI polish loops, and design-quality audits | [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) |

## Defaults

- start from the decision to unblock
- choose the smallest method mix that can answer the question
- use qual for motives and friction, quant for scale and segmentation
- treat synthetic participants as hypothesis generation only
- require confidence level and evidence trail in every output
- current standards and regulatory claims must be verified before final advice

## Quality Lens

Choose the evidence layers the decision needs: task success and friction for a flow fix; emotion and meaning when studying trust, retention, or adoption. State which layers were studied and limit conclusions to them. Load [references/consumer-experience-quality.md](references/consumer-experience-quality.md) for the four-layer lens and its methods; task completion alone does not establish a retention benefit.

## Workflow

1. Define the decision and deadline.
2. Inventory existing evidence.
3. Choose the method and explain why weaker alternatives were rejected.
   For surveys, predeclare fraud, bot, duplicate, and speeder screening before distribution; use [references/survey-design-guide.md#survey-integrity-fraud-bots-and-speeders](references/survey-design-guide.md#survey-integrity-fraud-bots-and-speeders).
4. Produce one decision-ready output.
5. Tag confidence and data-handling constraints.

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
| scale, segments, or behavioral patterns | analytics review, surveys, feedback analysis (review mining: research-review-mining) |
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
- [ ] Sample rationale names tasks, segments, risk, excluded populations, numeric stop threshold, consecutive evaluation window, maximum sample/budget, and action at the cap; experiments are power-calculated
- [ ] Confidence level and evidence trail stated in the output
- [ ] Synthetic participants labeled as hypothesis generation only — not cited as evidence
- [ ] AI-assisted analysis plan predeclares the tolerated disagreement by severity, audit-batch size, consecutive passing batches, maximum audit size, and the human-recoding/escalation action if the cap is reached
- [ ] Consent obtained; recordings, transcripts, and participant identity stored separately
- [ ] EU/UK participant data: DPA in place before sending to AI-processing vendor; check whether EU AI Act high-risk (Annex III) deployer obligations apply and take their current application dates from qualified EU regulatory counsel or the Official Journal text, not from memory
- [ ] Disconfirming evidence documented, not only confirming clips
- [ ] Agentic products: study ran multi-turn, exercised at least one interruption, and included seeded incorrect outputs if trust was measured

## Research Ops Rules

- capture the decision, audience, segment, and evidence links in intake
- use one taxonomy across studies and atomic insights
- separate participant identity from notes and recordings
- redact broad-share artifacts
- let non-researchers run only templated studies with review guardrails

Prefer ISO, W3C, regulator, and primary-method sources over summaries.

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
- start analysis from a human-coded seed sample, then let AI extend; audit every tag class plus low-confidence and random items against the predeclared disagreement rule
- AI moderators are appropriate only when the protocol is structured enough for a junior human to follow
- inventory every AI tool that processes participant data (vendor, data sent, DPA, AI Act classification — see the EU/UK checklist item above and [references/ai-in-research.md#eu-ai-act](references/ai-in-research.md#eu-ai-act))

Write qualitative stop rules (saturation threshold, window, cap, action at the cap) and AI-coding audit rules before recruitment: [references/research-frameworks.md#reproducible-qualitative-stop-rules](references/research-frameworks.md#reproducible-qualitative-stop-rules).

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
- Sending EU/UK participant recordings to a non-EU AI vendor (Dovetail, Marvin, Looppanel, or any foundation-model-backed service) without a current DPA and explicit AI processing disclosure in consent — Chapter V GDPR transfer rules apply.
- Recruiting only from professional research panels (Prolific, UserTesting panel) for behavior studies, then generalising to product users — panel respondents are experienced participants whose behavior systematically diverges from first-time real users.

## Common Anti-Patterns

Wrong method for the question (surveys for `why`, heuristic review for comprehension risk), n=5 read as representative, single-quote decisions, post-hoc segment hunting, stopping experiments at significance, and panel or CS-rolodex recruiting. Full list with mitigations: [references/research-frameworks.md#research-practice-anti-patterns](references/research-frameworks.md#research-practice-anti-patterns); AI and agentic-product anti-patterns: [references/ai-in-research.md#anti-patterns](references/ai-in-research.md#anti-patterns).

## Navigation

**References**

- [references/usability-testing-guide.md](references/usability-testing-guide.md)
- [references/survey-design-guide.md](references/survey-design-guide.md)
- [references/westrum-culture-measurement.md](references/westrum-culture-measurement.md) — worked example of a validated seven-item team-culture survey construct (Westrum typology, scoring, provenance limits); pairs with `foundations-team-theory`
- [references/ux-audit-framework.md](references/ux-audit-framework.md) — expert review vs user research, cognitive walkthrough, evidence-tied severity model
- [references/ux-metrics-framework.md](references/ux-metrics-framework.md)
- [references/research-repository-management.md](references/research-repository-management.md)
- [references/ab-testing-implementation.md](references/ab-testing-implementation.md) — experiment vs research decision, readout checks, maturity levels; experiment mechanics route to marketing-product-analytics
- [references/non-technical-user-research.md](references/non-technical-user-research.md)
- [references/ai-in-research.md](references/ai-in-research.md)
- [references/agentic-evaluation-methods.md](references/agentic-evaluation-methods.md) — evaluating multi-turn agentic products: interruption/steering testing, multi-turn first-person evaluation, trust calibration with seeded errors, agent-augmented heuristic evaluation
- [references/consumer-experience-quality.md](references/consumer-experience-quality.md) — Continuous Discovery, JTBD Switch, friction logging, emotion measurement, diary studies, competitive UX benchmarking, opportunity sizing, JTBD outcome statements, watch parties, embedding models
- [references/ia-testing-guide.md](references/ia-testing-guide.md) — card sort (open/closed/hybrid), tree testing, first-click testing, 5-second testing
- [references/evaluative-methods-guide.md](references/evaluative-methods-guide.md) — Wizard of Oz, concierge, painted-door, fake-door/smoke, conjoint, MaxDiff, Kano, beta panels
- [references/consumer-recruiting-guide.md](references/consumer-recruiting-guide.md) — sources, screeners, incentive ethics, kids/teens (COPPA, ICO Children's Code, GDPR Art. 8), Hawthorne, accessibility recruiting, churned-user recruiting
- [references/research-frameworks.md](references/research-frameworks.md) — choosing a research method (discovery vs evaluative, method-selection matrix)
- [references/customer-journey-mapping.md](references/customer-journey-mapping.md) — journey maps, service blueprints, experience mapping
- [references/competitive-ux-analysis.md](references/competitive-ux-analysis.md) — competitive UX benchmarking method and report templates
- [references/feedback-tools-guide.md](references/feedback-tools-guide.md) — in-product feedback, survey, and voice-of-customer tooling, plus feedback operating patterns
- [references/demographic-research-methods.md](references/demographic-research-methods.md) — research methods adapted by age group and demographic
- [references/remote-research-patterns.md](references/remote-research-patterns.md) — remote and unmoderated research methods and operations
- [data/sources.json](data/sources.json)

**Assets**

- [assets/research-plan-template.md](assets/research-plan-template.md)
- [assets/testing/usability-test-plan.md](assets/testing/usability-test-plan.md)
- [assets/testing/usability-testing-checklist.md](assets/testing/usability-testing-checklist.md)
- [assets/testing/think-aloud-protocol.md](assets/testing/think-aloud-protocol.md) — think-aloud session protocol template
- [assets/competitive/competitive-ux-matrix.md](assets/competitive/competitive-ux-matrix.md) — competitive UX matrix; load with [references/competitive-ux-analysis.md](references/competitive-ux-analysis.md)
- [assets/audits/ux-audit-report-template.md](assets/audits/ux-audit-report-template.md)
- [assets/metrics/ux-metrics-dashboard.md](assets/metrics/ux-metrics-dashboard.md)
- [assets/journeys/customer-journey-canvas.md](assets/journeys/customer-journey-canvas.md) — load with [references/customer-journey-mapping.md](references/customer-journey-mapping.md) when mapping touchpoints and emotional arcs
- [assets/journeys/service-blueprint-template.md](assets/journeys/service-blueprint-template.md) — load with [references/customer-journey-mapping.md](references/customer-journey-mapping.md) when documenting front/backstage service delivery

## Related Skills

- [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md)
- [../software-accessibility/SKILL.md](../software-accessibility/SKILL.md)
- [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md)
- `marketing-product-analytics`
- `research-review-mining`
- [../qa-persona-testing/SKILL.md](../qa-persona-testing/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
