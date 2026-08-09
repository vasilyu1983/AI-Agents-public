# GraphQL Triage

Single-repo health queries, batch-alias patterns, repo discovery via `search` connection, and `gh api graphql` invocation. Replaces ~150 REST calls with 1 GraphQL call for 30-repo triage.

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
  5 calls × 30 repos = 150 REST calls, consuming ~3% of the 5,000/hr budget
```

Triaging 30 repos with GraphQL batch-alias: **1 request**.

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
# Save query to a file for readability, then invoke:
gh api graphql --input batch_triage.graphql \
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
    }' | sort_by(.stars) | reverse
```

Common discovery queries for research-git modes:

```bash
# Mode A: skill repos
"topic:claude-skills stars:>100 archived:false"
"topic:codex-skills stars:>50 archived:false"
"filename:SKILL.md language:Markdown stars:>200"

# Mode B: practice repos
"monorepo stars:>1000 archived:false pushed:>2026-01-01"
"topic:github-actions stars:>500 archived:false"

# Mode C: code pattern repos
"language:TypeScript stars:>2000 pushed:>2026-01-01 archived:false"
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

# Read query from file (cleaner for multi-repo batch queries)
gh api graphql --input my_query.graphql

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

Rate-limit note: GraphQL calls count against the REST 5,000 req/hr budget (1 call per request, regardless of how many repos are aliased). This makes batch-alias extremely cost-efficient — 30 repos in one call vs 150+ REST calls.
