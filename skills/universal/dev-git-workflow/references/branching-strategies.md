# Branching Strategies

Decision support for GitHub Flow, trunk-based development, release branches, and GitFlow. The SKILL.md table gives the default; this file gives the reasoning, the per-model failure modes, hotfix paths, and migrations.

## Contents

- [Deciding Variables](#deciding-variables)
- [Comparison](#comparison)
- [GitHub Flow](#github-flow)
- [Trunk-Based Development](#trunk-based-development)
- [Release Branches](#release-branches)
- [GitFlow](#gitflow)
- [Hotfix Path by Model](#hotfix-path-by-model)
- [Migrations](#migrations)
- [Readiness Checks](#readiness-checks)
- [Anti-Patterns](#anti-patterns)

## Deciding Variables

Choose on these, in this order:

1. **Supported versions.** More than one live version (customers on 2.x and 3.x, app-store builds under review, on-prem installs) is what forces release branches. One live version almost never needs them.
2. **Merge concurrency.** Count concurrently open branches, including agent worktrees. High concurrency favors short-lived branches and a merge queue.
3. **CI speed and stability.** Trunk-based work needs CI that answers quickly and a default branch that is rarely red. Slow or flaky CI pushes teams toward batching, which is what GitFlow formalizes.
4. **Contributor model.** Fork-based contributions rule out pushing to trunk; use PR-based GitHub Flow.
5. **Audit requirements.** Independent approval, signed commits, and traceable release artifacts can be satisfied by any model through rulesets; they do not by themselves justify GitFlow.

## Comparison

| | GitHub Flow | Trunk-based | Release branches | GitFlow |
|--|-------------|-------------|------------------|---------|
| Long-lived branches | main | main | main + `release/*` | main + develop + `release/*` |
| Typical branch life | hours to days | hours to about a day | as long as a version is supported | days to weeks |
| Unfinished work on main | avoided | behind feature flags | behind feature flags | kept on feature branches |
| Release source | deploy or tag main | deploy or tag main | tag the release branch | tag main after release merge |
| Main cost | review latency | flag debt, CI discipline | backporting | double merges, drift between develop and main |

## GitHub Flow

Main is always deployable; every change is a PR to main; deploy from main.

- Fits one production line with frequent deploys, and fork-based open source.
- Breaks down when CI is slow relative to merge rate: PRs go stale and need repeated updates, and semantic conflicts between green PRs break main. The fix is a merge queue, not a new branching model.
- Large features use feature flags or stacked PRs rather than a long-lived branch.

## Trunk-Based Development

Everyone integrates into main at least daily through short-lived branches (or direct commits in very small, high-trust teams); incomplete work hides behind feature flags.

- Needs fast, reliable CI, a feature-flag system, and a culture of small changes. Without all three it degrades into GitHub Flow with more broken builds.
- Flags are the real cost: every flag needs an owner and a removal date, or flag combinations become an untested configuration space.
- At high concurrency add a merge queue so each merge is tested against the actual state of main.
- Scaled variant: cut `release/*` branches from main for scheduled releases; fix on main and cherry-pick into the release branch.

## Release Branches

Cut `release/<version>` from main when a version must be stabilized or supported while main moves on.

- Upstream first: fix on main, then `git cherry-pick -x <sha>` into each supported release branch. `-x` records the source commit, so audits and later backports can trace it.
- Only fixes enter a release branch; no features.
- Each supported branch multiplies backport work. Write down how many versions you support and for how long, and delete branches at end of support.

## GitFlow

`develop` integrates features; `release/*` stabilizes; `main` holds released states; `hotfix/*` branches from main and merges into both main and develop.

- Justified when releases are infrequent and scheduled, several versions are supported, and a release needs a stabilization window that must not block ongoing integration.
- Costs: every release and hotfix is a double merge; forgetting the merge back into develop reintroduces fixed bugs; develop and main drift; CI must cover two integration branches.
- Most teams that "need GitFlow" need release branches cut from main. Try that first.

## Hotfix Path by Model

| Model | Hotfix path |
|-------|-------------|
| GitHub Flow / trunk-based | Short branch from main, expedited review, full CI, deploy. If main contains unreleased work you cannot ship, branch from the last release tag, ship, then land the same fix on main. |
| Release branches | Fix on main, cherry-pick to affected release branches, tag each. |
| GitFlow | `hotfix/*` from main, merge to main and tag, merge to develop (and any open `release/*`). |

In every model an expedited review is still a review, and CI still runs. See [release-management.md](release-management.md) for rollback.

## Migrations

**GitFlow to GitHub Flow or trunk-based**

1. Finish or close open release branches; decide what happens to unmerged features on develop.
2. Merge develop into main one final time, tag, and make main the default branch.
3. Retarget open PRs from develop to main, update CI triggers and rulesets, then delete or archive develop.
4. Introduce feature flags before the first large feature, not after.

Risk: developers keep branching from a stale local develop. Delete it on the remote and announce the change.

**GitHub Flow to trunk-based**

1. Add a feature-flag system and a flag-removal policy.
2. Bring CI time and default-branch failure rate into range; add a merge queue.
3. Shorten branch life gradually. Measure branch age from the PR's first commit or creation time in the host's API, not with ad hoc `git log` counts.

## Readiness Checks

- **GitHub Flow:** automated CI on every PR; one production version; reviews usually turn around within a working day.
- **Trunk-based:** everything above, plus fast CI, rarely-red main, a feature-flag system, and flag ownership.
- **Release branches or GitFlow:** a named release owner, a written support window per version, and a backport process.

## Anti-Patterns

- **Long-lived feature branches.** Weeks of divergence turn into a merge project. Split into stacked PRs or merge behind a flag.
- **Environment branches** (`dev`, `staging`, `prod` promoted by merging). Environments drift and "promotion" merges carry unreviewed differences. Build one artifact from main and promote the artifact.
- **Accidental branch chains.** Branching from a feature branch without meaning to stack creates an unclear base. Branch from main unless you are deliberately stacking ([stacked-diffs-guide.md](stacked-diffs-guide.md)).
- **No protection on main.** Direct pushes bypass review and CI. See the ruleset baseline in SKILL.md.
- **Model by fashion.** Adopting trunk-based development without fast CI and flags, or GitFlow without multiple supported versions.
