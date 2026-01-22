---
name: startup-go-to-market
description: GTM strategy, channel selection, launch planning, AI-powered automation, and market entry execution
metadata:
  version: "2.0"
---

# Startup Go-to-Market

Systematic framework for designing and executing market entry strategies.

**Modern Best Practices (Jan 2026)**:
- Start from ICP + positioning, then pick 1–2 channels to sequence (avoid "all channels").
- Instrument the funnel end-to-end (activation and retention defined, not assumed).
- Use tight feedback loops (weekly learning reviews) and write stop/pivot thresholds.
- Leverage AI-powered GTM tools for lead enrichment, personalized outreach, and pipeline intelligence.
- Align RevOps across sales, marketing, and CS—75% of fastest-growing companies have RevOps by 2026.
- Treat customer data with purpose limitation, retention, and access controls.

---

## Decision Tree: What GTM Analysis?

```
GTM QUESTION
    │
    ├─► "How do I reach customers?" ───► Channel Strategy
    │                                     └─► Channel selection, sequencing
    │
    ├─► "PLG or Sales-led?" ───────────► Motion Selection
    │                                     └─► GTM motion design
    │
    ├─► "How do I launch?" ────────────► Launch Planning
    │                                     └─► Launch playbook
    │
    ├─► "Who is my ICP?" ──────────────► Segmentation
    │                                     └─► ICP definition, targeting
    │
    ├─► "How do I scale?" ─────────────► Scaling Strategy
    │                                     └─► Growth loops, expansion
    │
    └─► "Full GTM strategy" ───────────► COMPREHENSIVE ANALYSIS
                                          └─► All dimensions
```

---

## GTM Motion Types

### Motion Taxonomy

| Motion | Description | Best For | Examples |
|--------|-------------|----------|----------|
| **Product-Led Growth (PLG)** | Product drives acquisition, conversion, expansion | SMB, developers, horizontal | Slack, Figma, Notion |
| **Sales-Led** | Reps drive deals through outbound and inbound | Enterprise, complex sales | Salesforce, Workday |
| **Community-Led** | Community drives awareness and adoption | Developer tools, open source | Hashicorp, MongoDB |
| **Channel/Partner-Led** | Partners drive distribution | Enterprise, geographic expansion | Microsoft, Cisco |
| **Marketing-Led** | Marketing drives demand generation | B2C, SMB | HubSpot, Mailchimp |

### Motion Selection Framework

```
ACV < $5K + Self-serve possible?
    │
    ├─► YES ──► PLG (primary)
    │              └─► Add Sales-assist for expansion
    │
    └─► NO ───► Is buyer technical?
                    │
                    ├─► YES ──► Developer/Community-Led
                    │              └─► Bottom-up adoption
                    │
                    └─► NO ───► Sales-Led
                                   └─► Inbound + Outbound
```

### Hybrid Motions (2025-2026 Reality)

| Hybrid | Components | Examples |
|--------|------------|----------|
| PLG + Sales | Self-serve → Sales-assist for enterprise | Slack, Zoom, Figma |
| Community + PLG | OSS → Hosted → Enterprise | MongoDB, Elastic |
| Marketing + Sales | Inbound MQLs → Sales conversion | HubSpot |
| Partner + Sales | Partner referrals → Direct sales | AWS Partners |
| **AI-Augmented** | AI SDRs + Human closers | Emerging 2026 |

### Vertical vs. Horizontal Strategy (2026)

| Strategy | When to Use | Examples |
|----------|-------------|----------|
| **Vertical** | Deep industry workflows, compliance needs | Veeva (pharma), Toast (restaurants) |
| **Horizontal** | Broad applicability, platform play | Slack, Notion |
| **Vertical-first** | Start narrow, expand | Rippling (HR → IT → Finance) |

2026 trend: Horizontal platforms face increasing competition from specialized vertical solutions. Successful strategies either dominate specific verticals or create platform ecosystems.

---

## Ideal Customer Profile (ICP)

### ICP Components

| Component | Questions | Example |
|-----------|-----------|---------|
| **Firmographics** | Size, industry, geography | 50-500 employees, B2B SaaS, US |
| **Technographics** | Tech stack, tools | Uses Salesforce, Modern data stack |
| **Behavioral** | Buying behavior, adoption patterns | Self-serve evaluation, fast decisions |
| **Pain indicators** | Symptoms of the problem | Growing support tickets, churn issues |
| **Success indicators** | Signs of good fit | Strong product-market alignment |

### ICP Template

