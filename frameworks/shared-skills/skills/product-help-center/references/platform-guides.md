# Platform Guides

Setup and configuration guides for help center platforms.

## Contents

- Platform Selection Matrix
- Zendesk Guide Setup
- Intercom Setup
- Freshdesk Setup
- GitBook Setup
- Notion as Help Center
- Enterprise AI Platforms (2026)
- Migration Guide

## Platform Selection Matrix

### By Company Stage

| Stage | Revenue | Team Size | Recommended | Why |
|-------|---------|-----------|-------------|-----|
| Pre-seed/Seed | <$1M ARR | 1-10 | Notion + Intercom | Low cost, fast setup |
| Series A | $1-5M ARR | 10-50 | Intercom or Freshdesk | Balance features/cost |
| Series B+ | $5-20M ARR | 50-200 | Zendesk or Intercom | Scalability, integrations |
| Enterprise | >$20M ARR | 200+ | Zendesk | Compliance, customization |

### By Use Case

| Use Case | Best Platform | Alternatives |
|----------|---------------|--------------|
| Developer docs | GitBook, ReadMe | Docusaurus, Mintlify |
| SaaS help center | Intercom, Zendesk | Freshdesk, HelpScout |
| E-commerce support | Zendesk, Gorgias | Freshdesk, Gladly |
| Internal knowledge | Notion, Guru | Confluence, Slite |
| API documentation | ReadMe, Stoplight | Swagger, Redocly |

### Feature Comparison

| Feature | Zendesk | Intercom | Freshdesk | GitBook |
|---------|---------|----------|-----------|---------|
| Help Center | Yes | Yes | Yes | Yes |
| Ticketing | Yes | Yes | Yes | No |
| Live Chat | Yes | Yes | Yes | No |
| AI Chatbot | Add-on | Fin ($0.99/res) | Freddy (built-in) | No |
| Email Support | Yes | Yes | Yes | No |
| Docs-as-Code | No | No | No | Yes |
| API | Full | Full | Full | Full |
| SSO | Enterprise | Yes | Pro+ | Business |
| HIPAA | Enterprise | Enterprise | Enterprise | No |
| Starting Price | $55/agent | $29/seat | $15/agent | Free |

## Zendesk Guide Setup

### Initial Configuration

```
SETUP CHECKLIST

1. Create Help Center
   Admin > Guide > Activate Guide

2. Configure settings
   - Default language
   - Search settings
   - SEO settings (sitemap, robots.txt)
   - Google Analytics

3. Brand customization
   - Logo, colors, favicon
   - Header/footer
   - Custom CSS
   - Theme selection

4. Structure
   - Create categories
   - Create sections
   - Set permissions (public/internal)

5. Content migration
   - Import from CSV
   - API migration
   - Manual creation
```

### Theme Customization

```css
/* Zendesk Copenhagen Theme Customization */

/* Brand colors */
:root {
  --primary-color: #1a73e8;
  --secondary-color: #5f6368;
  --background-color: #ffffff;
  --text-color: #202124;
}

/* Search bar prominence */
.search-container {
  background: var(--primary-color);
  padding: 60px 20px;
}

/* Article styling */
.article-body {
  max-width: 800px;
  line-height: 1.6;
  font-size: 16px;
}

/* Category cards */
.category-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}
```

### Zendesk AI Configuration

```
ANSWER BOT SETUP

1. Enable Answer Bot
   Admin > Channels > Bots > Answer Bot

2. Training sources
   - Help Center articles (primary)
   - Canned responses
   - Previous tickets

3. Trigger configuration
   - Web Widget
   - Email auto-reply
   - Ticket creation flow

4. Confidence thresholds
   - High (show answer): >0.8
   - Medium (show with disclaimer): 0.6-0.8
   - Low (don't show): <0.6

5. Escalation rules
   - No match -> Create ticket
   - Low confidence -> Offer human
   - Negative feedback -> Escalate
```

### Zendesk Best Practices

