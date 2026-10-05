# Audit Commands Reference

Quick commands for docs folder analysis.

---
## Table of Contents

- [Tooling Fallbacks](#tooling-fallbacks)
- [Discovery Commands](#discovery-commands)
- [List all docs with line counts (sorted)](#list-all-docs-with-line-counts-sorted)
- [Count total lines](#count-total-lines)
- [List files by category](#list-files-by-category)
- [Find large files (>200 lines)](#find-large-files-200-lines)
- [Find potential duplicates (similar names)](#find-potential-duplicates-similar-names)
- [Content Analysis](#content-analysis)
- [Find generic theory signals](#find-generic-theory-signals)
- ["Why X matters" sections](#why-x-matters-sections)
- ["What is X" sections](#what-is-x-sections)
- ["Best practices" (often generic)](#best-practices-often-generic)
- [Template/example sections (may be generic)](#templateexample-sections-may-be-generic)
- [Find project-specific signals](#find-project-specific-signals)
- [YOUR numbers (prices, metrics)](#your-numbers-prices-metrics)
- [YOUR endpoints](#your-endpoints)
- [YOUR code references](#your-code-references)
- [YOUR decisions](#your-decisions)
- [Redundancy Detection](#redundancy-detection)
- [Find files with similar content](#find-files-with-similar-content)
- [Compare two files for similarity (requires diff)](#compare-two-files-for-similarity-requires-diff)
- [Find orphan files (not referenced anywhere)](#find-orphan-files-not-referenced-anywhere)
- [List all md files, check if referenced in other files](#list-all-md-files-check-if-referenced-in-other-files)
- [Cleanup Commands](#cleanup-commands)
- [Remove empty files](#remove-empty-files)
- [Find and remove backup files](#find-and-remove-backup-files)
- [Reporting](#reporting)
- [Generate simple audit summary](#generate-simple-audit-summary)


## Tooling Fallbacks

If a tool isn’t installed, use these equivalents:

- No `tree`: `find . -maxdepth 3 -print | sed 's|[^/]*/|  |g'` (or just `find . -maxdepth 3 -print`)
- No `jq` for `package.json`: `node -p "JSON.stringify(require('./package.json').dependencies, null, 2)"` (and swap `dependencies` for `devDependencies`)

---

## Discovery Commands

### List all docs with line counts (sorted)

```bash
find docs/ -name "*.md" -exec wc -l {} \; | sort -rn
```

### Count total lines

```bash
find docs/ -name "*.md" -exec cat {} \; | wc -l
```

### List files by category

```bash
find docs/ -mindepth 1 -maxdepth 2 -name "*.md" | sort
```

### Find large files (>200 lines)

```bash
find docs/ -name "*.md" -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -gt 200 ] && echo "$lines $1"' _ {} \; | sort -rn
```

### Find potential duplicates (similar names)

```bash
find docs/ -name "*.md" | xargs -I {} basename {} | sort | uniq -d
```

---

## Content Analysis

### Find generic theory signals

```bash
# "Why X matters" sections
grep -r "why.*matters" docs/ --include="*.md" -l

# "What is X" sections
grep -r "^## What is" docs/ --include="*.md" -l

# "Best practices" (often generic)
grep -r "best practices" docs/ --include="*.md" -l

# Template/example sections (may be generic)
grep -r "^## Template" docs/ --include="*.md" -l
grep -r "^## Example" docs/ --include="*.md" -l
```

### Find project-specific signals

```bash
# YOUR numbers (prices, metrics)
grep -rE '\$[0-9]+|\d+%|\d+K' docs/ --include="*.md" | head -20

# YOUR endpoints
grep -r "/api/" docs/ --include="*.md" -l

# YOUR code references
grep -r "src/" docs/ --include="*.md" -l

# YOUR decisions
grep -ri "we chose\|we decided\|our approach" docs/ --include="*.md" -l
```

---

## Redundancy Detection

### Find files with similar content

```bash
# Compare two files for similarity (requires diff)
diff -y --suppress-common-lines file1.md file2.md | wc -l
```

### Find orphan files (not referenced anywhere)

```bash
# List all md files, check if referenced in other files
for f in $(find docs/ -name "*.md"); do
  base=$(basename "$f")
  refs=$(grep -r "$base" docs/ --include="*.md" -l | grep -v "$f" | wc -l)
  [ "$refs" -eq 0 ] && echo "ORPHAN: $f"
done
```

---

## Cleanup Commands

### Remove empty files

```bash
find docs/ -name "*.md" -empty -delete
```

### Find and remove backup files

```bash
find docs/ -name "*.md.bak" -delete
find docs/ -name "*~" -delete
```

---

## Reporting

### Generate simple audit summary

```bash
echo "=== Docs Audit Summary ==="
echo "Total files: $(find docs/ -name '*.md' | wc -l)"
echo "Total lines: $(find docs/ -name '*.md' -exec cat {} \; | wc -l)"
echo ""
echo "=== Top 10 Largest Files ==="
find docs/ -name "*.md" -exec wc -l {} \; | sort -rn | head -10
echo ""
echo "=== Files by Directory ==="
find docs/ -mindepth 1 -maxdepth 1 -type d -exec sh -c 'echo "$(find "$1" -name "*.md" | wc -l) $1"' _ {} \; | sort -rn
```
