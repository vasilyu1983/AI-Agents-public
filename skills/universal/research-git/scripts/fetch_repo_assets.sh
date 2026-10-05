#!/usr/bin/env bash
# fetch_repo_assets.sh — fetch mode-specific assets from a GitHub repo without cloning
#
# Usage:
#   ./fetch_repo_assets.sh <owner>/<repo> <output_dir> --kind <skill|practice|code|killer-feature>
#
# Examples:
#   ./fetch_repo_assets.sh twostraws/SwiftUI-Agent-Skill ./docs/research/2026-04-23-skill-ios/raw/ --kind skill
#   ./fetch_repo_assets.sh vercel/next.js          ./docs/research/2026-04-23-practice-pr/raw/ --kind practice
#   ./fetch_repo_assets.sh lingui/js-lingui        ./docs/research/2026-04-23-code-i18n/raw/  --kind code
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
#     ├── _fetch-manifest.jsonl  # one {path,status} row per attempted path
#     └── _metadata.json    # repo, url, commit_sha, license, stars, mode, fetch_status,
#                           # tree_listing, scorecard, fetched_at
#
# scorecard is the numeric score, "not published (404)" when Scorecard has no
# result for the repo, or "unavailable (...)" when the lookup itself failed.
#
# Skill mode lists the repo with the REST git/trees API. GitHub truncates a
# recursive tree past its size limit (the response says "truncated": true); the
# script then walks subtrees one call at a time, capped by MAX_TREE_CALLS
# (default 200). A failed or capped walk marks the fetch "partial".
#
# Exit codes: 0 = fetch ran (check fetch_status in _metadata.json);
# 1 = usage error, repo not reachable, or commit SHA not resolvable.
#
# Requires: gh CLI authenticated, jq, base64, curl

set -euo pipefail

usage() { sed -n '2,41p' "$0" | sed 's/^# \{0,1\}//'; }

for arg in "$@"; do
    case "$arg" in -h|--help) usage; exit 0 ;; esac
done

