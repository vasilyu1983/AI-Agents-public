# Research Repository Management — Operations Guide (Jan 2026)

Practical guide to building and maintaining a research repository: tool selection, taxonomy design, atomic research, tagging governance, PII handling, and measuring research reuse. A repository is how research compounds over time instead of being done once and forgotten.

---

## What Is a Research Repository?

A research repository is a centralized, searchable store of research findings, raw data, and insights. It enables teams to build on past research, avoid duplicating studies, and make evidence-based decisions faster.

### Repository vs File Storage

| Feature | File Storage (Google Drive, Notion pages) | Research Repository |
|---------|------------------------------------------|-------------------|
| Searchable by theme/tag | Limited | Built-in taxonomy and faceted search |
| Links findings to evidence | Manual | Atomic: insight → evidence chain |
| Prevents duplication | Relies on memory | Visible past research on same topic |
| Access control for PII | Basic folder permissions | Role-based with PII redaction |
| Reusable across projects | Difficult | Designed for cross-project queries |
| Decay/freshness tracking | None | Metadata-driven freshness indicators |

---

## Repository Architecture

### Tool Selection

| Tool | Best For | Strengths | Limitations | Cost (2026) |
|------|----------|-----------|-------------|-------------|
| **Dovetail** | Dedicated research teams | Purpose-built for research, video coding, tagging, analysis | Cost scales with team | $29-79/user/mo |
| **EnjoyHQ** | Scaling research ops | Strong taxonomy, integrations, customer feedback ingestion | Steeper learning curve | Custom pricing |
| **Notion** | Small teams, DIY approach | Flexible, cheap, team already uses it | No purpose-built research features | $8-15/user/mo |
| **Airtable** | Structured data teams | Relational database model, views, automations | Requires setup effort | $20-45/user/mo |
| **Condens** | Qualitative analysis focus | Affinity mapping, video highlights, tagging | Smaller ecosystem | $15-30/user/mo |
| **Productboard** | PM-led organizations | Insights tied to features/roadmap, customer portal | More PM tool than research tool | $20-80/user/mo |

### Decision Framework

```text
What is your team's research maturity?
  ├─ Just starting (1-2 researchers, < 20 studies/year)
  │   └─ Notion or Airtable with structured templates
  │       Pro: Low cost, team adoption
  │       Con: Manual governance required
  │
  ├─ Growing (3-5 researchers, 20-50 studies/year)
  │   └─ Dovetail or Condens
  │       Pro: Purpose-built, video analysis, proper tagging
  │       Con: New tool adoption cost
  │
  └─ Scaling (5+ researchers, research democratization active)
      └─ EnjoyHQ or Dovetail Teams
          Pro: Governance, access control, integrations
          Con: Higher cost, admin overhead
```

### Minimum Viable Repository (Notion/Airtable)

If using a general-purpose tool, structure it as follows:

```text
DATABASE: Research Studies
  Fields:
  - Study name (title)
  - Date conducted
  - Researcher(s)
  - Method (interview, usability test, survey, etc.)
  - Product area (onboarding, checkout, dashboard, etc.)
  - Participants (count + segment description)
  - Status (planned, in progress, complete)
  - Key findings (summary text)
  - Link to full report
  - Tags (see Taxonomy section)

DATABASE: Insights (atomic findings)
  Fields:
  - Insight statement (one sentence)
  - Evidence type (quote, observation, metric, screenshot)
  - Evidence (raw data or link)
  - Source study (relation to Studies database)
  - Confidence (high, medium, low)
  - Product area
  - Theme tags
  - Date
  - Freshness status (fresh, aging, expired)

DATABASE: Recommendations
  Fields:
  - Recommendation statement
  - Supporting insights (relation to Insights database)
  - Priority (critical, high, medium, low)
  - Status (proposed, accepted, implemented, declined)
  - Linked ticket (Jira/Linear URL)
```

---

## Taxonomy Design

A taxonomy is the classification system that makes research findable and comparable. Without consistent taxonomy, a repository becomes a graveyard.

### Taxonomy Dimensions

