#!/usr/bin/env bash
# check_hub_freshness.sh — Detect when doc hub pages need updating
#
# Compares git commit history in source repos against hub document
# freshness metadata to identify which hub docs are stale.
#
# Usage:
#   check_hub_freshness.sh <repos_dir> <hub_dir> [OPTIONS]
#
# Options:
#   --since YYYY-MM-DD   Check commits since this date (default: extracted from hub docs)
#   --json               Output machine-readable JSON instead of markdown
#   --mapping FILE       Explicit repo→hub-doc mapping (JSON). Without this, auto-discovers.
#   --out FILE           Write report to file instead of stdout
#   --verbose            Show per-repo scan progress on stderr
#
# Exit codes:
#   0 = hub is fresh (no updates needed)
#   1 = updates needed
#   2 = error (bad args, missing dirs)

set -euo pipefail

# ─── Defaults ────────────────────────────────────────────────────────────────

SINCE_DATE=""
JSON_OUTPUT=false
MAPPING_FILE=""
OUT_FILE=""
VERBOSE=false

# Change detection patterns (regex matched against git diff paths).
#
# Language-agnostic defaults cover the most common stack-neutral signals.
# Override via check_hub_freshness.config.sh (see .example for template).
SCHEMA_PATTERNS='\.sql$|openapi.*\.ya?ml|\.proto$|package\.json|pyproject\.toml|Cargo\.toml|go\.mod'
API_PATTERNS='openapi|swagger|\.proto$|/routes/|/handlers?/'
MESSAGING_PATTERNS='kafka|rabbit|consumer|producer|\.avsc$'
CONFIG_PATTERNS='package\.json|pyproject\.toml|Cargo\.toml|go\.mod|docker-compose|\.env\.'
INFRA_PATTERNS='Dockerfile|\.ya?ml$|\.gitlab-ci|\.github/workflows|helm|k8s|terraform'

# Override via check_hub_freshness.config.sh (see .example for template).
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$_SCRIPT_DIR/check_hub_freshness.config.sh" ]]; then
  # shellcheck source=/dev/null
  source "$_SCRIPT_DIR/check_hub_freshness.config.sh"
fi

# ─── Helpers ─────────────────────────────────────────────────────────────────

die() { echo "ERROR: $*" >&2; exit 2; }
info() { [[ "$VERBOSE" == true ]] && echo "[info] $*" >&2 || true; }

usage() {
  sed -n -e '2,/^$/{' -e 's/^# //' -e 's/^#//' -e 'p' -e '}' "$0"
  exit 2
}

