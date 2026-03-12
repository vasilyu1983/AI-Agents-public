# FCA/EMI Compliance Rules for AI Coding Agents

> Copy this file to `.claude/rules/compliance-fca-emi.md` in every repository.
> This is a MANDATORY rule file for FCA-regulated Electronic Money Institutions.

## Audit Trail

- All commits MUST be signed (GPG or SSH key)
- Force-push is PROHIBITED on all protected branches
- Use merge commits to main/master (no squash, no rebase) to preserve full history
- Every PR must use the AI disclosure template (see pr-template-ai-disclosure.md)
- Commit messages must follow conventional commit format: `type(scope): description`

## Separation of Duties

- AI agents MUST NOT approve pull requests
- AI agents MUST NOT merge to production branches
- AI agents MUST NOT trigger deployments
- The PR author MUST NOT be the sole reviewer (four-eyes principle)
- Code reviewer MUST be a different person from the developer who used the AI agent
- Security-critical changes (auth/, payments/, crypto/, compliance/) require an additional security reviewer

## Prohibited Actions

- NEVER auto-merge pull requests to production branches
- NEVER bypass branch protection rules
- NEVER commit without signing
- NEVER store real customer data in code, tests, comments, or context files
- NEVER include credentials, API keys, or connection strings in committed files
- NEVER disable security scanning gates in CI/CD

## AI-Generated Code Tracking

- All PRs involving AI-generated code must declare AI involvement in the PR description
- AI tools used must be listed (Claude Code, Codex, Cursor, Copilot)
- Files that are primarily AI-generated must be identified
- Human verification checklist must be completed before merge approval

## Model Risk Inventory

- AI-generated code artifacts are subject to SS1/23 model risk management principles
- Track AI-generated components in the team's model risk register
- Defect rates for AI-generated code must be monitored and reported quarterly
- Any AI-generated code in critical paths (auth, payments, crypto) requires enhanced review

## SM&CR Accountability

- The designated Senior Manager (SMF) is accountable for AI tool governance
- "The AI wrote it" is not an acceptable explanation for defects or compliance failures
- Developers must understand all AI-generated code they approve
- Training on AI tool usage and governance is required for all certified persons

## Operational Resilience

- AI tool unavailability is a scenario in operational resilience testing
- Manual development fallback procedures must be documented and tested quarterly
- AI tool providers (Anthropic, OpenAI) are listed in the IBS dependency register
- Portability: AGENTS.md format supports multiple AI tools (Claude Code + Codex)
