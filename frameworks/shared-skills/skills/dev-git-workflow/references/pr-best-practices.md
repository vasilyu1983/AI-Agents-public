# Pull Request Best Practices

Comprehensive guide to creating, reviewing, and merging pull requests for high-performing teams.

## Contents

- PR Size Impact (Data-Driven)
- PR Lifecycle Best Practices
- Code Review Best Practices
- Addressing Review Comments
- Merge Strategies
- Advanced PR Patterns
- Status

---

## PR Size Impact (Data-Driven)

### Research Findings

**Study: Small PRs Lead to Faster Development**

| PR Size (LOC) | Avg Review Time | Merge Rate | Bug Escape Rate |
|---------------|----------------|------------|-----------------|
| < 50 | 8 minutes | 95% same day | 2% |
| 50-200 | 25 minutes | 85% same day | 3% |
| 200-400 | 45 minutes | 70% same day | 5% |
| 400-1000 | 2 hours | 50% same day | 12% |
| > 1000 | 4+ hours | 20% same day | 25% |

**Key Insight**: PRs in the 200-400 LOC range achieve 1.5x velocity improvement

**Source**: Redox Engineering Team Study

---

## PR Lifecycle Best Practices

### 1. Before Creating PR

**Code Quality Checklist**:
- [ ] All tests pass locally (`npm test`, `pytest`, etc.)
- [ ] No console.log, debugger, or print statements
- [ ] Code formatted (`prettier`, `black`, `gofmt`)
- [ ] No linter errors (`eslint`, `pylint`, `golangci-lint`)
- [ ] Self-reviewed changes in diff view
- [ ] Checked for secrets or API keys
- [ ] Added tests for new functionality
- [ ] Updated documentation if needed

**Quick Self-Review**:
```bash
# Review your own changes first
git diff main...HEAD

# Check for common issues
git diff main...HEAD | grep -i "TODO\|FIXME\|console\.log\|debugger"

# Verify test coverage
npm test -- --coverage
# Or: pytest --cov=src
```

### 2. Writing PR Description

**High-Quality Template**:

```markdown
## Summary
[1-2 sentence description of what changed and why]

## Motivation
[Business or technical reason for this change]
Why is this change needed? What problem does it solve?

## Changes
[Detailed list of what changed]
- Added X feature
- Refactored Y module
- Fixed Z bug

## Implementation Details
[Technical approach and key decisions]
- Chose approach A over B because [reason]
- Used library X for [specific need]
- Considered edge cases: [list]

## Testing
[How you verified this works]
- [ ] Unit tests added (coverage: X%)
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Tested on Chrome, Firefox, Safari
- [ ] Tested edge cases: [list]

## Screenshots/Videos
[For UI changes]
Before:
[image or video]

After:
[image or video]

## Performance Impact
[If applicable]
- Benchmark results: [data]
- Load time: before X ms -> after Y ms
- Database queries: optimized from N to M

## Security Considerations
[If applicable]
- Input validation added for [fields]
- Authorization check for [resource]
- No secrets in code (verified)

## Deployment Notes
[Important information for deployment]
- Database migration required: `npm run migrate`
- Feature flag: `ENABLE_NEW_SEARCH` (default: false)
- Environment variable: `API_TIMEOUT=5000`
- Backward compatible: Yes/No

## Rollback Plan
[If needed]
- Disable feature flag `ENABLE_NEW_SEARCH`
- Or: Revert commit abc123

## Related Issues
Fixes #234
Relates to #456
Part of epic #789

## Questions for Reviewers
[Specific areas where you want feedback]
- Is the error handling approach appropriate?
- Should we add more test coverage for X?
- Any performance concerns with this implementation?
```

**Bad Example**:
```markdown
# Title: fix stuff

Changed some files
```