# Extract the earliest last_verified date from hub markdown files.
# Looks for YAML frontmatter or inline metadata like "last_verified: 2026-03-19".
extract_hub_baseline_date() {
  local hub_dir="$1"
  local earliest=""

  while IFS= read -r line; do
    local date_val
    date_val=$(echo "$line" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
    [[ -z "$date_val" ]] && continue
    if [[ -z "$earliest" ]] || [[ "$date_val" < "$earliest" ]]; then
      earliest="$date_val"
    fi
  done < <(grep -rh 'last_verified' "$hub_dir" --include='*.md' 2>/dev/null || true)

  if [[ -n "$earliest" ]]; then
    echo "$earliest"
  else
    # Fallback: 30 days ago
    if date -v-30d '+%Y-%m-%d' >/dev/null 2>&1; then
      date -v-30d '+%Y-%m-%d'  # macOS
    else
      date -d '30 days ago' '+%Y-%m-%d'  # GNU
    fi
  fi
}

# Get the latest commit date (ISO) for a repo.
repo_latest_commit_date() {
  local repo="$1"
  git -C "$repo" log -1 --format='%aI' 2>/dev/null | cut -dT -f1
}

# Get changed files since a date, one per line.
repo_changed_files_since() {
  local repo="$1" since="$2"
  git -C "$repo" log --name-only --format='' --since="$since" 2>/dev/null | sort -u | grep -v '^$' || true
}

# Get commit count since a date.
repo_commit_count_since() {
  local repo="$1" since="$2"
  git -C "$repo" rev-list --count --since="$since" HEAD 2>/dev/null || echo 0
}

# Categorize a list of changed files (stdin) into change types.
# Outputs space-separated unique categories.
categorize_changes() {
  local categories=""
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    if echo "$file" | grep -qE "$SCHEMA_PATTERNS"; then
      categories="$categories SCHEMA"
    fi
    if echo "$file" | grep -qE "$API_PATTERNS"; then
      categories="$categories API"
    fi
    if echo "$file" | grep -qE "$MESSAGING_PATTERNS"; then
      categories="$categories MESSAGING"
    fi
    if echo "$file" | grep -qE "$CONFIG_PATTERNS"; then
      categories="$categories CONFIG"
    fi
    if echo "$file" | grep -qE "$INFRA_PATTERNS"; then
      categories="$categories INFRA"
    fi
  done
  # Deduplicate and sort
  if [[ -n "$categories" ]]; then
    echo "$categories" | tr ' ' '\n' | sort -u | grep -v '^$' | tr '\n' ' ' | sed 's/ $//'
  fi
}

# Determine priority from change categories.
# P1: SCHEMA or API changes — likely break contracts or data models
# P2: MESSAGING changes — affect event flows
# P3: CONFIG or INFRA — operational but less likely to invalidate docs
# P4: Other changes only
compute_priority() {
  local cats="$1"
  if echo "$cats" | grep -qE 'SCHEMA|API'; then
    echo "P1"
  elif echo "$cats" | grep -q 'MESSAGING'; then
    echo "P2"
  elif echo "$cats" | grep -qE 'CONFIG|INFRA'; then
    echo "P3"
  else
    echo "P4"
  fi
}

# Auto-discover which hub docs reference a given repo name.
# Searches for the repo name (case-insensitive) in hub markdown files.
find_hub_docs_for_repo() {
  local hub_dir="$1" repo_name="$2"
  # Normalise repo name: try exact, lowercase, and with dots replaced by hyphens
  local patterns=("$repo_name")
  local lower
  lower=$(echo "$repo_name" | tr '[:upper:]' '[:lower:]')
  [[ "$lower" != "$repo_name" ]] && patterns+=("$lower")
  local dotless
  dotless=$(echo "$repo_name" | tr '.' '-')
  [[ "$dotless" != "$repo_name" ]] && patterns+=("$dotless")

  local found_files=""
  for pattern in "${patterns[@]}"; do
    while IFS= read -r match; do
      # Return path relative to hub_dir
      local rel
      rel=$(echo "$match" | sed "s|^${hub_dir}/||")
      found_files="$found_files $rel"
    done < <(grep -rli "$pattern" "$hub_dir" --include='*.md' 2>/dev/null || true)
  done

  # Deduplicate
  if [[ -n "$found_files" ]]; then
    echo "$found_files" | tr ' ' '\n' | sort -u | grep -v '^$' | tr '\n' ',' | sed 's/,$//'
  fi
}

# Load explicit mapping from JSON file.
# Expected format: { "mappings": [ { "repo_pattern": "payments-ledger", "hub_docs": ["a.md","b.md"] } ] }
load_mapping() {
  local mapping_file="$1" repo_name="$2"
  if command -v python3 &>/dev/null; then
    python3 -c "
import json, sys, fnmatch
data = json.load(open('$mapping_file'))
for m in data.get('mappings', []):
    pat = m.get('repo_pattern', '')
    if fnmatch.fnmatch('$repo_name'.lower(), pat.lower()) or fnmatch.fnmatch('$repo_name', pat):
        print(','.join(m.get('hub_docs', [])))
        sys.exit(0)
" 2>/dev/null || true
  fi
}

# Extract last_verified date from a specific hub doc.
extract_doc_last_verified() {
  local doc_path="$1"
  grep -oE 'last_verified:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$doc_path" 2>/dev/null \
    | head -1 \
    | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || echo "unknown"
}

# ─── Argument Parsing ────────────────────────────────────────────────────────

[[ $# -lt 2 ]] && usage

REPOS_DIR="$1"; shift
HUB_DIR="$1"; shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --since)    SINCE_DATE="$2"; shift 2 ;;
    --json)     JSON_OUTPUT=true; shift ;;
    --mapping)  MAPPING_FILE="$2"; shift 2 ;;
    --out)      OUT_FILE="$2"; shift 2 ;;
    --verbose)  VERBOSE=true; shift ;;
    -h|--help)  usage ;;
    *)          die "Unknown option: $1" ;;
  esac
