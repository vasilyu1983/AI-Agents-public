# Codex Skills Index

This directory contains 81 production-grade skills organized by domain.

**Total Skills:** 81 (77 domain skills + 4 routers)
**Last Updated:** 2026-01-21

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
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│  router-startup   │  │ router-engineering│  │ router-operations │
│  23 skills        │  │  33 skills        │  │   19 skills       │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

| Router | Skills | Domain |
|--------|--------|--------|
| [router-main](router-main/SKILL.md) | — | Universal entry point, routes to domain routers |
| [router-startup](router-startup/SKILL.md) | 23 | Business, marketing (9), documents, product, UX |
| [router-engineering](router-engineering/SKILL.md) | 33 | AI/ML, software, data (3), Claude Code framework |
| [router-operations](router-operations/SKILL.md) | 20 | QA (8), testing (5), DevOps, git, documentation, large codebase setup |

---

## Quick Reference

| Domain | Skills | Description |
|--------|--------|-------------|
| [Routers](#routers-4-skills) | 4 | Meta-orchestration for intelligent skill routing |
| [Startup](#startup-7-skills) | 7 | Idea validation, competitive analysis, business models, fundraising, GTM |
| [AI/ML](#aiml-8-skills) | 8 | LLMs, agents, RAG, MLOps, data science |
| [Claude Code](#claude-code-6-skills) | 6 | Agents, commands, hooks, MCP, skills, memory |
| [Data](#data-3-skills) | 3 | Data lake/lakehouse, SQL optimization, analytics engineering |
| [Documentation](#documentation-2-skills) | 2 | AI-friendly PRDs, codebase docs |
| [Document Formats](#document-formats-4-skills) | 4 | PDF, DOCX, XLSX, PPTX file processing |
| [Developer Tools](#developer-tools-5-skills) | 5 | API design, dependencies, git, workflows |
| [Marketing](#marketing-9-skills) | 9 | SEO, AI search, social media, lead gen, content, paid ads, email, CRO, product analytics |
| [Operations](#operations-2-skills) | 2 | DevOps platform, help center design |
| [Product](#product-1-skill) | 1 | Product management |
| [Quality](#quality-8-skills) | 8 | Debugging, refactoring, observability, resilience, docs coverage, agent testing, API contracts |
| [Software](#software-11-skills) | 11 | Frontend, backend, mobile, architecture, security, UX research, clean code |
| [Testing](#testing-5-skills) | 5 | Automation, Playwright, iOS simulator, mobile testing, Android |
| [Project-only](#project-only-6-skills) | 6 | Project-specific domain expertise (astrology suite, real estate, QTax) |

---

## Routers (4 skills)

| Skill | Description |
|-------|-------------|
| [router-main](router-main/SKILL.md) | Universal entry point that routes to domain-specific routers |
| [router-startup](router-startup/SKILL.md) | Routes startup, marketing (8), documents, and product skills (22 total) |
| [router-engineering](router-engineering/SKILL.md) | Routes AI/ML, software, data, and Claude Code skills (32 total) |
| [router-operations](router-operations/SKILL.md) | Routes QA, testing, DevOps, and git skills (15 total) |

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

## Marketing (10 skills)

| Skill | Description |
|-------|-------------|
| [marketing-ai-search-optimization](marketing-ai-search-optimization/SKILL.md) | AI search optimization for ChatGPT, Perplexity, Claude, Gemini (AEO/GEO/LLMO) |
| [marketing-content-strategy](marketing-content-strategy/SKILL.md) | Content strategy: positioning, trust building, brand architecture, message hierarchy |
| [marketing-cro](marketing-cro/SKILL.md) | Conversion rate optimization: A/B testing, landing pages, ICE/PIE prioritization |
| [marketing-email-automation](marketing-email-automation/SKILL.md) | Email marketing automation: workflows, sequences, deliverability, segmentation |
| [marketing-leads-generation](marketing-leads-generation/SKILL.md) | Lead generation: ICP/offers, outbound cadences, LinkedIn, lead scoring |
| [marketing-paid-advertising](marketing-paid-advertising/SKILL.md) | Paid advertising: Meta Ads, Google Ads, campaign structure, bidding strategies |
| [marketing-product-analytics](marketing-product-analytics/SKILL.md) | Product analytics: event taxonomy, tracking plans, PostHog/Pendo/Amplitude, activation metrics, attribution |
| [marketing-seo-complete](marketing-seo-complete/SKILL.md) | Technical SEO: Core Web Vitals, crawlability, structured data, mobile |
| [marketing-social-media](marketing-social-media/SKILL.md) | Social media marketing: SMMA, paid social, content creation, offers |
| [marketing-visual-design](marketing-visual-design/SKILL.md) | Marketing visual design: ad creatives, social graphics, email visuals, presentations, AI tools |

---

## Data (3 skills)

| Skill | Description |
|-------|-------------|
| [data-analytics-engineering](data-analytics-engineering/SKILL.md) | Analytics engineering: dbt, metrics layer, semantic modeling, data quality |
| [data-lake-platform](data-lake-platform/SKILL.md) | Universal data lake/lakehouse: ingestion (dlt, Airbyte), transformation (SQLMesh, dbt), storage (Iceberg, Delta), query engines (ClickHouse, DuckDB, Doris), streaming (Kafka), orchestration, visualization (Metabase, Superset) |
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

## Quality (8 skills)

| Skill | Description |
|-------|-------------|
| [qa-agent-testing](qa-agent-testing/SKILL.md) | LLM agent/persona testing: 10-task test suites, 5 refusal edge cases, 6-dimension scoring rubric, regression protocols |
| [qa-api-testing-contracts](qa-api-testing-contracts/SKILL.md) | API contract testing: OpenAPI validation, consumer-driven contracts, schema evolution |
| [qa-debugging](qa-debugging/SKILL.md) | Debugging: logging, error tracking, profiling, root cause analysis |
| [qa-docs-coverage](qa-docs-coverage/SKILL.md) | Audit codebases for documentation gaps, generate coverage reports |
| [qa-observability](qa-observability/SKILL.md) | Observability: OpenTelemetry, tracing, metrics, SLO/SLI, APM |
| [qa-refactoring](qa-refactoring/SKILL.md) | Refactoring: code smells, technical debt, automated quality gates |
| [qa-resilience](qa-resilience/SKILL.md) | Resilience: circuit breakers, retries, bulkheads, chaos engineering |

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

## Testing (5 skills)

| Skill | Description |
|-------|-------------|
| [qa-testing-strategy](qa-testing-strategy/SKILL.md) | Test strategy: unit, integration, E2E, BDD, performance with Jest/Vitest/Playwright |
| [qa-testing-android](qa-testing-android/SKILL.md) | Android testing: Espresso, UIAutomator, Compose Testing, ADB automation, CI/CD |
| [qa-testing-ios](qa-testing-ios/SKILL.md) | iOS testing: Xcode simulator, XCTest, Swift Testing, UI automation |
| [qa-testing-mobile](qa-testing-mobile/SKILL.md) | Mobile testing: iOS + Android, device matrix, Appium, Detox |
| [qa-testing-playwright](qa-testing-playwright/SKILL.md) | E2E web testing: Playwright, page objects, authentication, CI/CD |

---

## Project-only (6 skills)

| Skill | Description |
|-------|-------------|
| [project-astrology-chinese](project-astrology-chinese/SKILL.md) | Expert Chinese astrology advisor for 12 Animal Zodiac, Five Elements, BaZi (project) |
| [project-astrology-numerology](project-astrology-numerology/SKILL.md) | Expert Western astrological advisor with natal charts, transits, synastry, and numerology (project) |
| [project-astrology-tarot-divination](project-astrology-tarot-divination/SKILL.md) | Expert tarot and divination advisor with spreads, card meanings, I Ching (project) |
| [project-astrology-vedic](project-astrology-vedic/SKILL.md) | Expert Vedic/Jyotish astrology advisor with dashas, nakshatras, doshas (project) |
| [project-qtax](project-qtax/SKILL.md) | QTax domain expertise (project-specific) |
| [project-real-estate-agent](project-real-estate-agent/SKILL.md) | Real estate agent assistant with property analysis and market insights (project) |

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
