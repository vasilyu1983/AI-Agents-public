---
name: software-code-review
description: "Applies systematic code review patterns and checklists. Use when reviewing PRs or diffs for correctness, security, readability, maintainability, and AI-generated changes."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Code Review

This skill is for reviewing existing changes. It routes the agent to the right checklist, review mode, and platform workflow without turning `SKILL.md` into a tool catalog.

## Quick Reference

| Task | Use | Primary Reference |
|------|-----|-------------------|
| General PR or diff review | Baseline review flow and severity rubric | [references/operational-playbook.md](references/operational-playbook.md) |
| AI-generated or agent-created changes | Human-in-the-loop review rules and platform controls | [references/automation-tools.md](references/automation-tools.md) |
| Building or tuning an AI review tool/integration | Pre-review deterministic gate, size-gated planning pass, self-refutation filter pass | [references/deterministic-vs-llm-routing.md](references/deterministic-vs-llm-routing.md) |
| Backend/API review | Error handling, contracts, persistence, operability | [assets/backend-api/api-review.md](assets/backend-api/api-review.md) |
| Frontend review | Accessibility, responsive behavior, Core Web Vitals | [assets/web-frontend/frontend-review.md](assets/web-frontend/frontend-review.md) |
| Mobile review | Platform patterns, lifecycle, permissions, UX | [assets/mobile/mobile-review.md](assets/mobile/mobile-review.md) |
| Infrastructure review | CI/CD, IaC, secrets, deploy safety | [assets/infrastructure/infrastructure-review.md](assets/infrastructure/infrastructure-review.md) |
| Smart contract review | Access control, reentrancy, unsafe assumptions | [assets/blockchain/crypto-review.md](assets/blockchain/crypto-review.md) |
| Data / ML review | Pipelines, experiments, models, deployment | [assets/data-ml/data-pipeline-review.md](assets/data-ml/data-pipeline-review.md) |

## When to Use This Skill

Use this skill when the primary task is to:

- review a PR, merge request, or diff
- find correctness, security, reliability, or maintainability issues
- assess test gaps and regression risk
- critique AI-generated or agent-created changes before merge
- recommend small, behavior-preserving refactors

## When NOT to Use This Skill

- **Greenfield architecture** → [software-architecture-design](../software-architecture-design/SKILL.md)
- **Deep AppSec design or formal threat modeling** → [software-security-appsec](../software-security-appsec/SKILL.md)
- **Writing a new feature from scratch** → use the stack-specific implementation skill

## Workflow

1. Confirm the review surface: diff, PR, merge request, generated code, or a focused file set.
2. Route architecture-only or formal security-design questions to the adjacent skill when review is not the primary task.
3. Apply review modes in order: correctness, security, reliability, performance, and maintainability.
4. Pull in the stack overlay only when the code actually needs that domain-specific lens.
5. Return concrete findings with evidence, then verify any platform-specific claims via the navigation sources.

## ASCII Flow

```text
Code review request
  -> Identify diff, scope, and expected behavior
  -> Trace changed control flow and data contracts
  -> Look for regressions, security, performance, and test gaps
  -> Rank findings by severity and confidence
  -> Cite exact files and lines
  -> Summarize residual risk and verification gaps
```

## Review Routing

Apply review modes in this order unless the user asks for a narrower scope:

1. Correctness and edge cases
2. Security and data handling
3. Reliability and operability
4. Performance and cost
5. Maintainability and test coverage

Stack overlays:

- Frontend: [assets/web-frontend/frontend-review.md](assets/web-frontend/frontend-review.md)
- Backend/API: [assets/backend-api/api-review.md](assets/backend-api/api-review.md)
- Mobile: [assets/mobile/mobile-review.md](assets/mobile/mobile-review.md)
- Infrastructure: [assets/infrastructure/infrastructure-review.md](assets/infrastructure/infrastructure-review.md)
- Blockchain: [assets/blockchain/crypto-review.md](assets/blockchain/crypto-review.md)
- Data/ML: [assets/data-ml/data-pipeline-review.md](assets/data-ml/data-pipeline-review.md), [assets/data-ml/ml-model-review.md](assets/data-ml/ml-model-review.md), [assets/data-ml/ml-deployment-review.md](assets/data-ml/ml-deployment-review.md)

Platform overlays:

- GitHub: Copilot review, repository instructions, excluded files, Code Quality, merge queue
- GitLab: Duo review instructions, merge request approvals, approval rules
- Bitbucket: Code Insights, branch restrictions, required checks

If the user asks a platform-specific automation question, open the official entries in [data/sources.json](data/sources.json) first and use [references/automation-tools.md](references/automation-tools.md).

## AI-Assisted Review Rules

