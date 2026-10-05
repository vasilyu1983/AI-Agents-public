# Monorepo Git Workflows

Git-level decisions for monorepos: clone shape, ownership, affected-only CI, and merge-queue interplay. Build-system internals (task graphs, remote caching) belong to the build tool's own docs.

## Contents

- [Monorepo or Polyrepo](#monorepo-or-polyrepo)
- [Branching](#branching)
- [Clone Shape: Partial Clone and Sparse Checkout](#clone-shape-partial-clone-and-sparse-checkout)
- [CODEOWNERS](#codeowners)
- [Affected-Only CI](#affected-only-ci)
- [Merge Queues in Monorepos](#merge-queues-in-monorepos)
- [Pitfalls](#pitfalls)

## Monorepo or Polyrepo

| Factor | Favors monorepo | Favors polyrepo |
|--------|-----------------|-----------------|
| Shared code | many packages change together | shared code is stable and can be versioned and published |
| Cross-cutting changes | frequent; atomic multi-package commits matter | rare |
| Team autonomy | shared tooling and conventions are acceptable | teams need independent toolchains, access control, or release cadence |
| Access control | everyone may read everything | some code must be restricted (repo-level permissions are the simple control) |
| CI capability | you can invest in affected-only CI and caching | per-repo pipelines are enough |

A monorepo without affected-only CI and ownership rules becomes slow and unowned; do not adopt one without planning both.

## Branching

Trunk-based development with short-lived branches is the default. A long-lived branch in a monorepo diverges from every package at once, and conflicts compound. Put incomplete work behind flags. Scope commits and PRs to one package where possible (the commit scope names it; see [dev-git-commit-message](../../dev-git-commit-message/SKILL.md)); cross-package changes land atomically in one PR only when they must.

## Clone Shape: Partial Clone and Sparse Checkout

| Who | Clone | Why |
|-----|-------|-----|
| Developer | `git clone --filter=blob:none <url>` (blobless) | full history of commits and trees, file contents fetched on demand; `log`, `blame`, and `merge-base` stay usable |
| CI job that builds one commit | `--filter=tree:0` (treeless) or a shallow clone | smallest download; history operations trigger slow on-demand fetches, so do not use it for developer work |
| CI job that computes affected packages | blobless, or shallow with enough depth to include the merge base | affected detection needs the merge base with the target branch |

Sparse checkout limits the working tree to the directories you need:

```bash
git clone --filter=blob:none --sparse <url> monorepo && cd monorepo
git sparse-checkout set packages/payments packages/shared   # cone mode is the default for `set`
git sparse-checkout add packages/notifications
git sparse-checkout disable                                  # back to a full checkout
```

Sparse checkout hides files but does not change what the build needs; if a package depends on something outside the sparse set, builds fail locally while CI passes. Include dependencies in the set, or generate the set from the build graph.

## CODEOWNERS

```text
# .github/CODEOWNERS: the LAST matching pattern wins
*                        @org/platform
/packages/payments/      @org/payments
/packages/auth/          @org/identity
/.github/workflows/      @org/devops
/packages/*/Dockerfile   @org/devops
```

- **Last match wins, and it replaces, not adds.** With the file above, a change to `packages/payments/Dockerfile` needs `@org/devops` only, not payments. Put broad defaults first and specific paths last, and list several owners on one line when both must be able to approve.
- A CODEOWNERS entry only blocks merge when the ruleset requires code-owner review.
- Protect the CODEOWNERS file itself (and `.github/workflows/`) with an owner, or anyone can reassign ownership in the same PR.
- Owners must be teams or users with write access; invalid entries are silently ignored. Check the host's CODEOWNERS error view after edits.

## Affected-Only CI

Run tests for the packages a change touches plus their dependents, computed against the merge base with the target branch (`main...HEAD`, three dots), not the current tip of main.

- Use the build tool's affected command (for example `nx affected`, Turborepo filters such as `--filter=...[origin/main...HEAD]`, or a Bazel `rdeps` query) rather than hand-written path lists; path lists miss transitive dependents.
- Changes to root files (lockfile, root build config, CI config, toolchain version) affect everything; run the full suite.
- Run the full suite on main after merge (or nightly) as a safety net for gaps in the dependency graph.
- In CI, make sure the base is fetched: a shallow checkout without the merge base computes the wrong set or fails.

**Required checks with path filters.** A workflow with `paths:` filters that is also a required check stays pending when it does not run, blocking unrelated PRs and merge-queue entries. Use one always-running required job that decides internally what to test (a detect-changes job feeding a dynamic matrix, plus a final aggregate job that is the only required check). See [automated-quality-gates.md](automated-quality-gates.md#required-checks-mechanics-and-traps).

## Merge Queues in Monorepos

- The queue tests the combination of PRs, so affected-only detection in the queue must use the queue's base, not each PR's original base.
- "Require branches to be up to date" and a merge queue solve the same problem; with a queue enabled, the queue does the updating, and requiring authors to keep branches current only adds update-and-rerun cycles.
- Flaky tests in one package eject PRs for unrelated packages; quarantine them quickly.
- If queue throughput is still too low after affected-only CI and caching, consider partitioning the queue by path where the host supports it (check its docs), or separate required checks per area.

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Full test suite on every PR | Affected-only CI plus full runs on main |
| Treeless clones for developers | Blobless for developers; treeless only for single-commit CI builds |
| Path-filtered required checks | One always-running required aggregate job |
| CODEOWNERS ordered specific-first | Broad patterns first; last match wins |
| Affected detection against the tip of main | Diff against the merge base |
| Long-lived cross-package branches | Trunk-based with flags |
