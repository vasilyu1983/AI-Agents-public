# Content Migration Guide

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

Rule: never migrate and redesign at the same time. Migrate first, redesign after baseline metrics stabilize.

## Pre-Migration Audit

Before touching content, build a complete inventory.

```
AUDIT CHECKLIST

1. Content inventory
   - Export full article list with metadata (title, URL, category, author, last updated)
   - Record article count per category
   - Flag draft/unpublished articles

2. Traffic data
   - Export 90-day page views per article (GA4 or platform analytics)
   - Identify top 50 articles by traffic
   - Identify bottom 20% (candidates for archive/delete)

3. Link health
   - Run broken link scan (Screaming Frog, Ahrefs, or platform tool)
   - Document internal cross-links between articles
   - List external sites linking to your help center (Ahrefs, Search Console)

4. Content quality
   - Pull helpfulness ratings per article
   - Flag articles not updated in 12+ months
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
| Delete | Zero traffic, outdated, no inbound links | Remove, set up 301 to nearest relevant article |

Priority order: migrate high-traffic articles first, then work down the triage list.

## URL Redirect Strategy

Every old URL must resolve. Broken links destroy SEO and user trust.

```
REDIRECT RULES

1. Build a redirect map spreadsheet
   Columns: old_url | new_url | redirect_type | status | verified

2. Redirect types
   - 301 (permanent): default for all migrations
   - 302 (temporary): only during staged rollout or A/B testing

3. Wildcard redirects
   - Use for entire category moves: /old-category/* -> /new-category/*
   - Test wildcards thoroughly — bad patterns break unrelated pages

4. Testing
   - Crawl all old URLs and verify 301 response
   - Spot-check top 50 articles manually
   - Verify redirect chains are max 1 hop (no chains of 301 -> 301 -> 301)

5. Monitoring
   - Set up 404 monitoring post-launch (GA4, Search Console, platform alerts)
   - Review 404 report daily for first 2 weeks
```

## Migration Phases

```
PHASE 1: AUDIT (Week 1)
- Complete content inventory
- Pull traffic and quality data
- Run broken link scan
- Document external inbound links

PHASE 2: TRIAGE (Week 2)
- Apply triage matrix to every article
- Get stakeholder sign-off on delete/archive decisions
- Identify articles needing rewrite

PHASE 3: MAP REDIRECTS (Week 2-3)
- Build redirect map spreadsheet
- Define new URL structure
- Set up wildcard rules
- Peer-review redirect map

PHASE 4: MIGRATE (Week 3-4)
- Export from old platform
- Import to new platform (API or CSV)
- Re-upload images and attachments
- Apply new templates and formatting
- Restore internal cross-links

PHASE 5: QA (Week 5)
- Crawl all new URLs
- Test redirects from old URLs
- Verify images, videos, embedded content
- Check search index on new platform
- Test on mobile and screen readers
- Validate analytics tracking fires

PHASE 6: LAUNCH (Week 6)
- Switch DNS or publish new help center
- Submit updated sitemap to Search Console
- Monitor 404s and traffic daily
- Communicate change to support team
```

## Platform Export/Import

| Platform | Export Method | Format | Notes |
|----------|-------------|--------|-------|
| Zendesk Guide | Admin > Guide > CSV export; or API | CSV, JSON via API | API preserves metadata and attachments |
| Intercom | Settings > Help Center > Export; or API | CSV, JSON via API | No native bulk image export — use API |
| Freshdesk | Admin > Knowledge Base > Export | CSV | Tags and categories export separately |
| Confluence | Space tools > Content tools > Export | XML, HTML, PDF | XML preserves structure best |
| Notion | Settings > Export | HTML, Markdown | Markdown loses some formatting |
| GitBook | Git repo clone | Markdown | Cleanest export for docs-as-code workflows |

Import tip: always do a test import with 10-20 articles before running the full batch. Validate formatting, images, and metadata.

## SEO Preservation

```
SEO CHECKLIST

1. Canonical URLs
   - Set canonical tags on all new articles
   - Remove canonical tags from old platform (or shut it down)

2. Sitemap
   - Generate and submit new sitemap to Google Search Console
   - Remove old sitemap
   - Verify new sitemap is indexed (Search Console > Sitemaps)

3. Google Search Console
   - Add new property if domain changed
   - Use Change of Address tool if moving domains
   - Monitor Index Coverage report for errors
   - Monitor Core Web Vitals on new platform

4. Structured data
   - Preserve or add FAQ schema, HowTo schema, Breadcrumb schema
   - Test with Google Rich Results Test

5. Meta tags
   - Migrate title tags and meta descriptions
   - Do not let the new platform auto-generate generic descriptions
```

## Post-Migration Validation

```
VALIDATION CHECKLIST (run within 48 hours of launch)

Content integrity:
- [ ] Article count matches expected (migrated + new - deleted)
- [ ] All images and attachments load
- [ ] Embedded videos play
- [ ] Code blocks render correctly
- [ ] Tables display properly on mobile

Links and navigation:
- [ ] Internal cross-links resolve
- [ ] Old URLs redirect (spot-check top 50)
- [ ] Breadcrumbs show correct hierarchy
- [ ] Search returns results for top 20 queries

SEO and analytics:
- [ ] Sitemap submitted and indexed
- [ ] Analytics tracking fires on all pages
- [ ] 404 error rate below 1% of traffic
- [ ] Google Search Console shows no new crawl errors

Functional:
- [ ] Search works (test 10 common queries)
- [ ] Feedback widget works
- [ ] Contact/escalation links work
- [ ] AI chatbot (if any) pulls from new content
```

## Rollback Plan

Never migrate without a fallback.

```
ROLLBACK STRATEGY

1. Keep old platform running in parallel for 30-90 days
   - Read-only mode is fine
   - Do not delete old content until new platform is stable

2. DNS rollback
   - Document exact DNS changes made
   - Test DNS revert in staging before launch
   - Keep old SSL certificate valid

3. Rollback triggers
   - 404 rate exceeds 5% of traffic for 24+ hours
   - Search index not picked up after 7 days
   - Critical content missing with no backup
   - Platform outage on new provider lasting 4+ hours

4. Communication plan
   - Notify support team immediately on rollback
   - Post status page update if customer-facing
```

## Timeline Template: 6-Week Migration

| Week | Phase | Key Deliverables |
|------|-------|-----------------|
| 1 | Audit | Content inventory, traffic data, link audit |
| 2 | Triage + redirect mapping | Triage decisions, redirect spreadsheet |
| 3 | Migrate (batch 1) | Top 50 articles migrated, images uploaded |
| 4 | Migrate (batch 2) | Remaining articles, cross-links restored |
| 5 | QA | Full crawl, redirect testing, analytics verified |
| 6 | Launch + monitor | DNS switch, sitemap submitted, daily 404 review |

Adjust timeline based on article count. Under 100 articles: compress to 3-4 weeks. Over 500 articles: extend to 8-10 weeks.

## Do/Avoid

```
DO

- Build the redirect map before migrating anything
- Test-import a small batch first
- Preserve URL slugs where possible
- Monitor 404s daily for the first 2 weeks
- Keep the old platform alive as a rollback
- Communicate the migration timeline to the support team

AVOID

- Migrating and redesigning simultaneously
- Deleting old platform before validating the new one
- Skipping the content triage (migrating junk wastes effort)
- Using 302 redirects when you mean 301
- Relying solely on wildcard redirects without testing
- Ignoring external inbound links (they carry SEO value)
- Launching on a Friday
```
