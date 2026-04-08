# Architecture Decision Records (ADRs) - Writing Guide

Complete guide for documenting architectural and technical decisions using Architecture Decision Records (ADRs).

## What Are ADRs?

**Architecture Decision Records** document important architectural decisions made during a project's lifecycle, including the context, decision, and consequences.

**Purpose**:
- Create searchable history of why decisions were made
- Onboard new team members quickly
- Prevent repeating past mistakes
- Document trade-offs and alternatives considered

**When to write an ADR**:
- [OK] Choosing a database technology
- [OK] Selecting a framework or library
- [OK] Architectural pattern changes (microservices, event-driven, etc.)
- [OK] Authentication/authorization approach
- [OK] Deployment strategy
- [OK] API design standards
- [OK] Testing strategy
- [FAIL] Minor refactoring (no ADR needed)
- [FAIL] Bug fixes (no ADR needed)
- [FAIL] Temporary workarounds (no ADR needed)

## ADR Structure

Every ADR should follow this structure:

### 1. Title

**Format**: `ADR-NNN: [Verb] [Technology/Pattern] for [Purpose]`

**Examples**:
- `ADR-001: Use PostgreSQL for Primary Database`
- `ADR-002: Implement Event-Driven Architecture with Kafka`
- `ADR-003: Adopt TypeScript for Frontend Development`
- `ADR-004: Use JWT for API Authentication`

**Best practices**:
- Sequential numbering (001, 002, 003...)
- Action verb (Use, Implement, Adopt, Replace)
- Specific technology/pattern
- Clear purpose

### 2. Status

**Purpose**: Track the decision lifecycle.

**Valid statuses**:
- **Proposed** - Under discussion
- **Accepted** - Decision approved and active
- **Deprecated** - Still in use but being phased out
- **Superseded** - Replaced by another decision (link to new ADR)
- **Rejected** - Considered but not implemented

**Format**:
```markdown
## Status

Accepted

Date: 2025-11-22
```

**Status transitions**:
```
Proposed → Accepted → Deprecated → Superseded
         ↓
       Rejected
```

### 3. Context

**Purpose**: Explain the problem, constraints, and requirements.

**What to include**:
- Problem statement
- Current situation
- Constraints (technical, business, time, budget)
- Requirements (functional and non-functional)
- Stakeholder concerns

**Format**:
```markdown
## Context

We need a primary database for our e-commerce platform that will:

- Handle 10,000+ transactions per day
- Support complex queries with joins
- Provide ACID guarantees for financial data
- Scale to 1TB+ of data over 3 years
- Work with our Node.js backend

**Constraints**:
- Team has limited DBA expertise
- Budget: $500/month for managed hosting
- Must deploy in 3 months

**Current situation**:
- Using SQLite for prototype
- SQLite cannot handle production load
- Need production-ready solution
```

**Best practices**:
- Be specific with numbers (users, transactions, data size)
- Include timeline constraints
- Mention team expertise/limitations
- Reference business requirements

### 4. Decision

**Purpose**: State what was decided clearly and concisely.

**Format**:
```markdown
## Decision

We will use PostgreSQL 14+ as our primary database.

**Implementation**:
- PostgreSQL 14.5 on managed AWS RDS
- Multi-AZ deployment for high availability
- Automated daily backups with 7-day retention
- Connection pooling with PgBouncer
```

**Best practices**:
- Start with declarative statement
- Include version numbers
- Specify deployment details
- Mention critical configuration

### 5. Consequences

**Purpose**: Document impacts (positive, negative, neutral).

**Format**:
```markdown
## Consequences

### Positive

- **ACID compliance** - Full transaction guarantees for financial data
- **Rich ecosystem** - Extensive tooling (pgAdmin, PostgREST, TimescaleDB)
- **JSON support** - Native JSONB for semi-structured data
- **Performance** - Excellent query optimizer for complex joins
- **Community** - Large community, extensive documentation

### Negative

- **Vertical scaling limitations** - Single-node writes limit scale
- **Operational complexity** - More complex than MongoDB for simple CRUD
- **Cost** - $400/month for managed RDS Multi-AZ
- **Learning curve** - Team needs to learn SQL optimization

### Neutral

- **Migration effort** - 2-3 weeks to migrate from SQLite
- **Backup strategy** - Need to implement point-in-time recovery
```

**Best practices**:
- Be honest about negatives
- Include costs (time, money, complexity)
- Quantify impacts where possible
- Consider long-term implications

### 6. Alternatives Considered

**Purpose**: Document options that were rejected and why.

