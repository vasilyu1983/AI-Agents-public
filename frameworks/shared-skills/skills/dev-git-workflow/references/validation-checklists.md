# Git Workflow Validation Checklists

Comprehensive checklists for PR creation, merging, and release management to ensure quality and consistency.

## Contents

- Before Creating PR
- Before Merging PR
- Before Releasing
- Post-Deployment Checklist
- Hotfix Checklist
- Code Review Checklist (for Reviewers)
- Merge Strategy Checklist
- Stacked Diffs Checklist
- Rebase Checklist
- Release Branch Checklist (GitFlow)
- Related Resources

---

## Before Creating PR

### Code Quality

- [ ] Branch is up-to-date with base branch
- [ ] All tests pass locally (unit, integration, e2e)
- [ ] No linter errors or warnings
- [ ] Code follows project style guide
- [ ] No console.log or debugging statements
- [ ] No commented-out code blocks

### Commit Hygiene

- [ ] Commits follow conventional commit format
- [ ] Each commit has a clear, descriptive message
- [ ] WIP commits squashed into logical commits
- [ ] Commit history is clean and linear

### PR Scope

- [ ] PR size < 400 lines (or split into stacked diffs)
- [ ] PR addresses single concern (feature/fix/refactor)
- [ ] Self-reviewed changes before submitting
- [ ] No unrelated changes included

### Testing

- [ ] Added tests for new functionality
- [ ] Updated tests for changed functionality
- [ ] Test coverage meets project threshold (e.g., 80%)
- [ ] Edge cases covered in tests
- [ ] Integration tests added (if applicable)

### Documentation

- [ ] Code comments added for complex logic
- [ ] API documentation updated (if applicable)
- [ ] README updated (if applicable)
- [ ] Migration guide added (if breaking changes)

---

## Before Merging PR

### Review Process

- [ ] Required approvals obtained (1-2+ reviewers)
- [ ] All review comments addressed or discussed
- [ ] No unresolved conversations
- [ ] Reviewer feedback incorporated or explained

### CI/CD Checks

- [ ] All automated tests pass
- [ ] Code coverage meets threshold
- [ ] No linter errors
- [ ] Security scan clean (no vulnerabilities)
- [ ] No secrets detected in code
- [ ] Performance benchmarks pass (if applicable)

### Merge Readiness

- [ ] No merge conflicts with base branch
- [ ] Branch is up-to-date with latest base
- [ ] Breaking changes documented in PR description
- [ ] Deployment plan documented (if needed)
- [ ] Feature flags configured (if partial rollout)

### Final Checks

- [ ] PR title follows conventional commit format
- [ ] PR description complete (What, Why, How, Testing)
- [ ] Related issues linked (Fixes #123, Relates to #456)
- [ ] Screenshots/videos added (if UI changes)
- [ ] Database migrations tested (if applicable)

---

## Before Releasing

### Pre-Release Testing

- [ ] All features tested in staging environment
- [ ] Integration tests pass in staging
- [ ] Load testing completed (if applicable)
- [ ] Security scan clean
- [ ] Cross-browser testing (for web apps)
- [ ] Mobile testing (iOS/Android if applicable)

### Version Management

- [ ] Version number follows SemVer (MAJOR.MINOR.PATCH)
- [ ] Version bumped correctly:
  - MAJOR for breaking changes
  - MINOR for new features
  - PATCH for bug fixes
- [ ] Pre-release version if needed (alpha, beta, rc)

### Documentation

- [ ] CHANGELOG.md updated with all changes
- [ ] Release notes drafted
- [ ] API documentation updated
- [ ] User-facing documentation updated
- [ ] Migration guide prepared (if breaking changes)

### Database & Infrastructure

- [ ] Database migration scripts tested
- [ ] Rollback migration scripts prepared
- [ ] Infrastructure changes deployed to staging
- [ ] Environment variables updated
- [ ] Feature flags configured

### Deployment Planning

- [ ] Rollback plan documented
- [ ] Deployment schedule communicated
- [ ] Downtime window scheduled (if needed)
- [ ] On-call engineer assigned
- [ ] Monitoring dashboards prepared

### Stakeholder Communication

- [ ] Release notes shared with team
- [ ] Customer-facing changelog prepared
- [ ] Support team briefed on changes
- [ ] Marketing notified (if user-facing features)
- [ ] Stakeholders informed of deployment schedule

---

## Post-Deployment Checklist

### Immediate Verification (First 15 minutes)

- [ ] Deployment successful (no errors in logs)
- [ ] Smoke tests pass
- [ ] Critical user flows work
- [ ] Database migrations applied successfully
- [ ] No spike in error rates
- [ ] Application responds normally

### Short-Term Monitoring (First Hour)

- [ ] Error rates within normal range
- [ ] Response times acceptable
- [ ] CPU and memory usage normal
- [ ] Database query performance stable
- [ ] No unusual user reports
- [ ] Feature flags working as expected

### Post-Release Tasks

- [ ] Monitor error logs for 24 hours
- [ ] Update documentation site
- [ ] Close related issues and PRs
- [ ] Merge release branch back to develop (GitFlow)
- [ ] Send release announcement
- [ ] Plan next release cycle

---

## Hotfix Checklist

### Critical Bug Verification

- [ ] Bug confirmed in production
- [ ] Severity assessed (critical/high/medium)
- [ ] Impact scope determined (users affected, data at risk)
- [ ] Root cause identified

### Hotfix Preparation

- [ ] Hotfix branch created from main/production
- [ ] Minimal fix implemented (no feature additions)
- [ ] Fix tested locally
- [ ] Regression tests pass
- [ ] Patch version bumped

### Fast-Track Review

- [ ] Emergency reviewer assigned
- [ ] Code review completed (even if abbreviated)
- [ ] Tests added for bug fix
- [ ] No additional changes included
- [ ] Rollback plan prepared

### Deployment

- [ ] Deployed to staging first (if time allows)
- [ ] Smoke tests pass in staging
- [ ] Production backup taken
- [ ] Hotfix deployed to production
- [ ] Verification tests pass

### Post-Hotfix

- [ ] Monitor for 1 hour minimum
- [ ] Verify bug is resolved
- [ ] No new errors introduced
- [ ] Hotfix merged back to develop/main
- [ ] Incident report created
- [ ] Team notified of resolution

---

## Code Review Checklist (for Reviewers)

### Functionality

- [ ] Code does what PR description claims
- [ ] Edge cases handled properly
- [ ] Error handling is appropriate
- [ ] No obvious bugs or logic errors

### Security

- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] No authentication/authorization bypass
- [ ] Secrets not hardcoded
- [ ] Input validation present
- [ ] Output sanitization present

