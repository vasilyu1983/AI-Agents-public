---
name: marketing-paid-advertising
description: Paid advertising strategy for Google, Meta, TikTok, LinkedIn - campaign structure, bidding, audiences, creative, measurement, budget allocation, unit economics (CAC/LTV), revenue attribution, payback period, and sales alignment.
---

# PAID ADVERTISING — CAMPAIGN OS (OPERATIONAL)

Built as a **no-fluff execution skill** for paid acquisition across Google, Meta, TikTok, and LinkedIn.

**Structure**: Core paid advertising fundamentals first. Platform-specific tactics in dedicated sections. AI automation in clearly labeled "Optional: AI / Automation" sections.

---

## Modern Best Practices (January 2026)

- Google Ads: https://support.google.com/google-ads/
- Meta Business Help: https://www.facebook.com/business/help
- TikTok Ads Manager: https://ads.tiktok.com/help/
- LinkedIn Campaign Manager: https://business.linkedin.com/marketing-solutions

### Local Reference PDFs (Internal)

- [Google: Responsive Search Ads - A guide to writing ads that perform (2023)](<../../../../custom-gpt/productivity/SMM Assistant/sources/15. Google responsive_search_ads_a_guide_to_writing_ads_that_perform_2023.pdf>)
- [Google: Search Creative Best Practices Guide (Responsive Search Ads)](<../../../../custom-gpt/productivity/SMM Assistant/sources/12. Google creative best practices guide.pdf>)

---

## When to Use This Skill

- **New campaigns**: Structure, audiences, bidding, creative strategy
- **Scaling spend**: Budget allocation, ROAS targets, diminishing returns
- **Platform selection**: Which channels for which goals
- **Creative strategy**: Ad formats, hooks, testing frameworks
- **Measurement**: Attribution, incrementality, cross-platform tracking
- **Unit economics**: CAC/LTV modeling, payback period, max allowable spend
- **Revenue attribution**: Multi-touch attribution, incrementality testing
- **Sales alignment**: Lead quality, MQL/SQL handoffs, shared KPIs

---

## When NOT to Use This Skill

- **Organic social strategy** → Use [marketing-social-media](../marketing-social-media/SKILL.md)
- **SEO/content marketing** → Use [marketing-seo](../marketing-seo/SKILL.md)
- **Email automation** → Use [marketing-email-automation](../marketing-email-automation/SKILL.md)
- **Landing page optimization** → Use [marketing-cro](../marketing-cro/SKILL.md)
- **Affiliate/influencer marketing** → Different attribution and partnership models
- **Programmatic display (DSP)** → Requires specialized DSP knowledge beyond self-serve platforms

---

## Core: Platform Selection Matrix

| Platform | Best For | Avg CPL (B2B) | Avg CPL (B2C) | Targeting Strength |
|----------|----------|---------------|---------------|-------------------|
| **Google Search** | High intent, ready-to-buy | $30-80 | $15-40 | Intent-based |
| **Google Display** | Awareness, retargeting | $10-30 | $5-15 | Contextual |
| **Meta (FB/IG)** | B2C, visual products, awareness | $20-60 | $5-25 | Interest/behavior |
| **LinkedIn** | B2B, enterprise, high ACV | $50-150 | N/A | Professional |
| **TikTok** | Gen Z/Millennial, viral potential | $15-40 | $3-15 | Interest/behavior |
| **YouTube** | Education, demos, brand | $20-50 | $8-20 | Intent + interest |

### Platform Selection Decision Tree

```text
HIGH INTENT (ready to buy)?
├─ YES → Google Search (always include)
│        └─ Add branded terms + competitor terms
└─ NO → What's your goal?
         ├─ Awareness/Brand → Meta, TikTok, YouTube
         ├─ B2B/Enterprise → LinkedIn, Google Search
         ├─ E-commerce → Meta, Google Shopping, TikTok
         └─ App installs → Meta, TikTok, Google UAC
```

---

## Core: Campaign Structure Framework

### Google Ads Structure

```text
ACCOUNT
├─ Campaign 1: Brand (Search)
│   ├─ Ad Group: Exact brand terms
│   └─ Ad Group: Brand + product
│
├─ Campaign 2: Non-Brand (Search)
│   ├─ Ad Group: Pain/problem keywords
│   ├─ Ad Group: Solution keywords
│   └─ Ad Group: Competitor keywords
│
├─ Campaign 3: Retargeting (Display)
│   ├─ Ad Group: Site visitors (7d)
│   ├─ Ad Group: Site visitors (30d)
│   └─ Ad Group: Cart abandoners
│
└─ Campaign 4: Performance Max (if applicable)
    └─ Asset group by product/service line
```

