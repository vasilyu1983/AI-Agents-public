---
name: marketing-email-automation
description: Email marketing automation - workflow design, platform setup (HubSpot, Klaviyo, Mailchimp), nurture sequences, lifecycle emails, deliverability, revenue attribution, and retention economics.
---

# EMAIL AUTOMATION — WORKFLOW OS (OPERATIONAL)

Built as a **no-fluff execution skill** for email marketing automation across B2B and B2C.

**Structure**: Core workflows and segmentation in SKILL.md. Platform setup in `references/`. Revenue economics in `references/email-economics.md`. Templates in `assets/`.

---

## Modern Best Practices (January 2026)

### 2026 Email Landscape

| Trend | Impact | Action |
|-------|--------|--------|
| **SPF/DKIM/DMARC mandatory** | Non-authenticated mail blocked | Audit quarterly, not just at setup |
| **BIMI adoption** | 38% higher opens, 120% brand recall | Implement verified logo display |
| **Intelligent inboxes** | Engagement signals (scroll, reply, delete) determine placement | Focus on quality over quantity |
| **Complaint threshold <0.3%** | Google/Yahoo enforce strictly | Monitor FBL, clean aggressively |
| **One-click unsubscribe required** | Bulk senders must comply | List-Unsubscribe-Post header mandatory |
| **Domain/IP warm-up critical** | ISPs monitor sending consistency | Gradual ramp for new infrastructure |
| **Inactive subscribers harm reputation** | Disengagement = strong negative signal | Sunset flows, re-engagement campaigns |

**Authentication & Deliverability (Critical)**
- Google Sender Guidelines: https://support.google.com/a/answer/81126?hl=en
- Yahoo Sender Hub: https://senders.yahooinc.com/best-practices/
- Microsoft Outlook Requirements: https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dmarc-configure
- BIMI Group (Brand Indicators): https://bimigroup.org/
- Google BIMI Setup: https://support.google.com/a/answer/10911320?hl=en
- Mailtrap Deliverability Guide: https://mailtrap.io/blog/email-deliverability/
- ExpertSender 2026 Deliverability: https://expertsender.com/blog/email-deliverability-in-2026-key-observations-trends-challenges-for-marketers/
- ExactVerify Compliance Guide: https://www.exactverify.com/blog/email-deliverability-compliance-guide
- Amplemarket 2026 Guide: https://www.amplemarket.com/blog/email-deliverability-guide-2026

**Platforms**
- HubSpot Email: https://knowledge.hubspot.com/marketing-email/create-and-send-marketing-emails
- Klaviyo Help: https://help.klaviyo.com/
- Klaviyo Platform Comparison: https://www.klaviyo.com/blog/best-email-marketing-platforms
- Mailchimp Resources: https://mailchimp.com/resources/
- Brevo Platform Guide: https://www.brevo.com/blog/best-email-marketing-services/
- Knak Email Creation: https://knak.com/blog/2026-email-marketing-trends/

**Industry Insights**
- Litmus Blog: https://www.litmus.com/blog/
- Mailjet 2026 Trends: https://www.mailjet.com/blog/email-best-practices/email-marketing-trends-2026/
- Email Vendor Selection Guide: https://www.emailvendorselection.com/email-deliverability-guide/
- Vertical Response 2026 Strategies: https://verticalresponse.com/blog/email-marketing-in-2026-trends-tactics-and-what-to-do-now/

---

## When to Use This Skill

- **Workflow design**: Trigger-based sequences, nurture flows, lifecycle emails
- **Platform setup**: HubSpot, Klaviyo, Mailchimp, Braze configuration
- **Segmentation**: List management, behavioral segments, RFM models
- **Deliverability**: Authentication, warm-up, reputation management
- **Revenue attribution**: RPE calculation, attribution models, email-attributed revenue
- **Retention economics**: Churn reduction ROI, segment LTV, cohort analysis
- **Channel mix**: Email vs. paid comparison, budget allocation, investment justification
- **AI optimization**: Send-time optimization, predictive content, personalization at scale

---

## When NOT to Use This Skill

- **Cold email outreach** → Sales prospecting, not marketing automation
- **Transactional email infrastructure** → Developer/DevOps email delivery setup
- **Email HTML/CSS coding** → Template development, not strategy
- **SMS-only campaigns** → Different compliance and workflow patterns
- **One-off announcements** → This skill focuses on automated sequences