```markdown
## Ideal Customer Profile: {{PRODUCT}}

### Company Profile
- **Industry**: {{INDUSTRY}}
- **Size**: {{EMPLOYEE_RANGE}} employees
- **Revenue**: ${{REVENUE_RANGE}}
- **Geography**: {{REGIONS}}
- **Growth Stage**: {{STAGE}}

### Technology Profile
- **Must have**: {{REQUIRED_TECH}}
- **Nice to have**: {{PREFERRED_TECH}}
- **Red flags**: {{AVOID_TECH}}

### Buyer Profile
- **Primary Buyer**: {{TITLE}}
- **Champions**: {{TITLES}}
- **Economic Buyer**: {{TITLE}}
- **Influencers**: {{TITLES}}

### Pain Indicators
- {{PAIN_1}}
- {{PAIN_2}}
- {{PAIN_3}}

### Success Indicators
- {{SUCCESS_1}}
- {{SUCCESS_2}}
```

### ICP Scoring

| Factor | Weight | Score (1-10) |
|--------|--------|--------------|
| Budget available | 20% | |
| Problem severity | 25% | |
| Technical fit | 15% | |
| Decision timeline | 15% | |
| Champion identified | 15% | |
| Expansion potential | 10% | |
| **ICP Score** | 100% | |

### ICP Tiering (2026 Best Practice)

Don't treat ICP as a static persona—tier it based on fit and intent signals.

| Tier | Definition | Action | Resources |
|------|------------|--------|-----------|
| **Tier 1** | Perfect fit + active buying signals | Priority outbound, personalized | High-touch, exec involvement |
| **Tier 2** | Good fit, lower/no intent signals | Nurture sequences, monitor | Marketing-led, SDR follow-up |
| **Tier 3** | Partial fit, no current signals | Marketing only, monitor | Automated, low-touch |

**Intent Signals to Monitor**:
- Hiring patterns (roles that use your product)
- Technology adoption (complementary tools)
- Funding events (Series A+ for growth stage)
- Buying committee activity (multiple visitors from same company)
- Content engagement (pricing page, case studies)

---

## Channel Strategy

### Channel Categories

| Category | Channels | Best For |
|----------|----------|----------|
| **Organic** | SEO, content, social, community | Long-term, sustainable |
| **Paid** | SEM, paid social, display | Fast, scalable, expensive |
| **Outbound** | Email, cold calls, LinkedIn | Enterprise, high ACV |
| **Partnerships** | Referrals, integrations, resellers | Leverage, distribution |
| **Product** | Viral, freemium, PLG | Self-serve, network effects |
| **Events** | Conferences, webinars, meetups | Enterprise, brand |

### Channel Selection Matrix

| Channel | CAC | Volume | Time to Impact | Control |
|---------|-----|--------|----------------|---------|
| SEO/Content | Low | High | 6-12 months | High |
| Paid Search | Medium | Medium | Immediate | High |
| Paid Social | Medium | High | Immediate | Medium |
| Outbound Email | Medium | Medium | 1-3 months | High |
| LinkedIn Outbound | High | Low | 1-3 months | High |
| Conferences | High | Low | 3-6 months | Medium |
| Partnerships | Medium | Medium | 6-12 months | Low |
| Product/Viral | Low | High | 3-6 months | Medium |
| Community | Low | Medium | 6-12 months | Medium |

### Channel Sequencing by Stage

| Stage | Primary Channels | Why |
|-------|------------------|-----|
| Pre-PMF | Founder sales, communities, early users | Direct feedback |
| Early | Content, outbound, founder network | Capital efficient |
| Growth | Paid, SEO, partnerships | Scale |
| Scale | All channels optimized | Efficiency |

---

## PLG Playbook

### PLG Funnel

```
AWARENESS
    │
    ▼
ACQUISITION (Sign up)
    │
    ▼
ACTIVATION (First value moment)
    │
    ▼
RETENTION (Continued usage)
    │
    ▼
REVENUE (Convert to paid)
    │
    ▼
REFERRAL (Viral spread)
```

### Key PLG Metrics

| Stage | Metric | Benchmark |
|-------|--------|-----------|
| Acquisition | Visitor → Signup | 2-10% |
| Activation | Signup → Activated | 30-60% |
| Retention | Day 1 / Day 7 / Day 30 | 40% / 20% / 10% |
| Revenue | Activated → Paid | 10-30% |
| Referral | % users who invite | 20-30% |

### Activation Definition

**"Activation" = When user experiences core value**

