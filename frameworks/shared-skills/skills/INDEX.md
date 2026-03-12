# Skills Index

This directory contains 62 production-grade skills organized by domain and prefix family.

**Total Skills:** 62
**Last Updated:** 2026-03-12

**Note:** Skills are defined by `SKILL.md`. Avoid adding `README.md` inside skill folders.

---

## Prefix Policy

Prefixes encode the skill's primary operating domain.

| Prefix | Use For |
|--------|---------|
| `agents-` | Agent runtime building blocks and orchestration |
| `ai-` | AI/ML methods, systems, inference, prompting, RAG |
| `software-` | Application and platform engineering domains |
| `dev-` | Developer workflow, engineering process, repo/system-of-work practices |
| `data-` | Analytics engineering, BI, SQL, data platforms |
| `qa-` | Testing, reliability, debugging, observability, refactoring quality |
| `docs-` | Documentation systems, PRDs, codebase docs, doc governance |
| `document-` | File-format operations on `.pdf`, `.docx`, `.xlsx`, `.pptx` |
| `ops-` | Infrastructure and platform operations |
| `product-` | Reusable product strategy or product-risk skills |

Naming rule:
- Use `software-*` for what teams build.
- Use `dev-*` for how engineers work.
- Avoid introducing new singleton prefixes unless you are intentionally creating a new family.

---

## Quick Reference

