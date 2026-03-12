# Frontmatter Reference

Complete specification for SKILL.md YAML frontmatter fields. For an overview, see the main [SKILL.md](../SKILL.md).

## Required Fields

### `name`

Unique identifier matching the skill's folder name.

```yaml
name: software-backend
```

- Kebab-case only: `a-z`, `0-9`, `-`
- Must exactly match the containing directory name
- Forbidden words: `claude`, `anthropic` (reserved)

### `description`

The primary trigger mechanism. The runtime reads all descriptions to decide which skills to auto-invoke.

```yaml
description: Production backend APIs for Node.js, Python, Go, and Rust. Use when building REST/GraphQL services or auth.
```

- Format: `[What it does]. Use when [trigger phrases].`
- Target ~150 chars per skill when library exceeds 50 skills
- **Budget**: 2% of context window (~16,000 chars fallback) is shared across ALL skill descriptions; exceeding it causes silent skill exclusion
- Single-line YAML — avoid multiline `>-` for descriptions
- Include technology names and action verbs as trigger keywords
- Override budget via env var `SLASH_COMMAND_TOOL_CHAR_BUDGET` (not recommended)

## Invocation Control Fields

### `argument-hint`

Autocomplete hint displayed in the `/` slash-command menu.

```yaml
argument-hint: "[issue-number]"
```

Shown as: `/skill-name [issue-number]`

### `disable-model-invocation`

Prevents the model from auto-triggering this skill. User must explicitly invoke via `/skill-name`.

```yaml
disable-model-invocation: true
```

Use for: project-specific skills, meta-orchestration, skills the user always invokes explicitly.

### `user-invocable`

Controls visibility in the `/` slash-command menu.

```yaml
user-invocable: false
```

- `true` (default): appears in menu and can be invoked with `/skill-name`
- `false`: hidden from menu; used as background context or auto-triggered only

### `allowed-tools`

Restricts which tools the skill can use. Comma-separated list.

```yaml
allowed-tools: Read, Grep, Glob, Bash(python *)
```

- Omit to allow all tools (default)
- Supports glob patterns for Bash: `Bash(python *)` allows only `python` commands
- Use for read-only analysis skills or skills that need specific tool subsets

## Execution Context Fields

### `context`

Controls execution context for the skill.

```yaml
context: fork
```

- `fork`: runs the skill body in a subagent (separate context window)
- Omit for normal inline execution (default)

### `agent`

Specifies which subagent type to use when `context: fork`.

```yaml
context: fork
agent: Explore
```

Options: `Explore`, `Plan`, `general-purpose`, or custom agent names defined in `.claude/agents/`.

### `model`

Overrides the model used when executing this skill.

```yaml
model: sonnet
```

Options: `opus`, `sonnet`, `haiku`. Useful for cost control or when a skill needs maximum capability.

### `hooks`

Lifecycle hooks scoped to this skill. Same format as settings hooks but only active when this skill is loaded.

```yaml
hooks:
  PreToolUse:
    - matcher: Write
      command: "echo 'File write detected'"
```

## Metadata Fields

### `license`

License identifier for the skill.

```yaml
license: MIT
```

### `compatibility`

Platform or version compatibility notes (1-500 chars).

```yaml
compatibility: Claude Code 1.0+, Codex CLI 0.5+
```

### `metadata`

Additional metadata as key-value pairs.

```yaml
metadata:
  author: team-name
  version: "2.1"
  mcp-server: github
```

## String Substitutions

Available in the skill body (content after frontmatter):

| Variable | Resolves To | Example |
|----------|-------------|---------|
| `$ARGUMENTS` | Full argument string from `/skill arg1 arg2` | `"arg1 arg2"` |
| `$ARGUMENTS[0]` | First argument | `"arg1"` |
| `$ARGUMENTS[1]` | Second argument | `"arg2"` |
| `$1`, `$2`, ... | Shorthand for `$ARGUMENTS[0]`, `$ARGUMENTS[1]` | `"arg1"` |
| `${CLAUDE_SESSION_ID}` | Current session UUID | `"abc-123-def"` |
| `${CLAUDE_SKILL_DIR}` | Absolute path to skill directory | `"/path/to/skills/my-skill"` |

**Example**:

```markdown
---
name: review-issue
description: Reviews a GitHub issue. Use when asked to review or triage an issue by number.
argument-hint: "[issue-number]"
---

Fetch and review GitHub issue #$1 for the current repository.
Use `gh issue view $1` to get the details.
Load additional context from `${CLAUDE_SKILL_DIR}/references/review-checklist.md`.
```

## Dynamic Context Injection

Use `` !`command` `` syntax in the skill body to inject command output at skill load time:

```markdown
Current git status:
!`git status --short`

Recent commits:
!`git log --oneline -5`
```

The command runs when the skill activates and its stdout replaces the `` !`command` `` line.

## Security Restrictions

1. **No XML angle brackets** (`<`, `>`) in frontmatter values — they conflict with system prompt parsing
2. **No reserved words** in `name`: `claude`, `anthropic`
3. **No secrets** in frontmatter or skill body — use environment variables
4. **`allowed-tools`** should follow least-privilege: only grant tools the skill actually needs

## Complete Example

```yaml
---
name: dev-review-pr
description: Reviews pull requests for code quality and security. Use when reviewing PRs, diffs, or merge requests.
argument-hint: "[PR-number]"
allowed-tools: Read, Grep, Glob, Bash(gh *)
model: sonnet
metadata:
  author: engineering
  version: "1.0"
---
```

## Related

- [skill-patterns.md](skill-patterns.md) - Common skill organizational patterns
- [skill-validation.md](skill-validation.md) - Validation criteria and scripts
- [../SKILL.md](../SKILL.md) - Main agents-skills reference
