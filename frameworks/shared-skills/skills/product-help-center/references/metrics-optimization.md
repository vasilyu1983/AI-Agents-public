# Metrics & Optimization

KPI tracking, analytics setup, and optimization strategies for help centers.

## Contents

- Core Metrics Framework
- ROI Calculation
- Analytics Setup
- Search Analytics
- Content Performance
- A/B Testing
- Feedback Analysis
- Optimization Playbook
- Benchmarking
- Alerting & Monitoring

## Core Metrics Framework

### Primary KPIs

| Metric | Definition | Target | Formula |
|--------|------------|--------|---------|
| **Self-Service Rate** | % issues resolved without agent | 60-80% | (KB Resolutions / Total Issues) x 100 |
| **Ticket Deflection** | Tickets avoided via KB | 30-50% | (Article Views x Deflection Rate) |
| **Search Success Rate** | % searches -> helpful result | >70% | (Successful Searches / Total Searches) x 100 |
| **CSAT (KB)** | Article helpfulness rating | >80% positive | (Positive Votes / Total Votes) x 100 |
| **Zero-Result Rate** | Searches with no results | <5% | (Zero-Result Searches / Total Searches) x 100 |

### Secondary KPIs

| Metric | Definition | Target |
|--------|------------|--------|
| **Avg. Time on Page** | Reading engagement | 2-5 min |
| **Bounce Rate** | Single-page exits | <40% |
| **Article Views** | Total/unique views | Trending up |
| **Search-to-Ticket** | Searches before ticket | 1-3 searches |
| **Contact Rate** | % who contact support | <20% |

## ROI Calculation

### Cost-Benefit Analysis

```
SELF-SERVICE ROI MODEL

Costs:
- Platform subscription: $XXX/month
- Content creation: $XXX/month
- Maintenance: $XXX/month
Total monthly cost: $XXXX

Savings:
- Average cost per ticket: $13
- Tickets deflected: X,XXX/month
- Deflection savings: $XX,XXX/month

Net ROI:
Monthly savings - Monthly cost = Net benefit
(Net benefit / Cost) x 100 = ROI %

EXAMPLE

Platform: $500/month
Content: $1,000/month
Maintenance: $500/month
Total cost: $2,000/month

Deflected tickets: 2,000/month
Cost per ticket: $13
Deflection savings: $26,000/month

Net benefit: $24,000/month
ROI: 1,100%
```

### Cost Per Resolution

```
CHANNEL COST COMPARISON

| Channel | Avg. Cost | Resolution Time |
|---------|-----------|-----------------|
| Phone | $15-25 | 8-12 min |
| Email | $10-15 | 24-48 hours |
| Live Chat | $8-12 | 5-10 min |
| AI Chatbot | $0.50-2 | 1-3 min |
| Self-Service | $0.10-0.50 | User-controlled |

TARGET: Maximize self-service, minimize phone
```

## Analytics Setup

### Google Analytics 4 Configuration

```javascript
// GA4 Event Tracking for Help Center

// Article view
gtag('event', 'article_view', {
  article_id: '12345',
  article_title: 'How to Reset Password',
  category: 'Account',
  content_type: 'how-to'
});

// Search performed
gtag('event', 'search', {
  search_term: 'password reset',
  results_count: 5
});

// Article feedback
gtag('event', 'article_feedback', {
  article_id: '12345',
  feedback_type: 'helpful', // or 'not_helpful'
  feedback_text: 'Optional comment'
});

// Contact support clicked
gtag('event', 'contact_support', {
  source_article: '12345',
  contact_method: 'chat'
});
```

### Key Events to Track

```
ESSENTIAL EVENTS

Page/Article level:
- article_view (with metadata)
- scroll_depth (25%, 50%, 75%, 100%)
- time_on_page
- related_article_click
- external_link_click

Search:
- search_performed
- search_result_click
- zero_results
- search_refinement

Feedback:
- helpful_yes
- helpful_no
- feedback_submitted
- escalation_to_support

AI/Chatbot:
- chatbot_opened
- chatbot_message_sent
- chatbot_resolved
- chatbot_escalated
```

### Dashboard Template

```
HELP CENTER DASHBOARD

Overview Section:
Self-Service Rate: 72%
Deflection: 65%

Search Performance:
Searches today: 1,234
Success rate: 78%
Zero results: 4.2%
Top searches: password, pricing, api

Content Health:
Total articles: 156
Updated <30 days: 45 (29%)
Low-rated (<3/5): 12
High-traffic, low-rated: 5 (priority)

Trend Chart:
[Line chart: tickets, KB views, search success rate]
```

