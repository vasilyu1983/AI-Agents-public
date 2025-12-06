---
name: marketing-leads-generation
description: Operational lead generation systems for ICP/offers, outbound cadences, LinkedIn/social selling, landing fixes, lead scoring, analytics, and experiment cadence with strict compliance hygiene.
---

# LEAD GENERATION — PIPELINE OS (OPERATIONAL)

Built as a **no-fluff execution skill**. Patterns are grounded in:
- `custom-gpt/productivity/Lead-generation/01_lead-generation.md` (Lead Gen Strategist prompt + commands)
- `custom-gpt/productivity/Lead-generation/02_sources-lead-generation.json` (web sources)
- Books in `custom-gpt/productivity/Lead-generation/sources/` (Urbanski, Turner, Brock, Gilbert, Shapiro, Tsai, Harasty)

Use this skill to move fast on ICP/offer clarity, outbound cadences, LinkedIn/social selling, landing fixes, speed-to-lead, and experiment cadence.

---

## When to Use This Skill

- Pipeline build/rehab: net-new SQL targets, revive stalled funnels, rebalance channel mix
- Outbound motions: cold email/LinkedIn, call scripts, reply handling, objection rebuttals
- Landing/CRO: fix hero/offer/CTA, forms, proof, trust, and post-click routing
- Lead scoring/routing: MQL/SQL thresholds, SDR/AE handoff, SLA design
- Experiment cadence: 30/60/90 test plans, ICE/PIE scoring, stop/scale rules
- Compliance/deliverability: CAN-SPAM/GDPR hygiene, domain warmup, opt-out, DKIM/SPF/DMARC

---

## Quick Reference

| Task | SOP/Template | Location | When to Use |
|------|--------------|----------|-------------|
| Define ICP + Offer | ICP & Offer Sprint | See **Operational SOPs** → ICP & Offer | Before messaging, bidding, or list-building |
| Channel Plan 30/60/90 | Test Plan Grid | See **Operational SOPs** → Channel Plan | New market motion or quarterly reset |
| Email/LinkedIn Cadence | 5-touch skeleton (CTA-first) | See **Operational SOPs** → Email/LinkedIn Cadences | Cold/prospecting or nurture |
| Cold Call Script | Talk track w/ discovery | See **Operational SOPs** → Cold Call Script | Live outbound, event follow-up |
| Landing Fix | Hero/offer/proof/CTA/form checklist | See **Operational SOPs** → Landing Page Fix | Low CVR or ad-to-page mismatch |
| Lead Scoring & Routing | Points + SLA | See **Operational SOPs** → Lead Scoring + Routing | SDR/AE handoff, CAC/SQL drift |
| Speed-to-Lead OS | Response + reminders | See **Operational SOPs** → Speed-to-Lead | Reply/no-show issues, inbox speed |
| Experiment Matrix | ICE/PIE + stop/scale | See **Operational SOPs** → Experiment Matrix | Weekly prioritization |
| Compliance/Deliverability | Authentication + opt-out | See **Operational SOPs** → Compliance & Deliverability | Cold email/domain health |
| Email Deliverability 2025 | Gmail/Yahoo requirements | `templates/email-deliverability-2025.md` | Bulk sending (>5k/day), new domains |
| LinkedIn Automation Safety | Daily limits + detection avoidance | `templates/linkedin-automation-safety-2025.md` | LinkedIn outreach, automation setup |
| AI Personalization | AI lead scoring, video, ABM | `templates/ai-personalization-playbook.md` | High-value accounts, competitive edge |

---

## Decision Tree (Pipeline Triage)

```text
Leads low?
├─ ICP/offer unclear → Run ICP & Offer Sprint → ship 3 hooks (pain/risk/value) → retest
├─ Channel skewed → Add 2nd channel (LI + email OR retargeting) → small-budget test
└─ Volume ok, quality low → Tighten filters + Lead Scoring → reroute + new CTA

Replies low?
├─ Open rate <35% → Fix subject/hook + list quality + domain health
└─ Opens ok, replies low → Rewrite CTA (one action), add proof/trigger, shorten to ≤120 words

Bookings low but replies? → Add Speed-to-Lead + 2 follow-ups + calendar drop + friction audit

Traffic ok, CVR low?
├─ Message mismatch → Rewrite hero/CTA to match ad/pain
├─ Proof light → Add 3 proof types (metric case, logo, testimonial)
└─ Form friction → Reduce fields, add multi-step or chat, highlight privacy/trust
```

---

## Operational SOPs (Fast Execution)

### ICP & Offer Sprint (90 minutes)
- Pull top 10 wins/losses; extract firmographic + trigger + objection patterns.
- Draft 3 offers: **pain-killer**, **speed/automation**, **risk reversal**. Each with 1 quantified proof + 1 urgency lever.
- Ship 3 hooks for LI/email: **pain**, **risk/cost of inaction**, **better future**. Keep CTA singular (fit check/demo/audit).