| Product Type | Activation Moment |
|--------------|-------------------|
| Slack | Sent 2,000 messages |
| Dropbox | Installed + synced file |
| Zoom | Completed first meeting |
| Notion | Created and shared doc |
| Your product | {{ACTIVATION_MOMENT}} |

### PLG Pricing Considerations

| Element | Recommendation |
|---------|----------------|
| Free tier | Yes, with usage limits |
| Trial length | 14 days (card optional) |
| Upgrade triggers | Hit limits, need feature |
| Pricing page | Transparent, self-serve |
| Enterprise | "Contact sales" option |

### PLG Evolution (2026)

**Key Shift: "Aha Moment" → "Oh Wow Moment"**

Getting users to value once isn't enough. The real metric is when they keep coming back: "Wait, it does this too?"

| Old PLG (2020-2024) | Modern PLG (2025-2026) |
|---------------------|------------------------|
| Single activation moment | Repeatable value discovery |
| MQL-driven qualification | PQL-driven (Engagement + Fit + Intent) |
| 14-30 day trials | Instant value, progressive commitment |
| Manual onboarding flows | AI-powered personalization |
| Time-based conversion | Value-based conversion |

**PQL (Product Qualified Lead) Scoring**:

```text
PQL Score = (Engagement × 0.4) + (Fit × 0.3) + (Intent × 0.3)

Engagement: Feature usage depth, session frequency, collaboration
Fit: Company size, industry, tech stack match
Intent: Pricing page visits, integration setup, team invites
```

| Qualification | Conversion Rate | Action |
|---------------|-----------------|--------|
| MQL (Marketing) | 5-10% | Nurture |
| PQL (Product) | 25-30% | Sales-assist |
| PQL + Sales signal | 40-50% | Priority outbound |

**2026 Buyer Expectations**:
- Value within minutes, not days
- Try first, account later
- AI-personalized onboarding
- Self-serve to enterprise upgrade path

---

## Sales-Led Playbook

### Sales Motion Design

| Element | SMB | Mid-Market | Enterprise |
|---------|-----|------------|------------|
| **ACV** | $1-10K | $10-50K | $50K+ |
| **Sales cycle** | <30 days | 30-90 days | 90-270 days |
| **Touch model** | Low-touch/inside | Inside/field | Field/strategic |
| **Demo** | Self-serve or 15 min | 30-60 min | Custom POC |
| **Stakeholders** | 1-2 | 3-5 | 5-10+ |
| **Procurement** | Credit card | Simple | Complex |

### Outbound Playbook

**Sequence Structure**:
```
Day 1: Email 1 (Pain-focused)
Day 3: LinkedIn connection
Day 5: Email 2 (Value-focused)
Day 8: LinkedIn message
Day 12: Email 3 (Social proof)
Day 16: Email 4 (Break-up)
```

**Targeting**:
| Element | Specification |
|---------|---------------|
| Company size | {{RANGE}} |
| Titles | {{LIST}} |
| Industries | {{LIST}} |
| Signals | {{TRIGGERS}} |

### Sales Stages

| Stage | Definition | Exit Criteria |
|-------|------------|---------------|
| **Prospecting** | Identifying targets | Meeting booked |
| **Discovery** | Understanding needs | Qualified (BANT/MEDDIC) |
| **Demo** | Showing solution | Interest confirmed |
| **Evaluation** | POC, trial, references | Success criteria met |
| **Proposal** | Pricing, terms | Proposal sent |
| **Negotiation** | Contract discussion | Agreement on terms |
| **Closed Won** | Signed | Revenue booked |

---

## Launch Planning

### Launch Types

| Type | Goal | Timeline |
|------|------|----------|
| **Soft launch** | Test, iterate | 2-4 weeks |
| **Beta launch** | Build waitlist, get feedback | 4-8 weeks |
| **ProductHunt launch** | Awareness, early adopters | 1 day + prep |
| **Full launch** | Maximum awareness | 1-2 weeks |
| **Feature launch** | Existing customer expansion | Ongoing |

### Launch Playbook Template