done

[[ -d "$REPOS_DIR" ]] || die "Repos directory not found: $REPOS_DIR"
[[ -d "$HUB_DIR" ]]   || die "Hub directory not found: $HUB_DIR"

# Resolve to absolute canonical paths (resolve symlinks on macOS)
if command -v realpath &>/dev/null; then
  REPOS_DIR=$(realpath "$REPOS_DIR")
  HUB_DIR=$(realpath "$HUB_DIR")
else
  REPOS_DIR=$(cd "$REPOS_DIR" && pwd -P)
  HUB_DIR=$(cd "$HUB_DIR" && pwd -P)
fi

# Determine baseline date
if [[ -z "$SINCE_DATE" ]]; then
  SINCE_DATE=$(extract_hub_baseline_date "$HUB_DIR")
  info "Auto-detected baseline date from hub: $SINCE_DATE"
fi
info "Checking commits since: $SINCE_DATE"

# ─── Main Scan ───────────────────────────────────────────────────────────────

declare -a RESULTS=()
UPDATES_NEEDED=0

# Find all git repos under REPOS_DIR (depth 1-2)
while IFS= read -r git_dir; do
  repo_dir=$(dirname "$git_dir")
  repo_name=$(basename "$repo_dir")

  # Skip the hub itself if it lives under repos_dir (resolve to canonical path)
  canonical_repo_dir=""
  if command -v realpath &>/dev/null; then
    canonical_repo_dir=$(realpath "$repo_dir" 2>/dev/null || echo "$repo_dir")
  else
    canonical_repo_dir=$(cd "$repo_dir" && pwd -P 2>/dev/null || echo "$repo_dir")
  fi
  [[ "$canonical_repo_dir" == "$HUB_DIR" ]] && continue

  info "Scanning: $repo_name"

  # Count commits since baseline
  commit_count=$(repo_commit_count_since "$repo_dir" "$SINCE_DATE")
  [[ "$commit_count" -eq 0 ]] && continue

  # Get changed files and categorize
  changed_files=$(repo_changed_files_since "$repo_dir" "$SINCE_DATE")

  # Skip repos with commits but no file changes (merge commits, rebases)
  if [[ -z "$changed_files" ]]; then
    continue
  fi
  file_count=$(echo "$changed_files" | wc -l | tr -d ' ')

  categories=$(echo "$changed_files" | categorize_changes)
  [[ -z "$categories" ]] && categories="OTHER"

  priority=$(compute_priority "$categories")
  latest_commit=$(repo_latest_commit_date "$repo_dir")

  # Find affected hub docs
  hub_docs=""
  if [[ -n "$MAPPING_FILE" && -f "$MAPPING_FILE" ]]; then
    hub_docs=$(load_mapping "$MAPPING_FILE" "$repo_name")
  fi
  if [[ -z "$hub_docs" ]]; then
    hub_docs=$(find_hub_docs_for_repo "$HUB_DIR" "$repo_name")
  fi

  [[ -z "$hub_docs" ]] && hub_docs="(no hub docs reference this repo)"

  # Store result
  RESULTS+=("${priority}|${repo_name}|${commit_count}|${file_count}|${categories}|${latest_commit}|${hub_docs}")
  UPDATES_NEEDED=1

done < <(find "$REPOS_DIR" -maxdepth 2 -name ".git" -type d 2>/dev/null | sort)

# ─── Sort results by priority ────────────────────────────────────────────────

IFS=$'\n' SORTED=($(printf '%s\n' "${RESULTS[@]}" | sort)); unset IFS

# ─── Output ──────────────────────────────────────────────────────────────────