**Format**:
```markdown
## Alternatives Considered

### MySQL 8.0

**Pros**:
- Similar to PostgreSQL in features
- Team has MySQL experience
- Slightly cheaper hosting

**Cons**:
- Weaker JSON support than PostgreSQL
- Oracle licensing concerns
- Less advanced query optimizer

**Why rejected**: PostgreSQL's superior JSON support and query optimizer outweigh familiarity with MySQL.

### MongoDB 6.0

**Pros**:
- Simpler schema-less design
- Horizontal scaling built-in
- Team has MongoDB experience

**Cons**:
- No ACID transactions across collections (until v4.0)
- Eventual consistency model risky for financial data
- Weak support for complex joins

**Why rejected**: Lack of strong ACID guarantees unacceptable for financial transactions.

### DynamoDB

**Pros**:
- Fully managed by AWS
- Excellent horizontal scaling
- Pay-per-use pricing

**Cons**:
- Vendor lock-in to AWS
- Complex query limitations
- Expensive for consistent workloads
- No joins or complex queries

**Why rejected**: Query limitations and vendor lock-in outweigh scaling benefits.
```

**Best practices**:
- Include at least 2-3 alternatives
- Be fair to alternatives (honest pros/cons)
- Explain rejection rationale clearly
- Consider similar complexity options

### 7. Implementation (Optional)

**Purpose**: Next steps and migration plan.

**Format**:
```markdown
## Implementation

### Phase 1: Setup (Week 1)
- [ ] Provision PostgreSQL RDS instance
- [ ] Configure security groups and VPC
- [ ] Set up PgBouncer connection pooling
- [ ] Configure automated backups

### Phase 2: Migration (Weeks 2-3)
- [ ] Create PostgreSQL schema from SQLite
- [ ] Write data migration scripts
- [ ] Test migration on staging environment
- [ ] Migrate production data (scheduled downtime)

### Phase 3: Verification (Week 4)
- [ ] Performance testing
- [ ] Data integrity validation
- [ ] Monitoring and alerting setup
- [ ] Documentation update

**Owner**: Backend team
**Target date**: 2025-12-15
```

### 8. References

**Purpose**: Link to relevant documentation and resources.

**Format**:
```markdown
## References

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- AWS RDS Best Practices: https://docs.aws.amazon.com/rds/
- Internal database comparison spreadsheet: [Google Drive link]
- Slack discussion: #architecture channel, Nov 10-15
- Performance benchmarks: [Confluence link]
```

## Complete ADR Example

