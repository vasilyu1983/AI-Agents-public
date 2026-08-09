#!/usr/bin/env bash
# audit_repo.sh — single-repo AGENTS.md audit
#
# Verifies that every backticked path in AGENTS.md/CLAUDE.md resolves on disk,
# every backticked command is a real script/binary, and runs the existing
# lint_claude_memory.sh checks (size, symlink/mirror, secrets, @imports).
#
# Output: structured report to stdout. Exit 0 on clean, 1 on issues found.
#
# Usage:
#   audit_repo.sh <repo-path>
#   audit_repo.sh <repo-path> --json    # machine-readable output

set -euo pipefail

repo="${1:-}"
mode="${2:-text}"

if [[ -z "$repo" || ! -d "$repo" ]]; then
  echo "Usage: $0 <repo-path> [--json]" >&2
  exit 2
fi

repo="$(cd "$repo" && pwd -P)"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

# ---- collect memory files ----
memory_files=()
for f in AGENTS.md CLAUDE.md AGENTS.override.md CLAUDE.local.md; do
  [[ -e "$repo/$f" ]] && memory_files+=("$repo/$f")
done

if [[ ${#memory_files[@]} -eq 0 ]]; then
  if [[ "$mode" == "--json" ]]; then
    printf '{"repo":"%s","status":"no_memory_files","issues":[]}\n' "$repo"
  else
    echo "[$repo] no AGENTS.md / CLAUDE.md found"
  fi
  exit 0
fi

# Pick the canonical file to scan (AGENTS.md if present, else CLAUDE.md).
# CLAUDE.md as symlink is followed automatically.
canonical="$repo/AGENTS.md"
[[ ! -e "$canonical" ]] && canonical="$repo/CLAUDE.md"

issues=()
add_issue() {
  local severity="$1" category="$2" detail="$3"
  issues+=("${severity}|${category}|${detail}")
}

# Detect path prefixes:
#   1. Explicit hint: <!-- audit-path-prefix: app/src --> in AGENTS.md
#   2. Fallback: common conventions if directories exist
has_pre_code_caveat=0
if grep -qiE '(^|\s)pre[- ]code caveat|<!-- *pre-code' "$canonical" 2>/dev/null; then
  has_pre_code_caveat=1
fi

# Build ignore-pattern list from <!-- audit-ignore: pattern1,pattern2 -->
ignore_patterns=()
while IFS= read -r raw; do
  [[ -z "$raw" ]] && continue
  IFS=',' read -ra parts <<<"$raw"
  for part in "${parts[@]}"; do
    part="${part## }"; part="${part%% }"
    [[ -z "$part" ]] && continue
    ignore_patterns+=("$part")
  done
done < <(grep -oE '<!-- *audit-ignore: *[^>]+-->' "$canonical" 2>/dev/null \
  | sed -E 's/<!-- *audit-ignore: *([^>]*[^> ]) *-->/\1/' || true)

is_ignored() {
  local p="$1"
  for pat in "${ignore_patterns[@]:-}"; do
    [[ -z "$pat" ]] && continue
    [[ "$p" == $pat ]] && return 0
  done
  return 1
}

prefixes=("")
# Explicit directive: <!-- audit-path-prefix: a/b/,c/d/ --> (comma-separated, multiple lines OK)
while IFS= read -r explicit; do
  [[ -z "$explicit" ]] && continue
  IFS=',' read -ra parts <<<"$explicit"
  for part in "${parts[@]}"; do
    part="${part## }"; part="${part%% }"
    [[ -z "$part" ]] && continue
    prefixes+=("${part%/}/")
  done
done < <(grep -oE '<!-- *audit-path-prefix: *[^>]+-->' "$canonical" 2>/dev/null \
  | sed -E 's/<!-- *audit-path-prefix: *([^>]*[^> ]) *-->/\1/' || true)

for candidate in app app/src app/lib src lib docs/context; do
  [[ -d "$repo/$candidate" ]] && prefixes+=("$candidate/")
done

# Try each prefix when resolving a relative path
resolve_with_prefix() {
  local p="$1"
  for pre in "${prefixes[@]}"; do
    [[ -e "$repo/$pre$p" ]] && return 0
  done
  return 1
}

# ---- 1. size budget ----
lines="$(wc -l <"$canonical" | tr -d ' ')"
if [[ "$lines" -gt 300 ]]; then
  add_issue "MED" "size" "$canonical has $lines lines (>300; instruction-budget risk)"
fi

# ---- 2. extract backticked paths and verify ----
# Strategy: only treat a backtick token as a path if it has path-like shape:
#   - starts with ./ or ../ or /
#   - OR is a single token (no spaces) with / and a recognizable filename pattern
# Skip command invocations (`git -C ...`, `rg -n ...`), placeholders (<...>),
# globs (*), URLs.
paths_tmp="$(mktemp)"
trap 'rm -f "$paths_tmp"' EXIT

grep -oE '`[^`]+`' "$canonical" \
  | sed 's/^`//;s/`$//' \
  | grep -vE '^(https?://|ftp://|git@|ssh://|mailto:)' \
  | awk '
    {
      first = $1
      # Skip URLs and protocol-prefixed
      if (first ~ /^(https?|ftp|ssh|git|mailto):/) next
      # Skip command invocations
      if (first ~ /^(git|rg|grep|sed|awk|cat|cd|echo|export|bash|sh|npm|yarn|pnpm|cargo|go|python|pip|brew|chmod|find|mkdir|touch|cp|mv|rm|ls|wc|sort|uniq|tr|jq|curl|wget|kubectl|docker|gh|xcodebuild|gradle|gradlew)$/) next

      # Only emit HIGH-confidence path candidates:
      # 1. Starts with ./ or ../ (explicitly relative)
      # 2. Real absolute path (/Users/ /home/ /opt/ /etc/ /var/ /tmp/)
      # 3. Relative with file extension (.ts .js .json .md .swift .kt .sh .py .yml .yaml .toml .xml .html .css .lock)
      # 4. Relative ending in / (directory)
      # Anything else (URL routes, npm packages, prefix-relative paths) is skipped.
      if (first ~ /^\.\.?\//) { print first; next }
      if (first ~ /^\/(Users|home|opt|etc|var|tmp|usr)\//) { print first; next }
      if (first ~ /^[A-Za-z][^\/]*\/.*\.(ts|tsx|js|jsx|json|md|swift|kt|kts|sh|py|yml|yaml|toml|xml|html|css|scss|sql|lock|env|gradle|plist)$/) { print first; next }
      if (first ~ /^[A-Za-z][^\/]*\/.*\/$/) { print first; next }
    }
  ' \
  | sed 's/[,;:.]$//' \
  | sort -u >"$paths_tmp"

while IFS= read -r p; do
  [[ -z "$p" ]] && continue
  # User-declared ignores
  is_ignored "$p" && continue
  # Skip placeholders and globs
  case "$p" in
    *\<*\>* | *\**) continue ;;
    /*) check_path="$p" ;;
    \./*) check_path="$repo/${p#./}" ;;
    \.\./*)
      check_path="$repo/$p"
      # Fallback: strip leading ../ segments and check repo-rooted variant
      # (handles paths shown as relative-from-worktree-subdir, e.g. ../../scripts/foo.sh)
      stripped="$p"
      while [[ "$stripped" == ../* ]]; do stripped="${stripped#../}"; done
      [[ -e "$repo/$stripped" ]] && continue
      ;;
    # Bare `dir/...` — first try repo root, then auto-detected prefixes,
    # then sibling-repo (cross-repo references)
    */*)
      if [[ -e "$repo/$p" ]]; then
        check_path="$repo/$p"
      elif resolve_with_prefix "$p"; then
        continue
      elif [[ -e "$(dirname "$repo")/$p" ]]; then
        # Sibling-repo reference resolved at parent dir; treat as valid
        continue
      else
        check_path="$repo/$p"
      fi
      ;;
    *) continue ;;
  esac
  if [[ ! -e "$check_path" ]]; then
    base="${check_path%%(*}"
    base="${base%% *}"
    [[ -e "$base" ]] && continue
    add_issue "HIGH" "stale-path" "$p does not resolve (checked: $check_path)"
  fi
done <"$paths_tmp"

# ---- 3. verify referenced shell scripts are executable ----
script_paths="$(grep -oE '`\./[^ ]+\.sh[^ `]*`' "$canonical" 2>/dev/null \
  | sed 's/^`//;s/`$//' | sort -u || true)"

while IFS= read -r s; do
  [[ -z "$s" ]] && continue
  # Strip args and flags
  script_only="${s%% *}"
  full="$repo/${script_only#./}"
  if [[ -e "$full" && ! -x "$full" ]]; then
    add_issue "MED" "script-not-executable" "$script_only exists but is not executable"
  fi
done <<<"$script_paths"

# ---- 4. delegate to lint_claude_memory.sh for size/symlink/secrets/@import ----
lint_output="$(bash "$script_dir/lint_claude_memory.sh" "$repo" 2>&1 || true)"
while IFS= read -r line; do
  if [[ "$line" == ERROR:* ]]; then
    add_issue "HIGH" "lint" "${line#ERROR: }"
  elif [[ "$line" == WARN:* ]]; then
    add_issue "LOW" "lint" "${line#WARN: }"
  fi
done <<<"$lint_output"

# ---- 5. hallucination-bait heuristics ----
# Wrong-layer hint: "authoritative in *.ts" when there's a sibling *.json with same stem
ts_authoritative="$(grep -oE 'authoritative in `[^`]+\.ts`' "$canonical" 2>/dev/null || true)"
if [[ -n "$ts_authoritative" ]]; then
  while IFS= read -r match; do
    ts_file="${match#authoritative in \`}"
    ts_file="${ts_file%\`}"
    json_sibling="${ts_file%.ts}.json"
    full_ts="$repo/$ts_file"
    full_json="$repo/$json_sibling"
    if [[ -e "$full_ts" && -e "$full_json" ]]; then
      add_issue "MED" "wrong-layer-suspect" "$ts_file claimed authoritative but $json_sibling exists; verify which is config vs logic"
    fi
  done <<<"$ts_authoritative"
fi

# Scaffold-tense smell: present-tense enforcement in repos with very few code files
if [[ "$has_pre_code_caveat" -eq 0 && ! -d "$repo/src" && ! -d "$repo/app" && ! -e "$repo/project.yml" && ! -e "$repo/package.json" && ! -e "$repo/build.gradle" && ! -e "$repo/build.gradle.kts" && ! -e "$repo/Package.swift" ]]; then
  if grep -qE '(must come from|must be|All user-facing)' "$canonical" 2>/dev/null; then
    add_issue "MED" "scaffold-tense" "AGENTS.md uses present-tense enforcement but no code roots detected (src/ app/ etc); add a Pre-Code Caveat (see references/cross-doc-audit.md)"
  fi
fi

# Generic "Agent Execution Style" platitudes
if grep -qE '^## Agent Execution Style' "$canonical" 2>/dev/null; then
  add_issue "LOW" "platitudes" "'## Agent Execution Style' section detected — usually generic platitudes; consider deletion"
fi

# ---- 6. emit report ----
if [[ "$mode" == "--json" ]]; then
  printf '{"repo":"%s","lines":%s,"issues":[' "$repo" "$lines"
  first=1
  for entry in "${issues[@]:-}"; do
    [[ -z "$entry" ]] && continue
    sev="${entry%%|*}"
    rest="${entry#*|}"
    cat="${rest%%|*}"
    msg="${rest#*|}"
    msg_escaped="$(printf '%s' "$msg" | sed 's/\\/\\\\/g;s/"/\\"/g')"
    if [[ $first -eq 1 ]]; then first=0; else printf ','; fi
    printf '{"severity":"%s","category":"%s","message":"%s"}' "$sev" "$cat" "$msg_escaped"
  done
  printf ']}\n'
else
  echo "=== $repo ==="
  echo "memory files:"
  for f in "${memory_files[@]}"; do
    echo "  - ${f#$repo/}"
  done
  echo "AGENTS.md size: $lines lines"
  if [[ ${#issues[@]} -eq 0 ]]; then
    echo "STATUS: clean"
    echo
    exit 0
  fi
  echo "issues (${#issues[@]}):"
  for entry in "${issues[@]:-}"; do
    [[ -z "$entry" ]] && continue
    sev="${entry%%|*}"
    rest="${entry#*|}"
    cat="${rest%%|*}"
    msg="${rest#*|}"
    printf '  [%-4s] %-24s %s\n' "$sev" "$cat" "$msg"
  done
  echo
fi

# Exit 1 if any HIGH issue, else 0
for entry in "${issues[@]:-}"; do
    [[ -z "$entry" ]] && continue
  [[ "${entry%%|*}" == "HIGH" ]] && exit 1
done
exit 0
