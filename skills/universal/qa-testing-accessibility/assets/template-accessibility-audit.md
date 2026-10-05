# Accessibility Audit Template

## Audit Metadata

| Field | Value |
|-------|-------|
| Application | {{app_name}} |
| Version / Release | {{version}} |
| Audit Date | {{date}} |
| Auditor | {{auditor}} |
| Target Standard | WCAG 2.2 Level {{AA/AAA}} |
| Regulatory Requirement | {{ADA Title II / Section 508 / EN 301 549 / EAA / None}} |

## Scope

### Pages / Flows Audited

| Page / Flow | URL or Screen | Priority |
|-------------|---------------|----------|
| {{page_name}} | {{url_or_screen}} | Critical / High / Medium |

### Platforms Tested

| Platform | Browser / Device | Assistive Technology |
|----------|-----------------|---------------------|
| Web (Desktop) | {{browser}} | Keyboard, NVDA/VoiceOver |
| Web (Mobile) | {{browser}} | VoiceOver / TalkBack |
| iOS Native | {{device}} | VoiceOver |
| Android Native | {{device}} | TalkBack |

### Testing Methods

- [ ] Automated scan (axe-core)
- [ ] Automated scan (Lighthouse)
- [ ] Manual keyboard navigation
- [ ] Screen reader testing (VoiceOver / NVDA / TalkBack)
- [ ] Zoom/reflow testing (200%, 400%)
- [ ] Color contrast manual verification
- [ ] Reduced motion testing
- [ ] Accessibility overlay/widget present on the audited surface? {{Yes/No — if Yes, flag as an open risk item, not a completed control}}
- [ ] Testing session with actual assistive-technology-using participants (not just staff running a checklist)

## Automated Scan Results

| Tool | Pages Scanned | Critical | Serious | Moderate | Minor |
|------|---------------|----------|---------|----------|-------|
| axe-core | {{count}} | {{count}} | {{count}} | {{count}} | {{count}} |
| Lighthouse | {{count}} | Score: {{score}}/100 | | | |

## Findings

### Critical Violations

| # | WCAG Criterion | Description | Page / Component | Impact | Remediation |
|---|----------------|-------------|------------------|--------|-------------|
| 1 | {{criterion_id}} | {{description}} | {{location}} | {{impact_description}} | {{fix}} |

### Serious Violations

| # | WCAG Criterion | Description | Page / Component | Impact | Remediation |
|---|----------------|-------------|------------------|--------|-------------|
| 1 | {{criterion_id}} | {{description}} | {{location}} | {{impact_description}} | {{fix}} |

### Moderate Violations

| # | WCAG Criterion | Description | Page / Component | Impact | Remediation |
|---|----------------|-------------|------------------|--------|-------------|
| 1 | {{criterion_id}} | {{description}} | {{location}} | {{impact_description}} | {{fix}} |

### Observations and Best Practice Recommendations

| # | Area | Observation | Recommendation |
|---|------|-------------|----------------|
| 1 | {{area}} | {{observation}} | {{recommendation}} |

## Remediation Plan

### Priority Matrix

| Priority | Criteria | Target Date |
|----------|----------|-------------|
| P0 — Immediate | Critical violations blocking AT users | {{date}} |
| P1 — Sprint | Serious violations in critical flows | {{date}} |
| P2 — Quarter | Moderate violations and best practices | {{date}} |
| P3 — Backlog | Minor violations and enhancements | {{date}} |

### Assigned Remediation

| Finding # | Assignee | Target Sprint | Status |
|-----------|----------|---------------|--------|
| {{finding_number}} | {{assignee}} | {{sprint}} | Open / In Progress / Resolved |

## Retest Schedule

| Milestone | Date | Scope |
|-----------|------|-------|
| P0 retest | {{date}} | Critical violations only |
| P1 retest | {{date}} | Serious violations in critical flows |
| Full retest | {{date}} | All findings |

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| QA Lead | | | Pending / Approved |
| Product Owner | | | Pending / Approved |
| Accessibility SME | | | Pending / Approved |
