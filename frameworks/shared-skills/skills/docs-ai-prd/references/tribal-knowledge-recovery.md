# Tribal Knowledge Recovery Guide

Techniques for extracting undocumented, implicit knowledge from codebases.

---

## What is Tribal Knowledge?

Information that exists only in people's heads:
- Why certain decisions were made
- Known workarounds and gotchas
- Historical context affecting current code
- Unwritten conventions
- "That's just how we do it" patterns

---

## Git History Mining

### Find Decision Commits

```bash
# Commits explaining "why"
git log --all --oneline --grep="because\|reason\|decided\|chose\|instead of"

# Architectural changes
git log --all --oneline --grep="refactor\|migrate\|restructure\|redesign"

# Breaking changes
git log --all --oneline --grep="breaking\|BREAKING\|major change"

# Bug fix context
git log --all --oneline --grep="fix\|bug\|issue\|workaround\|hack"

# Performance decisions
git log --all --oneline --grep="performance\|optimize\|slow\|fast"
```

### Analyze Commit Messages

```bash
# Most active areas (indicates complexity/importance)
git log --oneline --all --format="%s" | cut -d: -f1 | sort | uniq -c | sort -rn | head -20

# Find commits with detailed messages (likely important context)
git log --all --format="%H %s" | while read hash msg; do
  body=$(git log -1 --format="%b" $hash)
  if [ ${#body} -gt 100 ]; then
    echo "=== $msg ==="
    echo "$body" | head -10
  fi
done
```

### Blame Analysis

```bash
# Who knows this code best?
git shortlog -sn -- path/to/important/file.ts

# When was this section last meaningfully changed?
git blame -w -C -C -C path/to/file.ts | head -30
```

---

## Comment Mining

### Find Explanatory Comments

```bash
# TODO/FIXME/HACK comments (often explain workarounds)
grep -rn "TODO\|FIXME\|HACK\|XXX\|NOTE\|WARNING" --include="*.ts" --include="*.js" --include="*.py"

# "Because" explanations
grep -rn "because\|since\|reason\|workaround" --include="*.ts" --include="*.js" --include="*.py"

# Historical context
grep -rn "legacy\|deprecated\|old\|previous\|originally" --include="*.ts" --include="*.js" --include="*.py"

# Decision comments
grep -rn "decided\|chose\|instead of\|rather than" --include="*.ts" --include="*.js" --include="*.py"
```

### Categorize Findings

| Category | Example | Document As |
|----------|---------|-------------|
| **Workaround** | `// HACK: Safari doesn't support X` | Known Gotcha |
| **Decision** | `// Using Redis instead of Memcached for persistence` | Technical Decision |
| **Debt** | `// TODO: Refactor when we have time` | Tech Debt |
| **Warning** | `// WARNING: Order matters here` | Gotcha |
| **Context** | `// Legacy from v1, kept for compatibility` | Historical Context |

---

## Documentation Archaeology

### Search Existing Docs

```bash
# Find all documentation
find . -name "README*" -o -name "*.md" -o -name "CONTRIBUTING*" | grep -v node_modules

# Search for architectural notes
grep -r "architecture\|design\|decision\|pattern" --include="*.md"

# Find API documentation
find . -name "openapi*" -o -name "swagger*" -o -name "*.yaml" | xargs grep -l "paths:"
```

### Check Configuration Files

```bash
# Environment variable documentation
cat .env.example 2>/dev/null | grep "#"

# Config file comments
find . -name "*.config.*" -exec grep -l "#\|//" {} \;

# Package.json scripts (often have hidden context)
cat package.json | jq '.scripts' | grep -v null
```

---

## Interview Patterns

If you can ask team members, use these questions:

### General Context

1. "What's the one thing you wish you knew before working on this codebase?"
2. "What's the weirdest bug you've encountered here?"
3. "Why is [specific component] structured this way?"
4. "What would you change if you could start over?"

### Technical Decisions

1. "Why did you choose [technology X] over [alternative Y]?"
2. "What constraints influenced [this design decision]?"
3. "Is there anything that looks wrong but is actually intentional?"

### Operational Knowledge

1. "What breaks most often?"
2. "What's the process when [common scenario] happens?"
3. "Are there any manual steps that aren't documented?"

---

## Pattern Recognition

### Identify Implicit Conventions

```bash
# Naming patterns
ls -la src/**/*.ts | awk -F/ '{print $NF}' | sort | uniq -c | sort -rn

# File organization patterns
tree -d -L 2 src/

# Import patterns
grep -h "import.*from" src/**/*.ts | sort | uniq -c | sort -rn | head -20
```

### Common Implicit Patterns

| Pattern | Indicator | Document As |
|---------|-----------|-------------|
| **Naming convention** | Consistent prefixes/suffixes | Convention |
| **File location rule** | Similar files in same directory | Convention |
| **Code organization** | Consistent function order | Convention |
| **Error handling** | Same try/catch patterns | Pattern |
| **Logging** | Consistent log format | Convention |

---

## Documentation Template

```markdown
## Tribal Knowledge

### Why We Made These Decisions

#### [Decision Title]
**Context**: [What problem were we solving?]
**Decision**: [What did we choose?]
**Alternatives considered**: [What else was evaluated?]
**Why this choice**: [The reasoning]
**Consequences**: [What this means for future development]

### Known Gotchas

#### [Gotcha Title]
**What**: [Description of the non-obvious behavior]
**Why**: [Historical/technical reason it exists]
**Workaround**: [How to handle it]
**Future**: [Plans to fix, if any]

### Historical Context

#### [Context Title]
**Original situation**: [How things used to be]
**What changed**: [The migration/refactor]
**Artifacts remaining**: [Legacy code/patterns still present]
**Impact on current development**: [What you need to know]

### Undocumented Processes

#### [Process Title]
**When needed**: [Trigger condition]
**Steps**: [What to do]
**Who knows more**: [Subject matter expert]
```

---

## Recovery Checklist

- [ ] Git history mined for decision commits
- [ ] TODO/FIXME/HACK comments catalogued
- [ ] README and docs reviewed
- [ ] Config files checked for comments
- [ ] Implicit naming conventions identified
- [ ] Error handling patterns documented
- [ ] Team members interviewed (if possible)
- [ ] Known gotchas listed
- [ ] Historical context captured
- [ ] Undocumented processes noted

---

## Red Flags to Document

These often indicate important tribal knowledge:

- Code that looks "wrong" but has many commits (probably intentional)
- Complex workarounds with no comments
- Disabled tests or skipped validations
- Magic numbers or hardcoded values
- Catch blocks that swallow errors
- Commented-out code that's never deleted
- Files with many authors (contentious area)
- Old dates in "temporary" solutions
