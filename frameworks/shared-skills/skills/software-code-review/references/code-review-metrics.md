# Code Review Metrics

Measuring code review effectiveness without creating perverse incentives. This guide covers what to measure, how to interpret metrics, and how to build dashboards that drive improvement rather than gaming.

---

## Table of Contents

1. [Why Measure Code Review](#why-measure-code-review)
2. [Review Turnaround Time](#review-turnaround-time)
3. [Review Thoroughness](#review-thoroughness)
4. [Defect Escape Rate](#defect-escape-rate)
5. [Review Cycle Time and Iterations](#review-cycle-time-and-iterations)
6. [Reviewer Load Balancing](#reviewer-load-balancing)
7. [DORA Metrics Intersection](#dora-metrics-intersection)
8. [Avoiding Gaming and Perverse Incentives](#avoiding-gaming-and-perverse-incentives)
9. [Dashboard Design](#dashboard-design)
10. [Implementation Guide](#implementation-guide)
11. [Anti-Patterns](#anti-patterns)

---

## Why Measure Code Review

### Goals of Review Metrics

| Goal | What Metrics Help With |
|------|------------------------|
| Speed | Are PRs getting reviewed quickly enough to unblock developers? |
| Quality | Are reviews catching real bugs before they reach production? |
| Fairness | Is review load distributed evenly across the team? |
| Sustainability | Are reviewers burning out from review volume? |
| Process health | Is the review process improving over time? |

### What Metrics Cannot Tell You

Metrics measure process efficiency, not review quality. A fast, low-iteration review could mean:

- The code was well-written and easy to review (good)
- The reviewer rubber-stamped it (bad)

Always interpret metrics in context. Use them as diagnostic signals, not performance targets.

---

## Review Turnaround Time

### Key Metrics

| Metric | Definition | Target | Why It Matters |
|--------|-----------|--------|----------------|
| Time to First Response (TTFR) | Time from PR creation to first substantive reviewer comment | < 4 hours (business hours) | Long TTFR blocks authors and creates context-switching |
| Time to Approval (TTA) | Time from PR creation to final approval | < 24 hours (P2), < 4 hours (P0) | Determines merge velocity |
| Time to Merge (TTM) | Time from PR creation to merge | < 48 hours (P2) | Includes CI, post-review fixes, and merge queue |
| Pickup Time | Time from review request to reviewer starting | < 2 hours | Indicates reviewer availability |

### Measurement

```sql
-- Time to first response (PostgreSQL example)
SELECT
  pr.id,
  pr.created_at,
  MIN(comment.created_at) AS first_response_at,
  EXTRACT(EPOCH FROM (
    MIN(comment.created_at) - pr.created_at
  )) / 3600 AS hours_to_first_response
FROM pull_requests pr
LEFT JOIN review_comments comment
  ON comment.pr_id = pr.id
  AND comment.author_id != pr.author_id
WHERE pr.created_at > NOW() - INTERVAL '30 days'
GROUP BY pr.id, pr.created_at;
```

### SLA by Priority

| Priority | First Response SLA | Approval SLA |
|----------|-------------------|--------------|
| P0 (Security/Incident) | 1 hour | 4 hours |
| P1 (Bug fix, blocker) | 4 hours | 24 hours |
| P2 (Feature work) | 8 hours | 48 hours |
| P3 (Docs, refactoring) | 24 hours | 72 hours |

### Turnaround Distribution

Track the distribution, not just the average:

```text
TTFR Distribution (last 30 days):
  < 1 hour:    25%  -- Excellent
  1-4 hours:   40%  -- Good
  4-8 hours:   20%  -- Acceptable
  8-24 hours:  10%  -- Needs attention
  > 24 hours:   5%  -- Problem
```

The P90 and P95 values matter more than the median. A median of 3 hours is fine, but a P95 of 48 hours indicates a systemic problem for some PRs.

---

## Review Thoroughness

### Defects Found in Review

| Metric | Definition | How to Measure |
|--------|-----------|----------------|
| Comments per PR | Average number of substantive comments | Count comments excluding bot, nit, style |
| Blocking findings per PR | Average P0/P1 issues found | Count comments tagged as blocking |
| Issues found by category | Security, correctness, performance, style | Categorize review comments |
| Review depth score | Ratio of files reviewed to files changed | Track "viewed" checkmarks in GitHub |

### Categorizing Review Comments

Establish a tagging system for review comments to track what reviewers catch:

| Category | Tag | Example |
|----------|-----|---------|
| Security | `security` | Missing input validation, hardcoded secret |
| Correctness | `bug` | Off-by-one error, missing null check |
| Performance | `perf` | N+1 query, missing index |
| Design | `design` | Poor abstraction, wrong pattern |
| Maintainability | `readability` | Unclear naming, missing documentation |
| Style | `nit` | Formatting, import order |

### Review Comment Quality Ratio

```text
Quality ratio = (security + bug + perf + design comments) / total comments

Target: > 0.5 (at least half of comments are substantive)
Warning: < 0.3 (most comments are nits)
```

### Meaningful vs Superficial Reviews

Track the proportion of reviews with zero substantive comments:

```text
Reviews with 0 substantive comments: 30% -- May indicate rubber-stamping
Reviews with 1-3 substantive comments: 50% -- Normal range
Reviews with 4+ substantive comments: 20% -- Complex PRs or thorough review
```

A high percentage of zero-comment reviews combined with post-merge defects suggests review thoroughness is low.

---

## Defect Escape Rate

### Definition

Defect escape rate measures bugs that pass through code review and reach production (or are found in QA/staging).

```text
Escape Rate = Defects found after merge /
              (Defects found in review + Defects found after merge)

Target: < 20% (80%+ of defects caught in review)
Warning: > 40% (review process needs significant improvement)
```

### Tracking Post-Merge Defects

| Source | How to Correlate |
|--------|------------------|
| Bug tickets filed | Tag with originating PR number |
| Reverts | Track which PRs were reverted and why |
| Hotfixes | Link hotfix PRs to the PR that introduced the issue |
| Incident reports | Link incidents to contributing PRs |
| Security advisories | Track vulnerabilities traced to specific changes |

### Escape Rate by Category

```text
Category         Found in Review    Escaped    Escape Rate
Security         12                 2          14%
Correctness      45                 18         29%
Performance      8                  5          38%
Integration      3                  7          70%

Insight: Integration issues frequently escape review because
they require running the full system, not just reading diffs.
```

### Using Escape Rate to Improve

When a defect escapes:

1. **Retroactive review**: Could this have been caught in the original PR?
2. **Root cause**: Was it a reviewer oversight, missing test, or insufficient context?
3. **Process improvement**: Does the checklist need a new item? Do we need more test coverage?
4. **Knowledge sharing**: Should the team discuss this pattern?

---

## Review Cycle Time and Iterations

### Key Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Review rounds | Number of request-changes/re-review cycles | 1-2 rounds |
| Comments per round | Average comments in each iteration | Decreasing per round |
| Rework time | Time author spends addressing review feedback | < 4 hours per round |
| Abandonment rate | PRs closed without merge after review | < 5% |

### Iteration Analysis

```text
PR Iteration Breakdown (last 30 days):
  1 round (approve on first review):    45%
  2 rounds:                             35%
  3 rounds:                             15%
  4+ rounds:                             5%  -- Investigate these
```

### What High Iteration Counts Indicate

| Iteration Count | Possible Cause | Action |
|----------------|----------------|--------|
| 1 round consistently | Well-written PRs or rubber-stamping | Check defect escape rate |
| 2 rounds average | Normal, healthy process | Maintain |
| 3+ rounds frequently | Unclear requirements, scope creep, perfectionism | Review process, not code |
| 4+ rounds | Misaligned expectations between author and reviewer | Pair programming may help |

---

## Reviewer Load Balancing

### Load Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Reviews per person per week | Number of PRs reviewed | 5-10 (varies by team size) |
| Review hours per person per week | Time spent reviewing | 4-8 hours (20% of time) |
| Pending review queue | PRs waiting for a specific reviewer | < 3 at any time |
| Review distribution Gini coefficient | Evenness of review distribution | < 0.3 (lower is more even) |

### Detecting Imbalances

```sql
-- Review distribution across team members (last 30 days)
SELECT
  reviewer.name,
  COUNT(DISTINCT pr.id) AS reviews_completed,
  AVG(EXTRACT(EPOCH FROM (
    review.submitted_at - pr.review_requested_at
  )) / 3600) AS avg_hours_to_review
FROM reviews review
JOIN pull_requests pr ON review.pr_id = pr.id
JOIN users reviewer ON review.reviewer_id = reviewer.id
WHERE review.submitted_at > NOW() - INTERVAL '30 days'
GROUP BY reviewer.name
ORDER BY reviews_completed DESC;
```

### Healthy Distribution Indicators

```text
Team of 8 engineers, 40 PRs/week:

Healthy:
  Alice:   6 reviews  (15%)
  Bob:     5 reviews  (12.5%)
  Carol:   5 reviews  (12.5%)
  Dave:    5 reviews  (12.5%)
  Eve:     5 reviews  (12.5%)
  Frank:   5 reviews  (12.5%)
  Grace:   5 reviews  (12.5%)
  Hank:    4 reviews  (10%)

Unhealthy:
  Alice:  15 reviews  (37.5%)  -- Bottleneck
  Bob:     8 reviews  (20%)
  Carol:   7 reviews  (17.5%)
  Dave:    5 reviews  (12.5%)
  Eve:     3 reviews  (7.5%)
  Frank:   1 review   (2.5%)
  Grace:   1 review   (2.5%)
  Hank:    0 reviews  (0%)     -- Not reviewing at all
```

---

## DORA Metrics Intersection

### How Review Practices Affect DORA

| DORA Metric | Review Impact |
|-------------|---------------|
| **Deployment Frequency** | Long review cycles reduce deploy frequency; smaller PRs with faster review enable daily deploys |
| **Lead Time for Changes** | Review turnaround is often the largest component of lead time; TTFR and TTA directly affect this |
| **Change Failure Rate** | Thorough reviews reduce post-deploy failures; measure defect escape rate |
| **Mean Time to Recovery** | Fast review of hotfix PRs (P0 SLA) directly affects MTTR |

### Correlating Review Metrics with DORA

```text
Track monthly:
  Review turnaround (P50, P90) vs Lead Time for Changes
  Defect escape rate vs Change Failure Rate
  P0 review SLA compliance vs Mean Time to Recovery
  PR throughput vs Deployment Frequency
```

### The Review Bottleneck Signal

If lead time is high but coding time is low, review is likely the bottleneck:

```text
Total Lead Time: 5 days
  - Coding time:     1 day   (20%)
  - Review wait:     3 days  (60%)  <-- Bottleneck
  - CI + merge:      0.5 day (10%)
  - Deploy wait:     0.5 day (10%)
```

Focus improvement efforts on review turnaround when this pattern appears.

---

## Avoiding Gaming and Perverse Incentives

### Common Gaming Patterns

| Metric | Gaming Behavior | Why It Is Harmful |
|--------|----------------|-------------------|
| TTFR | Quick "I'll look later" comment | Inflates response time without actual review |
| Comments per PR | Adding trivial nit comments | Wastes author time, does not improve quality |
| Approval speed | Rubber-stamping to hit SLA | Defects escape to production |
| Reviews per week | Claiming reviews done by bots/auto-approve | Misrepresents actual review effort |
| Defect escape rate | Not filing bugs found post-merge | Hides real quality signal |

### Principles for Healthy Metrics

1. **Measure for diagnosis, not performance evaluation**. Review metrics should inform process improvement, not individual performance reviews.

2. **Use composite indicators, not single metrics**. Fast reviews are only good if the defect escape rate is also low. Track both together.

3. **Track trends, not absolutes**. A team with 6-hour TTFR improving to 4-hour is healthier than a team at 2-hour TTFR that is rubber-stamping.

4. **Make metrics visible but not punitive**. Display team dashboards. Do not rank individuals or tie metrics to bonuses.

5. **Periodically audit the metrics**. Spot-check that low TTFR corresponds to substantive first comments. Verify that low escape rate is not hiding unfiled bugs.

### Suggested Composite Health Score

```text
Review Health Score = weighted average of:
  - TTFR P90 < SLA:           30% weight
  - Defect escape rate < 20%: 30% weight
  - Review rounds <= 2 avg:   20% weight
  - Load balance Gini < 0.3:  10% weight
  - Abandonment rate < 5%:    10% weight

Score interpretation:
  0.8-1.0: Excellent review process
  0.6-0.8: Good, minor improvements possible
  0.4-0.6: Needs attention in specific areas
  < 0.4:   Significant process issues
```

---

## Dashboard Design

### Team-Level Dashboard

```text
+--------------------------------------------------+
|  CODE REVIEW HEALTH - January 2026               |
+--------------------------------------------------+
|                                                    |
|  TURNAROUND              QUALITY                  |
|  TTFR (P50): 2.3h       Escape Rate: 18%         |
|  TTFR (P90): 7.1h       Comments/PR: 3.2 avg     |
|  TTA  (P50): 18.4h      Quality ratio: 0.62      |
|                                                    |
|  THROUGHPUT              BALANCE                   |
|  PRs merged: 142/mo     Gini coeff: 0.24          |
|  Avg rounds: 1.8        Max queue: 4 PRs          |
|  Abandon rate: 3.2%     Overloaded: 0 people      |
|                                                    |
|  TRENDS (12 weeks)                                |
|  TTFR:    Improving                                |
|  Escapes: Improving                                |
|  Load:    Stabilized                               |
+--------------------------------------------------+
```

### Key Dashboard Components

| Panel | Metrics | Visualization |
|-------|---------|---------------|
| Turnaround | TTFR, TTA, TTM (P50 and P90) | Time series + gauge |
| Quality | Defect escape rate, quality ratio | Percentage + trend |
| Throughput | PRs merged, avg iterations | Counter + bar chart |
| Balance | Review distribution, queue depth | Heatmap + bar chart |
| SLA compliance | % of PRs within SLA by priority | Stacked bar chart |
| Trends | All metrics over 12 weeks | Sparklines |

### Data Sources

| Platform | API for Metrics |
|----------|----------------|
| GitHub | GraphQL API (pullRequests, reviews, comments) |
| GitLab | REST API (/merge_requests, /approvals) |
| Bitbucket | REST API (/pullrequests, /activity) |
| Graphite | CLI + API for stack metrics |
| LinearB | Built-in engineering metrics |
| Swarmia | Built-in review analytics |
| Jellyfish | Engineering management platform |

---

## Implementation Guide

### Phase 1: Baseline (Week 1-2)

1. Start collecting TTFR and TTA from your Git platform API
2. Calculate current review distribution across team
3. Establish current defect escape rate (review last month's bugs)
4. Set initial targets based on baseline (improve by 20%)

### Phase 2: Visibility (Week 3-4)

1. Build a simple dashboard (Grafana, Datadog, or spreadsheet)
2. Share with team in sprint retrospective
3. Discuss the numbers without assigning blame
4. Identify one area to improve

### Phase 3: Process Improvement (Month 2)

1. Implement changes based on metrics (reviewer rotation, PR size limits)
2. Track metrics weekly
3. Adjust targets as the team improves
4. Add review SLAs to team agreements

### Phase 4: Continuous Monitoring (Ongoing)

1. Automate data collection (scheduled scripts or engineering platform)
2. Set up alerts for anomalies (TTFR P90 > 24 hours, escape rate spike)
3. Monthly review of composite health score
4. Quarterly target adjustment

### GitHub Actions Metric Collection

```yaml
# .github/workflows/review-metrics.yml
name: Review Metrics
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
  workflow_dispatch:

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Collect PR metrics
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh api graphql -f query='
            query {
              repository(owner: "org", name: "repo") {
                pullRequests(last: 50, states: MERGED) {
                  nodes {
                    createdAt
                    mergedAt
                    reviews(first: 10) {
                      nodes {
                        createdAt
                        state
                        author { login }
                      }
                    }
                    comments { totalCount }
                    additions
                    deletions
                  }
                }
              }
            }
          ' > metrics.json
```

---

## Anti-Patterns

### 1. Metrics Without Context

**Problem**: Presenting raw numbers without explaining what they mean or what is actionable.

**Fix**: Always pair metrics with interpretation and recommended actions.

### 2. Individual Leaderboards

**Problem**: Ranking reviewers by speed or volume, creating competition instead of collaboration.

**Fix**: Show team-level metrics only. Use individual data privately for coaching, not public ranking.

### 3. Optimizing One Metric at the Expense of Others

**Problem**: Pushing TTFR down to 30 minutes but defect escape rate doubles because reviews are superficial.

**Fix**: Use composite health scores. Improvements must not degrade other metrics.

### 4. Measuring What Is Easy, Not What Matters

**Problem**: Tracking comments per PR (easy to count) but ignoring whether those comments catch real bugs.

**Fix**: Invest in categorizing review comments and tracking escape rate, even though they require more effort.

### 5. Setting Targets Too Aggressively

**Problem**: Setting 1-hour TTFR as a target when the team averages 8 hours, causing stress and gaming.

**Fix**: Set targets at 20% improvement from baseline. Ratchet down gradually over quarters.

---

## Cross-References

- [operational-playbook.md](operational-playbook.md) -- SLA definitions and priority matrix
- [large-pr-review-strategies.md](large-pr-review-strategies.md) -- PR size impact on review effectiveness
- [automation-tools.md](automation-tools.md) -- Tools for automating metric collection
- [psychological-safety-guide.md](psychological-safety-guide.md) -- Presenting metrics without blame
- [../../software-clean-code-standard/references/clean-code-standard.md](../../software-clean-code-standard/references/clean-code-standard.md) -- Quality standards that reviews enforce
