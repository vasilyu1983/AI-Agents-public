---
name: agents-skills
description: Comprehensive reference for creating AI agent skills (Claude Code, Codex CLI) with progressive disclosure, SKILL.md structure, references/ organization, frontmatter specification, and best practices for modular capability development.
---

# Agent Skills - Meta Reference

This skill provides the definitive reference for creating, organizing, and maintaining agent skills. Use this when building new skills or improving existing skill architecture.

## Quick Reference

| Component | Purpose | Required |
|-----------|---------|----------|
| `SKILL.md` | Main reference file with frontmatter | Yes |
| `scripts/` | Executable code (prefer running) | Optional |
| `references/` | Documentation (loaded on-demand) | Recommended |
| `assets/` | Output files (templates, icons) | Optional |
| `data/sources.json` | Curated external links | Recommended |

**Cross-Platform**: Agent Skills are designed to be portable across runtimes (Claude Code, Codex CLI, Gemini CLI, VS Code Copilot).

## Skill Structure

```text
skills/
	└── skill-name/
	    ├── SKILL.md           # Main reference (required)
	    ├── scripts/           # Executable code (Python/Bash) - prefer running; read only to patch/review
	    │   └── validate.py
	    ├── references/        # Documentation loaded into context on-demand
	    │   ├── patterns.md
	    │   └── examples.md
    ├── assets/            # Files for OUTPUT (templates, icons, fonts)
    │   └── template.html
    └── data/
        └── sources.json   # External references
```

**Directory purposes**:

- `scripts/` - Executable code; prefer running scripts and consuming output (read only when you need to modify/review)
- `references/` - Documentation loaded into context when the agent needs it
- `assets/` - Files used in generated output (not loaded into context)
 
Notes:
- Prefer executing scripts instead of pasting large code into context; read scripts only when you need to modify or review them.

## SKILL.md Template

```markdown
---
name: skill-name
description: One-line description of what this skill provides and when to use it (include trigger keywords here)
---

# Skill Name - Quick Reference

Brief overview of the skill's purpose and value.

## Quick Reference

| Task | Tool/Method | When to Use |
|------|-------------|-------------|
| Task 1 | Tool A | Context for usage |

## Scope (Optional)

Keep this brief; the primary trigger mechanism is the frontmatter `description`.

## Core Concepts

### Concept 1

Explanation with code example:

\`\`\`language
code example
\`\`\`

### Concept 2

Additional patterns...

## Navigation

**Resources**
- [references/skill-patterns.md](references/skill-patterns.md) - Common patterns
- [references/skill-validation.md](references/skill-validation.md) - Validation criteria

**Related Skills**
- [../agents-subagents/SKILL.md](../agents-subagents/SKILL.md) - Agent creation
```

## Progressive Disclosure

Skills use **progressive disclosure** to optimize token usage:

| Layer | Content | Token Cost |
|-------|---------|------------|
| **Discovery** | Name + description only | ~50 tokens |
| **Activation** | Full SKILL.md body | 2K-5K tokens |
| **Execution** | scripts/, references/, assets/ | On-demand |

**Pattern**: SKILL.md provides overview -> Resources load only when needed

**Limits**: Keep SKILL.md under **500 lines** (<5K tokens)

### When to Split Content

| Keep in SKILL.md | Move to references/ |
|------------------|-------------------|
| Decision trees | Full API references |
| Quick commands | Step-by-step tutorials |
| Common patterns | Edge case handling |
| 1-2 code examples | Complete implementations |

## Frontmatter Specification

```yaml
---
name: string                        # Required: lowercase-kebab-case, matches folder name
description: string                 # Required: PRIMARY trigger mechanism (50-300 chars)
---
```

**Name rules**:
- Use kebab-case: `ai-llm`, not `AI_LLM_Engineering`
- Match folder name exactly
- Be specific: `software-backend` not `backend`

**Description rules** (PRIMARY TRIGGER):
- Description is the primary triggering mechanism - the runtime uses it to decide when to invoke
- Include "when to use" context HERE, not in the body
- Single line, 50-300 characters
- Include key technologies/concepts as trigger keywords

Do not add extra frontmatter keys unless your runtime explicitly documents and supports them.

## Skill Categories

| Category | Prefix | Examples |
|----------|--------|----------|
| AI/ML | `ai-` | `ai-llm`, `ai-ml-data-science` |
| Software | `software-` | `software-backend`, `software-frontend` |
| Operations | `ops-` | `ops-devops-platform` |
| Data | `data-` | `data-lake-platform`, `data-sql-optimization` |
| Quality | `qa-` | `qa-debugging`, `qa-docs-coverage` |
| Developer Tools | `dev-`, `git-` | `dev-api-design`, `git-commit-message`, `dev-workflow-planning` |
| Product | `product-` | `product-management`, `docs-ai-prd` |
| Document | `document-` | `document-pdf`, `document-xlsx` |
| Testing | `testing-`, `qa-testing-` | `qa-testing-playwright`, `qa-testing-strategy` |
| Marketing | `marketing-` | `marketing-social-media`, `marketing-seo-complete` |
| Agents/Tools | `agents-` | `agents-subagents`, `agents-skills`, `agents-hooks` |

## sources.json Schema

```json
{
  "metadata": {
    "title": "Skill Name - Sources",
    "description": "Brief description",
    "last_updated": "YYYY-MM-DD",
    "skill": "skill-name"
  },
  "category_name": [
    {
      "name": "Resource Name",
      "url": "https://example.com/docs",
      "description": "What this covers",
      "add_as_web_search": true
    }
  ]
}
```

**Categories** should group logically:
- `official_documentation`
- `tutorials`
- `community_resources`
- `tools_and_libraries`

## Quality Checklist

```text
SKILL VALIDATION CHECKLIST

Frontmatter:
[ ] name matches folder name (kebab-case)
[ ] description is concise and actionable

Structure:
[ ] SKILL.md under 500 lines (split into references/ if needed)
[ ] references/ for detailed content
[ ] data/sources.json with curated links

Content:
[ ] Quick reference table at top
[ ] Frontmatter `description` includes trigger keywords
[ ] Code examples are copy-paste ready
[ ] Related skills linked at bottom

Quality:
[ ] >40% operational content (code, tables, checklists)
[ ] <50% prose paragraphs
[ ] All URLs are live (no 404s)
[ ] Sources updated within 6 months
```

## Multi-Tech vs Single-Tech Skills

### Single-Tech Skill

```text
software-backend/
├── SKILL.md              # Node.js focus
└── references/
    └── nodejs-patterns.md
```

### Multi-Tech Skill

```text
software-backend/
├── SKILL.md              # Overview + decision tree
├── references/
│   ├── nodejs-patterns.md
│   ├── go-patterns.md
│   ├── rust-patterns.md
│   └── python-patterns.md
└── assets/
    ├── nodejs/
    ├── go/
    ├── rust/
    └── python/
```

## Navigation

**Resources**
- [references/skill-patterns.md](references/skill-patterns.md) - Common skill patterns
- [references/skill-validation.md](references/skill-validation.md) - Validation criteria
- [data/sources.json](data/sources.json) - Official documentation links

**Related Skills**

- [../agents-subagents/SKILL.md](../agents-subagents/SKILL.md) - Agent creation
- [../agents-hooks/SKILL.md](../agents-hooks/SKILL.md) - Hook automation
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) - MCP server integration
