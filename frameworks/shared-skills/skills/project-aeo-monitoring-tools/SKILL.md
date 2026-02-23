---
name: project-aeo-monitoring-tools
description: "Use when building custom AEO monitoring infrastructure. Covers API access, scraping architecture, legal compliance, and cost estimation for AI search visibility tracking. Reference implementation: TypeScript/Next.js/Supabase stack."
version: 1.0.0
tags: [aeo, monitoring, scraping, api, competitive-analysis, engineering]
---

# AEO Monitoring Tools

Build custom infrastructure for monitoring AI search engine visibility and competitive citation analysis.

**Audience**: Engineers building custom AEO monitoring systems
**Related**: For AEO strategy and optimization guidance, see `marketing-ai-search-optimization`

## When to Use This Skill

- Building custom AEO monitoring infrastructure
- Evaluating build vs. buy decisions for AI search tracking
- Understanding API vs. scraping trade-offs per platform
- Designing data pipelines for citation analysis
- Estimating costs for multi-platform monitoring

## Verify Before Committing

AEO tools evolve rapidly (acquisitions, pricing changes, new entrants). Before committing to any tool or API, verify current status via web search:

- `"[tool name] pricing [current year]"`
- `"[platform] API rate limits [current year]"`
- `"AEO monitoring tools comparison [current year]"`

## Decision Framework: Build vs. Buy

Before building custom tools, evaluate whether commercial solutions fit your needs.

| Factor | Use Commercial Tools | Build Custom |
| ------ | -------------------- | ------------ |
| Budget | <$500/mo | >$2,000/mo in tool costs OR need custom queries |
| Query volume | <500 queries/week | >2,000 queries/week |
| Platform coverage | Standard 5-6 engines | Need niche engines or custom prompts |
| Integration needs | Standard exports (CSV, API) | Deep CRM/analytics integration |
| Engineering capacity | No dedicated engineer | 1+ FTE available |
| Customization | Standard metrics sufficient | Custom scoring, proprietary analysis |

**Commercial tools to evaluate first:**

**AEO-Native Tools:**

| Tool | Price | Strengths |
| ---- | ----- | --------- |
| Profound | $499/mo | Full AEO tracking, competitor analysis |
| Goodie AI | $495+/mo | GEO-first (ChatGPT, Gemini, Perplexity, Claude, Copilot, DeepSeek) |
| Otterly.AI | Contact | Multi-platform monitoring (ChatGPT, Perplexity, Gemini, AI Overviews) |
| AIclicks.io | Varies | All-in-one ChatGPT monitoring + optimization advice |
| LLMrefs | Free | Basic citation tracking |
| OmniSEO | Free | Free comprehensive AI tracking |

**Incumbents Adding AEO Features:**

| Tool | Price | Strengths |
| ---- | ----- | --------- |
| Semrush AI Toolkit | $188+/mo | Enterprise + full SEO suite integration |
| Ahrefs Brand Radar | Varies | Real-time brand monitoring across AI platforms |
| SE Ranking AI Visibility | Varies | Combined AI + classic SEO tracking |
| Authoritas | Enterprise | Complex custom prompt analysis |
| BrightEdge | Enterprise | Enterprise SEO + AI visibility |

See `docs/context.md` in the reference implementation for 24+ competitors with funding data.

## Platform Access Overview

Each AI platform requires different access approaches.

| Platform | Recommended Approach | API Available | Monthly Cost | Citation Support |
| -------- | -------------------- | ------------- | ------------ | ---------------- |
| Perplexity | Sonar API | Yes (citations native) | $15-30 | Native |
| Gemini | Free API tier | Yes (1,500/day free) | $0 | Extract from response |
| Claude | Claude API | Yes | $75-150 | Extract from response |
| ChatGPT / OpenAI | Official API (use web search tools if available) OR commercial vendor | Yes (varies) | $60-500+ | Varies (official tools or vendor) |
| Google AI Overviews | Commercial tools only | No (typically) | N/A | Commercial tools only |
| Microsoft Copilot | Commercial tools only | Limited | N/A | Commercial tools only |
| DeepSeek | DeepSeek API | Yes | $5-50 | Extract from response |
| Grok | X API (limited) | Limited | Varies | Extract from response |

> **Note**: DeepSeek and Grok are listed for completeness. The reference implementation currently supports Perplexity, Gemini, Claude, and OpenAI. DeepSeek and Grok collectors are not yet implemented.

**Key insight**: Perplexity Sonar API is the most AEO-friendly - it returns citations natively in the response.

See: [references/platform-access-methods.md](references/platform-access-methods.md)

## Architecture Tiers

### Tier 1: API-First (Recommended)

Use official APIs where available. Lowest risk, most maintainable.

