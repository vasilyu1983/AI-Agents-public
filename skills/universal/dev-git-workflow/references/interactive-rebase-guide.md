# Interactive Rebase and History Cleanup

When and how to clean up branch history before merge. Whether a rewrite is allowed at all is decided by SKILL.md History-Rewrite Risk Judgment; this file covers the mechanics that keep a permitted rewrite safe.

## Contents

- [When Cleanup Is Worth It](#when-cleanup-is-worth-it)
- [Fixup and Autosquash](#fixup-and-autosquash)
- [Splitting, Rewording, Reordering](#splitting-rewording-reordering)
- [Rebasing Stacks](#rebasing-stacks)
- [Showing Reviewers What Changed](#showing-reviewers-what-changed)
- [Force-Pushing Safely](#force-pushing-safely)
- [Recovery](#recovery)
- [Newer Git Commands](#newer-git-commands)

## When Cleanup Is Worth It

- **Repo squash-merges PRs:** in-branch cleanup mostly does not matter; the PR title and body become the commit. Spend the effort on the PR description instead.
- **Repo rebase-merges or merge-commits:** every commit lands on main, so each should be one logical, building change with a meaningful message. Clean up before requesting review.
- **PR already under review with approvals:** prefer adding commits; rewriting dismisses approvals and hides what changed since the last review.

## Fixup and Autosquash

Record fixes as `fixup!` commits while working, then fold them in once:

```bash
git commit --fixup=<sha>            # fold into <sha>, keep its message
git commit --fixup=amend:<sha>      # fold in and replace its message
git commit --fixup=reword:<sha>     # change only the message
git rebase -i --autosquash origin/main
git config --global rebase.autosquash true   # make autosquash the default for rebase -i
```

`git absorb` (a separate tool) can create the fixup commits automatically by matching staged hunks to the commits that last touched them; review its choices before rebasing.

## Splitting, Rewording, Reordering

- **Split a commit:** mark it `edit` in `rebase -i`, then `git reset HEAD^`, stage and commit the pieces (`git add -p` for partial files), and `git rebase --continue`.
- **Reword:** `reword` in the todo list; for the last commit, `git commit --amend`.
- **Reorder:** move lines in the todo list. Reordering commits that touch the same lines produces conflicts; reorder before the fixups pile up.
- **Test every commit** when the repo rebase-merges: `git rebase -i --exec "<test command>" origin/main` runs the command after each commit and stops at the first failure.

## Rebasing Stacks

`git rebase --update-refs` (Git 2.38 and later) moves every branch that points into the rebased range, so a whole stack of branches can be restacked from its top branch in one command. Set `rebase.updateRefs=true` to make it the default. See [stacked-diffs-guide.md](stacked-diffs-guide.md#manual-stacks-with-plain-git).

## Showing Reviewers What Changed

After rewriting a branch that someone already reviewed, show the difference between the two versions of the series rather than asking for a full re-review:

```bash
git range-diff <old-base>..<old-tip> <new-base>..<new-tip>
# shorter form when both versions share history:
git range-diff <old-tip>...<new-tip>
```

Record the old tip SHA before rewriting so this command has exact inputs.

## Force-Pushing Safely

```bash
old=$(git rev-parse origin/feature)           # the remote tip you rebased on top of
git push --force-with-lease=feature:$old origin feature
```

- A bare `--force-with-lease` compares against your remote-tracking ref, which a background `git fetch` (IDE, agent tooling) can silently update, defeating the lease. Passing the expected SHA explicitly avoids that; `--force-if-includes` adds a check that the remote tip was integrated locally.
- A rejected lease means someone else pushed. Fetch, inspect their commits, and integrate; never retry with bare `--force`.
- Never force-push `main`, release branches, tags, or any branch others build on; rulesets should block it anyway.

## Recovery

| Situation | Recovery |
|-----------|----------|
| Rebase in progress, going wrong | `git rebase --abort` |
| Rebase finished, result wrong | `git reset --hard ORIG_HEAD` right away, or find the pre-rebase tip in `git reflog show <branch>` |
| Pushed a bad rewrite | Push the recorded old tip back with `--force-with-lease=<branch>:<bad-sha>` and tell collaborators |
| Want a safety net first | `git branch backup/<name>` before starting; delete it after merge |

## Newer Git Commands

Git's experimental `git history fixup <commit>` folds staged changes into an earlier commit and updates descendant local branches. It currently does not run Git hooks or support merge histories or conflict-producing rewrites. Keep `--fixup` plus `rebase --autosquash` as the default when those limits matter; check the installed `git history --help` and [Git's command reference](https://git-scm.com/docs/git-history) before recommending it. For future Git upgrades, check [Git's breaking-change list](https://git-scm.com/docs/BreakingChanges) for new-repository defaults such as SHA-256, reftable, and `main`; it gives no Git 3.0 release date and does not deprecate existing SHA-1 repositories.
