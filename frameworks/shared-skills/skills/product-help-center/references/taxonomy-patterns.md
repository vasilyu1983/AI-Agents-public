# Taxonomy Patterns

Information architecture patterns for help centers and knowledge bases.

## Contents

- Category Hierarchy Rules
- Standard Category Structures
- User-Centric Organization
- Tagging Strategies
- Search Optimization
- Navigation Patterns
- Cross-Linking Strategy
- Content Deduplication
- URL Structure

## Category Hierarchy Rules

### Depth Limits

```
HIERARCHY BEST PRACTICES

Maximum depth: 3 levels
Optimal depth: 2 levels
Top-level categories: 5-9 (Miller's Law)
Articles per category: 10-20

BAD: Products > Software > Desktop > Windows > Settings > Display
GOOD: Settings > Display Settings
```

### Cognitive Load Principle

Users can hold 7 +/- 2 items in working memory. Apply this to:

| Element | Target | Maximum |
|---------|--------|---------|
| Top-level categories | 5-7 | 9 |
| Subcategories per parent | 5-7 | 10 |
| Steps in how-to | 5-7 | 10 |
| FAQ questions per section | 5-8 | 12 |

## Standard Category Structures

### SaaS Product (B2B)

```
RECOMMENDED STRUCTURE

1. Getting Started
   |-- Quick Start Guide
   |-- Account Setup
   \\-- First Project

2. [Core Feature 1]
   |-- Overview
   |-- How-To Guides
   \\-- Best Practices

3. [Core Feature 2]
   |-- Overview
   |-- How-To Guides
   \\-- Best Practices

4. Integrations
   |-- Native Integrations
   |-- API
   \\-- Zapier/Make

5. Account & Billing
   |-- Account Settings
   |-- Team Management
   |-- Billing & Invoices
   \\-- Security

6. Troubleshooting
   |-- Common Issues
   |-- Error Messages
   \\-- Performance

7. What's New
   |-- Release Notes
   \\-- Roadmap
```

### E-commerce Platform

```
RECOMMENDED STRUCTURE

1. Getting Started
   |-- Account Creation
   |-- First Order
   \\-- App Download

2. Orders & Shipping
   |-- Track Order
   |-- Shipping Options
   |-- Returns & Exchanges
   \\-- Order Issues

3. Payments
   |-- Payment Methods
   |-- Refunds
   |-- Gift Cards
   \\-- Payment Issues

4. Account
   |-- Profile Settings
   |-- Addresses
   |-- Password & Security
   \\-- Notifications

5. Products
   |-- Size Guides
   |-- Care Instructions
   \\-- Availability

6. Loyalty Program
   |-- How It Works
   |-- Points & Rewards
   \\-- Member Benefits
```

### Developer Platform

```
RECOMMENDED STRUCTURE

1. Getting Started
   |-- Quick Start
   |-- Installation
   |-- Authentication
   \\-- First API Call

2. Guides
   |-- Core Concepts
   |-- Tutorials
   \\-- Best Practices

3. API Reference
   |-- Endpoints
   |-- Authentication
   |-- Rate Limits
   \\-- Errors

4. SDKs & Libraries
   |-- JavaScript
   |-- Python
   |-- Ruby
   \\-- Go

5. Integrations
   |-- Webhooks
   |-- OAuth
   \\-- Third-Party

6. Resources
   |-- Changelog
   |-- Status Page
   \\-- Community
```

## User-Centric Organization

### Organize by User Goal, Not Feature

```
WRONG (feature-centric)
|-- Dashboard
|-- Reports Module
|-- Settings Panel
|-- API Section

RIGHT (goal-centric)
|-- Track Performance
|-- Analyze Results
|-- Configure Your Account
|-- Build Integrations
```

### Audience-Based Categories

```
MULTI-AUDIENCE STRUCTURE

For Users
|-- Getting Started
|-- Daily Tasks
\\-- Troubleshooting

For Admins
|-- Setup & Configuration
|-- User Management
|-- Security & Compliance

For Developers
|-- API Reference
|-- SDKs
\\-- Webhooks
```

### Journey-Based Categories

```
USER JOURNEY STRUCTURE

Evaluate
|-- Product Overview
|-- Pricing
|-- Comparison Guides

Onboard
|-- Quick Start
|-- Initial Setup
|-- First Success

Use Daily
|-- Core Workflows
|-- Tips & Tricks
|-- Shortcuts

Expand
|-- Advanced Features
|-- Integrations
|-- Team Collaboration

Troubleshoot
|-- Common Issues
|-- Error Reference
|-- Contact Support
```

## Tagging Strategies

### Flat Tags (Recommended for <500 articles)

```
TAG TYPES

Topic tags: billing, security, api, mobile
Audience tags: admin, user, developer
Content type: how-to, troubleshooting, reference, faq
Product area: dashboard, reports, settings
Difficulty: beginner, intermediate, advanced
```

### Hierarchical Tags (For >500 articles)

```
TAG HIERARCHY

integration/
|-- integration/native
|-- integration/api
|-- integration/zapier
\\-- integration/webhooks

billing/
|-- billing/payments
|-- billing/invoices
|-- billing/refunds
\\-- billing/subscriptions
```

