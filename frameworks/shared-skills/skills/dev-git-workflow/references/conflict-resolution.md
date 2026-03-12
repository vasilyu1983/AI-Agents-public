# Merge Conflict Resolution Guide

Comprehensive guide to preventing, understanding, and resolving Git merge conflicts.

## Contents

- Understanding Conflicts
- Prevention Strategies
- Conflict Resolution Strategies
- Rebase vs Merge
- Common Conflict Scenarios
- Advanced Resolution Techniques
- Conflict Resolution Checklist
- Testing After Conflict Resolution
- Team Conflict Resolution Practices
- Tools and Workflows
- Recovery from Mistakes
- Quick Reference

---

## Understanding Conflicts

### What Causes Conflicts?

Git conflicts occur when:
1. Two branches modify the **same lines** in the same file
2. One branch modifies a file, another deletes it
3. Both branches add a file with the same name but different content

### Conflict Markers

```
<<<<<<< HEAD (your changes)
const API_URL = "https://api.prod.com";
=======
const API_URL = "https://api.staging.com";
>>>>>>> feature/new-api (their changes)
```

**Components**:
- `<<<<<<<` - Start of conflict
- `=======` - Divider between versions
- `>>>>>>>` - End of conflict
- `HEAD` - Your current branch
- `feature/new-api` - Branch being merged

---

## Prevention Strategies

### 1. Merge/Rebase Frequently

**Pull from main daily**:
```bash
# At start of day
git checkout feature/my-feature
git fetch origin
git rebase origin/main

# Or merge if rebase is too complex
git merge origin/main
```

**Why it helps**: Smaller, incremental conflicts are easier to resolve than large accumulated conflicts.

### 2. Communicate with Team

**Before refactoring**:
- Announce in team chat: "Refactoring auth module today"
- Check who else is working on same area
- Coordinate to avoid overlapping changes

### 3. Small, Focused PRs

**Good** (small, focused):
```bash
# PR 1: Refactor auth service
# PR 2: Add OAuth2 (depends on PR 1)
# PR 3: Add 2FA (depends on PR 1)
```

**Bad** (large, overlapping):
```bash
# PR 1: Huge rewrite touching 50 files
# PR 2: Another huge rewrite overlapping 30 files
# Result: Massive conflicts
```

### 4. Use Feature Flags

**Avoid conflicts in shared files**:
```javascript
// Instead of modifying shared config directly
export const config = {
  // Old way: everyone edits this file
  apiUrl: process.env.API_URL,
};

// Use feature flags
export const config = {
  apiUrl: featureFlags.isEnabled('newApi')
    ? 'https://api-v2.com'
    : 'https://api-v1.com',
};
```

---

## Conflict Resolution Strategies

### Strategy 1: Accept Ours vs Theirs

**Use when**: One version is clearly correct.

**Keep your changes**:
```bash
git checkout --ours path/to/file
git add path/to/file
```

**Keep their changes**:
```bash
git checkout --theirs path/to/file
git add path/to/file
```

**Example**:
```bash
# Conflict in config file
# You: production URL
# Them: staging URL
# Decision: Keep production (yours)

git checkout --ours config/api.ts
git add config/api.ts
git commit -m "merge: resolve conflict, keep production API URL"
```

### Strategy 2: Manual Resolution

**Use when**: Need both changes or custom solution.

**Steps**:
1. Open file in editor
2. Find conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Edit to combine or choose parts
4. Remove all markers
5. Stage and commit

**Example - Before**:
```javascript
<<<<<<< HEAD
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
=======
function calculateTotal(items) {
  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  return total;
}
>>>>>>> feature/quantity-support
```

**After - Combined**:
```javascript
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}
```

### Strategy 3: Use Merge Tool

**Visual conflict resolution** with 3-way diff.

**Configure merge tool**:
```bash
# VS Code
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Or use default (opendiff, vimdiff, etc.)
git mergetool
```

**Usage**:
```bash
# When conflict occurs
git mergetool

# Opens visual diff showing:
# - Left: your changes (ours)
# - Right: their changes (theirs)
# - Bottom: result (edit this)

# Save and close when done
git add resolved-file
git commit
```

---

## Rebase vs Merge

### When to Use Merge

**Use merge when**:
- Working on shared branch
- History preservation is important
- Multiple developers on same branch
- Conflicts are complex (easier to track in merge commit)

**Command**:
```bash
git checkout feature/my-feature
git merge main

# If conflicts, resolve and:
git add .
git commit -m "merge: resolve conflicts with main"
```

**Result**:
```
*   merge commit
|\
| * main commit 3
| * main commit 2
* | feature commit 2
* | feature commit 1
|/
* main commit 1
```

### When to Use Rebase

**Use rebase when**:
- Working on solo feature branch
- Want clean linear history
- Preparing for PR (clean up commits)
- Conflicts are simple

**Command**:
```bash
git checkout feature/my-feature
git rebase main

# If conflicts, resolve and:
git add .
git rebase --continue

# Repeat for each commit with conflicts
```

**Result** (linear history):
```
* feature commit 2 (rebased)
* feature commit 1 (rebased)
* main commit 3
* main commit 2
* main commit 1
```

