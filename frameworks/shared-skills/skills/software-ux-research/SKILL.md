---
name: software-ux-research
description: Covers user research methods and research ops. Use when running interviews, usability tests, surveys, or A/B tests to de-risk product decisions.
---

# Software UX Research Skill — Quick Reference

Use this skill to identify problems/opportunities and de-risk decisions. Use `software-ui-ux-design` to implement UI patterns, component changes, and design system updates.

---

## Mar 2026 Baselines (Core)

- **Human-centred design**: Iterative design + evaluation grounded in evidence (ISO 9241-210:2019) https://www.iso.org/standard/77520.html
- **Usability definition**: Effectiveness, efficiency, satisfaction in context (ISO 9241-11:2018) https://www.iso.org/standard/63500.html
- **Accessibility baseline**: WCAG 2.2 is a W3C Recommendation (12 Dec 2024) https://www.w3.org/TR/WCAG22/
- **WCAG 3.0 preview**: Working Draft published Sep 2025; introduces Bronze/Silver/Gold conformance tiers and enhanced cognitive accessibility; not expected before 2028-2030 https://www.w3.org/WAI/standards-guidelines/wcag/wcag3-intro/
- **EU shipping note**: European Accessibility Act applies to covered products/services after 28 Jun 2025 (Directive (EU) 2019/882) https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019L0882

## When to Use This Skill

- Discovery: user needs, JTBD, opportunity sizing, mental models.
- Validation: concepts, prototypes, onboarding/first-run success.
- Evaluative: usability tests, heuristic evaluation, cognitive walkthroughs.
- Quant/behavioral: funnels, cohorts, instrumentation gaps, guardrails.
- Research Ops: intake, prioritization, repository/taxonomy, consent/PII handling.
- **Demographic research**: Age-diverse, cultural, accessibility participant recruitment.
- **A/B testing**: Experiment design, sample size, analysis, pitfalls.
- **Non-technical user research**: Digital literacy assessment, simplified-flow validation, low-tech-confidence usability testing.

## When NOT to Use This Skill

- **UI implementation** → Use [software-ui-ux-design](../software-ui-ux-design/SKILL.md) for components, patterns, code
- **Analytics instrumentation** → Use [marketing-product-analytics](../marketing-product-analytics/SKILL.md) for tracking plans and [qa-observability](../qa-observability/SKILL.md) for implementation patterns
- **Accessibility compliance audit** → Use accessibility-specific checklists (WCAG conformance)
- **Marketing research** → Use [marketing-social-media](../marketing-social-media/SKILL.md) or related marketing skills
- **A/B test platform setup** → Use experimentation platforms (Statsig, GrowthBook, LaunchDarkly)

---

## Operating Mode (Core)

If inputs are missing, ask for:

- Decision to unblock (what will change based on this research).
- Target roles/segments and top tasks.
- Platforms and contexts (web/mobile/desktop; remote/on-site; assisted tech).
- Existing evidence (analytics, tickets, reviews, recordings, prior studies).
- Constraints (timeline, recruitment access, compliance, budget).

Default outputs (pick what the user asked for):

- Research plan + output contract (prefer [../software-clean-code-standard/assets/checklists/ux-research-plan-template.md](../software-clean-code-standard/assets/checklists/ux-research-plan-template.md); use [assets/research-plan-template.md](assets/research-plan-template.md) for skill-specific detail)
- Study protocol (tasks/script + success metrics + recruitment plan)
- Findings report (issues + severity + evidence + recommendations + confidence)
- Decision brief (options + tradeoffs + recommendation + measurement plan)

### Required Output Sections

Every research output — plans, protocols, evaluations, reports — must include these sections. They represent the skill's core value beyond standard UX knowledge: governance, confidence calibration, and ethical research practice.

1. **Method Justification**: Name the chosen method AND explain why alternatives were rejected. Do not just describe the method; explain why it was selected over at least 2 alternatives given the specific context (stage, timeline, sample, question type).

2. **Confidence & Triangulation Assessment**: Tag every recommendation or finding with a confidence level:

   | Confidence | Evidence requirement | Use for |
   |------------|----------------------|---------|
   | High | Multiple methods or sources agree | High-impact decisions |
   | Medium | Strong signal from one method + supporting indicators | Prioritization |
   | Low | Single source / small sample | Exploratory hypotheses only |

3. **Consent & Data Handling**: Include a PII/consent section in every plan or protocol. Research that involves participants requires explicit attention to:
   - Minimum PII collection
   - Identity stored separately from study data
   - Name/email redaction before broad sharing
   - Recording access restricted to need-to-know
   - Consent, purpose, retention, and opt-out documented

