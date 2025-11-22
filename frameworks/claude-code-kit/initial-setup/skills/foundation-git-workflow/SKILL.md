---
name: foundation-git-workflow
description: Modern Git collaboration patterns for team development - branching strategies, PR workflows, commit conventions, and code review best practices
version: 2.0.0
tags: [git, collaboration, code-review, workflow, version-control]
---

# Git Collaboration Workflow — Modern Team Development

**Modern Best Practices**: GitHub Flow for continuous deployment, Trunk-Based for scale, conventional commits for automation, stacked diffs for large features

This skill provides modern Git collaboration patterns for high-performing engineering teams, covering branching strategies, pull request workflows, commit conventions, code review best practices, and release automation.

---

## When to Use This Skill

Invoke this skill when the user asks to:

- Design branching strategies for teams (GitHub Flow, Trunk-Based, GitFlow)
- Create pull request or merge request workflows
- Implement commit conventions (Conventional Commits, semantic versioning)
- Set up code review processes and quality gates
- Resolve merge conflicts or rebase issues
- Configure Git automation (GitHub Actions, GitLab CI PR checks)
- Implement stacked diffs workflows
- Design release management strategies
- Set up automated quality gates in CI/CD
- Create validation checklists for PRs and releases

---

## Quick Reference

| Task | Tool/Command | When to Use | Reference |
|------|-------------|-------------|-----------|
| Create feature branch | `git checkout -b feat/name main` | Start new work | [Branching Strategies](resources/branching-strategies.md) |
| Squash WIP commits | `git rebase -i HEAD~3` | Clean up before PR | [Interactive Rebase](resources/interactive-rebase-guide.md) |
| Conventional commit | `git commit -m "feat: add feature"` | All commits | [Commit Conventions](resources/commit-conventions.md) |
| Force push safely | `git push --force-with-lease` | After rebase | [Common Mistakes](resources/common-mistakes.md) |
| Resolve conflicts | `git mergetool` | Merge conflicts | [Conflict Resolution](resources/conflict-resolution.md) |
| Create stacked PRs | `gt create stack-name` (Graphite) | Large features | [Stacked Diffs](resources/stacked-diffs-guide.md) |
| Auto-generate changelog | `npx standard-version` | Before release | [Release Management](resources/release-management.md) |
| Run quality gates | GitHub Actions / GitLab CI | Every PR | [Automated Quality Gates](resources/automated-quality-gates.md) |

---

## Decision Tree: Choosing Branching Strategy

```text
Use this decision tree to select the optimal branching strategy for your team based on team size, release cadence, and CI/CD maturity.

Team characteristics → What's your situation?
    ├─ Small team (1-5 devs) + Continuous deployment + High CI/CD maturity?
    │   └─ GitHub Flow (main + feature branches)
    │
    ├─ Medium team (5-15 devs) + Continuous deployment + High CI/CD maturity?
    │   └─ Trunk-Based Development (main + short-lived branches)
    │
    ├─ Large team (15+ devs) + Continuous deployment + Very high CI/CD maturity?
    │   └─ Trunk-Based + Feature Flags (progressive rollout)
    │
    ├─ Scheduled releases + Medium CI/CD maturity?
    │   └─ GitFlow (main + develop + release branches)
    │
    └─ Multiple versions + Low-Medium CI/CD maturity?
        └─ GitFlow (long-lived release branches)
```

---

## Navigation: Core Workflows

### Branching Strategies

**[Branching Strategies Comparison](resources/branching-strategies.md)** - Comprehensive guide to choosing and implementing branching strategies

- GitHub Flow (recommended for modern teams): Simple, continuous deployment
- Trunk-Based Development (enterprise scale): Short-lived branches, daily merges
- GitFlow (structured releases): Scheduled releases, multiple versions
- Decision matrix: Team size, release cadence, CI/CD maturity
- Migration paths between strategies

### Pull Request Best Practices

**[PR Best Practices Guide](resources/pr-best-practices.md)** - Effective code reviews and fast PR cycles

- PR size guidelines: 200-400 lines optimal (46% faster merge)
- Review categories: BLOCKER, WARNING, NITPICK
- Review etiquette: Collaborative feedback, code examples
- PR description templates: What, Why, How, Testing
- Data-driven insights on review efficiency

### Commit Conventions

**[Conventional Commits Standard](resources/commit-conventions.md)** - Commit message formats and semantic versioning integration

- Conventional commit format: `type(scope): description`
- Commit types: feat, fix, BREAKING CHANGE, refactor, docs
- SemVer automation: Auto-bump versions from commits
- Changelog generation: Automated from commit history
- Tools: commitlint, semantic-release, standard-version

---

## Navigation: Advanced Techniques

### Stacked Diffs

**[Stacked Diffs Implementation](resources/stacked-diffs-guide.md)** - Platform-specific workflows and team adoption

- What are stacked diffs: Break large features into reviewable chunks
- When to use: Features > 500 lines, complex refactoring
- GitLab native support: MR chains
- GitHub with Graphite: CLI-based stacking
- Benefits: 60% faster review cycles, better quality

### Interactive Rebase

**[Interactive Rebase & History Cleanup](resources/interactive-rebase-guide.md)** - Maintain clean commit history

- Auto-squash workflow: `fixup!` and `squash!` commits
- Interactive rebase commands: pick, reword, edit, squash, fixup, drop
- Splitting commits: Break large commits into focused changes
- Reordering commits: Logical commit history
- Best practices: Never rebase public branches

