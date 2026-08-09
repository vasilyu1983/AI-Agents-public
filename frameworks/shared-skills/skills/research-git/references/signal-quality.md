# Signal Quality

Fake-star and astroturf detection: heuristics, GH Archive queries, contributor account-age checks, and issue/star ratio floors.

## Table of Contents

- [Why Fake Stars Matter](#why-fake-stars-matter)
- [Star/Fork Ratio Heuristic](#starfork-ratio-heuristic)
- [GH Archive Star-Spike Detection](#gh-archive-star-spike-detection)
- [Contributor Account-Age Bulk Check](#contributor-account-age-bulk-check)
- [Issue/Star Ratio Floor](#issuestar-ratio-floor)
- [Combining Signals](#combining-signals)
- [Quick Triage Checklist](#quick-triage-checklist)

## Why Fake Stars Matter

Astroturfed repos skew discovery rankings. In the agent-skill ecosystem (April-June 2026), mutual-follow networks and purchased star packages routinely push low-content repos into the top-20 of `gh search repos --sort stars`. Trusting star count alone wastes extraction budget on zero-signal content.

## Star/Fork Ratio Heuristic

Organic repos accumulate forks as developers clone for contribution or personal use. Astroturfed repos receive stars en masse from accounts that never fork.

Rule of thumb:

```
fork_count > stars * 0.05
```

A repo with 2,000 stars and 120+ forks passes. A repo with 2,000 stars and 8 forks is a red flag.

Check via REST:

```bash
gh api repos/{owner}/{repo} \
  --jq '{stars: .stargazers_count, forks: .forks_count,
         fork_ratio: (.forks_count / (.stargazers_count + 1)),
         threshold: 0.05,
         passes: (.forks_count / (.stargazers_count + 1) >= 0.05)}'
```

Or batch-check with GraphQL (see [graphql-triage.md](graphql-triage.md)):

```bash
# After a batch query, compute ratio in jq:
jq '.data | to_entries[] | {
  repo: .key,
  stars: .value.stargazerCount,
  forks: .value.forkCount,
  fork_ratio: (.value.forkCount / (.value.stargazerCount + 1)),
  passes_fork_floor: (.value.forkCount / (.value.stargazerCount + 1) >= 0.05)
}'
```

Caveat: documentation-only repos and single-file skill repos legitimately have fewer forks. Apply the heuristic to code repos (Mode B/C) and multi-file skill repos (Mode A with scripts/). Single-SKILL.md repos may fail the fork floor without being astroturfed.

## GH Archive Star-Spike Detection

GH Archive ingests the full GitHub event stream into BigQuery (`bigquery-public-data.github_archive_day`). A 2,000-star day with no accompanying `PushEvent` or `IssuesEvent` activity is almost always a purchased-star burst.

BigQuery SQL pattern:

```sql
-- Star events per day for a specific repo
SELECT
  DATE(created_at) AS event_date,
  COUNT(*) AS star_count
FROM `bigquery-public-data.github_archive_day.events_*`
WHERE
  type = 'WatchEvent'
  AND repo.name = 'owner/repo'
  AND _TABLE_SUFFIX BETWEEN '20260101' AND '20260610'
GROUP BY 1
ORDER BY 1;

-- Cross-reference with push activity on the same days
SELECT
  DATE(created_at) AS event_date,
  COUNTIF(type = 'WatchEvent') AS stars,
  COUNTIF(type = 'PushEvent') AS pushes,
  COUNTIF(type = 'IssuesEvent') AS issue_events
FROM `bigquery-public-data.github_archive_day.events_*`
WHERE
  repo.name = 'owner/repo'
  AND _TABLE_SUFFIX BETWEEN '20260101' AND '20260610'
GROUP BY 1
ORDER BY 1;
```

Interpretation:

- A day with `stars > 500` and `pushes = 0` and `issue_events = 0` is a strong astroturf signal.
- A day with `stars > 500` accompanied by a viral HN/Reddit post and matching `IssuesEvent` spikes is likely organic.

Alternative without BigQuery: star-history.com (see `data/sources.json` → `ecosystem_analytics`) plots the star timeline visually. An S-curve is organic; a vertical cliff is purchased.

```bash
# Quick check via OSS Insight (no BigQuery needed)
# ossinsight.io shows star history with natural-language annotations
curl "https://api.ossinsight.io/v1/repos/{owner}/{repo}/stars/history" \
  | jq '.data[] | {date: .date, stars: .delta}'
```

## Contributor Account-Age Bulk Check

Astroturfed star farms often use accounts created in the same month as the star spike. Checking contributor account-age is a strong secondary signal.

```bash
# Fetch top 30 contributors
gh api repos/{owner}/{repo}/contributors \
  --jq '.[].login' | head -30 > /tmp/contributors.txt

# Spot-check 5 random contributors for account creation date
shuf /tmp/contributors.txt | head -5 | while read login; do
  gh api users/"$login" --jq '{login: .login, created_at: .created_at}'
done
```

Red flag: 3+ top contributors with accounts created within 30 days of the star spike.

For bulk checking all contributors:

```bash
gh api repos/{owner}/{repo}/contributors \
  --jq '.[].login' | head -30 | while read login; do
    created=$(gh api users/"$login" --jq '.created_at' 2>/dev/null || echo "unknown")
    echo "$login $created"
done
```

Note: the GitHub contributor list is sorted by commit count, not star count. Check the first 10-15 names (most active committers) plus a random sample from the bottom. If the bottom is full of same-month accounts, the contributor count is inflated.

Rate-limit awareness: each `gh api users/<login>` call costs 1 REST request. For 30 contributors: 30 calls. Cache results; don't re-check a repo within 30 days.

## Issue/Star Ratio Floor

Organic repos accumulate issues as users file bugs and feature requests. Near-zero issue counts on high-star repos indicate fake stars or zero real adoption.

Rule of thumb:

```
(open_issues + closed_issues) / stars >= 0.002
```

That's approximately 1 issue per 500 stars. A repo with 3,000 stars and 4 total issues is a red flag.

```bash
gh api graphql -f query='
{
  repository(owner:"OWNER", name:"REPO") {
    stargazerCount
    openIssues: issues(states:OPEN) { totalCount }
    closedIssues: issues(states:CLOSED) { totalCount }
  }
}' | jq '.data.repository | {
  stars: .stargazerCount,
  total_issues: (.openIssues.totalCount + .closedIssues.totalCount),
  ratio: ((.openIssues.totalCount + .closedIssues.totalCount) / (.stargazerCount + 1)),
  passes_floor: ((.openIssues.totalCount + .closedIssues.totalCount) / (.stargazerCount + 1) >= 0.002)
}'
```

Caveat: repos that disable issues (docs-only repos, mirrors, repos that use Discussions instead) will fail this heuristic. Check whether issues are disabled before flagging.

```bash
gh api repos/{owner}/{repo} --jq '.has_issues'
```

## Combining Signals

No single signal is conclusive. Apply them as a layered triage:

| Signal | Threshold | Weight |
|--------|-----------|--------|
| Fork ratio | `forks > stars * 0.05` | Medium |
| Issue/star ratio | `issues / stars >= 0.002` | Medium |
| Star spike (GH Archive) | No spikes > 500 in a single day without matching activity | High |
| Contributor account age | No 3+ same-month accounts in top contributors | High |
| Commit history pre-2025-09 | Exists with varied content | High |
| Description quality | Specific, not generic AI-written boilerplate | Low |

Disposition:

- 0 red flags → proceed to extraction
- 1 red flag → note it, proceed with caution
- 2+ red flags → skip unless the specific content is irreplaceable; if extracted, note suspicion in research pack

## Quick Triage Checklist

```bash
# Run all checks for one repo in sequence:
OWNER=anthropics
REPO=claude-code

# 1. Fork ratio
gh api repos/$OWNER/$REPO \
  --jq '{stars: .stargazers_count, forks: .forks_count, ratio: (.forks_count / (.stargazers_count+1))}'

# 2. Issue/star ratio (via GraphQL)
gh api graphql -f query="{
  repository(owner:\"$OWNER\", name:\"$REPO\") {
    stargazerCount
    openIssues: issues(states:OPEN) { totalCount }
    closedIssues: issues(states:CLOSED) { totalCount }
  }
}" | jq '.data.repository'

# 3. Spot-check 3 random contributors
gh api repos/$OWNER/$REPO/contributors --jq '.[].login' \
  | shuf | head -3 | while read u; do
    gh api users/$u --jq '{u: .login, created: .created_at}'
  done

# 4. View star history (requires browser or ossinsight.io)
echo "https://ossinsight.io/analyze/$OWNER/$REPO#overview"
echo "https://star-history.com/#$OWNER/$REPO"
```
