#!/usr/bin/env bash
# compare_blocks.sh — find AGENTS.md sections that appear in multiple repos
# and report whether they are identical, near-identical, or divergent.
#
# Use this to find alignment candidates (sections that should stay in sync
# across the portfolio) and intentional divergences (sections customized
# per-repo that should NOT be aligned).
#
# Usage:
#   compare_blocks.sh <repo1> <repo2> [<repo3> ...]
#   compare_blocks.sh --section "Agent Routing" <repo1> <repo2> ...
#
# Output: per-section table showing identical/near/divergent across repos.

set -euo pipefail

filter_section=""
if [[ "${1:-}" == "--section" ]]; then
  filter_section="${2:?--section requires a name}"
  shift 2
fi

repos=("$@")
if [[ ${#repos[@]} -lt 2 ]]; then
  echo "Usage: $0 [--section <name>] <repo1> <repo2> [<repo3> ...]" >&2
  exit 2
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

# Extract a section by H2 heading from a markdown file.
# Args: file, section_name
# Output: section body to stdout.
extract_section() {
  local file="$1" name="$2"
  awk -v name="$name" '
    BEGIN { in_section = 0 }
    /^## / {
      if (in_section) exit
      heading = $0
      sub(/^## /, "", heading)
      if (heading == name) in_section = 1
      next
    }
    in_section { print }
  ' "$file"
}

# List all H2 sections across all input repos.
sections_file="$tmpdir/sections.txt"
: >"$sections_file"
for repo in "${repos[@]}"; do
  agents="$repo/AGENTS.md"
  [[ -e "$agents" ]] || continue
  grep -E '^## ' "$agents" | sed 's/^## //' >>"$sections_file"
done

unique_sections="$tmpdir/unique-sections.txt"
sort "$sections_file" | uniq -c | awk '$1 >= 2 { sub(/^ +[0-9]+ /,""); print }' >"$unique_sections"

if [[ -n "$filter_section" ]]; then
  echo "$filter_section" >"$unique_sections"
fi

if [[ ! -s "$unique_sections" ]]; then
  echo "No sections appear in 2+ repos."
  exit 0
fi

echo "=========================================="
echo "SHARED SECTION ALIGNMENT REPORT"
echo "Repos: ${repos[*]}"
echo "=========================================="

while IFS= read -r section; do
  [[ -z "$section" ]] && continue

  # Extract this section from each repo
  bodies=()
  repo_labels=()
  for repo in "${repos[@]}"; do
    agents="$repo/AGENTS.md"
    [[ -e "$agents" ]] || continue
    body_file="$tmpdir/$(echo "$repo" | tr '/' '_')-$(echo "$section" | tr ' /' '__').md"
    extract_section "$agents" "$section" >"$body_file"
    if [[ -s "$body_file" ]]; then
      bodies+=("$body_file")
      repo_labels+=("$(basename "$repo")")
    fi
  done

  count=${#bodies[@]}
  [[ $count -lt 2 ]] && continue

  # Compute pairwise hashes to classify
  hashes=()
  for b in "${bodies[@]}"; do
    h="$(md5 -q "$b" 2>/dev/null || md5sum "$b" | awk '{print $1}')"
    hashes+=("$h")
  done

  # All same?
  all_same=1
  first_hash="${hashes[0]}"
  for h in "${hashes[@]:1}"; do
    [[ "$h" != "$first_hash" ]] && all_same=0
  done

  echo
  echo "## $section"
  if [[ $all_same -eq 1 ]]; then
    echo "  status: IDENTICAL across $count repos (${repo_labels[*]})"
    echo "  note: candidate for alignment via shared file or symlink"
    continue
  fi

  # Compute pairwise line-similarity (simple): count common lines / max lines
  echo "  status: DIVERGENT across $count repos"
  for ((i=0; i<count; i++)); do
    lines_i="$(wc -l <"${bodies[$i]}" | tr -d ' ')"
    printf '  - %-30s %s lines\n' "${repo_labels[$i]}" "$lines_i"
  done

  # Pairwise diffs (line-count similarity)
  echo "  pairwise similarity (common-lines / max-lines):"
  for ((i=0; i<count; i++)); do
    for ((j=i+1; j<count; j++)); do
      common="$(grep -Fxf "${bodies[$i]}" "${bodies[$j]}" 2>/dev/null | wc -l | tr -d ' ')"
      max_i="$(wc -l <"${bodies[$i]}" | tr -d ' ')"
      max_j="$(wc -l <"${bodies[$j]}" | tr -d ' ')"
      max=$(( max_i > max_j ? max_i : max_j ))
      [[ $max -eq 0 ]] && max=1
      pct=$(( common * 100 / max ))
      printf '    %s vs %s: %d%% (%s common / %s max)\n' \
        "${repo_labels[$i]}" "${repo_labels[$j]}" "$pct" "$common" "$max"
    done
  done

  # If any pair >80%, flag as alignment candidate
  highest=0
  for ((i=0; i<count; i++)); do
    for ((j=i+1; j<count; j++)); do
      common="$(grep -Fxf "${bodies[$i]}" "${bodies[$j]}" 2>/dev/null | wc -l | tr -d ' ')"
      max_i="$(wc -l <"${bodies[$i]}" | tr -d ' ')"
      max_j="$(wc -l <"${bodies[$j]}" | tr -d ' ')"
      max=$(( max_i > max_j ? max_i : max_j ))
      [[ $max -eq 0 ]] && max=1
      pct=$(( common * 100 / max ))
      [[ $pct -gt $highest ]] && highest=$pct
    done
  done

  if [[ $highest -ge 80 ]]; then
    echo "  → ALIGNMENT CANDIDATE: high overlap suggests these should be reconciled"
  elif [[ $highest -ge 40 ]]; then
    echo "  → REVIEW: moderate overlap; verify divergence is intentional"
  else
    echo "  → DIVERGENT: low overlap; likely intentionally different per repo"
  fi
done <"$unique_sections"

echo
echo "Done. To diff a specific section in detail:"
echo "  $0 --section \"<name>\" ${repos[*]}"