- Human review is authoritative. AI findings are advisory until confirmed.
- Treat AI-generated code and agent-created PRs as higher-context review tasks, not lower-effort review tasks: the bottleneck moves from writing to verifying, so budget reviewer time accordingly rather than assuming automation shrinks the review workload.
- Judge AI-generated code against this codebase's actual conventions, not an abstract style guide — consistency with surrounding code is the more useful bar than "is this idiomatic in general."
- Prefer native platform controls before third-party bots:
  - repository or path-specific review instructions
  - excluded files / generated file filters
  - required checks, approval rules, and merge queues
- Do not accept benchmark, pricing, or feature-comparison claims from memory. Verify current tool status first — this space (GitHub Copilot code review, CodeRabbit, Qodo/PR-Agent, and adjacent tools) changes ownership, pricing, and capability frequently; see `references/automation-tools.md` and `data/sources.json` and re-verify before quoting specifics.
- Never pin or cite a specific AI model version/ID as a reviewer-facing fact; capability and behavior shift too fast for that to stay true.

### AI-Generated Code Review Checklist

Apply these checks when reviewing AI-generated code or agent-created PRs:

| Check | What to look for |
|-------|-----------------|
| **Hallucinated imports** | Packages or methods that don't exist; verify with `npm info` / `pip index` |
| **Stale APIs** | Deprecated methods, old signatures, removed features |
| **Security gaps** | Missing input validation, hardcoded secrets, SQL concatenation, unescaped output |
| **Missing error handling** | Happy-path only; no try/catch, no null checks, no timeout handling |
| **Redundant abstractions** | Unnecessary wrappers, premature generalization, over-engineered patterns |
| **Copy-paste drift** | Similar blocks with subtle inconsistencies across files |
| **Test theater** | Tests that assert implementation details, mock everything, or test the framework |
| **Accessibility omissions** | Missing alt text, broken ARIA, no keyboard handling, div soup |
| **Design system violations** | Components that ignore existing tokens, spacing, or component patterns |
| **Confident but wrong comments** | Docstrings that describe what the code should do, not what it actually does |

