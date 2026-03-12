# Documentation Audit Workflows

This resource provides systematic workflows for conducting documentation audits, from initial discovery to ongoing maintenance.

---

## Contents

- Overview
- Phase 1: Discovery Scan
- Component Inventory
- Phase 2: Coverage Analysis
- Phase 3: Generate Documentation
- Phase 4: Maintain Coverage
- Audit Types
- Audit Checklist
- Tools and Automation
- Common Challenges
- Success Criteria
- Related Resources

## Overview

A documentation audit is a systematic review of a codebase to identify documentation gaps, outdated content, and orphaned documentation. This guide provides step-by-step workflows for different audit scenarios.

---

## Phase 1: Discovery Scan

### Objective

Identify all documentable components in the codebase.

### Workflow

#### Step 1: Prepare Audit Scope

Define what you're auditing:

- [ ] API layer (endpoints, models, authentication)
- [ ] Service layer (business logic, handlers)
- [ ] Data layer (database, entities, migrations)
- [ ] Integration layer (external APIs, webhooks, messages)
- [ ] Infrastructure layer (jobs, services, configuration)

#### Step 2: Identify Documentation Locations

Find where documentation currently exists:

```bash
# Common locations
- docs/
- README.md
- wiki/
- openapi/
- *.md files throughout codebase
- Inline code comments
```

#### Step 3: Scan for Components

Use discovery patterns from [discovery-patterns.md](discovery-patterns.md) to find components:

```bash
# Example: .NET codebase
rg "class.*Controller" --type cs > controllers.txt
rg "class.*Service" --type cs > services.txt
rg "class.*DbContext" --type cs > dbcontexts.txt
rg "Topic = \"" --type cs > kafka-topics.txt
```

#### Step 4: Create Component Inventory

Organize discovered components by category:

```markdown
## Component Inventory

### API Layer (23 components)
- PublicApi.Controllers.UsersController
- PublicApi.Controllers.OrdersController
- ...

### Service Layer (45 components)
- Core.Services.UserService
- Core.Services.OrderService
- ...

### Data Layer (12 components)
- Infrastructure.Data.AppDbContext
- Core.Models.User
- ...
```

### Output

- Component inventory (text file or spreadsheet)
- Total component counts by category
- Baseline for gap analysis

---

## Phase 2: Coverage Analysis

### Objective

Compare discovered components against existing documentation to identify gaps.

### Workflow

#### Step 1: Inventory Existing Documentation

List all existing documentation:

```bash
# Find all markdown files
find docs/ -name "*.md" -type f

# List documented endpoints (if OpenAPI exists)
yq '.paths | keys' openapi/spec.yaml

# Count documented components
grep -r "## " docs/ | wc -l
```

#### Step 2: Match Components to Documentation

Create a mapping:

| Component | Type | Documented? | Doc Location | Notes |
|-----------|------|-------------|--------------|-------|
| UsersController | API | Yes | docs/api/users.md | Complete |
| OrdersController | API | No | - | **GAP** |
| UserService | Service | Partial | docs/services.md | Missing dependencies |

#### Step 3: Calculate Coverage Metrics

```
Coverage Rate = (Documented Components / Total Components) × 100%

Example:
- Total: 80 components
- Documented: 52 components
- Coverage: 65%
```

#### Step 4: Categorize Gaps by Priority

Use [priority-framework.md](priority-framework.md) to assign priorities:

- **Priority 1 (Critical)**: External-facing APIs, webhooks, auth
- **Priority 2 (Important)**: Internal APIs, events, database schema
- **Priority 3 (Nice to Have)**: Config options, utilities

#### Step 5: Identify Outdated Documentation

Check for documentation that may be stale:

```bash
# Find docs older than code
find docs/ -name "*.md" -mtime +90  # Modified >90 days ago

# Compare doc dates with git history
git log --since="3 months ago" --name-only -- src/
```

### Output

Use template: [assets/coverage-report-template.md](../assets/coverage-report-template.md)

Key sections:
- Executive summary (coverage %, key findings)
- Coverage by category
- Gap analysis (P1, P2, P3)
- Outdated documentation list

---

## Phase 3: Generate Documentation

### Objective

Create missing documentation using appropriate templates.

### Workflow

#### Step 1: Prioritize Gaps

Start with Priority 1 (critical) gaps:

```markdown
## Priority 1 Gaps (5 items)

1. Document PrivateApi endpoints (8 controllers)
   - Template: api-docs-template.md
   - Effort: High (8 hours)
   - Owner: @team-backend

2. Create Kafka event schema reference
   - Template: Custom event catalog
   - Effort: Medium (4 hours)
   - Owner: @team-platform
```

#### Step 2: Select Templates

Match gaps to templates from [docs-codebase](../../docs-codebase/SKILL.md):

| Gap Type | Template |
|----------|----------|
| API endpoints | [api-docs-template.md](../../docs-codebase/assets/api-reference/api-docs-template.md) |
| Architecture decisions | [adr-template.md](../../docs-codebase/assets/architecture/adr-template.md) |
| Database schema | ER diagram + entity descriptions |
| Event schemas | Custom event catalog |
| Configuration | Config reference template |

#### Step 3: Generate Documentation

For each gap:

1. **Read the code** to understand functionality
2. **Use the template** to structure documentation
3. **Add examples** (request/response, code snippets)
4. **Review with code author** for accuracy
5. **Commit to docs/** directory

#### Step 4: Update Coverage Report

After generating documentation:

```markdown
## Progress Update

- Initial coverage: 65%
- Documented this sprint: 8 components
- Current coverage: 75%
- Remaining P1 gaps: 2
```

### Output

- Documentation files in `docs/` directory
- Updated coverage report
- Documentation backlog with completed items

---

## Phase 4: Maintain Coverage

### Objective

Ensure documentation stays up-to-date and gaps don't re-emerge.

### Workflow

#### Step 1: Add Documentation to PR Template

```markdown
## Documentation Checklist

- [ ] New APIs documented in OpenAPI spec
- [ ] New events added to event catalog
- [ ] Configuration changes documented
- [ ] Breaking changes noted in CHANGELOG
- [ ] Architecture decisions recorded (ADR)
```

#### Step 2: Set Up Documentation Checks (CI/CD)

See [cicd-integration.md](cicd-integration.md) for implementation details.

Example: GitHub Actions check

```yaml
- name: Documentation Coverage Check
  run: |
    # Count undocumented public APIs
    ./scripts/check-api-coverage.sh
```

#### Step 3: Schedule Regular Audits

- **Quarterly**: Full documentation audit (all phases)
- **Monthly**: Review documentation backlog progress
- **Weekly**: Review PR documentation checklist compliance

#### Step 4: Assign Documentation Owners

```markdown
## Documentation Ownership

| Area | Owner | Responsibilities |
|------|-------|------------------|
| Public API docs | @team-api | Keep OpenAPI spec current |
| Event catalog | @team-platform | Document new Kafka topics |
| Database schema | @team-data | Update ER diagrams |
| Runbooks | @team-ops | Document background jobs |
```

#### Step 5: Track Documentation Debt

Use [documentation-backlog-template.md](../assets/documentation-backlog-template.md) to track:

- In Progress items
- To Do (P1, P2, P3)
- Blocked items
- Completed items

### Output

- PR template with documentation checklist
- CI/CD checks for documentation coverage
- Quarterly audit schedule
- Documentation ownership matrix

---

## Audit Types

### Full Audit (Quarterly)

**Scope**: All components, all documentation

**Duration**: 1-2 weeks

**Output**:
- Complete coverage report
- Updated documentation backlog
- Documentation debt score

**When to use**:
- New project onboarding
- Pre-compliance audit
- Major architecture changes

---

### Incremental Audit (Monthly)

**Scope**: Recently changed components (last 30 days)

**Duration**: 1-2 days

**Output**:
- Mini coverage report (changed areas only)
- Updated backlog with new gaps

**When to use**:
- Ongoing maintenance
- After major feature releases

**Example**:

```bash
# Find files changed in last 30 days
git diff --name-only @{30.days.ago} HEAD -- src/

# Check if corresponding docs were updated
git diff --name-only @{30.days.ago} HEAD -- docs/
```

---

### Targeted Audit (Ad-hoc)

**Scope**: Specific component or area

**Duration**: 1-4 hours

**Output**:
- Gap analysis for target area
- Documentation plan

**When to use**:
- New team onboarding
- External partner integration
- Pre-feature launch

**Example**:

```markdown
## Targeted Audit: Payment Service

**Scope**: All payment-related components

**Findings**:
- PaymentController: Documented [check]
- PaymentService: Not documented [x]
- PaymentWebhook: Not documented [x]
- StripeClient: Partially documented ~

**Action**: Document PaymentService and PaymentWebhook (P1)
```

---

## Audit Checklist

### Pre-Audit

- [ ] Identify documentation locations (docs/, wiki, README)
- [ ] List all known documentation files
- [ ] Understand project structure and naming conventions
- [ ] Identify target audience (developers, operators, external integrators)
- [ ] Select audit type (full, incremental, targeted)
- [ ] Allocate time (full = 1-2 weeks, incremental = 1-2 days, targeted = 1-4 hours)

### During Audit

- [ ] Scan API layer for undocumented endpoints
- [ ] Scan service layer for undocumented services
- [ ] Scan data layer for undocumented entities
- [ ] Scan event layer for undocumented topics/schemas
- [ ] Scan infrastructure for undocumented jobs/configs
- [ ] Check for outdated documentation (code changed, docs didn't)
- [ ] Identify documentation that references non-existent code (orphaned docs)
- [ ] Record findings in coverage report template
- [ ] Categorize gaps by priority (P1, P2, P3)

### Post-Audit

- [ ] Generate coverage report (use template)
- [ ] Calculate documentation debt score
- [ ] Prioritize gaps by impact and effort
- [ ] Create documentation backlog
- [ ] Assign ownership for critical gaps (P1)
- [ ] Schedule documentation generation sprints
- [ ] Schedule follow-up audit (quarterly for full, monthly for incremental)
- [ ] Share report with stakeholders (eng managers, tech leads, product)

---

## Tools and Automation

### Manual Audit Tools

- **ripgrep (rg)**: Fast code search
- **grep**: Standard text search
- **find**: File discovery
- **diff**: Compare component lists with docs
- **wc**: Count components
- **Spreadsheet**: Track coverage mapping

### Automated Audit Tools

- **OpenAPI diff**: Compare spec versions
- **Swagger coverage**: Check endpoint documentation
- **Custom scripts**: Count components vs documented items
- **Git hooks**: Prevent commits without docs

### Documentation Generation Tools

- **Swagger/OpenAPI Generator**: Auto-generate API docs
- **TypeDoc**: Generate TypeScript docs
- **Docfx**: Generate .NET docs
- **Sphinx**: Generate Python docs
- **Mermaid**: Generate diagrams as code

---

## Common Challenges

### Challenge: Too Many Gaps (Debt Score > 100)

**Solution**: Break into phases

1. **Phase 1**: Document P1 gaps only (2-3 sprints)
2. **Phase 2**: Document top 10 P2 gaps (1-2 sprints)
3. **Phase 3**: Ongoing P3 documentation (opportunistic)

### Challenge: Outdated Documentation

**Solution**: Archive or update

- If code exists but changed: **Update docs**
- If code no longer exists: **Archive docs** (move to `docs/.archive/`)
- If uncertain: **Flag for review** (add "[WARNING] Needs verification" badge)

### Challenge: No Template Exists

**Solution**: Create custom template

1. Review similar documentation for inspiration
2. Consult [docs-codebase](../../docs-codebase/SKILL.md) templates
3. Create minimal viable template
4. Iterate based on feedback

### Challenge: Documentation Not Used

**Solution**: Improve discoverability

- Add to main README
- Link from relevant code (inline comments)
- Share in onboarding guides
- Present in team meetings

---

## Success Criteria

### Immediate (After Audit)

- [ ] Coverage report clearly shows gaps with priorities
- [ ] Documentation backlog is actionable and assigned
- [ ] Critical gaps (P1) identified with owners

### Short-term (1-2 Sprints)

- [ ] All P1 gaps documented
- [ ] Documentation coverage > 80% for external-facing components
- [ ] Documentation backlog actively managed

### Long-term (Ongoing)

- [ ] Quarterly audits show improving coverage (upward trend)
- [ ] PR documentation checklist compliance > 90%
- [ ] "How do I" questions in Slack decrease
- [ ] Onboarding time for new engineers decreases

---

## Related Resources

- [Discovery Patterns](discovery-patterns.md) - How to find components
- [Priority Framework](priority-framework.md) - How to prioritize gaps
- [CI/CD Integration](cicd-integration.md) - How to automate checks
- [Coverage Report Template](../assets/coverage-report-template.md) - Report structure
- [Documentation Backlog Template](../assets/documentation-backlog-template.md) - Backlog tracking