---

## Core: Email Workflow Types

| Workflow Type | Trigger | Purpose | Timeline |
|---------------|---------|---------|----------|
| **Welcome** | New subscriber | Introduce brand, set expectations | Day 0-7 |
| **Onboarding** | New customer | Drive activation, reduce churn | Day 0-30 |
| **Nurture** | Lead capture | Educate, build trust, convert | Weeks 1-8 |
| **Abandoned Cart** | Cart created, no purchase | Recover revenue | Hours 1-72 |
| **Re-engagement** | Inactive subscriber | Win back or clean list | Day 30-90 |
| **Upsell/Cross-sell** | Purchase complete | Increase LTV | Day 7-30 post-purchase |
| **Renewal/Retention** | Subscription nearing end | Prevent churn | Day -30 to -1 |

---

## Core: Workflow Design Framework

```text
WORKFLOW: [Name]
TRIGGER: [Event that starts flow]
GOAL: [Primary conversion action]
DURATION: [Total time span]

ENTRY → EMAIL 1 → WAIT → BRANCH (engaged/not) → EMAIL 2 → ... → EXIT

Exit when: Goal met | Unsubscribe | Time limit reached
```

See [assets/workflow-blueprint.md](assets/workflow-blueprint.md) for full template.

---

## Core: Standard Workflow Templates

### Welcome Sequence (4 emails, 7 days)

| Day | Email | Subject Pattern | CTA |
|-----|-------|-----------------|-----|
| 0 | Welcome + Value | "Welcome to [Brand]" | Primary action |
| 2 | Problem Agitation | "The [problem] most face" | Read guide |
| 4 | Social Proof | "How [Customer] achieved [Result]" | See stories |
| 7 | Soft Sell | "Ready to [achieve outcome]?" | Start trial / Buy |

### Abandoned Cart (3 emails, 72 hours)

| Time | Email | Focus | CTA |
|------|-------|-------|-----|
| 1hr | Reminder | Cart contents + images | Complete order |
| 24hr | Urgency + Support | FAQ, support link | Complete + Chat |
| 72hr | Incentive (optional) | Discount code | Use code |

### Lead Nurture (6 emails, 4 weeks)

Day 0 → Day 3 → Day 7 → Day 12 → Day 17 → Day 24

Deliver value → Educate → Case study → Handle objections → Compare → Soft close

See full templates: [assets/welcome-sequence.md](assets/welcome-sequence.md), [assets/nurture-sequence.md](assets/nurture-sequence.md), [assets/cart-abandonment.md](assets/cart-abandonment.md)

---

## Core: Segmentation Framework

### Behavioral Segments

| Segment | Definition | Use For |
|---------|------------|---------|
| **Engaged** | Opened/clicked in last 30 days | Primary campaigns |
| **Active** | Logged in / used product recently | Onboarding, upsell |
| **At-risk** | No engagement 31-60 days | Re-engagement |
| **Dormant** | No engagement 61-90 days | Win-back |
| **Churned** | No engagement 90+ days | Sunset or remove |

### RFM Segmentation (E-commerce)

| Segment | Recency | Frequency | Monetary | Strategy |
|---------|---------|-----------|----------|----------|
| **Champions** | Recent | Often | High | Reward, refer |
| **Loyal** | Recent | Often | Medium | Upsell |
| **Potential** | Recent | Rare | Low | Nurture |
| **At Risk** | Old | Often | High | Win back |
| **Hibernating** | Old | Rare | Low | Re-engage or remove |

---

## Core: Email Best Practices

### Subject Lines

**Do**: Under 50 chars, personalize, use numbers, A/B test
**Avoid**: ALL CAPS, !!! excessive punctuation, spam words, misleading

### Email Copy Structure

```text
1. Hook (first line): Grab attention, reference pain/benefit
2. Body (2-3 short paragraphs): Value, proof, bridge to CTA
3. CTA (clear, single action): Button or linked text
4. P.S. (optional): Reinforce urgency or secondary offer
```

### Timing

| Email Type | Best Days | Best Times |
|------------|-----------|------------|
| B2B | Tue-Thu | 9-11am, 1-3pm |
| B2C | Tue-Thu, Sat | 10am, 8pm |
| Transactional | Immediate | N/A |

**Better approach**: Use AI send-time optimization (STO) for per-subscriber timing. See section below.

