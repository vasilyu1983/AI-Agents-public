# Content Migration Guide

## Table of Contents

- [Contents](#contents)
- [Migration Triggers](#migration-triggers)
- [Pre-Migration Audit](#pre-migration-audit)
- [Content Triage Matrix](#content-triage-matrix)
- [URL Redirect Strategy](#url-redirect-strategy)
- [Migration Phases](#migration-phases)
- [Platform Export/Import](#platform-exportimport)
- [SEO Preservation](#seo-preservation)
- [Post-Migration Validation](#post-migration-validation)
- [Rollback Plan](#rollback-plan)
- [Timeline Template](#timeline-template)
- [Do/Avoid](#doavoid)

Patterns and checklists for migrating help center content between platforms or during redesigns.

## Contents

- Migration triggers
- Pre-migration audit
- Content triage matrix
- URL redirect strategy
- Migration phases
- Platform export/import
- SEO preservation
- Post-migration validation
- Rollback plan
- Timeline template
- Do/Avoid

## Migration Triggers

Common reasons to migrate:

| Trigger | Urgency | Typical Complexity |
|---------|---------|-------------------|
| Platform change (e.g., Zendesk to Intercom) | Medium | High |
| Help center redesign or IA overhaul | Low | Medium |
| Company acquisition or merger | High | High |
| Rebrand (name, domain, or visual identity) | Medium | Medium |
| Platform pricing change or sunset | High | High |
| Consolidating multiple help centers into one | Medium | High |

Separate platform migration from a major information-architecture redesign when possible. If they must ship together, record each content and URL change in the redirect map and test the new tree against top tasks.

## Pre-Migration Audit

Before touching content, build a complete inventory.

```
AUDIT CHECKLIST

1. Content inventory
   - Export full article list with metadata (title, URL, category, author, last updated)
   - Record article count per category
   - Flag draft/unpublished articles

2. Traffic data
   - Export a representative traffic period per article (analytics or platform reports)
   - Identify the highest-impact articles and inbound-linked URLs
   - Flag low-use articles for review, not automatic deletion

3. Link health
   - Run broken link scan (Screaming Frog, Ahrefs, or platform tool)
   - Document internal cross-links between articles
   - List external sites linking to your help center (Ahrefs, Search Console)

4. Content quality
   - Pull helpfulness ratings per article
   - Flag articles past their owner-defined review cadence
   - Flag articles with negative feedback trends
```

## Content Triage Matrix

Score every article before migration. Do not migrate garbage.

| Decision | Criteria | Action |
|----------|----------|--------|
| Migrate as-is | High traffic, positive ratings, current content | Copy to new platform, preserve URL |
| Rewrite | High traffic but outdated or low-rated | Rewrite before or immediately after migration |
| Merge | Multiple articles covering the same topic | Consolidate into one, redirect old URLs |
| Archive | Low traffic, still accurate, niche audience | Move to archive category, keep URL alive |
| Delete | Outdated with no continuing task or inbound-link value | Remove; redirect only where a genuinely equivalent destination exists |

Priority order: migrate high-traffic articles first, then work down the triage list.

## URL Redirect Strategy

Map old URLs to equivalent destinations where they exist. For removed content without an equivalent, return the appropriate removal status and update internal links.

```
REDIRECT RULES

1. Build a redirect map spreadsheet
   Columns: old_url | new_url | redirect_type | status | verified

2. Redirect types
   - Permanent redirect: for a permanent URL move to an equivalent destination
   - Temporary redirect: for a temporary move or staged rollout

3. Wildcard redirects
   - Use for entire category moves: /old-category/* -> /new-category/*
   - Test wildcards thoroughly — bad patterns break unrelated pages

4. Testing
   - Crawl old URLs and verify each mapped permanent or temporary redirect
   - Spot-check the highest-impact and externally linked articles manually
   - Verify redirect chains are max 1 hop (no chains of 301 -> 301 -> 301)

5. Monitoring
   - Set up 404 monitoring post-launch (GA4, Search Console, platform alerts)
   - Review 404 report daily for first 2 weeks
```

## Migration Phases

```
PHASE 1: AUDIT
- Complete content inventory
- Pull traffic and quality data
- Run broken link scan
- Document external inbound links

PHASE 2: TRIAGE
- Apply triage matrix to every article
- Get stakeholder sign-off on delete/archive decisions
- Identify articles needing rewrite

PHASE 3: MAP REDIRECTS
- Tree-test the new category tree on top tasks; fix failing paths first
- Build redirect map spreadsheet
- Define new URL structure
- Set up wildcard rules
- Peer-review redirect map

PHASE 4: MIGRATE
- Export from old platform
- Import to new platform (API or CSV)
- Re-upload images and attachments
- Apply new templates and formatting
- Restore internal cross-links

PHASE 5: QA
- Crawl all new URLs
- Test redirects from old URLs
- Verify images, videos, embedded content
- Check search index on new platform
- Test on mobile and screen readers
- Validate analytics tracking fires

PHASE 6: LAUNCH
- Switch DNS or publish new help center
- Submit updated sitemap to Search Console
- Monitor 404s and traffic daily
- Communicate change to support team
```

## Platform Export/Import

For each platform, check its current export and import documentation before selecting API, bulk export, or repository sync. Test a small representative batch that includes images, attachments, code blocks, metadata, and redirects before importing the full library.

## SEO Preservation

```
SEO CHECKLIST

1. Canonical URLs
   - Set canonical tags on all new articles
   - Confirm the old URLs redirect and the new pages carry the intended canonical URL

2. Sitemap
   - Generate and submit new sitemap to Google Search Console
   - Review the old sitemap and redirects during the [site move](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes); do not remove discovery paths before old URLs have been checked
   - Use Search Console to inspect discovery and indexing of the new URLs; sitemap submission does not guarantee indexing

3. Google Search Console
   - Add new property if domain changed
   - Use Change of Address tool if moving domains
   - Monitor Page indexing for errors
   - Monitor Core Web Vitals on new platform

4. Structured data
   - Preserve supported, relevant markup such as Breadcrumb where it matches visible content; [Google retired HowTo rich results and restricted FAQ rich results](https://developers.google.com/search/blog/2023/08/howto-faq-changes)
   - Check Google's current supported structured-data types and test eligible markup

5. Meta tags
   - Migrate title tags and meta descriptions
   - Do not let the new platform auto-generate generic descriptions
```

## Post-Migration Validation

```
VALIDATION CHECKLIST (begin at launch and repeat until stable)

Content integrity:
- [ ] Article count matches expected (migrated + new - deleted)
- [ ] All images and attachments load
- [ ] Embedded videos play
- [ ] Code blocks render correctly
- [ ] Tables display properly on mobile

Links and navigation:
- [ ] Internal cross-links resolve
- [ ] Old URLs redirect to equivalent destinations (spot-check important and linked URLs)
- [ ] Breadcrumbs show correct hierarchy
- [ ] Search resolves the highest-volume and highest-risk queries

SEO and analytics:
- [ ] Sitemap submitted; new URL indexing monitored separately
- [ ] Analytics tracking fires on all pages
- [ ] 404s reviewed against the pre-migration baseline and redirect map
- [ ] New crawl and indexing errors are triaged against the baseline

Functional:
- [ ] Search works for representative common and high-risk queries
- [ ] Feedback widget works
- [ ] Contact/escalation links work
- [ ] AI chatbot (if any) pulls from new content
```

## Rollback Plan

Never migrate without a fallback.

```
ROLLBACK STRATEGY

1. Keep the old platform available until redirect, content, and rollback checks pass
   - Read-only mode is fine
   - Do not delete old content until new platform is stable

2. DNS rollback
   - Document exact DNS changes made
   - Test DNS revert in staging before launch
   - Keep old SSL certificate valid

3. Rollback triggers
   - Important old URLs fail to reach the mapped equivalent pages
   - Search cannot find task-critical content
   - Critical content missing with no backup
   - Platform outage exceeds the team's agreed recovery threshold

4. Communication plan
   - Notify support team immediately on rollback
   - Post status page update if customer-facing
```

## Timeline Template

| Phase | Exit evidence |
|-------|---------------|
| Audit | Content inventory, traffic data, and link audit complete |
| Triage + redirect mapping | Content decisions and mapped equivalent URLs reviewed |
| Representative import | Images, metadata, links, and formatting checked |
| Full migration + QA | Crawl, redirects, search, and analytics verified |
| Launch + monitor | Rollback path ready; 404 and support signals monitored |

Set the schedule from article volume, export capability, review capacity, and the team's release window.

## Do/Avoid

```
DO

- Build the redirect map before migrating anything
- Test-import a small batch first
- Preserve URL slugs where possible
- Monitor 404s during the agreed stabilization window
- Keep the old platform alive as a rollback
- Communicate the migration timeline to the support team

AVOID

- Combining migration and redesign without a tested redirect and task map
- Deleting old platform before validating the new one
- Skipping the content triage (migrating junk wastes effort)
- Using 302 redirects when you mean 301
- Relying solely on wildcard redirects without testing
- Ignoring external inbound links (they carry SEO value)
- Launching on a Friday
```