### Conflict Resolution

**[Conflict Resolution Techniques](resources/conflict-resolution.md)** - Merge strategies and conflict handling

- Resolution strategies: `--ours`, `--theirs`, manual merge
- Rebase vs merge: When to use each
- Merge tool setup: VS Code, Meld, custom tools
- Conflict markers: Understanding `<<<<<<<`, `=======`, `>>>>>>>`
- Prevention strategies: Frequent rebasing, small PRs

---

## Navigation: Automation & Quality

### Automated Quality Gates

**[Automated Quality Gates](resources/automated-quality-gates.md)** - CI/CD pipelines and quality enforcement

- Essential gates: Tests, coverage, linting, security scans
- Advanced gates: Performance benchmarks, bundle size, a11y checks
- GitHub Actions workflows: Complete PR checks pipeline
- GitLab CI pipelines: MR quality gates
- Pre-commit hooks: Husky + lint-staged setup
- Quality metrics thresholds: Coverage 80%, complexity < 10

### Validation Checklists

**[Validation Checklists](resources/validation-checklists.md)** - Pre-PR, pre-merge, pre-release checklists

- Before creating PR: Code quality, commit hygiene, testing
- Before merging PR: Review process, CI/CD checks, final verification
- Before releasing: Pre-release testing, version management, documentation
- Post-deployment: Immediate verification, monitoring, tasks
- Hotfix checklist: Critical bug fast-track process

### Release Management

**[Release Management](resources/release-management.md)** - Versioning and deployment workflows

- Semantic versioning: MAJOR.MINOR.PATCH
- Manual release workflow: GitFlow release branches
- Automated releases: semantic-release automation
- Hotfix workflow: Emergency patches
- Changelog generation: Keep a Changelog format
- Release checklists: Pre-release, release day, post-release

---

## Navigation: Learning & Troubleshooting

### Common Mistakes

**[Common Mistakes & Fixes](resources/common-mistakes.md)** - Learn from common pitfalls

- Large unfocused PRs → Split into stacked diffs
- Vague commit messages → Use conventional commits
- Rewriting public history → Never rebase main
- Ignoring review comments → Address all feedback
- Committing secrets → Use environment variables
- Force push dangers → Use `--force-with-lease`

---

## Decision Tables

### When to Use Each Branching Strategy

| Requirement | GitHub Flow | Trunk-Based | GitFlow |
|-------------|-------------|-------------|---------|
| Continuous deployment | ✅ Best | ✅ Best | ❌ Poor |
| Scheduled releases | ⚠️ OK | ⚠️ OK | ✅ Best |
| Multiple versions | ❌ Poor | ❌ Poor | ✅ Best |
| Small team (< 5) | ✅ Best | ⚠️ OK | ❌ Overkill |
| Large team (> 15) | ⚠️ OK | ✅ Best | ⚠️ OK |
| Fast iteration | ✅ Best | ✅ Best | ❌ Poor |

### PR Size vs Review Time

| LOC | Review Time | Bug Detection | Recommendation |
|-----|-------------|---------------|----------------|
| < 50 | < 10 min | High | ✅ Ideal for hotfixes |
| 50-200 | 10-30 min | High | ✅ Ideal for features |
| 200-400 | 30-60 min | Medium-High | ✅ Acceptable |
| 400-1000 | 1-2 hours | Medium | ⚠️ Consider splitting |
| > 1000 | > 2 hours | Low | ❌ Always split |

---

## Related Skills

- [Software Code Review](../software-code-review/SKILL.md) - Code review standards and techniques
- [Quality Debugging & Troubleshooting](../quality-debugging-troubleshooting/SKILL.md) - Git bisect, debugging workflows
- [DevOps Platform Engineering](../ops-devops-platform/SKILL.md) - CI/CD pipelines, automation
- [Software Testing & Automation](../software-testing-automation/SKILL.md) - Test-driven development, coverage gates
- [Documentation Standards](../foundation-documentation/SKILL.md) - Changelog formats, documentation workflows

---

## Usage Notes

**For Claude Code**:

- Recommend GitHub Flow for most modern teams (simple, effective)
- Suggest stacked diffs for features > 500 lines
- Always validate commit messages against conventional commit format
- Check PR size - warn if > 400 lines, block if > 1000 lines
- Reference templates/ for copy-paste ready configurations
- Use resources/ for deep-dive implementation guidance

**Progressive Disclosure**:

1. Start with Quick Reference for fast lookups
2. Use Decision Tree for choosing strategies
3. Navigate to specific resources for detailed implementation
4. Reference templates for production-ready configurations
5. Check validation checklists before PR/merge/release

---

## Quick Command Reference

**Common Operations**:

```bash
# Rebase feature branch
git fetch origin && git rebase origin/main

# Interactive rebase last 3 commits
git rebase -i HEAD~3

# Squash all commits in branch
git rebase -i $(git merge-base HEAD main)

# Force push safely
git push --force-with-lease origin feature-branch

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Cherry-pick specific commit
git cherry-pick abc123

# Stash changes
git stash save "WIP: implementing feature X"
git stash pop
```

**Conflict Resolution**:

```bash
# Pull latest with rebase
git pull --rebase origin main

# Use visual merge tool
git mergetool

# Accept their changes
git checkout --theirs <file>

# Accept your changes
git checkout --ours <file>
```
