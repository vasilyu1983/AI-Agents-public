# Gemini Router Rules

This document defines routing logic for Gemini CLI to leverage Claude Code Kit skills and agents via the `/claude-router` command.

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
- **marketing-ai-search-optimization**: AI search engine optimization (AEO/GEO/LLMO) for ChatGPT, Perplexity, Claude, Gemini, and Google AI Overviews with technical setup, content strategies, and measurement frameworks.
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
- **mobile-engineer**: Production-grade mobile app development with Swift/Kotlin/React Native, testing, and deployment (uses `software-mobile`).
- **prd-architect**: PRD creation, validation, and technical specifications for software projects (uses `product-prd-development`, `foundation-documentation`).
- **product-manager**: Product strategy, roadmaps, user research, and metrics analysis (uses `product-management`, `foundation-documentation`).
- **prompt-engineer**: Prompt design, optimization, and validation for LLM-powered systems (uses `ai-prompt-engineering`, `ai-llm-development`).
- **security-specialist**: Application security specialist covering OWASP Top 10 2025, zero trust architecture, supply chain security, threat modeling, and secure design patterns (uses `software-security-appsec`, `ai-ml-ops-security`).
- **smm-strategist**: Social media marketing strategist for content, campaigns, and growth across major platforms (uses `marketing-social-media`).
- **sql-engineer**: SQL optimization, query tuning, database design, schema migrations, and indexing (uses `ops-database-sql`).
- **system-architect**: System design, architecture review, and technical strategy for complex software systems (uses `software-architecture-design`, `quality-resilience-patterns`, `quality-observability-performance`).
- **test-architect**: Test strategy, planning, and coverage analysis across testing levels (uses `software-testing-automation`, `quality-code-refactoring`, `quality-debugging-troubleshooting`).

---

## Routing Priority

The router applies a 4-level priority system:

1. **Explicit user override**  
   - User specifies `agent: X` and/or `skill: Y` in the prompt.  
   - Router must respect these hints even if another route might be better.

2. **Task-specific routing**  
   - Match the request type to a specialized agent+skill pair.  
   - Examples: PRD work, RAG design, SQL optimization, prompt engineering.

3. **Domain-specific routing**  
   - Match the technology stack or domain to an agent.  
   - Examples: backend vs frontend vs mobile vs data-science vs infra.

4. **Default fallback**  
   - Use the most general agent when no specific match is found.  
   - Example: route general software questions to `backend-engineer` or `ai-agents-builder` depending on focus.

---

## Task-Specific Routes (Examples)

These examples mirror the test cases in `router-tests.md`.

**AI agent architecture and RAG:**
- Agent: `ai-agents-builder`
- Skill: `ai-agents-development`

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
- Skill: `ops-database-sql`

**ML deployment, monitoring, and data ingestion:**
- Agent: `data-scientist` or `llm-engineer` (depending on model type)
- Skill: `ai-ml-ops-production`

**RAG pipeline design:**
- Agent: `llm-engineer`
- Skill: `ai-llm-rag-engineering`

**Prompt engineering and structured outputs:**
- Agent: `prompt-engineer`
- Skill: `ai-prompt-engineering`

**PRD creation and validation:**
- Agent: `prd-architect`
- Skill: `product-prd-development`

**LLM inference optimization (vLLM, quantization, batching):**
- Agent: `llm-engineer`
- Skill: `ai-llm-ops-inference`

**ML/LLM security and prompt-injection defense:**
- Agent: `llm-engineer`
- Skill: `ai-ml-ops-security`

---

## Override Rules

The router must honor explicit user instructions when present:

- If the user specifies `agent: X`, use agent X regardless of task.
- If the user specifies `skill: Y`, use skill Y regardless of task.
- If the user specifies both `agent: X` and `skill: Y`, use that exact combination.
- If the user writes "no agent" or "no skill", skip that component when possible.

When no explicit override is provided, apply task-specific, then domain-specific, then fallback rules in that order.

---

## Conflict Resolution

**When multiple agents could apply:**
- Choose the most specialized agent for the primary task.
- Example: "Optimize SQL query performance in a Python ML pipeline" → `sql-engineer` + `ops-database-sql` (SQL is the bottleneck).

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
- Template storage (this repository): `frameworks/gemini-kit/initial-setup/`
- User deployment: `.gemini/` and `.gemini/commands/`

Referenced resources:
- Skills: `.claude/skills/` (where Claude skills are stored)
- Agents: `.claude/agents/` (where Claude agents are stored)
- Commands: `.claude/commands/` (Claude-side commands, for reference)

Usage pattern:
- Gemini CLI loads `GEMINI.md` for global context.
- User invokes `gemini run /claude-router "<task>" [files...]`.
- Router selects agent and skill, prints the routing line, then completes the task using the chosen combination.
