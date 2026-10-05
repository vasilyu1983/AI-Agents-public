---
description: Code Review — extracted from monolith for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## Code Review

**Typical scenario**

You have an auth-related PR and want a fast multi-perspective review before merge.

**Claude prompt**

```text
Create an agent team using the installed `software-code-review-board` members.

Scenario: Review a pull request that changes session refresh logic, token rotation, and rate limiting in the auth module.

Required context:
- Review target: current branch diff
- Focus area: auth/session code and adjacent tests
- Optional artifacts if present: graphs/code-graph.json, reports/query-*.md

Instructions:
- software-security-reviewer: audit auth boundaries, token handling, secret exposure, and abuse paths
- software-performance-reviewer: audit latency, cache behavior, query efficiency, and hot-path regressions
- qa-test-reviewer: audit coverage gaps, edge cases, and flake risk
- Each reviewer works independently
- Return findings with severity, rationale, and the smallest safe fix
- Parent thread synthesizes a prioritized review report
- Clean up the team when done
```

**Codex prompt**

```text
Spawn security_reviewer, performance_reviewer, and test_reviewer in parallel.

Task: Review the current branch diff with emphasis on auth session refresh, token rotation, and rate limiting.

Context:
- Use graphs/code-graph.json and reports/query-*.md first if they exist
- Otherwise do bounded reads around the changed files

Deliverable from each agent:
- prioritized findings
- likely regression risk
- specific fix suggestion

Wait for all three agents, then produce one merged review report grouped by severity.
```
