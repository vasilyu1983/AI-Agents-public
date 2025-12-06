---
name: marketing-seo-technical
description: Technical SEO auditing for traditional search engines (Google, Bing) covering Core Web Vitals, crawlability, structured data, mobile optimization, site architecture, and actionable fix recommendations.
---

# TECHNICAL SEO AUDITING — OPERATIONAL SKILL

This skill contains **actionable, production-ready systems** for performing comprehensive technical SEO audits and delivering prioritized optimization recommendations for **traditional search engines** (Google, Bing).

Use this skill when the user asks for:
- Technical SEO audits (full or targeted)
- Core Web Vitals optimization (LCP, INP, CLS)
- Crawlability and indexation issues
- Structured data/Schema.org implementation
- Mobile-first optimization
- Site speed and performance fixes
- Internal linking architecture
- Duplicate content and canonical handling
- International SEO (hreflang)
- Security and HTTPS configuration

---

## Quick Reference

| Task | Resource/Template | Location | When to Use |
|------|------------------|----------|-------------|
| **Auditing** | | | |
| Full Technical Audit | 10-Point Checklist | `templates/audits/full-technical-audit.md` | Comprehensive site-wide audit |
| Quick Audit | Abbreviated Checklist | `templates/audits/quick-audit-checklist.md` | Fast issue identification |
| Priority Matrix | Impact vs Effort | `templates/priority/impact-effort-matrix.md` | Prioritize audit findings |
| **Core Web Vitals** | | | |
| CWV Deep Dive | CWV Guide | `resources/core-web-vitals-guide.md` | LCP, INP, CLS optimization |
| CWV Report | Report Template | `templates/cwv/core-web-vitals-report.md` | Document CWV findings |
| **Crawlability** | | | |
| Indexation Issues | Crawlability Guide | `resources/crawlability-indexing.md` | Robots.txt, sitemaps, GSC issues |
| **Performance** | | | |
| Site Speed | Speed Guide | `resources/site-speed-optimization.md` | TTFB, render-blocking, images |
| **Technical Setup** | | | |
| Mobile Optimization | Mobile Guide | `resources/mobile-seo-guide.md` | Responsive, viewport, mobile-first |
| Structured Data | Schema Guide | `resources/structured-data-guide.md` | JSON-LD, rich snippets |
| Schema Report | Validation Template | `templates/schema/schema-validation-report.md` | Document schema findings |
| Security/HTTPS | Security Guide | `resources/security-https-guide.md` | HTTPS, HSTS, headers |
| **Architecture** | | | |
| Internal Linking | Link Strategy | `resources/internal-linking-strategy.md` | Link equity, orphan pages |
| Duplicate Content | Canonical Guide | `resources/duplicate-content-handling.md` | Canonicals, pagination |
| International SEO | Hreflang Guide | `resources/internationalization-hreflang.md` | Multi-language/region sites |

---

## 10-Point Audit Framework

Every technical SEO audit follows this systematic checklist:

| # | Area | Key Metrics | Weight |
|---|------|-------------|--------|
| 1 | **Crawlability** | robots.txt status, sitemap coverage, crawl budget | High |
| 2 | **Core Web Vitals** | LCP <2.5s, INP <200ms, CLS <0.1 | High |
| 3 | **Site Speed** | TTFB <800ms, FCP <1.8s, Speed Index | High |
| 4 | **Mobile** | Mobile-friendly score, viewport, touch targets | High |
| 5 | **Security** | HTTPS, mixed content, HSTS, headers | Medium |
| 6 | **Structured Data** | Schema validity, rich snippet eligibility | Medium |
| 7 | **On-Page** | Meta tags, heading hierarchy, keyword signals | Medium |
| 8 | **Architecture** | Internal links, URL structure, canonicals | High |
| 9 | **Duplicate Content** | Canonical implementation, pagination | Medium |
| 10 | **Internationalization** | Hreflang (if applicable), geo-targeting | Low |

**Scoring**: Rate each area 0-10, calculate weighted average for overall Technical Health Score.

---

## Decision Trees

```text
### Audit Type Selection
Full site audit needed
  └─ Use templates/audits/full-technical-audit.md
Quick issue check
  └─ Use templates/audits/quick-audit-checklist.md
CWV-only deep dive
  └─ Use templates/cwv/core-web-vitals-report.md
Schema validation only
  └─ Use templates/schema/schema-validation-report.md

### Core Web Vitals Failing
LCP >2.5s
  └─ Preload LCP element, optimize images, add CDN
  └─ See resources/core-web-vitals-guide.md
INP >200ms
  └─ Reduce JavaScript, optimize event handlers
  └─ See resources/core-web-vitals-guide.md
CLS >0.1
  └─ Add dimensions to images/ads, avoid layout shifts
  └─ See resources/core-web-vitals-guide.md

### Indexation Issues
Pages not indexed
  └─ Check robots.txt blocking
  └─ Verify sitemap inclusion
  └─ Check canonical tags
  └─ See resources/crawlability-indexing.md
Crawl budget problems
  └─ Remove low-value pages from crawl
  └─ Fix redirect chains
  └─ Optimize pagination
  └─ See resources/crawlability-indexing.md

### Mobile Issues
Mobile-unfriendly
  └─ Check viewport meta tag
  └─ Verify responsive CSS
  └─ Test touch target sizes
  └─ See resources/mobile-seo-guide.md

### Security Issues
Mixed content warnings
  └─ Update all HTTP resources to HTTPS
  └─ See resources/security-https-guide.md
SSL/TLS issues
  └─ Run SSL Labs test
  └─ See resources/security-https-guide.md
```

