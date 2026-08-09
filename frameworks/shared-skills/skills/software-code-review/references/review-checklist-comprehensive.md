# Comprehensive Code Review Checklist 

Based on research from Microsoft, Google, and industry leaders in code review practices.

## Table of Contents

- [Pre-Review Validation](#pre-review-validation)
- [PR Readiness](#pr-readiness)
- [Automated Checks Status](#automated-checks-status)
- [Functionality & Correctness (40% focus)](#functionality-&-correctness-40%-focus)
- [Core Logic](#core-logic)
- [Data Handling](#data-handling)
- [Error Scenarios](#error-scenarios)
- [Security (20% focus)](#security-20%-focus)
- [Input Validation](#input-validation)
- [Authentication & Authorization](#authentication-&-authorization)
- [Data Protection](#data-protection)
- [Dependencies](#dependencies)
- [Dependency Upgrades](#dependency-upgrades)
- [Architecture & Design (30% focus)](#architecture-&-design-30%-focus)
- [Code Organization](#code-organization)
- [Design Patterns](#design-patterns)
- [API Design](#api-design)
- [Error Handling Architecture](#error-handling-architecture)
- [Performance (10% focus - but critical)](#performance-10%-focus-but-critical)
- [Computational Efficiency](#computational-efficiency)
- [Database Performance](#database-performance)
- [Resource Management](#resource-management)
- [Frontend Performance (if applicable)](#frontend-performance-if-applicable)
- [Readability & Maintainability (10% focus)](#readability-&-maintainability-10%-focus)
- [Testing (Critical - must be comprehensive)](#testing-critical-must-be-comprehensive)
- [Test Coverage](#test-coverage)
- [Test Types](#test-types)
- [Test Quality](#test-quality)
- [Test Structure (AAA Pattern)](#test-structure-aaa-pattern)
- [AI-Specific Considerations ()](#ai-specific-considerations)
- [AI-Generated Code](#ai-generated-code)
- [LLM Integration (if applicable)](#llm-integration-if-applicable)
- [Review Process Metadata](#review-process-metadata)
- [Review Size Metrics](#review-size-metrics)
- [Timing Expectations](#timing-expectations)
- [Comment Categories](#comment-categories)
- [Common Pitfalls to Check](#common-pitfalls-to-check)
- [Logic Errors](#logic-errors)
- [Security Vulnerabilities](#security-vulnerabilities)
- [Performance Issues](#performance-issues)
- [Maintainability Problems](#maintainability-problems)
- [Psychological Safety Checklist](#psychological-safety-checklist)
- [Communication Style](#communication-style)
- [Feedback Quality](#feedback-quality)
- [Post-Review Actions](#post-review-actions)
- [After Providing Feedback](#after-providing-feedback)
- [After Receiving Feedback](#after-receiving-feedback)
- [Metrics to Track](#metrics-to-track)
- [Effectiveness Metrics](#effectiveness-metrics)
- [Quality Metrics](#quality-metrics)
- [References](#references)

## Pre-Review Validation

### PR Readiness
- [ ] PR title and description clearly explain the "why" (not just "what")
- [ ] Changes are reasonably small (<= ~400 LOC is a common guideline); split if larger
- [ ] Linked to relevant issue/ticket with acceptance criteria
- [ ] CI/CD pipeline is green (all automated checks passing)
- [ ] No merge conflicts

### Automated Checks Status
- [ ] Linters passed (no style violations)
- [ ] Tests passed (unit, integration, E2E)
- [ ] Code coverage meets team threshold and covers critical paths
- [ ] Security scanners passed (Snyk, Dependabot, etc.)
- [ ] Build successful

## Functionality & Correctness (40% focus)

### Core Logic
- [ ] Code implements stated requirements accurately
- [ ] Business logic is correct and complete
- [ ] Edge cases are handled (null, empty, boundary values)
- [ ] No off-by-one errors or logic bugs
- [ ] Async operations handled correctly (race conditions, deadlocks)

### Data Handling
- [ ] Data transformations are correct
- [ ] Type conversions are safe
- [ ] Null/undefined checks where needed
- [ ] Data validation before processing
- [ ] Proper handling of optional vs required fields

### Error Scenarios
- [ ] All error paths identified and handled
- [ ] No silent failures (empty catch blocks)
- [ ] Errors logged with sufficient context
- [ ] User-facing error messages are helpful
- [ ] Graceful degradation where appropriate

## Security (20% focus)

### Input Validation
- [ ] All external inputs validated (HTTP, CLI, files, messages)
- [ ] Whitelist validation (not just blacklist)
- [ ] Input length limits enforced
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (proper escaping/sanitization)
- [ ] Command injection prevention
- [ ] Path traversal prevention

### Authentication & Authorization
- [ ] Authentication required for protected endpoints
- [ ] Authorization checks on every sensitive operation
- [ ] No authentication bypasses possible
- [ ] Session management is secure
- [ ] Token/credential expiration handled

### Data Protection
- [ ] No credentials, API keys, or secrets in code
- [ ] Sensitive data not logged
- [ ] PII handled according to privacy requirements
- [ ] Encryption used for sensitive data at rest
- [ ] TLS/HTTPS for data in transit

### Dependencies
- [ ] No known vulnerabilities in dependencies
- [ ] Dependencies are up-to-date
- [ ] Minimal dependency footprint
- [ ] License compatibility checked

### Dependency Upgrades

*Attribution: pattern from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), commit `7676817`, `skills/code-review-and-quality/SKILL.md`. MIT license. Recorded 2026-08-09 in `docs/research/2026-08-09-skill-addyosmani-agent-skills-scan.md`.*

The "adding a new dependency" checks above cover security posture at introduction time. An upgrade PR is a different review shape — the package is already trusted, but the version bump itself can carry breaking changes, supply-chain risk, or masked transitive drift:

- [ ] Changelog read, not just the version number — a semver bump alone does not prove the change is safe; read what actually changed
- [ ] One dependency per change — a PR that bumps multiple unrelated packages together is rejected or split; isolate each upgrade so a regression traces to a single cause
- [ ] Major version bumps carry an explicit breaking-changes check against the changelog, not an assumption that CI green means safe
- [ ] Lockfile is honest — the lockfile diff matches the stated dependency change exactly; unexplained transitive version churn in the lockfile is investigated, not waved through as noise

## Architecture & Design (30% focus)

### Code Organization
- [ ] Single Responsibility Principle followed
- [ ] Separation of concerns maintained
- [ ] Proper layering (presentation, business, data)
- [ ] No circular dependencies
- [ ] Module boundaries are clear

### Design Patterns
- [ ] Appropriate design patterns used
- [ ] No anti-patterns introduced
- [ ] DRY principle followed (no unnecessary duplication)
- [ ] Code is not over-engineered
- [ ] Abstractions are at the right level

### Behavioral Infrastructure Review
For changes to shared packages that alter runtime semantics (e.g., commit behavior, failure routing, retry policy):
- [ ] Review before rollout — behavioral infrastructure changes benefit from review-first workflow since they can introduce subtle semantic shifts (shutdown handling, dead-task behavior, missing pipeline coverage) that implementation-only iteration misses
- [ ] Backward compatibility rule is explicit and locked before code starts
- [ ] New behavior is opt-in, not a default flip for existing consumers
- [ ] Legacy extension points and shared-consumer composition have dedicated regression coverage

### API Design
- [ ] Public interfaces are intuitive
- [ ] Function signatures are clear and consistent
- [ ] Return types are appropriate
- [ ] Breaking changes are documented
- [ ] Backwards compatibility considered

### Error Handling Architecture
- [ ] Consistent error handling strategy
- [ ] Error types are meaningful
- [ ] Errors propagate correctly through layers
- [ ] Retry logic where appropriate
- [ ] Circuit breakers for external services

## Performance (10% focus - but critical)

### Computational Efficiency
- [ ] Avoid premature optimization; profile and tune measured hotspots only
- [ ] No O(n²) algorithms where O(n) is possible
- [ ] No unnecessary computation in loops
- [ ] Lazy loading used appropriately
- [ ] Caching implemented where beneficial

### Database Performance
- [ ] No N+1 query problems
- [ ] Indexes used appropriately
- [ ] Query optimization considered
- [ ] Connection pooling implemented
- [ ] Batch operations where possible

### Resource Management
- [ ] No memory leaks (event listeners cleaned up)
- [ ] File handles closed
- [ ] Database connections released
- [ ] Large datasets processed in chunks
- [ ] Resource pooling where appropriate

### Frontend Performance (if applicable)
- [ ] No unnecessary re-renders
- [ ] Bundle size reasonable
- [ ] Code splitting implemented
- [ ] Images optimized
- [ ] Lazy loading for routes/components

## Readability & Maintainability (10% focus)

Use the clean code standard as the single source of truth. In review comments, cite `CC-*` IDs instead of restating rules:

- Standard: [../../software-clean-code-standard/references/clean-code-standard.md](../../software-clean-code-standard/references/clean-code-standard.md)
- Common categories: `CC-NAM` (naming), `CC-FUN` (functions), `CC-FLOW` (control flow), `CC-ERR` (errors), `CC-DOC` (docs)

Prefer automation for formatting and mechanical style enforcement; use human review time on correctness, risk, and intent.

## Testing (Critical - must be comprehensive)

### Test Coverage
- [ ] New functionality has tests
- [ ] Critical paths have 100% coverage
- [ ] Business logic has 90%+ coverage
- [ ] Overall coverage ≥80%
- [ ] Changed code paths are tested

### Test Types
- [ ] Unit tests for business logic
- [ ] Integration tests for component interactions
- [ ] E2E tests for critical user flows
- [ ] Regression tests for bug fixes
- [ ] Performance tests for critical paths (if needed)

### Test Quality
- [ ] Tests are independent (no interdependencies)
- [ ] Tests are deterministic (no flaky tests)
- [ ] Tests have meaningful assertions
- [ ] Test names clearly describe what's being tested
- [ ] Edge cases and error scenarios tested

### Test Structure (AAA Pattern)
- [ ] Arrange section is clear
- [ ] Act section is minimal
- [ ] Assert section is comprehensive
- [ ] Mocking is appropriate (not excessive)
- [ ] Test data is realistic

## AI-Specific Considerations ()

### AI-Generated Code
- [ ] AI-generated code has been reviewed (not blindly accepted)
- [ ] Logic correctness verified
- [ ] Security implications checked
- [ ] Performance characteristics validated
- [ ] Tests added for AI-generated code

### LLM Integration (if applicable)
- [ ] Prompt injection prevention
- [ ] Output sanitization
- [ ] Rate limiting and cost controls
- [ ] Fallback behavior defined
- [ ] PII not sent to external LLMs

## Review Process Metadata

### Review Size Metrics
- **Optimal review size**: 200-400 lines (Cisco/SmartBear peer-review research; see `references/large-pr-review-strategies.md`)
- **Review time estimate**: roughly 60-90 minutes for a 200-400 LOC review; pace well under ~400-450 LOC/hour
- **If >400 lines**: Request split into multiple PRs
- **Prioritization**: Apply 80/20; surface correctness/security blockers before style or micro-optimizations

### Timing Expectations
- **Initial review**: Within 24 hours
- **Follow-up**: Within 4-8 hours
- **Final approval**: Same day after changes

### Comment Categories
- **REQUIRED**: Must fix before merge (bugs, security, critical design flaws)
- **SUGGESTION**: Should consider (design improvements, refactoring)
- **QUESTION**: Clarification needed
- **PRAISE**: Positive feedback (reinforces good practices)

## Common Pitfalls to Check

### Logic Errors
- [ ] Off-by-one errors
- [ ] Race conditions in concurrent code
- [ ] Incorrect null checks (== vs ===)
- [ ] Timezone handling issues
- [ ] Integer overflow
- [ ] Floating-point comparison

### Security Vulnerabilities
- [ ] Hardcoded credentials
- [ ] Missing CSRF protection
- [ ] Insecure random number generation
- [ ] Weak cryptography
- [ ] Missing rate limiting
- [ ] Unvalidated redirects

### Performance Issues
- [ ] N+1 queries
- [ ] Missing database indexes
- [ ] Unnecessary data fetching
- [ ] Large objects in memory
- [ ] Synchronous operations blocking

### Maintainability Problems
- [ ] Magic numbers (no explanation)
- [ ] Deep nesting (>3 levels)
- [ ] Long functions (>50 lines)
- [ ] Tight coupling
- [ ] Global state mutation

## Psychological Safety Checklist

### Communication Style
- [ ] Comments are respectful and constructive
- [ ] Questions rather than commands ("Consider..." vs "Change this")
- [ ] Explanations for suggestions ("This might cause X because Y")
- [ ] Acknowledgment of good practices
- [ ] Focus on code, not the person

### Feedback Quality
- [ ] Specific and actionable
- [ ] Includes examples where helpful
- [ ] Prioritized (critical vs nice-to-have)
- [ ] Balanced (positives and improvements)
- [ ] Educational (helps reviewer learn)

## Post-Review Actions

### After Providing Feedback
- [ ] Respond to author questions promptly
- [ ] Review updated code in follow-up commits
- [ ] Approve when all REQUIRED items addressed
- [ ] Thank the author for addressing feedback

### After Receiving Feedback
- [ ] Address all REQUIRED items
- [ ] Respond to QUESTIONS with clarification
- [ ] Consider SUGGESTIONS thoughtfully
- [ ] Ask for clarification if feedback unclear
- [ ] Re-request review when ready

## Metrics to Track

### Effectiveness Metrics
- Average review turnaround time
- Defects found in review vs production
- Review comment resolution rate
- Time to merge after first review
- Number of review iterations

### Quality Metrics
- Code coverage trends
- Production bug rate
- Security vulnerabilities found
- Performance regression incidents
- Technical debt accumulation

## References

- Microsoft: Code With Engineering Playbook - Code Reviews
- Google Engineering Practices: Code Review
- OWASP: Code Review Guide
- SmartBear: Peer Code Review Best Practices
- See `../data/sources.json` for the current verified source set
