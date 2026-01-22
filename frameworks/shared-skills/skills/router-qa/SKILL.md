---
name: router-qa
description: "QA skill orchestrator: routes quality engineering questions through 12 specialized skills covering testing, observability, resilience, refactoring, debugging, and documentation quality."
metadata:
  version: "1.1"
  skills_count: 12
---

# Router: Quality Assurance

Master orchestrator for quality engineering that routes testing, observability, resilience, debugging, and documentation quality questions through 12 specialized QA skills.

---

## Quick Decision Tree

```text
QA QUESTION
    │
    ├─► "What tests do I need?" ──────────► qa-testing-strategy
    │                                        └─► Test pyramid, coverage, risk-based
    │
    ├─► "Write E2E tests" ────────────────► qa-testing-playwright
    │                                        └─► Selectors, page objects, CI/CD
    │
    ├─► "Test iOS app" ───────────────────► qa-testing-ios
    │                                        └─► XCTest, simulators, device matrix
    │
    ├─► "Test mobile app" ────────────────► qa-testing-mobile
    │                                        └─► Cross-platform, Android + iOS
    │
    ├─► "Test Android app" ──────────────► qa-testing-android
    │                                        └─► Espresso, UIAutomator, Compose
    │
    ├─► "Test API contracts" ─────────────► qa-api-testing-contracts
    │                                        └─► OpenAPI, Pact, schema validation
    │
    ├─► "Test LLM agent" ─────────────────► qa-agent-testing
    │                                        └─► Scenarios, scoring, refusals
    │
    ├─► "Debug this issue" ───────────────► qa-debugging
    │                                        └─► Stack traces, logging, profiling
    │
    ├─► "Setup monitoring" ───────────────► qa-observability
    │                                        └─► OpenTelemetry, SLOs, tracing
    │
    ├─► "Handle failures" ────────────────► qa-resilience
    │                                        └─► Circuit breakers, retries, chaos
    │
    ├─► "Refactor safely" ────────────────► qa-refactoring
    │                                        └─► Characterization tests, seams
    │
    └─► "Check docs coverage" ────────────► qa-docs-coverage
                                             └─► Gap analysis, runbook validation

```

---

## Skill Registry (12 Skills)

### Testing Skills (7)

| Skill | Purpose | Key Triggers |
|-------|---------|--------------|
| `qa-testing-strategy` | Test pyramid, risk-based testing, coverage | "test strategy", "what tests", "coverage" |
| `qa-testing-playwright` | E2E web testing with Playwright | "E2E test", "Playwright", "browser test" |
| `qa-testing-ios` | iOS testing with XCTest/XCUITest | "iOS test", "XCTest", "simulator" |
| `qa-testing-android` | Android testing with Espresso/UIAutomator | "Android test", "Espresso", "UIAutomator", "Compose test" |
| `qa-testing-mobile` | Cross-platform mobile testing | "mobile test", "cross-platform", "device matrix" |
| `qa-api-testing-contracts` | API schema and contract testing | "API test", "contract", "OpenAPI", "Pact" |
| `qa-agent-testing` | LLM agent and persona testing | "agent test", "LLM test", "refusal", "scoring" |

### Quality Skills (5)

| Skill | Purpose | Key Triggers |
|-------|---------|--------------|
| `qa-debugging` | Debugging, logging, profiling | "debug", "error", "stack trace", "profile" |
| `qa-observability` | Metrics, traces, logs, SLOs | "monitor", "tracing", "SLO", "OpenTelemetry" |
| `qa-resilience` | Circuit breakers, retries, chaos | "circuit breaker", "retry", "chaos", "timeout" |
| `qa-refactoring` | Safe refactoring, tech debt | "refactor", "code smell", "tech debt" |
| `qa-docs-coverage` | Documentation quality gates | "docs coverage", "undocumented", "runbook" |
| `claude-code-project-memory` | Large codebase documentation | "CLAUDE.md", "AGENTS.md", "large codebase", "100K LOC" |

---

## Domain Detection

### Domain 1: TEST PLANNING

**Triggers**: "what tests", "test strategy", "coverage", "test pyramid", "shift-left", "risk-based"

**Route to**: `qa-testing-strategy`

**Example questions**:
- "What tests do I need for this API?"
- "How do I prioritize testing?"
- "What's the right test coverage target?"

### Domain 2: E2E & UI TESTING

**Triggers**: "E2E", "end-to-end", "Playwright", "browser test", "UI test", "page object", "visual test"

**Route to**: `qa-testing-playwright`

**Example questions**:
- "Write Playwright tests for login"
- "How to handle flaky E2E tests?"
- "Best practices for page objects?"

### Domain 3: MOBILE TESTING

**Triggers**: "iOS", "Android", "mobile", "XCTest", "XCUITest", "Espresso", "UIAutomator", "Appium", "simulator", "emulator", "device"