```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status

Accepted

Date: 2025-11-22

## Context

We need a primary database for our e-commerce platform that will:

- Handle 10,000+ transactions per day
- Support complex queries with joins (orders + products + users)
- Provide ACID guarantees for financial data
- Scale to 1TB+ of data over 3 years
- Work with our Node.js backend

**Constraints**:
- Team has limited DBA expertise
- Budget: $500/month for managed hosting
- Must deploy in 3 months
- Need high availability (99.9% uptime SLA)

**Current situation**:
- Using SQLite for prototype
- SQLite cannot handle production load (50 concurrent users)
- Need production-ready solution with automatic failover

## Decision

We will use PostgreSQL 14+ as our primary database.

**Implementation**:
- PostgreSQL 14.5 on managed AWS RDS
- Multi-AZ deployment for high availability
- db.t3.medium instance (2 vCPU, 4GB RAM)
- Automated daily backups with 7-day retention
- Connection pooling with PgBouncer (50 connections)

## Consequences

### Positive

- **ACID compliance** - Full transaction guarantees for financial data
- **Rich ecosystem** - Extensive tooling (pgAdmin, PostgREST, TimescaleDB)
- **JSON support** - Native JSONB for semi-structured data (product attributes)
- **Performance** - Excellent query optimizer for complex joins
- **Community** - Large community, extensive documentation, Stack Overflow support

### Negative

- **Vertical scaling limitations** - Single-node writes limit scale to ~10k writes/sec
- **Operational complexity** - More complex than MongoDB for simple CRUD
- **Cost** - $400/month for managed RDS Multi-AZ (within budget)
- **Learning curve** - Team needs to learn SQL optimization (2-week ramp-up)

### Neutral

- **Migration effort** - 2-3 weeks to migrate from SQLite (50k rows)
- **Backup strategy** - Need to implement point-in-time recovery (AWS RDS built-in)

## Alternatives Considered

### MySQL 8.0

**Pros**:
- Similar to PostgreSQL in features
- Team has MySQL experience (2 developers)
- Slightly cheaper hosting ($350/month)

**Cons**:
- Weaker JSON support than PostgreSQL (JSON vs JSONB)
- Oracle licensing concerns
- Less advanced query optimizer

**Why rejected**: PostgreSQL's superior JSON support and query optimizer outweigh familiarity with MySQL.

### MongoDB 6.0

**Pros**:
- Simpler schema-less design
- Horizontal scaling built-in (sharding)
- Team has MongoDB experience (1 developer)

**Cons**:
- No ACID transactions across collections (until v4.0)
- Eventual consistency model risky for financial data
- Weak support for complex joins (requires $lookup aggregation)

**Why rejected**: Lack of strong ACID guarantees unacceptable for financial transactions.

### DynamoDB

**Pros**:
- Fully managed by AWS (zero operational overhead)
- Excellent horizontal scaling (millions of requests/sec)
- Pay-per-use pricing (~$200/month for our workload)

**Cons**:
- Vendor lock-in to AWS
- Complex query limitations (no joins, limited filtering)
- Expensive for consistent workloads
- No complex queries or analytics

**Why rejected**: Query limitations and vendor lock-in outweigh scaling benefits. Analytics queries impossible.

## Implementation

### Phase 1: Setup (Week 1)
- [ ] Provision PostgreSQL RDS instance (db.t3.medium, Multi-AZ)
- [ ] Configure security groups and VPC (private subnet)
- [ ] Set up PgBouncer connection pooling (50 connections)
- [ ] Configure automated backups (daily, 7-day retention)

### Phase 2: Migration (Weeks 2-3)
- [ ] Create PostgreSQL schema from SQLite (using pg_dump equivalent)
- [ ] Write data migration scripts (Python with psycopg2)
- [ ] Test migration on staging environment (10k test records)
- [ ] Migrate production data (scheduled 2-hour downtime window)

### Phase 3: Verification (Week 4)
- [ ] Performance testing (10k concurrent users with k6)
- [ ] Data integrity validation (checksum comparison)
- [ ] Monitoring and alerting setup (CloudWatch + PagerDuty)
- [ ] Documentation update (runbooks, connection strings)

**Owner**: Backend team (John, Sarah)
**Target date**: 2025-12-15
**Estimated effort**: 80 hours

## References

- PostgreSQL Documentation: https://www.postgresql.org/docs/14/
- AWS RDS Best Practices: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html
- Internal database comparison spreadsheet: https://docs.google.com/spreadsheets/d/xyz
- Slack discussion: #architecture channel, Nov 10-15
- Performance benchmarks: https://confluence.internal/benchmarks
- ADR template: [Link to this template]
```

## ADR Naming Convention

**File naming**:
```
docs/adr/
├── 0001-use-postgresql-for-primary-database.md
├── 0002-implement-event-driven-architecture.md
├── 0003-adopt-typescript-for-frontend.md
└── README.md  # Index of all ADRs
```

**Numbering**:
- Zero-padded (0001, 0002, not 1, 2)
- Sequential (no gaps)
- Never reuse numbers

## ADR Index (README)

Create an index in `docs/adr/README.md`:

```markdown
# Architecture Decision Records

## Active ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-use-postgresql-for-primary-database.md) | Use PostgreSQL for Primary Database | Accepted | 2025-11-22 |
| [0002](0002-implement-event-driven-architecture.md) | Implement Event-Driven Architecture | Accepted | 2025-11-25 |

## Deprecated ADRs

| ADR | Title | Status | Date | Superseded By |
|-----|-------|--------|------|---------------|
| [0003](0003-use-mongodb.md) | Use MongoDB for Sessions | Superseded | 2025-10-01 | ADR-0001 |
```

## Architecture Doc State Separation

Architecture documents (ADRs, design docs, migration specs) must distinguish three states:

- **Verified current state**: what has been confirmed against actual repos, contracts, and runtime behavior — not inherited from stale summaries.
- **Selected target state**: the decided direction, with explicit ADR or decision reference.
- **Unresolved gaps**: what is still open, who owns resolution, and when it is expected to close.

Flattening these together makes docs unsafe to trust. Cross-repo architecture claims (participating repo inventories, event flows, contract surfaces, publication-safety assertions) must be repo-verified, not copied from prior documentation.

For platform libraries, stale docs are not cosmetic — they change how future engineers and agents modify the code. Update docs and ADRs in the same delivery cycle as runtime behavior changes.

---

## ADR Anti-Patterns

**BAD: Avoid**:

