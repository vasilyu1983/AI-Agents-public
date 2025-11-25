# Codex Router Rules

This document defines routing logic for Codex CLI to leverage Claude Code Kit skills and agents.

---

## Skills

Available skills from `.claude/skills/` (names match skill directories):

- **ai-agents-development**: Production-grade AI agent patterns with MCP integration, agentic RAG, handoff orchestration, multi-layer guardrails, and observability.
- **ai-llm-development**: LLM development workflows covering prompt engineering, parameter-efficient fine-tuning, evaluation, and dataset preparation.
- **ai-llm-engineering**: Operational hub for LLM engineering with templates, patterns, and checklists for building, evaluating, deploying, and optimizing LLM-powered systems.
- **ai-llm-ops-inference**: LLM serving optimization (quantization, vLLM, TensorRT, batching, caching, throughput/latency tuning).
- **ai-llm-rag-engineering**: RAG system design including chunking, retrieval, reranking, grounding, and hallucination control.
- **ai-llm-search-retrieval**: Modern search and retrieval patterns for hybrid, semantic, and vector search systems.
- **ai-ml-data-science**: End-to-end data science workflows from problem framing and EDA through feature engineering, modeling, and evaluation.
- **ai-ml-ops-production**: Production ML workflows for deployment, monitoring, drift detection, and automated retraining.
- **ai-ml-ops-security**: ML/LLM security, privacy, and safety patterns including prompt-injection defenses and multi-layer guardrails.
- **ai-ml-timeseries**: Time series forecasting, temporal validation, feature engineering, and deployment patterns.
- **ai-prompt-engineering**: Operational prompt engineering patterns and validation flows for prompts, RAG, agents, and extractors.
- **codebase-documentation-audit**: Systematically audit codebases for documentation gaps, generate coverage reports, and create missing documentation using foundation-documentation templates.
- **foundation-api-design**: Production API design for REST, GraphQL, and gRPC including versioning, authentication, pagination, and error handling.
- **foundation-dependency-management**: Dependency management and update strategies across ecosystems (npm, pip, cargo, maven, and others).
- **foundation-documentation**: Technical documentation patterns for READMEs, ADRs, API docs, changelogs, and docs-as-code workflows.
- **foundation-git-workflow**: Collaborative Git workflows, branching strategies, PR conventions, and code review best practices.
- **git-commit-message**: Auto-generates conventional commit messages from git diffs with tiered format enforcement (feat/fix/perf = detailed, refactor/test = standard, docs/chore = minimal).
- **marketing-ai-search-optimization**: AI search engine optimization (AEO/GEO/LLMO) for ChatGPT, Perplexity, Claude, Gemini, and Google AI Overviews with technical setup, content strategies, and measurement frameworks.
- **marketing-leads-generation**: Operational lead generation systems for ICP/offers, outbound cadences, LinkedIn/social selling, landing fixes, lead scoring, analytics, and experiment cadence with compliance hygiene.
- **marketing-social-media**: Social media marketing strategy, content planning, and campaign execution patterns.
- **ops-database-metabase**: Metabase BI platform configuration, dashboard design, SQL queries, data visualization, and analytics workflows.
- **ops-database-sql**: Production SQL optimization, indexing, schema design, migrations, and operational best practices.
- **ops-devops-platform**: DevOps and platform engineering for infrastructure as code, Kubernetes, CI/CD, and observability.
- **ops-document-automation**: Document generation automation with templates, mail merge, PDF creation, and workflow integration.
- **product-management**: Product discovery, strategy, AI/LLM products, roadmaps, and metrics.
- **product-prd-development**: PRD creation, validation, and technical specification workflows.
- **quality-code-refactoring**: Systematic refactoring, code quality improvements, and technical debt management.
- **quality-debugging-troubleshooting**: Debugging workflows, troubleshooting practices, logging, and root cause analysis.
- **quality-observability-performance**: Observability and performance engineering with traces, metrics, logs, and SLOs.
- **quality-resilience-patterns**: Resilience patterns including retries, circuit breakers, timeouts, and graceful degradation.
- **software-architecture-design**: System design, architecture patterns, and scalability tradeoffs for distributed systems.
- **software-backend**: Backend API development patterns for REST/GraphQL, databases, authentication, security, testing, and deployment.
- **software-code-review**: Structured code review checklists and patterns for correctness, security, performance, and maintainability.
- **software-crypto-web3**: Blockchain and Web3 development patterns for smart contracts, DeFi, NFTs, and security.
- **software-frontend**: Modern frontend development with Next.js, React, TypeScript, Tailwind CSS, and accessibility best practices.
- **software-mobile**: Native and cross-platform mobile development with Swift, Kotlin, and React Native.
- **software-security-appsec**: Application security and AppSec patterns including OWASP Top 10 and supply-chain security.
- **software-testing-automation**: Test strategy and automation across unit, integration, end-to-end, performance, and regression testing.
- **software-ui-ux-design**: UI/UX principles, design systems, accessibility, and interaction design.

