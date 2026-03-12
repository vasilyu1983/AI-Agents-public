# Monorepo Git Workflows

Git workflow patterns for monorepo repositories covering branching, CI optimization, code ownership, and tooling.

## Contents

- When Monorepo vs Polyrepo
- Branching Strategy: Trunk-Based for Monorepos
- Partial Clone and Sparse Checkout
- CODEOWNERS and Path-Based Review Rules
- Affected-Only CI
- GitHub Actions: Path-Based Triggers
- Tooling Comparison
- Merge Queue Considerations
- Decision Table: Monorepo vs Polyrepo
- Do / Avoid
- Related Resources

---

## When Monorepo vs Polyrepo

Use a monorepo when packages share significant code, release together, or when cross-cutting refactors are frequent. Use polyrepo when teams are fully autonomous, deploy independently, and rarely touch each other's code.

---

## Branching Strategy: Trunk-Based for Monorepos

Trunk-based development is strongly preferred for monorepos. Long-lived branches across many packages create exponential merge conflict risk.

```bash
# Short-lived branch touching one or two packages
git checkout -b feat/payments-retry-logic main

# Commit scoped to one package
git commit -m "feat(payments): add exponential backoff on retry"

# Merge same day; keep branch alive < 24 hours
git push origin feat/payments-retry-logic
# Open PR, get review, merge, delete branch
```

**Why trunk-based wins in monorepos**:
- Merge conflicts compound across packages on long-lived branches
- Feature flags let you merge incomplete work safely
- Small PRs touching 1-2 packages get reviewed fast
- CI runs only affected packages (see below), keeping feedback quick

---

## Partial Clone and Sparse Checkout

### Partial Clone

Skip downloading blob content until needed. Cuts clone time dramatically for large repos.

```bash
# Clone without file contents (fetches on demand)
git clone --filter=blob:none https://github.com/org/monorepo.git

# Clone without trees and blobs (even faster, less local data)
git clone --filter=tree:0 https://github.com/org/monorepo.git
```

### Sparse Checkout

Check out only the directories you work on. Essential when the repo has dozens of packages.

```bash
# Enable sparse checkout (cone mode is faster)
git sparse-checkout init --cone

# Check out only the packages you need
git sparse-checkout set packages/payments packages/shared-lib

# Add another package later
git sparse-checkout add packages/notifications

# View current sparse checkout config
git sparse-checkout list

# Disable and get everything back
git sparse-checkout disable
```

**Combine both** for the fastest developer setup:

```bash
git clone --filter=blob:none https://github.com/org/monorepo.git
cd monorepo
git sparse-checkout init --cone
git sparse-checkout set packages/my-service packages/shared
```

---

## CODEOWNERS and Path-Based Review Rules

Define ownership per package directory so PRs auto-assign the right reviewers.

```bash
# .github/CODEOWNERS
# Global fallback
* @org/platform-team

# Package-level ownership
/packages/payments/       @org/payments-team
/packages/auth/           @org/identity-team
/packages/shared-lib/     @org/platform-team
/packages/web-app/        @org/frontend-team

# Infrastructure files
/infra/                   @org/devops-team
/.github/workflows/       @org/devops-team
/packages/*/Dockerfile    @org/devops-team
```

**Path-based merge rules** (GitHub branch protection):
- Require review from CODEOWNERS for their paths
- Set different approval counts per path if needed (use Ruleset with path filters)
- Prevent merging if any CODEOWNERS review is missing

---

## Affected-Only CI

Running the entire test suite on every PR is wasteful. Run tests only for changed packages and their dependents.

### Nx

```bash
# Run tests only for packages affected by changes since main
npx nx affected --target=test --base=main --head=HEAD

# Build only affected packages
npx nx affected --target=build --base=main --head=HEAD

# Lint only affected
npx nx affected --target=lint --base=main --head=HEAD
```

### Turborepo

```bash
# Run tests for packages changed since main
npx turbo run test --filter=...[main...HEAD]

# Build only changed packages and their dependents
npx turbo run build --filter=...[main...HEAD]
```

### Bazel

```bash
# Query targets affected by changed files
bazel query "rdeps(//..., set($(git diff --name-only main...HEAD)))"

# Test only affected targets
bazel test $(bazel query "rdeps(//..., set($(git diff --name-only main...HEAD)))" \
  --output=label 2>/dev/null | grep '_test$')
```

