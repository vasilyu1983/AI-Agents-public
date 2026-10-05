# Automated Quality Gates

Which checks block a merge, how they interact with merge queues, and how to bypass them without losing control. Starter pipelines are in [assets/ci-cd/github-pr-checks.yml](../assets/ci-cd/github-pr-checks.yml) and [assets/ci-cd/gitlab-mr-checks.yml](../assets/ci-cd/gitlab-mr-checks.yml); the GitHub starter triggers on `pull_request` only, so add the `merge_group` event before using it with a merge queue. What to test and how is owned by the QA skills; supply-chain scanning policy by [dev-dependency-management](../../dev-dependency-management/SKILL.md).

## Contents

- [Choosing Blocking Checks](#choosing-blocking-checks)
- [Required Checks: Mechanics and Traps](#required-checks-mechanics-and-traps)
- [Merge Queue and Merge Train Settings](#merge-queue-and-merge-train-settings)
- [Flaky Checks](#flaky-checks)
- [Emergency Bypass](#emergency-bypass)
- [Exemptions](#exemptions)
- [Local Gates](#local-gates)
- [Watching the Gates](#watching-the-gates)

## Choosing Blocking Checks

A check blocks merge only if it is deterministic, reasonably fast, and a failure means the change is actually wrong. Everything else reports without blocking.

| Usually blocking | Usually reporting only |
|------------------|------------------------|
| build, unit and integration tests on the changed scope | PR size labels |
| lint and type-check with zero-error policy | complexity metrics |
| secret scan | bundle-size and benchmark deltas (block only with a stable baseline and noise margin) |
| dependency vulnerabilities above the team's triage threshold | coverage totals |
| API or schema compatibility check for published interfaces | documentation coverage |

Coverage gates work better on the diff (new and changed lines) than on the repository total: a total threshold punishes the PR that touches legacy code and rewards tests that execute lines without asserting anything. Pick the threshold from the codebase's current state and raise it deliberately, rather than copying a number.

Keep the blocking set small enough that the whole required pipeline finishes well inside the time a developer will wait; slow required checks push people toward bypasses and batching.

## Required Checks: Mechanics and Traps

- **Required checks are matched by name.** Renaming a job, or changing a matrix so the job name changes, leaves the old required check "expected" forever and blocks every PR. Update the ruleset in the same change.
- **Path-filtered required workflows block PRs they skip.** If a required workflow uses `paths:` filters and does not run, the check stays pending. Either make the workflow always run and skip work inside it (report success when nothing relevant changed), or require an aggregate "all checks passed" job that always runs.
- **Merge queues run on their own event.** On GitHub Actions every required workflow needs the `merge_group` trigger; third-party CI must build the queue's temporary branches (check the host docs for the branch pattern). GitLab merge trains run merge request pipelines on the train's merged result.
- **Test the merged result, not only the branch head.** A green branch can still break main after a semantic conflict with another PR; merge-result pipelines, "require branch up to date", or a merge queue close that gap.
- **Pin third-party actions to a commit SHA** in required workflows; a mutable tag in a required check is a supply-chain path into main.
- **Fork PRs:** do not expose secrets to workflows triggered by untrusted forks; gate privileged jobs behind approval.

## Merge Queue and Merge Train Settings

When to adopt a queue and the throughput formula are in SKILL.md (Merge Queue). Settings are judgment calls tied to the repo's own numbers:

- **Build concurrency:** raise it until CI runner capacity or cost becomes the limit; concurrency multiplies runner use.
- **Group size:** larger groups mean fewer CI runs per merged PR, but one failure ejects or retests the whole group. Grow group size only while the queue's failure rate is low.
- **Timeout:** set above the slowest normal pipeline so slow-but-healthy runs are not ejected, and low enough that a hung runner does not stall the queue for hours.
- **Required checks in the queue** should be the same set as on the PR; a check that only runs in the queue surprises authors after approval.
- **Status/failure-handling options** that let a group merge despite some failing entries change what "green main" means. Before enabling any such option, read the host's current documentation for exactly which failures it tolerates; never use it as a way to live with flaky tests.

Measure time-in-queue, ejection rate, and queue length; they tell you whether to cut CI time, fix flakes, or change settings.

## Flaky Checks

A flaky required check teaches everyone to click "re-run" and trusts failures less each time.

1. Detect: track reruns that pass without code changes, per test.
2. Quarantine: move the test to a non-blocking job with an owner and a ticket; do not delete it or mark the whole job optional.
3. Fix or remove within an agreed period; a quarantine that only grows is a disabled test suite.

Automatic retries of failed tests hide flakiness from the metrics; if you use them, record every retry.

## Emergency Bypass

For a production outage, an actively exploited vulnerability, or ongoing data loss:

- Use the ruleset's bypass list (named people or a break-glass role), not a commit-message CI skip. `[skip ci]`-style markers skip the pipeline entirely and leave nothing to review later.
- The change still gets the fastest meaningful subset of checks before merge where possible, and full CI immediately after merge.
- Record who bypassed, why, and the follow-up issue (missing tests, full review). Review bypasses in the retrospective; frequent bypasses mean the gates are too slow or too flaky.

## Exemptions

Path-based exemptions (legacy code excluded from a coverage gate, generated code excluded from lint) are acceptable when each one has a reason, an owner, and an expiry date that CI enforces: an exemption past its expiry fails the gate. Exemptions without expiry become permanent holes.

## Local Gates

Local hooks give fast feedback but are optional for the developer (`--no-verify`) and not a control. Everything that must hold is enforced again in CI. Hook setup is in [git-hooks-automation.md](git-hooks-automation.md).

## Watching the Gates

Track per repository: required-pipeline duration, flaky-rerun rate, queue time and ejections, bypass count, and main-branch breakage. Compare trends after each gate change instead of chasing published targets.
