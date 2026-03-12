# Documentation Coverage Report

**Project**: [Project Name]
**Generated**: YYYY-MM-DD
**Auditor**: [Human/AI Name]
**Audit Type**: [Full / Incremental / Targeted]

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Coverage** | X% |
| **Components Discovered** | N |
| **Components Documented** | M |
| **Critical Gaps** | P |
| **Documentation Health** | Good / Moderate / Poor |

### Key Findings

1. [Most significant gap]
2. [Second most significant gap]
3. [Third most significant gap]

### Recommendations

1. **Immediate**: [Action for critical gaps]
2. **Short-term**: [Action for important gaps]
3. **Ongoing**: [Process improvements]

---

## Coverage by Category

### API Layer

| Component | Location | Documented | Doc Location | Priority |
|-----------|----------|------------|--------------|----------|
| PublicApi Controllers | `sources/presentation/PublicApi/` | Yes/No | `docs/api/` | P1/P2/P3 |
| PrivateApi Controllers | `sources/presentation/PrivateApi/` | Yes/No | | |
| OpenAPI Spec | `openapi/` | Yes/No | | |
| Error Codes | | Yes/No | | |
| Authentication | | Yes/No | | |

**API Coverage**: X / Y endpoints (Z%)

### Service Layer

| Component | Location | Documented | Doc Location | Priority |
|-----------|----------|------------|--------------|----------|
| Commands | `sources/core/*/Commands/` | Yes/No | | |
| Handlers | `sources/core/*/Handlers/` | Yes/No | | |
| Services | `sources/core/*/Services/` | Yes/No | | |

**Service Coverage**: X / Y services (Z%)

### Data Layer

| Component | Location | Documented | Doc Location | Priority |
|-----------|----------|------------|--------------|----------|
| DbContexts | `sources/infrastructure/` | Yes/No | | |
| Entities | `sources/core/*/Models/` | Yes/No | | |
| Migrations | | Yes/No | | |

**Data Coverage**: X / Y entities (Z%)

### Events/Messaging

| Component | Location | Documented | Doc Location | Priority |
|-----------|----------|------------|--------------|----------|
| Kafka Topics | | Yes/No | | |
| Message Schemas | `sources/core/*/Models/Kafka/` | Yes/No | | |
| Producers | | Yes/No | | |
| Consumers | | Yes/No | | |

**Event Coverage**: X / Y events (Z%)

### Infrastructure

| Component | Location | Documented | Doc Location | Priority |
|-----------|----------|------------|--------------|----------|
| Background Jobs | `sources/infrastructure/*/Jobs/` | Yes/No | | |
| Hosted Services | `sources/infrastructure/*/HostedServices/` | Yes/No | | |
| Configuration | `sources/core/*/Configuration/` | Yes/No | | |

**Infrastructure Coverage**: X / Y components (Z%)

### External Integrations

| Integration | Location | Documented | Doc Location | Priority |
|-------------|----------|------------|--------------|----------|
| [Provider 1] | | Yes/No | | |
| [Provider 2] | | Yes/No | | |
| Webhooks | | Yes/No | | |

**Integration Coverage**: X / Y integrations (Z%)

---

## Gap Analysis

### Critical Gaps (Priority 1)

These gaps affect external integrators, compliance, or operational safety.

| # | Component | Type | Impact | Effort | Owner |
|---|-----------|------|--------|--------|-------|
| 1 | | API | High | Medium | |
| 2 | | Events | High | Low | |
| 3 | | Config | High | Low | |

### Important Gaps (Priority 2)

These gaps affect internal developers or cross-team collaboration.

| # | Component | Type | Impact | Effort | Owner |
|---|-----------|------|--------|--------|-------|
| 1 | | Service | Medium | Medium | |
| 2 | | Data | Medium | High | |

### Nice to Have (Priority 3)

These gaps are helpful but not blocking.

| # | Component | Type | Impact | Effort | Owner |
|---|-----------|------|--------|--------|-------|
| 1 | | Utility | Low | Low | |
| 2 | | Internal | Low | Low | |

---

## Outdated Documentation

Documentation that exists but may not match current code:

| Document | Last Updated | Code Changed | Action Needed |
|----------|--------------|--------------|---------------|
| | YYYY-MM-DD | Yes/No | Update/Remove/Verify |

---

## Documentation Debt Score

```
Debt Score = (Critical Gaps * 3) + (Important Gaps * 2) + (Nice to Have * 1)
Current Score: X
Target Score: Y (reduce by Z% by [date])
```

---

## Action Plan

### Sprint 1 (Immediate)

- [ ] Document [Critical Gap 1]
- [ ] Document [Critical Gap 2]
- [ ] Update [Outdated Doc 1]

### Sprint 2-3 (Short-term)

- [ ] Document [Important Gap 1]
- [ ] Document [Important Gap 2]
- [ ] Create [Missing Diagram]

### Ongoing

- [ ] Add documentation check to PR template
- [ ] Schedule quarterly audit
- [ ] Assign documentation owners

---

## Audit Metadata

| Field | Value |
|-------|-------|
| Scan Method | Manual / Automated / Hybrid |
| Files Scanned | N |
| Patterns Used | See [discovery patterns] |
| Duration | X hours |
| Tools Used | [List tools] |

---

## Next Audit

**Scheduled**: YYYY-MM-DD
**Focus Areas**: [Areas to re-audit]
**Success Criteria**: Coverage > X%, Critical Gaps = 0
