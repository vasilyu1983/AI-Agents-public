# Skills Conventions

Centralized patterns and conventions for Claude Code Kit skills.

---

## Overview

This document defines conventions to:

1. **Eliminate duplication** across 50+ skills
2. **Ensure consistency** in structure and naming
3. **Enable automation** for validation and sync
4. **Simplify maintenance** with centralized definitions

---

## Directory Structure

### Standard Skill Layout

```
skill-name/
├── SKILL.md                  # Main skill file (REQUIRED)
├── README.md                 # AVOID: extraneous; prefer SKILL.md
├── data/
│   └── sources.json          # External references (REQUIRED)
├── references/
│   ├── operational-playbook.md
│   └── [topic]-best-practices.md
└── assets/
    └── template-[name].md
```

### Shared Resources

```
software-clean-code-standard/
├── SKILL-TEMPLATE.md         # Template for new skills
├── sources-schema.json       # JSON Schema for sources.json
├── skill-dependencies.json   # Dependency graph for Related Skills
└── CONVENTIONS.md            # This file
```

---

## Naming Conventions

### Skill Names

| Pattern | Example | Use When |
|---------|---------|----------|
| `domain-topic` | `software-backend` | Primary skills |
| `domain-topic-focus` | `ai-ml-data-science` | Specialized skills |
| `domain-topic-tool` | `qa-testing-playwright` | Tool-specific skills |

### File Names

| Type | Pattern | Example |
|------|---------|---------|
| Best practices | `[topic]-best-practices.md` | `nodejs-best-practices.md` |
| Patterns | `[topic]-patterns.md` | `fullstack-patterns.md` |
| Playbooks | `operational-playbook.md` | (standard name) |
| Templates | `template-[stack]-[variant].md` | `template-nodejs-prisma-postgres.md` |

### Directory Names

- All lowercase
- Kebab-case: `qa-testing-playwright`
- No underscores in skill names

---

## Version References

### Required Format

Always include explicit versions in:

1. **Frontmatter description**
2. **Modern Best Practices section**
3. **Quick Reference table**
4. **Decision trees**

### Version Notation

| Format | Example | Meaning |
|--------|---------|---------|
| Exact | `Node.js 24.11.0` | Specific version |
| Minor range | `Express 5.x` | Any 5.x version |
| Minimum | `Python 3.14+` | 3.14 or higher |
| LTS | `Node.js 24 LTS` | Long-term support |
| Current | `Node.js 25 Current` | Latest non-LTS |

### Version Sources

Centralized in `/.claude/skills/tech-stack-updater/data/version-registry.json`

Update versions using: `/update-tech-versions`

---

## Section Standards

### SKILL.md Required Sections

```markdown
# [Skill Name] — Quick Reference    ← H1 title with "Quick Reference"

[Intro paragraph]

**Modern Best Practices (Month Year)**: ...    ← Always include month/year

---

## Quick Reference                  ← 4-column table

## When to Use This Skill           ← Bullet list

## Decision Tree: [Topic]           ← Text-based tree

---

## Navigation                       ← Three subsections

**Resources**
**Templates**
**Related Skills**

---

## Operational Playbooks            ← Optional
```

### Quick Reference Table Format

```markdown
| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
```

All 4 columns required. Include versions in Tool/Framework column.

### Decision Tree Format

```text
Project needs: [Decision Point]
    ├─ Option A?
    │   ├─ Sub-option → Tool v1.x (reason)
    │   └─ Sub-option → Tool v2.x (reason)
    │
    └─ Option B?
        └─ Sub-option → Tool (reason)
```

Use `├─`, `│`, `└─` characters. Max 4 levels deep.

---

## Related Skills

### Auto-Generation

Related Skills sections can be auto-generated from `skill-dependencies.json`.

```json
{
  "skill-name": {
    "primary": ["skill-1", "skill-2"],
    "secondary": ["skill-3", "skill-4"],
    "description_map": {
      "skill-1": "Brief description of relationship"
    }
  }
}
```

