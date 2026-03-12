# Review Mining Playbook

Practical guide to mining user reviews from B2B and B2C platforms. Extract pain points, competitive intelligence, and feature opportunities.

---

## Quick Reference: Which Platform for What

| Platform | Type | Best For | Avg Review Length | Data Quality |
|----------|------|----------|-------------------|--------------|
| App Store | B2C | iOS app feedback | 50-100 words | High (verified purchase) |
| Play Store | B2C | Android app feedback | 50-100 words | High (verified) |
| G2 | B2B | SaaS competitive intel | 130 words | High (LinkedIn verified) |
| TrustRadius | B2B | Deep enterprise feedback | 408 words | Very high (detailed) |
| Capterra | B2B | Volume signals, discovery | 100 words | Medium (incentivized) |
| Trustpilot | B2C | Service/e-commerce | 100 words | Medium |

---

## B2C: App Store Mining

### Access Methods

**Manual (Free)**:
1. App Store Connect → My Apps → [App] → App Analytics → Reviews
2. Or: Apple App Store → Search app → Ratings & Reviews → See All

**AppFollow (Automated)**:
- Connect app via App Store Connect API
- Auto-sync reviews daily
- Sentiment tagging included

**App Store Connect API**:
```bash
# Get reviews via App Store Connect API
# Requires: API Key from App Store Connect

curl -X GET "https://api.appstoreconnect.apple.com/v1/apps/{app_id}/customerReviews" \
  -H "Authorization: Bearer {token}"
```

### Star Rating Decoder

| Rating | User State | Signal | Action |
|--------|------------|--------|--------|
| 1-star | Rage, frustration | Critical bugs, data loss, crashes | Immediate fix + respond |
| 2-star | Disappointed | Usability issues, unmet expectations | UX audit priority |
| 3-star | Ambivalent | "Good but..." — feature gaps | Roadmap consideration |
| 4-star | Satisfied with caveats | Minor friction, polish issues | Backlog improvements |
| 5-star | Delighted | Delight signals — what to protect | Document what works |

### Extraction Workflow

**Step 1: Filter Reviews**

```
Filters to apply:
- Date range: Last 30/90 days
- Rating: Start with 1-2 stars (problems first)
- Version: Filter by recent releases
- Country: Focus on primary market
```

**Step 2: Scan for Keywords**

| Category | Keywords to Search |
|----------|-------------------|
| Bugs | crash, freeze, bug, error, broken, doesn't work |
| Performance | slow, loading, lag, freeze, battery drain |
| UX | confusing, can't find, complicated, hard to use |
| Features | wish, need, should have, would be nice, missing |
| Onboarding | setup, getting started, don't understand, how do I |
| Design | ugly, outdated, cluttered, redesign |

**Step 3: Extract Pain Points**

For each review:
1. Identify the core complaint
2. Note the affected feature/flow
3. Rate severity (Critical/High/Medium/Low)
4. Copy the exact quote
5. Check if version-specific

**Step 4: Aggregate Themes**

```markdown
## Theme Summary: [App Name] - [Date Range]

### Top 5 Pain Points (1-2 star reviews)
1. [Theme] - N mentions - "[sample quote]"
2. [Theme] - N mentions - "[sample quote]"
...

### Most Requested Features (3-4 star reviews)
1. [Feature] - N mentions
2. [Feature] - N mentions
...

### Delight Signals (5 star reviews)
1. [What users love] - N mentions
2. [What users love] - N mentions
...
```

### Competitor Review Mining (App Store)

**Process**:
1. Search competitor app in App Store
2. Go to Ratings & Reviews → See All
3. Filter by 1-2 stars
4. Extract their pain points
5. Map to your strengths

**Opportunity Template**:

| Competitor Pain Point | Our Status | Opportunity |
|-----------------------|------------|-------------|
| "App crashes on export" | We're stable | Highlight in marketing |
| "No dark mode" | We have it | Feature comparison |
| "Confusing pricing" | Same issue | Fix before they do |

---

## B2C: Play Store Mining

### Access Methods

**Manual (Free)**:
1. Google Play Console → Quality → Ratings & Reviews
2. Or: Play Store → App → Ratings and reviews

**Play Console Export**:
```
Play Console → Quality → Reviews → Download (CSV)
```