4. **Decision Framework**: For evaluations and analysis outputs, provide a structured decision table with options, confidence levels, timelines, and risks — not just a single recommendation.

5. **Pre-Decision Checklist**: For experiment evaluations (A/B tests, etc.), include a verification checklist of confounds and data quality checks to complete before any ship/kill decision.

---

## Method Chooser (Core)

### Decision Tree (Fast)

```text
What do you need?
  ├─ WHY / needs / context → interviews, contextual inquiry, diary
  ├─ HOW / usability → moderated usability test, cognitive walkthrough, heuristic eval
  ├─ WHAT / scale → analytics/logs + targeted qual follow-ups
  └─ WHICH / causal → experiments (if feasible) or preference tests
```

When selecting a method, always justify the choice by explaining why 2+ alternatives were rejected given the user's specific context. This is a key differentiator — generic "we'll do interviews" without justification is insufficient.

---

## Research by Product Stage

### Stage Framework (What to Do When)

| Stage | Decisions | Primary Methods | Secondary Methods | Output |
|-------|-----------|-----------------|-------------------|--------|
| Discovery | What to build and for whom | Interviews, field/diary, journey mapping | Competitive analysis, feedback mining | Opportunity brief + JTBD + Forces of Progress |
| Concept/MVP | Does the concept work? | Concept test, prototype usability | First-click/tree test | MVP scope + onboarding plan |
| Launch | Is it usable + accessible? | Usability testing, accessibility review | Heuristic eval, session replay | Launch blockers + fixes |
| Growth | What drives adoption/value? | Segmented analytics + qual follow-ups | Churn interviews, surveys | Retention drivers + friction |
| Maturity | What to optimize/deprecate? | Experiments, longitudinal tracking | Unmoderated tests | Incremental roadmap |

### Discovery Outputs: Beyond Basic JTBD

Discovery research should produce more than job statements. Include:
- **Forces of Progress diagram**: Map the four forces acting on switching behavior — Push (current pain), Pull (new solution appeal), Anxiety (fear of change), Habit (inertia). These forces explain why users do or don't adopt, which directly informs positioning and onboarding.
- **Pain Point Severity Matrix**: Score each pain point by Frequency × Impact × Breadth to prioritize objectively. A pain that affects 3 roles weekly outranks one that affects 1 role monthly, even if the single-role pain feels more dramatic in interviews.

---

## Research for Complex Systems (Workflows, Admin, Regulated)

### Complexity Indicators

| Indicator | Example | Research Implication |
|-----------|---------|----------------------|
| Multi-step workflows | Draft → approve → publish | Task analysis + state mapping |
| Multi-role permissions | Admin vs editor vs viewer | Test each role + transitions |
| Data dependencies | Requires integrations/sync | Error-path + recovery testing |
| High stakes | Finance, healthcare | Safety checks + confirmations |
| Expert users | Dev tools, analytics | Recruit real experts (not proxies) |

### Evaluation Methods (Core)

- Contextual inquiry: observe real work and constraints.
- Task analysis: map goals → steps → failure points.
- Cognitive walkthrough: evaluate learnability and signifiers.
- Error-path testing: timeouts, offline, partial data, permission loss, retries.
- Multi-role walkthrough: simulate handoffs (creator → reviewer → admin).

### Multi-Role Coverage Checklist

- [ ] Role-permission matrix documented.
- [ ] “No access” UX defined (request path, least-privilege defaults).
- [ ] Cross-role handoffs tested (notifications, state changes, audit history).
- [ ] Error recovery tested for each role (retry, undo, escalation).

---

## Research Ops & Governance (Core)

### Intake (Make Requests Comparable)

Minimum required fields:

- Decision to unblock and deadline.
- Research questions (primary + secondary).
- Target users/segments and recruitment constraints.
- Existing evidence and links.
- Deliverable format + audience.

### Prioritization (Simple Scoring)

Use a lightweight score to avoid backlog paralysis:

- Decision impact
- Knowledge gap
- Timing urgency
- Feasibility (recruitment + time)

### Repository & Taxonomy

- Store each study with: method, date, product area, roles, tasks, key findings, raw evidence links.
- Tag for reuse: problem type (navigation/forms/performance), component/pattern, funnel step.
- Prefer “atomic” findings (one insight per card) to enable recombination [Inference].

### Consent, PII, and Access Control

Follow applicable privacy laws; GDPR is a primary reference for EU processing https://eur-lex.europa.eu/eli/reg/2016/679/oj

PII handling checklist:

