# SKILL-TEMPLATE.md

Copy this file into a new skill folder and edit.

For conventions and validation rules, see: [CONVENTIONS.md](CONVENTIONS.md)

---

## Required File: SKILL.md (Skeleton)

```markdown
---
name: skill-name
description: One sentence describing when to use this skill (include key versions when relevant).
---

# Skill Name — Quick Reference

One paragraph explaining what this skill provides and when to use it.

**Modern Best Practices (Month Year)**: Key technologies with versions, recent changes, and current recommendations.

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Task 1 | Tool v1.x | `command` | Use case |
| Task 2 | Tool v2.x | `command` | Use case |

## When to Use This Skill

Use this skill when the user requests:

- Use case 1
- Use case 2
- Use case 3

## Decision Tree: [Primary Decision]

\`\`\`text
Project needs: [Decision Point]
    ├─ Option A?
    │   ├─ Sub-option A1 → Tool (reason)
    │   └─ Sub-option A2 → Tool (reason)
    │
    └─ Option B?
        └─ Sub-option B1 → Tool (reason)
\`\`\`

---

## Navigation

**Resources**
- [data/sources.json](data/sources.json) — Curated external references
- [references/](references/) — Deep dives and playbooks (recommended)

**Templates**
- [assets/](assets/) — Optional starter templates

**Related Skills**
- [../related-skill/SKILL.md](../related-skill/SKILL.md) — Why it is related

---

## Operational Playbooks
- (Optional) Link to a `references/operational-playbook.md` when the skill has substantial operational content.
```

---

## Recommended Directory Structure

```
skill-name/
├── SKILL.md                           # Main skill file (required)
├── README.md                          # AVOID: extraneous; prefer SKILL.md
├── data/
│   └── sources.json                   # External references (required)
├── references/
│   ├── operational-playbook.md        # Checklists, decisions (optional)
│   └── [topic]-best-practices.md      # Topic guides (optional)
└── assets/
    └── template-[name].md             # Production starters (optional)
```

---

## Centralization Guide

> **Important**: Extract shared utilities instead of duplicating them in controllers/services.

| Utility | Extract To | Reference |
|---------|------------|-----------|
| JWT, password | `src/utils/auth.ts` | [references/auth-utilities.md](references/auth-utilities.md) |
| Errors | `src/utils/errors.ts` | [references/error-handling.md](references/error-handling.md) |
| Config validation | `src/config/index.ts` | [references/config-validation.md](references/config-validation.md) |
| Logging | `src/utils/logger.ts` | [references/logging-utilities.md](references/logging-utilities.md) |
| Resilience (retry/circuit breaker) | `src/utils/resilience.ts` | [references/resilience-utilities.md](references/resilience-utilities.md) |

**Pattern**: Show imports from these utilities in examples (e.g., `import { hashPassword } from '@/utils/auth';`) instead of redefining helpers inline.

---

## Required: data/sources.json (Example)

`data/sources.json` MUST validate against [sources-schema.json](sources-schema.json).

```json
{
  "metadata": {
    "skill": "skill-name",
    "updated": "YYYY-MM-DD",
    "total_sources": 1,
    "description": "Brief description of sources coverage"
  },
  "categories": {
    "official_documentation": [
      {
        "name": "Resource Name",
        "url": "https://example.com",
        "type": "documentation",
        "relevance": "Why this resource matters (10-300 chars)",
        "add_as_web_search": true
      }
    ]
  }
}
```

---

## Validation

Validate sources JSON:

```bash
npx --yes -p ajv-cli@5.0.0 -p ajv-formats@3.0.1 ajv validate -c ajv-formats -s software-clean-code-standard/sources-schema.json -d skill-name/data/sources.json
```
