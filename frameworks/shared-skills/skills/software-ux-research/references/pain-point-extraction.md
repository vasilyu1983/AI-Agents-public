# Pain Point Extraction Guide

Extract actionable pain points from user feedback. Output feeds `software-ui-ux-design` for pattern selection.

---

## Quick Reference

| Input Source | Extraction Method | Output |
|--------------|-------------------|--------|
| App Store reviews | Star rating decoder + keyword scan | Pain point list |
| G2/Capterra | Cons section + theme clustering | Competitive gaps |
| Support tickets | Tag analysis + thematic synthesis | Friction map |
| NPS open-ends | Sentiment + theme extraction | Priority matrix |
| Social mentions | Keyword monitoring + sentiment | Real-time alerts |

---

## Input Sources

### B2C: App Store & Play Store

**Export Methods:**

```bash
# App Store Connect - Manual export
1. App Store Connect → My Apps → [App] → App Analytics → Reviews
2. Filter by: Version, Rating, Territory
3. Export CSV

# Play Console - Manual export
1. Play Console → Quality → Ratings & Reviews
2. Filter by: Rating, Device, Android version
3. Download CSV
```

**Automated via AppFollow:**

```bash
# AppFollow API (if using)
GET https://api.appfollow.io/reviews?app_id={id}&country={code}
Headers: X-AppFollow-API-Token: {token}
```

### B2B: G2, Capterra, TrustRadius

**Manual Extraction:**

1. Go to G2.com → Search competitor
2. Click "Reviews" tab
3. Filter: "Most Recent" or "Lowest Rating"
4. Focus on "What do you dislike?" section
5. Copy quotes into extraction template

**Export (G2 Paid):**

```
G2 Seller Solutions → Competitive Intelligence → Export Reviews
```

### Support Tickets

**Zendesk Export:**

```bash
# Zendesk API
GET https://{subdomain}.zendesk.com/api/v2/tickets.json?status=solved
# Filter by tags: ux, bug, feature-request
```

**Intercom Export:**

```bash
# Intercom - Use Data Export feature
Settings → Data Management → Export Data → Conversations
```

### NPS/CSAT Open-Ends

**Collection Points:**

| Trigger | Question | Expected Insight |
|---------|----------|------------------|
| Post-onboarding | "What was confusing?" | First-run friction |
| Post-purchase | "What almost stopped you?" | Checkout barriers |
| Churn survey | "Why are you leaving?" | Critical failures |
| Feature release | "How was [feature]?" | Adoption blockers |

---

## Extraction Process

### Step 1: Categorize by Pain Point Type

| Category | Signal Words | Severity | Example Quote |
|----------|--------------|----------|---------------|
| **Crash/Bug** | crashes, broken, doesn't work, error, freeze | Critical | "App crashes every time I try to login" |
| **Performance** | slow, loading, lag, takes forever | High | "Takes 10 seconds to load my dashboard" |
| **UX Friction** | confusing, can't find, too many steps, complicated | High | "Can't figure out how to change my settings" |
| **Onboarding** | don't understand, how do I, setup, getting started | High | "Spent 30 minutes figuring out the first step" |
| **Missing Feature** | wish, need, should have, would be nice | Medium | "Wish I could export to PDF" |
| **Visual/UI** | ugly, outdated, cluttered, hard to read | Medium | "The interface looks like it's from 2010" |
| **Pricing** | expensive, not worth, cheaper alternatives | Low (for UX) | "Too expensive for what it does" |
| **Support** | no response, unhelpful, can't contact | Low (for UX) | "Support never got back to me" |

### Step 2: Extract Themes

Core approach:

- Use manual coding or tool-assisted clustering to extract themes.
- Keep traceability: each theme links back to raw quotes/tickets.
- Don’t treat summaries as evidence without links to source.

#### Optional: AI/Automation — LLM Prompts

> Use only if you’re applying AI/automation to speed up extraction. Redact PII first.

**Prompt for Theme Extraction:**

