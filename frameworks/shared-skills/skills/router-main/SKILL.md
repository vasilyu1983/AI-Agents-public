---
name: router-main
description: Universal entry point that routes any query to the appropriate domain router (startup, engineering, operations) - orchestrates 80 skills
metadata:
  version: "1.4"
---

# Router: Main

**Universal entry point** for the Claude Code Kit framework. This router analyzes your query and hands off to the appropriate domain router.

---

## How It Works

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
│  23 skills        │  │  33 skills        │  │   20 skills       │
│                   │  │                   │  │                   │
│  Business         │  │  Technical        │  │  QA & DevOps      │
│  Marketing (9)    │  │  AI/ML            │  │  Testing          │
│  Documents        │  │  Software         │  │  Deployment       │
│  Startup          │  │  Data             │  │  Git              │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

---

## Quick Routing

| Your Question | Routed To | Examples |
|---------------|-----------|----------|
| Business/Startup | `router-startup` | "validate my idea", "pricing strategy", "pitch deck" |
| Technical/Build | `router-engineering` | "build an API", "create AI agent", "frontend app" |
| Test/Deploy | `router-operations` | "test this", "deploy to prod", "CI/CD pipeline" |

---

## Routing Decision Tree

```text
QUERY ANALYSIS
    │
    ├─► Business keywords detected?
    │   • "idea", "validate", "market", "pricing", "funding"
    │   • "competitor", "GTM", "launch", "startup"
    │   • "pitch deck", "investor", "business model"
    │   • "marketing", "SEO", "social media", "leads"
    │   • "spreadsheet", "presentation", "document"
    │   └─► router-startup
    │
    ├─► Technical keywords detected?
    │   • "build", "implement", "code", "develop"
    │   • "API", "frontend", "backend", "mobile", "database"
    │   • "AI", "LLM", "agent", "RAG", "ML", "fine-tune"
    │   • "architecture", "design system", "component"
    │   • "Claude Code", "skill", "command", "hook"
    │   └─► router-engineering
    │
    ├─► Operations keywords detected?
    │   • "test", "QA", "testing", "Playwright", "E2E"
    │   • "deploy", "CI/CD", "Kubernetes", "Docker"
    │   • "monitor", "observability", "metrics", "logs"
    │   • "debug", "error", "fix", "troubleshoot"
    │   • "git", "commit", "PR", "branch", "merge"
    │   • "CLAUDE.md", "AGENTS.md", "large codebase", "documentation setup"
    │   └─► router-operations
    │
    └─► Ambiguous or multi-domain?
        └─► Ask clarifying question OR invoke multiple routers
```

---

## Domain Routers

### router-startup (23 skills)

**Focus**: Business validation, marketing, documents, product management

| Category | Skills |
|----------|--------|
| Startup Validation | idea-validation, review-mining, trend-prediction, competitive-analysis, business-models, go-to-market, fundraising |
| Marketing (9) | social-media, leads-generation, seo-technical, ai-search-optimization, content-strategy, paid-advertising, email-automation, cro, **product-analytics** |
| Documents | pptx, docx, xlsx, pdf |
| Product | product-management |
| UX | ux-research, ui-ux-design |

**NEW in January 2026:**

- `marketing-product-analytics` - PostHog/Pendo/Amplitude instrumentation, event taxonomy, LLM analytics, attribution

**Use when**: You have a business idea, need market validation, want to create business documents, plan your GTM strategy, need traffic/leads, or want to track product metrics.

### router-engineering (33 skills)

**Focus**: Technical implementation, AI/ML, software development, Claude Code

| Category | Skills |
|----------|--------|
| AI/ML | agents, llm, llm-inference, ml-data-science, ml-timeseries, mlops, prompt-engineering, rag |
| Software | frontend, backend, mobile, architecture-design, clean-code-standard, code-review, security-appsec, crypto-web3, ui-ux-design, ux-research, localisation |
| Data | sql-optimization, lake-platform, analytics-engineering |
| Dev Workflow | api-design, dependency-management, workflow-planning |
| Claude Code | agents, commands, hooks, mcp, project-memory, skills |

