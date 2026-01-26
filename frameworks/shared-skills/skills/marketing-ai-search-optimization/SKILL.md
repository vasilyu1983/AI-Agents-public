---
name: marketing-ai-search-optimization
description: "Improve visibility in AI search and answer engines (ChatGPT, Perplexity, Gemini, Google AI Overviews) using GEO: crawl controls (robots/WAF/llms.txt), answer-ready content and entity pages, citation strategy, and measurement (query bank, share of model)."
---

# AI Search & Answer Engine Optimization (GEO)

Improve how assistants retrieve, summarize, and cite your pages.

**For traditional SEO**: Use [marketing-seo-complete](../marketing-seo-complete/SKILL.md) instead.

## Quick start (30–60 min)

1. Build a query bank (30–100 queries): problems, comparisons, “best”, “vs”, integrations, and pricing questions.
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

### 3) Make pages easy to extract and cite

- Put a direct, quotable answer block in the first screenful (then expand with proof).
- Use stable entities (product, category, competitors, integrations): use `references/entity-semantic-optimization.md`.
- Use repeatable content structures for questions, comparisons, and “best for”: use `references/content-structure-patterns.md`.
- Create/refresh high-intent pages first (alternatives, integrations, pricing, security, implementation): use `assets/strategy/ai-search-growth-plan.md`.

### 4) Add proof and trust hooks (citation fuel)

- Prefer primary sources and verifiable numbers; attribute claims clearly.
- Show authorship, review, and freshness (`dateModified` / “Last updated”) where appropriate.
- Avoid “LLM bait”: prioritize user value and factual accuracy.

### 5) Measure, iterate, and defend against regressions

- Track “share of model” / citation share using your query bank, not vanity rankings.
- Re-test after shipping changes; keep snapshots of answers and citations.
- Separate SEO wins vs assistant visibility wins; avoid false attribution.

---

## What to load (progressive disclosure)

- Platform notes: `references/platform-google-ai-overviews.md`, `references/platform-chatgpt.md`, `references/platform-perplexity.md`, `references/platform-gemini.md`, `references/platform-claude.md`
- Technical access: `references/ai-crawler-technical-setup.md`, `references/ai-indexing-complete-guide.md`
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
| [references/platform-chatgpt.md](references/platform-chatgpt.md) | ChatGPT optimization |
| [references/platform-perplexity.md](references/platform-perplexity.md) | Perplexity strategies |
| [references/platform-google-ai-overviews.md](references/platform-google-ai-overviews.md) | Google AIO optimization |
| [references/llm-tracking-tools.md](references/llm-tracking-tools.md) | LLM visibility tools |
| [references/competitor-citation-gap.md](references/competitor-citation-gap.md) | Competitor citation + query mining |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/audits/search-visibility-audit.md](assets/audits/search-visibility-audit.md) | Baseline audit |
| [assets/audits/ai-search-content-audit.md](assets/audits/ai-search-content-audit.md) | AI visibility audit |
| [assets/audits/competitor-citation-gap-audit.md](assets/audits/competitor-citation-gap-audit.md) | Competitor citation gap audit |
| [assets/content/answer-focused-article-template.md](assets/content/answer-focused-article-template.md) | Article template |
| [assets/content/ai-answer-diagnosis-template.md](assets/content/ai-answer-diagnosis-template.md) | Structured diagnosis output |

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
| [marketing-seo-complete](../marketing-seo-complete/SKILL.md) | Traditional SEO |
| [marketing-content-strategy](../marketing-content-strategy/SKILL.md) | Content planning |
| [software-frontend](../software-frontend/SKILL.md) | SSR implementation |
| [project-aeo-monitoring-tools](../project-aeo-monitoring-tools/SKILL.md) | Build custom AEO monitoring infrastructure (APIs, scraping, pipelines) |
