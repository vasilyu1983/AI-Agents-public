# Interactive Rebase & History Cleanup

Maintain clean commit history before merging using interactive rebase and auto-squash workflows.

## Contents

- Auto-Squash Workflow (Modern Practice)
- Interactive Rebase Commands
- Quick Example - Clean Up Before PR
- Rewriting Commit Messages
- Splitting Commits
- Reordering Commits
- Best Practices
- Force Push Safely
- Recovering from Mistakes
- Advanced: Autosquash with Commit Hash
- Related Resources

---

## Auto-Squash Workflow (Modern Practice)

Enable auto-squash globally for cleaner workflow:

```bash
git config --global rebase.autosquash true
```

### Workflow with Auto-Squash

**1. Work with WIP commits**:
```bash
git commit -m "feat: add user service"
git commit -m "WIP test coverage"
git commit -m "WIP fix typo"
git commit -m "WIP add validation"
```

**2. Mark fixup commits**:
```bash
# Instead of "WIP", use fixup! or squash!
git commit -m "fixup! feat: add user service"  # Squashes silently
git commit -m "squash! feat: add user service" # Squashes with message
```

**3. Rebase auto-squashes**:
```bash
git rebase -i main  # Auto-squash flag triggers automatically
# Commits are automatically organized and squashed
```

---

## Interactive Rebase Commands

| Command | Short | Action |
|---------|-------|--------|
| `pick` | `p` | Keep commit as-is |
| `reword` | `r` | Keep commit, edit message |
| `edit` | `e` | Pause to amend commit |
| `squash` | `s` | Combine with previous, keep message |
| `fixup` | `f` | Combine with previous, discard message |
| `drop` | `d` | Remove commit |

---

## Quick Example - Clean Up Before PR

```bash
# Your messy history
git log --oneline
a1b2c3d WIP add tests
b2c3d4e fix typo
c3d4e5f feat: implement user authentication
d4e5f6g initial commit

# Interactive rebase
git rebase -i HEAD~3

# Editor opens with:
pick c3d4e5f feat: implement user authentication
pick b2c3d4e fix typo
pick a1b2c3d WIP add tests

# Change to:
pick c3d4e5f feat: implement user authentication
fixup b2c3d4e fix typo
fixup a1b2c3d WIP add tests

# Result: Clean single commit
git log --oneline
c3d4e5f feat: implement user authentication
```

---

## Rewriting Commit Messages

### Rewording Last Commit

```bash
git commit --amend -m "feat(auth): implement JWT authentication"
```

### Rewording Older Commits

```bash
# Rebase to reword commit 3 commits back
git rebase -i HEAD~3

# In editor:
reword c3d4e5f feat: implement user authentication
pick b2c3d4e fix typo
pick a1b2c3d add tests

# Save, then editor opens again for each 'reword'
# Update commit message and save
```

---

## Splitting Commits

Break a large commit into multiple focused commits:

```bash
# Start interactive rebase
git rebase -i HEAD~3

# In editor, mark commit to split:
edit c3d4e5f feat: implement multiple features
pick b2c3d4e fix typo

# When rebase pauses:
git reset HEAD~1  # Undo commit, keep changes

# Stage and commit incrementally
git add src/auth.ts
git commit -m "feat: add JWT authentication"

git add src/validation.ts
git commit -m "feat: add input validation"

git add tests/
git commit -m "test: add auth and validation tests"

# Continue rebase
git rebase --continue
```

---

## Reordering Commits

Change commit order during interactive rebase:

```bash
git rebase -i HEAD~4

# In editor, reorder lines:
pick a1b2c3d docs: update README
pick c3d4e5f feat: implement user authentication
pick b2c3d4e fix typo
pick d4e5f6g test: add auth tests

# Becomes:
pick c3d4e5f feat: implement user authentication
pick d4e5f6g test: add auth tests
pick b2c3d4e fix typo
pick a1b2c3d docs: update README
```

---

## Best Practices

**DO**:
- [OK] Squash WIP, debug, and fixup commits before merging
- [OK] Rebase frequently to avoid complex conflicts
- [OK] Keep logical commits separate (feature ≠ tests ≠ docs)
- [OK] Use `--autosquash` for cleaner workflow
- [OK] Test after rebasing to ensure nothing broke

**DON'T**:
- [FAIL] Rebase commits already pushed to `main`
- [FAIL] Rebase shared branches others are working on
- [FAIL] Force push to protected branches
- [FAIL] Squash meaningful commits (feature milestones)
- [FAIL] Rebase if you don't understand what you're doing

---

## Force Push Safely

When you've rebased and need to update remote:

```bash
# Safer than --force (prevents overwriting others' work)
git push --force-with-lease origin feature-branch

# If rejected, someone else pushed - fetch and review first
git fetch origin
git log origin/feature-branch
```

**Never force push to**:
- `main` or `master` branches
- Shared feature branches
- Any branch others are working on

---

## Recovering from Mistakes

### Undo Rebase

```bash
# Find commit before rebase started
git reflog

# Reset to that commit
git reset --hard HEAD@{5}  # Adjust number based on reflog
```

### Abort Rebase in Progress

```bash
git rebase --abort
```

---

## Advanced: Autosquash with Commit Hash

When you discover a typo in an older commit:

```bash
# Find commit hash
git log --oneline
c3d4e5f feat: implement user authentication

# Create fixup commit referencing hash
git commit --fixup=c3d4e5f

# Rebase auto-squashes
git rebase -i main --autosquash
```

---

## Related Resources

- [Conventional Commits Standard](commit-conventions.md) - Commit message formats
- [PR Best Practices Guide](pr-best-practices.md) - PR size and review guidelines
- [Conflict Resolution Techniques](conflict-resolution.md) - Handling merge conflicts