```text
Query Bank -> API Orchestrator -> Response Store -> Analysis Layer
   (30-100 quick start;     (rate limiting,    (PostgreSQL/    (citation extraction,
    queries)     retry logic)       BigQuery)       brand detection)
```

**Platforms covered**: Perplexity, Gemini, Claude, OpenAI (baseline; use official web-search tooling if available)
**Cost**: $15-300/mo depending on volume
**Risk**: Low

### Tier 2: Hybrid (API + Commercial Scraping)

Add commercial scraping services for platforms without good APIs.

**Additional coverage**: ChatGPT web interface, Google AI Overviews
**Cost**: $500-1,500/mo (adds commercial scraper fees)
**Risk**: Medium (dependent on scraper provider)

### Tier 3: Full Custom Scraping (Not Recommended)

DIY web scraping of AI platforms.

**Why to avoid**:

- High ToS violation risk
- Aggressive bot detection (especially Google, ChatGPT)
- Maintenance burden (UI changes break scrapers)
- Potential legal liability

See: [assets/technical/architecture-diagrams.md](assets/technical/architecture-diagrams.md)

## Risk Assessment Matrix

| Approach | ToS Risk | Legal Risk | Detection Risk | Recommendation |
| -------- | -------- | ---------- | -------------- | -------------- |
| Official APIs | None | None | None | RECOMMENDED |
| Commercial scraping services | Transferred to provider | Provider's liability | Low | Acceptable with due diligence |
| DIY web scraping | High | Medium-High | High | NOT RECOMMENDED |
| Violating robots.txt | Very High | High | Very High | NEVER |

**Legal developments to monitor**:

- Publisher lawsuits and data sourcing disputes (example: Reddit v. Perplexity AI (2024))
- Platform ToS enforcement and liquidated damages policies (example: X ToS changes)
- Rising use of crawler blocks and WAF rules (GPTBot, ClaudeBot, etc.)

See: [references/legal-compliance.md](references/legal-compliance.md)

## Cost Estimation

| Tier | Components | Monthly Cost |
| ---- | ---------- | ------------ |
| Minimal | Gemini free + Perplexity Sonar + Supabase | $15-50 |
| Standard | Multi-platform APIs + PostgreSQL | $150-300 |
| Comprehensive | APIs + commercial scraping + analytics | $500-1,500 |
| Enterprise | Full coverage + dedicated infrastructure | $2,000+ |

See: [references/cost-estimation.md](references/cost-estimation.md)

## Implementation Timeline

| Week | Focus | Deliverables |
| ---- | ----- | ------------ |
| 1 | Foundation | Query bank (30-100 quick start, scale to 250-500), API accounts, database schema |
| 2 | Core pipeline | API orchestrator, response storage, citation extraction |
| 3 | Analysis | Brand detection, competitor tracking, Share of Model calc |
| 4 | Reporting | Dashboard, alerts, maintenance procedures |
| 5-6 | Advanced features | Bot analytics, page health scoring, IndexNow integration, `.well-known/` file access tracking |
| 7-8 | Intelligence layer | Citation graph analysis, persona visibility, content optimization engine |

See: [assets/setup/minimal-setup-guide.md](assets/setup/minimal-setup-guide.md)

## What to Load (Progressive Disclosure)

Load additional references based on your needs:

| Reference | When to Load |
| --------- | ------------ |
| [references/platform-access-methods.md](references/platform-access-methods.md) | API setup, rate limits, authentication per platform |
| [references/legal-compliance.md](references/legal-compliance.md) | ToS analysis, compliance checklist, disclaimer language |
| [references/cost-estimation.md](references/cost-estimation.md) | Detailed pricing breakdown, ROI calculation |
| [assets/technical/architecture-diagrams.md](assets/technical/architecture-diagrams.md) | System architecture, data flow diagrams |
| [assets/technical/code-templates.md](assets/technical/code-templates.md) | Python orchestrator, SQL schema, extraction functions |
| [assets/technical/typescript-patterns.md](assets/technical/typescript-patterns.md) | TypeScript-specific patterns for the reference implementation |
| [assets/setup/minimal-setup-guide.md](assets/setup/minimal-setup-guide.md) | Step-by-step 4-week implementation guide |

## Quick Validation (First API Call)

Test Perplexity Sonar to confirm citations work:

```bash
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [{"role": "user", "content": "What is [YOUR_BRAND]?"}]
  }'
```

Expected: JSON response with `citations` array containing source URLs. If your brand appears with citations, monitoring is viable for that platform.

## Quick Start Checklist

