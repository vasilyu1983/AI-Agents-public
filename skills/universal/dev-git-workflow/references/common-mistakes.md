# Common Git Workflow Mistakes

An index from symptom to fix. Each fix points to the reference that owns the full rule.

| Mistake | Why it hurts | Fix | Owner |
|---------|--------------|-----|-------|
| Large PR mixing feature, refactor, and bugfix | Review quality drops; one problem blocks everything; revert takes all of it | Split behavior-preserving refactors from behavior changes; stack dependent layers | [pr-best-practices.md](pr-best-practices.md#sizing), [stacked-diffs-guide.md](stacked-diffs-guide.md) |
| Vague commit messages ("fix stuff") | Breaks changelog and release automation; history cannot be searched | Follow the repo convention; lint PR titles when squash-merging | [dev-git-commit-message](../../dev-git-commit-message/SKILL.md) |
| Rewriting shared history | Collaborators' branches diverge; approvals dismissed; work silently lost | Rewrite only unshared branches; `--force-with-lease` against a recorded tip; revert instead on shared branches | SKILL.md History-Rewrite Risk Judgment |
| Starting work on a stale base | Late, large conflicts; code written against an old schema | Branch from a freshly fetched `origin/main`; integrate at least daily | [conflict-resolution.md](conflict-resolution.md#prevention-is-a-process-decision) |
| Committing secrets | Exposure persists in clones, forks, and host-side refs even after a rewrite | Rotate first; push protection and a pre-commit secret scan; rewrite with `git filter-repo` only if still needed | SKILL.md History-Rewrite Risk Judgment, [git-hooks-automation.md](git-hooks-automation.md) |
| Ignoring review comments | Known defects ship; reviewers disengage | Answer every comment with a fix or a reason; `blocker:` comments block merge | [pr-best-practices.md](pr-best-practices.md#responding-to-review) |
| Pushing without running the gate | CI becomes the first test run; main breaks under concurrency | Run the repo gate locally; required checks plus merge queue on main | [automated-quality-gates.md](automated-quality-gates.md) |
| Bare `git push --force` | Overwrites commits pushed since your last fetch | `--force-with-lease` (ideally with an explicit expected SHA); a lease rejection means stop and inspect | [interactive-rebase-guide.md](interactive-rebase-guide.md#force-pushing-safely) |
| `git stash` in a tree shared with agents | Sweeps other agents' uncommitted work into one shared stash | Commit, move work to its own worktree, or stop | SKILL.md Local Safety Preflight |
| Mixed merge methods in one repo | History, bisect, and revert behave differently per PR | One allowed merge method in the ruleset | SKILL.md Merge Method |
| Unclear PR description | Reviewers guess at intent, risk, and rollback | Use the description contract and template | [pr-best-practices.md](pr-best-practices.md#description-contract) |
| Deleting "merged" branches with `git branch --merged` after squash merges | Squash-merged branches never show as merged, so cleanup misses them (or people force-delete unmerged work) | Use the host's merged-PR state to decide what to delete | [ai-agent-worktrees.md](ai-agent-worktrees.md#cleanup) |
