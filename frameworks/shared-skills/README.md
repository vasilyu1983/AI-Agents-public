# Shared Skills

Reusable AI coding agent skills for Claude Code, Codex CLI, and Gemini CLI.

## Structure

```text
shared-skills/
├── skills/           # 62 domain skills
│   ├── ai-agents/
│   ├── ai-llm/
│   ├── ...
│   └── INDEX.md      # Complete catalog
└── README.md         # This file
```

## Usage

### Install Skills in a Repo

Copy skills into your AI coding agent workspace:

```bash
# Claude Code
cp -r frameworks/shared-skills/skills/ /path/to/repo/.claude/skills/

# Codex CLI
cp -r frameworks/shared-skills/skills/ /path/to/repo/.codex/skills/
```

**Note**: The source of truth is `frameworks/shared-skills/skills/`. Avoid editing workspace copies directly if you want repeatable updates.

### Workflow

1. Clone this repo
2. Copy skills into your target repo workspace
3. Skills auto-activate based on context

## Skill Format

Skills follow the [Agent Skills specification](https://agentskills.io/specification):

```text
skill-name/
├── SKILL.md          # Required: frontmatter + instructions
├── data/
│   └── sources.json  # Curated web resources
├── references/       # Detailed documentation (loaded on-demand)
├── assets/           # Static resources: templates, images, data files
└── scripts/          # Executable code (Python, Bash, JS)
```

This repository intentionally avoids per-skill `README.md`. Put essential overview content in `SKILL.md`.

## Target Platforms

| Platform | Workspace Path | Notes |
| --- | ---- | ----- |
| Claude Code | `.claude/skills/` | Loaded by Claude Code |
| Codex CLI | `.codex/skills/` | Loaded by Codex CLI |
| Gemini CLI | `.gemini/skills/` | Via GEMINI.md configuration |

## Multi-Repo Workspaces

When working with multiple repositories, avoid duplicating skills across repos. Instead:

### Recommended: Workspace-Level Skills

```text
workspace/
├── .claude/                    # Shared skills (single source)
│   └── skills/
│       └── shared-api-design/
├── repo-a/
│   └── .claude/CLAUDE.md       # Repo-specific context only
└── repo-b/
    └── .claude/CLAUDE.md       # Repo-specific context only
```

**Why:**

- Claude Code [auto-discovers skills from nested directories](https://code.claude.com/docs/en/skills)
- No copy-paste drift between repos
- Saves 40-60% token budget vs duplicated skills

### Multi-Repo Commands

```bash
# Add repos to session
/add-dir ../other-repo
claude --add-dir ../frontend --add-dir ../backend
```

### Decision Guide

| Situation                    | Approach                          |
|------------------------------|-----------------------------------|
| Repos share domain knowledge | Workspace-level `.claude/skills/` |
| Independent projects         | Repo-level `.claude/` only        |
| Enterprise standardization   | Managed org-wide skills           |

**Resources:** [Multi-Repo Context Loading](https://blackdoglabs.io/blog/claude-code-decoded-multi-repo-context)

## Large Codebase Documentation (100K-1M LOC)

For repositories with 100K-1M lines of code, use the `agents-project-memory` skill:

**Key patterns:**

- Keep root CLAUDE.md under ~300 lines
- Use hierarchical structure: subdirectory docs auto-load when needed
- Symlink strategy: `ln -s AGENTS.md CLAUDE.md` for cross-platform support

**Skill chain:**

```text
agents-project-memory → qa-docs-coverage → docs-codebase
```

**Official sources:**

- [Anthropic Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [OpenAI AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md)

## See Also

- [Skills INDEX](skills/INDEX.md) - Complete skill catalog
- [Agent Skills Spec](https://agentskills.io/specification) - Official format
