---
name: startup-growth-playbooks
description: Evidence-based growth tactics from real startups with specific numbers. Stage-specific playbooks (0 users to scaling), bootstrapped/no-budget strategies, case studies by growth motion (PLG, content-led, community-led, bootstrapped). Use when you have a product but need proven distribution tactics, not frameworks.
---

# Startup Growth Playbooks

Proven growth strategies from real startups with specific metrics. Not frameworks -- tactics that worked, organized by stage and budget.

**Modern Best Practices (Jan 2026)**: Distribution > product. Pick one channel, go deep, measure weekly. Paid acquisition before PMF is burning money. Build in public costs nothing and compounds. Every feature should have a distribution angle. AI search visibility (GEO/AEO) is a new compounding channel -- optimize for LLM citations, not just Google rankings.

---

## When to Use

- You have a product but zero/low traction
- You need specific examples of what worked (not frameworks)
- You are bootstrapped or budget-constrained
- You want stage-specific tactics (not "it depends")
- You need to choose between growth strategies with evidence
- You want to design growth loops into your product

## When NOT to Use

- GTM strategy and motion selection -> [startup-go-to-market](../startup-go-to-market/)
- Content positioning and messaging -> [marketing-content-strategy](../marketing-content-strategy/)
- SEO technical execution -> [marketing-seo-complete](../marketing-seo-complete/)
- AI search optimization (GEO/AEO) -> [marketing-ai-search-optimization](../marketing-ai-search-optimization/)
- Paid advertising campaigns -> [marketing-paid-advertising](../marketing-paid-advertising/)
- Sales process design -> [startup-sales-execution](../startup-sales-execution/)
- Product analytics setup -> [marketing-product-analytics](../marketing-product-analytics/)
- Pricing and unit economics -> [startup-business-models](../startup-business-models/)

---

## Quick Start (Inputs)

Ask for the minimum context to give relevant advice:

- Product: what it does, who uses it, pricing model
- Stage: 0 users / some users no traction / early traction / scaling
- Budget: bootstrapped ($0) / limited (<$1K/mo) / moderate ($1-10K/mo)
- Current channels: what has been tried, what worked/didn't
- Product type: B2B SaaS / B2C app / marketplace / dev tool / other
- Built-in virality: does using the product expose it to non-users?

## Workflow

1. Diagnose stage using the Stage Map below
2. Identify 1-2 applicable growth strategies from Case Studies by Strategy
3. Select tactics from the stage-specific playbook
4. Design 2-week growth sprint using `assets/weekly-growth-sprint.md`
5. Measure, learn, double down or pivot

---

## Stage Map

| Stage | Signal | Primary Focus | Playbook |
|-------|--------|---------------|----------|
| **Stage 0** | Product built, 0-10 users | Get first 100 users manually | `references/first-100-users-playbook.md` |
| **Stage 1** | Some users, no retention | Fix activation + retention before growth | Talk to users, fix product |
| **Stage 2** | Users stay, no growth engine | Find repeatable channel | Test 2-3 channels, pick winner |
| **Stage 3** | One channel works | Scale it + build growth loops | `references/growth-loops-implementation.md` |

### Stage Decision Tree

```text
WHAT STAGE AM I IN?
  |-- Do you have paying users?
  |     |-- No -> Stage 0 (first-100-users-playbook.md)
  |     |-- Yes -> Do they retain (D30 > 20% or monthly active)?
  |           |-- No -> Stage 1 (fix product, not distribution)
  |           |-- Yes -> Do you know which channel works?
  |                 |-- No -> Stage 2 (channel testing)
  |                 |-- Yes -> Stage 3 (scale + growth loops)
```

---

## Case Studies by Growth Strategy

### PLG (Product-Led Growth)

| Company | Strategy | Key Numbers | Replicable Tactic |
|---------|----------|-------------|-------------------|
| **Calendly** | Viral by design | Every meeting link = exposure. 10M+ users by 2020, $3B valuation | Build sharing into core action |
| **Loom** | Video sharing = marketing | Each video shared = new user exposure. Grew to $4.4B acquisition | Make output shareable by default |
| **Notion** | Templates ecosystem | $0 marketing spend to 30M+ users. Community-created templates | Enable user-generated templates |
| **Figma** | Multiplayer + community | 4M users pre-acquisition. $20B exit to Adobe (blocked) | Make collaboration the default mode |
| **Slack** | Team invite viral loop | 8K signups in 24h of launch (2014). $27.7B acquisition | Product requires team adoption |
| **Dropbox** | Referral program | 3900% growth in 15 months. 100K to 4M users via referrals | Give storage for inviting friends |
| **Canva** | Free tier + templates | 170M+ monthly active users. Freemium to $40B valuation | Free version that's genuinely useful |

For detailed breakdowns with timelines and replicable patterns: `references/case-studies-plg.md`

### Content/SEO-Led Growth

