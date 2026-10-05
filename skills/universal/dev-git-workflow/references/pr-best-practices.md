# Pull Request Practices

Workflow policy for creating, reviewing, and merging PRs. Line-by-line code review technique lives in [software-code-review](../../software-code-review/SKILL.md); commit-message and PR-title format lives in [dev-git-commit-message](../../dev-git-commit-message/SKILL.md).

## Contents

- [Sizing](#sizing)
- [Description Contract](#description-contract)
- [Review Policy](#review-policy)
- [Comment Severity](#comment-severity)
- [Responding to Review](#responding-to-review)
- [Merge Methods in Detail](#merge-methods-in-detail)
- [Draft PRs and Auto-Merge](#draft-prs-and-auto-merge)
- [Agent-Authored PRs](#agent-authored-prs)
- [Measuring the PR Process](#measuring-the-pr-process)
- [Pitfalls](#pitfalls)

## Sizing

The right size is the largest change a reviewer can understand in one sitting without losing context. Line counts are a proxy: a 600-line generated migration can be easier to review than a 60-line concurrency change.

| PR shape | Action |
|----------|--------|
| One logical change | Keep it self-contained and described |
| Feature + refactor + bugfix | Split: refactor first (no behavior change), then the feature, then the fix |
| Dependent layers | Stack them ([stacked-diffs-guide.md](stacked-diffs-guide.md)) |
| Too large to finish before main moves | Merge in slices behind a feature flag |

Behavior-preserving refactors and behavior changes belong in separate PRs: the reviewer can then verify "nothing changed" and "the right thing changed" as two easy questions instead of one hard one. Mechanical changes (renames, formatting, generated code) get their own PR and say so in the title.

A size warning in CI (for example, a comment above a few hundred changed lines excluding generated files and lockfiles) nudges without blocking. Hard size blocks get bypassed with worse splits.

## Description Contract

Every PR description answers, in this order:

1. **What and why:** one or two sentences, plus the linked issue.
2. **Risk:** what could break and who would notice.
3. **How it was verified:** tests added or run, manual checks, environments.
4. **Rollout and rollback:** migrations, flags and their defaults, config or secrets needed, backward compatibility, how to undo.
5. **Where to look:** the files or decisions the author wants scrutinized.

Screenshots for UI changes, benchmark numbers for performance claims, and a security note for auth or input-handling changes are required when applicable. The template is in [assets/pull-requests/pr-template.md](../assets/pull-requests/pr-template.md).

## Review Policy

- Set a review-latency target the team can keep (for example, first response within one working day) and measure it. Unreviewed PRs are the most common cause of stale branches and conflicts.
- Required approvals come from someone other than the author; CODEOWNERS covers sensitive paths. Two approvals for high-risk paths only; requiring two everywhere mainly adds latency.
- Dismiss stale approvals on new pushes so approval always refers to the code being merged.
- Reviewers pull and run complex changes rather than reviewing the diff alone.
- Style is enforced by formatters and linters in CI, not in review comments.

## Comment Severity

Prefix comments so the author knows what blocks merge:

| Prefix | Meaning |
|--------|---------|
| `blocker:` | Must change before merge: correctness, security, data loss, breaking change |
| `should:` | Expected to change, or explain why not |
| `nit:` | Optional; never blocks |
| `question:` | Needs an answer, not necessarily a change |

A useful blocking comment names the problem, where it is, why it matters, and a concrete fix or alternative.

## Responding to Review

- Answer every comment: a fix (link the commit) or a reason.
- Push fixes as new commits during review so reviewers can see what changed since their last pass; squash at merge time if the repo squashes. If you must rewrite, post `git range-diff` output.
- Move out-of-scope suggestions to a linked follow-up issue and say so in the thread.
- Re-request review after addressing blockers; the reviewer resolves their own threads where the host allows it.

## Merge Methods in Detail

SKILL.md sets the default (one method per repository). The details that decide edge cases:

- **Squash:** the squash commit's message comes from the PR title and body, so lint the PR title. `Co-authored-by:` trailers from individual commits are only kept if the host copies them into the squash message; check before relying on them for attribution. Squashing the base of a stack requires `rebase --onto` for the next layer.
- **Rebase-merge:** every commit lands on main, so every commit must build and pass tests, or bisect will stop on broken states. Landed SHAs differ from reviewed SHAs.
- **Merge commit:** the only method that lands exactly the SHAs CI tested on the branch. Use `git log --first-parent` and `git bisect --first-parent` to read main as a sequence of PRs.
- **Reverting:** a squash or rebase-merged PR reverts with `git revert <sha>` (one or several commits); a merge commit reverts with `git revert -m 1 <merge-sha>`, and re-landing that branch later requires reverting the revert first.

## Draft PRs and Auto-Merge

- Open a draft PR early for direction feedback; mark it ready only when the description contract is complete.
- Enable auto-merge once approved, so the PR lands when required checks pass instead of waiting for the author to return. With a merge queue, auto-merge enqueues the PR.

## Agent-Authored PRs

- A human reviews every agent-authored PR before merge; an AI reviewer's comments are input, not an approval.
- The agent's own summary is a claim to verify, not evidence. Require the repo's real gate output (CI run) rather than the agent's report of local test results.
- Label agent PRs (label or bot author) so review load and defect rates can be measured separately.
- Budget human review time explicitly when agents raise PR volume; reviewer time, not agent throughput, sets the ceiling.

## Measuring the PR Process

Track trends locally rather than chasing published targets: time to first review, time to merge, review rounds, PR size distribution, revert rate, and PRs idle without activity. Compare before and after a process change; do not use these as individual performance metrics, because that rewards splitting and rubber-stamping.

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| PRs wait days for review | Review rotation or auto-assignment, a measured latency target, smaller PRs |
| Bike-shedding on style | Formatter and linter in CI; `nit:` never blocks |
| Rubber-stamp approvals | CODEOWNERS for risky paths, reviewers run the change, review quality discussed in retros |
| Force-push mid-review wipes context | Add commits during review; rewrite only with range-diff |
| Unclear PR descriptions | Enforce the description contract with the template and a PR-body check |