Sources: [Hallucination Detection](../software-clean-code-standard/references/code-quality-operational-playbook.md#113-hallucination-detection-checklist), [AI Design Antipatterns](../software-ui-ux-design/references/ai-automation-ux.md#ai-generated-design-antipatterns)

## Severity Rubric

| Priority | Label | Criteria | Review action |
|----------|-------|----------|---------------|
| P0 | BLOCKER | Data loss, security hole, correctness bug, crashes in prod path | Must fix before merge |
| P1 | REQUIRED | Missing error handling, broken rollback, undefined behavior, SLA violation | Must fix before merge |
| P2 | SUGGESTED | Test gap for non-critical path, minor inefficiency, readability issue | Fix in this PR or tracked issue |
| P3 | OPTIONAL | Style preference, naming taste, future improvement | Author decides; no block |

Mark each finding with its priority and label. Do not lump P0 and P3 findings in the same comment thread.

## When Not to Block a Merge

Blocking is a cost: it delays value delivery, encourages batching future changes to avoid another round, and burns reviewer credibility if used on low-stakes disagreements. Do not block on:

- P3-only findings (style, naming taste, a "nicer" abstraction) — leave as non-blocking suggestions and let the author decide.
- A correct approach you would have written differently, with no identified defect or maintainability cost.
- Missing test coverage for genuinely low-risk, low-change-frequency code, when the author explicitly acknowledges the gap and it is tracked.
- Pre-existing issues outside the diff's blast radius — file a follow-up instead of expanding this review's scope.
- Disagreements that are actually about product/requirements, not the code — escalate to the right owner rather than relitigating in review comments.

Do block on P0/P1 findings, missing tests for genuinely risky new behavior, and anything that would be expensive or unsafe to fix after merge (data migrations, public API shape, security boundaries). When in doubt, separate the blocking finding from the optional ones instead of letting one bleed into the other's priority.

## Rubber-Stamp Detection

Fast, low-comment reviews are not automatically a problem — well-written, small, low-risk changes should review quickly. Treat these as a warning signal warranting a second look, not proof of bad review:

- Approval on a diff far larger than roughly 200-400 LOC with review duration implausibly short for that size (see `references/large-pr-review-strategies.md` and `references/code-review-metrics.md` for the size/pace data this heuristic is based on).
- "LGTM" with zero substantive comments on a change touching auth, money movement, migrations, or public APIs.
- A team or individual with a defect-escape rate trending up while review turnaround trends down — the speed gain is likely coming from skipped scrutiny.
- Approvals that only restate the PR description back rather than referencing specific lines or behavior.

Use these as coaching signals (spot-check, pair on a review, ask what was actually read), not as a public leaderboard — see `references/code-review-metrics.md` for how to track this without creating gaming incentives.

## Review the Tests, Not Just the Code

A diff with green tests and no test-quality review is only half-reviewed. Apply the same scrutiny to test code as to production code:

- Confirm new/changed behavior actually has a test that would fail without the fix, not just a test that happens to pass alongside it.
- Watch for tests that assert implementation details (mocking everything, checking internal call counts) instead of observable behavior — these pass trivially and catch nothing on refactor.
- Check that error paths and boundaries are tested, not just the happy path.
- Treat a bug fix with no regression test as incomplete, not as a style nit.

## Known Traps

- Reviewing from the PR description first and the diff second. Treat descriptions as claims, not evidence.
- Spending most effort on style and almost none on behavioral risk, migration risk, or rollback safety.
- Treating generated files, snapshots, or lockfile churn as noise without checking whether they hide contract or dependency drift.
- Reviewing only changed lines when the bug is in the surrounding invariant, caller expectations, or teardown path.
- Calling out `needs tests` generically without naming the missing scenario, boundary, or regression.
- Accepting benchmark, security, or framework claims in the diff comments without live verification when the claim is version-sensitive.

## Common Anti-Patterns

- Treating review as approval theater: light comments on naming while correctness and rollout risk remain unexamined.
- Rewriting the author's architecture in review when the real issue is a smaller bug, missing guardrail, or weak contract.
- Conflating preference with defect. Mark taste as optional and reserve blocking comments for correctness, safety, or maintainability risk.
- Collapsing multiple independent issues into one large comment thread instead of separating discrete findings with evidence.
- Using AI review output as authoritative instead of validating each finding against the actual diff and local context.

## Default Review Output

Default to:

- a short summary of intent and risk
- findings grouped by `P0` / `P1` / `P2` / `P3`
- `REQUIRED` vs `OPTIONAL` labeling
- concrete remediation: minimal diff, test case, or configuration fix
- follow-up questions only when requirements are genuinely unclear

Use [assets/core/review-comment-guidelines.md](assets/core/review-comment-guidelines.md) for phrasing and [assets/core/review-checklist-judgment.md](assets/core/review-checklist-judgment.md) for final pass judgment. Label comment intent using the [Conventional Comments](https://conventionalcomments.org/) convention (`suggestion:`, `issue:`, `question:`, `nitpick:`, `praise:`) so blocking vs. non-blocking intent is unambiguous without relying on tone.

## Navigation

Core references:

- [references/operational-playbook.md](references/operational-playbook.md)
- [references/automation-tools.md](references/automation-tools.md)
- [references/review-checklist-comprehensive.md](references/review-checklist-comprehensive.md)
- [references/looks-good-to-me-checklist.md](references/looks-good-to-me-checklist.md) — constructive, high-signal review practices ("Looks Good To Me")
- [references/implementing-effective-code-reviews-checklist.md](references/implementing-effective-code-reviews-checklist.md) — operational practices from "Implementing Effective Code Reviews"
- [references/security-focused-review-guide.md](references/security-focused-review-guide.md)
- [references/large-pr-review-strategies.md](references/large-pr-review-strategies.md)
- [references/code-review-metrics.md](references/code-review-metrics.md)
- [references/psychological-safety-guide.md](references/psychological-safety-guide.md)
- [references/dotnet-efcore-crypto-rules.md](references/dotnet-efcore-crypto-rules.md)
- [references/adversarial-review-protocol.md](references/adversarial-review-protocol.md) — stripped-context handoff and fixed-precedence finding reconciliation for pre-commit decision review
- [references/complexity-only-review-pass.md](references/complexity-only-review-pass.md) — narrow, tagged, over-engineering-only review pass as a fast complement to the full checklist
- [references/deterministic-vs-llm-routing.md](references/deterministic-vs-llm-routing.md) — pre-review deterministic file gate, size-gated planning-pass threshold, and self-refutation filter pass for AI review tooling

Templates:

- [assets/core/pull-request-description-template.md](assets/core/pull-request-description-template.md)
- [assets/core/review-comment-guidelines.md](assets/core/review-comment-guidelines.md)
- [assets/backend-api/api-review.md](assets/backend-api/api-review.md)
- [assets/web-frontend/frontend-review.md](assets/web-frontend/frontend-review.md)
- [assets/mobile/mobile-review.md](assets/mobile/mobile-review.md)
- [assets/infrastructure/infrastructure-review.md](assets/infrastructure/infrastructure-review.md)
- [assets/blockchain/crypto-review.md](assets/blockchain/crypto-review.md)

Sources:

- [data/sources.json](data/sources.json) - verified source set with platform status and replacements for retired links

## Freshness Protocol

When the user asks for:

- the best or latest code review tool
- current PR automation practices
- GitHub Copilot vs CodeRabbit vs Qodo vs platform-native options
- whether a tool is still relevant

you must:

1. Use web search.
2. Prefer official docs and release/status pages over vendor comparison blogs.
3. Use [data/sources.json](data/sources.json) as the starting source set.
4. Treat vendor metrics and case-study performance numbers as directional unless independently verified.

If web access is unavailable, say so and answer from `data/sources.json`, clearly marking time-sensitive advice as unverified.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