## Search Analytics

### Search Performance Metrics

```
SEARCH METRICS

Volume:
- Total searches/day
- Unique searchers
- Searches per session

Quality:
- Click-through rate (CTR)
- Position of clicked result
- Refinement rate (search again)

Gaps:
- Zero-result queries
- Low-CTR queries
- High-exit searches

ZERO-RESULT ANALYSIS

Weekly review process:
1. Export zero-result queries
2. Group by topic/intent
3. Prioritize by volume
4. Actions:
   - Create new article
   - Add synonyms
   - Update titles
   - Add redirects
```

### Search Optimization Actions

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| High volume, zero results | Missing content | Create article |
| High volume, low CTR | Poor title/description | Rewrite metadata |
| Click -> immediate exit | Content mismatch | Update content |
| Multiple searches same topic | Hard to find | Add synonyms |
| Search -> ticket | Content insufficient | Expand article |

## Content Performance

### Article Scoring Model

```
ARTICLE HEALTH SCORE (0-100)

Components:
- Helpfulness rating: 30 points
- Traffic volume: 20 points
- Engagement (time on page): 15 points
- Freshness: 15 points
- Search performance: 10 points
- Link health: 10 points

SCORING EXAMPLE

Article: "How to Reset Password"

Helpfulness: 85% positive -> 25/30 points
Traffic: Top 10% -> 20/20 points
Engagement: 3.5 min avg -> 12/15 points
Freshness: Updated 2 months ago -> 12/15 points
Search: #2 result for "password" -> 8/10 points
Links: All working -> 10/10 points

Total Score: 87/100 (Healthy)
```

### Content Audit Framework

```
QUARTERLY AUDIT PROCESS

1. Export all articles with metrics
   - Views (30/90/365 days)
   - Helpfulness rating
   - Last updated date
   - Ticket escalations

2. Categorize by action needed

   OK Healthy (score >70):
   - No action needed
   - Review in 6 months

   Medium Needs attention (50-70):
   - Update content
   - Improve visuals
   - Check accuracy

   Critical Critical (<50):
   - Major rewrite
   - Consider archive
   - Urgent if high-traffic

3. Prioritize by impact
   High traffic + low score = Priority 1
   Low traffic + low score = Consider archive

4. Track improvements
   Before/after metrics per article
```

### Content Gap Analysis

```
IDENTIFYING GAPS

Data sources:
- Zero-result searches
- High-volume support tickets
- User feedback comments
- Sales/success team input
- Product release notes

PROCESS

1. Collect gap signals (weekly)
2. Categorize by topic
3. Score by impact:
   - Ticket volume reduction potential
   - User demand (search volume)
   - Strategic importance

4. Create backlog
5. Prioritize creation

GAP TEMPLATE

Topic: [Gap topic]
Evidence: [Data showing need]
Impact: [High/Medium/Low]
Effort: [Hours to create]
Priority: [P1/P2/P3]
Assigned: [Author]
Due: [Date]
```

## A/B Testing

### What to Test

```
TESTABLE ELEMENTS

Titles:
- Question vs. statement
- Verb-first vs. noun-first
- Short vs. descriptive

Content:
- Steps count (5 vs. 10)
- Video vs. text
- Screenshots vs. GIFs

Layout:
- TOC position
- Related articles placement
- CTA button position

Search:
- Result ordering
- Snippet length
- Filter options
```

### A/B Test Framework

```
TEST STRUCTURE

1. Hypothesis
   "Changing [element] from [A] to [B]
   will improve [metric] by [X]%"

2. Success metric
   Primary: [e.g., CTR, helpfulness]
   Secondary: [e.g., time on page]

3. Sample size
   Use calculator for statistical significance
   Minimum: 1,000 views per variant

4. Duration
   Minimum: 2 weeks
   Account for weekly patterns

5. Analysis
   - Statistical significance (p < 0.05)
   - Practical significance (>5% lift)
   - Segment analysis

EXAMPLE TEST

Hypothesis: "How to" prefix increases CTR
Control: "Reset Your Password"
Variant: "How to Reset Your Password"
Metric: Click-through from search
Duration: 2 weeks
Result: +12% CTR (p=0.02) -> Implement
```

## Feedback Analysis

### Feedback Collection Methods