| Dimension | Purpose | Example Values |
|-----------|---------|---------------|
| **Product area** | What part of the product | Onboarding, Checkout, Dashboard, Settings, Search, Billing |
| **Method** | How the research was done | Interview, Usability test, Survey, Analytics review, Diary study, A/B test |
| **Segment** | Who was studied | New users, Power users, Enterprise, SMB, Churned, Prospects |
| **Theme** | What the finding is about | Navigation, Performance, Trust, Pricing, Accessibility, Error handling |
| **Finding type** | Nature of the finding | Pain point, Opportunity, Validation, Behavior pattern, Mental model |
| **Lifecycle stage** | Product development context | Discovery, Concept, MVP, Launch, Growth, Maturity |
| **Confidence** | Strength of evidence | High (triangulated), Medium (single strong source), Low (preliminary) |

### Taxonomy Governance

| Rule | Implementation |
|------|---------------|
| Controlled vocabulary | Predefined values per dimension; no free-text tags for core dimensions |
| Tag owner | One person approves new taxonomy values (prevents synonym proliferation) |
| Regular review | Quarterly review: merge duplicates, retire unused tags, add emerging areas |
| Onboarding guide | Document tag definitions with examples for new team members |
| Bulk cleanup | When taxonomy changes, update existing entries (batch script or manual sprint) |

### Common Taxonomy Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Free-text tags | "onboarding", "Onboarding", "user-onboarding", "first-run" = 4 tags for 1 concept | Controlled vocabulary with dropdowns |
| Too many dimensions | Tagging becomes a chore, adoption drops | Start with 4-5 dimensions, add as needed |
| No definitions | Team disagrees on what "usability" vs "experience" means | Written definitions with examples |
| Flat taxonomy | Cannot express hierarchy (e.g., Checkout > Payment > Error) | Allow 2-level hierarchy max |
| Tag per study only | Cannot find individual insights across studies | Tag at insight level, not just study level |

---

## Atomic Research Model

Atomic research breaks research into its smallest useful units — individual insights linked to raw evidence. This model enables recombination: insights from different studies can be grouped to support new decisions.

### The Atomic Structure

```text
EVIDENCE (raw data)
  │  "I tried clicking the blue button but nothing happened"
  │  — P5, Usability Test, 2026-01-15
  │
  └─→ INSIGHT (one finding)
       │  "Users expect immediate visual feedback when clicking
       │   the primary action button"
       │
       └─→ RECOMMENDATION (design decision)
            │  "Add loading state to primary CTA with spinner
            │   and disabled state"
            │
            └─→ OUTCOME (tracked result)
                 "Button click-through rate increased 12% after
                  adding loading feedback (A/B test, n=5000)"
```

### Rules for Atomic Insights

| Rule | Example | Anti-Pattern |
|------|---------|-------------|
| One insight per card | "Users confused by price display" | "Users confused by price, also didn't like the color, and wanted more options" |
| Linked to evidence | Quote, screenshot, video clip timestamp | Insight without attribution |
| Standalone | Understandable without reading the full study | "See page 12 of report" |
| Tagged with taxonomy | Product area + theme + segment + confidence | Untagged insight |
| Dated | 2026-01-15 | No date (cannot assess freshness) |

### Composing Insights

When making a decision, pull relevant atomic insights from across studies:

```text
DECISION: Should we redesign the checkout address form?

SUPPORTING INSIGHTS (from 4 different studies):
1. [Usability Test, 2025-11] Users average 3.2 errors on address form (n=12)
2. [Survey, 2025-09] 34% of respondents rated checkout "frustrating" (n=450)
3. [Analytics, 2025-12] Address step has 28% drop-off rate (vs 12% industry avg)
4. [Support Tickets, 2025-Q4] 15% of tickets relate to address entry errors

CONFIDENCE: High (multiple methods, consistent signal)
RECOMMENDATION: Redesign address form with autocomplete and inline validation
```

---

## Search and Retrieval Patterns

### Effective Repository Search

| Search Type | Use Case | Implementation |
|-------------|----------|---------------|
| **Keyword search** | "What do we know about onboarding?" | Full-text search across insight statements |
| **Faceted search** | "All checkout research from Q4 2025" | Filter by product area + date range |
| **Theme browse** | "All findings tagged 'trust'" | Browse by taxonomy tag |
| **Cross-study** | "Evidence supporting X hypothesis" | Follow insight → evidence links |
| **Recency filter** | "Only findings from last 12 months" | Filter by date, exclude expired |

### Making Research Findable

