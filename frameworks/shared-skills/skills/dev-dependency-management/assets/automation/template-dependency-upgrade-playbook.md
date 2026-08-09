# Dependency Upgrade Playbook (Production)

Use this playbook to upgrade dependencies with small blast radius and a clear rollback path.

## Policies

- Lockfiles are required for deployable applications.
- CI uses exact installs: `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`, `bun ci`, `uv sync --frozen`, `poetry sync`, `cargo build --locked`.
- Every temporary pin, override, or resolution has an owner and removal date.
- Major upgrades are isolated unless there is an explicit reason to couple them.

## Default Cadence

- Critical security fixes: same day when production-exploitable
- High security fixes: within SLA
- Patch updates: weekly
- Minor updates: monthly
- Major updates: planned work

## Triage

### Low risk

- patch versions
- dev-only tools
- internal libraries with strong test coverage

### Medium risk

- runtime minor updates
- framework-adjacent tooling

### High risk

- majors
- auth, crypto, database, ORM, build, and package-manager changes

## Workflow

1. Create a small, clearly named dependency PR.
2. Update the dependency and the matching lock state only.
3. Rebuild from the exact install command for the ecosystem.
4. Run tests, type checks, and runtime smoke checks.
5. Review release notes and migration notes for anything non-trivial.
6. Refresh SBOM or artifact metadata if the release build changes.
7. Merge only with a rollback path that is actually executable.

## Rollback

- Revert the PR or commit.
- Restore the previous lock state.
- Redeploy the last known good artifact if runtime behavior changed.

## Do / Avoid

### Do

- Keep PRs reviewable.
- Group low-risk updates by family.
- Keep security fixes separate from unrelated refactors.
- Use update bots for discovery, not as a substitute for review.

### Avoid

- Upgrading everything to latest in one PR.
- Mixing package-manager migration with regular dependency refreshes.
- Leaving long-lived overrides undocumented.
- Accepting large lockfile churn without inspecting the graph.
