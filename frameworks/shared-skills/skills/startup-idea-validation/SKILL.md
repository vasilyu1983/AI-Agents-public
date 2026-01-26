---
name: startup-idea-validation
description: "Use when validating a startup idea before building. Produces evidence-based GO/NO-GO decisions using a 9-dimension scorecard (problem, market, timing, moat, unit economics, founder-market fit, feasibility, GTM, risk), a validation ladder (interviews -> smoke test -> concierge/WoZ -> paid pilot), and riskiest-assumption-first experiments."
---

# Startup Idea Validation

Systematic validation for testing ideas before building: define hypotheses, collect evidence, score the opportunity, and make a decision you can defend.

## Operating Principles (2026)

- Prefer decisions over inventories: each dimension ends with `GO / CONDITIONAL / PIVOT / NO-GO` and a next action.
- Separate evidence quality from confidence: weak evidence cannot justify a high score.
- Pre-register thresholds and stop rules before running experiments (avoid moving goalposts).
- Validate willingness-to-pay and time-to-value early (price is part of the product).
- Calibrate thresholds to the target outcome (venture-scale vs cash-flow business) and business model (B2B SaaS, B2C, marketplace, services).
- Stay safe and ethical: no misrepresentation, respect ToS, and handle customer data with minimization and retention limits.

## Intake Checklist (Ask First)

- One-sentence idea + target user + job-to-be-done
- Business model: B2B/B2C, SaaS/usage-based/marketplace/services, ACV/ARPU range
- Geography, constraints (regulated domain, procurement/security requirements, data access)
- Target outcome: venture-scale, profitable small business, or thesis-driven R&D
- Current evidence: interviews, pilots, pre-sales, traffic, competitor list, pricing assumptions

## Choose the Right Output

| If the user asks… | Produce… | Use… |
|---|---|---|
| “Validate this idea” / “Is this worth building?” | 9-dimension scorecard + verdict | [validation-scorecard.md](assets/validation-scorecard.md), [go-no-go-decision.md](assets/go-no-go-decision.md) |
| “What’s the riskiest assumption?” | RAT + test plan | [riskiest-assumption-test.md](assets/riskiest-assumption-test.md), [validation-experiment-planner.md](assets/validation-experiment-planner.md) |
| “Test my hypothesis” | Hypothesis canvas + experiment design | [hypothesis-canvas.md](assets/hypothesis-canvas.md), [hypothesis-testing-guide.md](references/hypothesis-testing-guide.md) |
| “Market size for X” | TAM/SAM/SOM sizing + assumptions table | [market-sizing-worksheet.md](assets/market-sizing-worksheet.md), [market-sizing-patterns.md](references/market-sizing-patterns.md) |
| “Can this be profitable / what’s my runway?” | Unit economics + runway + scenarios | [financial-modeling-calculator.md](assets/financial-modeling-calculator.md) |
| “Should I build X or Y?” | Comparative scorecard + decision memo | [validation-scorecard.md](assets/validation-scorecard.md), [go-no-go-decision.md](assets/go-no-go-decision.md) |

## Workflow

1. Clarify the target outcome and business model; set default thresholds accordingly.
2. Identify the RAT (the assumption that kills the business if wrong).
3. Plan the validation ladder: interviews -> smoke test -> concierge/WoZ -> paid pilot.
4. Run the cheapest falsifiable test first; pre-register PASS/FAIL thresholds and stop rules.
5. Score all 9 dimensions using evidence; downgrade scores when evidence is weak.
6. Produce a decision memo: verdict, why, what would change the decision, and the next smallest reversible step.

## 9-Dimension Scorecard

| Dimension | Weight | What it measures |
|---|---:|---|
| Problem severity | 15% | Urgency, cost of inaction, current workarounds |
| Market size | 12% | Sufficient demand for the target outcome |
| Market timing | 10% | Clear “why now” and tailwinds |
| Competitive moat | 12% | Defensibility over time |
| Unit economics | 15% | Profit path (incl. payback and margins) |
| Founder-market fit | 8% | Access, expertise, and execution capability |
| Technical feasibility | 10% | Buildability, dependencies, constraints |
| GTM clarity | 10% | ICP, channels, motion, first customers |
| Risk profile | 8% | What can kill it and likelihood |

**Verdict thresholds (default)**:
- `80–100`: GO
- `60–79`: CONDITIONAL (validate RAT first)
- `40–59`: PIVOT
- `<40`: NO-GO

Deep scoring rubrics and calibration live in [validation-methodology.md](references/validation-methodology.md).

## Evidence Rules

- Strong evidence is behavioral commitment with cost (time, money, switching, access); weak evidence is opinions and hypotheticals.
- Triangulate important claims across at least two sources (especially market sizing and competitor state).
- Keep an evidence trail: link + capture month; separate “fact” vs “assumption”.

## Validation Ladder (Default)

| Step | Goal | Strong signal |
|---|---|---|
| Interviews | Validate the problem and context | Repeated pain with real workarounds and spend |
| Smoke test | Validate demand | Qualified conversion with price shown |
| Concierge/WoZ | Validate workflow value | Users complete the job and return |
| Paid pilot | Validate willingness-to-pay | Paid, renewed, or expanded |

## AI / Automation Notes (2026)

If the idea depends on AI (agents, copilots, automation), validate these explicitly:

- Data rights and access: can you legally and reliably access required data?
- Reliability: define success metrics, failure modes, and human fallback; validate on real workflows.
- Cost-to-serve: model inference + retrieval + human-in-the-loop costs in `assets/financial-modeling-calculator.md`.

See [hypothesis-testing-guide.md](references/hypothesis-testing-guide.md) for AI-specific experiment patterns.

## Integration Points

### Receives From

- [startup-review-mining](../startup-review-mining/SKILL.md) - Pain point evidence
- [startup-trend-prediction](../startup-trend-prediction/SKILL.md) - Market timing inputs
- [startup-competitive-analysis](../startup-competitive-analysis/SKILL.md) - Competitor landscape

### Feeds Into

- [router-startup](../router-startup/SKILL.md) - Startup decision routing
- [product-management](../product-management/SKILL.md) - Validated requirements and roadmap inputs
- [startup-business-models](../startup-business-models/SKILL.md) - Monetization and packaging decisions

## Resources

| Resource | Purpose |
|---|---|
| [validation-methodology.md](references/validation-methodology.md) | Scoring rubrics and calibration |
| [hypothesis-testing-guide.md](references/hypothesis-testing-guide.md) | Experiment design and RAT workflows |
| [market-sizing-patterns.md](references/market-sizing-patterns.md) | TAM/SAM/SOM methods and pitfalls |
| [moat-assessment-framework.md](references/moat-assessment-framework.md) | Defensibility analysis |

## Templates

| Template | Purpose |
|---|---|
| [validation-scorecard.md](assets/validation-scorecard.md) | Full 9-dimension scoring |
| [go-no-go-decision.md](assets/go-no-go-decision.md) | Decision memo format |
| [hypothesis-canvas.md](assets/hypothesis-canvas.md) | Hypothesis definition |
| [validation-experiment-planner.md](assets/validation-experiment-planner.md) | Experiment planning + thresholds |
| [riskiest-assumption-test.md](assets/riskiest-assumption-test.md) | RAT identification and test design |
| [market-sizing-worksheet.md](assets/market-sizing-worksheet.md) | Sizing worksheet |
| [financial-modeling-calculator.md](assets/financial-modeling-calculator.md) | Runway + scenarios + unit economics |

## Data

| File | Purpose |
|---|---|
| [sources.json](data/sources.json) | Curated validation resources |