### Performance

- [ ] No N+1 query problems
- [ ] Database indexes appropriate
- [ ] No unnecessary computations in loops
- [ ] Caching used where appropriate
- [ ] No memory leaks

### Code Quality

- [ ] Code is readable and maintainable
- [ ] Functions are focused and small
- [ ] Variable/function names are clear
- [ ] No code duplication
- [ ] Complexity is reasonable (cyclomatic < 10)

### Testing

- [ ] Tests cover new functionality
- [ ] Tests cover edge cases
- [ ] Tests are maintainable
- [ ] Test names are descriptive
- [ ] No flaky tests introduced

### Documentation

- [ ] Complex logic has comments
- [ ] API changes documented
- [ ] Breaking changes clearly marked
- [ ] Migration steps documented (if needed)

---

## Merge Strategy Checklist

### Choose Merge Strategy

**Squash and Merge** - When:
- [ ] Feature branch with many WIP commits
- [ ] Want single commit in history
- [ ] PR is self-contained feature

**Rebase and Merge** - When:
- [ ] Commits are already clean and logical
- [ ] Want to preserve individual commits
- [ ] Linear history preferred

**Merge Commit** - When:
- [ ] Want to preserve branch context
- [ ] Multiple developers collaborated
- [ ] Shared feature branch

### Before Merging

- [ ] Chosen merge strategy aligns with team policy
- [ ] Commit message follows conventions (if squashing)
- [ ] Branch is up-to-date with base
- [ ] All checks pass

---

## Stacked Diffs Checklist

### Planning Stack

- [ ] Feature broken into logical increments
- [ ] Each stack is independently reviewable
- [ ] Each stack is < 400 lines
- [ ] Clear dependency order established
- [ ] Stack naming convention followed

### Creating Stack

- [ ] Base branch created from main
- [ ] Each stack builds on previous
- [ ] PR descriptions explain stack position
- [ ] Dependency chain documented

### Reviewing Stack

- [ ] Review bottom-up (base first)
- [ ] Each stack approved before next
- [ ] Maintain stack integrity during updates
- [ ] Rebase chain when needed

### Merging Stack

- [ ] Merge bottom-up (base first)
- [ ] Update subsequent PRs after each merge
- [ ] Verify tests pass after each merge
- [ ] Monitor for cascading issues

---

## Rebase Checklist

### Before Rebasing

- [ ] Understand what rebase does (rewrites history)
- [ ] Confirm branch is not shared with others
- [ ] Backup branch if unsure (`git branch backup`)
- [ ] Fetch latest changes from base

### During Rebase

- [ ] Resolve conflicts carefully
- [ ] Verify each commit after conflict resolution
- [ ] Test after rebase completes
- [ ] Ensure commit messages still make sense

### After Rebase

- [ ] All tests pass
- [ ] Force push safely (`--force-with-lease`)
- [ ] Verify history looks correct (`git log`)
- [ ] Update PR if needed

### Never Rebase If

- [ ] Commits already on main/master
- [ ] Branch is shared with teammates
- [ ] You're not confident in the process
- [ ] Protected branch (use merge instead)

---

## Release Branch Checklist (GitFlow)

### Creating Release Branch

- [ ] Branch from develop (not main)
- [ ] Name follows convention (release/vX.Y.Z)
- [ ] Version number determined (SemVer)
- [ ] CHANGELOG.md drafted

### Release Branch Activities

- [ ] Version bumped in all package files
- [ ] CHANGELOG.md finalized
- [ ] Documentation updated
- [ ] Release notes drafted
- [ ] No new features added (bug fixes only)

### Testing Release

- [ ] Deployed to staging
- [ ] Full regression testing
- [ ] Performance testing
- [ ] Security scan
- [ ] Manual QA sign-off

### Merging Release

- [ ] Merge to main with `--no-ff`
- [ ] Tag with version number
- [ ] Merge back to develop with `--no-ff`
- [ ] Delete release branch
- [ ] Deploy to production

---

## Related Resources

- [PR Best Practices Guide](pr-best-practices.md) - Detailed PR review guidelines
- [Branching Strategies Comparison](branching-strategies.md) - Workflow selection
- [Release Management](release-management.md) - Versioning and deployment
- [Automated Quality Gates](automated-quality-gates.md) - CI/CD checks
