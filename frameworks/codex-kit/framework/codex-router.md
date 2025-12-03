# Codex Router Rules

This document defines routing logic for Codex CLI to leverage Claude Code Kit skills and agents.

---

## Skills

Available skills from `.claude/skills/` (names match skill directories):

- **ai-agents**: Production-grade AI agent patterns with MCP, agentic RAG, orchestration, guardrails, and observability.
- **ai-llm**: LLM lifecycle covering prompt design, fine-tuning, evaluation, and data preparation.
- **ai-llm-inference**: LLM serving optimization (quantization, vLLM, TensorRT, batching, caching, perf tuning).
- **ai-ml-data-science**: E2E data science workflows from framing and EDA through features, modeling, and evaluation.
- **ai-ml-timeseries**: Time series forecasting, validation, feature engineering, and deployment patterns.
- **ai-mlops**: Production ML/LLM deployment, monitoring, drift detection, safety, and pipeline operations.
- **ai-prompts**: Operational prompt engineering for structured outputs, agents, RAG, and extractors.
- **ai-rag**: Retrieval, chunking, reranking, grounding, and hallucination control for RAG systems.
- **claude-code-agents**: Claude Code agent authoring (frontmatter, model routing, tools).
- **claude-code-commands**: Slash command design, command YAML scaffolding, and tool invocation patterns.
- **claude-code-hooks**: Pre/post run hooks, setup hooks, shell hooks, and automation glue.
- **claude-code-mcp**: MCP server design and configuration for Claude Code.
- **claude-code-project-memory**: CLAUDE.md project memory setup and hierarchy.
- **claude-code-skills**: Skill packaging, skill.yaml scaffolding, and meta-skill patterns.
- **document-docx**: Word document authoring and conversion workflows.
- **document-pdf**: PDF parsing, summarization, extraction, and analysis patterns.
- **document-pptx**: Slide deck planning, outlining, and PowerPoint/PPTX authoring.
- **document-xlsx**: Spreadsheet modeling, formulas, and Excel/xlsx data handling.
- **foundation-api-design**: Production API design for REST/GraphQL/gRPC (versioning, auth, error handling).
- **foundation-dependency-management**: Dependency and lockfile management across ecosystems.
- **foundation-documentation**: Docs-as-code patterns for READMEs, ADRs, changelogs, and guides.
- **foundation-git-commit-message**: Conventional commit generation and enforcement.
- **foundation-git-workflow**: Collaborative git workflows, branching, PR conventions, and reviews.
- **marketing-ai-search-optimization**: AEO/GEO/LLMO optimization for AI overviews and search surfaces.
- **marketing-leads-generation**: Lead gen systems for ICP/offers, outbound, landing fixes, and scoring.
- **marketing-seo-technical**: Technical SEO (schema, crawl budget, speed, sitemaps, indexing).
- **marketing-social-media**: Social media strategy, planning, and campaign execution.
- **ops-database-metabase**: Metabase configuration, modeling, dashboards, and SQL.
- **ops-database-sql**: SQL optimization, indexing, schema design, migrations, performance.
- **ops-devops-platform**: DevOps/IaC for Terraform, Kubernetes, CI/CD, and observability.
- **ops-document-automation**: Document automation pipelines, OCR, templating, and workflow orchestration.
- **product-management**: Product discovery, strategy, roadmaps, metrics, and AI/LLM product planning.
- **product-prd-for-agents**: PRD creation/validation tailored for agentic/LLM systems.
- **quality-code-refactoring**: Refactoring patterns and technical debt reduction.
- **quality-debugging-troubleshooting**: Debugging workflows, logs, root cause analysis.
- **quality-documentation-audit**: Documentation coverage audits and remediation plans.
- **quality-observability-performance**: Observability and performance engineering (metrics, traces, SLOs).
- **quality-resilience-patterns**: Resilience patterns (retries, circuit breakers, timeouts, graceful degradation).
- **software-architecture-design**: System design and architecture patterns for distributed systems.
- **software-backend**: Backend API design for REST/GraphQL, auth, DBs, testing, deployment.
- **software-code-review**: Code review patterns for correctness, security, performance, maintainability.
- **software-crypto-web3**: Smart contracts, DeFi/NFT patterns, audits, and multi-chain deployment.
- **software-frontend**: Modern frontend (Next.js/React/TypeScript/Tailwind) with accessibility/perf.
- **software-mobile**: Native/cross-platform mobile (Swift/Kotlin/React Native) architecture and delivery.
- **software-security-appsec**: AppSec patterns including OWASP Top 10 and supply chain security.
- **software-ui-ux-design**: UI/UX principles, design systems, accessibility, interaction design.
- **testing-automation**: Test strategy and automation across unit/integration/E2E/perf/regression.
- **testing-ios-simulator**: iOS simulator workflows (simctl/Xcode) for testing and automation.
- **testing-webapp-playwright**: Playwright-based web E2E testing and browser automation.
- **workflow-planning**: Workflow design, SOPs, task decomposition, and playbooks.