if [[ $# -lt 2 ]]; then
    usage >&2
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

if [[ ! "$REPO" =~ ^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$ ]]; then
    echo "ERROR: repo must be in <owner>/<repo> format" >&2
    exit 1
fi

if ! command -v gh &> /dev/null; then echo "ERROR: gh CLI not found" >&2; exit 1; fi
if ! command -v jq &> /dev/null; then echo "ERROR: jq not found" >&2; exit 1; fi

OWNER="${REPO%/*}"
NAME="${REPO#*/}"
OUT_DIR="${OUT_BASE%/}/${OWNER}__${NAME}"
if [[ -d "$OUT_DIR" ]] && [[ -n "$(find "$OUT_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    echo "ERROR: destination is nonempty; choose a fresh output directory to preserve commit provenance: $OUT_DIR" >&2
    exit 1
fi
mkdir -p "$OUT_DIR"
# Bare mktemp ignores TMPDIR on macOS; pass a template so sandboxed runs work.
ERR_FILE=$(mktemp "${TMPDIR:-/tmp}/fetch_repo_assets.XXXXXX")
TREE_PATHS_FILE=$(mktemp "${TMPDIR:-/tmp}/fetch_repo_assets.XXXXXX")
trap 'rm -f "$ERR_FILE" "$TREE_PATHS_FILE"' EXIT
MANIFEST="$OUT_DIR/_fetch-manifest.jsonl"
: > "$MANIFEST"
record_fetch() { jq -nc --arg path "$1" --arg status "$2" '{path:$path,status:$status}' >> "$MANIFEST"; }

# fd 3 keeps the real stderr: best-effort fetches run with 2>/dev/null, and a
# rate-limit or auth failure must still be reported before the script stops.
exec 3>&2
# abort_if_throttled <what> — a 403/429/401 or "rate limit" from gh is not a
# missing optional path. Stop instead of recording it as "unavailable".
abort_if_throttled() {
    if grep -qiE 'rate limit|HTTP (401|403|429)' "$ERR_FILE"; then
        echo "ERROR: $1 failed: $(tr '\n' ' ' < "$ERR_FILE")" >&3
        echo "Stopping: the fetch would otherwise record throttled paths as unavailable. Check: gh api rate_limit" >&3
        exit 1
    fi
}

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

SHA=$(gh api "repos/$REPO/commits/$DEFAULT_BRANCH" --jq '.sha' 2>"$ERR_FILE") || {
    echo "ERROR: cannot resolve the commit SHA for $REPO@$DEFAULT_BRANCH: $(tr '\n' ' ' < "$ERR_FILE")" >&2
    exit 1
}
if [[ -z "$SHA" ]]; then
    echo "ERROR: empty commit SHA for $REPO@$DEFAULT_BRANCH; refusing an unpinned fetch" >&2
    exit 1
fi
echo "  commit: $SHA"

# --- Repo tree listing (skill mode) ---------------------------------------
MAX_TREE_CALLS="${MAX_TREE_CALLS:-200}"
TREE_CALLS=0
TREE_STATE="complete"     # complete | failed | capped
TREE_TRUNCATED=0
TREE_LISTING="not-used"
TREE_JSON=""

# tree_call <tree-sha> <recursive 0|1> — one git/trees call into TREE_JSON.
tree_call() {
    if (( TREE_CALLS >= MAX_TREE_CALLS )); then
        TREE_STATE="capped"
        return 1
    fi
    TREE_CALLS=$((TREE_CALLS + 1))
    local query=""
    [[ "$2" == "1" ]] && query="?recursive=1"
    if ! TREE_JSON=$(gh api "repos/$REPO/git/trees/$1$query" 2>"$ERR_FILE"); then
        TREE_STATE="failed"
        echo "  ✗ git tree $1: $(tr '\n' ' ' < "$ERR_FILE")" >&2
        return 1
    fi
}

# walk_tree <tree-sha> <path-prefix> — append every blob path to TREE_PATHS_FILE.
# A truncated recursive listing is replaced by a per-subtree walk.
walk_tree() {
    local sha="$1" prefix="$2" sub_path sub_sha
    tree_call "$sha" 1 || return 1
    if [[ "$(jq -r '.truncated // false' <<<"$TREE_JSON")" != "true" ]]; then
        jq -r --arg p "$prefix" '.tree[] | select(.type == "blob") | $p + .path' <<<"$TREE_JSON" >> "$TREE_PATHS_FILE"
        return 0
    fi
    TREE_TRUNCATED=1
    tree_call "$sha" 0 || return 1
    jq -r --arg p "$prefix" '.tree[] | select(.type == "blob") | $p + .path' <<<"$TREE_JSON" >> "$TREE_PATHS_FILE"
    while IFS=$'\t' read -r sub_path sub_sha; do
        walk_tree "$sub_sha" "$prefix$sub_path/" || return 1
    done < <(jq -r '.tree[] | select(.type == "tree") | "\(.path)\t\(.sha)"' <<<"$TREE_JSON")
}

# list_repo_tree — fill TREE_PATHS_FILE and record the listing's completeness.
list_repo_tree() {
    walk_tree "$SHA" "" || true
    case "$TREE_STATE" in
        complete)
            if (( TREE_TRUNCATED )); then
                TREE_LISTING="complete-after-truncation"
                record_fetch "git tree (truncated; walked subtrees in $TREE_CALLS calls)" "fetched"
            else
                TREE_LISTING="complete"
            fi ;;
        failed)
            TREE_LISTING="failed"
            record_fetch "git tree" "failed" ;;
        capped)
            TREE_LISTING="capped"
            record_fetch "git tree (walk stopped at MAX_TREE_CALLS=$MAX_TREE_CALLS)" "capped"
            echo "  ⚠ tree walk capped at $MAX_TREE_CALLS calls; SKILL.md search is partial" >&2 ;;
    esac
}

# Fetch a path (file or directory) from the repo. Directories are fetched recursively.
# Args: <repo-path> <local-target-dir-or-file>
fetch_path() {
    local rpath="$1"
    local ltarget="$2"
    local entry type
    if ! entry=$(gh api "repos/$REPO/contents/$rpath?ref=$SHA" 2>"$ERR_FILE"); then
        abort_if_throttled "gh api contents/$rpath"
        record_fetch "$rpath" "unavailable"; return 1
    fi
    # Array = directory; object = file
    if [[ "$(echo "$entry" | jq -r 'type')" == "array" ]]; then
        mkdir -p "$ltarget"
        # Process substitution keeps the loop in this shell, so an abort inside
        # fetch_file exits the script instead of only the pipeline's subshell.
        while IFS= read -r item; do
            type=$(echo "$item" | jq -r '.type')
            local name; name=$(echo "$item" | jq -r '.name')
            case "$type" in
                file) fetch_file "$rpath/$name" "$ltarget/$name" || true ;;
                dir)  fetch_path "$rpath/$name" "$ltarget/$name" || true ;;
            esac
        done < <(echo "$entry" | jq -c '.[]')
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
    if gh api "repos/$REPO/contents/$rpath?ref=$SHA" 2>"$ERR_FILE" \
        | jq -er 'select(.encoding == "base64") | .content' \
        | "${B64_DECODE[@]}" > "$ltarget.part" 2>/dev/null; then
        mv "$ltarget.part" "$ltarget"
        record_fetch "$rpath" "fetched"
        echo "    ✓ $rpath"
    else
        rm -f "$ltarget.part"
        abort_if_throttled "gh api contents/$rpath"
        record_fetch "$rpath" "failed"
        echo "    ✗ $rpath (failed)" >&2
        return 1
    fi
}

