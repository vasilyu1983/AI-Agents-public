# GraphQL Triage

Single-repo health queries, batch-alias patterns, repo discovery via `search` connection, and `gh api graphql` invocation. Replaces ~150 REST calls with 1 GraphQL request for 30-repo triage; that request is billed in GraphQL points, not REST calls (see the rate-limit note at the end).

## Table of Contents

- [REST vs GraphQL Cost](#rest-vs-graphql-cost)
- [Single-Repo Health Query](#single-repo-health-query)
- [Batch-Alias Pattern (5-10 repos)](#batch-alias-pattern-5-10-repos)
- [Repo Discovery via search Connection](#repo-discovery-via-search-connection)
- [Invocation with gh api graphql](#invocation-with-gh-api-graphql)

## REST vs GraphQL Cost

Triaging 30 repos with REST:

```
Per-repo REST calls:
  GET /repos/{owner}/{repo}           → 1 call (stargazerCount, forkCount, pushedAt, license)
  GET /repos/{owner}/{repo}/contents/.github/CODEOWNERS → 1 call
  GET /repos/{owner}/{repo}/issues?state=open&per_page=1 → 1 call
  GET /repos/{owner}/{repo}/pulls?state=open&per_page=1  → 1 call
  GET /repos/{owner}/{repo}/issues?state=closed&per_page=1 → 1 call
  ─────────────────────────────────────────────────────────────────
  5 calls × 30 repos = 150 REST calls against the core REST budget
```

Triaging 30 repos with GraphQL batch-alias: **1 request**, costed in GraphQL points (a separate budget from REST; see the rate-limit note below). Ask for `rateLimit { cost remaining }` in the same query to see what it charged.

Use GraphQL when triaging 5+ repos in a single research session.

## Single-Repo Health Query

```graphql
query RepoHealth($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    stargazerCount
    forkCount
    pushedAt
    licenseInfo {
      spdxId
      name
    }
    openIssues: issues(states: OPEN) {
      totalCount
    }
    closedIssues: issues(states: CLOSED) {
      totalCount
    }
    openPRs: pullRequests(states: OPEN) {
      totalCount
    }
    codeowners: object(expression: "HEAD:.github/CODEOWNERS") {
      ... on Blob {
        text
      }
    }
  }
}
```

```bash
gh api graphql -f query='
query RepoHealth($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    stargazerCount
    forkCount
    pushedAt
    licenseInfo { spdxId }
    openIssues: issues(states: OPEN) { totalCount }
    closedIssues: issues(states: CLOSED) { totalCount }
    openPRs: pullRequests(states: OPEN) { totalCount }
    codeowners: object(expression: "HEAD:.github/CODEOWNERS") {
      ... on Blob { text }
    }
  }
}' -f owner="vercel" -f name="next.js" \
  | jq '.data.repository | {stars: .stargazerCount, forks: .forkCount, pushed: .pushedAt, license: .licenseInfo.spdxId}'
```

## Batch-Alias Pattern (5-10 repos)

Use GraphQL aliases to triage multiple repos in one call. Each alias is an independent field on the root `query`.

```graphql
query BatchTriage {
  repo1: repository(owner: "vercel", name: "next.js") {
    stargazerCount
    forkCount
    pushedAt
    licenseInfo { spdxId }
    openIssues: issues(states: OPEN) { totalCount }
    closedIssues: issues(states: CLOSED) { totalCount }
    openPRs: pullRequests(states: OPEN) { totalCount }
    codeowners: object(expression: "HEAD:.github/CODEOWNERS") {
      ... on Blob { text }
    }
  }
  repo2: repository(owner: "nrwl", name: "nx") {
    stargazerCount
    forkCount
    pushedAt
    licenseInfo { spdxId }
    openIssues: issues(states: OPEN) { totalCount }
    closedIssues: issues(states: CLOSED) { totalCount }
    openPRs: pullRequests(states: OPEN) { totalCount }
    codeowners: object(expression: "HEAD:.github/CODEOWNERS") {
      ... on Blob { text }
    }
  }
  # Add repo3...repo10 following the same alias pattern
}
```

```bash
# Save query to a file for readability, then invoke. --input would send the raw
# file as the HTTP body, which GraphQL rejects; -F query=@file wraps it as JSON:
gh api graphql -F query=@batch_triage.graphql \
  | jq '.data | to_entries[] | {
      repo: .key,
      stars: .value.stargazerCount,
      forks: .value.forkCount,
      pushed: .value.pushedAt,
      license: .value.licenseInfo.spdxId,
      openIssues: .value.openIssues.totalCount,
      closedIssues: .value.closedIssues.totalCount,
      openPRs: .value.openPRs.totalCount,
      hasCODEOWNERS: (.value.codeowners != null)
    }'
```

Inline version for up to 5 repos:

```bash
gh api graphql -f query='
{
  r1: repository(owner:"anthropics", name:"claude-code") {
    stargazerCount forkCount pushedAt
    licenseInfo { spdxId }
    openIssues: issues(states:OPEN) { totalCount }
    codeowners: object(expression:"HEAD:.github/CODEOWNERS") { ... on Blob { text } }
  }
  r2: repository(owner:"vercel", name:"ai") {
    stargazerCount forkCount pushedAt
    licenseInfo { spdxId }
    openIssues: issues(states:OPEN) { totalCount }
    codeowners: object(expression:"HEAD:.github/CODEOWNERS") { ... on Blob { text } }
  }
}' | jq '.data'
```

## Repo Discovery via search Connection

Use the GraphQL `search` connection to discover repos matching a query, with health signals in one call — avoiding a separate REST search + batch-health pattern.

```graphql
query DiscoverRepos($query: String!, $count: Int!) {
  search(query: $query, type: REPOSITORY, first: $count) {
    repositoryCount
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
        forkCount
        pushedAt
        isArchived
        licenseInfo { spdxId }
        openIssues: issues(states: OPEN) { totalCount }
        openPRs: pullRequests(states: OPEN) { totalCount }
        description
        url
      }
    }
  }
}
```

```bash
gh api graphql \
  -f query='query DiscoverRepos($q: String!, $count: Int!) {
    search(query: $q, type: REPOSITORY, first: $count) {
      repositoryCount
      nodes {
        ... on Repository {
          nameWithOwner
          stargazerCount
          forkCount
          pushedAt
          isArchived
          licenseInfo { spdxId }
          openIssues: issues(states: OPEN) { totalCount }
          description
        }
      }
    }
  }' \
  -f q="topic:claude-skills stars:>100 archived:false" \
  -F count=20 \
  | jq '.data.search.nodes[] | select(.isArchived == false) | {
      repo: .nameWithOwner,
      stars: .stargazerCount,
      forks: .forkCount,
      pushed: .pushedAt,
      license: .licenseInfo.spdxId
    }' | jq -s 'sort_by(.stars) | reverse'
```

Common discovery queries for research-git modes:

```bash
# Mode A: skill repos
"topic:claude-skills stars:>100 archived:false"
"topic:codex-skills stars:>50 archived:false"
# (filename:/path: are code-search qualifiers; the REPOSITORY search connection ignores them —
#  discover skill repos by topic here, then confirm SKILL.md with gh search code --repo)

# Set SINCE relative to today, e.g. 180 days back:
#   SINCE=$(python3 -c 'import datetime as d; print(d.date.today() - d.timedelta(days=180))')
# Mode B: practice repos
"monorepo stars:>1000 archived:false pushed:>$SINCE"
"topic:github-actions stars:>500 archived:false"

# Mode C: code pattern repos
"language:TypeScript stars:>2000 pushed:>$SINCE archived:false"
```

## Invocation with gh api graphql

```bash
# Inline query with -f flag
gh api graphql -f query='{ viewer { login } }'

# Multi-variable query with -f (string) and -F (typed: int/bool)
gh api graphql \
  -f query='query($owner:String!, $name:String!, $n:Int!) {
    repository(owner:$owner, name:$name) {
      issues(first:$n, states:OPEN) { totalCount nodes { title } }
    }
  }' \
  -f owner="vercel" \
  -f name="next.js" \
  -F n=5

# Read query from file (cleaner for multi-repo batch queries).
# `-F query=@file` reads the file into the "query" field; `--input file` would
# send the raw text as the request body, which the GraphQL endpoint rejects.
gh api graphql -F query=@my_query.graphql

# Paginate with cursor (for >100 results)
gh api graphql -f query='
  query($cursor: String) {
    search(query:"topic:claude-skills", type:REPOSITORY, first:100, after:$cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { ... on Repository { nameWithOwner stargazerCount } }
    }
  }' -f cursor="" \
  | jq '.data.search'

# Response path shortcut: --jq extracts without piping to jq
gh api graphql -f query='{ viewer { login } }' \
  --jq '.data.viewer.login'
```

Rate-limit note: GraphQL has its own primary limit, separate from the REST core and search budgets, and it is measured in points per hour, not requests. A query's cost is computed from the connections it has to resolve (each aliased repo and each nested connection adds to it; the documented minimum is 1 point per call), so a 30-alias batch is cheaper than 150 REST calls but is not "1 unit". Source: <https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api>. Before a large triage, read the budget instead of assuming it:

```bash
gh api graphql -f query='{ rateLimit { limit cost remaining resetAt } }'
gh api rate_limit --jq '.resources.graphql'
```

Add `rateLimit { cost }` to any batch query to record what it charged, and keep batches to the 5-10 aliases shown above unless the recorded cost leaves room.
