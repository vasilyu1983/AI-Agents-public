# Stacked Diffs Implementation Guide

Comprehensive guide to implementing stacked diffs workflows for faster code reviews and iterative development.

## Contents

- What Are Stacked Diffs?
- When to Use Stacked Diffs
- Platform Support
- Stacked Diffs Best Practices
- Handling Common Scenarios
- Stack Visualization Tools
- Migration Strategies
- Metrics to Track
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

Review time: 4-8 hours
Merge time: 3-5 days
```

**Stacked Diffs**:
```
Stack 1: feat/cart-models (200 lines)
  └─ Stack 2: feat/cart-api (250 lines)
      └─ Stack 3: feat/cart-ui (300 lines)
          └─ Stack 4: feat/payment (350 lines)
              └─ Stack 5: feat/confirmation (200 lines)

Review time per stack: 30-60 min
Total merge time: 1-2 days
```

### Key Benefits

[OK] **Faster Reviews**: 200-400 line PRs reviewed in 30-60 minutes vs 2-4 hours for 1000+ lines
[OK] **Better Code Quality**: Reviewers catch more issues with focused, manageable reviews
[OK] **Reduced Conflicts**: Smaller changes merged more frequently = fewer merge conflicts
[OK] **Parallel Work**: Continue building on top while previous stacks are under review
[OK] **Easier Reverts**: Revert individual stacks without undoing entire feature

### Trade-offs

[WARNING] **More CI Runs**: Each stack triggers CI, increasing compute costs
[WARNING] **Rebase Complexity**: Changes to earlier stacks require rebasing dependent stacks
[WARNING] **Tooling Required**: Native GitHub/GitLab support is limited, often requires tools like Graphite
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

### GitLab (Native Support)

GitLab added native stacked diffs support in 2024.

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
- GitLab automatically updates stack when base MR merges
- Native UI shows stack relationships

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

### GitHub (Requires Tooling)

GitHub doesn't natively support stacked diffs. Several tools enable stacking workflows:

#### Open-Source Stacking Alternatives

For a comprehensive comparison, see [The Stacking Workflow](https://www.stacking.dev/).

| Tool | Description | Pros | Cons |
|------|-------------|------|------|
| [Charcoal](https://github.com/danerwilliams/charcoal) | Open-source fork of Graphite CLI | Free, no limits | Community-maintained |
| [ghstack](https://github.com/ezyang/ghstack) | CLI for stacking on GitHub | Open-source, simple | Single commit per PR required |
| [Sapling](https://sapling-scm.com/) | Meta's source control system | Full-featured, maintained by Meta | Learning curve |
| [spr](https://github.com/ejoffe/spr) | Stacked PRs for GitHub | Lightweight, simple | Single commit per PR |
| [git-branchless](https://github.com/arxanas/git-branchless) | High-level Git CLI | Powerful, undo support | Complex for beginners |

#### Option 1: Graphite CLI (Recommended)

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

### 1. Keep Each Stack Small (200-400 LOC)

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

Visual stack view at https://app.graphite.dev:
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

## Metrics to Track

### Stack Effectiveness

| Metric | Before Stacks | With Stacks | Improvement |
|--------|--------------|-------------|-------------|
| Avg PR size | 800 LOC | 300 LOC | 62% reduction |
| Avg review time | 3.5 hours | 1.2 hours | 66% faster |
| PRs merged same day | 40% | 75% | 88% increase |
| Merge conflicts per PR | 4.2 | 1.1 | 74% reduction |
| Bug escape rate | 8% | 3% | 62% improvement |

### CI/CD Impact

| Metric | Impact |
|--------|--------|
| CI runs per feature | +150% (more PRs) |
| CI cost per feature | +25% (caching helps) |
| Time to first CI feedback | -60% (smaller PRs) |

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
| **Graphite** | GitHub | Best UX, automation, visual UI | Requires CLI | Free (< 10 devs) |
| **GitLab CLI** | GitLab | Native support, no external tool | GitLab only | Free |
| **git-stack** | GitHub | Open-source, lightweight | Basic features | Free |
| **Manual** | Any | Full control, no dependencies | Error-prone, tedious | Free |

---

## References

- **Graphite Guides**: https://graphite.dev/guides/stacked-diffs
- **GitLab Stacked Diffs**: https://docs.gitlab.com/user/project/merge_requests/stacked_diffs/
- **Pragmatic Engineer**: https://newsletter.pragmaticengineer.com/p/stacked-diffs
- **Phabricator Stacked Diffs**: https://secure.phabricator.com/book/phabricator/article/reviews/
