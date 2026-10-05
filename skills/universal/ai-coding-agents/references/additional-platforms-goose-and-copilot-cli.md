# Additional Platforms: Goose and GitHub Copilot CLI

Moved from the hub SKILL.md. Platform-choice context for Track A; the subsystem detail lives in the Track B skills named below.

## Goose as a fourth platform

Goose (github.com/aaif-goose/goose, formerly github.com/block/goose) is a Rust-based OSS coding agent donated by Block to the Agentic AI Foundation (AAIF) under the Linux Foundation. It is a meaningfully different platform from Claude Code / Codex / Agent SDK:

- **Protocols:** first-class MCP *and* ACP. Goose runs as an ACP server (`goose acp`) so editors drive it over stdio; Goose can also delegate to external ACP agents (Claude Code, Codex) as providers.
- **Unit of work:** a **recipe** — YAML with `version / title / description / instructions / extensions / activities / prompt / parameters`. Recipes are portable, statically validated, and declare their extension dependencies inline.
- **Distribution:** supports custom distros (white-label, pinned providers/extensions, branded binaries) as a first-class shipping class.
- **Project hints:** uses `.goosehints` alongside `AGENTS.md` — one more member of the narrative-hint family (see `../../agents-memory/SKILL.md`).

Treat it as the target when a coding agent must be OSS, editor-embedded, locally-operated, or enterprise-forkable. Detailed patterns live in the subsystem skills in the references of those skills (Goose patterns) — most relevantly in `ai-coding-agents-provider-runtime` (toolshim, agent-as-provider), `ai-coding-agents-surfaces` (ACP stdio, daemon+OpenAPI), `ai-coding-agents-state` (recipes as typed blueprints), and `ai-coding-agents-settings-policy` (custom distros).

## GitHub Copilot CLI: a fifth, lighter-weight platform

GitHub Copilot CLI is more than a shell-command explainer. It defines **custom agents** as Markdown files with YAML frontmatter (`.agent.md`, resolvable at repo or org scope), supports a **plugin system** (`/plugin install owner/repo`) that bundles MCP servers, agents, skills, and hooks, and ships with the GitHub MCP server pre-wired plus built-in `Explore` and `Task` agents. Track A (define an agent on an existing platform) applies to Copilot CLI on those primitives.

**Frontmatter shape:** `description` (required), `name`, `target` (`vscode` | `github-copilot`), `tools` (omit or `["*"]` for all; empty list disables all; MCP tools namespaced as `server-name/tool-name`), `model`, `disable-model-invocation`, `user-invocable`. Body is Markdown instructions under a character cap; read the current cap in the docs. Versioning rides on git commit SHAs rather than a semantic `version` field.

**Where it still falls short of Track B territory:** no native multi-agent orchestration (agents can invoke each other via an `agent` tool alias, but there is no coordinator/fork/team primitive), no formal session-resume or task-graph model, and no sandbox-mode equivalent to Codex's `workspace-write` / `read-only` / `network-off`. Do not port a coordinator-led team or peer-swarm design onto it — the primitives that make those patterns safe (worktree isolation, mailbox protocol, owned-files enforcement) are absent.

**When to prefer Copilot CLI:** a GitHub-centric repo where a lightweight, PR-aware custom agent is enough — GitHub MCP tools and PR-scoped agent versioning are first-class — and you do not need multi-agent coordination or fine-grained sandbox modes. Prefer Claude Code or Codex when the task needs a coordinator/team pattern, worktree isolation, or a documented permission-mode ladder. Verify current field names and limits against `docs.github.com/en/copilot` before depending on specifics — this surface is still moving faster than the rest of the platform list.