```
Analyze these user reviews and extract pain points.

For each pain point, provide:
1. Category (Crash/Bug, Performance, UX Friction, Onboarding, Missing Feature, Visual/UI)
2. Frequency (count of mentions)
3. Severity (Critical, High, Medium, Low)
4. Representative quote
5. Affected user flow/screen

Reviews:
{paste reviews here}

Output as a markdown table sorted by severity.
```

**Prompt for Sentiment Classification:**

```
Classify each review's sentiment and extract the core complaint.

Format:
- Sentiment: Positive/Negative/Neutral/Mixed
- Core complaint: [one sentence]
- Affected feature: [feature name]
- Urgency: [Immediate/Soon/Eventually/Never]

Review: {review text}
```

### Step 3: Score & Prioritize

**Priority Formula:**

```
Priority Score = Frequency × Severity × Business Impact

Where:
- Frequency: Count of mentions (1-10 scale)
- Severity: Critical=10, High=7, Medium=4, Low=1
- Business Impact: Revenue risk=10, Churn risk=7, NPS risk=4, Nice-to-have=1
```

**Example Calculation:**

| Pain Point | Frequency | Severity | Business Impact | Score |
|------------|-----------|----------|-----------------|-------|
| Login crashes | 8 | 10 (Critical) | 10 (Revenue risk) | 800 |
| Slow dashboard | 6 | 7 (High) | 7 (Churn risk) | 294 |
| Missing dark mode | 4 | 4 (Medium) | 1 (Nice-to-have) | 16 |

### Step 4: Map to User Journey

| Journey Stage | Common Pain Points | Design Pattern Fix |
|---------------|--------------------|--------------------|
| **Awareness** | Can't find info, unclear value prop | Landing page clarity |
| **Onboarding** | Confusing setup, too many steps | Progressive disclosure |
| **First Value** | Don't know what to do, empty state | Guided tours, templates |
| **Regular Use** | Can't find features, slow performance | Navigation, skeleton screens |
| **Advanced Use** | Missing features, limitations | Feature flags, integrations |
| **Renewal/Churn** | Billing issues, better alternatives | Retention flows |

---

## Output Format

### Pain Point Report Template

```markdown
## Pain Point Report: [Product Name]
**Analysis Date**: [YYYY-MM-DD]
**Sources Analyzed**: [List: App Store, G2, Zendesk, etc.]
**Total Feedback Items**: [N]
**Period**: [Date range]

---

### Critical (Immediate Action Required)

| # | Pain Point | Frequency | Severity | Quote | Flow | Pattern |
|---|------------|-----------|----------|-------|------|---------|
| 1 | [Issue] | X mentions | Critical | "[quote]" | [Stage] | [Link] |

**Recommended Action**: [Specific fix]
**Owner**: [Team/Person]
**Timeline**: [Immediate/This sprint]

---

### High Priority (Next Sprint)

| # | Pain Point | Frequency | Severity | Quote | Flow | Pattern |
|---|------------|-----------|----------|-------|------|---------|
| 1 | [Issue] | X mentions | High | "[quote]" | [Stage] | [Link] |

---

### Medium Priority (Backlog)

| # | Pain Point | Frequency | Severity | Quote | Flow | Pattern |
|---|------------|-----------|----------|-------|------|---------|

---

### Feature Requests (Evaluate)

| # | Request | Frequency | User Segment | Competitor Has? |
|---|---------|-----------|--------------|-----------------|

---

### Summary

- **Total pain points identified**: [N]
- **Critical issues**: [N]
- **Top 3 priorities**:
  1. [Issue 1]
  2. [Issue 2]
  3. [Issue 3]
```

---

## Pain Point → UI Pattern Mapping

