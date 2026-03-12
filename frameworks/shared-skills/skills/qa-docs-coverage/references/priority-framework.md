# Documentation Priority Framework

This resource defines the framework for prioritizing documentation efforts based on impact, audience, and compliance requirements.

---

## Contents

- Priority Levels Overview
- Priority 1: External-Facing (Must Document)
- Priority 2: Internal Integration (Should Document)
- Priority 3: Developer Reference (Nice to Have)
- Prioritization Decision Tree
- Documentation Coverage by Category
- Documentation Debt Scoring
- Effort Estimation
- Compliance Considerations
- Re-Prioritization Triggers
- Related Resources

## Priority Levels Overview

| Priority | Audience | Impact | Timeline | Examples |
|----------|----------|--------|----------|----------|
| **Priority 1** | External integrators, compliance auditors | High - blocks adoption, legal/compliance risk | Immediate (within sprint) | Public APIs, webhooks, error codes, authentication |
| **Priority 2** | Internal developers, cross-team collaboration | Medium - slows development, impacts velocity | Short-term (2-3 sprints) | Internal APIs, events, database schema, background jobs |
| **Priority 3** | Individual developers, onboarding | Low - improves DX, reduces questions | Ongoing (backlog) | Configuration options, utilities, constants, internal workflows |

---

## Priority 1: External-Facing (Must Document)

### Definition

Documentation that affects **external integrators**, **compliance requirements**, or **production operations**. Missing documentation blocks adoption or creates legal/operational risk.

### Components

| Component | Documentation Required | Rationale |
|-----------|----------------------|-----------|
| **Public API endpoints** | OpenAPI spec + reference docs | External developers need contracts |
| **Webhook payloads** | Schema + examples + retry behavior | Integrators need to implement handlers |
| **Error codes** | Code + description + remediation | Support teams need troubleshooting guidance |
| **Authentication** | Flow diagrams + examples + scopes | Security-critical, must be clear |
| **Rate limits** | Limits + headers + retry guidance | Prevents abuse, sets expectations |
| **Data contracts** | Schemas + field descriptions + validation rules | Ensures correct data exchange |
| **SLA/SLO** | Uptime guarantees + response times | Sets expectations, compliance |

### Documentation Standards

1. **OpenAPI/Swagger Spec**: Machine-readable, versioned, includes examples
2. **Authentication Guide**: Step-by-step with code examples in 3+ languages
3. **Error Reference**: Searchable by code, includes HTTP status + remediation
4. **Webhook Guide**: Payload schemas, signature verification, retry logic
5. **Rate Limit Guide**: Current limits, headers, backoff strategies

### Timeline

Immediate (same sprint as feature launch)

### Success Criteria

- External developers can integrate without Slack/email support
- Support ticket volume for "how do I" questions decreases
- Compliance audits pass documentation requirements

---

## Priority 2: Internal Integration (Should Document)

### Definition

Documentation that affects **internal developers** and **cross-team collaboration**. Missing documentation slows feature development and increases onboarding time.

### Components

| Component | Documentation Required | Rationale |
|-----------|----------------------|-----------|
| **Internal API endpoints** | Endpoint list + request/response schemas | Teams need integration contracts |
| **Event/message schemas** | Topic + schema + producer/consumer mapping | Event-driven architectures need clarity |
| **Database schema** | ER diagram + entity descriptions + relationships | Data modeling decisions affect all teams |
| **Service contracts** | Interface + responsibilities + dependencies | Service boundaries must be clear |
| **Background jobs** | Schedule + behavior + monitoring + failure handling | Ops teams need runbook material |
| **External integrations** | Provider + endpoints + auth + error handling | Teams need to understand third-party dependencies |

### Documentation Standards

1. **API Reference**: Internal OpenAPI spec or endpoint table
2. **Event Catalog**: Topic registry with schemas and ownership
3. **ER Diagram**: Visual schema with entity descriptions
4. **Service Map**: Architecture diagram showing service dependencies
5. **Job Registry**: List of all background jobs with schedules