```
CONTENT ORGANIZATION

- Use labels for cross-cutting topics
- Enable article voting
- Set up content cues (auto-suggestions)
- Use internal articles for sensitive docs
- Archive outdated content (don't delete)

SEARCH OPTIMIZATION

- Add search synonyms
- Configure promoted results
- Review zero-result searches weekly
- Use article labels for filtering

PERFORMANCE

- Enable CDN for images
- Compress images before upload
- Use lazy loading
- Monitor page load times
```

## Intercom Setup

### Initial Configuration

```
SETUP CHECKLIST

1. Create Help Center
   Settings > Help Center > Enable

2. Configure collection structure
   - Create collections (categories)
   - Set collection icons
   - Configure order

3. Customize appearance
   - Brand colors
   - Custom header
   - Search bar styling
   - Article formatting

4. Content settings
   - Default language
   - Multi-language setup
   - Public vs. private articles

5. Integration
   - Embed in Messenger
   - Enable article suggestions
   - Connect to Fin AI
```

### Fin AI Configuration

```
FIN SETUP

1. Enable Fin
   Settings > Fin > Enable

2. Content sources
   - Help Center articles (automatic)
   - Public website URLs
   - Custom snippets

3. Configure behavior
   - Persona/tone
   - Business hours
   - Languages
   - Handoff triggers

4. Test in sandbox
   - Test common queries
   - Review answer quality
   - Adjust prompts

5. Gradual rollout
   - Start with 10% traffic
   - Monitor metrics
   - Increase to 100%

PRICING

$0.99 per Fin resolution
Resolution = User marks as helpful OR doesn't escalate

COST OPTIMIZATION

- Improve content quality -> Higher resolution rate
- Clear escalation paths -> Fewer false resolutions
- Target: 60-70% Fin resolution rate
```

### Intercom Messenger Configuration

```
MESSENGER SETTINGS

Home screen:
- Recent articles
- Quick links
- Start conversation

Conversation settings:
- Auto-assign rules
- Business hours
- Away message

Article suggestions:
- Enable in Messenger
- Show during typing
- Smart suggestions

Proactive messages:
- Trigger on page view
- Time-based targeting
- User segment targeting
```

### Intercom Best Practices

```
CONTENT STRATEGY

- Keep articles concise (<500 words)
- Use rich media (images, GIFs, video)
- Cross-link related articles
- Regular freshness reviews

MESSENGER OPTIMIZATION

- Pin important articles
- Use article cards in conversations
- Enable suggested replies
- Configure macros for agents

FIN OPTIMIZATION

- Clear, keyword-rich titles
- FAQ structure (question as heading)
- Avoid duplicate content
- Update based on Fin feedback
```

## Freshdesk Setup

### Initial Configuration

```
SETUP CHECKLIST

1. Create Knowledge Base
   Admin > Support Channels > Knowledge Base

2. Structure setup
   - Create categories
   - Create folders
   - Set visibility (all/customers/agents)

3. Customize portal
   - Brand colors
   - Logo and favicon
   - Custom domain
   - Header/footer

4. SEO settings
   - Meta descriptions
   - Sitemap generation
   - Social sharing

5. Freddy AI
   - Enable Answer Bot
   - Train on KB content
   - Configure triggers
```

### Freddy AI Configuration

```
FREDDY SETUP

1. Enable Freddy
   Admin > Freddy > Answer Bot

2. Training
   - Solution articles (primary)
   - Canned responses
   - Historical tickets

3. Channels
   - Chat widget
   - Email auto-reply
   - Ticket creation

4. Behavior
   - Confidence threshold
   - Fallback message
   - Agent handoff

5. Monitoring
   - Resolution rate
   - Accuracy score
   - User feedback
```

### Freshdesk Portal Customization