---

## Agents

Available agents from `.claude/agents/` (names match agent files):

- **ai-agents-builder**: AI agent architecture, implementation, testing, and optimization for production systems (uses `ai-agents`, `ai-rag`, `ai-prompts`).
- **backend-engineer**: Production-grade backend API development, database design, authentication, security, testing, and deployment (uses `software-backend`, `ai-rag`, `ops-database-sql`).
- **code-reviewer**: Code quality, security, and best practices review across languages and frameworks (uses `software-code-review`).
- **crypto-engineer**: Blockchain and Web3 development with smart contracts, DeFi protocols, NFTs, audits, and multi-chain deployment (uses `software-crypto-web3`).
- **data-scientist**: Exploratory analysis, feature engineering, modeling, deployment, and monitoring for data science projects (uses `ai-ml-data-science`, `ai-ml-timeseries`, `ai-mlops`).
- **devops-engineer**: Infrastructure as code, CI/CD pipelines, Kubernetes operations, observability, deployment strategies, and incident response (uses `ops-devops-platform`).
- **frontend-engineer**: Production-grade frontend development with Next.js/React/TypeScript, Tailwind/shadcn, accessibility, and performance (uses `software-frontend`, `software-ui-ux-design`).
- **llm-engineer**: LLM lifecycle management – data curation, fine-tuning, evaluation, optimization, deployment, and safety (uses `ai-llm`, `ai-llm-inference`, `ai-rag`, `ai-prompts`, `ai-mlops`).
- **mobile-engineer**: Production-grade mobile app development with Swift/Kotlin/React Native, including architecture, navigation, state, networking, persistence, and deployment (uses `software-mobile`).
- **prd-architect**: Product Requirements Document creation, validation, and technical specification for software projects (uses `product-prd-for-agents`, `foundation-documentation`).
- **product-manager**: Product strategy, roadmaps, user research, and metrics analysis (uses `product-management`, `foundation-documentation`).
- **prompt-engineer**: Operational prompt engineering for LLMs – design, optimize, and validate prompts for structured outputs, RAG, agents, and extractors (uses `ai-prompts`, `ai-llm`).
- **security-specialist**: Application security specialist covering OWASP Top 10 2025, zero trust, supply chain security, threat modeling, and secure design patterns (uses `software-security-appsec`, `ai-mlops`).
- **leads-strategist**: Lead generation specialist for ICP/offer clarity, outbound cadences, LinkedIn/social selling, landing optimization, lead scoring, and experiment cadence (uses `marketing-leads-generation`, `marketing-social-media`).
- **smm-strategist**: Social media marketing strategist for content, campaigns, and growth across major platforms (uses `marketing-social-media`).
- **sql-engineer**: SQL optimization, query tuning, database design, schema migrations, indexing strategies, and performance analysis (uses `ops-database-sql`).
- **system-architect**: System design, architecture review, and technical strategy for complex software systems (uses `software-architecture-design`, `quality-resilience-patterns`, `quality-observability-performance`).
- **test-architect**: Test strategy, planning, and coverage analysis across testing levels (uses `testing-automation`, `quality-code-refactoring`, `quality-debugging-troubleshooting`).

---

## Routing Logic

### Priority Order

1. **Explicit user override** - If user specifies `agent: X` or `skill: Y`, use exactly that
2. **Task-specific routing** - Match request type to specialized agent+skill
3. **Domain-specific routing** - Match technology stack to domain agent
4. **Default fallback** - Use general-purpose agent when no specific match

---

### Task-Specific Routes

**If the task is about AI agents, prompts, or agent system design:**
- **Agent**: ai-agents-builder
- **Skill**: ai-agents

**If the task is about prompt engineering or prompt optimization:**
- **Agent**: prompt-engineer
- **Skill**: ai-prompts

**If the task is about RAG pipelines or retrieval systems:**
- **Agent**: llm-engineer (if LLM-focused) OR ai-agents-builder (if agent-focused)
- **Skill**: ai-rag

**If the task is about LLM fine-tuning, evaluation, or data preparation:**
- **Agent**: llm-engineer
- **Skill**: ai-llm

**If the task is about LLM inference optimization or serving:**
- **Agent**: llm-engineer
- **Skill**: ai-llm-inference

**If the task is about ML/LLM deployment, monitoring, safety, or drift:**
- **Agent**: llm-engineer OR data-scientist (depending on model type)
- **Skill**: ai-mlops

**If the task is about PRD creation or validation:**
- **Agent**: prd-architect
- **Skill**: product-prd-for-agents

