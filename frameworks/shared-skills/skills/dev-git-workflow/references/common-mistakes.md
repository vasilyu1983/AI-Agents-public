# Common Git Workflow Mistakes & Fixes

Learn from common pitfalls and antipatterns in Git collaboration workflows.

## Contents

- Mistake 1: Large, Unfocused PRs
- Mistake 2: Vague Commit Messages
- Mistake 3: Rewriting Public History
- Mistake 4: Ignoring Review Comments
- Mistake 5: Not Pulling Before Starting Work
- Mistake 6: Committing Secrets
- Mistake 7: Mixing Refactoring with Features
- Mistake 8: Not Testing Before Pushing
- Mistake 9: Unclear PR Descriptions
- Mistake 10: Force Push Without `--force-with-lease`
- Summary: Quick Reference
- Related Resources

---

## Mistake 1: Large, Unfocused PRs

### Problem

**Symptom**: PR with 2000 lines mixing features, refactoring, and bug fixes

**Why it's bad**:
- Impossible to review thoroughly
- Takes days or weeks to get approved
- High risk of bugs slipping through
- Merge conflicts inevitable
- Can't revert specific changes easily

### Example

```bash
# BAD: Bad: Everything in one massive PR
git commit -m "Add authentication, refactor database, fix bugs, update docs"

# PR contains:
# - 1200 lines of new authentication code
# - 500 lines of database refactoring
# - 200 lines of bug fixes
# - 100 lines of documentation updates
```

### Fix: Split into Focused PRs

**Use stacked diffs**:

```bash
# GOOD: Good: Separate logical changes

# Stack 1: Database refactoring (foundation)
git checkout -b refactor/database-schema main
git commit -m "refactor(db): normalize user tables"
git push origin refactor/database-schema
# PR #1: 250 lines

# Stack 2: Authentication (builds on Stack 1)
git checkout -b feat/authentication refactor/database-schema
git commit -m "feat(auth): add JWT authentication"
git push origin feat/authentication
# PR #2: 300 lines

# Stack 3: Bug fixes
git checkout -b fix/security-patches main
git commit -m "fix: patch SQL injection vulnerabilities"
git push origin fix/security-patches
# PR #3: 150 lines

# Stack 4: Documentation
git checkout -b docs/auth-guide main
git commit -m "docs: add authentication setup guide"
git push origin docs/auth-guide
# PR #4: 100 lines
```

**Benefits**:
- Each PR reviewed in 30-60 minutes instead of 2-3 hours
- Reviewers can focus on one concern at a time
- Can merge incrementally
- Easy to revert specific changes

---

## Mistake 2: Vague Commit Messages

### Problem

**Symptom**: Commits like `git commit -m "fix stuff"`, `git commit -m "WIP"`, `git commit -m "update"`

**Why it's bad**:
- No context for future developers
- Can't generate meaningful changelogs
- Difficult to find specific changes
- No semantic versioning automation

### Examples

```bash
# BAD: Bad commit messages
git commit -m "fix bug"
git commit -m "WIP"
git commit -m "update code"
git commit -m "changes"
git commit -m "asdfasdf"
```

### Fix: Use Conventional Commits

```bash
# GOOD: Good: Descriptive conventional commits

git commit -m "fix(auth): prevent duplicate user creation on concurrent requests

Add database unique constraint on email field and implement
transaction handling to prevent race conditions during user
registration.

Fixes #234"

git commit -m "feat(api): add OAuth2 social login providers

Implement Google and GitHub OAuth2 authentication using
passport.js. Includes user profile sync and account linking.

Closes #567"

git commit -m "refactor(db): optimize user lookup queries

Replace N+1 query pattern with single JOIN query, reducing
database roundtrips by 90%. Add database index on email field.

Performance improvement: 250ms -> 25ms average response time"
```

**Conventional commit format**:
```
<type>(<scope>): <short description>

<longer description>

<footer>
```

**Types**: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `ci`, `build`

---

## Mistake 3: Rewriting Public History

### Problem

**Symptom**: Force pushing to shared branches or main

**Why it's bad**:
- Breaks everyone's local branches
- Can lose commits permanently
- Causes confusion and merge conflicts
- Violates team trust

### Example

```bash
# BAD: DANGEROUS: Rewriting shared history
git checkout main
git rebase feature-branch  # Rewrites main's history
git push --force origin main  # Overwrites remote

# Result: Everyone's main branch is now broken
# Team members get errors like:
# "Your branch and 'origin/main' have diverged"
```

### Fix: Never Rebase Public Branches

```bash
# GOOD: Good: Use merge for shared branches
git checkout main
git merge feature-branch  # Preserves history
git push origin main  # Safe, no --force needed

# GOOD: Good: Only rebase feature branches
git checkout feature-branch
git rebase main  # OK, feature-branch is not shared
git push --force-with-lease origin feature-branch  # Safer than --force
```

