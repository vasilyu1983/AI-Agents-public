# Extraction Protocol

## Table of Contents

- [Mode-Aware Defaults](#mode-aware-defaults)
- [Step-by-Step (Mode A — Skill)](#step-by-step-mode-a--skill)
- [Deep Mode (Opt-In)](#deep-mode-opt-in)
- [Edge Cases](#edge-cases)
- [Common Extraction Mistakes](#common-extraction-mistakes)

How to fetch only the assets you need from a target repo, without cloning the whole thing. Use `scripts/fetch_repo_assets.sh <owner>/<repo> <out> --kind <skill|practice|code>` — it applies the per-mode defaults below.

## Mode-Aware Defaults

| Mode | Default assets | Skip by default |
|------|----------------|-----------------|
| `skill` | `SKILL.md`, `references/`, `data/sources.json` (if present) | `scripts/`, `assets/`, tests |
| `practice` | `.github/workflows/`, `CODEOWNERS`, `CONTRIBUTING.md`, `SECURITY.md`, PR/issue templates, `docs/adr/`, release config | Source code, tests, assets |
| `code` | Language + lint configs, `scripts/`, `Makefile`, test layout, representative source modules, README | `.github/`, binary assets |

## Step-by-Step (Mode A — Skill)

### 1. Locate SKILL.md

Some repos have SKILL.md at root, others nest it in a named subdirectory (e.g., `swiftui-pro/SKILL.md` in twostraws repos).

```bash
# Find SKILL.md anywhere in the repo
gh api repos/<owner>/<repo>/git/trees/main?recursive=1 \
  --jq '.tree[] | select(.path | endswith("SKILL.md")) | .path'
```

### 2. Fetch SKILL.md content

```bash
gh api repos/<owner>/<repo>/contents/<path-to-SKILL.md> \
  --jq '.content' | base64 -d > out/SKILL.md
```

### 3. List references/ directory

```bash
# Determine the references/ path (may be at root or nested)
gh api repos/<owner>/<repo>/contents/<skill-dir>/references \
  --jq '.[] | .name'
```

### 4. Fetch each reference file

```bash
for ref in $(gh api repos/<owner>/<repo>/contents/<skill-dir>/references --jq '.[] | .name'); do
  gh api "repos/<owner>/<repo>/contents/<skill-dir>/references/$ref" \
    --jq '.content' | base64 -d > "out/references/$ref"
done
```

### 5. Capture metadata

For each fetched repo, store:
- Source URL
- Commit SHA at fetch time (for reproducibility)
- Fetch date
- License (from LICENSE file)
- Star count and last commit date

```bash
# Get current commit SHA
gh api repos/<owner>/<repo>/commits/main --jq '.sha'

# Get license
gh api repos/<owner>/<repo>/license --jq '.license.spdx_id'
```

### 6. Store in audit trail

Save extracted content under:
```
docs/research/<scan-id>/raw/<owner>__<repo>/
  ├── SKILL.md
  ├── references/
  │   └── ...
  └── _metadata.json    # source URL, commit SHA, license, fetch date
```

## Deep Mode (Opt-In)

Only use when the repo has working scripts you want to study:
- `xcode-build-optimization` family (real benchmark scripts)
- Repos with `scripts/` containing executable workflows
- Repos with `schemas/` defining output contracts

```
Additional fetch:
  - scripts/ (especially .sh, .py, .ts files)
  - schemas/ (JSON Schema, YAML schema)
```

Do NOT use deep mode for:
- Repos with hundreds of files (waste of context)
- Repos where the value is in `references/` (most cases)
- Wrapper/aggregator repos

## Edge Cases

### Repos with multiple skills

Some repos bundle multiple skills (e.g., `xcode-build-optimization-agent-skill` has 6 sub-skills). Treat each subdirectory as a separate skill and extract them independently.

### Repos using non-standard paths

Some repos use `swift-concurrency-pro/` or `skill/` instead of `references/`. Use `git/trees` recursive listing to find SKILL.md, then fetch the directory containing it.

### Private repos

This skill does NOT support private repos. If you need to research a private repo, clone it manually first.

### Rate limits

`gh api` is rate-limited (5000 requests/hour authenticated). Each repo extraction uses ~10-20 requests. For bulk scans, batch and pause if you hit the limit. For listings of directory trees, prefer one GraphQL query over many REST calls.

### Practice / Code modes

For Mode B (practice) and Mode C (code), `fetch_repo_assets.sh --kind practice|code` fetches the mode-specific asset set listed in [Mode-Aware Defaults](#mode-aware-defaults). The step-by-step above applies to all modes — only the asset list changes.

## Common Extraction Mistakes

- **Cloning the whole repo** when you only need 5 files
- **Skipping metadata capture** — losing the audit trail
- **Fetching binary assets** (logos, images) that bloat storage
- **Not handling base64 decode errors** for non-text files
- **Assuming SKILL.md is at root** — many repos nest it