### Meta Ads Structure

```text
ACCOUNT
├─ Campaign 1: Prospecting (Conversions)
│   ├─ Ad Set: Lookalike 1% (customers)
│   ├─ Ad Set: Interest targeting
│   └─ Ad Set: Broad targeting (Advantage+)
│
├─ Campaign 2: Retargeting (Conversions)
│   ├─ Ad Set: Website visitors (7d)
│   ├─ Ad Set: Engaged (video/page 30d)
│   └─ Ad Set: Cart abandoners
│
└─ Campaign 3: Testing (CBO or ABO)
    ├─ Ad Set: Creative test A
    ├─ Ad Set: Creative test B
    └─ Ad Set: Creative test C
```

---

## Core: Bidding Strategy Guide

| Strategy | When to Use | Risk Level | Best For |
|----------|-------------|------------|----------|
| **Manual CPC** | New campaigns, learning | Low | Control freaks, testing |
| **Target CPA** | Stable conversion history | Medium | Lead gen, consistent volume |
| **Target ROAS** | E-commerce, known value | Medium | Revenue optimization |
| **Maximize Conversions** | Volume priority | High | Scale quickly, less control |
| **Maximize Clicks** | Traffic/awareness | Low | Brand campaigns |

### Bidding Decision Tree

```text
CONVERSION HISTORY?
├─ <50 conversions/month → Manual CPC or Max Clicks
├─ 50-100 conversions → Target CPA (start conservative)
└─ >100 conversions → Target CPA/ROAS (optimize for efficiency)

BUDGET CONSTRAINED?
├─ YES → Manual CPC or Target CPA (strict)
└─ NO → Maximize Conversions (let algorithm spend)
```

### Do (Bidding)

- Start with manual/conservative bids to gather data
- Set realistic CPA/ROAS targets based on unit economics
- Allow 2-4 weeks for learning phase before judging
- Use bid adjustments for device, location, time

### Avoid (Bidding)

