#!/usr/bin/env bash
# fetch_repo_assets.sh — fetch mode-specific assets from a GitHub repo without cloning
#
# Usage:
#   ./fetch_repo_assets.sh <owner>/<repo> <output_dir> --kind <skill|practice|code|killer-feature>
#
# Examples:
#   ./fetch_repo_assets.sh twostraws/SwiftUI-Agent-Skill ./docs/research/2026-04-23-skill-ios/raw/ --kind skill
#   ./fetch_repo_assets.sh vercel/next.js          ./docs/research/2026-04-23-practice-pr/raw/ --kind practice
#   ./fetch_repo_assets.sh lingui-js/js-lingui     ./docs/research/2026-04-23-code-i18n/raw/  --kind code
#
# What gets fetched per mode:
#   skill    — SKILL.md, references/, optional scripts/
#   practice — .github/ (workflows, CODEOWNERS, PR/issue templates), CONTRIBUTING.md,
#              SECURITY.md, docs/adr/, release-please/changelog config
#   code     — configs (tsconfig, biome, eslint, ruff, pyproject, Cargo.toml),
#              scripts/ or Makefile, representative source entry, test layout
#   killer-feature — README.md, CHANGELOG.md, docs/, website/, apps/landing/
#                    (contributes oss_clone_focus signal to the bundle's
#                    Killer-Feature Convergence Protocol; see
#                    references/killer-feature-mining.md)
#
# Output structure:
#   <output_dir>/<owner>__<repo>/
#     ├── <asset tree per mode>
#     └── _metadata.json    # repo, url, commit_sha, license, stars, mode, fetched_at
#
# Requires: gh CLI authenticated, jq, base64, curl

set -euo pipefail

if [[ $# -lt 2 ]]; then
    sed -n '2,22p' "$0" | sed 's/^# \?//'
    exit 1
fi

REPO="$1"
OUT_BASE="$2"
shift 2
KIND="skill"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --kind) KIND="${2:?--kind requires a value}"; shift 2 ;;
        *) echo "ERROR: unknown arg: $1" >&2; exit 1 ;;
    esac
done

case "$KIND" in
    skill|practice|code|killer-feature) ;;
    *) echo "ERROR: --kind must be one of: skill, practice, code, killer-feature" >&2; exit 1 ;;
esac

if [[ ! "$REPO" =~ ^[^/]+/[^/]+$ ]]; then
    echo "ERROR: repo must be in <owner>/<repo> format" >&2
    exit 1
fi

if ! command -v gh &> /dev/null; then echo "ERROR: gh CLI not found" >&2; exit 1; fi
if ! command -v jq &> /dev/null; then echo "ERROR: jq not found" >&2; exit 1; fi

OWNER="${REPO%/*}"
NAME="${REPO#*/}"
OUT_DIR="${OUT_BASE%/}/${OWNER}__${NAME}"
mkdir -p "$OUT_DIR"

echo "Fetching $REPO → $OUT_DIR (mode: $KIND)"

META=$(gh api "repos/$REPO" 2>/dev/null) || {
    echo "ERROR: cannot access $REPO (does it exist? are you authenticated?)" >&2
    exit 1
}

LICENSE=$(echo "$META" | jq -r '.license.spdx_id // "UNKNOWN"')
STARS=$(echo "$META" | jq -r '.stargazers_count')
UPDATED=$(echo "$META" | jq -r '.updated_at')
DESC=$(echo "$META" | jq -r '.description // ""')
DEFAULT_BRANCH=$(echo "$META" | jq -r '.default_branch')
ARCHIVED=$(echo "$META" | jq -r '.archived')
IS_FORK=$(echo "$META" | jq -r '.fork')

echo "  license: $LICENSE | stars: $STARS | branch: $DEFAULT_BRANCH | archived: $ARCHIVED | fork: $IS_FORK"

if [[ "$ARCHIVED" == "true" ]]; then
    echo "  ⚠ WARNING: repo is ARCHIVED — patterns may be stale" >&2
fi
if [[ "$IS_FORK" == "true" ]]; then
    echo "  ⚠ WARNING: repo is a FORK — consider extracting from upstream instead" >&2
fi

case "$LICENSE" in
    MIT|Apache-2.0|BSD-2-Clause|BSD-3-Clause|CC-BY-4.0|CC0-1.0|Unlicense|ISC)
        echo "  ✓ license safe for extraction" ;;
    GPL-2.0|GPL-3.0|AGPL-3.0|CC-BY-SA-4.0)
        echo "  ⚠ WARNING: $LICENSE is viral/copyleft — review before extracting" >&2 ;;
    UNKNOWN|"")
        echo "  ⚠ WARNING: license unknown — review LICENSE file manually before extracting" >&2 ;;
    *)
        echo "  ⚠ WARNING: $LICENSE — verify before extracting" >&2 ;;
esac

SHA=$(gh api "repos/$REPO/commits/$DEFAULT_BRANCH" --jq '.sha' 2>/dev/null)
echo "  commit: $SHA"

# Fetch a path (file or directory) from the repo. Directories are fetched recursively.
# Args: <repo-path> <local-target-dir-or-file>
fetch_path() {
    local rpath="$1"
    local ltarget="$2"
    local entry type
    entry=$(gh api "repos/$REPO/contents/$rpath?ref=$SHA" 2>/dev/null || echo "")
    [[ -z "$entry" ]] && return 1
    # Array = directory; object = file
    if [[ "$(echo "$entry" | jq -r 'type')" == "array" ]]; then
        mkdir -p "$ltarget"
        echo "$entry" | jq -c '.[]' | while IFS= read -r item; do
            type=$(echo "$item" | jq -r '.type')
            local name; name=$(echo "$item" | jq -r '.name')
            case "$type" in
                file) fetch_file "$rpath/$name" "$ltarget/$name" ;;
                dir)  fetch_path "$rpath/$name" "$ltarget/$name" || true ;;
            esac
        done
    else
        fetch_file "$rpath" "$ltarget"
    fi
}

