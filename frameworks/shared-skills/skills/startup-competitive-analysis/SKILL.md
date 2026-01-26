---
name: startup-competitive-analysis
description: "Competitive analysis for startups: identify and segment competitors (direct/indirect/substitutes/status quo), map markets, build sales battlecards, run win/loss + churn analyses, and refine positioning/differentiation. Use when asked to compare products vs competitors, define competitive alternatives, explain category structure, or set up competitive intelligence monitoring and update cadences."
---

# Startup Competitive Analysis

Use this skill to produce decision-oriented competitive intelligence: define the competitive set, collect evidence, synthesize `match / ignore / bet` decisions, and ship practical artifacts teams can use (briefs, landscapes, battlecards, win/loss).

## Operating Principles (2026)

- Prefer decisions over inventories: make explicit `match / ignore / bet` calls with rationale and owner.
- Treat competitor claims as hypotheses: validate with buyer reality and current evidence.
- Date-stamp key claims and keep an evidence trail (link + capture month).
- Triangulate important facts across sources (at least two).
- Stay ethical: respect ToS; don’t scrape behind auth/paywalls; don’t misrepresent identity.

## Intake Checklist (Ask First)

- Objective: sales enablement, positioning, strategy, fundraising, churn reduction
- Market: category, geography, segment (ICP), and time horizon (now vs 6–12 months)
- Known competitors and “do nothing” alternative (status quo / DIY / services)
- Constraints: available sources, web access, internal docs, legal/compliance requirements

## Choose the Right Output

| If the user asks… | Produce… | Use… |
|---|---|---|
| “Who are the competitors?” / “Map the landscape” | Market map + competitor set | `references/market-mapping-guide.md`, `assets/competitive-landscape.md` |
| “How do we differentiate?” / “What category are we in?” | Category structure + differentiation thesis | `references/industry-structure-and-differentiation.md`, `assets/competitive-analysis-brief.md` |
| “How should we position?” | Positioning canvas + statement + tests | `references/positioning-playbook.md`, `assets/competitive-analysis-brief.md` |
| “Deep dive Competitor X” | Deep dive + (optional) battlecard | `references/competitor-deep-dive.md`, `assets/battlecard.md` |
| “Why are we losing to X?” / “What’s driving churn?” | Win/loss + churn patterns + remediation | `assets/win-loss-analysis.md` |

## Workflow

1. Define the competitive set: direct/indirect/substitutes/status quo, segmented by ICP and job-to-be-done.
2. Collect evidence: product/docs/pricing, changelogs, job postings, reviews/VoC, partnerships, distribution signals.
3. Analyze on buyer criteria: switching costs, time-to-value, risk/procurement, integration ecosystem, ROI proof.
4. Synthesize into decisions: `match/ignore/bet`, wedge, proof points, landmines, and “walk-away” criteria.
5. Produce artifacts: narrative brief, landscape, battlecards, win/loss summary (use bundled templates).
6. Operationalize: set an update cadence and monitoring sources; refresh battlecards and decisions as signals change.

## Evidence & Freshness Rules

- Prefer primary sources first (docs, pricing pages, release notes, filings), then triangulate.
- Use dated evidence labels like `[YYYY-MM]` and include the source URL.
- If web search is available, verify “current state” (pricing, positioning, major launches, funding, M&A). If not, state the limitation and proceed with provided context.

## Lightweight CI Monitoring (No Tool Assumptions)

- Seed sources from `data/sources.json`; add category-specific sources for the market.
- Track changes to: pricing pages, docs/changelogs, security/compliance pages, partner directories, job postings, ad libraries, review sites.
- Keep a simple change log and review it on a fixed cadence (weekly/monthly/quarterly based on sales cycle).

## Resources

| Resource | Purpose |
|----------|---------|
| [competitor-deep-dive.md](references/competitor-deep-dive.md) | Full competitor analysis framework |
| [market-mapping-guide.md](references/market-mapping-guide.md) | Market map creation |
| [positioning-playbook.md](references/positioning-playbook.md) | Positioning methodology |
| [industry-structure-and-differentiation.md](references/industry-structure-and-differentiation.md) | Porter 5 Forces + JTBD alternatives + strategy canvas |

## Templates

| Template | Purpose |
|----------|---------|
| [competitive-analysis-brief.md](assets/competitive-analysis-brief.md) | Decision-oriented narrative brief |
| [competitive-landscape.md](assets/competitive-landscape.md) | Full competitive overview |
| [battlecard.md](assets/battlecard.md) | Sales enablement |
| [win-loss-analysis.md](assets/win-loss-analysis.md) | Deal analysis |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | Competitive intelligence sources |
