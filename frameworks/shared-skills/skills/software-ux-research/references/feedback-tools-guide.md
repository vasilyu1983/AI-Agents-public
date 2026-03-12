# Feedback Tools Guide

Practical setup guides for feedback collection and analysis tools. No theory — just how to get started.

---

## Tool Selection Matrix

| Tool | Type | Best For | Setup Time | Pricing |
|------|------|----------|------------|---------|
| **AppFollow** | Review aggregation | Mobile apps (B2C) | 15 min | Free → $79/mo |
| **Appbot** | Automated review analysis | Volume analysis | 20 min | $49/mo |
| **G2 Seller** | Competitive intel | B2B SaaS | 1-2 weeks | Contact sales |
| **Linear Customer Requests** | Feedback → issues | B2B product teams | 30 min | Included in Linear |
| **Productboard** | Voice of customer | Product roadmap | 1 hour | $20/user/mo |
| **Canny** | Feature requests | Public roadmap | 20 min | Free → $79/mo |
| **Hotjar** | In-app feedback | Quick surveys | 10 min | Free → $32/mo |
| **Dovetail** | Research repository | Qualitative synthesis | 30 min | $29/user/mo |

---

## Review Aggregation Tools

### AppFollow (B2C - Mobile Apps)

**Best for**: iOS/Android app review monitoring

**Setup Guide**:

```
1. Sign up at appfollow.io

2. Connect App Store Connect:
   - Go to App Store Connect → Users and Access → Integrations
   - Generate API Key (Admin role)
   - Copy: Issuer ID, Key ID, Private Key
   - Paste into AppFollow → Settings → Integrations

3. Connect Google Play:
   - Go to Play Console → Settings → API Access
   - Create service account
   - Download JSON key file
   - Upload to AppFollow → Settings → Integrations

4. Configure dashboard:
   - Add your apps + competitors
   - Set up Slack alerts: Settings → Notifications → Slack
   - Configure alert triggers: 1-2 star reviews, keywords

5. Set up weekly digest:
   - Settings → Reports → Email Digest
   - Choose: Weekly, recipients, metrics
```

**Key Features to Use**:
- **Sentiment tracking**: Auto-tags positive/negative/neutral
- **Keyword alerts**: Get notified for specific terms
- **Competitor monitoring**: Track competitor ratings
- **Reply management**: Respond from dashboard

**API Access** (for automation):
```bash
# Get reviews
curl -X GET "https://api.appfollow.io/reviews" \
  -H "X-AppFollow-API-Token: YOUR_TOKEN" \
  -d "app_id=123456&country=us&page=1"
```

---

### Appbot (B2C - Automated Analysis)

**Best for**: High-volume automated review analysis

**Setup Guide**:

```
1. Sign up at appbot.co

2. Connect stores:
   - Same process as AppFollow (App Store Connect / Play Console)

3. Configure automated analysis:
   - Topics: Let the tool identify or create custom topics
   - Sentiment: Review auto-classification accuracy
   - Alerts: Set up for negative sentiment spikes

4. Create dashboards:
   - Topic trends over time
   - Version comparison
   - Competitor benchmarking
```

**Key Features**:
- **Topic clustering**: Tool groups reviews by theme
- **Sentiment accuracy**: Higher precision than AppFollow
- **API exports**: Programmatic access to insights

---

## B2B Competitive Intelligence

### G2 Seller Solutions

**Best for**: SaaS competitive intelligence

**Setup Guide**:

```
1. Contact G2 sales for Seller account

2. Claim your G2 profile:
   - g2.com/products/claim
   - Verify company ownership

3. Access competitive features:
   - Dashboard → Competitive Intelligence
   - Set up competitor tracking
   - Configure quarterly reports

4. Export reviews:
   - Your reviews: Dashboard → Reviews → Export
   - Competitor reviews: Competitive Intel → Export (paid)
```

**Key Features**:
- **Grid reports**: Category rankings
- **Buyer Intent**: Who's researching you vs competitors
- **Review exports**: CSV for analysis
- **Comparison pages**: Head-to-head features

**Manual Extraction (Free)**:
```
1. g2.com → Search competitor
2. Reviews tab → Filter by rating
3. Copy "What do you dislike?" sections
4. Paste into your analysis tool for theme extraction (see Optional section below)
```

