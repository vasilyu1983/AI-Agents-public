#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
root="$(cd "$root" && pwd -P)"

if ! command -v rg >/dev/null 2>&1; then
  echo "ERROR: ripgrep (rg) is required." >&2
  exit 2
fi

has_issues=0

echo "Linting project memory (Claude Code + Codex) under: $root"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

files_list="$tmpdir/memory-files.txt"

find "$root" \( -type f -o -type l \) \
  \( -name 'CLAUDE.md' -o -name 'AGENTS.md' -o -name 'CLAUDE.local.md' -o \( -path '*/.claude/rules/*' -a -name '*.md' \) \) \
  -not -path '*/.archive/*' \
  -print0 \
  | while IFS= read -r -d '' path; do
      printf '%s\n' "$path"
    done \
  >"$files_list"

if [[ ! -s "$files_list" ]]; then
  echo "WARN: no memory files found (AGENTS.md / CLAUDE.md / CLAUDE.local.md / .claude/rules/*.md)."
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
    echo "WARN: $file has $lines lines (consider splitting via .claude/rules/ and @imports)."
  fi
done <"$files_list"

echo
echo "2) Secret-like tokens (hard fail)"
secret_re='(OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET_ACCESS_KEY|GITHUB_TOKEN|-----BEGIN (RSA )?PRIVATE KEY-----|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})'
secret_matches="$tmpdir/secret-matches.txt"
: >"$secret_matches"

while IFS= read -r file; do
  rg -n --no-heading "$secret_re" "$file" >>"$secret_matches" 2>/dev/null || true
done <"$files_list"

if [[ -s "$secret_matches" ]]; then
  echo "ERROR: possible secret-like material found in memory files:"
  cat "$secret_matches"
  has_issues=1
else
  echo "OK"
fi

echo
echo "3) @import targets (missing files = hard fail)"
import_re='@[A-Za-z0-9_.~-]+/[A-Za-z0-9_./~-]+'

missing_imports="$tmpdir/missing-imports.txt"
: >"$missing_imports"

while IFS= read -r file; do
  file_dir="$(cd "$(dirname "$file")" && pwd -P)"
  imports="$tmpdir/imports.txt"

  rg -oN "$import_re" "$file" | sort -u >"$imports" || true

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
