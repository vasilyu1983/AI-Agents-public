---
name: marketing-ai-search-optimization
description: "Use when optimizing content for AI search engines and answer platforms (ChatGPT, Perplexity, Gemini, Google AI Overviews). Covers GEO: crawl controls (robots/WAF/llms.txt), answer-ready content and entity pages, citation strategy, and measurement (query bank, share of model). For building monitoring infrastructure, see project-aeo-monitoring-tools."
---

# AI Search & Answer Engine Optimization (GEO)

Improve how assistants retrieve, summarize, and cite your pages.

**For traditional SEO**: Use [marketing-seo-complete](../marketing-seo-complete/SKILL.md) instead.

## GEO vs SEO (Overlap Map)

Use this to prevent “GEO-only” work that ignores discoverability and conversion.

### GEO is best at

- Making pages easier for assistants to extract, summarize, and cite
- Building entity/proof structures that improve citation probability
- Measuring assistant visibility via query banks and citation share

### SEO is still required for

- Getting pages discovered and indexed reliably (crawlability, internal linking, canonicalization)
- Capturing demand in classic search surfaces (SERPs, video, local, forums)
- Avoiding regressions from technical changes (rendering, performance, duplication)

### Default operating rule

- Keep classic SEO and conversion work running; treat GEO as a structured overlay on top of high-intent pages.

### GEO Monitoring vs GEO Optimization

This skill covers **optimization** — improving your content so AI platforms cite you more often.

For **monitoring infrastructure** — building the systems that track whether AI platforms cite you — see [project-aeo-monitoring-tools](../project-aeo-monitoring-tools/SKILL.md).

**Typical workflow**: Monitor (track current visibility) -> Optimize (improve content) -> Measure (verify improvement)

| Activity | This skill | project-aeo-monitoring-tools |
| -------- | ---------- | ---------------------------- |
| Content structure for citation | Yes | — |
| Entity and proof optimization | Yes | — |
| Query bank construction | Quick guidance | Full methodology |
| API orchestration and pipelines | — | Yes |
| Citation extraction and analysis | — | Yes |
| Share of Model dashboard | Concept | Implementation |
| Bot analytics and crawl tracking | — | Yes |
| Cost estimation and transparency | — | Yes |

## Quick start (30–60 min)

1. Build a query bank (30–100 queries for quick start; scale to 250–500 for advanced monitoring): problems, comparisons, "best", "vs", integrations, and pricing questions.
2. Confirm assistants can fetch content (robots/WAF/SSR): use `assets/audits/crawler-access-audit.md`.
3. Run a baseline visibility audit: use `assets/audits/search-visibility-audit.md` and `assets/audits/ai-search-content-audit.md`.
4. Ship one high-leverage page update: use `assets/content/ai-search-content-brief.md` + `assets/content/answer-focused-article-template.md`.
5. Set up measurement + retest cadence: use `references/measurement-analytics.md` and `assets/testing/ai-search-testing-protocol.md`.

## Core workflow

### 1) Decide scope (avoid wasted work)

- Confirm discovery channel: check whether your ICP uses assistants for research and comparisons.
- Pick one primary platform first (Google AI Overviews vs ChatGPT vs Perplexity) based on your audience.
- Treat GEO as additive: keep classic SEO and conversion work running.

### 2) Ensure assistants can access your content

- Allow/deny crawlers explicitly: use `references/ai-crawler-technical-setup.md` and `assets/technical/robots-txt-ai-crawlers.md`.
- Reduce JS dependency for critical copy (SSR/SSG): use `assets/technical/server-side-rendering-guide.md`.
- Add `llms.txt` when useful as a navigation map (not a guarantee): use `assets/technical/llms-txt-template.md`.
- Review emerging `.well-known/` AI discovery standards (`llmprofiles.json`, `mcp.json`, `agents.json`): use `assets/technical/well-known-ai-discovery.md`.

### 3) Make pages easy to extract and cite

- Put a direct, quotable answer block in the first screenful (then expand with proof).
- Use stable entities (product, category, competitors, integrations): use `references/entity-semantic-optimization.md`.
- Use repeatable content structures for questions, comparisons, and "best for": use `references/content-structure-patterns.md`.