```html
<!-- Freshdesk Portal Customization -->

<!-- Custom CSS location: Admin > General > Portal Customization -->

/* Hero section */
.solution-home-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 20px;
}

/* Category cards */
.solution-category-card {
  border-radius: 12px;
  transition: box-shadow 0.3s;
}

.solution-category-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

/* Article styling */
.article-body {
  font-size: 16px;
  line-height: 1.7;
  max-width: 720px;
}
```

### Freshdesk Best Practices

```
CONTENT ORGANIZATION

- Use tags for cross-category topics
- Enable article feedback
- Set up approval workflows
- Use draft mode for WIP content

AUTOMATION

- Auto-suggest articles in tickets
- Email notifications for feedback
- Scheduled content reviews
- Bulk operations for updates

FREDDY OPTIMIZATION

- Question-format titles
- Clear, concise answers
- Structured content (lists, tables)
- Regular content updates
```

## GitBook Setup

### Initial Configuration

```
SETUP CHECKLIST

1. Create space
   - Documentation type
   - Public or private
   - Custom domain

2. Structure
   - Groups (top-level)
   - Pages (articles)
   - Subpages (nested)

3. Customize
   - Brand colors
   - Custom fonts
   - Logo
   - Favicon

4. Integrations
   - Git sync (GitHub/GitLab)
   - Analytics (GA, Plausible)
   - Search (Algolia)

5. Publishing
   - Custom domain
   - SSL certificate
   - SEO settings
```

### Git Sync Configuration

```yaml
# .gitbook.yaml (repo root)

root: ./docs/

structure:
  readme: README.md
  summary: SUMMARY.md

redirects:
  old-page: new-page
  moved-article: articles/new-location
```

### GitBook Customization

```json
// space.json (GitBook configuration)

{
  "title": "Product Documentation",
  "description": "Help center for [Product]",
  "theme": {
    "extends": "@gitbook/theme-default",
    "colors": {
      "primary": "#1a73e8"
    },
    "font": "Inter"
  },
  "features": {
    "search": true,
    "feedback": true,
    "pdf": false
  }
}
```

### GitBook Best Practices

```
DOCS-AS-CODE WORKFLOW

1. Content in Markdown files
2. Version control (Git)
3. PR-based reviews
4. Automated deployment

STRUCTURE

- SUMMARY.md defines navigation
- Group related pages
- Use page variants for versions
- Inline code blocks for technical content

COLLABORATION

- Git sync for developers
- Web editor for non-technical
- PR reviews for quality
- Scheduled syncs
```

## Notion as Help Center

### Setup for External Help Center

```
SETUP STEPS

1. Create workspace
   - Dedicated workspace or section
   - Clean, minimal structure

2. Build template
   - FAQ database
   - How-to template
   - Category pages

3. Make public
   - Share > Publish to web
   - Custom domain (paid)
   - Search engine indexing

4. Customize
   - Cover images
   - Icons
   - Callout blocks
   - Toggle blocks (FAQ)
```

### Notion Help Center Template

```
STRUCTURE

Help Center (Page)
|-- Getting Started
|   |-- Quick Start Guide
|   |-- Account Setup
|   \\-- First Steps
|-- Features
|   |-- Feature A Guide
|   |-- Feature B Guide
|   \\-- Feature C Guide
|-- Billing
|   |-- Pricing FAQ
|   |-- Payment Methods
|   \\-- Refund Policy
|-- FAQ
|   \\-- FAQ Database (toggle blocks)
\\-- Contact Us
    \\-- Support form embed
```

### Notion Limitations

```
LIMITATIONS FOR HELP CENTER

- No built-in search analytics
- Limited customization
- No AI chatbot integration
- No ticket system
- Slow load times (vs dedicated)
- No offline access

WORKAROUNDS

- Use Super.so for better design
- Add Crisp/Intercom for chat
- Use Tally for feedback forms
- Third-party analytics (Plausible)

BEST FOR

- Early-stage startups
- Internal documentation
- Simple public docs
- Supplement to main help center
```

## Enterprise AI Platforms (2026)

### Salesforce Proactive Service AI