# Best-effort fetch: ignore misses rather than failing
try_fetch() { fetch_path "$1" "$2" 2>/dev/null || echo "    · $1 (not present)"; }

case "$KIND" in
    skill)
        mkdir -p "$OUT_DIR/references"
        echo "  searching for SKILL.md..."
        list_repo_tree
        SKILL_PATHS=$(grep -E '(SKILL|skill)\.md$' "$TREE_PATHS_FILE" || true)
        SKILL_PATH=$(echo "$SKILL_PATHS" | head -1)
        if [[ $(echo "$SKILL_PATHS" | sed '/^$/d' | wc -l | tr -d ' ') -gt 1 ]]; then
            record_fetch "SKILL.md selection" "ambiguous"
            echo "  Multiple skill paths; selected $SKILL_PATH. Review selection before reuse." >&2
        fi
        if [[ -n "$SKILL_PATH" ]]; then
            echo "  fetching $SKILL_PATH..."
            fetch_file "$SKILL_PATH" "$OUT_DIR/SKILL.md" || true
            SKILL_DIR=$(dirname "$SKILL_PATH")
            REF_DIR="${SKILL_DIR}/references"
            [[ "$SKILL_DIR" == "." ]] && REF_DIR="references"
            try_fetch "$REF_DIR" "$OUT_DIR/references"
        else
            record_fetch "SKILL.md" "unavailable"
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

# Scorecard (best-effort; absence is not a security verdict). A lookup that
# fails (network, proxy, DNS) is recorded separately from a project Scorecard
# has not published (404), so the metadata never blurs the two.
SCORECARD_BODY=$(mktemp "${TMPDIR:-/tmp}/fetch_repo_assets.XXXXXX")
SCORECARD_CODE=$(curl -s -o "$SCORECARD_BODY" -w '%{http_code}' \
    "https://api.scorecard.dev/projects/github.com/$REPO" 2>/dev/null) || SCORECARD_CODE=""
if [[ ! "$SCORECARD_CODE" =~ ^[0-9]{3}$ ]] || [[ "$SCORECARD_CODE" == "000" ]]; then
    SCORECARD="unavailable (fetch failed)"
elif [[ "$SCORECARD_CODE" == "404" ]]; then
    SCORECARD="not published (404)"
elif [[ "$SCORECARD_CODE" == "200" ]]; then
    SCORECARD=$(jq -r '.score // empty' "$SCORECARD_BODY" 2>/dev/null || true)
    [[ -z "$SCORECARD" ]] && SCORECARD="unavailable (no score in response)"
else
    SCORECARD="unavailable (HTTP $SCORECARD_CODE)"
fi
rm -f "$SCORECARD_BODY"
echo "  OpenSSF Scorecard: $SCORECARD"

INCOMPLETE=$(jq -s '[.[] | select(.status != "fetched")] | length' "$MANIFEST")
FETCH_STATUS="complete"
[[ "$INCOMPLETE" -gt 0 ]] && FETCH_STATUS="partial"
cat > "$OUT_DIR/_metadata.json" <<EOF
{
  "repo": "$REPO",
  "url": "https://github.com/$REPO",
  "mode": "$KIND",
  "fetch_status": "$FETCH_STATUS",
  "unavailable_or_failed_paths": $INCOMPLETE,
  "manifest": "_fetch-manifest.jsonl",
  "tree_listing": "$TREE_LISTING",
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

echo "  $FETCH_STATUS → $OUT_DIR (inspect _fetch-manifest.jsonl; unavailable includes missing optional paths and API failures)"
