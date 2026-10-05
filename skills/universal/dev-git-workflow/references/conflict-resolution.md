# Conflict Resolution

Judgment for preventing, resolving, and recovering from merge and rebase conflicts. Assumes you know conflict markers and `merge`/`rebase --continue`.

## Contents

- [Prevention Is a Process Decision](#prevention-is-a-process-decision)
- [Updating a Branch: Merge or Rebase](#updating-a-branch-merge-or-rebase)
- [Resolution Rules](#resolution-rules)
- [Traps](#traps)
- [Helpful Configuration](#helpful-configuration)
- [Recovery](#recovery)
- [Agent Rules](#agent-rules)

## Prevention Is a Process Decision

Most conflicts come from long-lived branches, not from bad luck.

- Keep branches short-lived and integrate main at least daily.
- Separate mechanical changes (renames, formatting, moves) into their own PR and land them fast; announce repo-wide mechanical changes so others can rebase before, not after.
- Put incomplete work behind feature flags instead of holding it on a branch.
- Give parallel agents disjoint file ownership; check overlap before merging with `comm -12 <(git diff --name-only main...a | sort) <(git diff --name-only main...b | sort)`. Use three dots (merge base), not two.
- Order dependent work upstream-first: merge the contract or schema change, then rebase the consumers.

## Updating a Branch: Merge or Rebase

| Situation | Update with |
|-----------|-------------|
| Branch only you (or one agent) pushes, no approvals yet | `git rebase origin/main` |
| Branch has approvals or active review | `git merge origin/main` (a rewrite dismisses approvals and loses review context) |
| Branch others commit to | merge |
| Many commits each conflicting on the same lines | merge once, or squash locally first, then rebase; replaying ten conflicts one by one invites mistakes |

Rebase conflicts are resolved per replayed commit; merge conflicts are resolved once. When the same hunk conflicts in several commits, a merge is often safer.

## Resolution Rules

1. **Understand both sides before editing.** Read what each side intended (`git log --merge -p <file>` shows the commits that touched the conflicted file on both sides). Keeping one side wholesale is correct only when you know the other side's intent is obsolete.
2. **Regenerate generated files instead of hand-merging them.** Lockfiles, snapshots, generated clients, and compiled assets: take either side, then rerun the generator or package manager and commit the result.
3. **Textually clean is not semantically clean.** A merge with no conflicts can still break: one side renames a function while the other adds a new call to the old name. Always build and run tests after any merge or rebase, not only after conflicted ones.
4. **Check for leftover markers** before committing: `git diff --check` flags them along with whitespace errors. Stage only the resolved paths. If the installed Git supports `git add --resolved`, it can stage formerly conflicted paths while leaving unrelated changes unstaged and rejects remaining conflict markers; check `git add --help` before using it ([release notes](https://github.com/git/git/blob/master/Documentation/RelNotes/2.56.0.adoc)).
5. **Explain non-obvious resolutions** in the merge commit message or PR description so reviewers can check them.
6. **Pair on conflicts in code you do not own.** The author of the other side resolves faster and more correctly.

## Traps

- **Ours and theirs flip during rebase.** In `git merge`, "ours" is your current branch. In `git rebase`, "ours" is the branch you are rebasing onto (upstream) and "theirs" is your own commit being replayed. Double-check before `git checkout --ours/--theirs <file>` during a rebase.
- **`-X ours` is not `-s ours`.** `git merge -X ours` resolves only conflicting hunks in favor of your side and still takes the other side's non-conflicting changes. `git merge -s ours` discards the other branch's changes entirely while recording it as merged. The second is almost never what people want.
- **Delete/modify conflicts.** One side deleted a file the other modified. Decide whether the modification must move elsewhere (the code may have been relocated, not removed); `git rm` or `git add` the file to record the choice.
- **Both-added files.** Two branches created the same path independently; usually the two implementations must be merged by hand or one renamed.
- **rerere replays mistakes.** `rerere` reuses a recorded resolution silently. If a resolution was wrong, forget it (`git rerere forget <path>`) before redoing the merge, or it comes back.

## Helpful Configuration

```bash
git config --global merge.conflictStyle zdiff3   # show the common ancestor in conflict hunks
git config --global rerere.enabled true          # reuse resolutions across repeated rebases
git config --global rerere.autoUpdate false      # keep reused resolutions unstaged so you review them
```

The ancestor section (`|||||||`) is the most useful part of a conflict: it shows what both sides changed from, so you can combine intent rather than pick a side. `zdiff3` needs a Git version that supports it; fall back to `diff3` on older Git.

## Recovery

| Situation | Recovery |
|-----------|----------|
| Merge or rebase in progress and going badly | `git merge --abort` / `git rebase --abort` |
| Merge just completed locally, not pushed | `git reset --hard ORIG_HEAD` (after confirming the tree has nothing else uncommitted) |
| Rebase completed, result wrong | find the pre-rebase tip in `git reflog` (or `ORIG_HEAD`) and reset the branch to it |
| Bad merge already pushed to a shared branch | `git revert -m 1 <merge-sha>`; do not rewrite shared history |
| Re-landing a branch whose merge was reverted | revert the revert first, then merge the new commits; otherwise Git considers the old commits already merged and silently drops them |
| Lost commits | `git reflog` (and `git fsck --lost-found` for unreachable objects) |

## Agent Rules

- On any conflict, an agent stops making new edits, resolves file by file, and reruns the relevant tests before continuing.
- An agent does not resolve conflicts in files outside its ownership; it reports them to the orchestrator or human.
- An agent never resolves by taking one side wholesale across the tree (`-X ours`/`-X theirs` or `checkout --ours .`) without explicit instruction.