---

## Navigation

### Core Resources

- [resources/core-web-vitals-guide.md](resources/core-web-vitals-guide.md) - LCP, INP, CLS thresholds and optimization
- [resources/crawlability-indexing.md](resources/crawlability-indexing.md) - Robots.txt, sitemaps, GSC, indexation
- [resources/site-speed-optimization.md](resources/site-speed-optimization.md) - TTFB, render-blocking, image optimization
- [resources/mobile-seo-guide.md](resources/mobile-seo-guide.md) - Mobile-first indexing, responsive design
- [resources/structured-data-guide.md](resources/structured-data-guide.md) - Schema.org, JSON-LD, rich snippets
- [resources/security-https-guide.md](resources/security-https-guide.md) - HTTPS, HSTS, security headers
- [resources/internal-linking-strategy.md](resources/internal-linking-strategy.md) - Link architecture, orphan pages
- [resources/duplicate-content-handling.md](resources/duplicate-content-handling.md) - Canonicals, pagination, parameters
- [resources/internationalization-hreflang.md](resources/internationalization-hreflang.md) - Hreflang, geo-targeting

### Templates

#### Audits
- [templates/audits/full-technical-audit.md](templates/audits/full-technical-audit.md) - Complete 10-point audit checklist
- [templates/audits/quick-audit-checklist.md](templates/audits/quick-audit-checklist.md) - Fast abbreviated audit

#### Core Web Vitals
- [templates/cwv/core-web-vitals-report.md](templates/cwv/core-web-vitals-report.md) - CWV-specific audit report

#### Structured Data
- [templates/schema/schema-validation-report.md](templates/schema/schema-validation-report.md) - Schema audit report

#### Prioritization
- [templates/priority/impact-effort-matrix.md](templates/priority/impact-effort-matrix.md) - Issue prioritization matrix

---

## Related Skills

**Marketing & SEO**
- [../marketing-ai-search-optimization/SKILL.md](../marketing-ai-search-optimization/SKILL.md) - AI search engines (ChatGPT, Perplexity, Claude, Gemini) - complementary to traditional SEO
- [../marketing-social-media/SKILL.md](../marketing-social-media/SKILL.md) - Social media marketing and content distribution

**Technical Implementation**
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) - Frontend performance optimization, SSR
- [../software-backend/SKILL.md](../software-backend/SKILL.md) - Server-side optimization, API performance
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) - Security hardening, HTTPS implementation

**Quality & Performance**
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md) - Performance monitoring, observability
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) - CDN setup, infrastructure optimization

---

## Key Differentiators

**Technical SEO vs AI Search Optimization:**
- Technical SEO: Optimize for Googlebot, traditional SERP rankings, Core Web Vitals
- AI Search: Optimize for LLM retrieval, citations, answer quality

**Audit Output Format:**
- **Critical Issues** - Fix immediately (high impact)
- **Important Optimizations** - Fix soon (medium impact)
- **Recommended Enhancements** - Nice to have

**Each finding includes:**
- What's wrong and why it matters
- Step-by-step fix instructions
- Expected outcome
- Validation method

---

## External Resources

See [data/sources.json](data/sources.json) for 53 curated sources across:
- Google official documentation (Search Central, web.dev)
- Core Web Vitals optimization guides
- Crawlability and indexing references
- SEO tools (Ahrefs, Semrush, Moz, Screaming Frog)
- Industry blogs and case studies
- JavaScript SEO guides

---

## Getting Started

**Quick audit (15 minutes):**
1. Run PageSpeed Insights on key pages
2. Check robots.txt and sitemap.xml accessibility
3. Validate structured data with Rich Results Test
4. Review GSC Coverage report for indexation issues
5. Use [templates/audits/quick-audit-checklist.md](templates/audits/quick-audit-checklist.md)

**Full audit (2-4 hours):**
1. Use [templates/audits/full-technical-audit.md](templates/audits/full-technical-audit.md)
2. Work through all 10 audit areas systematically
3. Score each area 0-10
4. Prioritize findings with [templates/priority/impact-effort-matrix.md](templates/priority/impact-effort-matrix.md)
5. Document fixes with validation steps

**Ongoing monitoring:**
1. Set up GSC alerts for indexation issues
2. Monitor Core Web Vitals in CrUX
3. Schedule quarterly audits
4. Track improvements against baseline

---

## Success Criteria

> A successful technical SEO audit delivers a prioritized list of issues with clear fix instructions and validation methods that measurably improve search visibility and Core Web Vitals scores.