# base64 decode flag differs by platform: GNU coreutils uses --decode/-d,
# BSD/macOS uses -D and rejects --decode. Detect once rather than in-pipe
# (an in-pipe fallback would consume stdin on the first failed attempt).
if printf '' | base64 --decode >/dev/null 2>&1; then
    B64_DECODE=(base64 --decode)
else
    B64_DECODE=(base64 -D)
fi

fetch_file() {
    local rpath="$1"
    local ltarget="$2"
    mkdir -p "$(dirname "$ltarget")"
    gh api "repos/$REPO/contents/$rpath?ref=$SHA" --jq '.content' 2>/dev/null \
        | "${B64_DECODE[@]}" > "$ltarget" 2>/dev/null \
        && echo "    ✓ $rpath" \
        || echo "    ✗ $rpath (failed)"
}

# Best-effort fetch: ignore misses rather than failing
try_fetch() { fetch_path "$1" "$2" 2>/dev/null || echo "    · $1 (not present)"; }

case "$KIND" in
    skill)
        mkdir -p "$OUT_DIR/references"
        echo "  searching for SKILL.md..."
        SKILL_PATHS=$(gh api "repos/$REPO/git/trees/$SHA?recursive=1" \
            --jq '.tree[] | select(.path | endswith("SKILL.md") or endswith("skill.md")) | .path' 2>/dev/null || true)
        SKILL_PATH=$(echo "$SKILL_PATHS" | head -1)
        if [[ -n "$SKILL_PATH" ]]; then
            echo "  fetching $SKILL_PATH..."
            fetch_file "$SKILL_PATH" "$OUT_DIR/SKILL.md"
            SKILL_DIR=$(dirname "$SKILL_PATH")
            REF_DIR="${SKILL_DIR}/references"
            [[ "$SKILL_DIR" == "." ]] && REF_DIR="references"
            try_fetch "$REF_DIR" "$OUT_DIR/references"
        else
            echo "  ⚠ No SKILL.md found"
        fi
        ;;
    practice)
        echo "  fetching practice-scan targets..."
        try_fetch ".github/workflows"       "$OUT_DIR/.github/workflows"
        try_fetch ".github/PULL_REQUEST_TEMPLATE.md" "$OUT_DIR/.github/PULL_REQUEST_TEMPLATE.md"
        try_fetch ".github/ISSUE_TEMPLATE"  "$OUT_DIR/.github/ISSUE_TEMPLATE"
        try_fetch "CODEOWNERS"              "$OUT_DIR/CODEOWNERS"
        try_fetch ".github/CODEOWNERS"      "$OUT_DIR/.github/CODEOWNERS"
        try_fetch "CONTRIBUTING.md"         "$OUT_DIR/CONTRIBUTING.md"
        try_fetch "SECURITY.md"             "$OUT_DIR/SECURITY.md"
        try_fetch "docs/adr"                "$OUT_DIR/docs/adr"
        try_fetch "release-please-config.json" "$OUT_DIR/release-please-config.json"
        try_fetch ".changeset"              "$OUT_DIR/.changeset"
        ;;
    killer-feature)
        echo "  fetching killer-feature (oss_clone_focus) targets..."
        try_fetch "README.md"        "$OUT_DIR/README.md"
        try_fetch "CHANGELOG.md"     "$OUT_DIR/CHANGELOG.md"
        try_fetch "docs"             "$OUT_DIR/docs"
        try_fetch "website"          "$OUT_DIR/website"
        try_fetch "apps/landing"     "$OUT_DIR/apps/landing"
        try_fetch "apps/web"         "$OUT_DIR/apps/web"
        # Manifest helpful for feature-flag enumeration
        for f in package.json Cargo.toml pyproject.toml go.mod; do
            try_fetch "$f" "$OUT_DIR/$f"
        done
        echo "  next: feed README.md + landing pages to LLM prompts §1/§2 in"
        echo "        references/killer-feature-mining.md"
        ;;
    code)
        echo "  fetching code-pattern targets..."
        for f in package.json tsconfig.json biome.json eslint.config.js eslint.config.ts \
                 .eslintrc.json pyproject.toml ruff.toml Cargo.toml go.mod Makefile \
                 README.md; do
            try_fetch "$f" "$OUT_DIR/$f"
        done
        for d in scripts tests __tests__; do
            try_fetch "$d" "$OUT_DIR/$d"
        done
        ;;
esac

# Scorecard (best-effort, skip failures silently)
SCORECARD=$(curl -s "https://api.scorecard.dev/projects/github.com/$REPO" 2>/dev/null | jq -r '.score // "n/a"' 2>/dev/null || echo "n/a")
echo "  OpenSSF Scorecard: $SCORECARD"

cat > "$OUT_DIR/_metadata.json" <<EOF
{
  "repo": "$REPO",
  "url": "https://github.com/$REPO",
  "mode": "$KIND",
  "commit_sha": "$SHA",
  "license": "$LICENSE",
  "stars": $STARS,
  "archived": $ARCHIVED,
  "fork": $IS_FORK,
  "updated_at": "$UPDATED",
  "description": $(echo "$DESC" | jq -Rs .),
  "scorecard": $(echo "$SCORECARD" | jq -R .),
  "fetched_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "  ✓ done → $OUT_DIR"