---

### TrustRadius

**Best for**: Deep enterprise feedback

**Access Methods**:

```
Free:
- trustradius.com → Search product → Read reviews
- Focus on Cons + Alternatives Considered sections

Vendor Portal (Free to claim):
- trustradius.com/vendors
- Claim profile, respond to reviews
- Access review analytics

API (Paid):
- Contact TrustRadius for enterprise API access
```

---

## Feedback → Product Integration

### Linear Customer Requests

**Best for**: B2B teams using Linear for issues

**Setup Guide**:

```
1. Enable Customer Requests:
   - Linear → Settings → Features → Enable "Customer Requests"

2. Connect support tools:
   - Settings → Integrations → Intercom/Zendesk/Front
   - Authorize connection
   - Map: Conversation → Linear issue

3. Configure customer attributes:
   - Settings → Customer Requests → Attributes
   - Add: Revenue, Company Size, Tier
   - (Syncs from CRM or manual entry)

4. Create feedback workflow:
   - When support gets feature request:
     - Create Customer Request
     - Link to existing issue or create new
     - Add customer attributes

5. Use for prioritization:
   - Issues view → Filter by customer count
   - Sort by: Total revenue of requesting customers
   - Filter by: Customer tier
```

**Key Features**:
- **Customer pages**: See all requests from one customer
- **Issue enrichment**: Customer count + attributes on issues
- **Prioritization**: Sort by revenue impact
- **Communication**: Notify customers when shipped

---

### Productboard

**Best for**: Enterprise voice of customer

**Setup Guide**:

```
1. Sign up at productboard.com

2. Set up Insights portal:
   - Insights → Settings → Integrations
   - Connect: Intercom, Zendesk, Salesforce, Slack

3. Configure feedback flow:
   - Insights → Rules
   - Auto-tag incoming feedback
   - Route to relevant product areas

4. Link feedback to features:
   - Features → Create feature
   - Link insights manually or via automation

5. Build prioritization scores:
   - Drivers → Create scoring formula
   - Example: (Customer Count × Revenue Weight) / Effort
```

**Browser Extension**:
```
1. Install Productboard Chrome extension
2. Highlight text on any page (email, doc, etc.)
3. Right-click → Save to Productboard
4. Auto-captured with source URL
```

---

### Canny

**Best for**: Public feature voting

**Setup Guide**:

```
1. Sign up at canny.io

2. Create boards:
   - Feature Requests (public)
   - Bug Reports (public or private)
   - Internal Ideas (private)

3. Embed widget:
   - Settings → Widget → Copy code
   - Add to your app's help menu or settings

4. Connect integrations:
   - Intercom: Auto-create posts from conversations
   - Slack: Notifications + posting
   - Jira/Linear: Sync status

5. Configure changelog:
   - When features ship, mark as "Complete"
   - Auto-notify voters
   - Public changelog page
```

**Key Features**:
- **Voting**: Users upvote features
- **Segmentation**: Filter by user segment (paid, trial, etc.)
- **Roadmap**: Public roadmap linked to requests
- **Changelog**: Automated "we shipped it" notifications

---

## In-App Feedback Collection

### Hotjar

**Best for**: Quick feedback widgets + heatmaps

**Setup Guide**:

```
1. Sign up at hotjar.com

2. Install tracking code:
   - Sites → Add New Site
   - Copy tracking code
   - Add to <head> of your app

3. Set up Feedback widget:
   - Feedback → Create Feedback
   - Choose: Emoji rating, text input, or NPS
   - Configure triggers: All pages, specific URLs, time delay

4. Create surveys:
   - Surveys → Create Survey
   - NPS: "How likely to recommend?"
   - Open-end: "What's frustrating you?"
   - Targeting: User segment, page, behavior

5. Set up session recordings (bonus):
   - Recordings → Enable
   - Watch frustrated users (rage clicks)
```

**Feedback Triggers**:
| Trigger | When to Use |
|---------|-------------|
| Exit intent | Capture leaving users |
| Time on page | Long dwells = confusion |
| Scroll depth | Page engagement |
| Click on element | After specific action |

---

### Userpilot

**Best for**: NPS + in-app surveys with targeting

