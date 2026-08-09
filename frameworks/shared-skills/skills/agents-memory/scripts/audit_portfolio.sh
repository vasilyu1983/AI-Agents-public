#!/usr/bin/env bash
# audit_portfolio.sh — run audit_repo.sh across N repos and produce an aggregate report.
#
# Usage:
#   audit_portfolio.sh <repo1> <repo2> ... <repoN>
#   audit_portfolio.sh --from-file <path-to-list-of-repos>
#
# Output: per-repo report + portfolio summary table. Exit code 0 if all repos
# are clean (no HIGH issues), 1 if any repo has HIGH issues.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
audit_one="$script_dir/audit_repo.sh"

if [[ ! -x "$audit_one" ]]; then
  echo "ERROR: $audit_one not executable. Run: chmod +x $audit_one" >&2
  exit 2
fi

repos=()
if [[ "${1:-}" == "--from-file" ]]; then
  list_file="${2:?--from-file requires a path argument}"
  while IFS= read -r line; do
    line="$(echo "$line" | sed 's/#.*//' | xargs)"
    [[ -z "$line" ]] && continue
    repos+=("$line")
  done <"$list_file"
else
  repos=("$@")
fi

if [[ ${#repos[@]} -eq 0 ]]; then
  echo "Usage: $0 <repo1> [<repo2> ...]" >&2
  echo "       $0 --from-file <list>" >&2
  exit 2
fi

# Temp dir to cache JSON results keyed by a hash of the repo path.
# Using md5 (available on both macOS and Linux) to derive a filename-safe key.
# This avoids re-invoking audit_repo.sh a second time per repo for the summary table.
cache_dir="$(mktemp -d)"
trap 'rm -rf "$cache_dir"' EXIT

_cache_key() {
  # Produce a short hex key from a repo path. md5 is available on macOS 3.x bash.
  printf '%s' "$1" | md5 2>/dev/null || printf '%s' "$1" | md5sum 2>/dev/null | cut -c1-32
}

# Run each audit, collect summary
total_high=0
total_med=0
total_low=0
failed_repos=()
clean_repos=()

for repo in "${repos[@]}"; do
  if [[ ! -d "$repo" ]]; then
    echo "[skip] $repo (not a directory)"
    continue
  fi

  bash "$audit_one" "$repo" || true

  # Run JSON mode once and cache the result
  cache_file="$cache_dir/$(_cache_key "$repo")"
  bash "$audit_one" "$repo" --json 2>/dev/null >"$cache_file" || true

  json="$(cat "$cache_file")"
  if [[ -z "$json" ]]; then
    continue
  fi

  high="$(printf '%s' "$json" | { grep -oE '"severity":"HIGH"' || true; } | wc -l | tr -d ' ')"
  med="$(printf '%s' "$json"  | { grep -oE '"severity":"MED"'  || true; } | wc -l | tr -d ' ')"
  low="$(printf '%s' "$json"  | { grep -oE '"severity":"LOW"'  || true; } | wc -l | tr -d ' ')"

  total_high=$((total_high + high))
  total_med=$((total_med + med))
  total_low=$((total_low + low))

  if [[ "$high" -gt 0 ]]; then
    failed_repos+=("$repo")
  elif [[ $((med + low)) -eq 0 ]]; then
    clean_repos+=("$repo")
  fi
done

# Summary
echo
echo "=========================================="
echo "PORTFOLIO AUDIT SUMMARY"
echo "=========================================="
printf '%-40s %5s %5s %5s\n' "repo" "HIGH" "MED" "LOW"
printf '%-40s %5s %5s %5s\n' "----" "----" "---" "---"

for repo in "${repos[@]}"; do
  [[ ! -d "$repo" ]] && continue
  cache_file="$cache_dir/$(_cache_key "$repo")"
  [[ ! -f "$cache_file" ]] && continue
  json="$(cat "$cache_file")"
  [[ -z "$json" ]] && continue
  h="$(printf '%s' "$json" | { grep -oE '"severity":"HIGH"' || true; } | wc -l | tr -d ' ')"
  m="$(printf '%s' "$json" | { grep -oE '"severity":"MED"'  || true; } | wc -l | tr -d ' ')"
  l="$(printf '%s' "$json" | { grep -oE '"severity":"LOW"'  || true; } | wc -l | tr -d ' ')"
  short="$(basename "$repo")"
  printf '%-40s %5s %5s %5s\n' "$short" "$h" "$m" "$l"
done

printf '%-40s %5s %5s %5s\n' "----" "----" "---" "---"
printf '%-40s %5s %5s %5s\n' "TOTAL" "$total_high" "$total_med" "$total_low"

echo
if [[ ${#failed_repos[@]} -gt 0 ]]; then
  echo "REPOS WITH HIGH-SEVERITY ISSUES (block agents):"
  for r in "${failed_repos[@]}"; do
    echo "  - $r"
  done
fi

if [[ ${#clean_repos[@]} -gt 0 ]]; then
  echo
  echo "CLEAN REPOS:"
  for r in "${clean_repos[@]}"; do
    echo "  - $r"
  done
fi

[[ "$total_high" -gt 0 ]] && exit 1
exit 0
