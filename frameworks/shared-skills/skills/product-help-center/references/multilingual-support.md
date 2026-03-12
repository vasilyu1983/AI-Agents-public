# Multilingual Support

Operational patterns for running a multilingual help center at scale.

## Contents

- Translation workflow
- Platform capabilities
- Translation management tools
- Machine translation + human review
- Glossary management
- Content prioritization
- URL structure for multilingual content
- RTL language support
- Measuring coverage and quality
- Checklist: multilingual launch readiness
- Do/Avoid

## Translation Workflow

Standard four-stage pipeline from source to published translation.

```
TRANSLATION PIPELINE

1. Source authoring
   - Write and publish article in source language (usually English)
   - Mark article as "ready for translation"
   - Freeze source content during translation cycle

2. Translation
   - Send to translation vendor, internal team, or MT engine
   - Provide glossary and style guide with every batch
   - Include screenshots with callout text for context

3. Review
   - Native speaker reviews for accuracy and tone
   - Product SME validates technical correctness
   - QA checks formatting, links, and placeholder variables

4. Publish
   - Publish translated article linked to source
   - Verify URL structure and hreflang tags
   - Update sitemap with new language URLs
```

Batch cadence: weekly for high-volume, biweekly for steady-state, per-release for product-driven content.

## Platform Capabilities

| Platform | Multilingual Support | How It Works |
|----------|---------------------|--------------|
| Zendesk Guide | Native | Built-in localization per article. Toggle languages in Guide settings. Auto-detects user locale. |
| Intercom | Native | Content localization per article. Language targeting in Messenger. Fin supports multiple languages. |
| Freshdesk | Native | Multi-language knowledge base. Separate folders per language. Auto-detect or manual toggle. |
| GitBook | Manual/Plugin | No native multilingual. Use separate spaces per language or variant groups. |
| Notion | Manual | Duplicate pages per language. No locale detection. Not recommended for multilingual. |
| Confluence | Plugin | Scroll Translations or manual page copies. Enterprise-oriented. |

For platforms without native multilingual support, use a TMS (translation management system) with API integration.

## Translation Management Tools

| Tool | Strength | Pricing Model | Best For |
|------|----------|--------------|----------|
| Crowdin | Developer-friendly, Git integration | Free for open source; from $40/mo | Technical docs, developer products |
| Phrase (Memsource) | Enterprise TMS, CAT tools, TM/glossary | From $25/user/mo | Large-scale, agency workflows |
| Transifex | Continuous localization, API-first | From $120/mo | SaaS products, frequent updates |
| Lokalise | Clean UI, screenshot context, branching | From $120/mo | Product teams, mobile + web |
| Smartling | Enterprise, neural MT, connector library | Custom pricing | Enterprise, regulated industries |

Selection criteria: integration with your help center platform, support for translation memory, glossary management, and reviewer workflows.

## Machine Translation + Human Review

Pure machine translation is not ready for customer-facing help content. Use MT as a first draft, then human-review.

```
MT + HUMAN REVIEW WORKFLOW

1. Source article finalized in English
2. Run through MT engine (DeepL, Google Cloud Translation, or TMS built-in)
3. Human reviewer edits for:
   - Product terminology (MT often mistranslates feature names)
   - Tone and formality (varies by locale)
   - UI label accuracy (must match localized product UI)
   - Cultural references and idioms
4. QA pass: check formatting, variables, links
5. Publish

QUALITY TIERS

Tier 1 (full human translation): legal, billing, security content
Tier 2 (MT + human review): how-to guides, feature docs
Tier 3 (MT + light review): release notes, changelog, low-traffic articles
```

Expected effort reduction with MT + review vs. full translation: 40-60% cost savings, 50-70% faster turnaround.

## Glossary Management

Glossary prevents inconsistent translations of product-specific terms.

```
GLOSSARY STRUCTURE

| Source Term | Target (es) | Target (de) | Target (ja) | Notes |
|-------------|-------------|-------------|-------------|-------|
| Dashboard | Dashboard | Dashboard | ダッシュボード | Do not translate |
| Workspace | Espacio de trabajo | Arbeitsbereich | ワークスペース | Translate |
| SSO | SSO | SSO | SSO | Acronym — keep as-is |
| Admin | Administrador | Administrator | 管理者 | Translate |

GLOSSARY RULES

- Brand name: never translate
- Product feature names: follow localized UI (check with product team)
- Technical acronyms (API, SSO, URL): keep in English unless locale convention differs
- UI labels: must match exactly what the user sees in the localized product
- Legal terms: use jurisdiction-appropriate equivalents, reviewed by legal

MAINTENANCE

- Update glossary with every product release that adds or renames features
- Share glossary with all translators and reviewers
- Store in TMS (single source of truth) or versioned spreadsheet
```

## Content Prioritization

Translate the highest-impact content first, not everything at once.

