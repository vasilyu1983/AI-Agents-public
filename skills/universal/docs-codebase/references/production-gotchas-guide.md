# Production Gotchas Documentation Guide

How to document platform-specific issues, known limitations, and production quirks: behavior that differs from what the docs or intuition suggest, and that causes incidents when forgotten.

---
## Table of Contents

- [Gotcha Documentation Template](#gotcha-documentation-template)
- [Categories](#categories)
- [Vendor and Platform Values Go Stale](#vendor-and-platform-values-go-stale)
- [Where to Store Gotchas](#where-to-store-gotchas)
- [Gotcha Review Process](#gotcha-review-process)
- [Integration with Incident Management](#integration-with-incident-management)
- [Anti-Patterns](#anti-patterns)
- [Related Resources](#related-resources)

---

## Gotcha Documentation Template

```markdown
## [Short Title]

**Severity**: Critical / High / Medium / Low
**Affects**: [service/component/environment]
**Last Verified**: YYYY-MM-DD

### The Problem

[Clear description of the unexpected behavior]

### Why It Happens

[Root cause explanation]

### The Fix / Workaround

[Step-by-step solution]

### How to Detect

[Symptoms, error messages, monitoring alerts]

### References

- [Link to related incident]
- [Link to upstream issue]
- [Link to vendor documentation for any limit or value quoted above]
```

---

## Categories

| Category | Typical gotcha | What the entry must pin down |
|----------|----------------|------------------------------|
| Infrastructure | Connection or instance limits hit when replicas × pool size exceed the database's max connections | The arithmetic (replicas × pool size × services) and where the limit is read from |
| Third-party APIs | Webhook retries delivering duplicates hours after a failed deploy | Idempotency key used, dedupe retention window, and the vendor doc stating the retry window |
| Language/runtime | Synchronous work (large JSON parse, crypto) blocking an event loop | Payload size limit enforced at the edge, and the latency metric that shows it |
| Database | Stale planner statistics after bulk loads | The command that fixes it and the job that must run it |
| Environment | DNS or network setup differing between local containers and production | Where the setting is configured (orchestrator, not a hand-edited file inside the image) |

## Vendor and Platform Values Go Stale

Instance connection limits, retry windows, rate limits, and quotas change with vendor plans and releases. For any number in a gotcha:

- Link the vendor page it came from and set **Last Verified**.
- Prefer describing how to read the live value (a query, console page, or API call) over quoting the number.
- Derive thresholds (alert levels, pool sizes) from the live value in config, not from the doc.

A gotcha that quotes a stale limit is worse than none: it gives false confidence during the incident it was meant to prevent.

---

## Where to Store Gotchas

Default: inline in the canonical doc for the affected service, under a "Known Issues & Gotchas" heading, so readers find it where they already look. Add a `docs/gotchas/README.md` index linking to them once there are more than a handful across services.

Use a dedicated `docs/gotchas/` directory only for cross-cutting gotchas that belong to no single service (shared infrastructure, CI/CD, containers).

Put a gotcha in `AGENTS.md`/`CLAUDE.md` only when it changes what an agent does on routine tasks, and then as a one-line rule linking to the full entry. Never copy vendor numbers into instruction files; they go stale where nobody reviews them.

---

## Gotcha Review Process

### When to Add

- After every production incident whose root cause was a known-but-undocumented behavior
- When onboarding reveals undocumented behavior
- When code review catches a gotcha

### Review Checklist

- [ ] Clear, specific title
- [ ] Severity assigned
- [ ] Root cause explained
- [ ] Solution provided
- [ ] Detection method documented
- [ ] Every quoted limit or value has a source link and Last Verified date

### Maintenance

- Review on the doc's ownership cadence and whenever the vendor plan, instance class, or runtime version changes
- Remove fixed issues (git keeps the history)
- Update when a workaround becomes a permanent fix

---

## Integration with Incident Management

Add a gotcha decision to the incident retro template:

```markdown
### Gotcha Documentation

**Should this be documented?** Yes / No

If yes:
- **Category**: Infrastructure / API / Runtime / Database / Environment
- **Severity**: Critical / High / Medium / Low
- **Owner**: [team]
- **Due**: [date]
```

List related incident IDs in the gotcha entry, so a recurrence is recognized as one.

---

## Anti-Patterns

### Don't Do This

```markdown
## Database Issues

Sometimes the database is slow. Check connections.
```

### Do This Instead

```markdown
## PostgreSQL Slow Queries After Bulk Insert

**Severity**: Medium
**Affects**: Reporting queries after ETL

### The Problem

After a large bulk insert, queries on that table can pick bad plans until autovacuum's auto-analyze runs, which may be much later.

### The Fix

Run `ANALYZE table_name` immediately after the bulk insert:

    INSERT INTO events SELECT ... FROM staging_events;
    ANALYZE events;

### How to Detect

- Query times spike after ETL jobs
- `EXPLAIN ANALYZE` shows row estimates far from actual rows
```

---

## Related Resources

- [writing-best-practices.md](writing-best-practices.md) - General documentation standards
- [changelog-best-practices.md](changelog-best-practices.md) - Tracking changes
- [adr-writing-guide.md](adr-writing-guide.md) - Architecture decisions
