# Gemini Router Rules

This document defines routing logic for Gemini CLI to leverage Claude Code Kit skills and agents via the `/claude-router` command.

---

## Skills

Available skills from `.claude/skills/` (61 skills organized by domain):

### AI/ML Skills (8)

- **ai-agents**: Production-grade AI agent patterns with MCP, agentic RAG, orchestration, guardrails, and observability.
- **ai-llm**: LLM lifecycle covering prompt design, fine-tuning, evaluation, and data preparation.
- **ai-llm-inference**: LLM serving optimization (quantization, vLLM, TensorRT, batching, caching, perf tuning).
- **ai-ml-data-science**: E2E data science workflows from framing and EDA through features, modeling, and evaluation.
- **ai-ml-timeseries**: Time series forecasting, validation, feature engineering, and deployment patterns.
- **ai-mlops**: Production ML/LLM deployment, monitoring, drift detection, safety, and pipeline operations.
- **ai-prompt-engineering**: Operational prompt engineering for structured outputs, agents, RAG, and extractors.
- **ai-rag**: Retrieval, chunking, reranking, grounding, and hallucination control for RAG systems.

### Claude Code Skills (6)

- **claude-code-agents**: Claude Code agent authoring (frontmatter, model routing, tools).
- **claude-code-commands**: Slash command design, command YAML scaffolding, and tool invocation patterns.
- **claude-code-hooks**: Pre/post run hooks, setup hooks, shell hooks, and automation glue.
- **claude-code-mcp**: MCP server design and configuration for Claude Code.
- **claude-code-project-memory**: CLAUDE.md project memory setup and hierarchy.
- **claude-code-skills**: Skill packaging, skill.yaml scaffolding, and meta-skill patterns.

### Software Engineering Skills (9)

- **software-frontend**: Modern frontend (Next.js/React/TypeScript/Tailwind) with accessibility/perf.
- **software-backend**: Backend API design for REST/GraphQL, auth, DBs, testing, deployment.
- **software-mobile**: Native/cross-platform mobile (Swift/Kotlin/React Native) architecture and delivery.
- **software-architecture-design**: System design and architecture patterns for distributed systems.
- **software-code-review**: Code review patterns for correctness, security, performance, maintainability.
- **software-security-appsec**: AppSec patterns including OWASP Top 10 and supply chain security.
- **software-crypto-web3**: Smart contracts, DeFi/NFT patterns, audits, and multi-chain deployment.
- **software-ui-ux-design**: UI/UX principles, design systems, accessibility, interaction design.
- **software-ux-research**: User research, usability testing, and UX methodologies.

### QA & Testing Skills (9)

- **qa-testing-strategy**: Test strategy and automation across unit/integration/E2E/perf/regression.
- **qa-testing-playwright**: Playwright-based web E2E testing and browser automation.
- **qa-testing-ios**: iOS simulator workflows (simctl/Xcode) for testing and automation.
- **qa-agent-testing**: QA harness for LLM agents/personas with test suites, scoring rubrics, regression protocols.
- **qa-debugging**: Debugging workflows, logs, root cause analysis.
- **qa-observability**: Observability and performance engineering (metrics, traces, SLOs).
- **qa-resilience**: Resilience patterns (retries, circuit breakers, timeouts, graceful degradation).
- **qa-refactoring**: Refactoring patterns and technical debt reduction.
- **qa-docs-coverage**: Documentation coverage audits and remediation plans.

### Data & Operations Skills (3)

- **data-sql-optimization**: SQL optimization, indexing, schema design, migrations, performance.
- **data-lake-platform**: Universal data lake/lakehouse with dlt, SQLMesh, Iceberg, DuckDB, ClickHouse.
- **ops-devops-platform**: DevOps/IaC for Terraform, Kubernetes, CI/CD, and observability.

### Development Workflow Skills (4)

- **dev-api-design**: Production API design for REST/GraphQL/gRPC (versioning, auth, error handling).
- **dev-dependency-management**: Dependency and lockfile management across ecosystems.
- **dev-workflow-planning**: Workflow design, SOPs, task decomposition, and playbooks.
- **git-workflow**: Collaborative git workflows, branching, PR conventions, and reviews.

