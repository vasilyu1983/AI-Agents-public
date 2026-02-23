---
name: startup-go-to-market
description: Use when designing go-to-market strategy, selecting GTM motion (PLG/sales-led/partner-led), defining ICP, planning product launches, designing partnership and channel partner programs, or implementing AI-powered GTM automation. Covers channel selection, growth loops, partnership strategy, RevOps alignment, and market entry execution.
---

# Startup Go-to-Market

Systematic workflow for designing and executing market entry, launch, and growth.

**Modern Best Practices (Jan 2026)**: Start from ICP + positioning, pick 1-2 channels to sequence, instrument the funnel end-to-end, use AI for execution (not strategy), align RevOps across sales/marketing/CS.

---

## When to Use

- Designing go-to-market strategy for new product
- Choosing between PLG and sales-led motion
- Planning product launches (soft, beta, ProductHunt, full)
- Defining ICP and channel strategy
- Designing partnership and channel partner programs
- Evaluating partner types and partner-led distribution
- Implementing AI-powered GTM automation

## When NOT to Use

- Positioning and messaging deep dive -> [marketing-content-strategy](../marketing-content-strategy/) (use [startup-competitive-analysis](../startup-competitive-analysis/) for differentiation inputs)
- Competitive intelligence -> [startup-competitive-analysis](../startup-competitive-analysis/)
- Fundraising strategy -> [startup-fundraising](../startup-fundraising/)
- Pricing and revenue models -> [startup-business-models](../startup-business-models/)
- Closing deals, discovery calls, negotiation, procurement -> [startup-sales-execution](../startup-sales-execution/)
- Onboarding, retention, renewals, expansion -> [startup-customer-success](../startup-customer-success/)
- Finance operations (cash runway, billing/collections, close cadence) -> [startup-finance-ops](../startup-finance-ops/)
- Legal basics (contracts, IP assignments, privacy fundamentals) -> [startup-legal-basics](../startup-legal-basics/)
- Hiring/management for the first team -> [startup-hiring-and-management](../startup-hiring-and-management/)

---

## Quick Start (Inputs)

Ask for the smallest set of inputs that makes decisions meaningful:

- Stage: pre-PMF, early PMF, growth, scale
- Product and category: what it is, who uses it, and what "first value" looks like
- ICP and buyer: firmographics, pains, procurement constraints, economic buyer vs champion
- Pricing and economics: current/target ACV/ARPA, COGS drivers (include variable compute), payback constraints
- Motion constraints: self-serve possible, sales cycle expectations, implementation/onboarding complexity
- Channel constraints: budget, time, audience access (communities, lists, partnerships), geo, compliance limits
- Baseline metrics: traffic, signup/demo rate, activation, retention, win rate, sales cycle length, pipeline
- Team and tooling: who executes (founder/marketing/sales/CS), CRM + analytics stack

If numbers are missing, proceed with ranges + explicit assumptions and list what to measure next.

## Workflow

1) Define ICP and the buying path
- Primary/secondary ICP, anti-ICP, trigger events, and an "activation" definition.
- Use `assets/icp-definition.md` to draft.

2) Align on positioning and proof
- If positioning is unclear, use [startup-competitive-analysis](../startup-competitive-analysis/) to map alternatives + differentiation, then [marketing-content-strategy](../marketing-content-strategy/) to express it as messaging.

3) Choose the motion (PLG / sales-led / hybrid)
- Use the decision tree below for a fast cut.
- For details: `references/plg-implementation.md` and `references/sales-motion-design.md`.
 - For founder-led closing and a repeatable pipeline: [startup-sales-execution](../startup-sales-execution/).

4) Pick 1-2 channels to sequence (not parallelize)
- Use a bullseye-style test plan: quick tests, measure, double down.
- For execution details: `references/channel-playbooks.md`.

5) Define measurement and RevOps alignment
- Define shared lifecycle stages and the "one source of truth" for metrics (product + CRM).
- Ensure handoffs are measurable (e.g., PQL -> SQL routing rules and SLAs for hybrid).
 - Define post-sale ownership (onboarding, retention) and the minimum CS metrics to track.

6) Produce deliverables + operating cadence
- Draft GTM plan (`assets/gtm-strategy.md`) and launch plan (`assets/launch-playbook.md`).
- Run a weekly GTM review: 30 minutes on pipeline + funnel, 30 minutes on experiments, 30 minutes on decisions.

---

## Decision Tree

```
GTM QUESTION
  |-- "How do I reach customers?" -> Channel Strategy
  |-- "PLG or Sales-led?" -> Motion Selection
  |-- "How do I launch?" -> Launch Planning
  |-- "Who is my ICP?" -> Segmentation
  `-- "How do I scale?" -> Growth Loops