> **Implementation reference**: The AEO monitoring platform's recommendation engine (`src/lib/recommendations/engine.ts`) automates gap analysis against these patterns. The optimization dashboard (`src/app/optimize/page.tsx`) surfaces actionable recommendations. See `project-aeo-monitoring-tools` for the full implementation.

- Create/refresh high-intent pages first (alternatives, integrations, pricing, security, implementation): use `assets/strategy/ai-search-growth-plan.md`.

### 4) Build off-site entity presence and earned citations

- Get your brand into third-party sources AI trusts (G2, Reddit, Wikipedia, YouTube, industry listicles): use `references/earned-aeo-third-party-citations.md`.
- Strengthen Knowledge Graph presence (Wikidata, Google Business Profile, `sameAs` linking): see Knowledge Graph section in `references/entity-semantic-optimization.md`.
- Create multimodal content (video, transcripts, audio) for AI platforms that cite non-text sources: use `references/multimodal-content-optimization.md`.
- For e-commerce: implement Google UCP for agentic shopping visibility: use `references/commerce-protocol-ucp.md`.

### 5) Add proof and trust hooks (citation fuel)

- Prefer primary sources and verifiable numbers; attribute claims clearly.
- Show authorship, review, and freshness (`dateModified` / "Last updated") where appropriate.
- Avoid "LLM bait": prioritize user value and factual accuracy.

### 6) Measure, iterate, and defend against regressions

- Track "share of model" / citation share using your query bank, not vanity rankings. For automated tracking, see [project-aeo-monitoring-tools](../project-aeo-monitoring-tools/SKILL.md) (custom infrastructure) or commercial alternatives in `references/llm-tracking-tools.md`.
- Re-test after shipping changes; keep snapshots of answers and citations.
- Separate SEO wins vs assistant visibility wins; avoid false attribution.

## Implementation Examples

### Query Bank Construction

**Quick start (30-100 queries)**:

```text
Problems:     "how to [solve X]", "why does [Y happen]"
Comparisons:  "[product] vs [competitor]", "best [category] for [use case]"
Integrations: "[product] [integration] setup", "does [product] work with [tool]"
Pricing:      "[product] pricing", "[product] free plan"
```

**Advanced (250-500 queries)**: Expand with persona variants, regional variations, long-tail variations, and seasonal queries. See `project-aeo-monitoring-tools` for full query bank methodology.

### Content Structure Patterns

Apply these patterns to high-intent pages:

```text
Comparison page:
  H1: [Product A] vs [Product B]: [Year] Guide
  TL;DR: 2-3 sentence verdict
  Table: Feature comparison
  Sections: Use cases, pricing, verdict

Alternatives page:
  H1: Best [Product] Alternatives in [Year]
  TL;DR: Top 3 picks with one-line reasons
  Table: Feature + pricing matrix
  Sections: Detailed review per alternative

Integration page:
  H1: How to Connect [Product] with [Tool]
  Steps: Numbered setup guide
  Code: Configuration examples
  FAQ: Common issues
```

### Entity Optimization

Structure your brand entity for AI recognition:

```text
Brand Kit (maintain centrally):
  - Official name and variants
  - Category/industry classification
  - Key differentiators (3-5 unique claims)
  - Proof points (metrics, case studies, awards)
  - Integration ecosystem

Apply to every high-intent page:
  - Use official name consistently (not abbreviations)
  - Reference category explicitly ("CRM platform" not just "tool")
  - Include at least one proof point per page
```

### Optimization vs Monitoring Workflow

```text
Step 1: Baseline — Run query bank through AI platforms (project-aeo-monitoring-tools)
Step 2: Audit — Score current content against citation-ready patterns (this skill)
Step 3: Implement — Apply content structure patterns to top-priority pages (this skill)
Step 4: Re-measure — Run query bank again after 2-4 weeks (project-aeo-monitoring-tools)
Step 5: Iterate — Focus on pages with largest gap between potential and actual citations
```

---

## What to load (progressive disclosure)