- [ ] Collect minimum PII needed for scheduling and incentives.
- [ ] Store identity/contact separately from study data.
- [ ] Redact names/emails from transcripts before broad sharing.
- [ ] Restrict raw recordings to need-to-know access.
- [ ] Document consent, purpose, retention, and opt-out path.

### Research Democratization (2026 Trend)

Research democratization is a recurring 2026 trend: non-researchers increasingly conduct research. Enable carefully with guardrails.

| Approach | Guardrails | Risk Level |
|----------|------------|------------|
| Templated usability tests | Script + task templates provided | Low |
| Customer interviews by PMs | Training + review required | Medium |
| Survey design by anyone | Central review + standard questions | Medium |
| Unsupervised research | Not recommended | High |

**Guardrails for non-researchers:**

- [ ] Pre-approved research templates only
- [ ] Central review of findings before action
- [ ] No direct participant recruitment without ops approval
- [ ] Mandatory bias awareness training
- [ ] Clear escalation path for unexpected findings

---

## Researching Non-Technical User Segments (2026)

Quick checklist for research involving users with low digital literacy or low tech confidence. Full guidance in [references/non-technical-user-research.md](references/non-technical-user-research.md).

- [ ] Assess digital literacy tier (excluded → dependent → hesitant → capable → confident)
- [ ] Recruit via offline-first channels (community centers, libraries, phone outreach)
- [ ] Use plain-language screening questions (no jargon, no self-rating scales)
- [ ] Adapt methods: moderated-only testing, shorter sessions (30-40 min), read tasks aloud
- [ ] Measure: unassisted task completion (>=80%), time-to-first-value (<2 min), error recovery rate
- [ ] Frame findings as "inclusion improvements," not "dumbing down"
- [ ] Cross-reference with [simplification audit template](../software-ui-ux-design/assets/audits/simplification-audit-template.md)

---

## Measurement & Decision Quality (Core)

### Research ROI Quick Reference

| Research Activity | Proxy Metric | Calculation |
|-------------------|--------------|-------------|
| Usability testing finding | Prevented dev rework | Hours saved × $150/hr |
| Discovery interview | Prevented build-wrong-thing | Sprint cost × risk reduction % |
| A/B test conclusive result | Improved conversion | (ΔConversion × Traffic × LTV) - Test cost |
| Heuristic evaluation | Early defect detection | Defects found × Cost-to-fix-later |

**Rules of thumb**:
- 1 usability finding that prevents 40 hours of rework = **$6,000 value**
- 1 discovery insight that prevents 1 wasted sprint = **$50,000-100,000 value**
- Research that improves conversion 0.5% on 100k visitors × $50 LTV = **$25,000/month**

### When NOT to Run A/B Tests

| Situation | Why it fails | Better method |
|----------|--------------|---------------|
| Low power/traffic | Inconclusive results | Usability tests + trends |
| Many variables change | Attribution impossible | Prototype tests → staged rollout |
| Need “why” | Experiments don’t explain | Interviews + observation |
| Ethical constraints | Harmful denial | Phased rollout + holdouts |
| Long-term effects | Short tests miss delayed impact | Longitudinal + retention analysis |

### Common Confounds (Call Out Early)

Always check for these in experiment evaluations. List each relevant confound with its risk level and how to verify — do not just name them:

- Selection bias (only power users respond) — check segment composition.
- Survivorship bias (you miss churned users) — compare with cohort-level data.
- Novelty effect (short-term lift) — plot daily metrics to check for trend decay.
- Instrumentation changes mid-test (metrics drift) — confirm no concurrent deployments.
- Sample ratio mismatch (SRM) — run chi-square on assignment counts.
- Peeking / multiple looks — confirm test was not checked before pre-set end date.
- Feature interaction — check if other experiments ran concurrently on same surface.

---

## Optional: AI/Automation Research Considerations

> Use only when researching automation/AI-powered features. Skip for traditional software UX.
>
> **2026 benchmark**: Trend reports consistently highlight AI-assisted analysis. Use AI for speed while keeping humans responsible for strategy and interpretation. Example reference: https://www.lyssna.com/blog/ux-research-trends/

### Key Questions

| Dimension | Question | Methods |
|----------|----------|---------|
| Mental model | What do users think the system can/can’t do? | Interviews, concept tests |
| Trust calibration | When do users over/under-rely? | Scenario tests, log review |
| Explanation usefulness | Does “why” help decisions? | A/B explanation variants, interviews |
| Failure recovery | Do users recover and finish tasks? | Failure-path usability tests |

### Error Taxonomy (User-Visible)