```markdown
## Launch: {{PRODUCT/FEATURE}}

### Objectives
- Primary: {{GOAL}}
- Secondary: {{GOAL}}
- Metrics: {{TARGETS}}

### Timeline
| Week | Activities |
|------|------------|
| -4 | {{PREP}} |
| -2 | {{PREP}} |
| -1 | {{FINAL}} |
| Launch | {{ACTIVITIES}} |
| +1 | {{FOLLOW_UP}} |

### Channels
| Channel | Asset | Owner | Date |
|---------|-------|-------|------|
| ProductHunt | Listing | | |
| Blog | Announcement | | |
| Email | Customer comms | | |
| Social | Posts | | |
| PR | Press release | | |
| Community | Posts | | |

### Assets Needed
- [ ] Landing page
- [ ] Demo video
- [ ] Blog post
- [ ] Social graphics
- [ ] Email templates
- [ ] Press kit
- [ ] Customer quotes

### Success Metrics
| Metric | Target | Actual |
|--------|--------|--------|
| Signups | {{N}} | |
| Traffic | {{N}} | |
| Mentions | {{N}} | |
| Trials | {{N}} | |
```

### ProductHunt Launch Playbook

**Before (4 weeks)**:
- [ ] Build hunter network
- [ ] Create assets (logo, screenshots, video)
- [ ] Write compelling tagline and description
- [ ] Prepare maker comment
- [ ] Coordinate with team for day-of support
- [ ] Schedule for Tuesday-Thursday

**Launch Day**:
- [ ] Launch at 12:01 AM PT
- [ ] Post maker comment immediately
- [ ] Share on social, email, communities
- [ ] Respond to ALL comments within hours
- [ ] Coordinate team upvotes (ethically)
- [ ] Update throughout the day

**After**:
- [ ] Thank supporters
- [ ] Follow up with interested users
- [ ] Publish retrospective
- [ ] Update based on feedback

---

## Growth Loops

### Loop Types

| Loop | Mechanism | Example |
|------|-----------|---------|
| **Viral** | User invites users | Dropbox referrals |
| **Content** | Content → SEO → Users → Content | HubSpot |
| **UGC** | Users create content | YouTube, TikTok |
| **Paid** | Revenue → Paid ads → Users | Performance marketing |
| **Sales** | Revenue → Sales team → Users | Enterprise sales |
| **Partner** | Partners drive users → Revenue share | App stores |

### Viral Loop Design

```
USER → CREATES/SHARES → CONTENT/INVITE
                             │
                             ▼
                        NEW USER → CREATES/SHARES → ...
```

**Viral Coefficient (K)**:
```
K = Invites per user × Conversion rate

Example:
Average invites: 5
Conversion rate: 20%
K = 5 × 0.20 = 1.0 (viral threshold)
```

### Content Loop Design

```
CONTENT → SEO TRAFFIC → SIGNUPS → PRODUCT USAGE
    ↑                                    │
    │                                    │
    └────── USER-GENERATED DATA ─────────┘
```

---

## AI-Powered GTM (2026)

AI has fundamentally changed GTM execution. Teams using AI report 12+ hours saved per week, shorter deal cycles, and higher win rates.

### AI GTM Capabilities

| Capability | Description | Tools |
|------------|-------------|-------|
| **Intent detection** | Real-time buyer intent signals | Demandbase, 6sense, Bombora |
| **Lead enrichment** | Automated data enrichment at scale | ZoomInfo, Clearbit, Apollo |
| **Outreach automation** | AI-personalized sequences | Reply.io, Outreach, Salesloft |
| **Content generation** | Automated GTM content | Copy.ai, Jasper, Writer |
| **Pipeline intelligence** | AI forecasting and deal insights | Clari, Gong, Chorus |
| **Conversation intelligence** | Call analysis and coaching | Gong, Chorus, Fireflies |

### GTM Engineer Role (Emerging 2026)

New hybrid role combining RevOps + engineering capabilities:

| Responsibility | Output |
|----------------|--------|
| Build AI-driven automations | Lead routing, scoring, enrichment pipelines |
| Integrate GTM tech stack | Unified data across CRM, marketing, product |
| Deploy AI SDRs | Automated qualification and initial outreach |
| Create custom dashboards | Real-time GTM intelligence |

**Key Trend**: Small teams generating enterprise-level outreach volume without hiring 20 SDRs—enabled by AI automation with human oversight.

### AI GTM Metrics Impact

| Metric | Pre-AI Baseline | AI-Enhanced |
|--------|-----------------|-------------|
| Lead processing time | Hours | Minutes |
| Personalization level | Segment-level | Individual |
| Deal cycle length | Standard | 20-30% shorter |
| Win rate | Baseline | 10-20% higher |
| SDR productivity | 50 touches/day | 200+ touches/day |

### AI GTM Implementation

**Phase 1: Foundation**
- Unified data layer (CRM + enrichment + intent)
- Basic automation (lead routing, task creation)

**Phase 2: Intelligence**
- AI-powered lead scoring
- Conversation intelligence
- Automated content personalization