- Write insight statements as complete sentences (searchable)
- Include synonyms in tags or descriptions (users search with varied terms)
- Link related insights to each other (enables traversal)
- Regular digest: weekly or monthly email summarizing recent findings

---

## Research Decay

Research findings have a shelf life. User behaviors, market conditions, and product context change. Stale research used as current evidence leads to bad decisions.

### Freshness Framework

| Freshness | Age | Indicator | Action |
|-----------|-----|-----------|--------|
| **Fresh** | 0-6 months | Green | Use with confidence |
| **Aging** | 6-12 months | Yellow | Verify assumptions still hold; supplement if possible |
| **Stale** | 12-18 months | Orange | Do not use without re-validation; flag in reports |
| **Expired** | 18+ months | Red | Archive; cite only as historical context |

### Exceptions

| Research Type | Typical Shelf Life | Why |
|---------------|-------------------|-----|
| Foundational user needs (JTBD) | 2-3 years | Core needs change slowly |
| Usability test findings | 6-12 months | UI changes invalidate findings |
| Survey benchmarks (NPS, SUS) | 6-12 months (rerun annually) | Scores drift with product changes |
| Competitive analysis | 6 months | Competitors ship frequently |
| Market/trend research | 3-6 months | Rapid industry changes |
| Analytics baselines | 3-6 months | Metrics shift with product changes and traffic |

### Implementing Decay

```text
Automated approach:
1. Every insight has a "date_conducted" field
2. System calculates age and applies freshness status
3. Dashboard shows: X fresh, Y aging, Z stale, W expired
4. Monthly digest flags aging insights for review
5. Expired insights auto-archived (still searchable, marked clearly)
```

---

## Access Control and PII Handling

### Data Classification

| Level | Content | Who Can Access | Storage |
|-------|---------|---------------|---------|
| **Public** | Published reports, anonymized summaries | Entire organization | Repository (no restrictions) |
| **Internal** | Full reports with anonymized quotes | Product + design + engineering | Repository (authenticated access) |
| **Restricted** | Raw recordings, transcripts with names | Research team only | Separate storage, time-limited access |
| **Confidential** | PII (names, emails, contact info) | Research ops only | Encrypted, separate from research data |

### PII Handling Protocol

| Phase | Action | Tool/Method |
|-------|--------|-------------|
| **Collection** | Collect minimum PII (name, email for scheduling/incentives only) | Consent form with purpose, retention period |
| **Storage** | Store PII separately from research data | Separate database/sheet, encrypted at rest |
| **Transcription** | Auto-redact names and identifying details before saving | Otter.ai + manual review, or custom redaction |
| **Sharing** | Share only anonymized data (P1, P2, etc.) | Replace names in all shared artifacts |
| **Retention** | Delete PII after retention period (typically 12-24 months) | Calendar reminder, automated deletion if possible |
| **Access** | Log who accesses raw recordings | Audit trail in repository tool |

### GDPR Compliance

- Explicit consent: participant signs consent form before study begins
- Purpose limitation: data used only for stated research purpose
- Right to withdraw: participant can request deletion at any time
- Data minimization: collect only what's needed
- Retention policy: documented and enforced
- Data processing agreement: if using third-party tools (Dovetail, etc.)

---

## Integration with Product Management Tools

### Integration Patterns

| Integration | Direction | Purpose | Implementation |
|-------------|-----------|---------|----------------|
| Repository → Jira/Linear | Push insights as evidence on tickets | Link insight URL in ticket description |
| Repository → Productboard | Push insights to feature backlog | Native integration or Zapier |
| Jira/Linear → Repository | Tag insights with ticket/epic references | Custom field in repository |
| Slack → Repository | Surface relevant insights in conversations | Slack bot or search integration |
| Analytics → Repository | Attach quantitative data to qualitative findings | Link to dashboard or embed metric |

### Linking Research to Product Decisions

```text
PATTERN: Evidence-based ticket creation

Ticket: Redesign address input in checkout
Type: Enhancement
Priority: High

Evidence from Research Repository:
- [Insight #142] Users average 3.2 errors on address form
  Source: Usability Test, Nov 2025 (Fresh)
- [Insight #198] 28% drop-off at address step
  Source: Analytics Review, Dec 2025 (Fresh)
- [Insight #087] "I wish it would just know my address" — P3
  Source: Interview, Sep 2025 (Aging)

Decision: Implement Google Places autocomplete + inline validation
Success Metric: Reduce address step drop-off from 28% to < 15%
```