### Git Skills (1)

- **git-commit-message**: Conventional commit generation with tiered format enforcement.

### Documentation Skills (2)

- **docs-codebase**: Docs-as-code patterns for READMEs, ADRs, changelogs, and guides.
- **docs-ai-prd**: PRD creation/validation tailored for agentic/LLM systems.

### Document Processing Skills (4)

- **document-pdf**: PDF parsing, summarization, extraction, and analysis patterns.
- **document-docx**: Word document authoring and conversion workflows.
- **document-xlsx**: Spreadsheet modeling, formulas, and Excel/xlsx data handling.
- **document-pptx**: Slide deck planning, outlining, and PowerPoint/PPTX authoring.

### Marketing Skills (4)

- **marketing-ai-search-optimization**: AEO/GEO/LLMO optimization for AI overviews and search surfaces.
- **marketing-leads-generation**: Lead gen systems for ICP/offers, outbound, landing fixes, and scoring.
- **marketing-seo-complete**: Technical SEO (schema, crawl budget, speed, sitemaps, indexing).
- **marketing-social-media**: Social media strategy, planning, and campaign execution.

### Product Management Skills (1)

- **product-management**: Product discovery, strategy, roadmaps, metrics, and AI/LLM product planning.

### Startup Ecosystem Skills (9)

- **startup-mega-router**: Master orchestrator routing startup problems through all skills for comprehensive analysis.
- **startup-idea-validation**: 9-dimension validation framework for GO/NO-GO decisions on ideas.
- **startup-review-mining**: Pain point extraction from reviews (G2, Capterra, Reddit, App Store, etc.).
- **startup-trend-prediction**: 2-3yr lookback to predict 1-2yr ahead using pattern recognition and cycles.
- **startup-competitive-analysis**: Competitive intelligence, market mapping, and strategic positioning.
- **startup-business-models**: Revenue model design, unit economics, pricing strategy, monetization.
- **startup-go-to-market**: GTM strategy, channel selection, launch planning, and market entry.
- **startup-fundraising**: Fundraising strategy, pitch preparation, investor relations, capital raising.
- **agent-fleet-operations**: Managing 50+ AI agents as services, fleet orchestration, monitoring, scaling.

---

## Agents

Available agents from `.claude/agents/` (18 agents):

- **ai-agents-builder**: AI agent architecture, implementation, testing, and optimization for production systems (uses `ai-agents`, `ai-rag`, `ai-prompt-engineering`, `agent-fleet-operations`).
- **backend-engineer**: Production-grade backend API development, database design, authentication, security, testing, and deployment (uses `software-backend`, `ai-rag`, `data-sql-optimization`).
- **code-reviewer**: Code quality, security, and best practices review across languages and frameworks (uses `software-code-review`).
- **crypto-engineer**: Blockchain and Web3 development with smart contracts, DeFi protocols, NFTs, audits, and multi-chain deployment (uses `software-crypto-web3`).
- **data-scientist**: Exploratory analysis, feature engineering, modeling, deployment, and monitoring for data science projects (uses `ai-ml-data-science`, `ai-ml-timeseries`, `ai-mlops`).
- **devops-engineer**: Infrastructure as code, CI/CD pipelines, Kubernetes operations, observability, deployment strategies, and incident response (uses `ops-devops-platform`).
- **frontend-engineer**: Production-grade frontend development with Next.js/React/TypeScript, Tailwind/shadcn, accessibility, and performance (uses `software-frontend`, `software-ui-ux-design`).
- **llm-engineer**: LLM lifecycle management – data curation, fine-tuning, evaluation, optimization, deployment, and safety (uses `ai-llm`, `ai-llm-inference`, `ai-rag`, `ai-prompt-engineering`, `ai-mlops`).
- **mobile-engineer**: Production-grade mobile app development with Swift/Kotlin/React Native, including architecture, navigation, state, networking, persistence, and deployment (uses `software-mobile`).
- **prd-architect**: Product Requirements Document creation, validation, and technical specification for software projects (uses `docs-ai-prd`, `docs-codebase`).
- **product-manager**: Product strategy, roadmaps, user research, metrics analysis, and startup advisory (uses `product-management`, `docs-codebase`, startup skills).
- **prompt-engineer**: Operational prompt engineering for LLMs – design, optimize, and validate prompts for structured outputs, RAG, agents, and extractors (uses `ai-prompt-engineering`, `ai-llm`).
- **security-specialist**: Application security specialist covering OWASP Top 10 2025, zero trust, supply chain security, threat modeling, and secure design patterns (uses `software-security-appsec`, `ai-mlops`).
- **leads-strategist**: Lead generation specialist for ICP/offer clarity, outbound cadences, LinkedIn/social selling, landing optimization, lead scoring, and GTM execution (uses `marketing-leads-generation`, `marketing-social-media`, `marketing-seo-complete`, `startup-go-to-market`).
- **smm-strategist**: Social media marketing strategist for content, campaigns, and growth across major platforms (uses `marketing-social-media`).
- **sql-engineer**: SQL optimization, query tuning, database design, schema migrations, indexing strategies, and performance analysis (uses `data-sql-optimization`).
- **system-architect**: System design, architecture review, and technical strategy for complex software systems (uses `software-architecture-design`, `qa-resilience`, `qa-observability`).
- **test-architect**: Test strategy, planning, and coverage analysis across testing levels (uses `qa-testing-strategy`, `qa-testing-playwright`, `qa-testing-ios`, `qa-agent-testing`, `qa-refactoring`, `qa-debugging`).