### Timeline

Short-term (2-3 sprints after initial implementation)

### Success Criteria

- New developers can understand system architecture in 1 day
- Cross-team integration PRs require minimal back-and-forth
- Onboarding time for new engineers decreases

---

## Priority 3: Developer Reference (Nice to Have)

### Definition

Documentation that improves **developer experience** and **code maintainability**. Missing documentation increases questions but doesn't block work.

### Components

| Component | Documentation Required | Rationale |
|-----------|----------------------|-----------|
| **Configuration options** | Option + type + default + description + example | Reduces "what does this do" questions |
| **Utilities/helpers** | Purpose + usage examples + edge cases | Encourages reuse over reimplementation |
| **Constants/enums** | Value + meaning + when to use | Clarifies magic numbers/strings |
| **Internal workflows** | Sequence diagrams + decision points | Helps with debugging and onboarding |
| **Development setup** | Local environment guide + dependencies | Speeds up onboarding |

### Documentation Standards

1. **Inline Code Comments**: For complex utilities, use JSDoc/XML doc comments
2. **Configuration Reference**: Auto-generated from config schema
3. **Development Guide**: README with setup, common tasks, troubleshooting
4. **Architecture Decision Records (ADRs)**: For non-obvious design choices

### Timeline

Ongoing (backlog, address during refactoring or onboarding sprints)

### Success Criteria

- Developers can find config options without reading source code
- "How do I" questions in Slack decrease
- Onboarding documentation rated 4+ / 5 by new hires

---

## Prioritization Decision Tree

```
New component discovered → Start here
    │
    ├─ Is it external-facing?
    │   ├─ Yes → Priority 1
    │   │   ├─ Public API? → OpenAPI spec required
    │   │   ├─ Webhook? → Schema + examples required
    │   │   └─ Authentication? → Flow diagrams required
    │   │
    │   └─ No → Continue to next question
    │
    ├─ Does it affect cross-team collaboration?
    │   ├─ Yes → Priority 2
    │   │   ├─ Internal API? → Endpoint list required
    │   │   ├─ Event/message? → Schema registry required
    │   │   ├─ Database? → ER diagram required
    │   │   └─ Background job? → Job registry required
    │   │
    │   └─ No → Continue to next question
    │
    └─ Is it used by multiple developers?
        ├─ Yes → Priority 3
        │   ├─ Utility? → Inline docs + examples
        │   └─ Config? → Schema + defaults
        │
        └─ No → Inline comments sufficient
```

---

## Documentation Coverage by Category

### API Layer

| Component | Priority | Documentation Type |
|-----------|----------|-------------------|
| Public REST endpoints | P1 | OpenAPI spec + reference guide |
| Private REST endpoints | P2 | OpenAPI spec or endpoint table |
| GraphQL schema | P1 (if public) / P2 (if internal) | Schema documentation + examples |
| WebSocket endpoints | P1 (if public) / P2 (if internal) | Connection guide + message schemas |
| gRPC services | P2 | Proto files + service docs |

### Service Layer

| Component | Priority | Documentation Type |
|-----------|----------|-------------------|
| Business logic services | P2 | Interface docs + responsibilities |
| Command handlers | P2 | Command schema + side effects |
| Query handlers | P2 | Query params + response schema |
| Domain models | P2 | Entity descriptions + invariants |

### Data Layer

| Component | Priority | Documentation Type |
|-----------|----------|-------------------|
| Database entities | P2 | ER diagram + descriptions |
| Migrations | P2 | Migration log with rationale |
| Stored procedures | P2 | Purpose + parameters + usage |
| Database views | P3 | Schema + purpose |

### Integration Layer

| Component | Priority | Documentation Type |
|-----------|----------|-------------------|
| External API clients | P2 | Provider + endpoints + auth |
| Webhook handlers | P1 (if public) / P2 (if internal) | Payload schema + verification |
| Message producers | P2 | Topic + schema + when published |
| Message consumers | P2 | Topic + schema + side effects |