**Good Example**:
```markdown
# Title: feat(auth): implement OAuth2 social login

## Summary
Add Google and GitHub OAuth2 authentication as alternative login methods,
reducing registration friction and improving conversion rates.

## Motivation
User research shows 45% of users abandon registration due to password
requirements. OAuth2 social login reduces registration time from 3 minutes
to 30 seconds.

Target metric: Increase registration completion rate from 55% to 75%.

## Changes
- Added OAuth2 providers (Google, GitHub) using passport.js
- Implemented account linking for existing email addresses
- Added profile sync (name, email, avatar)
- Updated login UI with social login buttons

## Implementation Details
Chose passport.js over next-auth because:
- Better TypeScript support
- More flexible middleware configuration
- Easier to customize OAuth flow

Edge cases handled:
- User registers with email, then logs in with OAuth (same email)
  -> Links accounts automatically
- User has Google AND GitHub with same email
  -> Allows both, shows linked accounts in profile
- OAuth fails or user cancels
  -> Graceful fallback to password login

## Testing
- [x] Unit tests: auth service, OAuth callback handlers (coverage: 92%)
- [x] Integration tests: full OAuth flow with mock providers
- [x] Manual testing: Verified on staging with real Google/GitHub OAuth
- [x] Edge cases: account linking, duplicate emails, OAuth failures

## Screenshots
Login page with social buttons:
[screenshot]

Account linking confirmation:
[screenshot]

## Security Considerations
- OAuth tokens stored encrypted in database
- CSRF protection enabled for OAuth callbacks
- State parameter validated to prevent CSRF
- No user data logged (GDPR compliant)
- Tested for OWASP Top 10 vulnerabilities

## Deployment Notes
Database migration required:
```bash
npm run migrate:oauth
```

New environment variables needed:
```env
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
OAUTH_CALLBACK_URL=https://app.com/auth/callback
```

Feature flag: `ENABLE_OAUTH` (default: false)
Enable after successful staging testing

## Rollback Plan
1. Disable feature flag: `ENABLE_OAUTH=false`
2. Or revert migration: `npm run migrate:rollback oauth`

## Related Issues
Fixes #234 (Add social login)
Relates to #456 (Improve registration flow)
Part of epic #789 (Authentication improvements)

## Questions for Reviewers
1. Should we add rate limiting for OAuth endpoints?
2. Is the account linking UX clear enough?
3. Any concerns with storing OAuth tokens encrypted vs hashed?
```

---

## Code Review Best Practices

### 3. Reviewing PRs

**Reviewer Responsibilities**:
- [ ] Review within 2-4 hours of request (ideal)
- [ ] Test changes locally for complex PRs
- [ ] Check for security vulnerabilities
- [ ] Verify test coverage
- [ ] Provide constructive feedback
- [ ] Approve when satisfied or request changes

**Review Timeline**:

| Priority | Target Review Time |
|----------|-------------------|
| Hotfix | < 1 hour |
| Bug fix | < 2 hours |
| Feature | < 4 hours |
| Refactoring | < 1 day |
| Documentation | < 1 day |

**Review Checklist**:

**Correctness**:
- [ ] Logic is correct and handles edge cases
- [ ] No obvious bugs or errors
- [ ] Meets requirements from ticket/issue
- [ ] Error handling is appropriate

**Security**:
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Input validation for user data
- [ ] Authorization checks present
- [ ] No secrets in code

**Performance**:
- [ ] No N+1 query problems
- [ ] Database queries optimized
- [ ] No unnecessary API calls
- [ ] Efficient algorithms used

**Maintainability**:
- [ ] Code is readable and clear
- [ ] Follows project conventions
- [ ] No code duplication
- [ ] Functions/methods are focused
- [ ] Comments explain "why", not "what"

**Testing**:
- [ ] Tests cover new functionality
- [ ] Tests cover edge cases
- [ ] Tests are readable and maintainable
- [ ] No flaky tests

**Documentation**:
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] README updated if needed

### Comment Categories (Modern Practice)

**BLOCKER (Must Fix)**:
- Security vulnerabilities
- Breaking changes
- Data loss risks
- Major bugs
- Performance regressions

**WARNING (Should Fix)**:
- Minor bugs
- Code quality issues
- Missing tests
- Unclear naming
- Incomplete error handling

**NITPICK (Nice to Have)**:
- Code style preferences
- Minor refactoring suggestions
- Formatting preferences

**QUESTION**:
- Asking for clarification
- Understanding reasoning
- Discussing alternatives

**PRAISE**:
- Acknowledging good solutions
- Highlighting clever approaches
- Encouraging improvements

### Writing Effective Review Comments

