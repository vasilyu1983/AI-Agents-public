# Codex Skills Kit

This folder is a Codex-native skills kit. It contains a guide for creating, installing, and managing Agent Skills in Codex CLI plus a sync helper for the shared skills source.

Source of truth: `frameworks/shared-skills/skills/`. Copy or sync those skills into `.codex/skills/` (and `.claude/skills/` if you use Claude Code in the same repo).

Codex supports skills natively. You do not need router prompts or Claude-specific bridging to use skills.

## What Are Agent Skills

A skill captures a capability expressed through markdown instructions inside a `SKILL.md` file, plus optional scripts, resources/references, templates/assets, and data. Codex uses skills to perform specific tasks.

A skill folder looks like this:

```
my-skill/
  SKILL.md         # Required: instructions + metadata
  scripts/         # Optional: executable code
  resources/       # Optional: documentation (references)
  templates/       # Optional: templates, resources (assets)
  data/            # Optional: structured sources (JSON)
```

Agent Skills are an open standard. Codex skills follow the Agent Skills specification.

## Where To Save Skills (Precedence)

Codex loads skills from the locations below. If two skills share the same name, the higher-precedence location wins. The list is ordered high to low precedence.

| Skill Scope | Location | Suggested Use |
| --- | --- | --- |
| REPO | `$CWD/.codex/skills` (current working directory) | Skills scoped to a specific folder (for example a microservice or module). |
| REPO | `$CWD/../.codex/skills` (parent of the working directory) | Skills for a shared area in a nested repo. |
| REPO | `$REPO_ROOT/.codex/skills` (top-level repo root) | Skills shared by everyone in the repo. |
| USER | `$CODEX_HOME/skills` (default: `~/.codex/skills`) | Personal skills you want available in any repo. |
| ADMIN | `/etc/codex/skills` | Machine-wide skills for shared environments. |
| SYSTEM | Bundled with Codex | Built-in skills like `$skill-creator` and `$plan`. |

## Quick Start (Use This Kit)

Copy the skills to the location you want Codex to load:

```
# Repo-local (recommended)
mkdir -p .codex/skills
cp -R frameworks/shared-skills/skills/* .codex/skills/

# Or user-level
mkdir -p ~/.codex/skills
cp -R frameworks/shared-skills/skills/* ~/.codex/skills/
```

Codex will discover the skills automatically. No additional prompts or routers are required.

## Using Codex and Claude Code Together

If you use both Codex CLI and Claude Code in the same repo, install skills in both locations. Keep one source of truth (the shared skills folder) and copy into both folders:

```
mkdir -p .claude/skills .codex/skills
cp -R frameworks/shared-skills/skills/* .claude/skills/
cp -R frameworks/shared-skills/skills/* .codex/skills/
```

Helper: `frameworks/sync-skills.sh` syncs from `frameworks/shared-skills/skills/` into both `.claude/skills/` and `.codex/skills/`.

## Create A Skill

Codex provides a built-in skill creator:

```
$skill-creator
```

You can also create a skill manually by adding a new folder in a valid skills location with a `SKILL.md` file.

Minimal `SKILL.md` example:

```
---
name: skill-name
description: Description that helps Codex select the skill
metadata:
  short-description: Optional user-facing description
---

Skill instructions for Codex to follow when using this skill.
```

## SKILL.md Frontmatter Requirements

`SKILL.md` must start with YAML frontmatter. Required fields:

- `name` (1 to 64 chars): lowercase letters, numbers, hyphens only; no leading/trailing hyphen; no consecutive hyphens. Must match the folder name.
- `description` (1 to 1024 chars): non-empty; describe what the skill does and when to use it. Include matching keywords.

Optional fields:

- `license`: license name or bundled license file.
- `compatibility`: environment requirements (system packages, network access, etc.).
- `metadata`: string key/value map for extra properties.
- `allowed-tools`: space-delimited pre-approved tools (experimental).

## Optional Directories

- `scripts/`: executable code used by the skill.
- `resources/`: detailed documentation, loaded on demand (references).
- `templates/`: templates, schemas, or static resources (assets).
- `data/`: structured sources (for example JSON).

## Progressive Disclosure

Codex uses progressive disclosure to manage context:

1. At startup, Codex loads only `name` and `description` from each skill.
2. When a skill is invoked, Codex reads the full `SKILL.md` body.
3. Extra files in `scripts/`, `resources/` (references), `templates/` (assets), and `data/` are loaded only if needed.

Keep `SKILL.md` under 500 lines when possible and move deep references into separate files. Keep file references one level deep from `SKILL.md`.

## How Skills Are Invoked

Codex can use skills in two ways:

- Explicit invocation: use `/skills` or type `$` to select a skill. (Codex web and iOS do not support explicit invocation yet.)
- Implicit invocation: Codex selects a skill when the user request matches a skill description.

## Install New Skills

Codex can download skills from a curated GitHub set using the built-in installer:

```
$skill-installer linear
```

You can also prompt the installer to download skills from other repositories.

## Validation

The Agent Skills reference library provides validation tools:

```
skills-ref validate ./my-skill
```

## Security Considerations

- Review skills before running scripts.
- Prefer trusted skill sources.
- Treat script execution as privileged and confirm with users when risk is non-trivial.

## Included Skills

This kit uses the shared skills catalog in `frameworks/shared-skills/skills/`.
See `frameworks/shared-skills/skills/INDEX.md` for the list.