| Domain | Skills | Description |
|--------|--------|-------------|
| [AI/ML](#aiml-8-skills) | 8 | LLMs, agents, RAG, MLOps, data science, inference |
| [Agents](#agents-6-skills) | 6 | Subagents, hooks, MCP, skills, memory, swarm orchestration |
| [Data](#data-4-skills) | 4 | Data lake/lakehouse, SQL optimization, analytics engineering, Metabase |
| [Documentation](#documentation-2-skills) | 2 | AI-friendly PRDs, codebase docs |
| [Document Formats](#document-formats-4-skills) | 4 | PDF, DOCX, XLSX, PPTX file processing |
| [Developer Tools](#developer-tools-8-skills) | 8 | API design, AI coding metrics, dependencies, context engineering, git workflow, git commit messages, dev planning, structured logs |
| [Operations](#operations-2-skills) | 2 | DevOps platform engineering, NUKE CI/CD |
| [Product](#product-2-skills) | 2 | Product management, help center design |
| [QA](#qa-13-skills) | 13 | Testing (8), quality (5): debugging, observability, resilience, refactoring, docs coverage |
| [Software](#software-13-skills) | 13 | Frontend, backend, C# backend, payments, mobile, architecture, security, UX research, clean code |

---

## AI/ML (8 skills)

| Skill | Description |
|-------|-------------|
| [ai-agents](ai-agents/SKILL.md) | Production-grade AI agent patterns with MCP integration, agentic RAG, handoff orchestration, multi-layer guardrails |
| [ai-llm](ai-llm/SKILL.md) | Complete LLM development: strategy selection, dataset design, PEFT/LoRA fine-tuning, evaluation workflows |
| [ai-llm-inference](ai-llm-inference/SKILL.md) | LLM inference optimization: serving, quantization, batching, caching, benchmarking |
| [ai-ml-data-science](ai-ml-data-science/SKILL.md) | ML workflows: EDA, feature engineering, model evaluation, data transformation |
| [ai-ml-timeseries](ai-ml-timeseries/SKILL.md) | Time series modeling patterns and forecasting strategies |
| [ai-mlops](ai-mlops/SKILL.md) | ML operations: data ingestion, drift detection, monitoring, ML security, privacy, governance |
| [ai-prompt-engineering](ai-prompt-engineering/SKILL.md) | Operational prompt engineering patterns, templates, and validation flows |
| [ai-rag](ai-rag/SKILL.md) | RAG and search engineering: chunking, hybrid retrieval, reranking, evaluation frameworks |

---

## Agents (6 skills)

| Skill | Description |
|-------|-------------|
| [agents-subagents](agents-subagents/SKILL.md) | Create Claude Code agents with YAML frontmatter, tool selection, model specification |
| [agents-hooks](agents-hooks/SKILL.md) | Event-driven hooks for automation: PreToolUse, PostToolUse, Stop events |
| [agents-mcp](agents-mcp/SKILL.md) | Build Model Context Protocol (MCP) servers for database, filesystem, API connections |
| [agents-project-memory](agents-project-memory/SKILL.md) | Configure CLAUDE.md/AGENTS.md/CODEX.md for large codebases (100K-1M LOC), hierarchical docs |
| [agents-skills](agents-skills/SKILL.md) | Reference for creating skills with SKILL.md structure, references/, progressive disclosure |
| [agents-swarm-orchestration](agents-swarm-orchestration/SKILL.md) | Coordinate parallel subagents via dependency-aware dispatch waves (Claude Code + Codex) |

---

## Documentation (2 skills)

| Skill | Description |
|-------|-------------|
| [docs-ai-prd](docs-ai-prd/SKILL.md) | Write PRDs, specs, briefs, and project context for AI coding agents (Claude Code, Cursor, Custom GPTs) |
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

## Developer Tools (8 skills)

| Skill | Description |
|-------|-------------|
| [dev-ai-coding-metrics](dev-ai-coding-metrics/SKILL.md) | Measure AI coding agent impact: adoption tracking, DORA/SPACE for AI teams, ROI frameworks, DX surveys, benchmarking |
| [dev-api-design](dev-api-design/SKILL.md) | REST, GraphQL, gRPC patterns: versioning, auth, rate limiting, pagination |
| [dev-context-engineering](dev-context-engineering/SKILL.md) | Context-driven development systems: AGENTS.md-first workflows, repo maturity, multi-repo coordination |
| [dev-dependency-management](dev-dependency-management/SKILL.md) | Package management: npm, pip, cargo, maven, lockfiles, security scanning |
| [dev-workflow-planning](dev-workflow-planning/SKILL.md) | Development workflows: brainstorm, write-plan, execute-plan patterns |
| [dev-git-commit-message](dev-git-commit-message/SKILL.md) | Auto-generate conventional commit messages from git diffs |
| [dev-git-workflow](dev-git-workflow/SKILL.md) | Git collaboration: branching strategies, PR workflows, commit conventions |
| [dev-structured-logs](dev-structured-logs/SKILL.md) | Structured logging migration: ILogger/Serilog rewrites, JSON sink config, .NET logging scopes |

---

## Data (4 skills)

| Skill | Description |
|-------|-------------|
| [data-analytics-engineering](data-analytics-engineering/SKILL.md) | Analytics engineering: dbt, metrics layer, semantic modeling, data quality |
| [data-lake-platform](data-lake-platform/SKILL.md) | Universal data lake/lakehouse: ingestion, transformation, storage, query engines |
| [data-metabase](data-metabase/SKILL.md) | Metabase API automation: API key auth, create/edit reports, dashboards |
| [data-sql-optimization](data-sql-optimization/SKILL.md) | OLTP SQL optimization: EXPLAIN ANALYZE, indexing, PostgreSQL/MySQL/Oracle |

---

## Operations (2 skills)

| Skill | Description |
|-------|-------------|
| [ops-devops-platform](ops-devops-platform/SKILL.md) | DevOps: Kubernetes, GitOps, SRE, CI/CD security, AWS/GCP/Azure, Terraform |
| [ops-nuke-cicd](ops-nuke-cicd/SKILL.md) | NUKE build pipelines: .NET CI/CD, target graphs, coverage/test reports, Docker image publishing |

---

## Product (2 skills)

| Skill | Description |
|-------|-------------|
| [product-management](product-management/SKILL.md) | Product management: discovery, OKRs, roadmapping, metrics, strategy |
| [product-help-center](product-help-center/SKILL.md) | Help center & knowledge base: AI-first support, taxonomy, self-service optimization |

---

## QA (13 skills)

### Testing (8)

| Skill | Description |
|-------|-------------|
| [qa-testing-strategy](qa-testing-strategy/SKILL.md) | Test strategy: unit, integration, E2E, BDD, performance with Jest/Vitest/Playwright |
| [qa-testing-playwright](qa-testing-playwright/SKILL.md) | E2E web testing: Playwright, page objects, authentication, CI/CD |
| [qa-testing-ios](qa-testing-ios/SKILL.md) | iOS testing: Xcode simulator, XCTest, Swift Testing, UI automation |
| [qa-testing-android](qa-testing-android/SKILL.md) | Android testing: Espresso, UIAutomator, Compose Testing, ADB automation |
| [qa-testing-mobile](qa-testing-mobile/SKILL.md) | Mobile testing: iOS + Android, device matrix, Appium, Detox |
| [qa-testing-nunit](qa-testing-nunit/SKILL.md) | C# testing: NUnit fixtures, WireMock, Testcontainers, API/component/integration scenarios |
| [qa-api-testing-contracts](qa-api-testing-contracts/SKILL.md) | API contract testing: OpenAPI validation, consumer-driven contracts |
| [qa-agent-testing](qa-agent-testing/SKILL.md) | QA harness for agentic systems: scenario suites, determinism controls, scoring rubrics |

### Quality (5)

| Skill | Description |
|-------|-------------|
| [qa-debugging](qa-debugging/SKILL.md) | Debugging: logging, error tracking, profiling, root cause analysis |
| [qa-observability](qa-observability/SKILL.md) | Observability: OpenTelemetry, tracing, metrics, SLO/SLI, APM |
| [qa-resilience](qa-resilience/SKILL.md) | Resilience: circuit breakers, retries, bulkheads, chaos engineering |
| [qa-refactoring](qa-refactoring/SKILL.md) | Refactoring: code smells, technical debt, automated quality gates |
| [qa-docs-coverage](qa-docs-coverage/SKILL.md) | Audit codebases for documentation gaps, generate coverage reports |

---

## Software (13 skills)

| Skill | Description |
|-------|-------------|
| [software-architecture-design](software-architecture-design/SKILL.md) | System design: microservices, event-driven, CQRS, modular monoliths |
| [software-backend](software-backend/SKILL.md) | Backend API: Node.js/Python/Rust/Go, Prisma ORM, PostgreSQL, GraphQL |
| [software-payments](software-payments/SKILL.md) | Payments & billing: Stripe, Adyen, GoCardless, Mollie, Paddle, LemonSqueezy, Chargebee, Recurly, Lago, subscriptions, webhooks |
| [software-clean-code-standard](software-clean-code-standard/SKILL.md) | Clean code standard: `CC-*` rule IDs, governance, language-agnostic rules |
| [software-code-review](software-code-review/SKILL.md) | Code review: checklists, templates for correctness, security, performance |
| [software-csharp-backend](software-csharp-backend/SKILL.md) | C#/.NET backend: service layers, data access, resilience, observability, anti-pattern detection |
| [software-crypto-web3](software-crypto-web3/SKILL.md) | Blockchain: Solidity (EVM), Rust (Solana), CosmWasm, DeFi, security |
| [software-frontend](software-frontend/SKILL.md) | Frontend: Next.js 16, React, TypeScript, Tailwind, shadcn/ui |
| [software-localisation](software-localisation/SKILL.md) | Localization: i18n/l10n, ICU message format, RTL, translation workflows |
| [software-mobile](software-mobile/SKILL.md) | Mobile: Swift (iOS), Kotlin (Android), React Native, WebView patterns |
| [software-security-appsec](software-security-appsec/SKILL.md) | Application security: OWASP Top 10:2025, zero trust, authentication |
| [software-ui-ux-design](software-ui-ux-design/SKILL.md) | UI/UX: usability heuristics, accessibility (WCAG 2.2 + 3.0 preview), design systems |
| [software-ux-research](software-ux-research/SKILL.md) | UX research: JTBD, Kano Model, journey mapping, heuristic evaluation |

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

### Adding New Skills

See [agents-skills](agents-skills/SKILL.md) for the complete guide to creating new skills.

---

## Contributing

1. Follow the standard skill structure
2. Include SKILL.md with proper frontmatter
3. Add data/sources.json with curated references
4. Create references/ with operational guides
5. Add assets/ with reusable starting points