- **No context** - Decision without explaining why
- **No alternatives** - Looks like no research was done
- **No consequences** - Ignoring trade-offs
- **Too vague** - "Use a database" instead of "Use PostgreSQL 14"
- **Too detailed** - Implementation code in ADR (link to PRs instead)
- **No date** - Can't track when decision was made
- **Retroactive ADRs** - Writing ADRs for old decisions (acceptable for critical legacy decisions)

## ADR Best Practices

**GOOD: Do**:

- Write ADRs when decision is made (not before, not after)
- Keep ADRs immutable (don't edit after acceptance)
- Supersede with new ADRs (don't delete old ADRs)
- Be specific with versions and dates
- Include quantitative data (numbers, metrics)
- Link to related ADRs
- Update index/README when adding ADRs
- Get team review before accepting
- Store ADRs in version control with code

## ADR Tools

**Generators**:
- `adr-tools` - CLI for creating/managing ADRs
- `log4brains` - ADR management with web UI

**Installation**:
```bash
# adr-tools
npm install -g adr-log

# Create new ADR
adr new "Use PostgreSQL for Primary Database"
```

**Templates**:
- [MADR](https://adr.github.io/madr/) - Markdown ADR format
- [Nygard ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Original format

## ADR Review Checklist

Before accepting an ADR, verify:

- [ ] Title follows naming convention
- [ ] Status is set (Proposed/Accepted)
- [ ] Date is included
- [ ] Context explains the problem clearly
- [ ] Decision is specific (versions, technologies)
- [ ] Consequences include positives AND negatives
- [ ] At least 2-3 alternatives considered
- [ ] Alternatives have fair pros/cons
- [ ] References link to relevant docs
- [ ] File named with sequential number
- [ ] Index/README updated

## After-Action Reviews (January 2026 Best Practice)

**Purpose**: Review each ADR one month after acceptance to compare documented expectations with actual outcomes.

**When to conduct**:

- 1 month after ADR acceptance (standard)
- After major milestone completion
- When unexpected issues arise related to the decision

**Review Process**:

### 1. Schedule the Review

```markdown
## After-Action Review

**ADR**: ADR-001: Use PostgreSQL for Primary Database
**Review Date**: 2026-01-22 (30 days after acceptance)
**Attendees**: Backend team, Tech Lead
```

### 2. Review Questions

Ask these questions during the review:

- Did the decision achieve its stated goals?
- Were there unexpected consequences (positive or negative)?
- Did the predicted costs and benefits materialize?
- Would we make the same decision today with current knowledge?
- What should we document for future similar decisions?

### 3. Document Findings

```markdown
### After-Action Review - 2026-01-22

**Goals Achieved**:
- [OK] ACID compliance working as expected for financial data
- [OK] Query performance meets requirements (avg 50ms)
- [PARTIAL] JSON support used less than expected

**Unexpected Consequences**:
- Positive: PgBouncer connection pooling reduced costs by 20%
- Negative: Backup restore took 4 hours (expected 1 hour)

**Lessons Learned**:
- Test backup restore procedures before production
- Consider read replicas earlier for reporting workloads

**Recommendation**: No changes to ADR status. Add backup testing to future ADR checklist.
```

### 4. Readout Meeting Style

AWS recommends a "readout meeting" approach:

1. Attendees spend 10-15 minutes reading the ADR silently
2. Written comments on sections requiring clarification
3. Discussion of differing opinions
4. Keep total participants under 10 people

**After-Action Review Checklist**:

- [ ] Review scheduled 30 days after acceptance
- [ ] Original decision-makers invited
- [ ] Affected teams represented
- [ ] Goals vs actuals documented
- [ ] Lessons learned captured
- [ ] ADR index updated if status changed

---

## When to Update ADRs

**Never edit** accepted ADRs. Instead:

1. **Status change**: Create new ADR that supersedes it
2. **New information**: Create new ADR referencing the old one
3. **Implementation details**: Update separate implementation docs

**Example**:

- ADR-001: Use PostgreSQL (Accepted) → Later becomes (Superseded by ADR-010)
- ADR-010: Migrate to CockroachDB (Accepted)

## ADR Success Criteria

**A good ADR enables readers to**:

1. [OK] Understand the problem and constraints
2. [OK] See what was decided and why
3. [OK] Know what alternatives were considered
4. [OK] Understand trade-offs and consequences
5. [OK] Find references for more context
6. [OK] Determine if decision is still valid

**Quality metrics**:
- Time to understand decision: < 5 minutes
- Completeness: All sections filled
- Clarity: No ambiguous statements
- Traceability: Links to discussions, docs, PRs