**Setup Guide**:

```
1. Sign up at userpilot.com

2. Install snippet:
   - Settings → Installation → Copy code
   - Add to your app

3. Identify users:
   - userpilot.identify(userId, {
       name: "...",
       email: "...",
       plan: "...",
       signupDate: "..."
     });

4. Create NPS survey:
   - Experiences → New → NPS
   - Trigger: 14 days after signup
   - Frequency: Every 90 days

5. Add follow-up question:
   - After NPS score: "What's the main reason?"
   - Segment by score: Promoters vs Detractors

6. Build dashboards:
   - Insights → NPS Dashboard
   - Track: Score over time, by segment, by feature
```

---

## Optional: AI/Automation — Assisted Analysis

> Use only if you’re applying AI/automation tools to speed up tagging/synthesis. Skip for manual workflows.

### Dovetail

**Best for**: Qualitative research repository

**Setup Guide**:

```
1. Sign up at dovetail.com

2. Create project:
   - Projects → New Project
   - Name: "Q4 2024 Feedback Analysis"

3. Import data:
   - Data → Import
   - Sources: CSV, Intercom, Zendesk, video files

4. Tag and highlight:
   - Open transcript/review
   - Highlight text → Create tag
   - Build tag taxonomy: Pain Points, Features, Praise

5. Analyze patterns:
   - Insights → Charts
   - View: Tag frequency, co-occurrence, sentiment

6. Generate insights:
   - Insights → Create Insight
   - Link supporting evidence (highlights)
   - Share with team
```

**Tag Taxonomy Example**:
```
Pain Points
├── Bugs
│   ├── Crashes
│   └── Data loss
├── UX Friction
│   ├── Navigation
│   └── Onboarding
└── Performance
    ├── Speed
    └── Reliability

Features
├── Requested
└── Praised

Competitors
├── Compared to
└── Switched from
```

---

### Optional: AI/Automation - Theme Extraction

Use only after PII redaction and with an audit trail (no fabricated quotes).

Tooling: use your approved LLM tool (local or hosted); do not paste secrets/PII.

**Prompt: Bulk Classification**
```
Classify these reviews into themes. For each theme:
- Name
- Count
- Severity (Critical/High/Medium/Low)
- Sample quotes (2)

Reviews:
[paste reviews]

Output as markdown table.
```

**Prompt: Sentiment + Pain Point**
```
For each review, extract:
1. Sentiment (Positive/Negative/Neutral/Mixed)
2. Core pain point (one phrase)
3. Affected feature
4. Priority (Immediate/Soon/Eventually)

Reviews:
[paste reviews]
```

**Prompt: Competitor Comparison**
```
Compare reviews from two products:

Product A Reviews:
[paste]

Product B Reviews:
[paste]

Output:
1. Unique pain points for A
2. Unique pain points for B
3. Shared pain points
4. Switching triggers
```

---

## Integration Patterns

### Slack + Feedback Flow

**Pattern**: Alert team on negative feedback

```
Setup:
1. AppFollow/Hotjar → Slack integration
2. Channel: #product-feedback
3. Trigger: 1-2 star reviews, negative NPS

Workflow:
- Review appears in Slack
- Team member triages
- Create Linear issue if actionable
- Track in weekly digest
```

### CRM + Feedback Enrichment

**Pattern**: Link feedback to revenue

```
Setup:
1. Salesforce/HubSpot → Productboard sync
2. Customer attributes flow to feedback

Use:
- Filter feedback by: ARR, company size, industry
- Prioritize: High-revenue customer pain points
- Track: Churn risk signals
```

### Support → Product Loop

**Pattern**: Support tickets → roadmap

```
Setup:
1. Zendesk/Intercom → Linear Customer Requests
2. Tag: "feature-request", "ux-issue", "bug"

Workflow:
- Support tags conversation
- Creates Customer Request in Linear
- PM reviews weekly
- Links to existing issues or creates new
- Customer notified on ship
```

---

## Related Resources

- [pain-point-extraction.md](pain-point-extraction.md) - What to do with feedback
- [review-mining-playbook.md](review-mining-playbook.md) - Platform-specific extraction
- [bigtech-feedback-patterns.md](bigtech-feedback-patterns.md) - Enterprise patterns