### Manual Format

```markdown
**Related Skills**
- [../related-skill/SKILL.md](../related-skill/SKILL.md) — Description
```

- Use relative paths: `../skill-name/SKILL.md`
- Include 3-8 related skills
- One-line descriptions

---

## Sources Schema

### Required Fields

```json
{
  "metadata": {
    "skill": "skill-name",           // REQUIRED: kebab-case
    "updated": "YYYY-MM-DD",         // REQUIRED: ISO date
    "total_sources": 45              // REQUIRED: count
  },
  "categories": {
    "category_name": [
      {
        "name": "Resource Name",     // REQUIRED
        "url": "https://...",        // REQUIRED: HTTPS only
        "type": "documentation",     // REQUIRED: from enum
        "relevance": "Why useful"    // REQUIRED: 10-300 chars
      }
    ]
  }
}
```

### Type Enum

```
documentation, tutorial, reference, tool, examples,
framework, library, guide, blog, course, book,
video, podcast, specification, announcement, research
```

### Validation

Validate against `sources-schema.json`:

```bash
npx --yes -p ajv-cli@5.0.0 -p ajv-formats@3.0.1 ajv validate -c ajv-formats -s software-clean-code-standard/sources-schema.json -d skill-name/data/sources.json
```

---

## Cross-Skill Patterns

### Avoiding Duplication

| Pattern | Instead Of | Use |
|---------|------------|-----|
| Shared templates | Copy-paste templates | Reference `software-clean-code-standard/SKILL-TEMPLATE.md` |
| Dependency graph | Manual Related Skills | Use `skill-dependencies.json` |
| Version registry | Hardcoded versions | Reference `version-registry.json` |
| Common playbooks | Duplicate checklists | Link to shared resource |

### Common Content to Centralize

1. **Technology versions** → `version-registry.json`
2. **Related Skills descriptions** → `skill-dependencies.json`
3. **Sources schema** → `sources-schema.json`
4. **Skill structure** → `SKILL-TEMPLATE.md`
5. **Code utilities** → `references/*.md`

---

## Clean Code in Templates

Templates should guide users to create **centralized utilities** instead of duplicated code.

### Utility Centralization Guides

| Utility | Guide | Location in Project |
|---------|-------|---------------------|
| Auth (JWT, password) | [references/auth-utilities.md](references/auth-utilities.md) | `src/utils/auth.ts` |
| Error handling | [references/error-handling.md](references/error-handling.md) | `src/utils/errors.ts` |
| Config validation | [references/config-validation.md](references/config-validation.md) | `src/config/index.ts` |
| Resilience (retry, circuit breaker) | [references/resilience-utilities.md](references/resilience-utilities.md) | `src/utils/resilience.ts` |
| Logging | [references/logging-utilities.md](references/logging-utilities.md) | `src/utils/logger.ts` |
| Testing (fixtures, mocks) | [references/testing-utilities.md](references/testing-utilities.md) | `src/test/factories.ts` |
| Observability (tracing, metrics) | [references/observability-utilities.md](references/observability-utilities.md) | `src/utils/telemetry.ts` |
| LLM (tokens, streaming, costs) | [references/llm-utilities.md](references/llm-utilities.md) | `src/utils/llm.ts` |

### Template Requirements

All code templates MUST include a **Centralization Guide** section after project structure:

```markdown
## Centralization Guide

> **Important**: Extract utilities to shared modules. Do not duplicate.

| Utility | Extract To | Reference |
|---------|------------|-----------|
| JWT, password | `src/utils/auth.ts` | [auth-utilities.md](...) |
| Errors | `src/utils/errors.ts` | [error-handling.md](...) |
```

### Code Anti-Patterns to Avoid

Templates should NOT show:

