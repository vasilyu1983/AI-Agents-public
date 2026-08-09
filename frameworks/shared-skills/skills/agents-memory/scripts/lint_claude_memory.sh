#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
root="$(cd "$root" && pwd -P)"

has_issues=0

echo "Linting project memory (Claude Code + Codex) under: $root"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

files_list="$tmpdir/memory-files.txt"

find "$root" \( -type f -o -type l \) \
  \( -name 'CLAUDE.md' -o -name 'AGENTS.md' -o -name 'AGENTS.override.md' -o -name 'CLAUDE.local.md' -o \( -path '*/.claude/rules/*' -a -name '*.md' \) \) \
  -not -path '*/.archive/*' \
  -print0 \
  | while IFS= read -r -d '' path; do
      printf '%s\n' "$path"
    done \
  >"$files_list"

if [[ ! -s "$files_list" ]]; then
  echo "WARN: no memory files found (AGENTS.md / CLAUDE.md / AGENTS.override.md / CLAUDE.local.md / .claude/rules/*.md)."
  exit 0
fi

echo
echo "Memory files:"
sed 's/^/- /' "$files_list"

echo
echo "1) Size checks"
while IFS= read -r file; do
  lines="$(wc -l <"$file" | tr -d ' ')"
  if [[ "$lines" -gt 300 ]]; then
    echo "WARN: $file has $lines lines (consider splitting via .claude/rules/, docs, or nested AGENTS.md files)."
  fi
done <"$files_list"

echo
echo "2) Symlink and mirror checks"
dirs_list="$tmpdir/memory-dirs.txt"

while IFS= read -r file; do
  dirname "$file"
done <"$files_list" | sort -u >"$dirs_list"

while IFS= read -r dir; do
  claude_file="$dir/CLAUDE.md"
  agents_file="$dir/AGENTS.md"

  if [[ -L "$claude_file" && ! -e "$claude_file" ]]; then
    echo "ERROR: dangling CLAUDE.md symlink: $claude_file"
    has_issues=1
    continue
  fi

  if [[ -f "$claude_file" && -f "$agents_file" && ! -L "$claude_file" ]]; then
    if ! cmp -s "$claude_file" "$agents_file"; then
      echo "WARN: $dir has AGENTS.md and CLAUDE.md as regular files with different contents (stale mirror risk)."
    fi
  fi
done <"$dirs_list"

echo
echo "3) Secret-like tokens (hard fail)"
secret_re='(OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET_ACCESS_KEY|GITHUB_TOKEN|-----BEGIN (RSA )?PRIVATE KEY-----|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})'
secret_matches="$tmpdir/secret-matches.txt"
: >"$secret_matches"

while IFS= read -r file; do
  grep -nE "$secret_re" "$file" >>"$secret_matches" 2>/dev/null || true
done <"$files_list"

if [[ -s "$secret_matches" ]]; then
  echo "ERROR: possible secret-like material found in memory files:"
  cat "$secret_matches"
  has_issues=1
else
  echo "OK"
fi

echo
echo "4) @import targets (missing files = hard fail)"
import_re='@[A-Za-z0-9_.~-]+/[A-Za-z0-9_./~-]+'

missing_imports="$tmpdir/missing-imports.txt"
: >"$missing_imports"

while IFS= read -r file; do
  file_dir="$(cd "$(dirname "$file")" && pwd -P)"
  imports="$tmpdir/imports.txt"

  grep -oE "$import_re" "$file" 2>/dev/null | sort -u >"$imports" || true

  while IFS= read -r imp; do
    ref="${imp#@}"

    case "$ref" in
      "~/"* | "~" ) continue ;;
    esac

    if [[ "$ref" == /* ]]; then
      if [[ ! -e "$ref" ]]; then
        printf '%s: %s (missing)\n' "$file" "$imp" >>"$missing_imports"
      fi
      continue
    fi

    if [[ -e "$file_dir/$ref" || -e "$root/$ref" ]]; then
      continue
    fi

    printf '%s: %s (missing)\n' "$file" "$imp" >>"$missing_imports"
  done <"$imports"
done <"$files_list"

if [[ -s "$missing_imports" ]]; then
  echo "ERROR: missing @imports:"
  cat "$missing_imports"
  has_issues=1
else
  echo "OK"
fi

echo
if [[ "$has_issues" -eq 0 ]]; then
  echo "PASS"
  exit 0
fi

echo "FAIL"
exit 1
