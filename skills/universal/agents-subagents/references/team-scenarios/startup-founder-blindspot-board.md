---
description: Startup Founder Blindspot Board — extracted from monolith for progressive disclosure.
last_verified: 2026-08-26
status: stable
---

## Startup Founder Blindspot Board

**Typical scenario**

Growth is ambiguous. The founder suspects something important is being missed, but it is not clear whether the issue is messaging, wedge, segment, or timing.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "founder-blindspot"`.

Scenario: A startup has steady traffic and signups, mixed activation, and weak monetization. The founder feels there may be a better wedge or segment hidden in the current market signal.

Required context:
- Target customer: operations leaders in SMB and mid-market teams
- Current signs: people sign up, some activate, paid conversion is weak
- Inputs: competitor notes, customer complaints, support themes, and public reviews

Instructions:
- startup-painpoint-scout maps repeated pain and workflow friction
- startup-review-miner extracts user language, switching triggers, and objections
- startup-trend-analyst checks timing and adjacent market shifts
- startup-competitive-analyst checks what competitors may be seeing first
- product-strategist synthesizes the founder memo
- Run independently first
- Then debate whether the best next move is a narrower wedge, a new segment, a timing adjustment, or a messaging correction
- Include what not to chase
- Clean up the team when done
```

**Codex prompt**

```text
Spawn generic role-brief workers for pain-point discovery, review mining, trend analysis, competition, and product strategy in parallel.

Task: Find the hidden opportunities or ignored objections behind mixed growth and weak monetization.

Context:
- traffic and signups exist
- activation is mixed
- paid conversion is weak
- evidence includes reviews, support themes, objections, and competitor notes

Rules:
- each agent returns a short memo first
- then run a debate on wedge vs segment vs timing vs messaging
- synthesize a final founder memo with the best narrow wedge and what not to chase
```

**Debate-first variant**

Use when the core disagreement is "we need a new segment" versus "we already have the right segment but the wrong story."

---

**Typical scenario (variant: new niche validation / greenfield)**

Founder is evaluating whether to build a new app in a niche they have not entered yet. There is no existing product to defend — only the question of whether the niche is real, defensible, and worth shipping. This variant uses the same workflow mode but pins each role brief to its canonical skill artifact so the output is auditable evidence, not narrative prose.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "founder-blindspot"` and state `new-niche-validation` in the question and context.

Scenario: Founder is deciding whether to build an iOS app in a new niche. No prior product, no prior users — only the question "is this niche real, defensible, and worth shipping in 2026?".

Required context:
- Target niche: <one-sentence description of the niche / job-to-be-done>
- Founder stack/skill fit: <e.g., Swift + SwiftUI, solo, $0 marketing budget>
- Geography/locale: <e.g., UK + US English-speaking>
- Time-to-revenue constraint: <e.g., must reach £500 MRR within 90 days or kill>
- Competitor list (3–5): <named competitors to mine for switching triggers>
- Optional: any adjacent PostHog or App Store Connect data from existing apps

Instructions (each member produces its canonical artifact, not narrative):
- startup-painpoint-scout: produce a `painpoint-scan-report.md` from `research-painpoint-scanner` covering 7d/30d/90d windows across reddit, hn, app-store reviews. Required fields per cluster: pain_dimension, theme, severity_1_5, frequency, evidence (≥3 threads with thread_url + source_context + verbatim quote), windows trend direction, cross-source corroboration (top 3 themes in ≥2 sources).
- startup-review-miner: produce a `switching-trigger-analysis.md` + `review-evidence-ledger.tsv` from `research-review-mining` for the 3–5 named competitors. Required scoring fields: frequency (unique reviewers), severity_1_5, segment_importance, addressability_1_5, confidence_1_3, evidence_quotes with source_url.
- startup-trend-analyst: produce a `timing memo` from `startup-market-intel`. Required: evidence stack (strong vs weak signals), verdict (enter/wait/monitor/avoid), confidence, review trigger with calendar date, ≥1 counter-signal.
- startup-competitive-analyst: produce competitive landscape + moat assessment for the 3–5 named competitors.
- product-strategist (synthesis owner): produce a `validation-scorecard.md` from `startup-idea-validation` — 9-dimension scorecard (Problem Severity 15%, Market Size 12%, Market Timing 10%, Competitive Moat 12%, Unit Economics 15%, Founder-Market Fit 8%, Technical Feasibility 10%, GTM Clarity 10%, Risk 8%) with verdict thresholds GO ≥80, CONDITIONAL 60–79, PIVOT 40–59, NO-GO <40, plus a Riskiest Assumption Test (RAT) canvas. Embed the four upstream artifacts verbatim as appendix — synthesis sits ON TOP of them, not instead of them.

Execution mode: run all four data-gathering members in parallel, then product-strategist synthesizes.

Debate trigger: only if scorecard verdict and trend timing disagree, or if painpoint frequency is high but addressability is low.

Cleanup: close the team after the scorecard is produced.
```

**Codex prompt**

```text
Spawn generic role-brief workers for pain-point discovery, review mining, trend analysis, competition, and product strategy. Mode: new-niche validation.

Task: Decide whether founder should build an iOS app in <niche>. Output must be auditable artifacts, not narrative.

Context:
- target niche: <one-sentence>
- founder stack/skill fit: <e.g., Swift + SwiftUI, solo>
- geography: <e.g., UK + US>
- time-to-revenue constraint: <e.g., £500 MRR in 90 days>
- competitor list (3–5): <named>

Per-member artifact assignment (mandatory):
- painpoint_scout → painpoint-scan-report.md (painpoint-scanner schema: pain_dimension, theme, severity_1_5, frequency, evidence ≥3 threads, 7d/30d/90d trend, cross-source)
- review_miner → switching-trigger-analysis.md + review-evidence-ledger.tsv (review-mining schema: frequency, severity_1_5, segment_importance, addressability_1_5, confidence_1_3, evidence_quotes)
- trend_analyst → timing memo (trend-prediction schema: evidence stack, verdict enter/wait/monitor/avoid, confidence, review trigger, ≥1 counter-signal)
- competitive_analyst → competitive landscape + moat for 3–5 named competitors
- product_strategist → validation-scorecard.md (idea-validation 9-dimension scorecard with weights, verdict GO/CONDITIONAL/PIVOT/NO-GO, RAT canvas)

Rules:
- each member returns its canonical artifact first
- if any member cannot run because of missing tool access, abort with GATING DATA GAP — do not produce partial narrative
- product_strategist embeds the four upstream artifacts verbatim as appendix
- debate only if scorecard verdict and trend verdict disagree
```

**Debate-first variant (new-niche)**

Skip debate when the four artifacts converge on the same verdict. Engage debate only when the trend memo says "enter" but the scorecard says "PIVOT" (or vice versa) — that's where the founder's blind spot lives.
