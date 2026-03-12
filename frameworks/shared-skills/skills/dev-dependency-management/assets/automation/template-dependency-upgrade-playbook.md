# Dependency Upgrade Playbook (Production)

Use this playbook to upgrade dependencies safely with predictable risk and minimal disruption.

---

## Core

### 1) Policies (Set Once)

- Lockfiles are required and committed for all environments.
- CI uses lockfile installs (`npm ci`, `pip-sync`/`poetry install --sync`, `cargo build --locked`).
- Dependency updates are reviewed like code (tests required, changelog review for majors).
- Exceptions (pins/overrides) require an owner, a reason, and a removal date.

### 2) Upgrade Cadence (Default)

- Security fixes: within SLA (same-day for critical, <7 days for high).
- Patch updates: weekly.
- Minor updates: monthly (batched).
- Major updates: quarterly (planned, with canary/rollback).

### 3) Triage and Batching

Batch by risk to keep blast radius small:

- Batch A (low): patch versions, internal libs, dev-only tools.
- Batch B (medium): minor versions, runtime libs with good test coverage.
- Batch C (high): majors, auth/crypto, database drivers, build systems.

Rules:

- Max one high-risk upgrade per PR unless explicitly approved.
- Keep upgrade PRs reviewable (small diff + clear changelog summary).

### 4) Implementation Workflow

1. Create branch/PR: `chore(deps): bump <group>`
2. Update dependency + lockfile.
3. Run full test suite + linters + build.
4. Run security scan (SCA) and verify no new critical findings.
5. Validate runtime behavior in staging (or canary) for production dependencies.
6. Merge with clear rollback plan.

### 5) Rollback Strategy (Required)

- Ensure previous lockfile state is easily restorable (revert commit/PR).
- For containerized deploys, keep last-known-good artifact available.
- For DB migrations shipped with upgrades, document forward-only vs reversible.

### 6) Operability and Cost Control

- Cache dependencies in CI to reduce minutes and improve signal-to-noise.
- Run heavyweight tests only when relevant packages changed (path filters).
- Track build time regressions after major dependency upgrades.

---

## Do / Avoid

### Do

- Do batch upgrades by risk and keep PRs small
- Do read release notes for majors and security-sensitive packages
- Do treat overrides/pins as temporary debt with a removal date
- Do canary major upgrades when the dependency affects runtime behavior

### Avoid

- Avoid floating ranges for production dependencies
- Avoid unreviewed transitive upgrades via lockfile churn
- Avoid upgrading everything at once (hard to debug and rollback)
- Avoid ignoring supply-chain signals (provenance, signatures, maintainer changes)

---

## Optional: AI/Automation

- Auto-group upgrade PRs by ecosystem and risk (human-reviewed)
- Summarize changelogs and highlight breaking changes (human-validated)
- Draft upgrade PR descriptions with test evidence and rollback notes

### Bounded Claims

- Automation cannot decide business risk acceptance.
- Changelog summaries can miss edge cases; validate against real tests.