| Pain Point Type | Suggested Patterns | Resource |
|-----------------|--------------------| ---------|
| **Slow loading** | Skeleton screens, optimistic UI | [modern-ux-patterns-2025.md](../../software-ui-ux-design/references/modern-ux-patterns-2025.md) |
| **Confusing navigation** | Breadcrumbs, tab navigation, search | [nielsen-heuristics.md](../../software-ui-ux-design/references/nielsen-heuristics.md) |
| **Too many steps** | Progressive disclosure, wizards | [modern-ux-patterns-2025.md](../../software-ui-ux-design/references/modern-ux-patterns-2025.md) |
| **Can't find features** | Command palette, improved IA | [design-systems.md](../../software-ui-ux-design/references/design-systems.md) |
| **Empty states** | Action-oriented prompts, templates | [modern-ux-patterns-2025.md](../../software-ui-ux-design/references/modern-ux-patterns-2025.md) |
| **Form errors** | Inline validation, clear messages | [nielsen-heuristics.md](../../software-ui-ux-design/references/nielsen-heuristics.md) |
| **Onboarding confusion** | Guided tours, checklist progress | [modern-ux-patterns-2025.md](../../software-ui-ux-design/references/modern-ux-patterns-2025.md) |
| **Accessibility issues** | WCAG compliance | [wcag-accessibility.md](../../software-ui-ux-design/references/wcag-accessibility.md) |
| **Visual clutter** | Whitespace, hierarchy, grouping | [frontend-aesthetics-2025.md](../../software-ui-ux-design/references/frontend-aesthetics-2025.md) |
| **Outdated design** | Design system refresh | [component-library-comparison.md](../../software-ui-ux-design/references/component-library-comparison.md) |

---

## Frequency Tracking

### Weekly Digest Format

```markdown
## Weekly Feedback Digest: [Week of YYYY-MM-DD]

### Volume
- App Store: [N] reviews (↑/↓ X% vs last week)
- G2: [N] reviews
- Support tickets: [N] tagged "ux"
- NPS open-ends: [N] responses

### Sentiment Trend
- Positive: [X]%
- Neutral: [X]%
- Negative: [X]%

### Top 3 Themes This Week
1. [Theme] - [N] mentions - [Trend: New/Growing/Stable/Declining]
2. [Theme] - [N] mentions
3. [Theme] - [N] mentions

### New Pain Points (Not seen before)
- [Pain point]: [N] mentions

### Resolved (No longer appearing)
- [Pain point]: Last seen [date]
```

---

## Integration with JTBD Framework

Map pain points to Jobs-to-be-Done for root cause analysis:

| Pain Point | Surface Issue | Underlying Job | Forces Analysis |
|------------|---------------|----------------|-----------------|
| "Can't find settings" | Navigation problem | "Make the app work how I want" | Push: Frustration. Pull: Control. |
| "Too slow" | Performance | "Get work done quickly" | Push: Wasted time. Pull: Efficiency. |
| "Missing export" | Feature gap | "Share my work with others" | Push: Blocked workflow. Pull: Collaboration. |

See [research-frameworks.md](research-frameworks.md#jtbd) for full JTBD methodology.

---

## Optional: AI/Automation — Automation Options

> Use only if you’re automating ingestion/classification. Ensure PII handling and access controls are defined first.

### Set Up Continuous Monitoring

**Option 1: AppFollow (B2C)**

- Auto-collects App Store + Play Store reviews
- Sentiment tagging
- Slack/email alerts for negative reviews
- Pricing: Free tier → $79/mo

**Option 2: G2 Seller Solutions (B2B)**

- Competitive review tracking
- Buyer intent signals
- Quarterly reports
- Pricing: Contact sales

**Option 3: Custom with GPT + Zapier**

1. Zapier: New Zendesk ticket → Webhook
2. Webhook → GPT API for classification
3. GPT response → Notion/Airtable database
4. Weekly: Generate digest report

---

## Related Resources

- [review-mining-playbook.md](review-mining-playbook.md) - Detailed platform-specific extraction
- [feedback-tools-guide.md](feedback-tools-guide.md) - Tool setup tutorials
- [bigtech-feedback-patterns.md](bigtech-feedback-patterns.md) - How top companies do this
- [pain-point-report-template.md](../assets/feedback/pain-point-report-template.md) - Copy-paste template