### Infrastructure Layer

| Component | Priority | Documentation Type |
|-----------|----------|-------------------|
| Background jobs | P2 | Schedule + behavior + monitoring |
| Hosted services | P2 | Purpose + lifecycle + dependencies |
| Configuration options | P3 | Schema + defaults + examples |
| Deployment scripts | P2 | Purpose + usage + rollback |

---

## Documentation Debt Scoring

### Formula

```
Debt Score = (P1 gaps × 3) + (P2 gaps × 2) + (P3 gaps × 1)
```

### Interpretation

| Debt Score | Health | Action Required |
|------------|--------|-----------------|
| **0-10** | Excellent | Maintain current practices |
| **11-30** | Good | Address P1 gaps immediately |
| **31-60** | Moderate | Create documentation sprint plan |
| **61-100** | Poor | Major documentation initiative needed |
| **100+** | Critical | Consider documentation freeze (document before new features) |

### Example Calculation

```
Current state:
- 5 P1 gaps (public APIs)
- 12 P2 gaps (internal services, events)
- 20 P3 gaps (configs, utilities)

Debt Score = (5 × 3) + (12 × 2) + (20 × 1)
           = 15 + 24 + 20
           = 59 (Moderate)

Action: Create 2-sprint plan to address all P1 gaps + top 5 P2 gaps
```

---

## Effort Estimation

### Effort Guidelines

| Documentation Type | Typical Effort | Notes |
|-------------------|----------------|-------|
| **OpenAPI endpoint** | 30 min - 1 hour | Per endpoint, includes examples |
| **Event schema** | 15-30 min | Per topic, includes producer/consumer map |
| **Database entity** | 15 min | Per entity in ER diagram |
| **Service documentation** | 1-2 hours | Interface + responsibilities + dependencies |
| **Architecture diagram** | 2-4 hours | Initial creation, 30 min updates |
| **Configuration reference** | 30 min - 1 hour | Can be auto-generated from schema |

### Prioritization Matrix

| Impact | Effort | Priority | Action |
|--------|--------|----------|--------|
| High | Low | **P1** | Do immediately |
| High | High | **P1** | Break into increments |
| Medium | Low | **P2** | Schedule in next sprint |
| Medium | High | **P2** | Schedule in backlog |
| Low | Low | **P3** | Opportunistic (during refactoring) |
| Low | High | **P3** | Defer or skip |

---

## Compliance Considerations

### ISO 27001 / SOC 2

Requires documentation of:
- Access controls (P1)
- Data flow diagrams (P2)
- Change management processes (P2)
- Incident response procedures (P1)

### GDPR / Data Privacy

Requires documentation of:
- Personal data processing (P1)
- Data retention policies (P1)
- Data subject rights procedures (P1)
- Data breach response (P1)

### HIPAA (Healthcare)

Requires documentation of:
- PHI handling procedures (P1)
- Access controls (P1)
- Audit logs (P1)
- Business associate agreements (P1)

**Implication**: For regulated industries, many P2 items become P1 due to compliance requirements.

---

## Re-Prioritization Triggers

### When to Escalate Priority

- **P3 → P2**: Component used by 3+ teams, frequent questions in Slack
- **P2 → P1**: Component becomes externally exposed, compliance audit required
- **Any → P1**: Production incident caused by missing documentation

### When to Downgrade Priority

- **P1 → P2**: API deprecated or made internal-only
- **P2 → P3**: Service ownership consolidated to single team
- **Any → Archive**: Component deprecated and scheduled for removal

---

## Related Resources

- [Audit Workflows](audit-workflows.md) - How to discover and categorize components
- [Discovery Patterns](discovery-patterns.md) - How to find undocumented components
- [CI/CD Integration](cicd-integration.md) - How to enforce documentation standards
