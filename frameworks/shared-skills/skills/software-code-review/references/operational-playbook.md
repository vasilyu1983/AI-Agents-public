## Review Scope Rule

Review **only new or modified code** in the merge request, not the entire repository.

- Feedback must be limited to changes in the diff unless new code directly interacts with existing components where consistency is important
- Do not comment on untouched legacy code
- If context from unchanged files is needed, read it but do not critique it

This rule prevents scope creep and keeps reviews focused and actionable.

---
## Table of Contents

- [Review Scope Rule](#review-scope-rule)
- [Severity Ratings](#severity-ratings)
- [Review Health Signals](#review-health-signals)
- [AI Impact on Reviews](#ai-impact-on-reviews)
- [Navigation](#navigation)
- [Resources](#resources)
- [Templates](#templates)
- [Related Skills](#related-skills)
- [Core Review Checklist (Inline)](#core-review-checklist-inline)
- [Review Modes](#review-modes)
- [Simplicity and Complexity Controls](#simplicity-and-complexity-controls)
- [Pattern: Pull Request Review Workflow](#pattern-pull-request-review-workflow)
- [Pattern: Security-Focused Review](#pattern-security-focused-review)
- [Pattern: Test-Gap Review](#pattern-test-gap-review)
- [Pattern: Refactor-Suggestion Review](#pattern-refactor-suggestion-review)
- [Navigation](#navigation)
- [Review Templates by Domain](#review-templates-by-domain)
- [Web & Frontend](#web-&-frontend)
- [Backend & APIs](#backend-&-apis)
- [Mobile Applications](#mobile-applications)
- [Infrastructure as Code](#infrastructure-as-code)
- [Blockchain & Smart Contracts](#blockchain-&-smart-contracts)
- [External Resources](#external-resources)


## Severity Ratings

Use consistent severity labels to help authors prioritize:

- **P0 (Critical)**: Security vulnerability, data loss risk, funds at risk, immediate exploit possible
- **P1 (High)**: Correctness bug, missing error handling, complex exploit path
- **P2 (Medium)**: Performance issue, logic error, gas inefficiency, poor UX
- **P3 (Low)**: Code quality, naming, style, documentation, best practices

Mark P0/P1 as **REQUIRED** fixes. Mark P2/P3 as **SUGGESTION** or **OPTIONAL**.

---

## Review Health Signals

Use delivery metrics as context, not as a substitute for review-specific signals.

| Signal | What It Measures | Good Default |
|--------|------------------|--------------|
| Time to first substantive review | Pickup speed after a review request | Same day during working hours |
| Time to approval | End-to-end review latency | Short enough that authors do not lose context |
| Review rounds | Amount of rework introduced by review | Usually 1-2 for routine PRs |
| Escape rate | Bugs or regressions found after merge | Track trend, reduce over time |
| Reviewer load | Concentration of review work on a few people | Spread across owners, avoid bottlenecks |

### AI Impact on Reviews

AI-assisted coding often increases submission volume and can hide shallow reasoning behind polished diffs. Treat vendor metrics and one-off case studies as directional only. Re-verify current claims in `data/sources.json` before using them for policy decisions.

Stable guidance:

- keep PRs small and reviewable
- allocate extra review attention to AI-generated or agent-created changes
- use automation to remove routine style and scanner work from human review
- track post-merge defects and churn to see whether AI assistance is improving or degrading outcomes

---

## Navigation

### Resources

- [references/review-checklist-comprehensive.md](review-checklist-comprehensive.md) — Expanded review checklist and prompts
- [references/automation-tools.md](automation-tools.md) — Automation helpers (linters, static analysis, PR bots)
- [references/psychological-safety-guide.md](psychological-safety-guide.md) — How to deliver feedback constructively
- [data/sources.json](../data/sources.json) — Curated references and standards

### Templates

- [assets/blockchain/crypto-review.md](../assets/blockchain/crypto-review.md) — Checklist for smart contract and blockchain reviews

### Related Skills

**Development & Testing:**

- [../software-backend/SKILL.md](../../software-backend/SKILL.md) — Backend patterns and language-specific implementation details
- [../software-frontend/SKILL.md](../../software-frontend/SKILL.md) — Frontend/Next.js specifics and accessibility considerations
- [../software-mobile/SKILL.md](../../software-mobile/SKILL.md) — iOS, Android, and React Native development patterns
- [../qa-testing-strategy/SKILL.md](../../qa-testing-strategy/SKILL.md) — Test strategies, coverage, and automation
- [../software-ui-ux-design/SKILL.md](../../software-ui-ux-design/SKILL.md) — UI/UX principles and accessibility standards

**Architecture & Design:**

- [../software-architecture-design/SKILL.md](../../software-architecture-design/SKILL.md) — System-level review context and tradeoffs
- [../dev-api-design/SKILL.md](../../dev-api-design/SKILL.md) — RESTful and GraphQL API design principles

**Security & Quality:**

- [../software-security-appsec/SKILL.md](../../software-security-appsec/SKILL.md) — Security deep dives and hardening patterns
- [../software-clean-code-standard/SKILL.md](../../software-clean-code-standard/SKILL.md) — Clean code rule IDs (`CC-*`) for citation in reviews
- [../qa-resilience/SKILL.md](../../qa-resilience/SKILL.md) — Resilience and failure-handling considerations
- [../qa-refactoring/SKILL.md](../../qa-refactoring/SKILL.md) — Refactoring techniques and code improvement
- [../qa-debugging/SKILL.md](../../qa-debugging/SKILL.md) — Debugging methodologies and troubleshooting

**Infrastructure & Operations:**

- [../ops-devops-platform/SKILL.md](../../ops-devops-platform/SKILL.md) — DevOps practices, CI/CD, and infrastructure
- [../data-sql-optimization/SKILL.md](../../data-sql-optimization/SKILL.md) — Database query optimization and schema design
- [../dev-git-workflow/SKILL.md](../../dev-git-workflow/SKILL.md) — Git best practices and branching strategies

---

## Core Review Checklist (Inline)

Use this checklist as a baseline for any review:

- Correctness: logic matches requirements, handles edge cases
- Security: input validation, auth, access control checks
- Reliability: error handling, retries, timeouts where needed
- Performance: obvious hot paths, unnecessary work, N+1 patterns
- Readability: clear naming, small functions, consistent style
- Standards: cite `CC-*` IDs instead of restating clean code rules ([../../software-clean-code-standard/references/clean-code-standard.md](../../software-clean-code-standard/references/clean-code-standard.md))
- Tests: coverage for happy path, errors, and regression cases

---

## Review Modes

Choose the mode that matches the task:

- Safety review: focus on security, data handling, privacy, and dangerous operations (deletes, money movement, external calls).
- Design review: focus on boundaries, abstractions, and how the code fits the architecture.
- Maintainability review: focus on readability, duplication, naming, and complexity.
- Performance review: focus on hot paths, database access, allocations, and unnecessary work.
- Test review: focus on coverage, flakiness, and meaningful assertions.

Explicitly note which mode(s) you are applying so comments stay coherent.

---

## Simplicity and Complexity Controls

- Prefer library and platform capabilities over custom code when behavior is equivalent.
- Remove dead/commented-out code and collapse duplication (DRY) before layering new logic.
- Keep functions/classes single-purpose; split large modules before adding features.
- Avoid premature optimization; tune based on profiling evidence, not intuition.
- Schedule incremental refactors alongside risky changes to prevent complexity creep.

---

## Pattern: Pull Request Review Workflow

Use this pattern for PR-based reviews.

1. Context
   - Read the PR description, issue link, and acceptance criteria.
   - Identify risk areas (security, data migration, public APIs).
2. High-level scan
   - Look at changed files and folders first, not individual lines.
   - Confirm the change shape matches the description (no surprise changes).
3. Deep review
   - Walk file-by-file in a stable order.
   - Apply the core checklist: correctness → security → reliability → performance → readability → tests.
4. Tests
   - Check that new behavior has tests.
   - Check that risky paths have regression coverage.
5. Feedback
   - Group comments by theme (bugs, design, style, tests).
   - Clearly distinguish REQUIRED vs NICE-TO-HAVE.

Review comment template:

- Summary: what this change does, risk level.
- Strengths: what is working well.
- Required changes: correctness, security, reliability issues.
- Suggested improvements: design, naming, structure, tests.

---

## Pattern: Security-Focused Review

Use when code touches authentication, authorization, input handling, secrets, or external integrations.

- Inputs:
  - Validate all external inputs (HTTP, CLI, file, message queue).
  - Prefer whitelists over blacklists.
- Auth and access control:
  - Confirm authentication is required where expected.
  - Ensure authorization checks run on every sensitive operation.
- Data handling:
  - Avoid logging secrets, tokens, or personal data.
  - Ensure encryption/transport security is handled at the right layer.
- Dangerous operations:
  - Confirm explicit confirmation or safeguards for deletes, payments, or irreversible operations.

When security concerns dominate, pair this skill with:

- [software-security-appsec](../../software-security-appsec/SKILL.md) for OWASP Top 10, authentication, authorization, input validation, and cryptography patterns.
- [ai-mlops](../../ai-mlops/SKILL.md) for LLM/ML safety and threat models.

---

## Pattern: Test-Gap Review

Use this when a change is large or risky.

- Map behaviors:
  - For each new or changed behavior, ask: "Where is this tested?"
- Check test types:
  - Unit tests: core logic functions.
  - Integration tests: modules talking to DBs, queues, or external APIs.
  - E2E or system tests: critical user flows.
- Validate assertions:
  - Tests assert both happy path and failure behavior.
  - Tests check boundaries (empty lists, large values, invalid inputs).

If tests are missing:
- Call out missing coverage as REQUIRED when bugs would be likely or high impact.
- Suggest concrete test cases and where to put them.

---

## Pattern: Refactor-Suggestion Review

Use when the code is correct but could be simpler.

- Start with correctness: never propose refactors that change behavior without acknowledgment.
- Suggest incremental improvements:
  - Extract functions to reduce duplication.
  - Rename variables and functions for clarity.
  - Reduce nested branching and long functions.
- Use neutral, constructive language:
  - "Consider extracting this block into a helper for readability."
  - "This condition could be inverted to reduce nesting."

Mark refactor suggestions as OPTIONAL unless they impact correctness or maintainability significantly.

---

## Navigation

When more depth is needed, use:

- [../software-backend/SKILL.md](../../software-backend/SKILL.md), [../software-frontend/SKILL.md](../../software-frontend/SKILL.md), and [../software-mobile/SKILL.md](../../software-mobile/SKILL.md) for stack details.
- [data/sources.json](../data/sources.json) for external guides on secure coding, style guides, and language-specific best practices.

---

## Review Templates by Domain

Specialized review checklists organized by technology stack and domain:

### Web & Frontend

- [assets/web-frontend/frontend-review.md](../assets/web-frontend/frontend-review.md) - React, Next.js, Vue, Angular
  - UI/UX correctness (responsive design, accessibility WCAG 2.1)
  - Performance (bundle size, runtime performance, network optimization)
  - React/Next.js patterns (hooks, state management, SSR/SSG)
  - Security (XSS prevention, authentication, data handling)
  - TypeScript best practices and testing strategies

### Backend & APIs

- [assets/backend-api/api-review.md](../assets/backend-api/api-review.md) - Node.js, Python, Go, Java, Rust
  - API design (RESTful principles, GraphQL patterns)
  - Security (authentication, authorization, input validation, rate limiting)
  - Data handling (database operations, migrations, validation)
  - Error handling and logging
  - Performance and scalability
  - Language-specific patterns (async/await, error handling, concurrency)

### Mobile Applications

- [assets/mobile/mobile-review.md](../assets/mobile/mobile-review.md) - iOS, Android, React Native
  - Platform-specific patterns (SwiftUI, Jetpack Compose, RN best practices)
  - UI/UX and accessibility
  - Performance (launch time, memory management, battery efficiency)
  - Networking and data persistence
  - Security (biometric auth, data encryption, code obfuscation)
  - App store compliance

### Infrastructure as Code

- [assets/infrastructure/infrastructure-review.md](../assets/infrastructure/infrastructure-review.md) - Terraform, Kubernetes, Docker, CI/CD
  - Terraform/IaC patterns (state management, security, best practices)
  - Kubernetes (deployments, security contexts, observability)
  - Docker (Dockerfile optimization, security scanning)
  - CI/CD pipelines (GitHub Actions, GitLab CI)
  - Cloud-specific (AWS, GCP configurations)
  - Monitoring and observability

### Blockchain & Smart Contracts

- [assets/blockchain/crypto-review.md](../assets/blockchain/crypto-review.md) - Solidity, Rust, FunC, Tact
  - Critical security issues (reentrancy, access control, integer overflow, oracle manipulation)
  - High severity issues (frontrunning/MEV, delegatecall safety, flash loan protection)
  - DeFi-specific checks (AMM/DEX, lending/borrowing, staking/yield farming)
  - Token-specific checks (ERC20, ERC721, ERC1155)
  - Platform-specific checks (Solana account validation, TON message handling)
  - Testing coverage, documentation review, deployment preparation

---

## External Resources

See [data/sources.json](../data/sources.json) for curated references on:

- Secure coding standards and OWASP guidance
- Language-specific style guides and idioms
- Code review best practices for engineering teams
