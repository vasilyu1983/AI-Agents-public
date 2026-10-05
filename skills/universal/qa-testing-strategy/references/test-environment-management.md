# Test Environment Management

Environment-as-code boilerplate (Docker Compose, Terraform, Pulumi, WireMock, Kubernetes namespaces) is standard and not repeated here; infrastructure and pipeline design belong to [ops-devops-platform](../../ops-devops-platform/SKILL.md). This file keeps the decision rules a test strategy has to make.

## Environment Types

| Environment | Purpose | Data | Lifecycle |
|---|---|---|---|
| Local | Developer testing | Synthetic/seeded | Persistent |
| CI | Automated tests | Synthetic, ephemeral | Per pipeline |
| Preview/PR | Feature review, thin E2E smoke | Seeded from template | Per PR, torn down on close |
| Staging | Integration and exploratory testing | Sanitised or synthetic subset | Long-lived |
| Pre-prod | Release validation, performance | Prod-like volume | Long-lived |

Keep real customer data out of CI and staging; see [synthetic-test-data.md](synthetic-test-data.md).

## When to Virtualize

| External dependency | Virtualize? | Rationale |
|---|---|---|
| Payment gateway | Yes, always (use the provider's test mode for a thin contract smoke) | Cost, rate limits, real side effects |
| Email / SMS provider | Yes, always | Side effects, delivery delays, cost |
| Auth provider | Usually | Rate limits; provider test tenants may suffice |
| Analytics / telemetry sinks | Yes | Irrelevant to the behaviour under test |
| Database | No | Use the real engine (container) |
| Message queue | Sometimes | Real broker for integration tests, fake for unit tests |

A virtualised dependency needs its own contract check against the real provider (scheduled, not per PR); otherwise the stub drifts and tests pass against behaviour that no longer exists.

## Shared vs Dedicated Environments

| Dimension | Shared | Dedicated |
|---|---|---|
| Cost | Low | High |
| Isolation | Low (data conflicts) | High |
| Stability | Broken by other teams | Self-controlled |
| Best for | Manual QA, demos, exploratory testing | Automated testing, CI, PR previews |

Default: dedicated ephemeral environments for anything that gates merge; shared long-lived environments only for manual and release-validation work. A required check must never depend on a shared environment another team can break.

Database isolation: separate databases for staging and pre-prod; schema-per-environment for ephemeral PR environments; avoid row-level (tenant-column) isolation for tests, because one missed filter leaks data across runs.

## Drift Detection

- Schedule an infrastructure drift check (for example `terraform plan -detailed-exitcode`, which exits 2 when drift exists) and treat drift as a failing check, not a warning.
- Compare runtime configuration (feature flags, dependency versions, env vars by name, not value) between staging and production before each release; a test pass on a drifted environment is weaker evidence.
- When the same test fails across unrelated suites at the same time, suspect environment drift before test flakiness.

## Cost Rules

- Tear down PR environments on close and sweep orphans on a schedule.
- Stop non-prod environments outside working hours when nothing depends on them.
- Track CI and environment cost per team or per merged PR; suites without a cost owner grow without limit.

## Related Resources

- [synthetic-test-data.md](synthetic-test-data.md) — privacy-safe seed data
- [operational-playbook.md](operational-playbook.md) — CI gates
- [shift-left-testing.md](shift-left-testing.md) — preview environments in the stage model
- [../SKILL.md](../SKILL.md) — parent testing strategy skill
