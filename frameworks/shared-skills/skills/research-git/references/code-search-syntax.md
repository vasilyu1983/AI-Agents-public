# Code Search Syntax

GitHub code search (powered by Blackbird) qualifiers, `gh search code` CLI equivalents, rate-limit budget strategy, and ready-to-run example queries mapped to Modes A/B/C.

## Table of Contents

- [Qualifiers](#qualifiers)
- [Boolean Operators](#boolean-operators)
- [gh search code CLI](#gh-search-code-cli)
- [Rate-Limit Budget Strategy](#rate-limit-budget-strategy)
- [Example Queries by Mode](#example-queries-by-mode)

## Qualifiers

| Qualifier | Effect | Example |
|-----------|--------|---------|
| `repo:<owner>/<repo>` | Restrict to one repository | `repo:anthropics/claude-code content:"SKILL.md"` |
| `org:<org>` | Restrict to all repos in an org | `org:vercel language:TypeScript path:tsconfig.json` |
| `path:<glob>` | Match on file path (glob OK) | `path:.github/workflows` |
| `language:<lang>` | Filter by detected language | `language:YAML` |
| `extension:<ext>` | Filter by file extension | `extension:toml` |
| `filename:<name>` | Match exact filename | `filename:SKILL.md` |
| `symbol:<name>` | Match a code symbol (function/class) | `symbol:runWorkflow language:TypeScript` |
| `/<regex>/` | Regex in content search | `/uses:\s*"softprops\/action-gh-release"/ language:YAML` |
| `NOT <term>` | Exclude term | `content:"SKILL.md" NOT archived:true` |

Qualifiers compose: all listed on one line are AND-joined unless `OR` / `NOT` is explicit.

Note: `content:` is the default qualifier when no qualifier precedes a bare term. Both forms are valid: `content:"SKILL.md"` and `"SKILL.md"`.

## Boolean Operators

```
# AND (implicit — just space between terms)
path:.github/workflows language:YAML uses: "googleapis/release-please-action"

# OR — must be uppercase; wrap in parentheses for clarity
(language:TypeScript OR language:JavaScript) filename:tsconfig.json

# NOT — uppercase
filename:SKILL.md NOT path:.archive

# Parentheses group sub-expressions
(org:vercel OR org:nrwl) path:.github/workflows language:YAML
```

## gh search code CLI

```bash
# Basic: search by content query across GitHub
gh search code "SKILL.md" --limit 30

# With qualifiers passed as --qualifier flags
gh search code "SKILL.md" \
  --qualifier "path:/" \
  --qualifier "language:Markdown" \
  --limit 30

# Restrict to a single repo
gh search code "pushedAt" \
  --qualifier "repo:anthropics/claude-code" \
  --limit 20

# Code search in an org
gh search code "uses:" \
  --qualifier "org:vercel" \
  --qualifier "path:.github/workflows" \
  --qualifier "language:YAML" \
  --limit 30

# JSON output for piping
gh search code "SKILL.md" --qualifier "language:Markdown" \
  --json path,repository,url --limit 30 | jq '.[] | .repository.fullName'
```

Note: `gh search code` forwards qualifiers to the GitHub Search API — the same Blackbird engine as the web UI. The `--qualifier` flag maps directly to qualifier strings.

## Rate-Limit Budget Strategy

GitHub's Search REST API has two different limits, both **separate from and much lower than** the 5,000 req/hr core REST budget (verified against docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api, 2026-07-11):

- **Code search specifically**: **9 requests per minute** for authenticated users — the tightest limit in the whole API surface.
- **All other search endpoints** (repo search, issue search, user search): **30 requests per minute** for authenticated users.

`gh search code` and the GraphQL `search(type: CODE, ...)` connection both draw from the 9 req/min code-search budget; `gh search repos` draws from the 30 req/min general-search budget. Don't conflate the two when budgeting a scan.

Batching rules to stay within budget:

1. **One wide query, local filter** — prefer a single broad query (`filename:SKILL.md language:Markdown`) over many narrow queries (`filename:SKILL.md language:Markdown path:/`, then `filename:SKILL.md language:Markdown path:references/`, ...). Fetch up to the page limit (up to 100 results) and filter client-side with `jq`.
2. **Never parallelize code search calls** — even two concurrent calls will collide against the 9 req/min window.
3. **Pause between pages** — when paginating (e.g. `--limit 100` + offset), add a `sleep 7` between pages to stay under 9 req/min (repo/issue search can tolerate a shorter `sleep 2` under the 30 req/min budget).
4. **Prefer GraphQL for repo-level filtering** — use a GraphQL `search` connection to narrow to candidate repos first, then run one targeted code search per candidate repo with `repo:<owner>/<repo>`.
5. **Cache results locally** — write raw JSON output to `docs/research/<scan-id>/raw/code-search-<query-slug>.json` so re-runs skip the API call.

## Example Queries by Mode

### Mode A — Skill Ecosystem Scan

```bash
# Find repos with SKILL.md at root or in subdirectories
gh search code "SKILL.md" \
  --qualifier "path:/" \
  --qualifier "language:Markdown" \
  --limit 100 \
  --json path,repository,url

# Find repos with a references/ directory alongside SKILL.md
gh search code "references" \
  --qualifier "filename:SKILL.md" \
  --limit 50 \
  --json repository,url

# Find skills for a specific domain (kafka)
gh search code "kafka" \
  --qualifier "filename:SKILL.md" \
  --qualifier "language:Markdown" \
  --limit 30 \
  --json path,repository,url

# Find skills that link to a known skill by name (cross-skill references)
gh search code "software-kafka" \
  --qualifier "filename:SKILL.md" \
  --limit 30
```

### Mode B — OSS Practice Harvest

```bash
# Find workflows using a specific action
gh search code 'uses: "softprops/action-gh-release"' \
  --qualifier "path:.github/workflows" \
  --qualifier "language:YAML" \
  --limit 50 \
  --json path,repository,url

# Find repos using merge-queue configuration
gh search code "merge_group:" \
  --qualifier "path:.github/workflows" \
  --qualifier "language:YAML" \
  --limit 40

# Find CODEOWNERS patterns for a specific team structure
gh search code "@platform-team" \
  --qualifier "filename:CODEOWNERS" \
  --limit 30

# Find release-please configuration
gh search code "release-type:" \
  --qualifier "filename:release-please-config.json" \
  --limit 30 \
  --json path,repository,url
```

### Mode C — Code Idiom Extraction

```bash
# Find tsconfig.json with strict mode patterns
gh search code '"strict": true' \
  --qualifier "filename:tsconfig.json" \
  --qualifier "language:JSON" \
  --limit 50

# Find ruff.toml configuration across high-signal Python repos
gh search code "[tool.ruff]" \
  --qualifier "filename:ruff.toml" \
  --limit 40 \
  --json path,repository,url

# Find cargo workspace configuration patterns
gh search code '[workspace]' \
  --qualifier "filename:Cargo.toml" \
  --qualifier "language:TOML" \
  --limit 40

# Find React Query cache configuration idioms
gh search code "staleTime" \
  --qualifier "language:TypeScript" \
  --qualifier "path:src" \
  --limit 30
```