**Play Developer API**:
```bash
# Reviews API
GET https://androidpublisher.googleapis.com/v3/applications/{packageName}/reviews

# Requires OAuth 2.0 token with Play Developer API access
```

### Android-Specific Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| Device-specific complaints | Fragmentation issue | Test on mentioned devices |
| Android version complaints | Compatibility | Check minSdkVersion |
| "Works on iOS" | Platform parity | Prioritize feature sync |
| Battery/performance | Resource usage | Optimize background processes |

### Cross-Platform Analysis

Compare App Store vs Play Store reviews:

```markdown
## Cross-Platform Pain Point Comparison

| Pain Point | iOS Mentions | Android Mentions | Platform-Specific? |
|------------|--------------|------------------|-------------------|
| Slow loading | 15 | 42 | Android (investigate) |
| Crashes | 8 | 12 | Both |
| Missing feature X | 20 | 5 | iOS users want more |
```

---

## B2B: G2 Mining

### Why G2 Matters

- 60M+ monthly visitors
- LinkedIn-verified reviewers
- Grid rankings influence B2B buyers
- Quarterly reports drive market perception

### Access Methods

**Free (Manual)**:
1. Go to G2.com
2. Search for competitor or category
3. Click "Reviews" tab
4. Use filters: Rating, Date, Company Size

**G2 Seller (Paid)**:
- Competitive intelligence dashboard
- Export competitor reviews
- Buyer intent signals
- Pricing: Contact sales

### G2 Review Structure

Every G2 review has:
- **What do you like best?** → Strengths to match
- **What do you dislike?** → Pain points to solve
- **Recommendations to others** → Buying criteria
- **Star ratings by category** → Feature comparison

### Extraction Process

**Step 1: Navigate to Competitor**
```
G2.com → Search "[Competitor]" → Reviews tab
```

**Step 2: Filter Reviews**
```
Filters:
- Sort: Most Recent (or Lowest Rating first)
- Company Size: Match your target segment
- Industry: Match your target vertical
- Rating: 1-3 stars for problems, 4-5 for what works
```

**Step 3: Focus on "What do you dislike?"**

This is the gold mine. Extract:
- Feature gaps
- UX complaints
- Support issues
- Pricing concerns
- Integration problems

**Step 4: Categorize Themes**

| Theme | Frequency | Representative Quote | Our Position |
|-------|-----------|---------------------|--------------|
| Steep learning curve | 12 | "Took weeks to onboard team" | Advantage: easier onboarding |
| Expensive for SMB | 8 | "Pricing doesn't scale down" | Parity: pricing concern |
| Limited integrations | 6 | "No Zapier integration" | Advantage: we have Zapier |

### Win/Loss from G2 Reviews

Look for reviews that mention switching:

```
Search terms in reviews:
- "switched from"
- "replaced"
- "moved to"
- "considering"
- "compared to"
```

**Template**:

| Reviewer Switched From | Reason | Our Opportunity |
|------------------------|--------|-----------------|
| Competitor A | "Too complex" | Position simplicity |
| Competitor B | "Poor support" | Highlight support |
| Competitor C | "Missing feature X" | Build feature X |

---

## B2B: TrustRadius Mining

### Why TrustRadius

- 408-word average reviews (3x G2)
- 70% include reviewer name + company
- Detailed pros/cons/alternatives
- Less incentive bias than Capterra

### TrustRadius Review Structure

- **Pros** - What works
- **Cons** - What doesn't
- **Overall** - Summary
- **Alternatives Considered** - Competitive landscape
- **Switching From** - Why they left competitor
- **ROI/Business Impact** - Value evidence

### Extraction Focus: Cons + Alternatives

**Step 1: Find Competitor**
```
TrustRadius.com → Search "[Competitor]" → Read Reviews
```

**Step 2: Extract Cons**

TrustRadius Cons are detailed. Look for:
- Specific feature complaints
- Workflow friction
- Admin/setup pain
- Scaling issues
- Support problems

**Step 3: Note Alternatives Considered**

This tells you:
- Who you're really competing with
- What factors drive decisions
- Feature/price thresholds

**Template**:

| Reviewer | Company Size | Top Con | Alternatives Considered | Decision Factor |
|----------|--------------|---------|------------------------|-----------------|
| [Name] | Enterprise | "API limitations" | [List] | "Integration needs" |
| [Name] | SMB | "Price jump at scale" | [List] | "Budget" |