| Failure type | Typical impact | What to measure |
|-------------|----------------|----------------|
| Wrong output | Rework, lost trust | Verification + override rate |
| Missing output | Manual fallback | Fallback completion rate |
| Unclear output | Confusion | Clarification requests |
| Non-recoverable failure | Blocked flow | Time-to-recovery, support contact |

### Optional: AI-Assisted Research Ops (Guardrailed)

- Use automation for transcription/tagging only after PII redaction.
- Maintain an audit trail: every theme links back to raw quotes/clips.

### Synthetic Users: When Appropriate (2026)

Trend reports frequently mention synthetic/AI participants. Use with clear boundaries. Example reference: https://www.lyssna.com/blog/ux-research-trends/

| Use Case | Appropriate? | Why |
|----------|--------------|-----|
| Early concept brainstorming | WARNING: Supplement only | Generate edge cases, not validation |
| Scenario/edge case expansion | PASS Yes | Broaden coverage before real testing |
| Moderator training/practice | PASS Yes | Practice without participant burden |
| Hypothesis generation | PASS Yes | Explore directions to test with real users |
| Validation/go-no-go decisions | FAIL Never | Cannot substitute lived experience |
| Usability findings as evidence | FAIL Never | Real behavior required |
| Quotes in reports | FAIL Never | Fabricated quotes damage credibility |

**Critical rule**: Synthetic outputs are **hypotheses**, not evidence. Always validate with real users before shipping.

---

## Navigation

### Resources

**Core Research Methods:**

- [references/research-frameworks.md](references/research-frameworks.md) — JTBD, Kano, Double Diamond, Service Blueprint, opportunity mapping
- [references/ux-audit-framework.md](references/ux-audit-framework.md) — Heuristic evaluation, cognitive walkthrough, severity rating
- [references/usability-testing-guide.md](references/usability-testing-guide.md) — Task design, facilitation, analysis
- [references/ux-metrics-framework.md](references/ux-metrics-framework.md) — Task metrics, SUS/HEART, measurement guidance
- [references/customer-journey-mapping.md](references/customer-journey-mapping.md) — Journey mapping and service blueprints
- [references/pain-point-extraction.md](references/pain-point-extraction.md) — Feedback-to-themes method
- [references/review-mining-playbook.md](references/review-mining-playbook.md) — B2B/B2C review mining

**Demographic & Quantitative Research:**

- [references/demographic-research-methods.md](references/demographic-research-methods.md) — Inclusive research for seniors, children, cultures, disabilities
- [references/non-technical-user-research.md](references/non-technical-user-research.md) — Research methods for non-technical and low-digital-literacy users
- [references/ab-testing-implementation.md](references/ab-testing-implementation.md) — A/B testing deep-dive (sample size, analysis, pitfalls)

**Competitive UX Analysis & Flow Patterns:**

- [references/competitive-ux-analysis.md](references/competitive-ux-analysis.md) — **Step-by-step flow patterns** from industry leaders (Wise, Revolut, Shopify, Notion, Linear, Stripe) + benchmarking methodology

**Research Operations & Methods:**

- [references/research-repository-management.md](references/research-repository-management.md) — Repository architecture, taxonomy, atomic research, PII handling, adoption metrics
- [references/survey-design-guide.md](references/survey-design-guide.md) — Question types, bias prevention, sampling, sample size, distribution, platform comparison
- [references/remote-research-patterns.md](references/remote-research-patterns.md) — Moderated remote, unmoderated testing, async methods, recruitment, tool comparison

**Feedback Collection & Analysis:**

- [references/bigtech-feedback-patterns.md](references/bigtech-feedback-patterns.md) — How top companies collect and act on user feedback
- [references/feedback-tools-guide.md](references/feedback-tools-guide.md) — Feedback collection tool setup guides and selection matrix

**Evaluative Iteration:**

- [references/evaluative-research-loop.md](references/evaluative-research-loop.md) — Prototype-parity polishing loop (two-surface audit, drift classification, fast iteration)

**Data & Sources:**

- [data/sources.json](data/sources.json) — Curated external references

---

## Domain-Specific UX Benchmarking

**IMPORTANT**: When designing UX flows for a specific domain, you MUST use WebSearch to find and suggest best-practice patterns from industry leaders.

### Trigger Conditions

- "We're designing [flow type] for [domain]"
- "What's the best UX for [feature] in [industry]?"
- "How do [Company A, Company B] handle [flow]?"
- "Benchmark our [feature] against competitors"
- Any UX design task with identifiable domain context

### Domain → Leader Lookup Table