---

## GitHub Actions: Path-Based Triggers

Trigger workflows only when relevant paths change. Reduces CI cost and queue time.

```yaml
# .github/workflows/payments-ci.yml
name: Payments CI

on:
  push:
    branches: [main]
    paths:
      - 'packages/payments/**'
      - 'packages/shared-lib/**'
  pull_request:
    paths:
      - 'packages/payments/**'
      - 'packages/shared-lib/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx nx test payments
```

For monorepos with many packages, use a dynamic matrix instead of one workflow per package:

```yaml
# .github/workflows/ci.yml
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            payments: 'packages/payments/**'
            auth: 'packages/auth/**'
            web-app: 'packages/web-app/**'

  test:
    needs: detect-changes
    if: needs.detect-changes.outputs.packages != '[]'
    strategy:
      matrix:
        package: ${{ fromJson(needs.detect-changes.outputs.packages) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx nx test ${{ matrix.package }}
```

---

## Tooling Comparison

| Feature | Nx | Turborepo | Bazel |
|---------|-----|-----------|-------|
| **Language** | TypeScript | Go | Java/Starlark |
| **Affected detection** | Built-in graph | `--filter` flag | Query language |
| **Remote cache** | Nx Cloud | Vercel Remote Cache | Remote execution |
| **Learning curve** | Medium | Low | High |
| **Best for** | JS/TS monorepos | JS/TS monorepos | Polyglot, large scale |
| **Task orchestration** | Yes | Yes | Yes |
| **Dependency graph** | Automatic | package.json based | Explicit BUILD files |

---

## Merge Queue Considerations

Monorepos with many packages strain merge queues. Common challenges and mitigations:

| Challenge | Mitigation |
|-----------|------------|
| Slow CI blocks the queue | Affected-only CI, remote caching |
| Many PRs competing to merge | GitHub merge queue with grouping |
| Flaky tests block unrelated packages | Isolate flaky tests, auto-retry |
| Dependency graph changes break cache | Pin dependency graph hash in cache key |
| Large rebases after queue entry | Keep PRs small, merge frequently |

```yaml
# GitHub merge queue settings (repo settings > Rules > Rulesets)
# - Max queue size: 20
# - Group size: 5 (batch merges to reduce CI runs)
# - Timeout: 60 minutes
# - Require branches to be up to date: Yes
```

---

## Decision Table: Monorepo vs Polyrepo

| Factor | Monorepo | Polyrepo |
|--------|----------|----------|
| Shared code between services | Preferred | Publish as packages |
| Cross-cutting refactors frequent | Preferred | Painful |
| Teams fully autonomous | Overhead | Preferred |
| Need atomic multi-package changes | Preferred | Coordinate releases |
| Repo size > 10 GB | Needs sparse checkout | Natural boundary |
| Different CI/CD per service | Path triggers | Preferred |
| Different languages per service | Bazel or separate CI | Preferred |
| < 5 packages | Either works | Either works |
| > 20 packages, same stack | Preferred with Nx/Turbo | Management overhead |

---

## Do / Avoid

**DO**:
- [OK] Use trunk-based development with short-lived branches
- [OK] Set up partial clone and sparse checkout for developer onboarding
- [OK] Define CODEOWNERS per package directory
- [OK] Run affected-only CI to keep feedback loops under 10 minutes
- [OK] Use path-based workflow triggers to reduce unnecessary CI runs
- [OK] Cache aggressively (Nx Cloud, Turborepo remote cache, Bazel remote cache)
- [OK] Keep cross-package PRs small and atomic

**AVOID**:
- [FAIL] Running full test suite on every PR regardless of what changed
- [FAIL] Long-lived feature branches spanning multiple packages
- [FAIL] Skipping CODEOWNERS (leads to changes merged without domain expertise)
- [FAIL] Cloning the full repo with all history in CI (use shallow + partial clone)
- [FAIL] One mega workflow file for all packages (use path-based triggers or dynamic matrix)
- [FAIL] Ignoring the dependency graph when determining what to test

---

## Related Resources

- [Branching Strategies](branching-strategies.md) - Strategy comparison and migration paths
- [Automated Quality Gates](automated-quality-gates.md) - CI/CD checks and enforcement
- [PR Best Practices](pr-best-practices.md) - PR size and review guidelines