Salesforce's proactive AI detects and resolves customer issues before they're reported.

```text
CAPABILITIES

1. Proactive Detection
   - Monitor unified customer data
   - Detect anomalies and issues
   - Alert before customer reports

2. Autonomous Resolution
   - Execute fixes automatically
   - Send proactive communications
   - Escalate only when necessary

3. Agent Assist
   - AI-generated summaries
   - Suggested next actions
   - Full context at handoff

USE CASES

- Shipping delay -> Proactive notification + discount offer
- Payment failure -> Auto-retry + customer alert
- Product issue -> Preemptive replacement initiation
- Renewal risk -> Churn prevention outreach

INTEGRATION

- Requires Salesforce Service Cloud
- Unified data platform (CDP)
- MuleSoft for external systems
- Einstein AI license required
```

### Google Gemini Enterprise CX

Google's agentic commerce platform combines shopping and customer service.

```text
CAPABILITIES

1. Agentic Commerce
   - End-to-end customer lifecycle
   - Product discovery to post-purchase
   - Autonomous resolution

2. Pre-built Agents
   - Deployable in days, not months
   - Configurable without code
   - Industry-specific templates

3. Integration
   - Google Cloud ecosystem
   - BigQuery for analytics
   - Vertex AI for customization

USE CASES (Retail/E-commerce)

- Product recommendations -> Conversational discovery
- Order tracking -> Real-time updates + proactive alerts
- Returns processing -> Autonomous handling
- Customer feedback -> Sentiment analysis + routing

PRICING

- Google Cloud consumption-based
- Vertex AI API calls
- Contact sales for enterprise pricing
```

### ServiceNow Knowledge Management

Enterprise-grade knowledge management with GenAI-powered content creation.

```text
CAPABILITIES

1. AI Content Generation
   - Auto-generate articles from closed incidents
   - Summarize resolution steps
   - Identify knowledge gaps

2. Enterprise Integration
   - ITSM workflow integration
   - Multi-department knowledge sharing
   - Approval workflows

3. Security & Compliance
   - SOC 2, ISO 27001, HIPAA
   - Role-based access control
   - Audit trails

BEST FOR

- Large enterprises (500+ employees)
- IT service management
- Regulated industries
- Complex multi-team environments

PRICING: Contact sales (enterprise only)
```

## Migration Guide

### Platform Migration Checklist

```
MIGRATION STEPS

1. Pre-migration
   - Audit current content
   - Map categories to new structure
   - Export all content (CSV/JSON)
   - Document redirects needed
   - Plan downtime (if any)

2. Content migration
   - Import via API or CSV
   - Update internal links
   - Re-upload images
   - Apply new templates
   - Review formatting

3. Configuration
   - Set up categories/sections
   - Configure search
   - Enable AI features
   - Set up analytics
   - Test all functionality

4. Launch
   - Update DNS (custom domain)
   - Set up redirects (301s)
   - Monitor 404s
   - Announce to users
   - Train support team

5. Post-migration
   - Monitor search analytics
   - Check for broken links
   - Gather user feedback
   - Optimize based on data
```

### Content Export Formats

```
EXPORT OPTIONS BY PLATFORM

Zendesk:
- CSV export (articles, categories)
- API (full content + metadata)
- Zendesk to Intercom migrator

Intercom:
- CSV export
- API export
- No native migrator

Freshdesk:
- Solution articles export
- API export
- CSV for bulk

GitBook:
- Git repo (full sync)
- PDF export
- API export

Notion:
- HTML export
- Markdown export
- No API export (limited)
```

### Redirect Setup

```
REDIRECT PATTERNS

Zendesk:
Settings > Guide > Search > Redirects

Intercom:
Settings > Help Center > Redirects

Freshdesk:
Admin > Support Channels > Redirects

GitBook:
.gitbook.yaml redirects section

Generic (server-level):
/old-path -> /new-path (301)
/old-category/* -> /new-category/* (wildcard)
```