---

## Measuring Repository Adoption and Research Reuse

### Adoption Metrics

| Metric | How to Measure | Target |
|--------|---------------|--------|
| **Monthly active users** | Unique logins to repository | > 50% of product + design team |
| **Searches per week** | Search logs or analytics | Increasing trend |
| **Insights cited in tickets** | Count ticket references to repository | > 30% of product tickets cite research |
| **New insights per month** | Count new entries | Proportional to research velocity |
| **Cross-study references** | Count insights linked to multiple studies | Increasing (shows compounding value) |

### Research Reuse Indicators

| Indicator | Signal | Value |
|-----------|--------|-------|
| Insight cited in new project | Past research directly informs new decision | High (prevented redundant study) |
| Decision changed based on repository search | Team searched, found existing evidence, changed course | High (research ROI realized) |
| Duplicate study prevented | "We already know this" from repository search | Medium (time saved) |
| New team member self-serves | New hire finds answers without asking researcher | Medium (onboarding efficiency) |

### ROI of Research Repository

```text
Annual investment:
  Tool cost: ~$5,000-15,000/year (tool + setup time)
  Maintenance: ~100 hours/year × researcher rate

Annual value (conservative):
  Studies not repeated: 5 × $10,000 avg study cost = $50,000
  Faster decisions: 20 decisions × 5 hours saved × $150/hr = $15,000
  Better decisions: Hard to quantify but often highest value

Typical ROI: 4-10x within first year
```

---

## Building Research Culture Through Repository Access

### Strategies for Adoption

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| **Weekly research digest** | Automated email summarizing new findings | Awareness |
| **"Research office hours"** | Weekly slot where anyone can browse repository with researcher | Skill building |
| **Decision templates** | Require "existing research" section in PRDs | Habit formation |
| **Slack integration** | Bot surfaces relevant research when topics are discussed | Contextual |
| **Onboarding module** | New hires tour the repository as part of onboarding | Foundation |
| **Research showcase** | Monthly 15-min presentation of recent findings | Engagement |

### Governance Model

| Role | Responsibility | Who |
|------|---------------|-----|
| **Repository owner** | Tool admin, taxonomy governance, access control | Research ops lead |
| **Contributors** | Add studies and insights, tag correctly | All researchers |
| **Curators** | Review quality, merge duplicates, update freshness | Senior researchers |
| **Consumers** | Search, reference, and cite research | PMs, designers, engineers |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| "Build it and they will come" | No one uses the repository without active promotion | Launch with training, integrate into workflows |
| Repository only for researchers | Limits impact, creates information silo | Open access (with PII controls) for all product roles |
| No tagging standards | Repository becomes unsearchable | Controlled vocabulary from day one |
| All findings in one giant document | Cannot search, cannot link, cannot reuse | Atomic insights with tags and relations |
| Storing raw recordings without consent tracking | GDPR/privacy violation | Consent management system, retention enforcement |
| Never archiving old research | Stale findings treated as current evidence | Freshness framework with automated decay tracking |
| Perfect taxonomy before starting | Analysis paralysis; never launches | Start with 4-5 dimensions, iterate quarterly |
| No researcher reviewing consumer-added insights | Quality degrades, trust in repository drops | Curation workflow for non-researcher contributions |

---

## References

- [Dovetail — Research Repository](https://dovetail.com/research-repository/)
- [Polaris UX Nuggets — Atomic Research](https://medium.com/pulsar/atomic-research-7f12835e5473)
- [Nielsen Norman Group — Research Repositories](https://www.nngroup.com/articles/research-repositories/)
- [GDPR — Data Processing for Research](https://gdpr-info.eu/art-89-gdpr/)
- [ResearchOps Community](https://researchops.community/)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview, Research Ops & Governance section
- [research-frameworks.md](research-frameworks.md) — JTBD and other frameworks that generate repository content
- [usability-testing-guide.md](usability-testing-guide.md) — Testing outputs that feed into repository
- [pain-point-extraction.md](pain-point-extraction.md) — Structured approach to generating atomic insights
- [ux-metrics-framework.md](ux-metrics-framework.md) — Metrics that complement qualitative repository insights