### Rebase Conflict Resolution Workflow

```bash
# Start rebase
git rebase main

# Git stops at first conflict
# CONFLICT (content): Merge conflict in file.ts

# Check status
git status
# Shows conflicted files

# Resolve conflicts in editor
vim file.ts
# Edit, remove markers, save

# Stage resolved file
git add file.ts

# Continue rebase
git rebase --continue

# Repeat until all commits rebased

# If you get stuck or make mistakes
git rebase --abort  # Cancel and go back to before rebase
```

---

## Common Conflict Scenarios

### Scenario 1: Same Line Modified

**Conflict**:
```javascript
<<<<<<< HEAD
const timeout = 5000;
=======
const timeout = 3000;
>>>>>>> feature/reduce-timeout
```

**Resolution** (decide which value or combine):
```javascript
// Option 1: Choose one
const timeout = 3000;  // Use their value

// Option 2: Use config
const timeout = process.env.TIMEOUT || 5000;
```

### Scenario 2: Function Modified Differently

**Conflict**:
```javascript
<<<<<<< HEAD
function authenticate(username, password) {
  return bcrypt.compare(password, user.passwordHash);
}
=======
function authenticate(username, password, token) {
  return bcrypt.compare(password, user.passwordHash) && validateToken(token);
}
>>>>>>> feature/2fa
```

**Resolution** (keep 2FA version):
```javascript
function authenticate(username, password, token) {
  const passwordValid = bcrypt.compare(password, user.passwordHash);
  const tokenValid = token ? validateToken(token) : true;
  return passwordValid && tokenValid;
}
```

### Scenario 3: Import Statements

**Conflict**:
```javascript
<<<<<<< HEAD
import { useState, useEffect } from 'react';
import { fetchUser } from './api';
=======
import { useState } from 'react';
import { fetchUser, fetchPosts } from './api';
>>>>>>> feature/add-posts
```

**Resolution** (combine both):
```javascript
import { useState, useEffect } from 'react';
import { fetchUser, fetchPosts } from './api';
```

### Scenario 4: File Deleted in One Branch

**Conflict**:
```
CONFLICT (modify/delete): legacy-api.ts deleted in their branch and modified in HEAD.
```

**Resolution options**:
```bash
# Keep the file (your modification)
git add legacy-api.ts

# Delete the file (their deletion)
git rm legacy-api.ts
```

**Decision factors**:
- Is the file still needed?
- Were the modifications important?
- Can functionality move elsewhere?

### Scenario 5: Same File Added Differently

**Conflict**:
```
CONFLICT (add/add): Merge conflict in config.ts
```

Both branches added `config.ts` with different content.

**Resolution**:
```bash
# View both versions
git show :2:config.ts  # Your version
git show :3:config.ts  # Their version

# Manually combine or choose one
vim config.ts
# Edit to combine best of both
git add config.ts
```

---

## Advanced Resolution Techniques

### Interactive Rebase to Resolve Conflicts

Sometimes better to rebase interactively and skip/edit commits:

```bash
# Interactive rebase
git rebase -i main

# Options in editor:
pick abc123 feat: add feature A
drop def456 feat: add feature B (conflicts with main)
pick ghi789 feat: add feature C

# Or edit to resolve differently
```

### Cherry-Pick with Conflict

**Pick specific commits from another branch**:
```bash
# Cherry-pick commit from feature branch
git cherry-pick abc123

# If conflict, resolve and continue
git add .
git cherry-pick --continue

# Or abort
git cherry-pick --abort
```

### Recursive Theirs/Ours Strategy

**Auto-resolve conflicts** (use with caution):
```bash
# Merge with "ours" strategy (keep your changes on conflict)
git merge -X ours feature-branch

# Merge with "theirs" strategy (keep their changes on conflict)
git merge -X theirs feature-branch

# Rebase with "theirs" (note: reversed in rebase)
git rebase -X theirs main
```

**When to use**:
- Mass refactoring where you know your version is correct
- Reverting temporary changes
- Emergency hotfix where conflicts are expected

**Warning**: This auto-resolves ALL conflicts, which can be dangerous.

---

## Conflict Resolution Checklist

### Before Resolving

- [ ] Understand what both changes are trying to accomplish
- [ ] Check with author if their change is unclear
- [ ] Review commit messages for context
- [ ] Decide on resolution strategy (manual, ours, theirs)

### During Resolution

- [ ] Keep both changes if both are needed
- [ ] Test the resolution works correctly
- [ ] Remove all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- [ ] Format code properly
- [ ] Verify logic is sound

### After Resolution

- [ ] Run tests to ensure nothing broke
- [ ] Review the diff of your resolution
- [ ] Commit with clear message explaining resolution
- [ ] Push and verify CI/CD passes

---

## Testing After Conflict Resolution

### Always Test

**Never assume conflict resolution is correct**. Test thoroughly:

```bash
# After resolving conflicts
git add .
git commit -m "merge: resolve conflicts with main"

# Run tests
npm test

# If tests fail, fix and amend
npm test
git add .
git commit --amend --no-edit
```

### Manual Testing

