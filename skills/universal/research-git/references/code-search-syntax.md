# Code Search Syntax

Qualifiers that the GitHub code search *API* accepts, `gh search code` CLI equivalents, rate-limit budget strategy, and ready-to-run example queries mapped to Modes A/B/C.

Engine caveat. Before relying on it, run `gh --version` and `gh search code --help` on the machine doing the scan, and read <https://docs.github.com/en/rest/search/search#search-code> and <https://cli.github.com/manual/gh_search_code>; record the version and check date in the scan notes. As of the last check the caveat held: `gh search code` and `GET /search/code` are served by the **legacy** code search engine, not the engine behind the github.com search box. Regex (`/.../`), `symbol:`, `is:archived`, `is:fork`, `content:` and path globs are web-UI-only; through the API they are either rejected or silently treated as plain search terms, so a query built from the web syntax page returns different or no results. Legacy rules from the REST doc: only the default branch is searched, only files under the documented size cap, and the query must contain at least one bare search term (`language:go` alone is invalid; `panic language:go` is valid). The legacy qualifier reference is <https://docs.github.com/en/search-github/searching-on-github/searching-code>. Use the web UI (or `gh search code --web`) when a regex or symbol query is needed, and record that the result came from the UI.

## Table of Contents

- [Qualifiers](#qualifiers)
- [Boolean Operators](#boolean-operators)
- [gh search code CLI](#gh-search-code-cli)
- [Rate-Limit Budget Strategy](#rate-limit-budget-strategy)
- [Example Queries by Mode](#example-queries-by-mode)

## Qualifiers

API (legacy) code-search qualifiers, from <https://docs.github.com/en/search-github/searching-on-github/searching-code>:

| Qualifier | Effect | Example |
|-----------|--------|---------|
| `repo:<owner>/<repo>` | Restrict to one repository | `pushedAt repo:cli/cli` |
| `org:<org>` / `user:<user>` | Restrict to all repos of an org or user | `tsconfig org:vercel language:JSON` |
| `path:<dir>` | Match files in a directory (or `path:/` for repo root); no globs | `SKILL.md path:/` |
| `language:<lang>` | Filter by detected language | `deque language:Python` |
| `extension:<ext>` | Filter by file extension | `ruff extension:toml` |
| `filename:<name>` | Match the filename | `references filename:SKILL.md` |
| `in:file,path` | Search contents, path, or both (default: contents only) | `octocat in:file,path` |
| `size:<n>` | File size in bytes, with range operators | `element language:xml size:>10000` |
| `-<qualifier>` | Exclude a qualifier match | `SKILL.md -path:.archive` |

Qualifiers compose: all listed on one line are AND-joined. Bare terms are matched in file contents unless `in:` says otherwise. `content:`, `symbol:`, `is:` and regex literals are not available here (see the engine caveat above).

## Boolean Operators

Legacy search syntax, from <https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax>:

```
# AND (implicit — just space between terms)
uses: "googleapis/release-please-action" path:.github/workflows language:YAML

# Exclude a keyword: NOT (string keywords only)
SKILL.md NOT deprecated

# Exclude a qualifier: hyphen prefix
filename:SKILL.md -path:.archive
```

`OR` and parentheses are web-UI code-search features; the API-backed search does not document them. Run two queries and merge locally instead.

## gh search code CLI

```bash
# Basic: search by content query across GitHub
gh search code "SKILL.md" --limit 30

# Qualifiers go in the query string, as separate arguments
gh search code "SKILL.md" path:/ language:Markdown --limit 30

# ...or through the native flags gh provides for the common ones
gh search code "pushedAt" --repo cli/cli --limit 20
gh search code "uses:" --owner vercel --language YAML --limit 30
gh search code lint --filename package.json --extension json

# JSON output for piping
gh search code "SKILL.md" --language Markdown \
  --json path,repository,url --limit 30 | jq '.[] | .repository.fullName'
```

Flags seen in `gh search code --help` at the last check: `--extension`, `--filename`, `--language`, `--match {file|path}`, `--owner`, `--repo`, `--size`, `--limit`, `--json`, `--jq`, `--template`, `--web`. There is no `--qualifier` flag; anything else is passed as a raw qualifier in the query. Run `gh --version` and `gh search code --help` before relying on a flag, since the set changes between releases.

## Rate-Limit Budget Strategy

GitHub rate-limits search separately from the core REST budget, and code search has its own, lower limit than repository and issue search. The numbers change, so read them before a scan instead of assuming them:

1. Run `gh api rate_limit --jq '.resources | {search, code_search, core}'`. `code_search` covers `gh search code`; `search` covers `gh search repos` and issue search; neither draws on `core`.
2. Read the published limits at <https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api> and <https://docs.github.com/en/rest/search/search#rate-limit>.
3. Set the scan's pace below the smaller of the two figures, and record the figures and the check date in the scan notes.

Do not assume GraphQL offers an equivalent code-search connection. Don't conflate the two search budgets when planning a scan.

Batching rules to stay within budget:

1. **One wide query, local filter** — prefer a single broad query (`skill filename:SKILL.md language:Markdown`) over many narrow queries (`... path:/`, then `... path:references`, ...). Fetch up to the page limit (up to 100 results) and filter client-side with `jq`.
2. **Never parallelize code search calls** — send them sequentially, at a pace safely below the current `code_search` limit you read in step 1.
3. **Pause between pages** — when paginating (e.g. `--limit 100` + offset), sleep between pages long enough to stay under that pace (60 seconds divided by your per-minute budget). Repo and issue search use the larger `search` budget and can take shorter pauses.
4. **Prefer GraphQL for repo-level filtering** — use a GraphQL `search` connection to narrow to candidate repos first, then run one targeted code search per candidate repo with `repo:<owner>/<repo>`.
5. **Cache results locally** — write raw JSON output to `docs/research/<scan-id>/raw/code-search-<query-slug>.json` so re-runs skip the API call.

## Example Queries by Mode

### Mode A — Skill Ecosystem Scan

```bash
# Find repos with SKILL.md at the repo root (path:/ = root only; drop it for any depth)
gh search code "SKILL.md" path:/ language:Markdown \
  --limit 100 \
  --json path,repository,url

# Find repos with a references/ directory alongside SKILL.md
gh search code "references" filename:SKILL.md \
  --limit 50 \
  --json repository,url

# Find skills for a specific domain (kafka)
gh search code "kafka" filename:SKILL.md language:Markdown \
  --limit 30 \
  --json path,repository,url

# Find skills that link to a known skill by name (cross-skill references)
gh search code "software-kafka" filename:SKILL.md \
  --limit 30
```

### Mode B — OSS Practice Harvest

```bash
# Find workflows using a specific action
gh search code 'uses: "softprops/action-gh-release"' path:.github/workflows language:YAML \
  --limit 50 \
  --json path,repository,url

# Find repos using merge-queue configuration
gh search code "merge_group:" path:.github/workflows language:YAML \
  --limit 40

# Find CODEOWNERS patterns for a specific team structure
gh search code "@platform-team" filename:CODEOWNERS \
  --limit 30

# Find release-please configuration
gh search code "release-type:" filename:release-please-config.json \
  --limit 30 \
  --json path,repository,url
```

### Mode C — Code Idiom Extraction

```bash
# Find tsconfig.json with strict mode patterns
gh search code '"strict": true' filename:tsconfig.json language:JSON \
  --limit 50

# Find ruff.toml configuration across high-signal Python repos
gh search code "[tool.ruff]" filename:pyproject.toml \
  --limit 40 \
  --json path,repository,url

# Find cargo workspace configuration patterns
gh search code '[workspace]' filename:Cargo.toml language:TOML \
  --limit 40

# Find React Query cache configuration idioms
gh search code "staleTime" language:TypeScript path:src \
  --limit 30
```