| Trigger | Route |
|---------|-------|
| iOS-only | `qa-testing-ios` |
| Android-only | `qa-testing-android` |
| Cross-platform | `qa-testing-mobile` |

**Example questions**:
- "Test iOS app on simulator"
- "Write Espresso tests for Android login"
- "Test Jetpack Compose UI"
- "Device matrix for Android testing"
- "Cross-platform mobile test strategy"

### Domain 4: API & CONTRACT TESTING

**Triggers**: "API test", "contract test", "OpenAPI", "GraphQL test", "gRPC", "Pact", "schema validation"

**Route to**: `qa-api-testing-contracts`

**Example questions**:
- "Write contract tests for REST API"
- "Validate OpenAPI schema"
- "Consumer-driven contract testing"

### Domain 5: AGENT TESTING

**Triggers**: "agent test", "LLM test", "persona", "refusal", "AI safety", "scoring rubric", "test harness"

**Route to**: `qa-agent-testing`

**Example questions**:
- "Create test suite for chatbot"
- "Test LLM refusal boundaries"
- "Score agent responses"

### Domain 6: DEBUGGING

**Triggers**: "debug", "error", "bug", "crash", "stack trace", "logging", "profiling", "troubleshoot"

**Route to**: `qa-debugging`

**Example questions**:
- "Debug memory leak"
- "Analyze this stack trace"
- "Setup structured logging"

### Domain 7: OBSERVABILITY

**Triggers**: "monitor", "metrics", "tracing", "logging", "SLO", "SLI", "OpenTelemetry", "APM", "alert"

**Route to**: `qa-observability`

**Example questions**:
- "Setup OpenTelemetry for Node.js"
- "Define SLOs for API"
- "Distributed tracing strategy"

### Domain 8: RESILIENCE

**Triggers**: "circuit breaker", "retry", "timeout", "backoff", "chaos", "fault injection", "degradation", "health check"

**Route to**: `qa-resilience`

**Example questions**:
- "Implement circuit breaker"
- "Retry strategy for external APIs"
- "Setup chaos engineering"

### Domain 9: REFACTORING

**Triggers**: "refactor", "code smell", "tech debt", "legacy code", "characterization test", "strangler fig"

**Route to**: `qa-refactoring`

**Example questions**:
- "Refactor this legacy code safely"
- "Add tests before refactoring"
- "Manage technical debt"

### Domain 10: DOCUMENTATION QUALITY

**Triggers**: "docs coverage", "undocumented", "runbook", "API docs audit", "stale docs", "CLAUDE.md", "AGENTS.md", "large codebase", "project memory"

**Route to**: `qa-docs-coverage` (audit) → `claude-code-project-memory` (large codebase setup)

**Example questions**:

- "Audit documentation coverage"
- "Find undocumented APIs"
- "Validate runbooks"
- "Set up CLAUDE.md for large codebase"
- "Create AGENTS.md for cross-platform support"

---

## Workflow Patterns

### Pattern 1: Test-First Development

```text
START
  │
  ▼
qa-testing-strategy ────────► Define test pyramid
  │
  ├─► Unit tests ──────────► Write inline
  ├─► Integration tests ───► Write with mocks
  └─► E2E tests ───────────► qa-testing-playwright
  │
  ▼
qa-api-testing-contracts ──► Contract tests (if API)
  │
  ▼
TESTS COMPLETE
```

### Pattern 2: Bug Investigation

```text
BUG REPORTED
  │
  ▼
qa-debugging ──────────────► Analyze logs, traces, stack
  │
  ├─► Need more visibility? → qa-observability
  ├─► Failure mode issue? ──→ qa-resilience
  └─► Code quality issue? ──→ qa-refactoring
  │
  ▼
ROOT CAUSE IDENTIFIED
  │
  ▼
qa-testing-strategy ───────► Add regression test
  │
  ▼
BUG FIXED + COVERED
```

### Pattern 3: Production Hardening

```text
PRE-PRODUCTION
  │
  ▼
qa-resilience ─────────────► Error handling, retries
  │
  ▼
qa-observability ──────────► Metrics, tracing, SLOs
  │
  ▼
qa-testing-strategy ───────► Smoke + E2E tests
  │
  ▼
PRODUCTION READY
  │
  ▼
qa-resilience ─────────────► Chaos experiments (post-launch)
```

### Pattern 4: Legacy Modernization

```text
LEGACY CODEBASE
  │
  ▼
qa-refactoring ────────────► Characterization tests
  │
  ▼
qa-testing-strategy ───────► Add missing test coverage
  │
  ▼
qa-refactoring ────────────► Incremental refactoring
  │
  ▼
qa-docs-coverage ──────────► Document updated code
  │
  ▼
MODERNIZED
```

### Pattern 6: Large Codebase Documentation (100K-1M LOC)