---

## Agents

Available agents from `.claude/agents/` (names match agent files):

- **ai-agents-builder**: AI agent architecture, implementation, testing, and optimization for production systems (uses `ai-agents-development`, `ai-llm-rag-engineering`, `ai-prompt-engineering`).
- **backend-engineer**: Production-grade backend API development, database design, authentication, security, testing, and deployment (uses `software-backend`, `ai-llm-search-retrieval`, `ops-database-sql`).
- **code-reviewer**: Code quality, security, and best practices review across languages and frameworks (uses `software-code-review`).
- **crypto-engineer**: Blockchain and Web3 development with smart contracts, DeFi protocols, NFTs, audits, and multi-chain deployment (uses `software-crypto-web3`).
- **data-scientist**: Exploratory analysis, feature engineering, modeling, deployment, and monitoring for data science projects (uses `ai-ml-data-science`, `ai-ml-timeseries`, `ai-ml-ops-production`).
- **devops-engineer**: Infrastructure as code, CI/CD pipelines, Kubernetes operations, observability, deployment strategies, and incident response (uses `ops-devops-platform`).
- **frontend-engineer**: Production-grade frontend development with Next.js/React/TypeScript, Tailwind/shadcn, accessibility, and performance (uses `software-frontend`, `software-ui-ux-design`).
- **llm-engineer**: LLM lifecycle management – data curation, fine-tuning, evaluation, optimization, deployment, and safety (uses `ai-llm-development`, `ai-llm-engineering`, `ai-llm-ops-inference`, `ai-llm-rag-engineering`, `ai-llm-search-retrieval`, `ai-ml-ops-security`).
- **mobile-engineer**: Production-grade mobile app development with Swift/Kotlin/React Native, including architecture, navigation, state, networking, persistence, and deployment (uses `software-mobile`).
- **prd-architect**: Product Requirements Document creation, validation, and technical specification for software projects (uses `product-prd-development`, `foundation-documentation`).
- **product-manager**: Product strategy, roadmaps, user research, and metrics analysis (uses `product-management`, `foundation-documentation`).
- **prompt-engineer**: Operational prompt engineering for LLMs – design, optimize, and validate prompts for structured outputs, RAG, agents, and extractors (uses `ai-prompt-engineering`, `ai-llm-development`).
- **security-specialist**: Application security specialist covering OWASP Top 10 2025, zero trust, supply chain security, threat modeling, and secure design patterns (uses `software-security-appsec`, `ai-ml-ops-security`).
- **leads-strategist**: Lead generation specialist for ICP/offer clarity, outbound cadences, LinkedIn/social selling, landing optimization, lead scoring, and experiment cadence (uses `marketing-leads-generation`, `marketing-social-media`).
- **smm-strategist**: Social media marketing strategist for content, campaigns, and growth across major platforms (uses `marketing-social-media`).
- **sql-engineer**: SQL optimization, query tuning, database design, schema migrations, indexing strategies, and performance analysis (uses `ops-database-sql`).
- **system-architect**: System design, architecture review, and technical strategy for complex software systems (uses `software-architecture-design`, `quality-resilience-patterns`, `quality-observability-performance`).
- **test-architect**: Test strategy, planning, and coverage analysis across testing levels (uses `software-testing-automation`, `quality-code-refactoring`, `quality-debugging-troubleshooting`).

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
- **Skill**: ai-agents-development

**If the task is about prompt engineering or prompt optimization:**
- **Agent**: prompt-engineer
- **Skill**: ai-prompt-engineering

**If the task is about RAG pipelines or retrieval systems:**
- **Agent**: llm-engineer (if LLM-focused) OR ai-agents-builder (if agent-focused)
- **Skill**: ai-llm-rag-engineering

**If the task is about search systems (non-RAG):**
- **Agent**: backend-engineer
- **Skill**: ai-llm-search-retrieval

**If the task is about LLM fine-tuning, evaluation, or data preparation:**
- **Agent**: llm-engineer
- **Skills**: ai-llm-development, ai-llm-engineering

**If the task is about LLM inference optimization or serving:**
- **Agent**: llm-engineer
- **Skill**: ai-llm-ops-inference

**If the task is about ML security, privacy, or safety:**
- **Agent**: llm-engineer OR data-scientist (depending on ML type)
- **Skill**: ai-ml-ops-security

**If the task is about PRD creation or validation:**
- **Agent**: prd-architect
- **Skill**: product-prd-development

**If the task is about technical specifications:**
- **Agent**: prd-architect
- **Skill**: product-prd-development

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
- **Skill**: software-testing-automation

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
- **Skill**: ai-ml-ops-production

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
- **Skill**: ai-ml-ops-security (if ML/LLM) OR [stack-specific skill with security focus]

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
