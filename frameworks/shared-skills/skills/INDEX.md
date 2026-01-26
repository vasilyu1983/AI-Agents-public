# Codex Skills Index

This directory contains 84 production-grade skills organized by domain.

**Total Skills:** 84 (79 domain skills + 5 routers)
**Last Updated:** 2026-01-25

---

## Router Architecture

Start with `router-main` as your entry point. It routes to domain-specific routers:

```text
YOUR QUERY
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              router-main                                     │
│                         (Universal Entry Point)                              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
      ┌───────────────┬───────────┴───────────┬───────────────┐
      │               │                       │               │
      ▼               ▼                       ▼               ▼
┌───────────┐  ┌─────────────┐  ┌─────────────────┐  ┌───────────┐
│  router-  │  │   router-   │  │     router-     │  │  router-  │
│  startup  │  │ engineering │  │   operations    │  │    qa     │
│ 26 skills │  │  29 skills  │  │    7 skills     │  │ 12 skills │
└───────────┘  └─────────────┘  └─────────────────┘  └───────────┘
```

| Router | Skills | Domain |
|--------|--------|--------|
| [router-main](router-main/SKILL.md) | — | Universal entry point, routes to domain routers |
| [router-startup](router-startup/SKILL.md) | 26 | Business, marketing (11), documents (6), product, UX |
| [router-engineering](router-engineering/SKILL.md) | 29 | AI/ML (8), software (11), data (4), Claude Code (6) |
| [router-operations](router-operations/SKILL.md) | 7 | DevOps, git (2), documentation (2), help center |
| [router-qa](router-qa/SKILL.md) | 12 | Testing (7), quality (5): debugging, observability, resilience, refactoring, docs coverage |

---

## Quick Reference