```text
[ ] Define query bank (30-100 for quick start; 250-500 for advanced)
[ ] Choose platforms to monitor (prioritize by ICP usage)
[ ] Evaluate build vs. buy decision
[ ] If building: Set up API accounts (Perplexity, Gemini, Claude/OpenAI)
[ ] Run quick validation call above to confirm API access
[ ] Create database schema (PostgreSQL recommended)
[ ] Build API orchestrator with rate limiting
[ ] Implement citation extraction
[ ] Set up scheduled runs (daily/weekly)
[ ] Create Share of Model dashboard
[ ] Document maintenance procedures
[ ] (Optional) Monitor access to discovery files (/llms.txt, /.well-known/*.json)
```

## Key Metrics

**Primary metric**: Share of Model (SoM)

```text
SoM = (Your brand mentions / Total responses) * 100
```

Track SoM:

- Per platform (ChatGPT, Perplexity, Gemini, Claude)
- Per query intent (informational, commercial, transactional)
- Over time (weekly/monthly trends)
- vs. competitors

**Secondary metrics**:

- Brand mention rate (% of responses where your brand is named in answer text — 3.2x more frequent than citations per BrightEdge)
- Citation rate (% of responses with your URL)
- Position in citations (1st, 2nd, 3rd mention)
- Third-party vs owned citation ratio (what % of citations come from G2, Reddit, YouTube vs your site)
- Sentiment of brand mentions
- Query coverage (% of target queries where you appear)

**Advanced metrics** (reference implementation features):

- Bot ingestion rate (% of pages crawled by AI bots from server logs)
- Page health score (composite: freshness + structure + citation-readiness)
- Citation network depth (how many hops from your cited page to the AI response)
- AI referral tracking (traffic from known AI assistant domains)
- Persona visibility (brand appearance segmented by user demographic/persona)
- Content optimization score (gap between current content and ideal citation-ready structure)

## Advanced Features (Beyond Basic Monitoring)

The reference implementation extends basic monitoring with these advanced capabilities:

### Bot Analytics and Crawler Intelligence

Track which AI crawlers access your content and how they process it.

- Server log analysis for GPTBot, ClaudeBot, PerplexityBot, GoogleOther
- Crawl frequency and depth patterns per bot
- Content type preferences (which pages bots visit most)
- Ingestion-to-citation correlation (does being crawled lead to being cited?)
- Discovery file access tracking: monitor requests to `/llms.txt`, `/.well-known/llmprofiles.json`, `/.well-known/mcp.json`, `/.well-known/agents.json` to measure AI agent adoption of emerging standards

### Citation Network Analysis

Map how citations flow between your content and AI responses.

- Citation graph: track which of your pages are cited, by which platforms, for which queries
- Citation co-occurrence: which competitor pages appear alongside yours
- Citation depth: direct citation vs. derived/summarized mentions
- Temporal patterns: how citation freshness decays over time
- Third-party citation tracking: monitor when third-party sources (G2, Reddit, YouTube, listicles) cite your brand in AI responses vs. your owned pages. See `marketing-ai-search-optimization/references/earned-aeo-third-party-citations.md` for the earned AEO strategy that feeds this data

### Content Optimization Engine

Automated recommendations for improving citation probability.

- Gap analysis: compare your content structure against top-cited pages
- Recommendation engine: specific suggestions (add TL;DR, add comparison table, cite primary sources)
- A/B tracking: measure citation rate changes after content updates
- Priority scoring: which pages have highest citation improvement potential

### Personas and Demographics

Understand how different user segments discover your brand through AI.

- Persona-based query segmentation (technical buyer, executive, end user)
- Platform preference by persona (developers prefer Perplexity, executives prefer ChatGPT)
- Visibility gaps by segment: where you're strong vs. weak per persona
- Brand hub: centralized brand identity data for consistent AI representation

## Related Skills

- `marketing-ai-search-optimization` - AEO strategy, content optimization, measurement methodology. Includes `.well-known/` AI discovery file implementation guides (`assets/technical/well-known-ai-discovery.md`): `llmprofiles.json`, `mcp.json`, `agents.json`, `agent.json`
- `marketing-ai-search-optimization/references/earned-aeo-third-party-citations.md` - Earned AEO strategy (Reddit, G2, YouTube, Wikipedia) that feeds monitoring data
- `marketing-ai-search-optimization/references/multimodal-content-optimization.md` - Video/audio optimization driving YouTube citation metrics
- `marketing-ai-search-optimization/references/commerce-protocol-ucp.md` - Google UCP for e-commerce monitoring
- `marketing-content-strategy` - Content planning and editorial strategy
- `marketing-product-analytics` - Product analytics and measurement frameworks
- `software-api-design` - API integration patterns
- `qa-observability` - Monitoring and alerting setup

## Disclaimer

This guidance is for educational purposes. Users must:

- Conduct their own legal review
- Ensure compliance with applicable terms of service
- Respect robots.txt directives
- Follow laws and regulations in their jurisdiction

Building monitoring tools that violate platform ToS may result in account termination, legal action, or both.