| Domain | Industry Leaders to Check | Key Flows |
|--------|---------------------------|-----------|
| **Fintech/Banking** | Wise, Revolut, Monzo, N26, Chime, Mercury | Onboarding/KYC, money transfer, card management, spend analytics |
| **E-commerce** | Shopify, Amazon, Stripe Checkout | Checkout, cart, product pages, returns |
| **SaaS/B2B** | Linear, Notion, Figma, Slack, Airtable | Onboarding, settings, collaboration, permissions |
| **Developer Tools** | Stripe, Vercel, GitHub, Supabase | Docs, API explorer, dashboard, CLI |
| **Consumer Apps** | Spotify, Airbnb, Uber, Instagram | Discovery, booking, feed, social |
| **Healthcare** | Oscar, One Medical, Calm, Headspace | Appointment booking, records, compliance flows |
| **EdTech** | Duolingo, Coursera, Khan Academy | Onboarding, progress, gamification |

### Required Searches

When user specifies a domain, execute:

1. Search: `"[domain] UX best practices 2026"`
2. Search: `"[leader company] [flow type] UX"`
3. Search: `"[leader company] app review UX" site:mobbin.com OR site:pageflows.com`
4. Search: `"[domain] onboarding flow examples"`

### What to Report

After searching, provide:

- **Pattern examples**: Screenshots/flows from 2-3 industry leaders
- **Key patterns identified**: What they do well (with specifics)
- **Applicable to your flow**: How to adapt patterns
- **Differentiation opportunity**: Where you could improve on leaders

### Example Output Format

```text
DOMAIN: Fintech (Money Transfer)
BENCHMARKED: Wise, Revolut

WISE PATTERNS:
- Upfront fee transparency (shows exact fee before recipient input)
- Mid-transfer rate lock (shows countdown timer)
- Delivery time estimate per payment method
- Recipient validation (bank account check before send)

REVOLUT PATTERNS:
- Instant send to Revolut users (P2P first)
- Currency conversion preview with rate comparison
- Scheduled/recurring transfers prominent

APPLY TO YOUR FLOW:
1. Add fee transparency at step 1 (not step 3)
2. Show delivery estimate per payment rail
3. Consider rate lock feature for FX transfers

DIFFERENTIATION OPPORTUNITY:
- Neither shows historical rate chart—add "is now a good time?" context
```

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about UX research, you MUST use WebSearch to check current trends before answering.

### Tool/Trend Triggers

- "What's the best UX research tool for [use case]?"
- "What should I use for [usability testing/surveys/analytics]?"
- "What's the latest in UX research?"
- "Current best practices for [user interviews/A/B testing/accessibility]?"
- "Is [research method] still relevant in 2026?"
- "What research tools should I use?"
- "Best approach for [remote research/unmoderated testing]?"

### Tool/Trend Searches

1. Search: `"UX research trends 2026"`
2. Search: `"UX research tools best practices 2026"`
3. Search: `"[Maze/Hotjar/UserTesting] comparison 2026"`
4. Search: `"AI in UX research 2026"`

### Tool/Trend Report Format

After searching, provide:

- **Current landscape**: What research methods/tools are popular NOW
- **Emerging trends**: New techniques or tools gaining traction
- **Deprecated/declining**: Methods that are losing effectiveness
- **Recommendation**: Based on fresh data and current practices

### Example Topics (verify with fresh search)

- AI-powered research tools (Maze AI, Looppanel)
- Unmoderated testing platforms evolution
- Voice of Customer (VoC) platforms
- Analytics and behavioral tools (Hotjar, FullStory)
- Accessibility testing tools and standards
- Research repository and insight management

---

### Templates

- Shared plan template: [../software-clean-code-standard/assets/checklists/ux-research-plan-template.md](../software-clean-code-standard/assets/checklists/ux-research-plan-template.md) — Product-agnostic research plan template (core + optional AI)
- [assets/research-plan-template.md](assets/research-plan-template.md) — UX research plan template
- [assets/testing/usability-test-plan.md](assets/testing/usability-test-plan.md) — Usability test plan
- [assets/testing/usability-testing-checklist.md](assets/testing/usability-testing-checklist.md) — Usability testing checklist
- [assets/audits/heuristic-evaluation-template.md](assets/audits/heuristic-evaluation-template.md) — Heuristic evaluation
- [assets/audits/ux-audit-report-template.md](assets/audits/ux-audit-report-template.md) — Audit report

---

## Evaluative Research Loop

For prototype-parity polishing (fast iteration when product is "almost ideal"), see [references/evaluative-research-loop.md](references/evaluative-research-loop.md). Covers: two-surface audit, drift classification (layout/density/control/content/state), friction-based prioritization, banner/loading guardrails, localization-readiness checks, and fast iteration cadence.

## Fact-Checking

- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.
