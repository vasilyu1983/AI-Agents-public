#!/usr/bin/env bash
# audit-agents.sh — report AGENTS.md / CLAUDE.md coverage and staleness
# across the source portfolio. Read-only. Generic.
set -euo pipefail

HUB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPOS_ROOT="${1:-$(dirname "$HUB_DIR")}"
STALE_DAYS="${STALE_DAYS:-120}"
now=$(date +%s)

printf '%-28s %-10s %s\n' "REPO" "AGENTS" "AGE(days)"
shopt -s nullglob
for repo in "$REPOS_ROOT"/*/; do
  name="$(basename "$repo")"
  [ "$repo" = "$HUB_DIR/" ] && continue
  [ -d "$repo/.git" ] || continue
  f=""
  [ -f "$repo/AGENTS.md" ] && f="$repo/AGENTS.md"
  [ -z "$f" ] && [ -f "$repo/CLAUDE.md" ] && f="$repo/CLAUDE.md"
  if [ -z "$f" ]; then
    printf '%-28s %-10s %s\n' "$name" "MISSING" "-"
    continue
  fi
  mtime=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f")
  age=$(( (now - mtime) / 86400 ))
  flag="ok"; [ "$age" -gt "$STALE_DAYS" ] && flag="STALE"
  printf '%-28s %-10s %s (%s)\n' "$name" "present" "$age" "$flag"
done
