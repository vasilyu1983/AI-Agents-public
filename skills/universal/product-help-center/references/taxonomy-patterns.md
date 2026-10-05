# Taxonomy Patterns

## Table of Contents

- [Contents](#contents)
- [Category Hierarchy Rules](#category-hierarchy-rules)
- [Standard Category Structures](#standard-category-structures)
- [User-Centric Organization](#user-centric-organization)
- [Tagging Strategies](#tagging-strategies)
- [Search Optimization](#search-optimization)
- [Navigation Patterns](#navigation-patterns)
- [Cross-Linking Strategy](#cross-linking-strategy)
- [Content Deduplication](#content-deduplication)
- [URL Structure](#url-structure)

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

### Depth and Breadth

```
HIERARCHY BEST PRACTICES

Keep paths as shallow as the tasks allow; validate depth with a tree test
Top-level categories: size them from top tasks and ticket intents, then confirm with a tree test
Split a category when users cannot scan or locate its articles in the tree test

BAD: Products > Software > Desktop > Windows > Settings > Display
GOOD: Settings > Display Settings
```

Do not justify a category count with Miller's "7 +/- 2": that is a working-memory span result, and people scan menus rather than recall them. Menu research points in a direction rather than to a number: in a web-structure experiment, added depth hurt search performance, yet the broadest, shallowest structure was not the best either (Larson & Czerwinski, CHI 1998). The count that works for your users is whatever passes a tree test.

### Tree Test Before Launch or Migration

Run a tree test (text-only hierarchy, no visual design) on the proposed category tree before building it or mapping redirects:

1. Take the top tasks from ticket intents, zero-result searches, and escalation-after-view data.
2. Write each task as a scenario in the user's words, not in category labels.
3. Record the path each participant takes and where they first go wrong.
4. Fix the labels or placement on failing paths, then retest those tasks.

Rerun the test after a large relabel, a merge of categories, or a platform migration.

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
| Tag count | Use only tags that change filtering or retrieval; review unused tags |
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
RANKING SIGNALS TO TEST

- Exact product terms and error strings in titles and headings
- Body relevance and approved synonyms
- Audience, role, plan, locale, and product-version filters
- Freshness for claims that change with releases or policy
- Popularity and helpfulness only after relevance is established

Measure search success before and after tuning. Remove archived content from search where the platform permits it; do not rely on an arbitrary negative boost.
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

Display: a short set of relevant articles; test whether readers use them
Position: End of article, sidebar
Selection criteria:
1. Same task or next step
2. Shared, governed tags and audience
3. Observed user paths, checked for relevance
4. Manual curation for high-risk or newly released topics

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
| Inline | First mention of related topic | `[topic name](https://example.com/related-topic)` |
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