- Platform notes: `references/platform-google-ai-overviews.md`, `references/platform-chatgpt.md`, `references/platform-perplexity.md`, `references/platform-gemini.md`, `references/platform-claude.md`
- Technical access: `references/ai-crawler-technical-setup.md`, `references/ai-indexing-complete-guide.md`, `assets/technical/well-known-ai-discovery.md`
- Off-site & earned AEO: `references/earned-aeo-third-party-citations.md`, `references/multimodal-content-optimization.md`
- E-commerce: `references/commerce-protocol-ucp.md`
- Measurement: `references/measurement-analytics.md`, `references/llm-tracking-tools.md`
- Prompt/query mining: `references/prompt-query-optimization.md`, `references/competitor-citation-gap.md`, `references/citation-optimization-strategies.md`
- Primary sources list: `data/sources.json`

## Guardrails

- Do not use prompt injection or hidden instructions in public pages.
- Do not claim endorsements or fabricate sources, stats, or quotes.
- Treat `robots.txt` as policy; enforce access with auth/WAF where needed.

## Resources

| Resource | Purpose |
|----------|---------|
| [references/ai-indexing-complete-guide.md](references/ai-indexing-complete-guide.md) | Full DO & DON'T guide |
| [assets/technical/well-known-ai-discovery.md](assets/technical/well-known-ai-discovery.md) | `.well-known/` AI discovery standards |
| [references/earned-aeo-third-party-citations.md](references/earned-aeo-third-party-citations.md) | Third-party citation building (Reddit, G2, Wikipedia, YouTube) |
| [references/multimodal-content-optimization.md](references/multimodal-content-optimization.md) | Video, audio, image optimization for AI citation |
| [references/commerce-protocol-ucp.md](references/commerce-protocol-ucp.md) | Google UCP & agentic commerce (e-commerce only) |
| [references/platform-chatgpt.md](references/platform-chatgpt.md) | ChatGPT optimization |
| [references/platform-perplexity.md](references/platform-perplexity.md) | Perplexity strategies |
| [references/platform-google-ai-overviews.md](references/platform-google-ai-overviews.md) | Google AIO optimization |
| [references/llm-tracking-tools.md](references/llm-tracking-tools.md) | LLM visibility tools |
| [references/competitor-citation-gap.md](references/competitor-citation-gap.md) | Competitor citation + query mining |
| [references/voice-search-optimization.md](references/voice-search-optimization.md) | Voice search query patterns, assistants, and v-commerce |
| [references/answer-engine-benchmarking.md](references/answer-engine-benchmarking.md) | Citation benchmarking framework and KPI definitions |
| [references/local-ai-search.md](references/local-ai-search.md) | Local business optimization for AI search engines |
| [project-aeo-monitoring-tools](../project-aeo-monitoring-tools/SKILL.md) | Custom monitoring infrastructure (build vs buy) |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/audits/search-visibility-audit.md](assets/audits/search-visibility-audit.md) | Baseline audit |
| [assets/audits/ai-search-content-audit.md](assets/audits/ai-search-content-audit.md) | AI visibility audit |
| [assets/audits/competitor-citation-gap-audit.md](assets/audits/competitor-citation-gap-audit.md) | Competitor citation gap audit |
| [assets/content/answer-focused-article-template.md](assets/content/answer-focused-article-template.md) | Article template |
| [assets/content/ai-answer-diagnosis-template.md](assets/content/ai-answer-diagnosis-template.md) | Structured diagnosis output |
| [project-aeo-monitoring-tools/assets/setup/minimal-setup-guide.md](../project-aeo-monitoring-tools/assets/setup/minimal-setup-guide.md) | Monitoring setup guide |

## International Markets

This skill uses US/English market defaults. For international AI search optimization:

| Need | See Skill |
|------|-----------|
| Regional AI platforms (Baidu AI, Yandex) | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |
| Non-English content optimization | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |
| Regional search behavior differences | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |
| Multilingual schema markup | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |

**Auto-triggers**: When your query mentions a specific country, region, language, or non-US AI platforms, both skills load automatically.

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| [project-aeo-monitoring-tools](../project-aeo-monitoring-tools/SKILL.md) | Build custom AEO monitoring infrastructure (APIs, pipelines, dashboards) — engineering skill |
| [marketing-seo-complete](../marketing-seo-complete/SKILL.md) | Traditional SEO |
| [marketing-content-strategy](../marketing-content-strategy/SKILL.md) | Content planning |
| [software-frontend](../software-frontend/SKILL.md) | SSR implementation |