**Phase 3: Autonomy**
- AI SDRs for initial qualification
- Predictive pipeline management
- Automated expansion signals

**Caution**: AI augments human judgment—don't automate strategy, only execution. Humans own positioning, messaging, and deal negotiation.

---

## RevOps Alignment (2026)

By 2026, 75% of fastest-growing companies will have RevOps. RevOps creates unified operational language across sales, marketing, and CS.

### RevOps Team Structure

| Function | Focus | Deliverables |
|----------|-------|--------------|
| **Business Partners** | Pipeline, forecasting | Revenue forecasts, deal support |
| **Business Process** | Workflow design | Process documentation, SLAs |
| **Revenue Technology** | GTM tech stack | System administration, integrations |
| **Process Innovation** | AI use cases | Automation, efficiency gains |

### Key RevOps Metrics (Board-Level 2026)

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **NRR (Net Revenue Retention)** | 120%+ | Expansion > churn |
| **CAC Payback** | <12 months | Capital efficiency |
| **Pipeline Velocity** | Increasing QoQ | Sales efficiency |
| **GTM Cost Ratio** | Decreasing | Operational leverage |
| **Win Rate** | Stable or increasing | Sales effectiveness |

### RevOps + GTM Alignment Checklist

- [ ] Single source of truth for customer data
- [ ] Unified definitions (MQL, SQL, PQL, opportunity stages)
- [ ] Shared dashboards across sales, marketing, CS
- [ ] Regular GTM reviews (weekly pipeline, monthly strategy)
- [ ] Clear handoff SLAs between teams
- [ ] Attribution model agreed across functions

---

## Expansion Strategy

### Land and Expand

```
LAND (Initial)
└─► Single team, single use case, low ACV

ADOPT (Prove)
└─► Usage growth, success metrics, champions

EXPAND (Grow)
└─► More teams, departments, use cases

STRATEGIC (Transform)
└─► Company-wide, multi-year, executive sponsor
```

### Expansion Signals

| Signal | Action |
|--------|--------|
| High usage | Proactive expansion conversation |
| New use case request | Cross-sell motion |
| Team growth | Seat expansion |
| Hitting limits | Upgrade conversation |
| Success metrics achieved | Case study + referral ask |

### Geographic Expansion

| Phase | Markets | Approach |
|-------|---------|----------|
| 1 | Home market | Direct |
| 2 | Adjacent (language/culture) | Localization |
| 3 | New regions | Local presence or partners |

---

## Resources

| Resource | Purpose |
|----------|---------|
| [channel-playbooks.md](references/channel-playbooks.md) | Detailed channel execution guides |
| [sales-motion-design.md](references/sales-motion-design.md) | Sales process design + RevOps alignment |
| [plg-implementation.md](references/plg-implementation.md) | PLG execution guide + PQL frameworks |

## Templates

| Template | Purpose |
|----------|---------|
| [gtm-strategy.md](assets/gtm-strategy.md) | Full GTM strategy document |
| [launch-playbook.md](assets/launch-playbook.md) | Launch planning template |
| [icp-definition.md](assets/icp-definition.md) | ICP documentation |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | GTM resources and guides |

---

## Do / Avoid (Jan 2026)

### Do

- Define activation as a concrete "first value moment" (and track "Oh wow moments" for retention).
- Track leading indicators (activation, PQL conversion, retention) alongside revenue.
- Run structured experiments with decision thresholds.
- Use AI for execution (outreach, enrichment, personalization) while humans own strategy.
- Align RevOps across sales, marketing, and CS with unified data and definitions.
- Tier your ICP and prioritize based on fit + intent signals.

### Avoid

- Content spam without measurement.
- "Do all channels" in parallel without learning loops.
- Vanity metrics without retention and payback context.
- Over-automating without human oversight (AI augments, doesn't replace judgment).
- Treating ICP as static—revisit quarterly based on win/loss data.

## What Good Looks Like

- ICP + positioning: one primary segment, explicit alternatives, and proof points (quotes, numbers, cases).
- Channel focus: 1 primary channel with a 4-week experiment plan and decision thresholds.
- Instrumentation: activation (“first value moment”) defined, tracked, and reviewed weekly.
- Launch plan: messaging, assets, owners, and a post-launch learning review scheduled.
- Feedback loop: win/loss + retention cohorts drive the next backlog decisions.

## Optional: AI / Automation

Use only when explicitly requested and policy-compliant.

- Draft assets and experiment variants; humans verify claims, brand voice, and compliance.
- Summarize call notes and objections; keep source links and spot-check.