**Bad Comment**:
```
This is wrong.
```

**Good Comment**:
```
BLOCKER: SQL injection vulnerability

The user input is directly interpolated into the SQL query on line 42:
`SELECT * FROM users WHERE id = '${req.params.id}'`

This allows attackers to inject malicious SQL.

Fix by using parameterized queries:
```javascript
const result = await db.query(
  'SELECT * FROM users WHERE id = ?',
  [req.params.id]
);
```

Reference: https://owasp.org/www-community/attacks/SQL_Injection
```

**Bad Comment**:
```
Why did you do it this way?
```

**Good Comment**:
```
QUESTION: Alternative approach?

I see you're using a nested loop here. Have you considered using a hash map
for O(n) instead of O(n²) complexity?

```javascript
const userMap = users.reduce((acc, user) => {
  acc[user.id] = user;
  return acc;
}, {});

orders.forEach(order => {
  order.user = userMap[order.userId];
});
```

This would improve performance for large datasets.
```

**Bad Comment**:
```
This could be better.
```

**Good Comment**:
```
NITPICK: Consider extracting to utility function

This validation logic appears in 3 places (auth.ts:45, user.ts:23, profile.ts:67).
Consider extracting to a reusable utility:

```typescript
// utils/validation.ts
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

Not blocking, but would improve maintainability.
```

### Review Etiquette

**DO**:
- Be respectful and constructive
- Focus on the code, not the person
- Provide specific examples
- Offer to pair on complex issues
- Use "we" instead of "you"
- Acknowledge good work

**Example**:
```
PRAISE: Excellent error handling!

I love how you handled all the edge cases here. The error messages
are clear and actionable. This will make debugging much easier.
```

**DON'T**:
- Be vague or dismissive
- Make personal attacks
- Ignore the PR for days
- Nitpick excessively
- Demand perfection
- Bikeshed on minor style issues

**Bad**:
```
This is terrible. Rewrite it.
```

**Good**:
```
WARNING: Refactoring suggestion

This function is doing multiple things (validation, transformation, API call).
We could improve testability by splitting it into smaller functions:

1. `validateUserInput(data)` - validation logic
2. `transformUserData(data)` - transformation logic
3. `createUser(data)` - API call

This would make each function easier to test and reason about.
What do you think?
```

---

## Addressing Review Comments

### 4. Responding to Feedback

**Author Responsibilities**:
- [ ] Read all comments carefully
- [ ] Address each comment (fix or respond)
- [ ] Ask questions if unclear
- [ ] Push changes in new commits (don't force push mid-review)
- [ ] Re-request review after changes
- [ ] Resolve conversations when addressed

**How to Respond**:

**If Agreeing with Feedback**:
```markdown
Reviewer: "Add error handling for network failures"

Author: "Good catch! Added try-catch in commit abc123.
Also added tests for network failure scenarios."
```

**If Disagreeing Respectfully**:
```markdown
Reviewer: "This should use library X instead of Y"

Author: "I considered library X, but chose Y because:
1. X doesn't support TypeScript (we need type safety)
2. Y has better performance for our use case (benchmark: Y is 3x faster)
3. Y is actively maintained (last update 2 weeks ago vs X at 2 years)

Happy to discuss if you have concerns about this approach!"
```

**If Needing Clarification**:
```markdown
Reviewer: "This needs refactoring"

Author: "Can you clarify what specific refactoring you'd like to see?
Are you concerned about:
- The function length?
- The nested conditionals?
- The variable naming?

Happy to refactor, just want to make sure I address your concern correctly."
```

**If Resolving Later**:
```markdown
Reviewer: "We should add caching here for better performance"

Author: "Agreed this would improve performance. To keep this PR focused
on the auth feature, I created #567 to track the caching improvement.

We can address it separately with proper benchmarking and cache
invalidation strategy.