---

## Routing Priority

The router applies a 5-level priority system:

1. **Explicit user override**
   - User specifies `agent: X` and/or `skill: Y` in the prompt.
   - Router must respect these hints even if another route might be better.

2. **Task-specific routing**
   - Match the request type to a specialized agent+skill pair.
   - Examples: PRD work, RAG design, SQL optimization, prompt engineering.

3. **Startup-specific routing**
   - Match startup-related requests to product-manager or leads-strategist with appropriate startup skill.
   - Examples: idea validation, competitive analysis, fundraising, GTM strategy.

4. **Domain-specific routing**
   - Match the technology stack or domain to an agent.
   - Examples: backend vs frontend vs mobile vs data-science vs infra.

5. **Default fallback**
   - Use the most general agent when no specific match is found.
   - Example: route general software questions to `backend-engineer` or `ai-agents-builder` depending on focus.

---

## Task-Specific Routes (Examples)

These examples mirror the test cases in `router-tests.md`.

**AI agent architecture and RAG:**
- Agent: `ai-agents-builder`
- Skill: `ai-agents`

**Backend API development (REST/GraphQL, auth, PostgreSQL):**
- Agent: `backend-engineer`
- Skill: `software-backend`

**Frontend development (Next.js, React, TypeScript, Tailwind):**
- Agent: `frontend-engineer`
- Skill: `software-frontend`

**Mobile development (iOS/Swift, Android/Kotlin, React Native):**
- Agent: `mobile-engineer`
- Skill: `software-mobile`

**DevOps/Infrastructure (Terraform, Kubernetes, CI/CD):**
- Agent: `devops-engineer`
- Skill: `ops-devops-platform`

**Data science and ML workflows (EDA, modeling, feature engineering):**
- Agent: `data-scientist`
- Skill: `ai-ml-data-science`

**Time series forecasting:**
- Agent: `data-scientist`
- Skill: `ai-ml-timeseries`

**SQL optimization and database design:**
- Agent: `sql-engineer`
- Skill: `data-sql-optimization`

**ML deployment, monitoring, and data ingestion:**
- Agent: `data-scientist` or `llm-engineer` (depending on model type)
- Skill: `ai-mlops`

**RAG pipeline design:**
- Agent: `llm-engineer`
- Skill: `ai-rag`

**Prompt engineering and structured outputs:**
- Agent: `prompt-engineer`
- Skill: `ai-prompt-engineering`

