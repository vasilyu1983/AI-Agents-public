# Claude Code Kit Architecture

This file has been simplified. Architecture diagrams are now distributed across individual component READMEs for better maintainability.

## Quick Reference

| Component | Count | Location |
|-----------|-------|----------|
| **Hooks** | 7 | [hooks/](hooks/) |
| **Commands** | 28 | [commands/](commands/) |
| **Agents** | 21 | [agents/](agents/) |
| **Skills** | 60 | [skills/](skills/) |

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

## Skill Categories (60 total)

| Category | Skills | Count |
|----------|--------|-------|
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
| Startup | startup-mega-router, startup-idea-validation, startup-review-mining, startup-trend-prediction, startup-competitive-analysis, startup-business-models, startup-go-to-market, startup-fundraising, agent-fleet-operations | 9 |

## Related Kits

- [Codex Kit](../../codex-kit/) - Codex CLI router
- [Gemini Kit](../../gemini-kit/) - Gemini CLI router
