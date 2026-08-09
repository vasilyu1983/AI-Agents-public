# Frontmatter Reference

Use this file as a compatibility matrix, not as a claim that every field works the same way everywhere.

## Table of Contents

- [Portable Core](#portable-core)
- [Compatibility Matrix](#compatibility-matrix)
- [Portable Description Rules](#portable-description-rules)
- [Anthropic-Specific Extensions](#anthropic-specific-extensions)
- [Anthropic Invocation And Substitutions](#anthropic-invocation-and-substitutions)
- [Repo-Local Codex Notes](#repo-local-codex-notes)
- [Examples](#examples)
- [Safety Rules](#safety-rules)

## Portable Core

Portable required fields:

### `name`

```yaml
name: software-backend
```

- Lowercase letters, digits, and hyphens only; no consecutive hyphens; must not start or end with a hyphen (open spec, verified July 2026)
- Must match the folder name exactly
- 1-64 characters (open spec hard limit)
- Avoid vendor names in the identifier unless the skill is truly vendor-specific
- Expert nuance: Claude Code itself treats frontmatter `name` as optional (it falls back to the directory name for display), but the open spec still requires it and requires the folder-name match. Always set it explicitly in the portable core — do not rely on a runtime's fallback.

### `description`

```yaml
description: Builds and reviews backend APIs for Node.js, Python, Go, or Rust. Use when implementing REST services, auth, or database-backed endpoints.
```

- Single-line YAML
- Write in third person
- State what the skill does, then when to use it
- Include concrete trigger words a user might actually say
- Keep it concise enough for shared description budgets
- Stay under 1024 characters

Portable optional fields:

### `license`

```yaml
license: MIT
```

Portable metadata for licensing and distribution notes.

### `compatibility`

```yaml
compatibility: Portable core only; runtime-specific fields are not used.
```

Portable note for scoping implementation expectations. Open-spec constraint (verified July 2026): 1-500 characters if present. The spec's own framing is environment requirements (target product, required system packages, network access — e.g. `Requires git, docker, jq, and access to the internet`), not exclusively a portability disclaimer; naming a target runtime (`Designed for Claude Code (or similar products)`) is an explicit spec example, so this repo's usage is spec-aligned. Most skills do not need this field — only add it when there is a real environment requirement or runtime-scoping to declare.

### `metadata`

```yaml
metadata:
  owner: engineering
  version: "1.0"
  graph:
    routes_from: [router-engineering]
    composes: [software-backend]
```

Portable free-form metadata object.

Use `metadata` for structured repo-local annotations that stay outside the
portable behavioral contract. Example: skill-graph relationships used by local
tooling. Do not assume runtimes read or act on `metadata`.

### `allowed-tools`

```yaml
allowed-tools: Read, Grep, Glob
```

Part of the open spec, but support may vary by implementation. In current Claude Code docs, this is the tool allowlist Claude can use without asking permission while the skill is active. Verify behavior in the target runtime before depending on it.

## Compatibility Matrix

| Field | Portable baseline | Anthropic / Claude Code | VS Code | Repo-local Codex note |
|------|--------------------|-------------------------|---------|-----------------------|
| `name` | Yes | Yes (display-only fallback to dir name; still set it) | Yes | Yes |
| `description` | Yes | Yes (Claude Code labels it "recommended," not required — set it anyway) | Yes | Yes |
| `when_to_use` | No | Supported (appended to description in skill listing; combined budget 1,536 chars) | Do not assume | Do not assume |
| `argument-hint` | No | Supported (shown during autocomplete) | Do not assume | Do not assume |
| `arguments` | No | Supported (named positional args for `$name` substitution; space-separated string or YAML list) | Do not assume | Do not assume |
| `disable-model-invocation` | No | Supported (also blocks subagent skill-preload and scheduled-task firing as of Claude Code v2.1.196+) | Do not assume | Do not assume |
| `user-invocable` | No | Supported (menu visibility only — does not block the Skill tool; use `disable-model-invocation` for that) | Do not assume | Do not assume |
| `allowed-tools` | Yes, but support may vary — portable baseline is a **space-separated** string only | Supported (space- or comma-separated string, or a YAML list; grants tool access without per-use approval) | Verify current support | Verify current support |
| `disallowed-tools` | No | Supported (space- or comma-separated string, or a YAML list; removes tools from available pool while skill is active; resets after next message) | Do not assume | Do not assume |
| `paths` | No | Supported (comma-separated string or YAML list of globs; skill auto-loads only when working files match) | Do not assume | Do not assume |
| `context` | No | Supported (`fork` to run in a subagent; forked run also loads `CLAUDE.md` unless `agent` is `Explore` or `Plan`) | Do not assume | Do not assume |
| `agent` | No | Supported (subagent type when `context: fork` is set; defaults to `general-purpose` if omitted) | Do not assume | Do not assume |
| `model` | No | Supported (overrides model for the current turn only) | Do not assume | Do not assume |
| `effort` | No | Supported (overrides effort level; resets after turn) | Do not assume | Do not assume |
| `hooks` | No | Supported (scoped to skill lifecycle) | Do not assume | Do not assume |
| `shell` | No | Supported (`bash` default or `powershell`, for inline `` !`command` `` / ` ```! ` blocks in the skill body) | Do not assume | Do not assume |
| `license` | Yes | Yes | Yes | Yes |
| `compatibility` | Yes (1-500 chars) | Yes | Yes | Yes |
| `metadata` | Yes | Yes | Yes | Yes |

Interpretation:

- "Portable baseline" means the field is safe to teach as part of the shared core contract.
- "Verify current support" means the field is part of the spec, but runtime behavior may still differ.
- "Do not assume" means you should check the current runtime docs before copying the field.

## Portable Description Rules

Description contract in this repo:

- `SKILL.md` `description` is the portable trigger-rich summary.
- `agents/openai.yaml` `interface.short_description` is the terse Codex UI label.
- `agents/openai.yaml` `interface.default_prompt` is the Codex invocation hint.
- These fields should stay semantically aligned, but they are not required to be
  exact string copies of each other.

Good portable descriptions:

```yaml
description: Creates release checklists and rollback plans for application deploys. Use when planning launches, hotfixes, or production rollback procedures.
```

```yaml
description: Reviews pull requests for correctness, security, and regression risk. Use when asked to review a diff, patch, or proposed code change.
```

Bad descriptions:

```yaml
description: Help with engineering.
```

```yaml
description: Use this for all coding tasks.
```

```yaml
description: Planning and maybe implementing things across every runtime and platform.
```

## Anthropic-Specific Extensions

Use these only when the target runtime is Anthropic-based and the current docs still support them.

Important scope note:

- Claude Code treats all frontmatter fields as optional and only recommends `description` for invocation help.
- This repository still keeps `name` and `description` as the portable shared baseline so the same skill bundle stays predictable across runtimes.
- Do not let Claude-specific flexibility erase the portable contract you want elsewhere.

Example:

```yaml
---
name: review-issue
description: Reviews GitHub issues and produces triage notes. Use when triaging, summarizing, or planning issue follow-up.
argument-hint: "[issue-number]"
model: sonnet
compatibility: Anthropic runtimes only; verify field semantics against current docs before reuse elsewhere.
---
```

Rules:

- If you add any runtime-specific field, add `compatibility` and name the target runtime.
- Do not combine runtime-specific fields with vague portability claims such as "all runtimes" or "cross-platform".
- Treat examples with `argument-hint`, `disable-model-invocation`, `user-invocable`, `when_to_use`, `disallowed-tools`, `paths`, `context`, `agent`, `model`, `effort`, or `hooks` as scoped examples, not the baseline.

## Anthropic Invocation And Substitutions

These are useful Claude-specific details to preserve in the skill library, but they are not portable assumptions.

### Invocation Controls

- `user-invocable: false` hides a skill from the `/` menu but does not mean the model can never use it.
- `disable-model-invocation: true` is the stronger control when the skill should not be auto-invoked by Claude. As of Claude Code v2.1.196+, it also removes the skill from subagent skill-preload and stops it firing when a scheduled task uses it as a prompt — treat it as "manual invocation only," not just "hidden from the model's listing."
- `context: fork` and `agent` are a paired pattern for skill-to-subagent delegation. When a skill sets `context: fork`, the runtime spawns a subagent using the skill body as the task prompt. The `agent:` field selects which subagent type executes it (e.g., `Explore`, `general-purpose`, or a custom agent name); it defaults to `general-purpose` if omitted. The subagent runs in isolation and returns a summary to the parent conversation.

  Key constraint: `context: fork` only makes sense for skills with explicit task instructions. A skill that contains only guidelines or conventions will give the subagent context but no actionable direction.

  Expert nuance: a forked skill also loads `CLAUDE.md` by default — except when `agent: Explore` or `agent: Plan`, which intentionally skip `CLAUDE.md` and git status to keep their context small. If your forked skill's instructions assume repo conventions from `CLAUDE.md`, do not pair it with `Explore`/`Plan` unless the skill body is fully self-contained.

  This is the inverse of the subagent `skills:` field pattern, where a subagent preloads skills as reference material. The distinction: with `context: fork`, the skill controls the prompt and the subagent is the executor; with subagent `skills:`, the subagent controls the prompt and skills are baked-in knowledge.

  ```yaml
  ---
  name: deep-research
  description: Research a topic thoroughly across the codebase.
  context: fork
  agent: Explore
  ---

  Research $ARGUMENTS thoroughly:
  - Find all relevant files and patterns
  - Summarize findings with file references
  ```

- `when_to_use` supplements `description` with additional invocation hints. In Claude Code, the combined `description` + `when_to_use` text is truncated at 1,536 characters in the skill listing. The open spec's per-field limit is 1,024 characters for `description` alone; `when_to_use` is not part of the portable spec.
- `disallowed-tools` removes tools from the available pool while the skill is active; the restriction clears after the user's next message. Use for autonomous background skills that must never call certain tools (e.g., `AskUserQuestion`).
- `paths` limits automatic skill activation to file paths matching the specified glob patterns. Claude loads the skill only when working with matching files; the skill is still user-invocable at any time.
- `model` and `effort` should be treated as Anthropic execution controls, not portable metadata.
- `hooks` should remain Anthropic-scoped until you have verified the exact lifecycle semantics in the current docs.

### String Substitutions

Current Claude docs describe these useful substitutions:

- `$ARGUMENTS` for the full user-supplied argument string
- `$ARGUMENTS[n]` for positional argument access (`$0`, `$1`, ... are shorthand)
- `$name` for a named positional argument declared in the `arguments` frontmatter list (e.g. `arguments: [issue, branch]` maps `$issue`/`$branch` to positions 0/1)
- `${CLAUDE_SESSION_ID}` for session-aware logging or temporary artifacts
- `${CLAUDE_SKILL_DIR}` for locating bundled scripts and reference files regardless of the working directory
- `${CLAUDE_PROJECT_DIR}` for the project root, independent of where the skill itself is installed (personal, project, or plugin) — requires Claude Code v2.1.196+; also usable inside `allowed-tools` rules, e.g. `Bash(${CLAUDE_PROJECT_DIR}/scripts/lint.sh *)`
- `${CLAUDE_EFFORT}` for the current effort level (`low`, `medium`, `high`, `xhigh`, or `max`); use to adapt skill instructions to the active effort setting

Dynamic context injection (Claude Code extension): lines starting with `` !`<command>` `` in a skill body are executed before Claude sees the content, and the output replaces the line. Use this to inline live context such as `git diff HEAD` or environment state. A fenced ` ```! ` block runs multi-line commands the same way. The `shell` frontmatter field (`bash` default or `powershell`) controls which shell executes these — treat it as Anthropic-scoped like the other execution-control fields.

If you document or demo these in a shared skill, label them as Anthropic-specific behavior.

## Repo-Local Codex Notes

This repository uses the portable `SKILL.md` contract for Codex-compatible skills.

Verified (July 2026, developers.openai.com/codex/skills): Codex CLI discovers skills natively from `.agents/skills` (scanned from the current working directory up to the repository root) and from `~/.codex/skills` (personal) / `.codex/skills` (project) — it reads the standard `name` + `description` frontmatter directly, the same as the open spec, with no adjunct YAML required. `agents/openai.yaml` in this repo is **not** part of that native mechanism; it is a repo-local convenience file for this codebase's own Codex/OpenClaw build tooling and UI surfaces. Do not present it as something Codex CLI itself reads out of the box.

If a Codex-facing UI metadata file exists, treat it as an adjunct file rather than frontmatter:

- `agents/openai.yaml` is repo-local metadata for UI surfaces, not part of the portable `SKILL.md` core.
- Keep `SKILL.md` valid on its own; do not move required workflow instructions into adjunct UI metadata.
- If `agents/openai.yaml` exists, regenerate or revalidate it when the skill intent changes.
- Keep the fields distinct:
  - `interface.short_description` should read like a compact UI label.
  - `interface.default_prompt` should tell Codex when to load the skill.
  - Do not enforce exact equality with `SKILL.md` `description`; enforce semantic alignment instead.

See:

- Repo-local Codex skill-authoring guidance may live at `.codex/skills/.system/skill-creator/SKILL.md` when installed. Do not treat that path as portable.

## Examples

### Portable Core Only

```yaml
---
name: docs-codebase
description: Documents codebases with README, ADR, and runbook updates. Use when writing or reorganizing technical documentation.
---
```

### Anthropic-Scoped Skill

```yaml
---
name: qa-review-pr
description: Reviews pull requests for bugs and regression risk. Use when reviewing diffs, patches, or merge requests.
disable-model-invocation: true
compatibility: Anthropic runtimes only; verify before reuse in other platforms.
---
```

### Mixed Claim to Avoid

```yaml
---
name: universal-reviewer
description: Reviews all software changes. Use when reviewing anything.
model: sonnet
compatibility: Portable across all runtimes.
---
```

Why this is bad:

- The skill depends on a runtime-specific field.
- The compatibility note claims universal portability anyway.
- A future runtime may ignore the field or interpret it differently.

## Safety Rules

- No secrets in frontmatter or the body.
- No XML angle brackets in frontmatter values.
- Do not promise cross-platform behavior you have not verified.
- Prefer the smallest set of runtime-specific fields that materially improves behavior.

## Related

- [skill-patterns.md](skill-patterns.md) - Structuring skill bundles
- [skill-validation.md](skill-validation.md) - Static and behavioral validation
- [../SKILL.md](../SKILL.md) - Main agents-skills reference