---

## B2B: Capterra Mining

### Capterra Characteristics

- Higher volume, shorter reviews
- More incentivized reviews (lower weight)
- Good for trend signals
- PPC model = featured placements

### When to Use Capterra

- Volume analysis (what's mentioned most?)
- Category discovery (who competes?)
- Quick competitive scan

### Extraction Process

```
Capterra.com → Search category or competitor → Reviews
Sort by: Most Recent or Lowest Rating
```

Focus on:
- Recurring themes across many reviews
- Category-wide pain points (not just one competitor)
- Feature baseline expectations

---

## Optional: AI/Automation — LLM Prompts

> Use only if you’re applying AI/automation to speed up classification. Redact PII first and keep traceability to raw reviews.

### Bulk Review Analysis

```
Analyze these G2/App Store reviews and provide:

1. Top 5 pain points with frequency count
2. Top 3 feature requests
3. Sentiment distribution (positive/negative/neutral)
4. Competitive mentions (products compared to)
5. Decision factors mentioned

Format as markdown tables.

Reviews:
[paste reviews]
```

### Competitive Gap Analysis

```
Compare these two sets of reviews and identify:

1. Pain points unique to Competitor A
2. Pain points unique to Competitor B
3. Shared pain points
4. Features praised in A but missing in B
5. Switching triggers (why users leave each)

Competitor A Reviews:
[paste]

Competitor B Reviews:
[paste]
```

### Theme Clustering

```
Cluster these review excerpts into themes.

For each theme:
- Theme name
- Count of mentions
- Severity (Critical/High/Medium/Low)
- Representative quotes (2-3)

Excerpts:
[paste "dislike" sections]
```

---

## Response Strategy

### When to Respond

| Review Type | Respond? | Template |
|-------------|----------|----------|
| 1-star with specific issue | Yes, within 24h | Apologize + fix path |
| 1-star venting | Maybe | Brief acknowledgment |
| 2-3 star with suggestion | Yes | Thank + roadmap hint |
| 4-5 star detailed | Yes | Thank + encourage share |
| 4-5 star brief | Optional | Quick thank you |

### Response Template (Negative)

```
Hi [Name],

Thank you for your feedback. We're sorry to hear about [specific issue].

[If bug/crash]: Our team is actively investigating this. Could you email support@[company].com with your device details so we can prioritize your case?

[If feature request]: This is on our radar! We're planning to [vague timeline hint] and your input helps us prioritize.

[If UX complaint]: We appreciate this feedback and are working on improvements to [area].

We'd love to make this right.

— [Name], [Title]
```

---

## Optional: AI/Automation — Automation Setup

### AppFollow (B2C)

**Setup Time**: 15 minutes

1. Sign up at appfollow.io
2. Connect App Store Connect / Google Play Console
3. Configure:
   - Review sync frequency (daily)
   - Sentiment tagging (auto)
   - Slack alerts (negative reviews)
4. Set up weekly digest email

### G2 Seller (B2B)

**Setup Time**: Contact sales

Features:
- Competitive review monitoring
- Buyer intent alerts
- Quarterly comparison reports

### Custom Monitoring (Zapier + LLM API)

**For**: Custom review sources, forums, social

1. Zapier: Monitor source (RSS, webhook, email)
2. Trigger: New review detected
3. Action: Send to LLM API for classification
4. Store: Airtable/Notion database
5. Alert: Slack for critical issues

---

## Output Templates

### Weekly Review Digest

See [pain-point-extraction.md](pain-point-extraction.md#weekly-digest-format)

### Competitive Review Matrix

See [competitor-review-matrix-template.md](../assets/feedback/competitor-review-matrix-template.md)

### Pain Point Report

See [pain-point-report-template.md](../assets/feedback/pain-point-report-template.md)

---

## Related Resources

- [pain-point-extraction.md](pain-point-extraction.md) - Full extraction methodology
- [feedback-tools-guide.md](feedback-tools-guide.md) - Tool setup tutorials
- [bigtech-feedback-patterns.md](bigtech-feedback-patterns.md) - Enterprise patterns
- [competitive-ux-analysis.md](competitive-ux-analysis.md) - Beyond reviews