**Golden Rules**:
- [OK] Rebase your feature branches
- [OK] Merge into main/develop
- [FAIL] Never rebase main/develop/master
- [FAIL] Never rebase shared branches

---

## Mistake 4: Ignoring Review Comments

### Problem

**Symptom**: Merging PR without addressing reviewer feedback

**Why it's bad**:
- Bugs slip into production
- Technical debt accumulates
- Disrespects reviewers' time
- Erodes team trust

### Example

```markdown
# BAD: Bad: Ignoring feedback

Reviewer: "This needs error handling for null values"
Author: [Marks as resolved, doesn't add error handling]
Author: [Merges PR]

# Result: Production crashes with null pointer exception
```

### Fix: Address All Feedback

```markdown
# GOOD: Good: Engage with feedback

Reviewer: "This needs error handling for null values"
Author: "Added try-catch in commit abc123. Good catch! Here's the updated code:
```typescript
try {
  const user = await getUserById(id);
  return user.profile;
} catch (error) {
  logger.error('Failed to fetch user profile', { id, error });
  throw new NotFoundError(`User ${id} not found`);
}
```
"

# GOOD: Good: Discuss disagreements respectfully

Reviewer: "This should use dependency injection"
Author: "I considered that, but decided against it because:
1. This is a utility function with no external dependencies
2. Adding DI would complicate the interface for minimal benefit
3. Current implementation is easier to test with mocks

Happy to discuss further if you feel strongly. What do you think?"
```

**Best Practices**:
- [OK] Respond to every comment
- [OK] Explain decisions when disagreeing
- [OK] Ask questions if unclear
- [OK] Thank reviewers for feedback
- [FAIL] Don't merge until all conversations resolved

---

## Mistake 5: Not Pulling Before Starting Work

### Problem

**Symptom**: Creating feature branch from outdated main

**Why it's bad**:
- Work on old codebase version
- Merge conflicts guaranteed
- May reintroduce fixed bugs
- Wastes time resolving avoidable conflicts

### Example

```bash
# BAD: Bad: Working on stale branch
git checkout main  # Last pulled 3 days ago
git checkout -b feature/new-api  # Branch from outdated main
# ... work for 2 days ...
git push origin feature/new-api
# PR has 47 merge conflicts

# Teammate merged a database schema change yesterday
# Your code uses old schema, will break in production
```

### Fix: Always Pull First

```bash
# GOOD: Good: Start with latest code
git checkout main
git pull origin main  # Fetch latest changes
git checkout -b feature/new-api  # Branch from up-to-date main
# ... work ...

# GOOD: Good: Rebase frequently
git fetch origin main
git rebase origin/main  # Keep feature branch up-to-date
# Resolve small conflicts incrementally instead of 47 at once
```

**Best Practice**: Pull/fetch at least once per day

---

## Mistake 6: Committing Secrets

### Problem

**Symptom**: Hardcoded API keys, passwords, tokens in code

**Why it's bad**:
- Security breach (secrets exposed in Git history)
- Can't rotate credentials easily
- Violates compliance regulations
- Attackers scan GitHub for secrets

### Example

```javascript
// BAD: DANGEROUS: Secrets in code
const config = {
  apiKey: 'sk_live_ABC123XYZ789',  // Stripe production key
  dbPassword: 'SuperSecret123!',
  jwtSecret: 'my-secret-key'
};
```

### Fix: Use Environment Variables

```javascript
// GOOD: Good: Environment variables
const config = {
  apiKey: process.env.STRIPE_API_KEY,
  dbPassword: process.env.DATABASE_PASSWORD,
  jwtSecret: process.env.JWT_SECRET
};

// .env file (git-ignored)
STRIPE_API_KEY=sk_live_ABC123XYZ789
DATABASE_PASSWORD=SuperSecret123!
JWT_SECRET=my-secret-key

// .env.example file (committed)
STRIPE_API_KEY=your_stripe_api_key_here
DATABASE_PASSWORD=your_database_password_here
JWT_SECRET=your_jwt_secret_here
```

**If you already committed secrets**:

```bash
# 1. Rotate the compromised credentials immediately
# 2. Remove from Git history (dangerous, coordinate with team)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/secrets.json" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (only if absolutely necessary)
git push origin --force --all

# Better: Use BFG Repo-Cleaner
java -jar bfg.jar --delete-files secrets.json
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

---

## Mistake 7: Mixing Refactoring with Features

### Problem

**Symptom**: PR that adds feature AND refactors unrelated code

**Why it's bad**:
- Impossible to review properly
- Can't isolate bugs if issues arise
- Can't cherry-pick feature without refactoring
- Cluttered diff makes review harder

### Example

```bash
# BAD: Bad: Feature + refactoring in one PR
git commit -m "Add user notifications and refactor authentication"

# PR contains:
# - New notification system (feature)
# - Rewrite authentication from scratch (refactoring)
# - Update 15 unrelated files
# Reviewer: "I can't tell what's new feature vs refactoring"
```

### Fix: Separate Concerns

```bash
# GOOD: Good: Refactor first, then feature