```
PRIORITIZATION FRAMEWORK

Phase 1 — Core (launch requirement):
- Top 20 articles by traffic
- Getting started / onboarding flow
- Billing and account management
- Contact support page

Phase 2 — Expand (first 30 days post-launch):
- Next 30 articles by traffic
- Troubleshooting for top error messages
- FAQ pages

Phase 3 — Long tail (ongoing):
- Remaining articles by descending traffic
- Release notes (translate per release)
- Community guidelines

DECISION GUIDE

Translate a new language when:
- 10%+ of traffic comes from that locale
- Sales is actively selling in that market
- Legal/regulatory requirements mandate it (e.g., EU, Quebec)
- Support ticket volume in that language exceeds 5% of total
```

## URL Structure for Multilingual Content

| Pattern | Example | Pros | Cons |
|---------|---------|------|------|
| Subdirectory | example.com/es/help/article | Simple, single domain, good for SEO | Slightly longer URLs |
| Subdomain | es.help.example.com | Clear separation, independent hosting | More DNS/SSL management |
| Parameter | example.com/help/article?lang=es | Easiest to implement | Poor for SEO, not recommended |
| Separate domain | ayuda.example.es | Strong local signal | Expensive, hard to maintain |

Recommended: subdirectory (`/en/`, `/es/`, `/de/`). Best balance of SEO, simplicity, and maintenance.

```
HREFLANG IMPLEMENTATION

Add to every page <head>:

<link rel="alternate" hreflang="en" href="https://help.example.com/en/article" />
<link rel="alternate" hreflang="es" href="https://help.example.com/es/article" />
<link rel="alternate" hreflang="de" href="https://help.example.com/de/article" />
<link rel="alternate" hreflang="x-default" href="https://help.example.com/en/article" />

RULES
- Every translated page must reference all its language variants
- x-default points to the fallback (usually English)
- Submit all language variants in sitemap
```

## RTL Language Support

Languages requiring right-to-left layout: Arabic, Hebrew, Farsi, Urdu.

```
RTL REQUIREMENTS

Layout:
- Mirror the entire page layout (navigation, sidebars, content flow)
- Use CSS logical properties (margin-inline-start instead of margin-left)
- Set dir="rtl" and lang attribute on <html> or content container

Typography:
- Use fonts that support Arabic/Hebrew glyphs (Noto Sans Arabic, IBM Plex Arabic)
- Increase line height by 10-20% for Arabic script readability
- Do not justify Arabic text — use right-aligned

Content:
- Numbers remain left-to-right within RTL text (bidirectional)
- UI screenshots must show RTL version of the product (if available)
- Code blocks remain LTR even in RTL articles

Testing:
- Test with native RTL speakers, not just visual inspection
- Verify breadcrumbs, tables, and navigation reverse correctly
- Check that mixed LTR/RTL content (English terms in Arabic text) renders properly
```

## Measuring Coverage and Quality

```
COVERAGE METRICS

| Metric | Formula | Target |
|--------|---------|--------|
| Translation coverage | Translated articles / Total articles x 100 | >80% for Tier 1 languages |
| Top-article coverage | Translated top-50 / 50 x 100 | 100% |
| Freshness | Translations updated within 7 days of source change | >90% |
| Missing translations | Articles with no translation in active languages | 0 for Phase 1 content |

QUALITY METRICS

| Metric | How to Measure | Target |
|--------|----------------|--------|
| Helpfulness per locale | Article feedback ratings by language | Within 10% of source language |
| Escalation rate per locale | Tickets after article view, by language | Within 15% of source language |
| Glossary compliance | Spot-check sample of translated articles | >95% correct term usage |
| Linguistic quality | Monthly review by native speaker (sample 10 articles) | Score 4+/5 |
```

## Checklist: Multilingual Launch Readiness

```
PRE-LAUNCH

- [ ] Target languages selected based on traffic/market data
- [ ] Glossary created and shared with translators
- [ ] TMS configured and integrated with help center platform
- [ ] URL structure defined (subdirectory recommended)
- [ ] Hreflang tags implemented
- [ ] Phase 1 content translated and reviewed
- [ ] RTL support tested (if applicable)
- [ ] Language switcher visible and functional
- [ ] Locale auto-detection configured (with manual override)
- [ ] Analytics configured to segment by language

POST-LAUNCH

- [ ] Sitemap updated with all language URLs
- [ ] Google Search Console shows indexed translations
- [ ] Helpfulness ratings tracked per language
- [ ] Translation freshness monitoring active
- [ ] Feedback loop established: support team flags translation issues
```

## Do/Avoid

```
DO

- Start with top 20 articles, not full coverage
- Use a TMS with translation memory to reduce cost over time
- Match translated UI labels exactly to the localized product
- Freeze source content during active translation cycles
- Track helpfulness per language separately
- Budget for ongoing translation with every release

AVOID

- Publishing raw machine translation without human review
- Translating screenshots by overlaying text (re-capture in localized UI instead)
- Assuming one Spanish variant works for all Spanish-speaking markets
- Ignoring RTL requirements until after launch
- Treating translation as a one-time project (it is ongoing ops)
- Letting glossary drift out of sync with the product
```
