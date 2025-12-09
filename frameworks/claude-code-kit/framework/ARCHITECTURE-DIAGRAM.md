# Claude Code Kit Architecture

This file has been simplified. Architecture diagrams are now distributed across individual component READMEs for better maintainability.

## Quick Reference

| Component | Count | Location |
|-----------|-------|----------|
| **Hooks** | 7 | [hooks/](hooks/) |
| **Commands** | 28 | [commands/](commands/) |
| **Agents** | 21 | [agents/](agents/) |
| **Skills** | 62 | [skills/](skills/) |

## Router Architecture

```
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
│  17 skills        │  │  29 skills        │  │   15 skills       │
│                   │  │                   │  │                   │
│  Business         │  │  Technical        │  │  QA & DevOps      │
│  Marketing        │  │  AI/ML            │  │  Testing          │
│  Documents        │  │  Software         │  │  Deployment       │
│  Startup          │  │  Data             │  │  Git              │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

## Four-Layer Architecture

```
Layer 1: Automation (Hooks)     - Event-driven orchestration
         ↓
Layer 2: User Interface (Commands) - Entry points and workflows
         ↓
Layer 3: Orchestration (Agents)    - Intelligent coordination
         ↓
Layer 4: Knowledge (Skills)        - Domain expertise and templates
```

## Component Documentation

- **Hooks Guide**: [hooks/HOOKS-GUIDE.md](hooks/HOOKS-GUIDE.md)
- **Framework README**: [README.md](README.md)
- **Kit README**: [../README.md](../README.md)

## Router Details

### router-main (Entry Point)

Universal dispatcher that analyzes queries and routes to domain routers.

### router-startup (17 skills)

| Category | Skills | Count |
|----------|--------|-------|
| Startup | idea-validation, review-mining, trend-prediction, competitive-analysis, business-models, go-to-market, fundraising | 7 |
| Marketing | ai-search-optimization, leads-generation, seo-technical, social-media | 4 |
| Documents | pdf, docx, xlsx, pptx | 4 |
| Product | product-management | 1 |
| UX | ux-research | 1 |

### router-engineering (29 skills)

| Category | Skills | Count |
|----------|--------|-------|
| AI/ML | agents, llm, llm-inference, ml-data-science, ml-timeseries, mlops, prompt-engineering, rag | 8 |
| Software | frontend, backend, mobile, architecture-design, code-review, security-appsec, crypto-web3, ui-ux-design | 8 |
| Data | sql-optimization, lake-platform | 2 |
| Dev Workflow | api-design, dependency-management, workflow-planning | 3 |
| Claude Code | agents, commands, hooks, mcp, project-memory, skills | 6 |
| Ops | devops-platform | 1 |
| Docs | ai-prd | 1 |

### router-operations (15 skills)

| Category | Skills | Count |
|----------|--------|-------|
| Testing | testing-strategy, testing-playwright, testing-ios, agent-testing | 4 |
| Quality | debugging, observability, resilience, refactoring, docs-coverage | 5 |
| DevOps | devops-platform | 1 |
| Git | commit-message, workflow | 2 |
| Docs | codebase, ai-prd | 2 |

## Skill Categories (62 total)

| Category | Skills | Count |
|----------|--------|-------|
| **Routers** | router-main, router-startup, router-engineering, router-operations | 4 |
| AI/ML | ai-agents, ai-llm, ai-llm-inference, ai-ml-data-science, ai-ml-timeseries, ai-mlops, ai-prompt-engineering, ai-rag | 8 |
| Claude Code | claude-code-agents, claude-code-commands, claude-code-hooks, claude-code-mcp, claude-code-project-memory, claude-code-skills | 6 |
| Software | software-frontend, software-backend, software-mobile, software-architecture-design, software-code-review, software-security-appsec, software-crypto-web3, software-ui-ux-design, software-ux-research | 9 |
| QA & Testing | qa-testing-strategy, qa-testing-playwright, qa-testing-ios, qa-agent-testing, qa-debugging, qa-observability, qa-resilience, qa-refactoring, qa-docs-coverage | 9 |
| Data & Ops | data-sql-optimization, data-lake-platform, ops-devops-platform | 3 |
| Dev Workflow | dev-api-design, dev-dependency-management, dev-workflow-planning, git-workflow | 4 |
| Git | git-commit-message | 1 |
| Docs | docs-codebase, docs-ai-prd | 2 |
| Documents | document-pdf, document-docx, document-xlsx, document-pptx | 4 |
| Marketing | marketing-ai-search-optimization, marketing-leads-generation, marketing-seo-technical, marketing-social-media | 4 |
| Product | product-management | 1 |
| Startup | startup-idea-validation, startup-review-mining, startup-trend-prediction, startup-competitive-analysis, startup-business-models, startup-go-to-market, startup-fundraising | 7 |

## Related Kits

- [Codex Kit](../../codex-kit/) - Codex CLI router
- [Gemini Kit](../../gemini-kit/) - Gemini CLI router