| Company | Strategy | Key Numbers | Replicable Tactic |
|---------|----------|-------------|-------------------|
| **Zapier** | Programmatic SEO | 25K+ landing pages. 5M+ monthly organic visitors | "How to connect X to Y" pages |
| **Ahrefs** | Product-led content | Every blog post demonstrates the tool. 800K+ monthly organic | Show your product solving real problems |
| **HubSpot** | Coined "inbound marketing" | Blog + free tools to $30B+ company. 7M+ monthly visits | Free tools + educational content |
| **Wise** | Transparency as PR | Price comparison calculator. 16M+ customers. $11B valuation | Make pricing transparent and PR-worthy |
| **Beehiiv** | Newsletter about newsletters | $0 to $25M ARR in ~2 years | Use your product to market your product |
| **Intercom** | Thought leadership blog | "Inside Intercom" blog drove early B2B SaaS growth | Opinionated content about your category |

For detailed breakdowns: `references/case-studies-content-seo.md`

### Bootstrapped / No-Budget Growth

| Company | Strategy | Key Numbers | Replicable Tactic |
|---------|----------|-------------|-------------------|
| **Mailchimp** | Bootstrapped to exit | $12B exit to Intuit, zero VC ever raised | Free tier + distinctive brand personality |
| **ConvertKit** | Creator content + affiliates | $0 to $2.5M ARR bootstrapped. Now $40M+ ARR | Teach your audience, affiliate program |
| **Lemlist** | Personal brand + cold email | $10M+ ARR bootstrapped. Founder LinkedIn strategy | Founder LinkedIn + product dogfooding |
| **Basecamp** | Opinionated writing | Books (Rework, Getting Real) drove thought leadership | Strong opinions, written publicly |
| **Pieter Levels** | Building in public | NomadList, RemoteOK. $3M+/yr solo founder | Ship fast, share everything on X |
| **Transistor.fm** | Podcast about podcasting | Bootstrapped to $1M+ ARR. Built audience first | Use your medium to market your product |
| **Carrd** | Solo founder, extreme simplicity | $1M+ ARR solo. Simple landing page builder | Nail one use case, price aggressively low |

For detailed breakdowns: `references/case-studies-bootstrapped.md`

### Community-Led Growth

| Company | Strategy | Key Numbers | Replicable Tactic |
|---------|----------|-------------|-------------------|
| **dbt Labs** | Community before monetization | 50K+ analytics engineers in community pre-revenue | Serve a professional identity |
| **Notion** | Ambassador program | 200+ ambassadors, user-run events worldwide | Empower power users as evangelists |
| **Supabase** | Open source + developer love | 80K+ GitHub stars. "Open source Firebase" positioning | Open source core, hosted premium |

---

## Budget-Constrained Tactics (Ranked by Impact)

| Tactic | Cost | Time to Impact | Impact | Best For |
|--------|------|----------------|--------|----------|
| Cold outreach (personalized, 10/day) | $0 | 2-4 weeks | High (B2B) | Stage 0, B2B products |
| ProductHunt launch | $0 | 1 day + 2 weeks prep | High (spike) | Stage 0-1, any product |
| Building in public (X, LinkedIn) | $0 | 2-4 weeks | Medium | All stages |
| Show HN post | $0 | 1 day | Medium-High | Dev tools, technical products |
| Reddit participation (genuine) | $0 | 4-8 weeks | Medium | Niche products |
| Product-led content (blog showing tool) | $0 | 2-4 months | High | Stage 1-2 |
| Programmatic SEO pages | $0 | 3-6 months | High | Products with combinatorial use cases |
| Integration partnerships | $0 | 1-3 months | High | Products with ecosystem fit |
| Affiliate/referral program | Low | 1-2 months setup | High | Stage 2-3 |
| Strategic guest posts | $0 | 1-2 months | Medium | Thought leadership, B2B |
| AI search optimization (GEO) | $0 | 2-6 months | Medium-High | Products in AI-searchable categories |

---

## Anti-Patterns (What Does NOT Work)

| Anti-Pattern | Why It Fails | Do This Instead |
|--------------|--------------|-----------------|
| Paid ads before PMF | Burns cash, masks retention problems | Fix retention first; paid amplifies what already works |
| Multi-channel spray | Dilutes effort, no channel gets depth | Pick 1 channel, go deep for 6-8 weeks |
| Vanity metrics focus | Followers/traffic without conversion | Track activation and retention, not reach |
| Building features over distributing | "If we build it, they will come" mindset | Every feature needs a distribution angle |
| Waiting for organic | Hope is not a strategy | Manually seed first 100 users |
| Premature community building | Community without PMF = empty forum | Participate in existing communities first |
| Copying big company playbooks | They have brand + budget you don't | Use tactics that work at your scale |
| Hiring a marketer too early | Can't delegate what you don't understand | Founder must do first sales/marketing personally |
| Perfect launch planning | Spending months preparing launch | Ship, get feedback, iterate. Launch is not a moment |

---

## Growth Loops (Design Into Your Product)