- Changing bids daily (resets learning)
- Setting unrealistic CPA targets (algorithm won't spend)
- Using ROAS bidding without accurate conversion values
- Ignoring seasonality effects on performance

---

## Core: Audience Strategy

### By Funnel Stage

| Stage | Google | Meta | TikTok |
|-------|--------|------|--------|
| **Top** (Awareness) | In-Market, Affinity | Broad, Lookalike 1-5% | Interest, Hashtag |
| **Middle** (Consideration) | Custom Intent, Search | Lookalike 1-2%, Engaged | Custom, Retargeting |
| **Bottom** (Decision) | Brand Search, RLSA | Retargeting 7-14d | Email retargeting |

### Key Audiences

- **Google:** In-Market (actively buying), Custom Intent (your keywords/competitor URLs), Remarketing
- **Meta:** Lookalike 1% (highest quality), Advantage+ (AI-optimized), Custom audiences
- **LinkedIn:** Job title, company size, industry targeting

---

## Core: First-Party Data Strategy (2026 Critical)

With third-party cookie deprecation complete, first-party and zero-party data are essential for targeting.

### Data Types

| Type | Definition | Collection Method |
|------|------------|-------------------|
| **First-party** | Data you collect directly | Website behavior, email, purchases |
| **Zero-party** | Data customers intentionally share | Surveys, preferences, quiz results |

### Implementation Checklist

- [ ] Customer Match lists uploaded (Google, Meta, LinkedIn)
- [ ] Enhanced Conversions enabled (Google)
- [ ] Conversions API (CAPI) implemented (Meta)
- [ ] Events API configured (TikTok, LinkedIn)
- [ ] Email/phone collection optimized on landing pages
- [ ] Lead enrichment workflow configured

### Platform-Specific Setup

| Platform | First-Party Feature | Priority |
|----------|---------------------|----------|
| **Google** | Customer Match, Enhanced Conversions | Critical |
| **Meta** | Conversions API (CAPI), Custom Audiences | Critical |
| **LinkedIn** | Matched Audiences, Insight Tag | High |
| **TikTok** | Events API, Custom Audiences | High |

### Why This Matters in 2026

- **Targeting precision**: Algorithms now rely on first-party signals, not third-party cookies
- **Signal quality**: Offline conversions and CRM data improve bidding accuracy
- **Audience building**: Lookalikes based on your data outperform interest targeting
- **Attribution recovery**: Server-side tracking recovers 10-20% of lost conversions

---

## Core: Creative Strategy

### Ad Format Selection

| Format | Platform | Best For |
|--------|----------|----------|
| Responsive Search | Google | High intent |
| Image/Carousel | Meta, LinkedIn | Products, features |
| Video (15-30s) | All | Engagement, brand |
| UGC-style | Meta, TikTok | Authenticity |

### Creative Testing Framework

Test ONE variable at a time: Hook (Week 1-2) → Format (Week 3-4) → CTA (Week 5-6).

### Platform Best Practices

- **Google Search:** Keywords in headlines, use all 15 headlines/4 descriptions. See [references/google-ads-guide.md](references/google-ads-guide.md)
- **Meta:** Hook in first 3 seconds, UGC outperforms polished, 1:1 feed / 9:16 stories
- **TikTok:** Native aesthetic, hook in 1 second, trending sounds
- **LinkedIn:** Professional tone, document ads for thought leadership

**Templates:** [assets/creative-brief.md](assets/creative-brief.md), [assets/google-rsa-asset-pack.md](assets/google-rsa-asset-pack.md)

---

## Core: Budget Allocation Framework

### Budget by Funnel Stage

| Stage | % of Budget | Goal |
|-------|-------------|------|
| **Brand** | 10-20% | Protect brand terms, low CPL |
| **Prospecting** | 40-60% | New customer acquisition |
| **Retargeting** | 20-30% | Convert warm audiences |
| **Testing** | 10-15% | New creative/audience tests |

### Budget Allocation by Platform

**Starter Budget ($5-10k/month):**
```text
Google Search (brand + non-brand): 60%
Meta (prospecting + retargeting): 30%
Testing budget: 10%
```

**Growth Budget ($10-50k/month):**
```text
Google Search: 40%
Meta: 35%
TikTok or LinkedIn: 15%
Testing: 10%
```

**Scale Budget ($50k+/month):**
```text
Google (Search + PMax + YouTube): 35%
Meta: 30%
TikTok: 15%
LinkedIn (if B2B): 10%
Testing: 10%
```

### Diminishing Returns Detection

| Signal | What It Means | Action |
|--------|---------------|--------|
| CPL increasing >20% | Audience saturation | Expand audiences, add channels |
| Frequency >3 (Meta) | Ad fatigue | New creative, expand audience |
| Impression share <80% | Budget limited | Increase budget or narrow targeting |
| CTR declining | Creative fatigue | Test new hooks, formats |

---

## Quick Reference

| Task | Template | Location |
|------|----------|----------|
| Campaign setup | Campaign structure template | `assets/campaign-structure.md` |
| Budget planning | Budget allocation worksheet | `assets/budget-allocation.md` |
| Unit economics | CAC/LTV/Payback calculator | `assets/unit-economics-calculator.md` |
| Google RSA copy pack | RSA headlines + descriptions pack | `assets/google-rsa-asset-pack.md` |
| Creative brief | Ad creative brief | `assets/creative-brief.md` |
| A/B testing | Creative test plan | `assets/creative-test-plan.md` |
| Performance review | Weekly/monthly review | `assets/performance-review.md` |

---

## Decision Tree (Campaign Triage)

```text
CPL too high?
├─ Check audience size → Too narrow = expand; too broad = tighten
├─ Check creative CTR → Below 1% = new creative needed
├─ Check landing page CVR → Below 2% = landing page issue (see marketing-cro)
└─ Check bid strategy → May need to increase bids or change strategy

ROAS below target?
├─ Check conversion tracking → Missing conversions = attribution issue
├─ Check audience quality → Low quality = tighten targeting
├─ Check offer → Weak offer = test new value prop
└─ Check funnel → Leaky funnel = fix downstream conversion

Volume too low?
├─ Check budget → Daily budget limiting impressions
├─ Check bid → Bids too low to win auctions
├─ Check audience → Audience too narrow
└─ Check creative → Low relevance score/quality score
```

---

## Operational SOPs

**Campaign Launch:** Pre-launch (define KPIs, build audiences, upload 3-5 creatives) → Launch (conservative bids, daily caps) → Learning phase (14 days, no major changes) → Optimization (pause losers, scale winners +20%).

**Weekly Review:** Monday (30 min): metrics, targets, top 3 actions. Thursday (15 min): pacing, pause disasters.

**Monthly Review:** Performance summary, audience insights, creative insights, budget reallocation.

**Full SOPs:** [references/operational-sops.md](references/operational-sops.md)

---

## Privacy & Compliance (2026)

CCPA 2.0 and EU AI Act are in full effect. Non-compliance risks account suspension and fines.

### Compliance Checklist

- [ ] Explicit consent obtained for personalized targeting
- [ ] Clear opt-out options available on all properties
- [ ] Third-party tracking tools audited for compliance
- [ ] Cookie consent banner with granular controls
- [ ] Data retention policies documented and enforced

### Platform Privacy Features

| Platform | Feature | Status |
|----------|---------|--------|
| **Google** | Consent Mode v2 | Required (EU/EEA) |
| **Meta** | Limited Data Use (LDU) | Required (California) |
| **All** | Server-side tracking | Recommended |
| **All** | Privacy-safe attribution | Recommended |

### Regional Requirements

| Region | Law | Key Requirement |
|--------|-----|-----------------|
| **EU/EEA** | GDPR + AI Act | Consent before tracking, AI transparency |
| **California** | CCPA 2.0 | Opt-out rights, data deletion |
| **UK** | UK GDPR | Similar to EU, separate enforcement |

### Do (Privacy)

- Implement Consent Mode v2 for Google Ads in EU
- Enable Limited Data Use for Meta in California
- Use server-side tracking for privacy-compliant attribution
- Document data flows and retention policies

### Avoid (Privacy)

- Tracking without consent in regulated regions
- Storing raw PII in ad platforms
- Using non-compliant third-party pixels
- Ignoring platform policy updates

---

## Metrics & KPIs

### Primary Metrics

| Metric | Definition | Target Range |
|--------|------------|--------------|
| **CPL** | Cost per lead | Industry dependent |
| **CPA** | Cost per acquisition | < LTV/3 |
| **ROAS** | Revenue / Ad spend | > 3:1 for e-com |
| **CAC** | Full acquisition cost | < LTV/3 |

### Secondary Metrics

| Metric | Definition | Watch For |
|--------|------------|-----------|
| **CTR** | Clicks / Impressions | <1% = creative issue |
| **CVR** | Conversions / Clicks | <2% = landing issue |
| **Frequency** | Avg impressions/user | >3 = fatigue |
| **Quality Score** | Google relevance | <6 = improve relevance |
| **Relevance Score** | Meta relevance | <5 = improve relevance |

---

## Core: Unit Economics & CAC/LTV Framework

Connect ad spend to business outcomes. Campaigns optimized for CPL without understanding downstream economics often acquire unprofitable customers.

**Key Metrics:**

| Ratio | Status | Action |
|-------|--------|--------|
| < 1:1 | Losing money | Stop spending |
| 3:1 | Healthy (target) | Maintain/scale |
| > 5:1 | Under-investing | Scale aggressively |

**Payback Benchmarks:**

| Business Model | Target | Max |
|----------------|--------|-----|
| B2C SaaS | < 6 mo | 12 mo |
| B2B SaaS (SMB) | < 12 mo | 18 mo |
| E-commerce | < 3 mo | 6 mo |

**Decision Tree:**
- LTV:CAC > 3:1 AND Payback < Target → Scale spend
- LTV:CAC 1-3:1 → Optimize efficiency
- LTV:CAC < 1:1 → Stop paid ads, fix unit economics

**Full guide:** [references/unit-economics-guide.md](references/unit-economics-guide.md)

**Calculator template:** [assets/unit-economics-calculator.md](assets/unit-economics-calculator.md)

---

## Core: Revenue Attribution Framework

Measure the true business impact of paid advertising through attribution modeling and incrementality testing.

**Attribution Models:**

| Model | Best For |
|-------|----------|
| Last Click | Short cycles (<7 days), simple tracking |
| Position-Based | B2B, multi-touch journeys |
| Data-Driven | High volume (>1000 conv/mo) |

**Incrementality Testing:**
- **Geo-lift**: Compare test markets (ads on) vs control (ads off)
- **Holdout**: Exclude 10-20% of audience, measure conversion lift

**Tracking Setup:**
- Google: Enhanced conversions + GA4
- Meta: Conversions API (CAPI)
- LinkedIn/TikTok: Events API + UTM → CRM backup

**Full guide:** [references/revenue-attribution-guide.md](references/revenue-attribution-guide.md)

---

## Core: Sales Alignment Protocol

Align paid advertising with sales teams to maximize revenue impact and accurate CAC measurement.

**Lead Pipeline:**

| Stage | Marketing KPI | Sales KPI |
|-------|---------------|-----------|
| Lead | Volume, CPL | Response time |
| MQL | MQL rate, Cost/MQL | Qualification rate |
| SQL | SQL rate, Cost/SQL | Demo rate |
| Customer | CAC, LTV:CAC | Revenue, ACV |

**Lead Scoring Thresholds:**
- 12-15: Hot → Immediate outreach
- 8-11: Warm → Sales within 24h
- <8: Nurture sequence

**Weekly Sync Agenda (30 min):**
1. Lead quality review (5 min)
2. Pipeline impact (10 min)
3. Targeting feedback (10 min)
4. Upcoming campaigns (5 min)

**Full guide:** [references/sales-alignment-guide.md](references/sales-alignment-guide.md)

---

## Platform-Specific Guides

### Google Ads Specifics

See [references/google-ads-guide.md](references/google-ads-guide.md)

### Meta Ads Specifics

See [references/meta-ads-guide.md](references/meta-ads-guide.md)

### TikTok Ads Specifics

See [references/tiktok-ads-guide.md](references/tiktok-ads-guide.md)

### LinkedIn Ads Specifics

See [references/linkedin-ads-guide.md](references/linkedin-ads-guide.md)

---

## Templates

| Template | Purpose |
|----------|---------|
| [campaign-structure.md](assets/campaign-structure.md) | Campaign hierarchy template |
| [budget-allocation.md](assets/budget-allocation.md) | Budget planning + unit economics worksheet |
| [unit-economics-calculator.md](assets/unit-economics-calculator.md) | CAC/LTV/Payback period calculator |
| [google-rsa-asset-pack.md](assets/google-rsa-asset-pack.md) | Google RSA headline/description asset pack |
| [creative-brief.md](assets/creative-brief.md) | Ad creative specification |
| [creative-test-plan.md](assets/creative-test-plan.md) | A/B testing framework |
| [performance-review.md](assets/performance-review.md) | Weekly/monthly review template |

---

## Trend Awareness Protocol

**IMPORTANT**: Use WebSearch to check current trends before answering recommendation questions.

**Triggers:** "Best strategy for 2026?", "What's new in [platform]?", "Is [feature] still effective?"

**Required Searches:**
1. `"paid advertising trends 2026"`
2. `"[platform] updates January 2026"`
3. `"[platform] best practices 2026"`

**Report:** Current landscape, emerging trends, deprecated features, recommendation based on fresh data.

---

## Anti-Patterns

- **Changing bids daily** → Resets learning. Wait 2-4 weeks.
- **Too many audiences** → Splits budget. Use 3-5 max.
- **Single creative** → Quick fatigue. Use 3-5 variants.
- **No negative keywords** → Wasted spend. Build weekly.
- **Platform FOMO** → Spreading thin. Master 1-2 first.

---

## Optional: AI / Automation

**AI Features:** Performance Max (Google), Advantage+ (Meta), Value-Based Bidding (all platforms).

**When to use:** 100+ conversions/month AND clear conversion values. Otherwise, stick to manual campaigns.

---

## Related Skills

- [marketing-leads-generation](../marketing-leads-generation/SKILL.md) — Lead capture and nurture
- [marketing-cro](../marketing-cro/SKILL.md) — Landing page optimization
- [marketing-content-strategy](../marketing-content-strategy/SKILL.md) — Content for ads
- [startup-go-to-market](../startup-go-to-market/SKILL.md) — Channel strategy

---

## Usage Notes (Claude)

- Stay operational: return campaign structures, budgets, creative specs
- Include platform-specific requirements (sizes, specs, limits)
- Always recommend starting conservative and scaling
- Cite current platform documentation when possible
- Do not invent benchmark data; use ranges or state "varies by industry"