generate_markdown() {
  echo "# Hub Freshness Report"
  echo ""
  echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')"
  echo "**Baseline date:** $SINCE_DATE"
  echo "**Repos scanned:** $(find "$REPOS_DIR" -maxdepth 2 -name ".git" -type d 2>/dev/null | wc -l | tr -d ' ')"
  echo "**Repos with changes:** ${#SORTED[@]}"
  echo ""

  if [[ ${#SORTED[@]} -eq 0 ]]; then
    echo "All hub documents are fresh. No source repos have changed since $SINCE_DATE."
    return
  fi

  echo "## Priority Legend"
  echo ""
  echo "- **P1**: Schema or API changes — likely invalidate data models, contracts, or interface docs"
  echo "- **P2**: Messaging changes — affect event flows, consumer/producer docs"
  echo "- **P3**: Config or infrastructure changes — operational impact"
  echo "- **P4**: Other changes (tests, minor code, docs)"
  echo ""
  echo "## Changes Detected"
  echo ""
  echo "| Priority | Repo | Commits | Files | Categories | Latest Commit | Affected Hub Docs |"
  echo "|----------|------|---------|-------|------------|---------------|-------------------|"

  for entry in "${SORTED[@]}"; do
    IFS='|' read -r pri repo commits files cats latest docs <<< "$entry"
    echo "| **$pri** | $repo | $commits | $files | $cats | $latest | $docs |"
  done

  echo ""
  echo "## Recommended Actions"
  echo ""

  local has_p1=false has_p2=false
  for entry in "${SORTED[@]}"; do
    IFS='|' read -r pri _ _ _ _ _ _ <<< "$entry"
    [[ "$pri" == "P1" ]] && has_p1=true
    [[ "$pri" == "P2" ]] && has_p2=true
  done

  if [[ "$has_p1" == true ]]; then
    echo "1. **Urgent**: P1 changes detected — re-verify hub docs referencing repos with schema/API changes"
  fi
  if [[ "$has_p2" == true ]]; then
    echo "2. **Soon**: P2 changes detected — review messaging/event docs for accuracy"
  fi
  echo "3. After updating, bump \`last_verified\` dates in affected hub documents"
}

generate_json() {
  echo "{"
  echo "  \"generated\": \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\","
  echo "  \"baseline_date\": \"$SINCE_DATE\","
  echo "  \"repos_scanned\": $(find "$REPOS_DIR" -maxdepth 2 -name ".git" -type d 2>/dev/null | wc -l | tr -d ' '),"
  echo "  \"repos_with_changes\": ${#SORTED[@]},"
  echo "  \"updates_needed\": $([[ $UPDATES_NEEDED -eq 1 ]] && echo true || echo false),"
  echo "  \"changes\": ["

  local first=true
  for entry in "${SORTED[@]}"; do
    IFS='|' read -r pri repo commits files cats latest docs <<< "$entry"
    [[ "$first" == true ]] && first=false || echo "    ,"

    # Convert comma-separated hub_docs to JSON array
    local docs_json="["
    local doc_first=true
    IFS=',' read -ra doc_array <<< "$docs"
    for doc in "${doc_array[@]}"; do
      doc=$(echo "$doc" | xargs)  # trim whitespace
      [[ "$doc_first" == true ]] && doc_first=false || docs_json="$docs_json, "
      docs_json="$docs_json\"$doc\""
    done
    docs_json="$docs_json]"

    # Convert space-separated categories to JSON array
    local cats_json="["
    local cat_first=true
    for cat in $cats; do
      [[ "$cat_first" == true ]] && cat_first=false || cats_json="$cats_json, "
      cats_json="$cats_json\"$cat\""
    done
    cats_json="$cats_json]"

    echo "    {"
    echo "      \"priority\": \"$pri\","
    echo "      \"repo\": \"$repo\","
    echo "      \"commits\": $commits,"
    echo "      \"files_changed\": $files,"
    echo "      \"categories\": $cats_json,"
    echo "      \"latest_commit\": \"$latest\","
    echo "      \"affected_hub_docs\": $docs_json"
    echo -n "    }"
  done

  echo ""
  echo "  ]"
  echo "}"
}

# Direct output or write to file
output() {
  if [[ "$JSON_OUTPUT" == true ]]; then
    generate_json
  else
    generate_markdown
  fi
}

if [[ -n "$OUT_FILE" ]]; then
  output > "$OUT_FILE"
  echo "Report written to: $OUT_FILE" >&2
else
  output
fi

exit $UPDATES_NEEDED