```typescript
// BAD: Inline utility in service
// user.service.ts
const hashPassword = async (pw: string) => bcrypt.hash(pw, 10);

// BAD: Duplicated in another file
// admin.service.ts
const hashPassword = async (pw: string) => bcrypt.hash(pw, 10);
```

Templates SHOULD show:

```typescript
// GOOD: Import from centralized utility
import { hashPassword } from '@/utils/auth';
```

### Checklist for Template Authors

- [ ] Includes "Centralization Guide" section
- [ ] Links to `references/*.md` for common patterns
- [ ] Shows import statements, not inline implementations
- [ ] Uses path aliases (`@/utils/`) for clean imports
- [ ] No duplicated functions across code examples

---

## Quality Checklist

### Before Committing a Skill

- [ ] YAML frontmatter has `name` and `description`
- [ ] Description includes key versions, under 300 chars
- [ ] Modern Best Practices section has (Month Year)
- [ ] Quick Reference table has all 4 columns
- [ ] When to Use has 3+ bullet points
- [ ] Decision tree uses correct characters
- [ ] Navigation has Resources, Templates, Related Skills
- [ ] All internal links are valid relative paths
- [ ] sources.json validates against schema
- [ ] No content duplicated from other skills
- [ ] Versions match version-registry.json

### Validation Commands

```bash
# Check character limit
wc -c skill-name/SKILL.md

# Validate sources.json
npx --yes -p ajv-cli@5.0.0 -p ajv-formats@3.0.1 ajv validate -c ajv-formats -s software-clean-code-standard/sources-schema.json -d skill-name/data/sources.json

# Check for broken links
python3 - <<'PY'
import re
from pathlib import Path

skill_md = Path("skill-name/SKILL.md")
text = skill_md.read_text(encoding="utf-8")

for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
    target = match.group(1)
    if target.startswith(("http://", "https://", "mailto:")):
        continue
    target = target.split("#", 1)[0]
    if not target:
        continue
    resolved = (skill_md.parent / target)
    if not resolved.exists():
        raise SystemExit(f"Broken link: {target}")

print("OK: no broken file links in SKILL.md")
PY

# Find duplicate content
rg "Modern Best Practices" */SKILL.md
```

---

## Maintenance

### Adding a New Skill

1. Copy `software-clean-code-standard/SKILL-TEMPLATE.md` to `skill-name/SKILL.md`
2. Create `skill-name/data/sources.json` following schema
3. Add to `skill-dependencies.json`
4. Run `/validate-skill skill-name`

### Updating Versions

1. Run `/update-tech-versions`
2. Review generated report
3. Update affected skills

### Syncing to Other Kits

1. Validate: `/validate-skill skill-name`
2. Sync: `/sync-kits skill skill-name`
3. Verify: `/sync-kits validate-all`

---

## Anti-Patterns

### Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Copy-paste sections | Drift, maintenance burden | Use shared templates |
| Hardcoded versions | Outdated quickly | Reference version-registry |
| Manual Related Skills | Inconsistent, incomplete | Use skill-dependencies.json |
| Long SKILL.md | Slow loading, hard to navigate | Progressive disclosure |
| Duplicate sources | Wasted tokens | Centralize common sources |
| Mixed naming conventions | Confusion | Follow conventions strictly |

---

## Migration Guide

### Updating Existing Skills

1. **Check structure** against SKILL-TEMPLATE.md
2. **Add missing sections** (Modern Best Practices, Navigation)
3. **Update versions** from version-registry.json
4. **Validate sources.json** against schema
5. **Add to skill-dependencies.json**
6. **Run validation**: `/validate-skill skill-name`

### Batch Updates

```bash
# Find skills missing Modern Best Practices
rg -L "Modern Best Practices" */SKILL.md

# Find outdated versions
rg "Node.js 2[0-3]" */SKILL.md

# Find skills not in dependencies
diff <(ls -d */ | sed 's/\///') <(jq -r '.dependencies | keys[]' software-clean-code-standard/skill-dependencies.json)
```