| Loop Type | Mechanism | Example | How to Build |
|-----------|-----------|---------|--------------|
| **Viral** | User action exposes product to non-users | Calendly links, Loom videos | Make output shareable and branded |
| **Content** | Users create content indexed by search | Notion templates, GitHub repos | Enable user-generated public pages |
| **UGC/Social** | Users share results on social | Spotify Wrapped, Duolingo streaks | Make progress/results shareable |
| **Data network** | More users = better product | Waze traffic, Clearbit data | Show aggregate value to new users |
| **Economic** | Revenue reinvested into growth | Revenue -> affiliates -> more users | Affiliate/referral with unit economics |

For implementation guide with viral coefficient math: `references/growth-loops-implementation.md`

---

## AEO/GEO as a Growth Channel (2026)

AI search engines (ChatGPT, Perplexity, Gemini, Google AI Overviews) are a new compounding distribution channel. Getting cited by AI models = free, high-intent traffic.

**Why it matters for early-stage**: Unlike traditional SEO (6-12 months), AI citation can happen faster because LLMs pull from structured, authoritative content regardless of domain authority.

**Quick wins**:
- Entity pages: "What is [your product]?" page with structured data
- Comparison pages: "[your product] vs [competitor]" with honest, detailed comparisons
- Integration pages: "How to use [your product] with [popular tool]"
- FAQ pages with direct, concise answers

For full implementation: [marketing-ai-search-optimization](../marketing-ai-search-optimization/)

---

## Do / Avoid

### Do

- Start with manual, unscalable tactics (do things that don't scale)
- Talk to 10 users before optimizing funnels
- Pick ONE channel and go deep before testing the next
- Design distribution into the product from day one
- Measure weekly, decide bi-weekly, pivot monthly
- Study case studies in your exact category and stage
- Track: activation rate, retention (D7/D30), revenue, referral rate

### Avoid

- Spending money on ads before 40%+ D30 retention (B2C) or 80%+ monthly retention (B2B)
- Building a community before you have 100+ active users
- Hiring a marketer before you can describe what works
- Copying tactics from companies 100x your size
- Optimizing conversion before you have meaningful traffic
- Treating launch as a single event (it's a series of sprints)
- Adding features when distribution is the bottleneck

---

## Resources

| Resource | Purpose |
|----------|---------|
| [first-100-users-playbook.md](references/first-100-users-playbook.md) | Stage 0: zero to first 100 users (30-day plan) |
| [case-studies-plg.md](references/case-studies-plg.md) | Detailed PLG case studies with timelines and numbers |
| [case-studies-content-seo.md](references/case-studies-content-seo.md) | Content/SEO growth stories with metrics |
| [case-studies-bootstrapped.md](references/case-studies-bootstrapped.md) | No-budget growth success stories |
| [growth-loops-implementation.md](references/growth-loops-implementation.md) | How to build compounding growth loops |
| [building-in-public.md](references/building-in-public.md) | Personal brand as distribution channel |
| [case-studies-community-led.md](references/case-studies-community-led.md) | Community-led growth case studies with timelines and metrics |
| [referral-program-design.md](references/referral-program-design.md) | Referral and viral program design, benchmarks, implementation |
| [product-hunt-launch-playbook.md](references/product-hunt-launch-playbook.md) | Product Hunt launch execution (hour-by-hour) and PH alternatives |
| [case-studies-marketplace.md](references/case-studies-marketplace.md) | Marketplace growth case studies (Airbnb, Uber, Etsy, Upwork, Bumble, Faire) |

## Templates

| Template | Purpose |
|----------|---------|
| [growth-diagnostic.md](assets/growth-diagnostic.md) | Diagnose stage and pick tactics |
| [founder-skill-audit.md](assets/founder-skill-audit.md) | Assess founder's 9 distribution capabilities |
| [weekly-growth-sprint.md](assets/weekly-growth-sprint.md) | 2-week experiment tracker |
| [launch-channel-scorecard.md](assets/launch-channel-scorecard.md) | Score and select launch channels |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | Growth newsletters, podcasts, case study databases |

---

## Related Skills

| Skill | Use For |
|-------|---------|
| [startup-go-to-market](../startup-go-to-market/) | GTM strategy, motion selection, ICP definition |
| [startup-business-models](../startup-business-models/) | Unit economics for growth math |
| [startup-customer-success](../startup-customer-success/) | Retention and activation |
| [marketing-content-strategy](../marketing-content-strategy/) | Positioning, messaging, content pillars |
| [marketing-seo-complete](../marketing-seo-complete/) | SEO technical execution |
| [marketing-ai-search-optimization](../marketing-ai-search-optimization/) | AI search / GEO optimization |
| [marketing-social-media](../marketing-social-media/) | Social channel execution |
| [marketing-cro](../marketing-cro/) | Conversion optimization |
| [product-management](../product-management/) | PLG activation design |

---

## What Good Looks Like

- You know your stage (0/1/2/3) and are working on the right problem for that stage.
- You have ONE primary channel with a 2-week experiment running.
- You can name 3 companies in your category that grew with a similar tactic and explain what they did.
- You are measuring activation, retention, and referral -- not just traffic.
- You have a growth diagnostic completed (`assets/growth-diagnostic.md`) and revisit it monthly.
- Every new feature ships with a distribution angle (sharing, SEO, virality, integration).