```

---

## GTM Motion Types

| Motion | Description | Best For | Examples |
|--------|-------------|----------|----------|
| **PLG** | Product drives acquisition, conversion, expansion | SMB, developers | Slack, Figma |
| **Hybrid (PLG + Sales-Assist)** | Product drives acquisition; sales assists conversion/expansion | Mid-market, higher ACV PLG | Atlassian, Notion |
| **Sales-Led** | Reps drive deals through outbound/inbound | Enterprise, complex sales | Salesforce |
| **Community-Led** | Community drives awareness and adoption | Developer tools, OSS | MongoDB |
| **Partner-Led** | Partners drive distribution | Enterprise, geographic expansion | Microsoft |

### Motion Selection Framework

```
ACV < $5K and self-serve possible?
  - yes: PLG (add sales-assist for expansion)
  - no: is buyer technical?
      - yes: developer/community-led (bottom-up)
      - no: sales-led
```

---

## ICP Components

| Component | Questions | Example |
|-----------|-----------|---------|
| **Firmographics** | Size, industry, geography | 50-500 employees, B2B SaaS, US |
| **Technographics** | Tech stack, tools | Uses Salesforce, modern data stack |
| **Pain indicators** | Symptoms of problem | Growing support tickets |
| **Success indicators** | Signs of good fit | Strong product-market alignment |

### ICP Scoring

| Factor | Weight |
|--------|--------|
| Budget available | 20% |
| Problem severity | 25% |
| Technical fit | 15% |
| Decision timeline | 15% |
| Champion identified | 15% |
| Expansion potential | 10% |

---

## Channel Strategy

| Category | Channels | Best For |
|----------|----------|----------|
| **Organic** | SEO, content, social, community | Long-term |
| **Paid** | SEM, paid social, display | Fast, scalable |
| **Outbound** | Email, cold calls, LinkedIn | Enterprise, high ACV |
| **Product** | Viral, freemium, PLG | Self-serve |

### Channel Sequencing by Stage

| Stage | Primary Channels |
|-------|------------------|
| Pre-PMF | Founder sales, communities |
| Early | Content, outbound, founder network |
| Growth | Paid, SEO, partnerships |
| Scale | All channels optimized |

---

## Measurement (Minimum Viable GTM Analytics)

- Prefer lifecycle + cohorts over vanity metrics. Always break down by ICP/segment + channel.
- Define a single funnel per motion (PLG vs sales-led) with clear stage definitions and owners.
- Track leading indicators (activation/retention, PQL, win rate) before "scale" decisions.

**PQL (Product Qualified Lead) Score**:
```
PQL = (Engagement * 0.4) + (Fit * 0.3) + (Intent * 0.3)
```

### Product-Led Sales (Sales-Assist) Basics

Use when PLG brings users in, but conversion/expansion benefits from a human touch.

**PQL -> SQL routing checklist**:
- [ ] Define PQL triggers (events) and thresholds (e.g., 3 key actions in 7 days)
- [ ] Define disqualifiers (students, competitors, tiny companies, unsupported geo)
- [ ] Set an SLA for first touch (e.g., <24 hours for high-intent PQLs)
- [ ] Define handoff criteria to AE (PQL -> meeting booked, security/procurement requested)
- [ ] Instrument outcomes (PQL->meeting->pipeline->won) and review weekly

---

## Launch Types

| Type | Goal | Timeline |
|------|------|----------|
| **Soft launch** | Test, iterate | 2-4 weeks |
| **Beta launch** | Build waitlist, feedback | 4-8 weeks |
| **ProductHunt** | Awareness, early adopters | 1 day + prep |
| **Full launch** | Maximum awareness | 1-2 weeks |

---

## Growth Loops

| Loop | Mechanism | Example |
|------|-----------|---------|
| **Viral** | User invites users | Dropbox referrals |
| **Content** | Content -> SEO -> Users | HubSpot |
| **UGC** | Users create content | YouTube |
| **Paid** | Revenue -> Ads -> Users | Performance marketing |
| **Sales** | Pipeline -> close -> revenue -> hiring -> more pipeline | Sales-led SaaS |
| **Partner** | Enable partners -> referrals -> deals -> partner revenue -> more partners | Cloud marketplaces |

---

## Partnership Strategy

Partnerships are a GTM channel, not a strategy. Treat them like any other channel: qualify, pilot, measure, scale or kill.

### Partner Types

| Type | What They Do | Economics | Best For |
|------|-------------|-----------|----------|
| **Integration / tech** | Build a joint product experience | Free or rev share on co-sold deals | Stickiness, product value |
| **Referral / affiliate** | Send qualified leads your way | 10-30% of first-year revenue (typical) | Low-touch, high-volume |
| **Reseller / channel** | Sell and support your product | 20-40% margin to partner | Geographic expansion, enterprise |
| **Co-selling** | Joint sales motions on shared accounts | Shared pipeline, no margin | Enterprise, complex deals |
| **Marketplace** | List on AWS/Azure/GCP/Salesforce | 3-20% marketplace fee | Enterprise procurement, discovery |

### Partnership Readiness Checklist

Do NOT pursue partnerships until:
- You have a repeatable direct sales motion (partners amplify, they don't create PMF)
- You can articulate mutual value (not just "they have customers we want")
- You can support partner-sourced customers without degrading direct customer experience
- You have someone (founder or hire) who owns the partnership

### Partnership Funnel

1. **Identify** — Map potential partners by audience overlap and incentive alignment
2. **Qualify** — Score fit: audience match, technical compatibility, business model alignment, champion access
3. **Pilot** — Run a small co-marketing or co-selling experiment with 1-2 partners (30-60 days)
4. **Measure** — Track partner-sourced pipeline, conversion, revenue, and support load
5. **Scale or kill** — Double down on partners that produce ROI; exit partnerships that don't

### When Partnerships Are Premature

- Pre-PMF (you don't know your own ICP yet — partners will amplify confusion)
- No direct sales process (you can't teach partners what you haven't figured out)
- Product requires heavy customization per deal (partners can't replicate your expertise)

For BD execution (outreach, deal structures, negotiation): see [startup-sales-execution](../startup-sales-execution/).
For deeper partnership strategy patterns: see `references/partnership-strategy.md`.

---

## Do / Avoid

### Do

- Define activation as concrete "first value moment"
- Track leading indicators (activation, PQL, retention)
- Use AI for execution while humans own strategy
- Tier ICP based on fit + intent signals

### Avoid

- Content spam without measurement
- "Do all channels" in parallel
- Vanity metrics without retention context
- Over-automating without human oversight
- Scaling paid before activation/retention is stable
- Treating benchmarks as targets without segmenting by ICP/channel

---

## Resources

| Resource | Purpose |
|----------|---------|
| [channel-playbooks.md](references/channel-playbooks.md) | Detailed channel execution |
| [sales-motion-design.md](references/sales-motion-design.md) | Sales process + RevOps |
| [plg-implementation.md](references/plg-implementation.md) | PLG execution + PQL frameworks |
| [ai-gtm-automation.md](references/ai-gtm-automation.md) | AI-powered GTM tools |
| [partnership-strategy.md](references/partnership-strategy.md) | Partner types, program design, marketplace listing, co-marketing |
| [launch-execution-guide.md](references/launch-execution-guide.md) | Launch types, timelines, day-of playbook, ProductHunt, post-launch analysis |
| [icp-research-methodology.md](references/icp-research-methodology.md) | ICP research, validation, scoring, tiering, anti-ICP, documentation |
| [revops-alignment.md](references/revops-alignment.md) | RevOps lifecycle stages, handoffs, SLAs, attribution, forecasting, reporting |

## Templates

| Template | Purpose |
|----------|---------|
| [gtm-strategy.md](assets/gtm-strategy.md) | Full GTM strategy document |
| [launch-playbook.md](assets/launch-playbook.md) | Launch planning |
| [icp-definition.md](assets/icp-definition.md) | ICP documentation |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | GTM resources |

---

## Related Skills

| Skill | Use For |
|-------|---------|
| [startup-competitive-analysis](../startup-competitive-analysis/) | Market mapping, battlecards |
| [startup-business-models](../startup-business-models/) | Pricing, unit economics |
| [startup-sales-execution](../startup-sales-execution/) | Discovery, qualification, closing, negotiation |
| [startup-customer-success](../startup-customer-success/) | Onboarding, retention, renewals, expansion |
| [startup-finance-ops](../startup-finance-ops/) | Cash runway, billing/collections, finance cadence |
| [startup-legal-basics](../startup-legal-basics/) | IP/contract/privacy readiness for selling |
| [startup-hiring-and-management](../startup-hiring-and-management/) | First hires, interview loops, management cadence |
| [marketing-ai-search-optimization](../marketing-ai-search-optimization/) | GEO/AI search visibility for content-led GTM |
| [marketing-social-media](../marketing-social-media/) | Social channel execution |
| [marketing-leads-generation](../marketing-leads-generation/) | Lead acquisition |
| [startup-growth-playbooks](../startup-growth-playbooks/) | Case studies with numbers, stage-specific growth tactics |

---

## What Good Looks Like

- One primary ICP with clear anti-ICP and measurable triggers (signals) for targeting.
- A motion decision with explicit economics (ACV, payback, touch model) and defined handoffs.
- One primary channel with a test plan, success metrics, and stop/pivot triggers.
- Instrumented funnel from source -> activation/value -> revenue/expansion (by segment + channel).
- A weekly operating cadence with a backlog of experiments and a written decision log.
