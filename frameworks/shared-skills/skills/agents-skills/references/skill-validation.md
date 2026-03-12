# Skill Validation Criteria

Comprehensive checklist for validating agent skills.

## Validation Levels

| Level | When | Checks |
|-------|------|--------|
| **Quick** | During development | Frontmatter, structure |
| **Standard** | Before commit | + Links, sources, content |
| **Full** | Before release | + Web search, best practices |

## 1. Frontmatter Validation (Critical)

```bash
# Check first 5 lines
head -5 SKILL.md
```

**Requirements:**

| Field | Rule | Example |
|-------|------|---------|
| `name` | kebab-case, matches folder | `software-backend` |
| `description` | ~150 chars (budget: 16K shared), includes triggers | "Backend APIs for Node.js. Use when..." |

**Validation regex:**

```bash
# Name format
grep -E "^name: [a-z0-9-]+$" SKILL.md

# Description length
desc=$(grep "^description:" SKILL.md | cut -d: -f2-)
echo ${#desc}  # Should be 50-300
```

## 2. Directory Structure

**Required:**

```text
skill-name/
└── SKILL.md           # Must exist
```

**Recommended:**

```text
skill-name/
├── SKILL.md
├── data/
│   └── sources.json   # Curated external links
└── references/         # If referenced in SKILL.md
```

**Validation:**

```bash
# Check required file
[ -f "SKILL.md" ] && echo "PASS" || echo "FAIL: Missing SKILL.md"

# Check for orphan references
grep -oE '\[.*\]\(references/[^)]+\)' SKILL.md | while read link; do
  path=$(echo "$link" | grep -oE 'references/[^)]+')
  [ -f "$path" ] || echo "DEAD LINK: $path"
done
```

## 3. Reference Link Validation (Critical)

All markdown links must resolve:

```bash
# Extract and validate all relative links
grep -oE '\]\([^http][^)]+\)' SKILL.md | tr -d '()' | cut -d']' -f2 | while read path; do
  [ -e "$path" ] || echo "DEAD: $path"
done
```

**Common issues:**

| Issue | Fix |
|-------|-----|
| `references/file.md` missing | Create file or remove link |
| `../other-skill/SKILL.md` missing | Check skill exists |
| Typo in path | Correct the path |

## 4. sources.json Validation

**Schema check:**

```bash
# Valid JSON
python3 -m json.tool data/sources.json > /dev/null && echo "PASS"

# Required fields
jq '.metadata.last_updated' data/sources.json  # Must exist
jq '.metadata.skill' data/sources.json         # Must match folder
```

**URL validation:**

```bash
# All URLs must be HTTPS
jq -r '.. | .url? // empty' data/sources.json | grep -v "^https://" && echo "FAIL: Non-HTTPS URL"

# Check for redirects (warning)
jq -r '.. | .url? // empty' data/sources.json | while read url; do
  status=$(curl -sI "$url" | head -1 | cut -d' ' -f2)
  [ "$status" = "301" ] && echo "REDIRECT: $url"
done
```

**Freshness:**

```bash
# Last updated within 6 months
last=$(jq -r '.metadata.last_updated' data/sources.json)
# Compare with current date
```

## 5. Content Quality

### Required Sections

| Section | Purpose | Check |
|---------|---------|-------|
| Quick Reference | Fast lookup table | `grep "## Quick Reference"` |
| Frontmatter `description` | Trigger context | `grep "^description:" SKILL.md` |
| Navigation | Cross-references | `grep "## Navigation"` |

### Operational Content Ratio

Target: **>40% operational** (code, tables, checklists)

```bash
# Count operational lines
total=$(wc -l < SKILL.md)
code=$(grep -c '```' SKILL.md)
tables=$(grep -c '^|' SKILL.md)
lists=$(grep -c '^- \[' SKILL.md)

operational=$((code + tables + lists))
ratio=$((operational * 100 / total))
echo "Operational: ${ratio}%"
```

### Anti-Fluff Check

Flag excessive prose:

```bash
# Paragraphs without code/lists
awk '/^[A-Z].*\.$/ && !/```/ && !/^|/ && !/^-/' SKILL.md | wc -l
```

## 6. Best Practices Alignment (Web Search)

**Automated checks:**

1. Search: `"[skill topic] best practices 2025 2026"`
2. Compare skill content with top 3 results
3. Flag deprecated tools/patterns

**Manual review:**

| Check | Pass Criteria |
|-------|---------------|
| Tools current | No deprecated libraries |
| Patterns match docs | Aligns with official documentation |
| Security advice | Matches OWASP/NIST current guidance |
| Examples work | Code samples are copy-paste ready |

## 7. Security Validation

```bash
# No shell injection patterns
grep -E '\$\(|`.*`|\beval\b' SKILL.md && echo "WARN: Potential injection"

# No credential patterns
grep -Ei 'password|secret|api.?key|token' SKILL.md && echo "WARN: Credential reference"

# No file access outside workspace
grep -E '\.\./\.\./|/etc/|/usr/' SKILL.md && echo "WARN: External path"
```

## Validation Output Format

```markdown
## Validation Summary

- **Status**: [PASS | FAIL | WARNING]
- **Skill**: `skill-name`
- **Issues**: X critical, Y warnings

## Critical Issues
[List or "None"]

## Warnings
[List or "None"]

## Recommendations
[List or "None"]
```

## Quick Validation Script

```bash
#!/bin/bash
SKILL_DIR="$1"

echo "Validating: $SKILL_DIR"

# 1. SKILL.md exists
[ -f "$SKILL_DIR/SKILL.md" ] || { echo "FAIL: Missing SKILL.md"; exit 1; }

# 2. Frontmatter valid
head -1 "$SKILL_DIR/SKILL.md" | grep -q "^---$" || echo "WARN: Missing frontmatter"

# 3. Name matches folder
name=$(grep "^name:" "$SKILL_DIR/SKILL.md" | cut -d: -f2 | tr -d ' ')
folder=$(basename "$SKILL_DIR")
[ "$name" = "$folder" ] || echo "FAIL: Name mismatch ($name != $folder)"

# 4. sources.json valid
if [ -f "$SKILL_DIR/data/sources.json" ]; then
  python3 -m json.tool "$SKILL_DIR/data/sources.json" > /dev/null || echo "FAIL: Invalid JSON"
fi

# 5. Dead links
grep -oE '\]\(references/[^)]+\)' "$SKILL_DIR/SKILL.md" | while read link; do
  path=$(echo "$link" | grep -oE 'references/[^)]+')
  [ -f "$SKILL_DIR/$path" ] || echo "DEAD LINK: $path"
done

echo "Validation complete"
```

## Related

- [skill-patterns.md](skill-patterns.md) - Common skill patterns
- [../SKILL.md](../SKILL.md) - Main skill reference
