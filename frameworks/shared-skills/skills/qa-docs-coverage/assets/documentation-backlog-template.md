# Documentation Backlog

**Project**: [Project Name]
**Last Updated**: YYYY-MM-DD
**Backlog Owner**: [Name/Team]

---

## Summary

| Status | Count |
|--------|-------|
| In Progress | X |
| To Do (P1) | X |
| To Do (P2) | X |
| To Do (P3) | X |
| Blocked | X |
| Completed | X |

---

## In Progress

| Task | Owner | Started | ETA | Notes |
|------|-------|---------|-----|-------|
| | @owner | YYYY-MM-DD | YYYY-MM-DD | |

---

## To Do - Priority 1 (Critical)

External-facing, compliance, or operational safety documentation.

| Task | Type | Effort | Template | Notes |
|------|------|--------|----------|-------|
| Document PrivateApi endpoints | API | High | [api-docs-template](../../docs-codebase/assets/api-reference/api-docs-template.md) | |
| Create Kafka event schema reference | Events | Medium | Custom | |
| Document error codes | API | Low | Custom | |
| Create database ER diagram | Data | Medium | Custom | |

---

## To Do - Priority 2 (Important)

Internal developer documentation and cross-team collaboration.

| Task | Type | Effort | Template | Notes |
|------|------|--------|----------|-------|
| Document service layer contracts | Service | High | Custom | |
| Document background jobs | Ops | Medium | Custom | |
| Create configuration reference | Config | Medium | Custom | |
| Document webhook validation | Integration | Low | Custom | |

---

## To Do - Priority 3 (Nice to Have)

Developer convenience and completeness.

| Task | Type | Effort | Template | Notes |
|------|------|--------|----------|-------|
| Document utility classes | Code | Low | Inline | |
| Add code examples to existing docs | Docs | Low | N/A | |
| Create troubleshooting guide | Ops | Medium | Custom | |

---

## Blocked

| Task | Blocked By | Since | Action Needed |
|------|------------|-------|---------------|
| | [Reason] | YYYY-MM-DD | [What unblocks] |

---

## Completed

| Task | Completed | By | Location |
|------|-----------|-----|----------|
| | YYYY-MM-DD | @owner | `docs/path/file.md` |

---

## Templates Reference

Quick links to documentation templates:

| Template | Use For | Location |
|----------|---------|----------|
| API Docs | REST endpoints | [api-docs-template.md](../../docs-codebase/assets/api-reference/api-docs-template.md) |
| ADR | Architecture decisions | [adr-template.md](../../docs-codebase/assets/architecture/adr-template.md) |
| README | Project overview | [readme-template.md](../../docs-codebase/assets/project-management/readme-template.md) |
| Changelog | Release notes | [changelog-template.md](../../docs-codebase/assets/project-management/changelog-template.md) |
| Tech Spec | Technical specs | [tech-spec-template.md](../../docs-ai-prd/assets/spec/tech-spec-template.md) |

---

## Conventions

### Effort Estimates

- **Low**: < 2 hours
- **Medium**: 2-8 hours
- **High**: > 8 hours (consider breaking down)

### Task Types

- **API**: Endpoint documentation
- **Events**: Kafka/messaging documentation
- **Data**: Database/entity documentation
- **Service**: Service layer documentation
- **Config**: Configuration documentation
- **Ops**: Operational/runbook documentation
- **Integration**: External integration documentation
- **Code**: Inline code documentation

### Priority Criteria

- **P1**: Blocks external integrators, required for compliance, affects production operations
- **P2**: Affects internal developers, needed for cross-team collaboration
- **P3**: Improves developer experience, completeness

---

## Review Cadence

- **Weekly**: Review In Progress items
- **Bi-weekly**: Prioritize backlog, assign owners
- **Monthly**: Review completed items, update coverage report
- **Quarterly**: Full documentation audit