**Use when**: You need to build something technical, implement an AI agent, design an API, or work with code.

### router-operations (20 skills)

**Focus**: QA, testing, DevOps, deployment, git workflows, documentation

| Category | Skills |
|----------|--------|
| Testing | testing-strategy, testing-playwright, testing-ios, testing-android, testing-mobile, api-testing-contracts, agent-testing |
| Quality | debugging, observability, resilience, refactoring, docs-coverage |
| DevOps | devops-platform |
| Git | commit-message, workflow |
| Docs | codebase, ai-prd, **claude-code-project-memory** |

**Use when**: You need to test code, deploy to production, set up CI/CD, debug issues, manage git workflows, or **set up documentation for large codebases (100K-1M LOC)**.

---

## Cross-Router Workflows

The routers hand off to each other automatically. Common flows:

### Flow 1: Idea → Product → Launch

```text
router-startup (validate idea)
       ↓
router-engineering (build MVP)
       ↓
router-operations (test & deploy)
       ↓
router-startup (GTM & launch)
```

### Flow 2: Technical Product

```text
router-engineering (architecture)
       ↓
router-engineering (implementation)
       ↓
router-operations (testing)
       ↓
router-operations (deployment)
       ↓
router-startup (pricing & launch)
```

### Flow 3: Quick Fix

```text
router-operations (debug issue)
       ↓
router-engineering (implement fix)
       ↓
router-operations (test & deploy)
```

---

## Example Queries

| Query | Routed To | Why |
|-------|-----------|-----|
| "I have an idea for a SaaS product" | `router-startup` | Business validation |
| "Build a REST API for user management" | `router-engineering` | Technical implementation |
| "Set up CI/CD for my Node.js app" | `router-operations` | DevOps/deployment |
| "Create a pitch deck for investors" | `router-startup` | Business document |
| "Implement RAG for my chatbot" | `router-engineering` | AI/ML |
| "Debug why my tests are failing" | `router-operations` | QA/debugging |
| "Analyze competitors in the CRM space" | `router-startup` | Market analysis |
| "Add authentication to my frontend" | `router-engineering` | Software dev |
| "Monitor my production app" | `router-operations` | Observability |
| "Set up CLAUDE.md for large codebase" | `router-operations` | Documentation setup |
| "Create AGENTS.md for cross-platform" | `router-operations` | Cross-platform docs |

---

## Error Handling & Fallbacks

```text
ROUTING FAILURE HANDLING
    │
    ├─► No route matched?
    │   └─► Ask clarifying question
    │   └─► "Could you clarify: is this a business, technical, or operations question?"
    │
    ├─► Multiple routes matched equally?
    │   └─► Invoke multiple routers in parallel
    │   └─► Synthesize combined results
    │
    ├─► Sub-router failed?
    │   └─► Retry with exponential backoff
    │   └─► Fallback to broader skill if specialized fails
    │
    └─► Critical failure?
        └─► Human escalation path
        └─► Log for observability
```

**Best Practices:**

- Implement retry logic with exponential backoff for transient failures
- Use circuit breakers to prevent cascading failures across routers
- Always have fallback paths for critical workflows

---

## Observability

For production deployments, trace routing decisions:

| Tool           | Use Case       | Integration                         |
| -------------- | -------------- | ----------------------------------- |
| LangSmith      | LangChain apps | Near-zero overhead                  |
| Arize Phoenix  | Open source    | OpenTelemetry-based                 |
| Custom logging | Any framework  | Log `query → router → skill` path   |

**Key metrics to track:**

- Routing latency (target: <100ms)
- Route distribution (detect drift)
- Fallback rate (should be <5%)

See `qa-observability` skill for full instrumentation guide.

---

## Getting Started

Just describe what you need. This router will figure out where to send you.

**Examples:**

- "Help me validate my startup idea"
- "I need to build a mobile app"
- "Set up testing for my project"
- "Create a financial model"
- "Implement an AI agent"

The framework has **80 specialized skills** ready to help across all domains.