Okay to defer to that issue?"
```

---

## Merge Strategies

### 5. Merging PR

**Merge Strategy Decision Matrix**:

| Scenario | Strategy | Result |
|----------|----------|--------|
| Small PR, clean commits | **Merge commit** | Preserves all commits + merge commit |
| Large PR, messy history | **Squash and merge** | Single commit with all changes |
| Feature branch with logical commits | **Rebase and merge** | Linear history, no merge commit |
| Hotfix | **Merge commit** | Quick, preserves urgency context |

**Merge Commit** (`--no-ff`):
```bash
git checkout main
git merge --no-ff feature/user-auth
# Creates merge commit, preserves feature branch history
```

**Pros**: Preserves context, shows feature grouping
**Cons**: More commits in history

**Squash and Merge**:
```bash
git checkout main
git merge --squash feature/user-auth
git commit -m "feat: implement user authentication

- Add JWT tokens
- Add OAuth providers
- Add account linking
- Add profile sync

Closes #234"
# All commits squashed into one
```

**Pros**: Clean history, one commit per feature
**Cons**: Loses individual commit context

**Rebase and Merge**:
```bash
git checkout feature/user-auth
git rebase main
git checkout main
git merge --ff-only feature/user-auth
# Linear history, no merge commit
```

**Pros**: Cleanest history, easy to bisect
**Cons**: Rewrites history (don't use on public branches)

### When to Use Each Strategy

**Use Merge Commit When**:
- Feature has logical commit progression
- Multiple developers worked on feature
- Want to preserve feature context
- Hotfix (need to track urgency)

**Use Squash and Merge When**:
- PR has many "WIP" or fixup commits
- Want one commit per feature
- Commits are not meaningful individually
- Enforcing linear history

**Use Rebase and Merge When**:
- Commits are clean and logical
- Want cleanest possible history
- Team understands rebase workflow
- Automated by CI/CD (e.g., trunk-based)

---

## Advanced PR Patterns

### Draft PRs for Early Feedback

```markdown
Title: [WIP] User Dashboard

## Status
[WIP] Work in Progress - Not ready for merge

## Progress
- [x] Layout component
- [x] Metrics cards
- [ ] Activity feed (in progress)
- [ ] Responsive design
- [ ] E2E tests

## Early Feedback Needed
1. Does the metrics layout look good? (see screenshot)
2. Should we use real-time or daily aggregates?
3. Any performance concerns with current approach?

## Next Steps
- Complete activity feed
- Add responsive breakpoints
- Write E2E tests
- Update documentation
```

**Benefits**:
- Get early feedback on approach
- Avoid wasted effort on wrong direction
- Build team awareness of ongoing work

### Stacked PRs for Large Features

**Problem**: Feature requires 2000 lines of code

**Solution**: Break into dependent PRs

```
PR #1: feat: add user dashboard data models (200 LOC)
  └─ PR #2: feat: add dashboard API endpoints (300 LOC)
      └─ PR #3: feat: add dashboard UI components (400 LOC)
          └─ PR #4: feat: integrate dashboard with API (250 LOC)
```

Each PR:
- Reviewed independently
- Merged when approved
- Next PR rebases on previous

**Benefits**:
- Faster reviews (smaller PRs)
- Better code quality (focused reviews)
- Easier to revert if needed

### Co-Authored PRs

When multiple developers work on same PR:

```bash
# In commit message
git commit -m "feat: implement user dashboard

Co-authored-by: Jane Doe <jane@example.com>
Co-authored-by: John Smith <john@example.com>"
```

Shows proper attribution in GitHub/GitLab.

---

## CI/CD Integration

### Automated PR Checks

**Minimum Quality Gates**:
- [ ] All tests pass
- [ ] Code coverage ≥ threshold (80%)
- [ ] No linter errors
- [ ] No security vulnerabilities
- [ ] Build succeeds

**Advanced Quality Gates**:
- [ ] Performance benchmarks pass
- [ ] Bundle size < threshold
- [ ] Accessibility tests pass
- [ ] Visual regression tests pass
- [ ] API compatibility check

**Example GitHub Actions**:

```yaml
name: PR Quality Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Check coverage
        run: |
          COVERAGE=$(npm test -- --coverage --silent | grep -oP '\d+(?=%)')
          if [ "$COVERAGE" -lt 80 ]; then
            echo "::error::Coverage $COVERAGE% is below 80% threshold"
            exit 1
          fi

      - name: Lint code
        run: npm run lint

      - name: Build project
        run: npm run build

      - name: Security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check bundle size
        uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Metrics and Measurement

### PR Metrics to Track