### Tag Governance

| Rule | Example |
|------|---------|
| Lowercase only | `billing` not `Billing` |
| Singular form | `integration` not `integrations` |
| No spaces | `getting-started` not `getting started` |
| Max tags per article | 3-5 tags |
| Required tags | At least 1 topic + 1 content type |

## Search Optimization

### Synonyms & Redirects

```
SYNONYM MAPPING

User searches -> Canonical term
"password reset" -> "reset password"
"cost" -> "pricing"
"sign up" -> "create account"
"login" -> "sign in"
"delete" -> "remove"
"cancel" -> "unsubscribe"

REDIRECT RULES

/help/billing -> /help/account/billing
/faq -> /help
/support -> /help
```

### Search Result Ranking

```
RANKING FACTORS (priority order)

1. Title match (exact)
2. Title match (partial)
3. Heading match
4. Body content match
5. Tag match
6. Popularity (views)
7. Freshness (updated date)

BOOST FACTORS

+50% Getting Started articles (for new users)
+30% Recently updated content
+20% High-rated content
-50% Archived content
```

### Zero-Result Search Handling

```
ZERO-RESULT STRATEGY

1. Track all zero-result queries
2. Weekly review of top 20 queries
3. Actions:
   - Create new article
   - Add synonyms
   - Update existing article title
   - Add to FAQ

FALLBACK UI

"No results for '[query]'"
- Did you mean: [suggestions]
- Popular articles: [top 3]
- Browse categories: [list]
- Contact support: [link]
```

## Navigation Patterns

### Breadcrumbs

```
BREADCRUMB RULES

Format: Home > Category > Subcategory > Article
Separator: > or /
Clickable: All except current page
Mobile: Collapse to "... > Parent > Current"

EXAMPLE
Help Center > Account > Security > Enable Two-Factor Auth
```

### Related Articles

```
RELATED ARTICLES LOGIC

Display: 3-5 articles
Position: End of article, sidebar
Selection criteria:
1. Same category (weight: 40%)
2. Shared tags (weight: 30%)
3. User behavior (also viewed) (weight: 20%)
4. Manual curation (weight: 10%)

EXCLUDE
- Current article
- Archived articles
- Different audience level
```

### Next Steps / Call-to-Action

```
NEXT STEPS PATTERN

After how-to:
-> Related advanced guide
-> Troubleshooting for this feature
-> Video tutorial

After troubleshooting:
-> Contact support (if unresolved)
-> Related how-to
-> Community forum

After conceptual:
-> How-to using this concept
-> API reference
-> Example project
```

### Table of Contents

```
TOC RULES

Show when: Article > 500 words OR > 3 headings
Position: Top of article, sticky sidebar
Depth: H2 and H3 only
Clickable: Smooth scroll to section
Highlight: Current section in view
```

## Cross-Linking Strategy

### Internal Link Rules

| Link Type | When to Use | Format |
|-----------|-------------|--------|
| Inline | First mention of related topic | [topic name](url) |
| See also | Alternative approaches | "See also: [title]" |
| Prerequisites | Required prior knowledge | Listed at top |
| Next steps | Continuation of journey | Listed at bottom |

### Link Maintenance

```
LINK HEALTH CHECKS

Weekly:
- [ ] Check for broken links (404s)
- [ ] Update redirects for moved content

Monthly:
- [ ] Review orphan pages (no incoming links)
- [ ] Check for circular references
- [ ] Update outdated cross-references

Quarterly:
- [ ] Full link audit
- [ ] Update deprecated content links
- [ ] Review external links
```

## Content Deduplication

### Avoiding Duplication

```
SINGLE SOURCE OF TRUTH

Problem: Same info in multiple places
Solution: One canonical article + links

EXAMPLE

BAD:
- Article A: "How to reset password" (full steps)
- Article B: "Account security" (same steps inline)
- FAQ: "How do I reset password?" (same steps)

GOOD:
- Article A: "How to reset password" (full steps)
- Article B: "Account security" (link to A)
- FAQ: "How do I reset password?" (link to A)
```

### Content Reuse Patterns

```
REUSABLE COMPONENTS

Warnings/Notes:
<!-- include: security-warning.md -->

Common steps:
<!-- include: navigate-to-settings.md -->

Product limits:
<!-- include: plan-limits-table.md -->

IMPLEMENTATION
- Zendesk: Content blocks
- Intercom: Reusable content
- GitBook: Reusable content / includes
- Notion: Synced blocks
```

## URL Structure

### URL Best Practices

```
URL PATTERNS

Good:
/help/billing/upgrade-plan
/docs/api/authentication
/guides/getting-started

Bad:
/help/article/12345
/kb/cat-billing/sub-payments/art-upgrade
/help/billing_and_payments/how_to_upgrade_your_plan

RULES
- Lowercase only
- Hyphens (not underscores)
- No IDs in URL
- Max 3 levels deep
- Descriptive slugs
```

### URL Redirects

```
REDIRECT TYPES

301 (Permanent): Content moved forever
302 (Temporary): Testing, A/B
Canonical: Duplicate content prevention

WHEN TO REDIRECT
- Article renamed
- Category restructured
- Content merged
- Old URLs bookmarked/linked externally
```