| Domain | Skills | Description |
|--------|--------|-------------|
| [Routers](#routers-5-skills) | 5 | Meta-orchestration for intelligent skill routing |
| [Startup](#startup-7-skills) | 7 | Idea validation, competitive analysis, business models, fundraising, GTM |
| [AI/ML](#aiml-8-skills) | 8 | LLMs, agents, RAG, MLOps, data science |
| [Claude Code](#claude-code-6-skills) | 6 | Agents, commands, hooks, MCP, skills, memory |
| [Data](#data-4-skills) | 4 | Data lake/lakehouse, SQL optimization, analytics engineering, Metabase automation |
| [Documentation](#documentation-2-skills) | 2 | AI-friendly PRDs, codebase docs |
| [Document Formats](#document-formats-4-skills) | 4 | PDF, DOCX, XLSX, PPTX file processing |
| [Developer Tools](#developer-tools-5-skills) | 5 | API design, dependencies, git, workflows |
| [Marketing](#marketing-11-skills) | 11 | SEO, AI search, social media, lead gen, content, paid ads, email, CRO, product analytics, geo-localization, visual design |
| [Operations](#operations-2-skills) | 2 | DevOps platform, help center design |
| [Product](#product-1-skill) | 1 | Product management |
| [QA](#qa-12-skills) | 12 | Testing (7), debugging, refactoring, observability, resilience, docs coverage, agent testing, API contracts |
| [Software](#software-11-skills) | 11 | Frontend, backend, mobile, architecture, security, UX research, clean code |
| [Project-only](#project-only-6-skills) | 6 | Project-specific domain expertise (astrology suite, real estate, QTax) |

---

## Routers (5 skills)

| Skill | Description |
|-------|-------------|
| [router-main](router-main/SKILL.md) | Universal entry point that routes to domain-specific routers |
| [router-startup](router-startup/SKILL.md) | Routes startup, marketing (11), documents (6), and product skills (26 total) |
| [router-engineering](router-engineering/SKILL.md) | Routes AI/ML (8), software (11), data (4), and Claude Code (6) skills (29 total) |
| [router-operations](router-operations/SKILL.md) | Routes DevOps, git (2), documentation (2), help center skills (7 total) |
| [router-qa](router-qa/SKILL.md) | Routes testing (7) and quality (5) skills: debugging, observability, resilience, refactoring, docs coverage (12 total) |

---

## Startup (7 skills)

| Skill | Description |
|-------|-------------|
| [startup-idea-validation](startup-idea-validation/SKILL.md) | Systematic 9-dimension validation: problem severity, market sizing, timing, moats, unit economics, founder-market fit, technical feasibility, GTM clarity, risk profile |
| [startup-competitive-analysis](startup-competitive-analysis/SKILL.md) | Deep competitive intelligence, market mapping, positioning (April Dunford), moat analysis, battlecards |
| [startup-business-models](startup-business-models/SKILL.md) | Revenue model design, unit economics (LTV, CAC, payback), pricing strategy, SaaS/marketplace metrics |
| [startup-fundraising](startup-fundraising/SKILL.md) | Fundraising strategy, pitch preparation, investor targeting, term sheet negotiation, data rooms |
| [startup-go-to-market](startup-go-to-market/SKILL.md) | GTM strategy, PLG/sales-led motion design, channel selection, launch planning, growth loops |
| [startup-trend-prediction](startup-trend-prediction/SKILL.md) | Analyze 2-3 year historical trends to predict 1-2 years ahead using adoption curves, cycle analysis, signal detection |
| [startup-review-mining](startup-review-mining/SKILL.md) | Extract pain points from reviews (G2, Capterra, App Store, Reddit, HN) across 7 dimensions: UI/UX, pricing, support, integration, performance, onboarding, value |

---

## AI/ML (8 skills)

| Skill | Description |
|-------|-------------|
| [ai-agents](ai-agents/SKILL.md) | Production-grade AI agent patterns with MCP integration, agentic RAG, handoff orchestration, multi-layer guardrails, and observability |
| [ai-llm](ai-llm/SKILL.md) | Complete LLM development: strategy selection, dataset design, PEFT/LoRA fine-tuning, evaluation workflows, vLLM deployment |
| [ai-llm-inference](ai-llm-inference/SKILL.md) | LLM inference optimization: serving, quantization, batching, caching, benchmarking |
| [ai-ml-data-science](ai-ml-data-science/SKILL.md) | ML workflows: EDA, feature engineering, model evaluation, data transformation |
| [ai-ml-timeseries](ai-ml-timeseries/SKILL.md) | Time series modeling patterns and forecasting strategies |
| [ai-mlops](ai-mlops/SKILL.md) | ML operations: data ingestion, drift detection, monitoring, ML security, privacy, governance |
| [ai-prompt-engineering](ai-prompt-engineering/SKILL.md) | Operational prompt engineering patterns, templates, and validation flows |
| [ai-rag](ai-rag/SKILL.md) | RAG and search engineering: chunking, hybrid retrieval, reranking, evaluation frameworks |

---

## Claude Code (6 skills)

| Skill | Description |
|-------|-------------|
| [claude-code-agents](claude-code-agents/SKILL.md) | Create Claude Code agents with YAML frontmatter, tool selection, model specification |
| [claude-code-commands](claude-code-commands/SKILL.md) | Create slash commands with $ARGUMENTS handling, agent invocation patterns |
| [claude-code-hooks](claude-code-hooks/SKILL.md) | Event-driven hooks for automation: PreToolUse, PostToolUse, Stop events |
| [claude-code-mcp](claude-code-mcp/SKILL.md) | Build Model Context Protocol (MCP) servers for database, filesystem, API connections |
| [claude-code-project-memory](claude-code-project-memory/SKILL.md) | Configure CLAUDE.md/AGENTS.md for large codebases (100K-1M LOC), hierarchical docs, cross-platform support |
| [claude-code-skills](claude-code-skills/SKILL.md) | Reference for creating skills with SKILL.md structure, references/, progressive disclosure |

---

## Documentation (2 skills)

| Skill | Description |
|-------|-------------|
| [docs-ai-prd](docs-ai-prd/SKILL.md) | PRDs, specs, and CLAUDE.md context for AI coding agents (Claude Code, Cursor, Custom GPTs) |
| [docs-codebase](docs-codebase/SKILL.md) | Technical writing: README, API docs, ADRs, changelogs, docs-as-code |

**Note:** Documentation coverage audits are in [qa-docs-coverage](qa-docs-coverage/SKILL.md) under Quality.

---

## Document Formats (4 skills)

| Skill | Description |
|-------|-------------|
| [document-docx](document-docx/SKILL.md) | Word documents: tracked changes, formatting, styles, tables, template generation |
| [document-pdf](document-pdf/SKILL.md) | PDF workflows: extraction, creation, merge/split, forms, annotations |
| [document-pptx](document-pptx/SKILL.md) | PowerPoint: slides, layouts, charts, animations, speaker notes |
| [document-xlsx](document-xlsx/SKILL.md) | Excel: formulas, formatting, charts, pivot tables, data validation |

---

## Developer Tools (5 skills)

| Skill | Description |
|-------|-------------|
| [dev-api-design](dev-api-design/SKILL.md) | REST, GraphQL, gRPC patterns: versioning, auth, rate limiting, pagination |
| [dev-dependency-management](dev-dependency-management/SKILL.md) | Package management: npm, pip, cargo, maven, lockfiles, security scanning |
| [git-commit-message](git-commit-message/SKILL.md) | Auto-generate conventional commit messages from git diffs |
| [git-workflow](git-workflow/SKILL.md) | Git collaboration: branching strategies, PR workflows, commit conventions |
| [dev-workflow-planning](dev-workflow-planning/SKILL.md) | Development workflows: brainstorm, write-plan, execute-plan patterns |

---

## Marketing (11 skills)

| Skill | Description |
|-------|-------------|
| [marketing-ai-search-optimization](marketing-ai-search-optimization/SKILL.md) | AI search visibility: GEO (Generative Engine Optimization), AI Overviews citations, ChatGPT/Perplexity/Gemini optimization, answer engine visibility |
| [marketing-content-strategy](marketing-content-strategy/SKILL.md) | Content strategy: positioning, messaging hierarchy, content pillars, editorial calendars, trust-building, brand architecture |
| [marketing-cro](marketing-cro/SKILL.md) | Conversion rate optimization: A/B testing methodology, landing page optimization, form design, statistical significance, funnel analysis |
| [marketing-email-automation](marketing-email-automation/SKILL.md) | Email marketing automation: workflow design, HubSpot/Klaviyo/Mailchimp, nurture sequences, deliverability, revenue attribution |
| [marketing-geo-localization](marketing-geo-localization/SKILL.md) | Geographic targeting and localization: regional campaigns, multi-market expansion, local SEO, geo-specific content |
| [marketing-leads-generation](marketing-leads-generation/SKILL.md) | B2B pipeline: revenue-aligned demand generation, lead types, funnel design, scoring/routing, attribution, ABS motions |
| [marketing-paid-advertising](marketing-paid-advertising/SKILL.md) | Paid advertising: Google, Meta, TikTok, LinkedIn - campaign structure, bidding, audiences, creative, CAC/LTV, revenue attribution |
| [marketing-product-analytics](marketing-product-analytics/SKILL.md) | Product analytics: event taxonomy, tracking plans, PostHog/Pendo/Amplitude/Mixpanel/Heap, activation/retention metrics, attribution |
| [marketing-seo-complete](marketing-seo-complete/SKILL.md) | Complete SEO: technical auditing (Core Web Vitals, crawlability, structured data), keyword research, content planning, competitive analysis, Total Search Optimization |
| [marketing-social-media](marketing-social-media/SKILL.md) | Social media marketing: platform-agnostic principles, content typology, engagement quality metrics, distribution workflows |
| [marketing-visual-design](marketing-visual-design/SKILL.md) | Visual marketing: ad creatives, social graphics, email visuals, presentations, brand collateral, AI design tools |

---

## Data (4 skills)

| Skill | Description |
|-------|-------------|
| [data-analytics-engineering](data-analytics-engineering/SKILL.md) | Analytics engineering: dbt, metrics layer, semantic modeling, data quality |
| [data-lake-platform](data-lake-platform/SKILL.md) | Universal data lake/lakehouse: ingestion (dlt, Airbyte), transformation (SQLMesh, dbt), storage (Iceberg, Delta), query engines (ClickHouse, DuckDB, Doris), streaming (Kafka), orchestration, visualization (Metabase, Superset) |
| [data-metabase](data-metabase/SKILL.md) | Metabase API automation: API key auth, create/edit reports (cards), dashboards, and chart settings via visualization_settings |
| [data-sql-optimization](data-sql-optimization/SKILL.md) | OLTP SQL optimization: EXPLAIN ANALYZE, indexing, performance across PostgreSQL/MySQL/Oracle/SQL Server |

---

## Operations (2 skills)

| Skill | Description |
|-------|-------------|
| [help-center-design](help-center-design/SKILL.md) | Help center & knowledge base: AI-first support, taxonomy, self-service optimization |
| [ops-devops-platform](ops-devops-platform/SKILL.md) | DevOps: Kubernetes, GitOps, SRE, CI/CD security, AWS/GCP/Azure, Terraform |

---

## Product (1 skill)

| Skill | Description |
|-------|-------------|
| [product-management](product-management/SKILL.md) | Product management: discovery, OKRs, roadmapping, metrics, strategy |

---

## QA (12 skills)

### Testing (7)

| Skill | Description |
|-------|-------------|
| [qa-testing-strategy](qa-testing-strategy/SKILL.md) | Test strategy: unit, integration, E2E, BDD, performance with Jest/Vitest/Playwright |
| [qa-testing-playwright](qa-testing-playwright/SKILL.md) | E2E web testing: Playwright, page objects, authentication, CI/CD |
| [qa-testing-ios](qa-testing-ios/SKILL.md) | iOS testing: Xcode simulator, XCTest, Swift Testing, UI automation |
| [qa-testing-android](qa-testing-android/SKILL.md) | Android testing: Espresso, UIAutomator, Compose Testing, ADB automation, CI/CD |
| [qa-testing-mobile](qa-testing-mobile/SKILL.md) | Mobile testing: iOS + Android, device matrix, Appium, Detox |
| [qa-api-testing-contracts](qa-api-testing-contracts/SKILL.md) | API contract testing: OpenAPI validation, consumer-driven contracts, schema evolution |
| [qa-agent-testing](qa-agent-testing/SKILL.md) | QA harness for agentic systems: scenario suites, determinism controls, tool sandboxing, scoring rubrics, regression protocols |

### Quality (5)

| Skill | Description |
|-------|-------------|
| [qa-debugging](qa-debugging/SKILL.md) | Debugging: logging, error tracking, profiling, root cause analysis |
| [qa-observability](qa-observability/SKILL.md) | Observability: OpenTelemetry, tracing, metrics, SLO/SLI, APM |
| [qa-resilience](qa-resilience/SKILL.md) | Resilience: circuit breakers, retries, bulkheads, chaos engineering |
| [qa-refactoring](qa-refactoring/SKILL.md) | Refactoring: code smells, technical debt, automated quality gates |
| [qa-docs-coverage](qa-docs-coverage/SKILL.md) | Audit codebases for documentation gaps, generate coverage reports |

---

## Software (11 skills)

| Skill | Description |
|-------|-------------|
| [software-architecture-design](software-architecture-design/SKILL.md) | System design: microservices, event-driven, CQRS, modular monoliths |
| [software-clean-code-standard](software-clean-code-standard/SKILL.md) | Clean code standard: `CC-*` rule IDs, governance, language-agnostic rules |
| [software-backend](software-backend/SKILL.md) | Backend API: Node.js/Python/Rust/Go, Prisma ORM, PostgreSQL, GraphQL |
| [software-code-review](software-code-review/SKILL.md) | Code review: checklists, templates for correctness, security, performance |
| [software-crypto-web3](software-crypto-web3/SKILL.md) | Blockchain: Solidity (EVM), Rust (Solana), CosmWasm, DeFi, security |
| [software-frontend](software-frontend/SKILL.md) | Frontend: Next.js 16, React, TypeScript, Tailwind, shadcn/ui |
| [software-localisation](software-localisation/SKILL.md) | Localization: i18n/l10n, ICU message format, RTL, translation workflows |
| [software-mobile](software-mobile/SKILL.md) | Mobile: Swift (iOS), Kotlin (Android), React Native, WebView patterns |
| [software-security-appsec](software-security-appsec/SKILL.md) | Application security: OWASP Top 10:2025, zero trust, authentication |
| [software-ui-ux-design](software-ui-ux-design/SKILL.md) | UI/UX: usability heuristics, accessibility (WCAG 2.2 + 3.0 preview), design systems, React Aria, AI design tools |
| [software-ux-research](software-ux-research/SKILL.md) | UX research: JTBD, Kano Model, journey mapping, heuristic evaluation, usability testing, LLM-assisted evaluation |

---

## Project-only (6 skills)

| Skill | Description |
|-------|-------------|
| [project-astrology-chinese](project-astrology-chinese/SKILL.md) | Expert Chinese astrology advisor for 12 Animal Zodiac, Five Elements, BaZi (project) |
| [project-astrology-numerology](project-astrology-numerology/SKILL.md) | Expert astrological advisor (30+ years): validates calculations, catches logic bugs, domain expertise for chart accuracy (project) |
| [project-astrology-tarot-divination](project-astrology-tarot-divination/SKILL.md) | Expert tarot and divination advisor with spreads, card meanings, I Ching (project) |
| [project-astrology-vedic](project-astrology-vedic/SKILL.md) | Expert Vedic/Jyotish astrology advisor with dashas, nakshatras, doshas (project) |
| [project-qtax](project-qtax/SKILL.md) | UK taxation expert: HMRC, MTD, Self-Assessment, income tax, NI contributions, tax software design (project) |
| [project-real-estate-agent](project-real-estate-agent/SKILL.md) | 30+ year London real estate advisor: mortgages, market trends, solicitors, council developments, Zone 1-3 specialist (project) |

---

## Skill Structure

Each skill follows a consistent structure:

```
skill-name/
├── SKILL.md           # Main skill definition (required)
├── data/
│   └── sources.json   # Curated external references
├── references/
│   └── *.md           # Operational guides and patterns
└── assets/
    └── *.md, *.json   # Copy-paste ready templates
```

### SKILL.md Format

```yaml
---
name: skill-name
description: One-line description for Claude Code UI
---

# Skill Title

[Overview and when to use]

## When to Use This Skill
[Bullet points]

## Quick Reference
[Tables of tools, frameworks, patterns]

## Navigation
[Links to references/, assets/]
```

---

## Using Skills

### In Claude Code

Skills are automatically loaded when relevant. You can also invoke explicitly:

```text
Use the software-frontend skill to help me build a Next.js component
```

### Router Usage

Start with `router-main` for automatic routing:

```text
Ask router-main: "I need help building an API for my startup"
→ Routes to router-engineering (technical) + router-startup (business)
```

### Adding New Skills

See [claude-code-skills](claude-code-skills/SKILL.md) for the complete guide to creating new skills.

---

## Contributing

1. Follow the standard skill structure
2. Include SKILL.md with proper frontmatter
3. Add data/sources.json with curated references
4. Create references/ with operational guides
5. Add assets/ with reusable starting points