**For complex conflicts**:
1. Start application locally
2. Test affected features manually
3. Verify no regressions
4. Check edge cases

---

## Team Conflict Resolution Practices

### Pair on Complex Conflicts

**When conflicts are complex**:
```bash
# Screen share with team member who made conflicting changes
git merge feature/their-branch
# Resolve together in real-time
# Both understand the resolution
```

### Document Resolution Decisions

**In merge commit message**:
```bash
git commit -m "merge: resolve conflicts between auth refactor and OAuth feature

Conflicts in auth/service.ts resolved by:
- Keeping OAuth2 flow from feature branch
- Integrating with refactored token handling from main
- Combined validation logic from both branches

Tested manually: login, OAuth, token refresh all working"
```

### Code Review After Resolution

**For critical conflicts**:
```bash
# Don't merge directly
# Create PR with conflict resolution
git push origin feature/my-feature

# In PR description:
## Conflict Resolution
Resolved conflicts in:
- auth/service.ts: Combined OAuth and refactored logic
- api/routes.ts: Kept new routing structure, added OAuth routes

Reviewers: Please verify auth flow works correctly
```

---

## Common Mistakes

### Mistake 1: Accepting All "Ours" or "Theirs"

**Problem**: Blindly accepting one version without reviewing.

**Fix**: Always read both versions and understand the changes.

```bash
# Bad
git checkout --ours .
git add .

# Good
# Review each file individually
git diff --name-only --diff-filter=U  # List conflicted files
# Resolve each thoughtfully
```

### Mistake 2: Leaving Conflict Markers

**Problem**: Forgetting to remove `<<<<<<<`, `=======`, `>>>>>>>` markers.

**Fix**: Search for markers before committing.

```bash
# Check for conflict markers
git diff --check

# Or grep
grep -r "<<<<<<< HEAD" .
grep -r "=======" .
grep -r ">>>>>>>" .

# Verify none exist before committing
```

### Mistake 3: Not Testing After Resolution

**Problem**: Assuming resolution is correct without testing.

**Fix**: Always run tests.

```bash
# After conflict resolution
git add .
git commit

# MUST RUN TESTS
npm test

# If failing, fix immediately
```

### Mistake 4: Force Pushing After Rebase Without Care

**Problem**: Force pushing destroys others' work.

**Fix**: Use `--force-with-lease` and communicate.

```bash
# Bad
git push --force

# Good
git push --force-with-lease origin feature/my-branch

# Even better: notify team first
# "Rebasing my feature branch, please don't push to it for 5 minutes"
```

---

## Tools and Workflows

### Git Config for Better Conflict Display

```bash
# Show more context around conflicts
git config --global merge.conflictstyle diff3

# Now conflicts show:
<<<<<<< HEAD
your changes
||||||| merged common ancestors
original code
=======
their changes
>>>>>>> feature-branch
```

### Git Rerere (Reuse Recorded Resolution)

**Automatically resolve recurring conflicts**:

```bash
# Enable rerere
git config --global rerere.enabled true

# Now git remembers how you resolved conflicts
# and auto-applies same resolution if conflict recurs
```

**When useful**:
- Rebasing frequently
- Recurring conflicts in long-lived branches

### Visualize Conflicts with Git Log

```bash
# See where branches diverged
git log --oneline --graph --all

# Find merge base
git merge-base HEAD feature-branch

# See commits causing conflicts
git log HEAD..feature-branch
git log feature-branch..HEAD
```

---

## Recovery from Mistakes

### Undo Merge

**If merge went wrong**:
```bash
# Immediately after merge (before other commits)
git reset --hard HEAD~1

# Or use reflog if commits made after
git reflog
git reset --hard HEAD@{2}  # Go back to before merge
```

### Undo Rebase

**If rebase went wrong**:
```bash
# Abort during rebase
git rebase --abort

# After rebase completed
git reflog
git reset --hard HEAD@{5}  # Go back to before rebase
```

### Recover Lost Work

**If you lost changes during conflict resolution**:
```bash
# View reflog
git reflog

# Find commit before mistake
git reflog show HEAD@{10}

# Restore
git checkout HEAD@{10} -- path/to/file
```

---

## Quick Reference

### Conflict Resolution Commands

```bash
# Start merge/rebase
git merge branch-name
git rebase branch-name

# View conflicted files
git status
git diff --name-only --diff-filter=U

# Choose resolution strategy
git checkout --ours path/to/file
git checkout --theirs path/to/file

# Manual resolution
vim path/to/file
# Edit, remove markers, save
git add path/to/file

# Continue
git commit  # For merge
git rebase --continue  # For rebase

# Abort
git merge --abort
git rebase --abort

# Use merge tool
git mergetool
```

### Conflict Markers

```
<<<<<<< HEAD           # Your changes start
your code
||||||| merged base    # Original code (if diff3 enabled)
original code
=======                # Divider
their code
>>>>>>> branch-name    # Their changes end
```

### Testing After Resolution

```bash
# Verify no markers left
git diff --check

# Run tests
npm test

# View your resolution
git diff HEAD~1

# Amend if needed
git add .
git commit --amend
```
