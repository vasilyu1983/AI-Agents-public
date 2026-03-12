# AI Agent Governance Rules

> Copy this file to `.claude/rules/ai-agent-governance.md` in every repository.
> This is a MANDATORY rule file for organizations using AI coding agents.

## Approved AI Tools

Only the following AI coding tools are approved for use:

| Tool | Approved Use | Restrictions |
|------|-------------|-------------|
| **Claude Code** | Interactive development, planning, code review, subagents | No auto-merge, no deployment |
| **Codex** | Async batch tasks, issue triage, test generation | Sandboxed execution only |
| **Cursor** | IDE-assisted editing (supplementary) | No autonomous mode on regulated code |
| **GitHub Copilot** | Inline suggestions (supplementary) | Review all suggestions before accepting |

Unapproved tools must not be used on company repositories without security team review.

## Usage Restrictions by Environment

| Environment | AI Agent Allowed | Restrictions |
|------------|-----------------|-------------|
| **Local development** | Yes | No real customer data in prompts |
| **CI/CD pipelines** | Codex only (sandboxed) | Read-only access, no deployments |
| **Staging** | Yes (via approved tools) | Synthetic data only |
| **Production** | No direct access | AI agents never touch production systems |
| **Production debugging** | Sanitized logs only | Strip PII before sharing with agents |

## Disclosure Requirements

### Every PR
- AI tools used must be declared in the PR description
- Role of AI must be specified (generated, reviewed, tested, debugged)
- Human verification checklist must be completed

### Quarterly Reporting
- Aggregate AI tool usage metrics reported to engineering leadership
- Defect rates in AI-assisted vs non-AI PRs tracked
- Cost metrics (token usage, subscription costs) reported

### Incident Reporting
- AI tool failures affecting development velocity: report to engineering lead
- AI-generated code causing production incidents: report to CTO + compliance
- Data exposure via AI tools: report to security team + DPO immediately

## AI Tool Configuration

### Required Settings
- Telemetry: Review and approve data sharing settings
- Context: AGENTS.md + CLAUDE.md symlink convention in all repos
- Rules: Mandatory compliance rules installed (compliance-fca-emi.md, data-handling-gdpr-pci.md)
- Hooks: Pre-commit validation hooks enabled where available

### Prohibited Configurations
- Do not disable security-related hooks or pre-commit checks
- Do not configure AI tools to bypass code review
- Do not grant AI tools write access to production branches
- Do not share API keys for AI tools across personal and company use

## Training Requirements

Before using AI coding agents on company repositories:

1. Complete AI tool governance briefing (provided by engineering leadership)
2. Review this governance document and the companion compliance rules
3. Understand the PR AI disclosure template and complete it consistently
4. Know the escalation path for AI-related incidents

## Inventory and Tracking

- All repositories using AI coding agents must be registered in the AI tool inventory
- AI-generated code artifacts in critical paths must be flagged in the model risk register
- New AI tool adoptions require security team review and compliance sign-off
- Annual review of approved tool list and governance policies