---

## AI-Powered Optimization (2026)

### Send Time Optimization (STO)

AI analyzes individual subscriber behavior to deliver emails at optimal times per recipient—replacing fixed send times.

| Platform | STO Feature | Tier |
|----------|-------------|------|
| **Klaviyo** | Smart Send Time | All plans |
| **HubSpot** | Send Time Optimization | Enterprise |
| **Braze** | Intelligent Timing | All plans |
| **ActiveCampaign** | Predictive Sending | Plus+ |
| **Mailchimp** | Send Time Optimization | Premium |

### Predictive Content

| Capability | What AI Does | Impact |
|------------|--------------|--------|
| Subject lines | A/B tests + predicts winners | +15-25% open rate |
| Product recs | Behavioral modeling | +20-40% click rate |
| Content blocks | Dynamic selection per recipient | +10-20% conversion |
| Next-best action | Determines optimal follow-up | Higher LTV |

### AI Performance Benchmarks (2026)

| Metric | Without AI | With AI | Lift |
|--------|------------|---------|------|
| Open rate | 20% | 27% | +35% |
| Click rate | 2% | 3% | +50% |
| Conversion | 1% | 1.5% | +50% |

### Quick Wins (Start Here)

1. **Enable STO** — Most platforms have this; immediate lift with no setup
2. **Dynamic subject lines** — Let AI pick from 3-5 variants per recipient
3. **Product recommendations** — Enable behavioral recs in cart/browse abandonment

❌ **Don't over-automate**: Complex 25-email flows without monitoring damage deliverability. Review automation performance monthly.

---

## Core: Deliverability Checklist

### 2025-2026 Compliance (Critical)

**Google, Yahoo, Microsoft** now enforce identical requirements for bulk senders (5000+/day):

- [ ] **SPF + DKIM + DMARC** all configured and aligned
- [ ] **One-click unsubscribe** (RFC 8058) header required
- [ ] **Spam rate** below 0.3% (target <0.1%)
- [ ] Custom sending domain (not @gmail.com)
- [ ] Valid PTR records for sending IPs
- [ ] **BIMI** configured (recommended for brand trust)

### BIMI (Brand Indicators for Message Identification)

BIMI displays your logo next to emails in Gmail, Yahoo, and Apple Mail—increasing brand recognition by up to 44%.

| Requirement | Details |
|-------------|---------|
| **DMARC** | Policy must be `p=quarantine` or `p=reject` with `pct=100` |
| **Logo** | SVG Tiny PS format, square |
| **Certificate** | VMC (trademark required) or CMC (no trademark, 1yr logo use) |
| **DNS** | BIMI TXT record at `default._bimi.yourdomain.com` |

**2026 Update**: Google now accepts CMC (Common Mark Certificates) without trademark registration—lowering the barrier for smaller brands.

### Enforcement Status (January 2026)

| Provider | Status | Non-Compliance Result |
|----------|--------|----------------------|
| **Google** | Enforcing since Nov 2025 | Emails **rejected** (not delayed) |
| **Yahoo** | Enforcing since Feb 2024 | Emails rejected |
| **Microsoft** | Enforcing since May 2025 | Bounced with `550 5.7.515` |

❌ **No grace period**: All three providers now reject unauthenticated bulk email outright.

### List Hygiene

- [ ] Double opt-in or clear consent
- [ ] Hard bounces removed immediately
- [ ] Inactive suppressed (90 days no engagement)
- [ ] Spam complaints monitored (<0.1%)

### Monitoring Targets

| Metric | Target | Action if Below |
|--------|--------|-----------------|
| Open rate | >20% | Check subject lines, reputation |
| Click rate | >2% | Check content, CTA, relevance |
| Bounce rate | <2% | Clean list |
| Spam rate | <0.1% | Review content, frequency |

---

## Email Revenue Economics (Summary)

Full details: [references/email-economics.md](references/email-economics.md)

### Attribution Models

| Model | Best For |
|-------|----------|
| **Last-click** | Simple reporting |
| **Position-based** | Balanced (40/40/20) |
| **Data-driven** | High volume, accuracy |

### Revenue Per Email Benchmarks

| Campaign Type | Typical RPE | Benchmark |
|---------------|-------------|-----------|
| Welcome series | $0.50 - $2.00 | $1.00 |
| Abandoned cart | $2.00 - $8.00 | $5.00 |
| Newsletter | $0.05 - $0.30 | $0.15 |