**Velocity Metrics**:
- Time to first review
- Time to merge
- Review cycles (how many rounds)
- Merge rate (% PRs merged vs closed)

**Quality Metrics**:
- Bug escape rate (bugs found after merge)
- Revert rate (% PRs reverted)
- Test coverage trend
- Review comment density

**Team Health Metrics**:
- PRs per developer per week
- Review participation (% of team reviewing)
- Average PR size
- Idle time (PR open but no activity)

### Healthy Benchmarks

| Metric | Healthy Range |
|--------|---------------|
| **Time to first review** | < 4 hours |
| **Time to merge** | < 24 hours (small), < 3 days (large) |
| **Review cycles** | 1-2 rounds |
| **Merge rate** | > 85% |
| **Average PR size** | 200-400 LOC |
| **Bug escape rate** | < 5% |
| **Revert rate** | < 2% |

---

## Common Pitfalls and Solutions

### Pitfall 1: Review Bottlenecks

**Problem**: PRs wait days for review

**Solutions**:
- Rotate review duties
- Set SLA for review time (e.g., 4 hours)
- Auto-assign reviewers
- Gamify reviews (leaderboard)
- Pair programming (review happens live)

### Pitfall 2: Bike-shedding

**Problem**: Endless debates on minor style issues

**Solutions**:
- Use automated formatters (Prettier, Black)
- Enforce style in CI/CD, not reviews
- Save nitpicks for separate "quality improvement" PRs
- Use "NITPICK" tag to signal non-blocking comments

### Pitfall 3: Large, Unfocused PRs

**Problem**: 2000 line PRs mixing features, refactoring, and bug fixes

**Solutions**:
- Enforce PR size limits (warning at 400 LOC, block at 1000 LOC)
- Use stacked diffs for large features
- Separate refactoring PRs from feature PRs
- Split PRs mid-review if too large

### Pitfall 4: Rubber-Stamp Reviews

**Problem**: Reviewers approve without actually reviewing

**Solutions**:
- Require 2+ approvals for critical code
- Track review quality metrics
- Rotate reviewers to avoid familiarity bias
- Spot-check reviews in team retrospectives

---

## PR Templates by Project Type

### Backend API PR Template

```markdown
## API Changes
- [ ] New endpoints added
- [ ] Existing endpoints modified
- [ ] Endpoints deprecated/removed

## Database Changes
- [ ] Migration file included
- [ ] Rollback tested
- [ ] Indexes added for new queries
- [ ] No breaking schema changes

## Testing
- [ ] Unit tests (service layer)
- [ ] Integration tests (API layer)
- [ ] Database migration tested
- [ ] Postman collection updated

## Performance
- [ ] Query performance checked (EXPLAIN ANALYZE)
- [ ] Response time < 500ms
- [ ] No N+1 queries

## Security
- [ ] Input validation
- [ ] Authorization checks
- [ ] No SQL injection
- [ ] Rate limiting considered
```

### Frontend PR Template

```markdown
## UI Changes
- [ ] Screenshots included
- [ ] Responsive design tested
- [ ] Dark mode support
- [ ] Cross-browser tested (Chrome, Firefox, Safari)

## Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader tested
- [ ] ARIA labels added
- [ ] Color contrast checked

## Performance
- [ ] Lighthouse score > 90
- [ ] Bundle size impact checked
- [ ] Images optimized
- [ ] Lazy loading for heavy components

## Testing
- [ ] Component tests
- [ ] Integration tests
- [ ] E2E tests for critical flows
- [ ] Manual QA completed
```

### Infrastructure PR Template

```markdown
## Infrastructure Changes
- [ ] Terraform/CloudFormation changes validated
- [ ] No secrets in code
- [ ] Cost impact estimated
- [ ] Rollback plan documented

## Security
- [ ] IAM permissions reviewed
- [ ] Security groups configured
- [ ] Encryption enabled
- [ ] Backup strategy defined

## Testing
- [ ] Tested in dev environment
- [ ] Tested in staging environment
- [ ] Monitoring/alerting configured
- [ ] Runbook updated

## Deployment
- [ ] Deployment order documented
- [ ] Downtime estimated
- [ ] Rollback procedure tested
- [ ] Stakeholders notified
```