**PRD creation and validation:**
- Agent: `prd-architect`
- Skill: `docs-ai-prd`

**LLM inference optimization (vLLM, quantization, batching):**
- Agent: `llm-engineer`
- Skill: `ai-llm-inference`

**ML/LLM security and prompt-injection defense:**
- Agent: `llm-engineer`
- Skill: `ai-mlops`

**Technical SEO and AI search optimization:**
- Agent: `leads-strategist`
- Skill: `marketing-seo-complete`

**Claude Code configuration (agents/commands/hooks/MCP/memory/skills):**
- Agent: `ai-agents-builder`
- Skill: `claude-code-agents` or related Claude Code meta skill (pick best fit)

**Document workflows (docx/pdf/pptx/xlsx):**
- Agent: `ai-agents-builder`
- Skill: `document-docx` / `document-pdf` / `document-pptx` / `document-xlsx` (pick best fit)

**Playwright/web E2E automation:**
- Agent: `test-architect`
- Skill: `qa-testing-playwright`

**LLM agent/persona QA testing:**
- Agent: `test-architect`
- Skill: `qa-agent-testing`

**Agent fleet management at scale:**
- Agent: `ai-agents-builder`
- Skill: `agent-fleet-operations`

---

## Startup-Specific Routes

**If the task is about validating a startup idea:**
- **Agent**: product-manager
- **Skill**: startup-idea-validation

**If the task is about pain point extraction from reviews:**
- **Agent**: product-manager
- **Skill**: startup-review-mining

**If the task is about market trends or timing analysis:**
- **Agent**: product-manager
- **Skill**: startup-trend-prediction

**If the task is about competitive analysis or positioning:**
- **Agent**: product-manager
- **Skill**: startup-competitive-analysis

**If the task is about revenue models, pricing, or unit economics:**
- **Agent**: product-manager
- **Skill**: startup-business-models

**If the task is about GTM strategy or launch planning:**
- **Agent**: leads-strategist
- **Skill**: startup-go-to-market

**If the task is about fundraising, pitch decks, or investors:**
- **Agent**: product-manager
- **Skill**: startup-fundraising

**If the task is about managing agent fleets or agent services:**
- **Agent**: ai-agents-builder
- **Skill**: agent-fleet-operations

**If the task is a general startup question spanning multiple areas:**
- **Agent**: product-manager
- **Skill**: startup-mega-router

---

## Override Rules

The router must honor explicit user instructions when present:

- If the user specifies `agent: X`, use agent X regardless of task.
- If the user specifies `skill: Y`, use skill Y regardless of task.
- If the user specifies both `agent: X` and `skill: Y`, use that exact combination.
- If the user writes "no agent" or "no skill", skip that component when possible.

When no explicit override is provided, apply task-specific, startup-specific, then domain-specific, then fallback rules in that order.

---

## Conflict Resolution

**When multiple agents could apply:**
- Choose the most specialized agent for the primary task.
- Example: "Optimize SQL query performance in a Python ML pipeline" → `sql-engineer` + `data-sql-optimization` (SQL is the bottleneck).

**When a skill is missing:**
- Route to the agent only and let it operate without a dedicated skill.
- Example: Blockchain question with no blockchain skill → `backend-engineer` without skill.

**When an agent is missing:**
- Use the skill directly if it is self-contained and can answer as a knowledge base.

**When both are missing:**
- Report "No matching route found" and suggest the closest alternative agent and skill.

---

## Reference Paths and Usage

Router deployment:
- Template storage (this repository): `frameworks/gemini-kit/framework/`
- User deployment: `.gemini/` and `.gemini/commands/`

Referenced resources:
- Skills: `.claude/skills/` (where Claude skills are stored)
- Agents: `.claude/agents/` (where Claude agents are stored)
- Commands: `.claude/commands/` (Claude-side commands, for reference)

Usage pattern:
- Gemini CLI loads `GEMINI.md` for global context.
- User invokes `gemini run /claude-router "<task>" [files...]`.
- Router selects agent and skill, prints the routing line, then completes the task using the chosen combination.