# Step 1: Refactoring PR (no functionality changes)
git checkout -b refactor/auth-cleanup main
git commit -m "refactor(auth): extract auth logic to service

No functionality changes. Reorganize code for better testability."
git push origin refactor/auth-cleanup
# PR #1: Reviewable refactoring only

# Step 2: Feature PR (builds on refactoring)
git checkout -b feat/notifications refactor/auth-cleanup
git commit -m "feat(notifications): add real-time user notifications

Uses new auth service for user context."
git push origin feat/notifications
# PR #2: Reviewable feature only
```

---

## Mistake 8: Not Testing Before Pushing

### Problem

**Symptom**: Push code that breaks CI/CD

**Why it's bad**:
- Blocks other developers
- CI/CD queue backed up
- Wastes team time
- Looks unprofessional

### Example

```bash
# BAD: Bad: Push without testing
git add .
git commit -m "feat: add new feature"
git push origin feature-branch
# CI fails: 47 test failures, 12 lint errors

# Team is blocked because CI queue is full of your failing builds
```

### Fix: Test Locally First

```bash
# GOOD: Good: Test before pushing
git add .

# Run all checks locally
npm test  # All tests pass
npm run lint  # No errors
npm run build  # Builds successfully
npm run type-check  # TypeScript checks pass

# Only push after local verification
git commit -m "feat: add new feature"
git push origin feature-branch
# CI passes on first try
```

**Use pre-commit hooks**:

```bash
# Install husky + lint-staged
npm install --save-dev husky lint-staged
npx husky install

# Pre-commit hook runs tests automatically
# Prevents bad commits from being created
```

---

## Mistake 9: Unclear PR Descriptions

### Problem

**Symptom**: PR description says "Fixed bug" with no context

**Why it's bad**:
- Reviewers waste time investigating
- Can't understand impact of changes
- No record of why change was made
- Hard to track down regressions later

### Example

```markdown
# BAD: Bad PR description
Title: Fix bug

Description: Fixed the bug in the code.

# Reviewer: "What bug? Where? Why? How?"
```

### Fix: Complete PR Template

```markdown
# GOOD: Good PR description

Title: fix(auth): prevent duplicate user creation on concurrent requests

## What
Adds database constraint and transaction handling to prevent duplicate
user records when registration requests arrive concurrently.

## Why
We've seen 47 duplicate user records in production over the last week,
causing login failures and support tickets. Root cause: race condition
between checking if user exists and creating user record.

## How
1. Add unique constraint on email field in database
2. Wrap user creation in transaction
3. Handle unique constraint violation with proper error

Technical details:
- Uses PostgreSQL transaction isolation level READ COMMITTED
- Returns 409 Conflict if email already exists
- Maintains backward compatibility with existing API

## Testing
- Added integration test for concurrent requests
- Tested manually with 100 concurrent requests
- Zero duplicates created in 1000 test runs

## Deployment Notes
- Database migration required (backward compatible)
- No downtime needed
- Can rollback by reverting migration

## Related
Fixes #234
Relates to #456 (broader authentication improvements)
```

---

## Mistake 10: Force Push Without `--force-with-lease`

### Problem

**Symptom**: Using `git push --force` and overwriting teammate's work

**Why it's bad**:
- Can permanently delete others' commits
- No safety check for remote changes
- Causes data loss
- Breaks team collaboration

### Example

```bash
# BAD: DANGEROUS: Force push without safety
git push --force origin feature-branch

# If teammate pushed to feature-branch, their work is gone forever
# No warning, no recovery (unless they have local copy)
```

### Fix: Use `--force-with-lease`

```bash
# GOOD: Safer: Force push with safety check
git push --force-with-lease origin feature-branch

# If remote has changes you don't have locally:
# "error: failed to push some refs"
# "Updates were rejected because the remote contains work that you do not have"

# You can review remote changes first:
git fetch origin
git log origin/feature-branch
# Decide: merge or rebase?
```

**Even better**: Avoid force pushing shared branches entirely

---

## Summary: Quick Reference

| Mistake | Fix |
|---------|-----|
| Large PRs | Split into < 400 line focused PRs |
| Vague commits | Use conventional commits |
| Rewrite public history | Never rebase main/master |
| Ignore reviews | Address all feedback |
| Stale branch | Pull before starting work |
| Commit secrets | Use environment variables |
| Mix concerns | Separate refactoring from features |
| Skip testing | Test locally before pushing |
| Unclear PRs | Use complete PR template |
| Force push | Use `--force-with-lease` |

---

## Related Resources

- [PR Best Practices Guide](pr-best-practices.md) - Detailed PR guidelines
- [Commit Conventions](commit-conventions.md) - Conventional commit standards
- [Validation Checklists](validation-checklists.md) - Pre-merge checklists
- [Conflict Resolution](conflict-resolution.md) - Handling merge conflicts