**If the task is about technical specifications:**
- **Agent**: prd-architect
- **Skill**: product-prd-for-agents

**If the task is about Claude Code configuration (agents/commands/hooks/MCP/memory/skills):**
- **Agent**: ai-agents-builder
- **Skill**: claude-code-agents OR claude-code-commands OR claude-code-hooks OR claude-code-mcp OR claude-code-project-memory OR claude-code-skills (pick best fit)

**If the task is about code review (general, multi-language, or security-focused):**
- **Agent**: code-reviewer
- **Skill**: software-code-review

**If the task is about high-level system design or architecture review:**
- **Agent**: system-architect
- **Skill**: software-architecture-design

**If the task is about product strategy, discovery, or roadmaps (including AI/LLM products):**
- **Agent**: product-manager
- **Skill**: product-management

**If the task is about test strategy, QA, or coverage planning:**
- **Agent**: test-architect
- **Skill**: testing-automation

**If the task is about technical SEO or AEO/LLMO:**
- **Agent**: leads-strategist
- **Skill**: marketing-seo-technical

**If the task is about document workflows (docx/pdf/pptx/xlsx) or automation:**
- **Agent**: ai-agents-builder
- **Skill**: document-docx OR document-pdf OR document-pptx OR document-xlsx OR ops-document-automation (pick best fit)

---

### Domain-Specific Routes (by Technology Stack)

**Backend API development (Node.js, Express, Prisma, PostgreSQL):**
- **Agent**: backend-engineer
- **Skill**: software-backend

**Frontend development (Next.js, React, TypeScript, Tailwind):**
- **Agent**: frontend-engineer
- **Skill**: software-frontend

**Mobile development (iOS/Swift or Android/Kotlin or React Native):**
- **Agent**: mobile-engineer
- **Skill**: software-mobile

**DevOps/Infrastructure (Terraform, Kubernetes, CI/CD):**
- **Agent**: devops-engineer
- **Skill**: ops-devops-platform

**Data Science/ML (EDA, modeling, feature engineering):**
- **Agent**: data-scientist
- **Skill**: ai-ml-data-science

**Time Series Forecasting:**
- **Agent**: data-scientist
- **Skill**: ai-ml-timeseries

**SQL optimization and database design:**
- **Agent**: sql-engineer
- **Skill**: ops-database-sql

**ML deployment, monitoring, or data ingestion:**
- **Agent**: data-scientist OR llm-engineer (depending on model type)
- **Skill**: ai-mlops

---

### Code Review Routes

**General or multi-language code review:**
- **Agent**: code-reviewer
- **Skill**: software-code-review

**Backend code review:**
- **Agent**: backend-engineer
- **Skill**: software-backend

**Frontend code review:**
- **Agent**: frontend-engineer
- **Skill**: software-frontend

**Mobile code review:**
- **Agent**: mobile-engineer
- **Skill**: software-mobile

**Security review (any stack):**
- **Agent**: [stack-specific agent]
- **Skill**: ai-mlops (if ML/LLM) OR software-security-appsec (app security) OR [stack-specific security skill]

**DevOps/infrastructure review:**
- **Agent**: devops-engineer
- **Skill**: ops-devops-platform

---

## Override Rules

- If the user specifies `agent: X`, use agent X regardless of task
- If the user specifies `skill: Y`, use skill Y regardless of task
- If the user specifies both `agent: X` and `skill: Y`, use that exact combination
- If the user says "no agent" or "no skill", skip that component

---

## Conflict Resolution

**When multiple agents could apply:**
- Choose the most specialized for the primary task
- Example: "Review Python ML API" → backend-engineer (API focus) over data-scientist (ML focus)

**When skill is missing:**
- Route to agent only, let agent handle without skill context
- Example: Backend question but no software-backend skill → use backend-engineer agent alone

**When agent is missing:**
- Use skill directly if it's self-contained and operational
- Example: Skill exists but no matching agent → provide skill patterns directly

**When both are missing:**
- Report "No matching route found" and suggest closest alternative
- Example: "Build iOS game" → suggest mobile-engineer with note about game-specific patterns

---

## Reference Paths

Router deployment:
- **Template storage**: `frameworks/codex-kit/` (this repository)
- **User deployment**: `.codex/` (user copies files here)

Referenced resources:
- **Skills**: `.claude/skills/` (where user copied Claude skills)
- **Agents**: `.claude/agents/` (where user copied Claude agents)
- **Commands**: `.claude/commands/` (where user copied Claude commands)

---

## Usage Notes

- Router is invoked at the start of each Codex session
- User pastes `codex-mega-prompt.txt` into Codex CLI
- Codex outputs routing decision on first line of every response
- User can override routing with explicit `agent: X | skill: Y` syntax
- Router references `.claude/` paths in the same repository