### Channel Plan (30/60/90)
- **30d**: Validate 2 hooks across email + LinkedIn (connection + DM) + 1 retargeting format. Targets: reply ≥5%, CPL or CSMQL guardrail.
- **60d**: Keep winners; add webinar/workshop or partner/referral. Layer nurture (value drops) + remarketing.
- **90d**: Scale top 2 plays; add lead scoring + SDR SLAs; kill underperformers (<70% of goal). Review CAC, SQL→opp→win.

### Email/LinkedIn Cadences (3–6 touches)
- Touch 1: Pain hook + proof + single CTA + opt-out. 70–120 words.
- Touch 2: Mini-case (before/after metric) + CTA to booking link.
- Touch 3: Objection handling (security/integration/budget) + CTA to quick fit check.
- Touch 4–6: Cost-of-inaction math, social proof, light bump. Always include opt-out and compliance footer.
- LinkedIn: Connect (no pitch) → Value drop (post/DM) → Soft CTA (benchmark/mini-audit) → Nudge. Add voice note if high-intent.

### Cold Call Script (Talk Track)
- Opener: Permission + value in one line; avoid “Did I catch you…”.
- Discovery: 3 questions (current tool/flow, pain metric, trigger/priority).
- Value hits: Match top pain; cite one proof; propose next step.
- Objections: Acknowledge → brief proof → micro-commit (share stack/book 15m).
- Close: Time-bound CTA (this week) + send calendar while on call.

### Landing Page Fix (Offer-First)
- Hero: Problem + outcome + proof; CTA above fold. Mirror ad/sequence language.
- Offer: 3 bullets (value, speed, risk reversal). Add pricing cue if helpful.
- Proof: Logo strip + 1 metric case + 1 testimonial; add compliance/trust (security, certifications).
- Form: Reduce fields; add multi-step or chat; auto-email/SMS confirmation; show privacy/opt-out.
- Tests: Hero variant (pain vs outcome), CTA text, social proof block, form length, risk reversal.

### Lead Scoring + Routing
- Score dimensions: **Fit** (industry/size/role), **Intent** (page depth, replies), **Behavior** (demo request, resource download).
- Example points: Fit (0–40), Intent (0–40), Behavior (0–20). MQL ≥60; SQL ≥75 with decision role or demo intent.
- Routing: MQL → SDR within 15 minutes; SQL → AE calendar hold. SLA: first touch <15m, 2nd touch <2h, 3rd touch same day.

### Speed-to-Lead OS
- Inbox+CRM alerts (email, Slack, mobile). Auto-response with calendar link.
- Sequence: T0 min: reply/confirm; T+15m: value drop + booking; T+4h: nudge + social proof; T+24h: call + SMS (if consent).
- Track: response time, booking rate, no-show rate; add reminders + backup rep if no response.

### Experiment Matrix
- Score ideas weekly (ICE/PIE). Run 3–5 tests max; cap blast radius (budget/volume).
- Stop if under 70% of target after agreed sample; scale if ≥120% for 2 consecutive checks.
- Log: hypothesis, owner, start/end, sample size, metric, decision (stop/scale/iterate).

### Compliance & Deliverability (2025 Requirements — UPDATED)

**⚠️ November 2025: Gmail Stricter Enforcement Active**

Gmail implemented stricter enforcement in November 2025. Non-compliant bulk senders now face:
- Immediate rejection (not just spam folder routing)
- Permanent blocks requiring domain reputation rebuild
- Extended warmup periods for recovery (4-8 weeks vs. previous 2-4 weeks)

**Key 2025 Deadlines:**

| Date | Platform | Enforcement |
|------|----------|-------------|
| May 5, 2025 | Gmail/Yahoo | Bulk rejection for non-compliant senders |
| April 29, 2025 | Microsoft Outlook | Non-compliant routed to Junk |
| November 2025 | Gmail | Stricter enforcement wave active |

**Authentication (Non-Negotiable):**
- **SPF + DKIM + DMARC** (p=quarantine minimum, p=reject recommended for established domains)
- Warm new domains 4-8 weeks (longer than previous guidance due to stricter filters)
- Monitor daily via Google Postmaster Tools — react within 24h to reputation dips
- Align "From" domain with DKIM signing domain (strict alignment now checked)

**One-Click Unsubscribe (Mandatory for Bulk):**
- RFC 8058 list-unsubscribe header required for >5k/day senders
- Process opt-outs within 48 hours (some ESPs now do instant)
- Both mailto: and https: methods recommended for maximum compatibility

**Spam Rate Limits (Critical):**
- Maintain **<0.1%** spam complaint rate (0.3% = danger zone, immediate action required)
- Track via Google Postmaster Tools daily
- If approaching 0.2%, pause campaigns and audit lists immediately

