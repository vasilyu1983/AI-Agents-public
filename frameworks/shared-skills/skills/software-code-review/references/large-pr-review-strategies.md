# Large PR Review Strategies

Patterns and techniques for reviewing large pull requests effectively, including PR stacking, incremental review, and cognitive load management. Large PRs are the single most common source of review pain -- they slow teams down, reduce review quality, and introduce more post-merge defects.

---

## Table of Contents

1. [PR Size Guidelines](#pr-size-guidelines)
2. [Why Smaller PRs Win](#why-smaller-prs-win)
3. [PR Stacking Patterns](#pr-stacking-patterns)
4. [Incremental Review Strategies](#incremental-review-strategies)
5. [Review Delegation and Splitting](#review-delegation-and-splitting)
6. [Commit-by-Commit vs Diff Review](#commit-by-commit-vs-diff-review)
7. [Reviewer Cognitive Load Management](#reviewer-cognitive-load-management)
8. [Tooling for Large PR Review](#tooling-for-large-pr-review)
9. [Anti-Patterns](#anti-patterns)
10. [Decision Framework](#decision-framework)

---

## PR Size Guidelines

### Recommended Size Thresholds

| PR Size (Lines Changed) | Category | Review Time | Defect Detection Rate |
|--------------------------|----------|-------------|----------------------|
| 1-50 | Small | 5-10 min | ~60-70% |
| 51-200 | Medium | 15-30 min | ~50-60% |
| 201-400 | Large | 30-60 min | ~30-40% |
| 401-1000 | Very Large | 60-120 min | ~15-25% |
| 1000+ | Unmanageable | 2+ hours | <15% |

**Target**: Keep PRs under 200 lines of meaningful changes (excluding generated code, lockfiles, and test fixtures).

### What Counts Toward Size

Include in line count:
- Application source code changes
- Test code (but weight less heavily)
- Configuration changes with logic implications

Exclude from line count:
- Auto-generated files (lockfiles, schema outputs)
- Large test fixture data files
- Snapshot files
- Migration files (review separately for correctness)

### Size Calculation

```bash
# Quick PR size check (GitHub CLI)
gh pr diff <PR-NUMBER> --stat

# Lines of meaningful code (exclude generated)
gh pr diff <PR-NUMBER> | grep '^[+-]' | grep -v '^[+-]{3}' | \
  grep -v 'package-lock\|yarn.lock\|\.snap' | wc -l

# Graphite CLI size check
gt stack info
```

---

## Why Smaller PRs Win

### Data-Backed Evidence

Research from Google, Microsoft, and SmartBear consistently shows:

- **Review effectiveness drops sharply after 200-400 lines**. Reviewers find fewer defects per line as PR size grows.
- **Review speed declines non-linearly**. A 400-line PR does not take twice as long as a 200-line PR -- it takes 3-4x as long due to context-switching overhead.
- **Defect escape rate correlates with size**. Large PRs are merged with more undetected issues because reviewers experience fatigue and start skimming.
- **Merge conflict probability increases quadratically** with the number of files touched and the time a branch stays open.

### Team Velocity Impact

| Metric | Small PRs (<200 LOC) | Large PRs (>400 LOC) |
|--------|----------------------|----------------------|
| Time to first review | Hours | Days |
| Review iterations | 1-2 rounds | 3-5 rounds |
| Merge conflicts | Rare | Frequent |
| Revert frequency | Low | High |
| Reviewer willingness | High | Low ("I'll look later") |

### The Compounding Problem

```text
Large PR submitted
  -> Reviewer delays (overwhelmed)
  -> Author continues building on branch
  -> Branch diverges further from main
  -> Merge conflicts accumulate
  -> Reviewer receives updated PR (even larger)
  -> Cycle repeats
```

Breaking this cycle requires structural changes, not willpower.

---

## PR Stacking Patterns

PR stacking decomposes a large feature into a chain of dependent, reviewable PRs that merge sequentially.

### Manual Stacking (Git)

```bash
# Create a stack of branches
git checkout main
git checkout -b feature/step-1-data-model
# ... make changes, commit, push
git checkout -b feature/step-2-api-layer
# ... make changes building on step 1
git checkout -b feature/step-3-ui-integration
# ... make changes building on step 2

# Create PRs: step-1 -> main, step-2 -> step-1, step-3 -> step-2
```

**Problem with manual stacking**: Rebasing the stack when step-1 changes is tedious and error-prone. Every dependent branch must be rebased.

### Graphite

```bash
# Install
npm install -g @withgraphite/graphite-cli

# Create stacked branches
gt branch create feature/step-1
# ... make changes
gt commit create -m "Add data model"

gt branch create feature/step-2
# ... make changes
gt commit create -m "Add API layer"

gt branch create feature/step-3
# ... make changes
gt commit create -m "Add UI integration"

# Submit entire stack for review
gt stack submit

# When step-1 is updated, restack automatically
gt stack restack

# Merge the whole stack
gt stack merge
```

**Key benefit**: Graphite automates rebasing. When a base PR changes, `gt stack restack` propagates changes through the stack.

### Git Town

```bash
# Create stacked feature branches
git town hack step-1
# ... make changes, commit
git town append step-2
# ... make changes, commit
git town append step-3
# ... make changes, commit

# Sync the entire stack with upstream
git town sync
```

### Stacking Strategy: How to Decompose

| Decomposition Axis | Example | When to Use |
|---------------------|---------|-------------|
| By layer | Data model -> API -> UI | Standard feature work |
| By concern | Auth -> Validation -> Business logic | Cross-cutting features |
| By risk level | High-risk core -> Low-risk wiring | Security-sensitive features |
| By reviewability | Schema migration -> Code changes | Database changes |
| By dependency | Library upgrade -> Consumer updates | Dependency bumps |

### Stack Sizing

- Each PR in a stack: 50-200 lines
- Stack depth: 3-5 PRs maximum (beyond 5, reconsider decomposition)
- Each PR should be independently testable (CI passes at each level)

---

## Incremental Review Strategies

When a large PR is unavoidable (migrations, major refactors, generated code), use incremental review.

### Multi-Pass Review

```text
Pass 1: Architecture and design (10 minutes)
  - Read the PR description and linked issue
  - Scan file list for scope and organization
  - Check for new dependencies or architectural changes
  - Identify the riskiest files

Pass 2: High-risk files first (20-30 minutes)
  - Security-sensitive code (auth, input handling, crypto)
  - Business logic with edge cases
  - Database queries and migrations
  - Public API surface changes

Pass 3: Supporting code (15-20 minutes)
  - Test coverage and quality
  - Error handling patterns
  - Configuration and infrastructure changes

Pass 4: Polish (5-10 minutes)
  - Naming and readability
  - Documentation and comments
  - Code style consistency
```

### Review Partitioning by File Groups

For PRs touching many files, mentally partition into groups:

```text
Group A: Core logic changes (review carefully)
  src/services/payment.ts
  src/models/transaction.ts

Group B: API surface (review for contract correctness)
  src/routes/payments.ts
  src/middleware/auth.ts

Group C: Tests (review for coverage, not style)
  tests/services/payment.test.ts
  tests/routes/payments.test.ts

Group D: Config/infra (review for correctness)
  docker-compose.yml
  .github/workflows/deploy.yml

Group E: Generated/mechanical (skim or skip)
  package-lock.json
  prisma/migrations/20240115_add_payments.sql
```

### Time-Boxing

Set a timer. If a PR requires more than 60 minutes of focused review, stop and request that the author split it. Continuing past 60 minutes yields diminishing returns.

---

## Review Delegation and Splitting

### When to Split Reviewers

| Scenario | Strategy |
|----------|----------|
| Full-stack feature | Frontend reviewer + Backend reviewer |
| Security-sensitive + Feature | Security reviewer (P0/P1) + Feature reviewer (P2/P3) |
| Cross-team changes | Domain expert per team |
| Infrastructure + Application | Platform engineer + App developer |
| Database + Application | DBA review migration + Developer review code |

### Delegation Template

```markdown
## Review Delegation

@frontend-reviewer: Please review `src/components/` and `src/hooks/` for:
- Component composition and prop design
- Accessibility (WCAG 2.2)
- Performance (unnecessary re-renders)

@backend-reviewer: Please review `src/api/` and `src/services/` for:
- Input validation and error handling
- Database query efficiency
- Authentication/authorization

@security-reviewer: Please review for:
- [ ] Input sanitization
- [ ] Authorization checks on all endpoints
- [ ] No secrets in code
```

### Reviewer Assignment Automation

```yaml
# .github/CODEOWNERS
# Assign reviewers by path
/src/components/    @frontend-team
/src/api/           @backend-team
/src/auth/          @security-team
/infrastructure/    @platform-team
/prisma/migrations/ @dba-team
```

---

## Commit-by-Commit vs Diff Review

### When to Use Commit-by-Commit

| Approach | Best For | Worst For |
|----------|----------|-----------|
| Commit-by-commit | Refactors with logical steps, well-structured histories | Messy commit histories, squash merges |
| Full diff | Small PRs, single-concern changes | Large PRs with mixed concerns |
| Hybrid | Large PRs with clean commits | Poorly structured histories |

### Commit-by-Commit Review Process

```text
1. Read PR description for overall intent
2. Review commits in order:
   Commit 1: "Extract PaymentService from PaymentController"
     -> Verify behavior preservation (no logic changes)
   Commit 2: "Add input validation to PaymentService"
     -> Verify validation logic and edge cases
   Commit 3: "Add PaymentService tests"
     -> Verify test coverage matches changes in commits 1-2
3. Sanity-check the full diff for anything missed
```

**Prerequisite**: Authors must structure commits for reviewability. If the history is messy (fixup commits interleaved with features), commit-by-commit review adds confusion rather than clarity.

### Author Guidelines for Reviewable Commits

- One logical change per commit (single responsibility)
- Each commit should compile and pass tests independently
- Use `git rebase -i` to clean up history before requesting review
- Prefix commits with intent: `refactor:`, `feat:`, `fix:`, `test:`
- Separate mechanical changes (renames, moves) from behavioral changes

---

## Reviewer Cognitive Load Management

### The 400-Line Rule

Human working memory holds approximately 4-7 chunks of information. After reviewing 200-400 lines, a reviewer's mental model of the changes starts degrading.

### Reducing Cognitive Load

**For authors:**

- Write a thorough PR description with context and motivation
- Highlight the most important files to review
- Call out intentional tradeoffs and known limitations
- Include before/after screenshots for UI changes
- Add inline comments explaining non-obvious decisions

**For reviewers:**

- Review when fresh (morning or after a break), not at end of day
- Close other tabs and notifications during review
- Take a 5-minute break between PRs
- Set a per-PR time limit (45-60 minutes)
- If confused, ask rather than guess

### Review Session Structure

```text
Review session (2 hours max per day):
  [10 min] PR 1: Small bug fix (50 lines) -> Approve or request changes
  [5 min]  Break
  [25 min] PR 2: Feature work (180 lines) -> Approve or request changes
  [5 min]  Break
  [40 min] PR 3: Larger refactor (350 lines) -> First pass, leave comments
  [5 min]  Break
  [30 min] PR 4: API change (150 lines) -> Approve or request changes
```

### Reviewer Rotation

Avoid the single-reviewer bottleneck:

| Practice | Implementation |
|----------|----------------|
| Round-robin assignment | Rotate primary reviewer across team |
| Expertise-based routing | Use CODEOWNERS for domain routing |
| Review buddies | Pair team members for shared context |
| Load-aware assignment | Track open review count per person |

---

## Tooling for Large PR Review

### GitHub Features

| Feature | How It Helps |
|---------|-------------|
| File tree filtering | Focus on specific directories |
| Viewed checkbox | Track which files you have reviewed |
| Suggestion blocks | Propose specific code changes inline |
| Required reviews by path | Different reviewers for different areas |
| PR templates | Structured descriptions with checklists |

### IDE-Based Review

```text
VS Code + GitHub Pull Requests extension:
  - Review diffs in full editor context
  - Navigate to definitions and references
  - Run tests against the PR branch locally
  - Leave comments with full code intelligence
```

### Third-Party Tools

| Tool | Key Feature for Large PRs |
|------|--------------------------|
| Graphite | PR stacking, stack-aware merge queue |
| Reviewable | Incremental review tracking, file-level disposition |
| CodeSee | Visual diff maps, impact analysis |
| Gitpod/Codespaces | One-click PR environments for manual testing |

### Folding and Focus Mode

For very large diffs, use file-level strategies:

```bash
# GitHub: Filter files by extension
?w=1  # Ignore whitespace changes (append to URL)

# View only specific file types in the diff
# Use the file tree filter in the GitHub UI

# Local review with selective diff
git diff main...feature -- '*.ts' '!*.test.ts'  # Only source files
git diff main...feature -- '*.test.ts'            # Only test files
```

---

## Anti-Patterns

### 1. "LGTM" on 1000-Line PRs

**Problem**: Rubber-stamping large PRs to unblock the author. The review provides no value and creates a false sense of safety.

**Fix**: If you cannot meaningfully review a PR, say so. Request that the author split it or assign additional reviewers.

### 2. Blocking on Perfectionism

**Problem**: Leaving 30 comments on style and naming in a large PR, creating multi-round review cycles that take weeks.

**Fix**: Separate blocking concerns (P0/P1: security, correctness) from non-blocking suggestions (P2/P3: style, naming). Approve with non-blocking suggestions.

### 3. Review Hoarding

**Problem**: One senior engineer reviews all PRs, creating a bottleneck. PRs queue for days.

**Fix**: Distribute review responsibility. Use CODEOWNERS and rotation schedules.

### 4. The "One More Thing" Cycle

**Problem**: Each review round introduces new requests, leading to scope creep. The PR grows instead of shrinking.

**Fix**: File follow-up issues for non-critical improvements. Approve the current PR and track improvements separately.

### 5. Reviewing Generated Code Line-by-Line

**Problem**: Spending time reviewing auto-generated migrations, lockfiles, or snapshot files line by line.

**Fix**: Verify the generation command is correct and the output is expected. Do not review generated artifacts character by character.

### 6. No PR Description

**Problem**: Reviewer must reverse-engineer intent from the diff. This doubles review time and reduces accuracy.

**Fix**: Require PR descriptions via templates. Block merge until the description meets minimum quality.

### 7. Mixing Refactors with Features

**Problem**: A PR contains both a refactor and a new feature. The reviewer cannot distinguish behavioral changes from mechanical restructuring.

**Fix**: Separate refactors into their own PRs. Review refactors for behavior preservation; review features for correctness.

---

## Decision Framework

### Should I Request a Split?

```text
PR arrives for review:
  |
  ├─ Under 200 lines of meaningful changes?
  │   └─ Review normally
  |
  ├─ 200-400 lines?
  │   ├─ Single concern? -> Review with multi-pass approach
  │   └─ Multiple concerns? -> Request split by concern
  |
  ├─ 400-1000 lines?
  │   ├─ Unavoidable (migration, generated code)?
  │   │   └─ Partition review, delegate, time-box
  │   └─ Could be split?
  │       └─ Request split, provide decomposition suggestions
  |
  └─ Over 1000 lines?
      └─ Always request split unless migration/generated
          Provide stacking strategy suggestions
```

### How to Request a Split Without Being Adversarial

```markdown
Hey, this PR covers a lot of ground and I want to give it a thorough review.
Could we split it into smaller pieces? Here's one way I see it breaking down:

1. **PR 1**: Data model changes (migrations + models) — ~80 lines
2. **PR 2**: Service layer (business logic + tests) — ~150 lines
3. **PR 3**: API endpoints (routes + integration tests) — ~120 lines

This would let me review each piece more carefully and unblock merging
the foundational changes sooner. Happy to discuss if this decomposition
doesn't work for the feature.
```

---

## Quick Reference Checklist

For authors submitting large PRs:

- [ ] PR description explains context, motivation, and scope
- [ ] Changes are decomposed into reviewable commits or stacked PRs
- [ ] Generated code is clearly marked and separated
- [ ] Riskiest changes are highlighted for the reviewer
- [ ] Tests cover the changed behavior
- [ ] Follow-up issues are filed for deferred improvements

For reviewers of large PRs:

- [ ] Read the PR description before looking at code
- [ ] Scan file list and identify risk groups
- [ ] Review high-risk files first (security, business logic)
- [ ] Use multi-pass approach (architecture -> logic -> polish)
- [ ] Time-box the review session (60 minutes max)
- [ ] Separate blocking issues (P0/P1) from suggestions (P2/P3)
- [ ] If overwhelmed, request a split rather than rubber-stamping

---

## Cross-References

- [operational-playbook.md](operational-playbook.md) -- Review modes, severity ratings, and PR workflow patterns
- [review-checklist-comprehensive.md](review-checklist-comprehensive.md) -- Full review checklist by concern
- [automation-tools.md](automation-tools.md) -- CI/CD automation and stack-aware merge queues (Graphite, Aviator)
- [psychological-safety-guide.md](psychological-safety-guide.md) -- Giving constructive feedback on large PRs
- [code-review-metrics.md](code-review-metrics.md) -- Measuring review effectiveness and turnaround time