```text
LARGE CODEBASE
  │
  ▼
claude-code-project-memory ► Hierarchical CLAUDE.md setup
  │                          (root + subdirectory docs)
  ├─► Root CLAUDE.md ────────► Architecture, conventions
  ├─► Subdirectory docs ─────► Module-specific context
  ├─► AGENTS.md symlink ─────► Cross-platform support
  │
  ▼
qa-docs-coverage ──────────► Audit existing documentation
  │
  ▼
docs-codebase ─────────────► Fill critical gaps
  │
  ▼
LLM-READY CODEBASE
```

### Pattern 5: LLM Agent Quality

```text
AGENT DEVELOPMENT
  │
  ▼
qa-agent-testing ──────────► Define test scenarios
  │
  ├─► Must-ace tasks ──────► Core functionality
  ├─► Refusal tests ───────► Safety boundaries
  └─► Scoring rubric ──────► Quality metrics
  │
  ▼
qa-observability ──────────► Token usage, latency metrics
  │
  ▼
VALIDATED AGENT
```

---

## Skill Chains

### Chain: Complete QA Setup

```
qa-testing-strategy → qa-testing-playwright → qa-api-testing-contracts
     ↓
qa-resilience → qa-observability → qa-debugging
     ↓
qa-refactoring → qa-docs-coverage
```

### Chain: Incident Response

```
qa-debugging → qa-observability → qa-resilience → qa-refactoring
```

### Chain: Mobile App Testing

```
qa-testing-strategy → qa-testing-mobile → qa-testing-ios (if iOS) → qa-testing-android (if Android)
```

---

## Quality Gates

### Pre-Release Checklist

| Gate | Skill | Criteria |
|------|-------|----------|
| Test coverage | `qa-testing-strategy` | >80% unit, >60% integration |
| E2E passing | `qa-testing-playwright` | Critical paths green |
| API contracts | `qa-api-testing-contracts` | Schema validation passing |
| Error handling | `qa-resilience` | Circuit breakers configured |
| Monitoring | `qa-observability` | SLOs defined, alerts set |
| Docs | `qa-docs-coverage` | API + README complete |

### Post-Incident Checklist

| Gate | Skill | Action |
|------|-------|--------|
| Root cause | `qa-debugging` | Document findings |
| Regression test | `qa-testing-strategy` | Add test for failure mode |
| Prevention | `qa-resilience` | Add/tune circuit breaker |
| Visibility | `qa-observability` | Add missing traces/alerts |

---

## Routing Matrix

| User Intent | Primary Skill | Supporting Skills |
|-------------|---------------|-------------------|
| Plan tests | `qa-testing-strategy` | `qa-testing-playwright`, `qa-api-testing-contracts` |
| Write E2E | `qa-testing-playwright` | `qa-testing-strategy` |
| Test mobile | `qa-testing-mobile`, `qa-testing-ios`, or `qa-testing-android` | `qa-testing-strategy` |
| Test API | `qa-api-testing-contracts` | `qa-testing-strategy` |
| Test agent | `qa-agent-testing` | `qa-testing-strategy` |
| Debug issue | `qa-debugging` | `qa-observability`, `qa-resilience` |
| Setup monitoring | `qa-observability` | `qa-debugging` |
| Add resilience | `qa-resilience` | `qa-observability` |
| Refactor code | `qa-refactoring` | `qa-testing-strategy` |
| Audit docs | `qa-docs-coverage` | `claude-code-project-memory` |
| Large codebase setup | `claude-code-project-memory` | `qa-docs-coverage`, `docs-codebase` |

---

## Cross-Router Handoffs

### To router-engineering

When user needs implementation:
- "Build the feature" → Route to `software-backend` or `software-frontend`
- "Implement the fix" → Route to relevant engineering skill

### To router-operations

When user needs deployment/infra:
- "Deploy to production" → Route to `ops-devops-platform`
- "Setup CI/CD" → Route to `ops-devops-platform`

### From router-operations

When operations router detects QA needs:
- "Test strategy" → Route here
- "Debug production issue" → Route here
- "Add resilience" → Route here

---

## Quick Reference Commands

| Need | Do This |
|------|---------|
| Test strategy | → `qa-testing-strategy` |
| E2E tests | → `qa-testing-playwright` |
| iOS tests | → `qa-testing-ios` |
| Android tests | → `qa-testing-android` |
| Mobile tests | → `qa-testing-mobile` |
| API tests | → `qa-api-testing-contracts` |
| Agent tests | → `qa-agent-testing` |
| Debug issue | → `qa-debugging` |
| Monitoring | → `qa-observability` |
| Resilience | → `qa-resilience` |
| Refactoring | → `qa-refactoring` |
| Doc quality | → `qa-docs-coverage` |

---

## Related Routers

| Router | Relationship |
|--------|--------------|
| `router-operations` | Parent router; includes QA + DevOps + git |
| `router-engineering` | Handoff target for implementation tasks |
| `router-startup` | Handoff target for business/product questions |