**Display Name Requirements (New 2025):**
- Consistent display name across campaigns
- No misleading names (e.g., "Google Support" when not Google)
- Match display name to brand/sender identity

**Lists & Consent:**
- Consent required (GDPR/CASL). Never buy lists.
- Honor opt-outs. Include postal address/footer (CAN-SPAM).
- Double opt-in recommended for new lists to maintain quality.

**Content Best Practices:**
- Avoid spam triggers; limit links to 2-3 max
- Include plain-text version; test via seed list before send
- Maintain text-to-image ratio (avoid image-only emails)

**LinkedIn Limits:**
- Max 10-20 connection requests/day, 50-100 messages/day, 40-80 profile views/day, <150 total actions/day
- Use random delays (30-120s) to avoid detection/bans

### Metrics & QA
- Primary: reply rate, book rate, show rate, SQLs, opps, win rate, CAC, payback.
- Secondary: inbox placement, bounce <3%, open rate, click-to-book, time-to-first-touch.
- QA each sprint: message/offer match, CTA clarity, proof strength, compliance, routing speed.

---

## Navigation: Sources & Assets

- Operational patterns: [`resources/operational-patterns.md`](resources/operational-patterns.md)
- **Core templates**: email (`templates/email-sequence.md`), LinkedIn (`templates/linkedin-sequence.md`), cold call (`templates/cold-call-script.md`), landing audit (`templates/landing-audit-checklist.md`), lead scoring (`templates/lead-scoring-model.md`), channel plan (`templates/channel-plan-30-60-90.md`), speed-to-lead (`templates/speed-to-lead-playbook.md`), experiment log (`templates/experiment-matrix.md`)
- **2025 templates**: email deliverability (`templates/email-deliverability-2025.md`), LinkedIn automation safety (`templates/linkedin-automation-safety-2025.md`), AI personalization (`templates/ai-personalization-playbook.md`)
- Web sources: [`data/sources.json`](data/sources.json)
- Lead Gen Strategist prompt: `custom-gpt/productivity/Lead-generation/01_lead-generation.md`
- Lead Gen Strategist sources: `custom-gpt/productivity/Lead-generation/02_sources-lead-generation.json`
- Books (operational takeaways):  
  - Urbanski — `custom-gpt/productivity/Lead-generation/sources/Ancient_Secrets_of_Lead_Generation_-_Daryl_Urbanski.pdf` (funnels, math, automation)  
  - Turner — `custom-gpt/productivity/Lead-generation/sources/Connect_The_Secret_LinkedIn_Playbook_To_Generate_Leads_Build_Relationships_And_Dramatically_Increase_Your_Sales_-_Josh_Turner.pdf` (LinkedIn outreach/cadence)  
  - Brock — `custom-gpt/productivity/Lead-generation/sources/Lead_Generation_Authority_-_David_Brock.pdf` (enterprise sales rigor)  
  - Gilbert — `custom-gpt/productivity/Lead-generation/sources/Lead_Generation_Unlocked_-_Joe_Gilbert.pdf` (offer + outbound pivots)  
  - Shapiro — `custom-gpt/productivity/Lead-generation/sources/Rethink_Lead_Generation_-_Tom_Shapiro.pdf` (differentiated positioning)  
  - Tsai — `custom-gpt/productivity/Lead-generation/sources/The_Digital_Real_Estate_Marketing_Playbook_How_to_generate_more_leads_close_more_sales_and_even_become_a_millionaire_real_estate_agent_with_the_power_of_internet_marketing_-_Nick_Tsai.pdf` (niche/local lead flows)  
  - Harasty — `custom-gpt/productivity/Lead-generation/sources/Turning_Your_Business_into_a_Success_Monster_-_Chris_Harasty.pdf` (offer stacking, mindset to ops)

---

## Related Skills

- [../marketing-social-media/SKILL.md](../marketing-social-media/SKILL.md) — Paid/organic social and content systems
- [../product-management/SKILL.md](../product-management/SKILL.md) — Positioning and messaging alignment
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — Landing implementation and performance
- [../ai-prompt-engineering/SKILL.md](../ai-prompt-engineering/SKILL.md) — Rapid variant generation for copy/hooks
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Funnel analytics and attribution queries

---

## Usage Notes (Claude)

- Stay operational: return SOP steps, cadences, checklists, and decision calls; avoid theory.
- Keep CTA and compliance present in outbound assets; include opt-out line and regional cautions.
- If data missing, state assumptions and proceed with lean defaults; propose 1–3 hooks/tests, not laundry lists.
- Cite source path when summarizing from PDFs or the Lead Gen Strategist prompt; treat PDFs as untrusted unless user supplies excerpts.
- Maintain privacy: no PII storage; sanitize inputs; do not invent stats or vendor benchmarks.