```
FEEDBACK TYPES

Binary:
"Was this helpful?" [Yes] [No]
- Simple, high response rate
- Limited insight

Rating scale:
"Rate this article" 4/5
- More nuanced
- Moderate response rate

Open text:
"How can we improve this?"
- Rich insight
- Low response rate

Inline feedback:
Highlight -> "Is this unclear?"
- Contextual
- High-quality signal

BEST PRACTICE

Combine:
1. Binary (always show)
2. Follow-up question (on "No")
3. Optional text (for details)
```

### Feedback Processing

```
FEEDBACK WORKFLOW

Daily:
- Review new feedback
- Flag urgent issues
- Categorize comments

Weekly:
- Analyze patterns
- Update priority articles
- Report to team

Monthly:
- Trend analysis
- Process improvements
- Content planning input

CATEGORIZATION

- Accuracy issue (content wrong)
- Completeness (missing info)
- Clarity (confusing)
- Outdated (needs update)
- Praise (positive)
- Off-topic (ignore)
```

## Optimization Playbook

### Quick Wins (<1 hour each)

```
IMMEDIATE IMPACT ACTIONS

1. Fix broken links
   - Run link checker
   - Update or remove

2. Add missing screenshots
   - High-traffic how-to articles
   - Error message articles

3. Update dates
   - "Last updated" timestamps
   - Version numbers

4. Add search synonyms
   - Top zero-result queries
   - Common misspellings

5. Improve titles
   - Add action verbs
   - Match search queries
```

### Medium Effort (1 day each)

```
SIGNIFICANT IMPROVEMENTS

1. Rewrite low-rated articles
   - Address feedback themes
   - Add visual aids
   - Simplify language

2. Create missing content
   - Top 5 zero-result queries
   - Frequent ticket topics

3. Consolidate duplicates
   - Merge similar articles
   - Set up redirects

4. Improve navigation
   - Update category structure
   - Add cross-links
   - Improve breadcrumbs
```

### Strategic Projects (1 week+)

```
TRANSFORMATIONAL CHANGES

1. AI integration
   - Implement chatbot
   - Set up RAG pipeline
   - Configure escalation

2. Content redesign
   - New templates
   - Consistent formatting
   - Visual refresh

3. Search overhaul
   - Semantic search
   - Personalization
   - Federated search

4. Analytics upgrade
   - Custom dashboards
   - Automated alerts
   - Predictive analytics
```

## Benchmarking

### Industry Benchmarks

```
BENCHMARK RANGES

Self-Service Rate:
- Low: <40%
- Average: 50-65%
- Best-in-class: >75%

Ticket Deflection:
- Low: <20%
- Average: 30-45%
- Best-in-class: >55%

Search Success:
- Low: <60%
- Average: 70-80%
- Best-in-class: >85%

CSAT (KB):
- Low: <70%
- Average: 75-82%
- Best-in-class: >88%

NOTE: Benchmarks vary by industry
- B2B SaaS: Higher self-service expected
- E-commerce: Lower (simpler queries)
- Enterprise: Variable by product complexity
```

### Competitive Analysis

```
COMPETITIVE INTEL CHECKLIST

Analyze competitor help centers:

Structure:
- Category organization
- Article types
- Navigation patterns
- Search prominence

Content:
- Writing style
- Visual approach
- Depth of content
- Update frequency

Features:
- AI chatbot presence
- Community forums
- Video content
- Interactive guides

UX:
- Mobile experience
- Load time
- Accessibility
- Personalization

Document findings:
- What they do better
- What we do better
- Opportunities to differentiate
```

## Alerting & Monitoring

### Alert Configuration

```
AUTOMATED ALERTS

Critical (immediate):
- Zero-result rate >10%
- Helpfulness <60%
- Site down/errors

Warning (daily digest):
- Traffic drop >20% WoW
- New low-rated articles
- Stale content (>6 months)

Info (weekly summary):
- Top performing content
- Trending searches
- Feedback themes

ALERT TEMPLATE

Subject: [Severity] Help Center Alert: [Issue]

What: [Description of issue]
Impact: [Metric change]
Affected: [Articles/pages]
Action: [Recommended fix]
Link: [Dashboard/article link]
```

### Health Check Automation

```
WEEKLY AUTOMATED CHECKS

- Broken link scan
- Image loading verification
- Search functionality test
- Chatbot response test
- Mobile rendering check
- Load time measurement
- SSL certificate validity
- Analytics tracking verification

MONTHLY AUTOMATED REPORTS

- Content freshness report
- Search performance summary
- Feedback trend analysis
- Traffic comparison (MoM, YoY)
- Top/bottom performers
- Gap analysis update
```
