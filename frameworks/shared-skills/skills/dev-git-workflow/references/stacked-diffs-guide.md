# Stacked Diffs Implementation Guide

## Table of Contents

- [Contents](#contents)
- [What Are Stacked Diffs?](#what-are-stacked-diffs)
- [When to Use Stacked Diffs](#when-to-use-stacked-diffs)
- [Platform Support](#platform-support)
- [Stacked Diffs Best Practices](#stacked-diffs-best-practices)
- [Stack Order](#stack-order)
- [Dependencies](#dependencies)
- [Handling Common Scenarios](#handling-common-scenarios)
- [Stack Visualization Tools](#stack-visualization-tools)
- [Migration Strategies](#migration-strategies)
- [Local Metrics to Track](#local-metrics-to-track)
- [Team Guidelines Template](#team-guidelines-template)
- [When to Use Stacks](#when-to-use-stacks)
- [Stack Size](#stack-size)
- [Naming Convention](#naming-convention)
- [PR Description Template](#pr-description-template)
- [Review Process](#review-process)
- [Tools](#tools)
- [Troubleshooting](#troubleshooting)
- [Merge Order (IMPORTANT)](#merge-order-important)
- [Tools Comparison](#tools-comparison)
- [References](#references)

Comprehensive guide to implementing stacked diffs workflows for faster code reviews and iterative development.

## Contents

- What Are Stacked Diffs?
- When to Use Stacked Diffs
- Platform Support
- Stacked Diffs Best Practices
- Handling Common Scenarios
- Stack Visualization Tools
- Migration Strategies
- Local Metrics to Track
- Team Guidelines Template
- Tools Comparison
- References

---

## What Are Stacked Diffs?

**Stacked diffs** (also called stacked PRs or stacked changes) is a development workflow where you break large features into a series of small, dependent pull requests that build upon each other.

### Traditional vs Stacked Approach

**Traditional Large PR**:
```
feature/checkout (2000 lines)
  ├── Add cart models
  ├── Implement cart API
  ├── Build cart UI
  ├── Add payment integration
  └── Add order confirmation

Review experience: reviewers must understand everything at once
Merge experience: changes often wait on one large review
```

**Stacked Diffs**:
```
Stack 1: feat/cart-models (200 lines)
  └─ Stack 2: feat/cart-api (250 lines)
      └─ Stack 3: feat/cart-ui (300 lines)
          └─ Stack 4: feat/payment (350 lines)
              └─ Stack 5: feat/confirmation (200 lines)

Review experience: each PR is focused and easier to reason about
Merge experience: earlier pieces can land while later pieces keep moving
```

### Key Benefits

[OK] **Faster Reviews**: reviewers can focus on one step of the change at a time
[OK] **Better Code Quality**: focused review units make reasoning and rollback easier
[OK] **Reduced Conflicts**: Smaller changes merged more frequently = fewer merge conflicts
[OK] **Parallel Work**: Continue building on top while previous stacks are under review
[OK] **Easier Reverts**: Revert individual stacks without undoing entire feature

### Trade-offs

[WARNING] **More CI Runs**: Each stack triggers CI, increasing compute costs
[WARNING] **Rebase Complexity**: Changes to earlier stacks require rebasing dependent stacks
[WARNING] **Tooling Required**: GitHub usually needs external tooling or disciplined manual stacks; GitLab stacked diffs are still experimental
[WARNING] **Team Adoption**: Requires team buy-in and workflow changes

---

## When to Use Stacked Diffs

### GOOD: Use Stacked Diffs When:

- Feature requires > 500 lines of code
- Multiple logical implementation phases
- Long-running feature branch (> 3 days)
- Complex refactoring with clear steps
- Want to ship partial functionality early
- Need faster feedback loops

### BAD: Don't Use Stacked Diffs When:

- Simple bug fix (< 100 lines)
- One-file change
- Hotfix requiring immediate merge
- Independent changes (no dependencies)
- Team unfamiliar with workflow

---

## Platform Support

### GitLab (Experimental Support)

GitLab documents stacked diffs, but the feature is still marked experimental. Use it only if your GitLab version and team workflow explicitly support it.

**Create stacked MR**:
```bash
# Create first MR to main
git checkout -b feat/cart-models main
git commit -m "feat: add cart data models"
git push origin feat/cart-models
# Create MR to main

# Create second MR stacked on first
git checkout -b feat/cart-api feat/cart-models
git commit -m "feat: implement cart API endpoints"
git push origin feat/cart-api
# Create MR to feat/cart-models (not main!)
```

**Key Points**:
- Target branch of dependent MR = previous MR's branch
- Re-check feature status on your GitLab version before standardizing on it
- Prefer merge trains for high-concurrency landing, not for modeling dependency stacks

**GitLab CLI (`glab stack`)** - Released in v1.42.0:

```bash
# Install GitLab CLI
brew install glab

# Create a new stack
glab stack create cart-feature

# Make changes and save to stack
# (creates a new branch automatically)
glab stack save "feat: add cart data models"

# Make more changes
glab stack save "feat: implement cart API endpoints"

# Push stack and create MRs
glab stack sync
# Creates MR for each stack entry

# Move between stacks
glab stack move
# Interactive selection of stacks to edit

# Amend current stack entry
glab stack amend

# View stack status
glab stack list
```

**Key Points**:

- Each `glab stack save` creates a new branch internally
- `glab stack sync` creates/updates MRs for the entire stack
- Stack metadata is stored locally in `.git/` directory
- See [glab stack documentation](https://docs.gitlab.com/cli/stack/) for full reference

**Legacy approach** (manual MR chaining):
```bash
# Create stacked MRs manually
glab mr create --target-branch feat/cart-models
```

### GitHub (Native + External Tooling)

**GitHub native stacked PRs** (`gh-stack` CLI extension) entered private preview on 13 April 2026. Verify GA status before standardizing on it — when available it eliminates the need for third-party tools for most teams.

For teams that cannot wait for GA, or that need advanced CLI ergonomics, use one of the tools below.

#### Open-Source Stacking Alternatives

For a comprehensive comparison, see [The Stacking Workflow](https://www.stacking.dev/).

| Tool | Description | Pros | Cons |
|------|-------------|------|------|
| [Charcoal](https://github.com/danerwilliams/charcoal) | Open-source fork of Graphite CLI | Free, no limits | Community-maintained |
| [ghstack](https://github.com/ezyang/ghstack) | CLI for stacking on GitHub | Open-source, simple | Single commit per PR required |
| [Sapling](https://sapling-scm.com/) | Meta's source control system | Full-featured, maintained by Meta | Learning curve |
| [spr](https://github.com/ejoffe/spr) | Stacked PRs for GitHub | Lightweight, simple | Single commit per PR |
| [git-branchless](https://github.com/arxanas/git-branchless) | High-level Git CLI | Powerful, undo support | Complex for beginners |

#### Option 1: Graphite CLI

**Install**:
```bash
npm install -g @withgraphite/graphite-cli
gt auth
```

**Workflow**:
```bash
# Initialize repository
gt repo init

# Create first stack
gt branch create feat/cart-models
# Make changes
git commit -m "feat: add cart data models"

# Create second stack (auto-stacks on current)
gt branch create feat/cart-api
# Make changes
git commit -m "feat: implement cart API endpoints"

# Create third stack
gt branch create feat/cart-ui
# Make changes
git commit -m "feat: build cart UI components"

# View stack
gt log short
# Output:
# ◉  feat/cart-ui (current)
# │
# ◉  feat/cart-api
# │
# ◉  feat/cart-models
# │
# ◉  main

# Submit entire stack to GitHub
gt stack submit
# Creates 3 PRs:
# - feat/cart-models -> main
# - feat/cart-api -> feat/cart-models
# - feat/cart-ui -> feat/cart-api
```

**Graphite Commands**:
```bash
# Navigation
gt up          # Move up stack
gt down        # Move down stack
gt top         # Jump to top of stack
gt bottom      # Jump to bottom of stack

# Stack management
gt stack      # View current stack
gt stack submit  # Submit all PRs in stack
gt stack test    # Run tests on entire stack
gt stack sync    # Sync stack with remote

# Rebasing
gt stack restack  # Rebase entire stack on latest main
gt upstack onto   # Rebase current branch + upstack onto target
```

**Handle changes to earlier stacks**:
```bash
# Make changes to feat/cart-models
gt checkout feat/cart-models
# Edit files
git commit -m "fix: update cart model validation"

# Restack dependent branches automatically
gt stack restack
# Rebases feat/cart-api and feat/cart-ui on updated feat/cart-models
```

#### Option 2: Manual GitHub Workflow

```bash
# Create first PR to main
git checkout -b feat/cart-models main
git commit -m "feat: add cart data models"
git push origin feat/cart-models
# Create PR: feat/cart-models -> main

# Create second PR stacked on first
git checkout -b feat/cart-api feat/cart-models
git commit -m "feat: implement cart API endpoints"
git push origin feat/cart-api
# Create PR: feat/cart-api -> feat/cart-models

# Continue stacking...
```

**Manual Rebase After Base PR Merges**:
```bash
# After feat/cart-models merges to main
git checkout feat/cart-api
git rebase main
git push --force-with-lease origin feat/cart-api

# Update PR target to main manually on GitHub
```

**Challenges with Manual Approach**:
- Must manually change PR target after base merges
- No visual stack representation
- Rebasing requires careful coordination
- Error-prone for large stacks

---

## Stacked Diffs Best Practices

### 1. Keep Each Stack Small and Reviewable

```bash
# GOOD: Good: Focused, reviewable stacks
Stack 1: Add cart data models (180 lines)
Stack 2: Implement cart CRUD API (250 lines)
Stack 3: Add cart UI components (320 lines)

# BAD: Bad: Stacks too large
Stack 1: Add entire cart feature (1500 lines)
Stack 2: Add payment integration (1200 lines)
```

### 2. Ensure Each Stack is Independently Reviewable

Each stack should:
- Have clear, focused purpose
- Include relevant tests
- Be self-contained logic
- Provide value on its own

```bash
# GOOD: Good: Self-contained stacks
Stack 1: feat: add cart data models + unit tests
Stack 2: feat: implement cart API endpoints + integration tests
Stack 3: feat: build cart UI components + component tests

# BAD: Bad: Incomplete stacks
Stack 1: feat: add half of cart models
Stack 2: feat: finish cart models + start API
Stack 3: feat: finish API + half of UI
```

### 3. Use Descriptive Stack Names

```bash
# GOOD: Good: Clear progression
feat/cart-01-models
feat/cart-02-api-crud
feat/cart-03-api-validation
feat/cart-04-ui-components
feat/cart-05-ui-integration

# BAD: Bad: Unclear order
feat/cart-stuff
feat/cart-more
feat/cart-final
```

### 4. Document Stack Dependencies

In each PR description:

```markdown
## Stack Order

This is **Part 3 of 5** in the cart feature stack:

1. [OK] #234 - Add cart data models
2. [OK] #235 - Implement cart CRUD API
3. [BLUE] #236 - Add cart API validation (this PR)
4. ⏸ #237 - Build cart UI components
5. ⏸ #238 - Integrate cart UI with API

## Dependencies

This PR depends on:
- #235 (cart CRUD API) - must merge first

This PR blocks:
- #237 (cart UI) - builds on this validation
```

### 5. Rebase Frequently

```bash
# Keep stack up-to-date with main
gt stack restack  # Graphite
# Or manually:
git checkout feat/cart-models
git rebase main
git checkout feat/cart-api
git rebase feat/cart-models
# ...continue for all stacks
```

### 6. CI/CD Optimization

Reduce CI cost with smart caching:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Cache dependencies across stack
      - uses: actions/cache@v3
        with:
          path: node_modules
          key: ${{ runner.os }}-${{ hashFiles('package-lock.json') }}

      # Only run tests for changed files
      - name: Run tests
        run: npm test -- --changedSince=origin/main
```

---

## Handling Common Scenarios

### Scenario 1: Reviewer Requests Changes to Earlier Stack

**Problem**: Stack 1 merged, but reviewer finds issue in Stack 2 that requires changes to Stack 1.

**Solution**:

```bash
# Graphite approach (recommended)
gt checkout feat/cart-models
# Make fixes
git commit -m "fix: address review feedback on cart models"
gt stack restack  # Automatically rebases dependent stacks

# Manual approach
git checkout feat/cart-models
# Make fixes
git commit -m "fix: address review feedback on cart models"
git push origin feat/cart-models

# Rebase all dependent stacks
git checkout feat/cart-api
git rebase feat/cart-models
git push --force-with-lease origin feat/cart-api

git checkout feat/cart-ui
git rebase feat/cart-api
git push --force-with-lease origin feat/cart-ui
```

### Scenario 2: Earlier Stack Blocked, Want to Continue

**Problem**: Stack 2 needs major revisions, but Stack 3-5 are ready.

**Solution**: Temporarily merge stacks or create parallel stack.

```bash
# Option 1: Squash Stack 2-5 temporarily
git checkout feat/cart-api
git merge --squash feat/cart-ui
git merge --squash feat/payment
git push origin feat/cart-api-combined
# Create PR: feat/cart-api-combined -> main

# Option 2: Create independent stack
git checkout main
git checkout -b feat/cart-ui-independent
# Cherry-pick only UI changes (skip API changes)
git cherry-pick <commit-hash>
```

### Scenario 3: Main Branch Advances, Causing Conflicts

**Problem**: Many commits merged to main, causing conflicts in Stack 1.

**Solution**: Rebase entire stack on latest main.

```bash
# Graphite
gt stack restack

# Manual
git checkout feat/cart-models
git fetch origin
git rebase origin/main
git push --force-with-lease origin feat/cart-models

# Rebase all dependent stacks...
```

### Scenario 4: Want to Ship Partial Feature

**Problem**: Stacks 1-3 complete, but Stacks 4-5 blocked. Want to ship 1-3.

**Solution**: Use feature flags.

```bash
# Stack 1: Add feature flag + models
if (featureFlags.cartEnabled) {
  // Cart logic
}

# Stack 2: Implement API behind flag
# Stack 3: Add UI behind flag

# Stacks 1-3 merge to main (feature flag OFF)
# Later: Turn feature flag ON when Stacks 4-5 ready
```

---

## Stack Visualization Tools

### Graphite Web App

Visual stack view at https://app.graphite.com (Graphite moved off the graphite.dev domain in November 2025):
- Drag-and-drop to reorder stacks
- See CI status for entire stack
- Merge stacks in order with one click

### GitLab Merge Request Stack View

GitLab UI shows stack relationships:
```
[MR !456] feat/cart-ui -> feat/cart-api
  ↓ depends on
[MR !455] feat/cart-api -> feat/cart-models
  ↓ depends on
[MR !454] feat/cart-models -> main
```

### ASCII Stack Visualization

Use `gt log short` (Graphite):
```
◉  feat/payment (under review)
│
◉  feat/cart-ui (merged)
│
◉  feat/cart-api (merged)
│
◉  feat/cart-models (merged)
│
◉  main
```

---

## Migration Strategies

### Migrate Existing Large PR to Stacks

**Step 1: Analyze PR Structure**
```bash
git log feat/large-feature --oneline
# Identify logical groupings of commits
```

**Step 2: Extract Stacks**
```bash
# Create Stack 1 from first logical group
git checkout -b feat/stack-1 main
git cherry-pick <commit1> <commit2>
git push origin feat/stack-1

# Create Stack 2
git checkout -b feat/stack-2 feat/stack-1
git cherry-pick <commit3> <commit4>
git push origin feat/stack-2
```

**Step 3: Create PRs**
```bash
# Stack 1 -> main
# Stack 2 -> Stack 1
# ...
```

### Gradual Team Adoption

**Phase 1: Pilot Team (Week 1-2)**
- 1-2 developers try stacked diffs
- Document learnings and pain points

**Phase 2: Expand (Week 3-4)**
- Share pilot results with team
- Train additional developers
- Set stack size guidelines

**Phase 3: Team-Wide (Month 2)**
- Require stacked diffs for features > 500 LOC
- Add stack visualization to PR template
- Track metrics (review time, merge rate)

---

## Local Metrics to Track

Measure stacked diffs against your current workflow instead of assuming universal gains.

- Time to first review
- Time from first PR opened to final PR merged
- Number of review rounds per stack
- Merge conflicts or rebases required per stack
- CI cost and queue time for a full stack
- Revert rate for stacked vs non-stacked changes

---

## Team Guidelines Template

```markdown
# Stacked Diffs Guidelines

## When to Use Stacks

- Features > 500 lines of code
- Multi-phase implementation
- Long-running branches (> 3 days)

## Stack Size

- **Target**: 200-400 lines per stack
- **Maximum**: 600 lines per stack
- **Include tests**: Each stack must have tests

## Naming Convention

Use format: `feat/<feature>-<number>-<description>`

Example:
- `feat/cart-01-models`
- `feat/cart-02-api`
- `feat/cart-03-ui`

## PR Description Template

Each stacked PR must include:

### Stack Context
- Part X of Y in <feature> stack
- Link to previous and next PRs
- High-level feature description

### This Stack
- What this specific stack adds
- Why this order/split
- Testing completed

## Review Process

- Review stacks in order (bottom to top)
- Approve each stack independently
- Merge stacks sequentially

## Tools

- **Required**: Graphite CLI or GitLab CLI
- **Optional**: Graphite web app for visualization
```

---

## Troubleshooting

### Problem: Rebase Conflicts Across Multiple Stacks

**Solution**: Resolve bottom-up
```bash
# Start with bottom stack
gt checkout feat/cart-models
git rebase main
# Resolve conflicts
git rebase --continue

# Restack automatically propagates fixes
gt stack restack
```

### Problem: CI Failing Due to Missing Dependencies

**Solution**: Ensure each stack includes dependencies
```bash
# BAD: Bad: Stack 2 depends on Stack 1 code but doesn't include it
Stack 1: Add CartModel class
Stack 2: Use CartModel (fails CI - CartModel not found)

# GOOD: Good: Each stack is independently testable
Stack 1: Add CartModel class + tests
Stack 2: Add CartService using CartModel + tests (passes CI)
```

### Problem: PR Merge Order Confusion

**Solution**: Document order clearly
```markdown
## Merge Order (IMPORTANT)

1. [OK] #234 - MERGE FIRST
2. ⏸ #235 - MERGE AFTER #234
3. ⏸ #236 - MERGE AFTER #235
```

---

## Tools Comparison

| Tool | Platform | Pros | Cons | Cost |
|------|----------|------|------|------|
| **GitHub gh-stack** | GitHub | Native, no extra tooling | Private preview as of April 2026; verify GA | Free (verify) |
| **Graphite** | GitHub | Mature; stack-aware merge queue; VS Code extension | External tool, team training, paid tiers | Free tier; paid from $20/user/month |
| **GitLab CLI (glab stack)** | GitLab | Works with GitLab-native concepts | Stacked diffs support version-gated / experimental | Free |
| **ghstack** | GitHub | Open-source, simple | Single commit per PR required | Free |
| **Manual** | Any | Full control, no dependencies | Easy to mis-order or mis-target PRs | Free |

---

## References

- **Graphite Guides**: https://graphite.com/guides/stacked-diffs (formerly graphite.dev)
- **GitLab Stacked Diffs**: https://docs.gitlab.com/user/project/merge_requests/stacked_diffs/
- **Pragmatic Engineer**: https://newsletter.pragmaticengineer.com/p/stacked-diffs
- **Phabricator Stacked Diffs**: https://secure.phabricator.com/book/phabricator/article/reviews/