### Key ROI Formula

```text
ROI = (Revenue - Costs) / Costs × 100
Example: ($8,000 - $500) / $500 = 1,500%
```

---

## Retention & Churn Economics (Summary)

Full details: [references/email-economics.md](references/email-economics.md)

### Email's Impact on Retention

| Workflow | Churn Impact |
|----------|--------------|
| Onboarding | -20-40% early churn |
| Re-engagement | 5-15% reactivation |
| Renewal reminder | -5-10% involuntary churn |

### Churn Reduction Value

```text
Value = Customers Saved × Remaining LTV × Gross Margin

Example: 50 saved × $1,200 LTV × 80% margin = $48,000/month
```

---

## Channel Mix Economics (Summary)

Full details: [references/email-economics.md](references/email-economics.md)

### Email vs. Other Channels

| Channel | ROAS | Efficiency |
|---------|------|------------|
| **Email (owned)** | 36:1 | Highest |
| **SMS** | 15:1 | High |
| **Paid social** | 3:1 | Medium |
| **Paid search** | 4:1 | Medium |

**Email efficiency**: 20-30% revenue on 1-3% spend = 10-20x efficiency vs. paid

### Email Program ROI

- Annual cost: $64,000 - $150,000
- Annual revenue (100k list): $650,000 - $1,300,000
- **Typical ROI: 500-700%**

---

## Metrics & KPIs

### Metric Reliability (2026)

| Metric | Reliability | Use |
|--------|-------------|-----|
| **Open rate** | Low (MPP) | Trends only |
| **Click rate** | High | Primary engagement |
| **Revenue per email** | High | Primary ROI metric |
| **Conversion rate** | High | Ultimate success |

### Primary Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Click rate | Clicks / Delivered | >2% |
| Conversion rate | Conversions / Clicks | Varies |
| Revenue per email | Revenue / Emails sent | Track trend |
| Email % of revenue | Email revenue / Total | 20-30% |

---

## Platform Setup Guides

- [references/hubspot-setup.md](references/hubspot-setup.md)
- [references/klaviyo-setup.md](references/klaviyo-setup.md)
- [references/mailchimp-setup.md](references/mailchimp-setup.md)

---

## Templates

| Template | Purpose |
|----------|---------|
| [workflow-blueprint.md](assets/workflow-blueprint.md) | Design any workflow |
| [welcome-sequence.md](assets/welcome-sequence.md) | New subscriber welcome |
| [nurture-sequence.md](assets/nurture-sequence.md) | Lead nurturing |
| [cart-abandonment.md](assets/cart-abandonment.md) | E-commerce recovery |
| [email-audit.md](assets/email-audit.md) | Health check template |
| [email-roi-calculator.md](assets/email-roi-calculator.md) | ROI calculation |

---

## Decision Tree (Email Triage)

```text
Open rates low (<15%)?
├─ Check sender reputation
├─ A/B test subject lines
└─ Remove inactive subscribers

Click rates low (<1%)?
├─ Check content relevance
├─ Simplify CTA
└─ Test mobile rendering

High unsubscribes (>0.5%)?
├─ Reduce frequency
├─ Improve segmentation
└─ Add preference center
```

---

## Anti-Patterns

| Anti-Pattern | Instead |
|--------------|---------|
| Batch-and-blast | Segment and trigger |
| No segmentation | Behavioral segments |
| Too many CTAs | One CTA per email |
| Ignoring mobile | Mobile-first design (60%+ opens) |
| Buying lists | Build organically |
| Set-and-forget automations | Monthly performance reviews |
| Relying on open rates | Use click rate, conversions, revenue |

---

## Related Skills

- [marketing-leads-generation](../marketing-leads-generation/SKILL.md) — Lead capture
- [marketing-content-strategy](../marketing-content-strategy/SKILL.md) — Content for emails
- [marketing-cro](../marketing-cro/SKILL.md) — Landing page optimization
- [startup-go-to-market](../startup-go-to-market/SKILL.md) — Channel strategy

---

## Usage Notes (Claude)

- Stay operational: return workflow diagrams, email copy templates, setup steps
- For revenue/ROI questions, reference `references/email-economics.md`
- Always include deliverability requirements (authentication, hygiene)
- Do not invent benchmark data; use ranges or state "varies by industry"
