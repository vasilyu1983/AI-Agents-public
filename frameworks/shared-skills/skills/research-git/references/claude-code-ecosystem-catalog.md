# Claude Code Ecosystem Catalog

Seed list of high-signal repos and resources for Claude Code / coding-agent research. Use as the input to `research-git` scans rather than rediscovering from scratch. Star counts and one-line summaries are quoted from the source post — verify before quoting them downstream.

Sources:

- @0x_kaize, 2026-04-25 — <https://x.com/0x_kaize/status/2048059417661174052> (categorized 100-repo list)
- @mattpocockuk, 2026-04-26 — <https://x.com/mattpocockuk/status/2048490818848075846> (`mattpocock/skills` ~23K ⭐)
- @LLMJunky, 2026-04-25 — <https://x.com/LLMJunky/status/2048117627294277832> (`codex-marketplace.com/skills`, Dimillian's macOS/iOS Codex skills)

> Catalog is a starting point — verify each repo is still active before lifting patterns. URLs reflect what was posted; if a repo has moved or been deprecated, note it inline rather than dropping silently.

## Table of Contents

- [1. Awesome Lists & Meta-Indexes](#1-awesome-lists--meta-indexes)
- [2. Official Anthropic](#2-official-anthropic)
- [3. Skills Collections](#3-skills-collections)
- [4. Agents & Subagents](#4-agents--subagents)
- [5. MCP Servers](#5-mcp-servers)
- [6. Orchestration & Workflows](#6-orchestration--workflows)
- [7. Memory & Context](#7-memory--context)
- [8. Slash Commands & Hooks](#8-slash-commands--hooks)
- [9. Guides & Learning](#9-guides--learning)
- [10. IDE Integrations & Desktop](#10-ide-integrations--desktop)
- [11. Specialized Workflows](#11-specialized-workflows)
- [Additional Pointers](#additional-pointers)

## 1. Awesome Lists & Meta-Indexes

- `hesreallyhim/awesome-claude-code` (~28.5K ⭐) — definitive curated index; only Claude itself submits PRs.
- `ComposioHQ/awesome-claude-skills` — 50+ production skills, cross-compatible with Claude Code/Codex/Cursor/Gemini CLI; install via `/skill add`.
- `ComposioHQ/awesome-claude-plugins` — plugins via `/plugin marketplace add`; includes connect-apps, frontend-design, artifacts-builder.
- `langgptai/awesome-claude-prompts` (~4.2K ⭐) — XML-structured prompt techniques.
- `alvinunreal/awesome-claude` — broad Anthropic-ecosystem catalog.
- `VoltAgent/awesome-agent-skills` (~1000+ skills) — cross-runtime, "battle-tested not AI slop."
- `VoltAgent/awesome-claude-code-subagents` — domain-specific subagent bundles.
- `ccplugins/awesome-claude-code-plugins` — install commands per entry; supports self-hosted marketplaces.
- `jqueryscript/awesome-claude-code` — IDE integrations and frameworks.
- `danielrosehill/Claude-Code-Repos-Index` — 75+ original-only repos.

## 2. Official Anthropic

- `anthropics/claude-code` (~55K ⭐) — CLI source.
- `anthropics/skills` (~37.5K ⭐) — official skills repo (PDF, DOCX, XLSX, PPTX, art generation).
- `anthropics/claude-plugins` (~2.8K ⭐) — vetted plugin directory.
- `anthropics/claude-code-sdk-python` (~6.1K ⭐).
- `anthropics/claude-agent-sdk-typescript` — V2 with `send()`/`stream()`.
- `anthropics/claude-code-security-review` (~2.8K ⭐) — PR security review Action.
- `anthropics/claude-code-action` — `@claude` mention triggers PR review.
- `github/github-mcp-server` — official GitHub MCP; `X-MCP-Readonly` for read-only mode.
- `anthropics/anthropic-cookbook` — RAG, classification, summarization recipes.
- `anthropics/courses` — prompt engineering, API usage, agents, AI Fluency.

## 3. Skills Collections

- `obra/superpowers` (~148K ⭐) — brainstorm → spec → plan → TDD → review → merge; subagent orchestration.
- `obra/superpowers-marketplace` — 20+ skills, `/brainstorm`, `/write-plan`, `/execute-plan`, SessionStart context injection.
- `obra/superpowers-skills` — community-editable, auto-cloned to `~/.config/superpowers/skills/`.
- `obra/superpowers-lab` — experimental (e.g., semantic duplicate-function detection).
- `affaan-m/everything-claude-code` — 30 agents, 136 skills, 60 slash commands, 1282 tests, 98% coverage.
- `travisvn/awesome-claude-skills` (~22K installs) — SEO/marketing/design/security/research.
- `trailofbits/claude-code-skills` — security-research and audit skills.
- `K-Dense-AI/claude-scientific-skills` — scientific-computing.
- `ay-automate/ay-skills` — 10 production-tested (SEO audits, headless browser, Remotion video, diagrams).
- `BehiSecc/awesome-claude-skills` — meta-list of skill lists.

## 4. Agents & Subagents

- `wshobson/agents` (~25K ⭐) — strategy/dev/security/design/data/research subagent pack.
- `vijaythecoder/awesome-claude-agents` (~3.7K ⭐) — collaborating agent teams.
- `davepoon/claude-code-subagents-collection` (~2.2K ⭐) — 100+ subagents.
- `baryhuang/claude-code-agents` — 59 specialists (TS/Python/Java/Kotlin reviewers, workflow automation).
- `ruvnet/multi-agent-squad` — task routing + consensus.
- `0xAsten/Agent-Fusion` — multi-agent across Claude Code/Codex/Amazon Q/Gemini.
- `webdevtodayjason/sub-agents` — subagent manager, hooks, slash commands.
- `dotneet/sub-agents-directory` — 100+ subagent prompts plus MCP servers.
- `iamcatdev/claude-code-heavy` — parallel research orchestration.
- `webdevtodayjason/ClaudeCodeAgents` — QA-focused.

## 5. MCP Servers

- `steipete/claude-code-mcp` — run Claude Code itself as MCP (agent-in-agent / recursive delegation).
- `zilliztech/claude-context` — semantic code search MCP for large codebases.
- `d-e-s-o/claude-context-mode` (~2.2K ⭐) — context-shrinking MCP, claims 315KB→5.4KB (~98%).
- `continuous-claude/continuous-claude-v2` (~2.2K ⭐) — ledger-based context hooks.
- `upstash/context7` — version-specific docs in prompts; works in Cursor/VS Code/Claude Code/Windsurf.
- `crystaldba/postgres-mcp` — read-only-default Postgres MCP, multi-connection.
- `microsoft/playwright-mcp` — browser automation MCP.
- `modelcontextprotocol/servers` — reference servers (incl. `mcp-server-sqlite`).
- `grahama1970/claude-code-mcp-enhanced` — emphatic-prompt variant for compliance.
- `danielrosehill/Claude-Code-MCP-List` — Linux-desktop MCP picks.

## 6. Orchestration & Workflows

- `ruvnet/claude-flow` (~11.4K ⭐) — multi-agent orchestration with persistent memory.
- `smtg-ai/claude-squad` (~5.6K ⭐) — terminal multiplexer for Claude Code/Aider/Codex/OpenCode/Amp.
- `Dicklesworthstone/claude_code_agent_farm` — parallel CC sessions at scale.
- `automazeio/ccpm` — project-management workflow (Ran Aroussi).
- `cc-sessions/cc-sessions` (~1.5K ⭐) — hooks/subagents/commands/task/git infra.
- `iannuttall/claude-sessions` (~1.1K ⭐) — session-tracking slash commands.
- `diet103/claude-code-infrastructure-showcase` — hooks that activate skills contextually.
- `disler/infinite-agentic-loop` — two-prompt infinite loop.
- `agentsys/agentsys` — 14 plugins, 43 agents, 30 skills across CC/OpenCode/Codex.
- `gabrieltonnellier/citadel` — orchestration harness with session-memory.

## 7. Memory & Context

- `thedotmack/claude-mem` — long-term memory via compression.
- `hanfang/claude-memory-skill` — minimal hierarchical memory + background agents.
- `0xfurai/claude-subconscious` (~2.4K ⭐) — background agent reading sessions, building memory.
- `dheerajoruganty/claude-code-semantic-memory` — vector-based recall across sessions.
- `brennercruvinel/claude-user-memory` — 12 specialist agents, auto-orchestration.
- `yamadashy/repomix` (~20.9K ⭐) — pack codebase into one AI-readable XML/MD/text file.
- `safishamsi/graphify` — interactive knowledge graph from codebases.
- `elizaOS/context-prime` — scenario-specific context priming.
- `iamcatdev/claude-code-heavy` — research-context multi-agent (also in §4).
- `continuous-claude/continuous-claude-v2` — ledger system (also in §5).

## 8. Slash Commands & Hooks

- `wshobson/commands` (~1.7K ⭐) — 57 commands: 15 workflows + 42 tools.
- `nizos/tdd-guard` (~1.7K ⭐) — blocks skipping tests; explains why.
- `RonitSachdev/ccundo` (~1.3K ⭐) — granular action-level rollback.
- `claude-canvas/claude-canvas` (~1.1K ⭐) — TUI display toolkit for CC.
- `ClaudoPro/claudopro-directory` — hooks/commands/subagents directory.
- `danielrosehill/Claude-Slash-Commands` — categorized commands with pre-push sync hook.
- `claude-commands/command-fix-issue` — TDD-based GitHub issue fixer (`/fix-issue 456`); auto-PR.
- `patrick-ellis/design-review-workflow` — automated UI/UX review with subagents.
- `jerseycheese/tdd-implement` — Red/Green/Refactor enforcement.
- `anthropics/claude-code-security-review` — official security-review command.

## 9. Guides & Learning

- `ThamJiaHe/claude-prompt-engineering-guide` — covers Opus 4.6 / Sonnet 4.6 / Haiku 4.5; Skills/Plugins/MCP/Hooks/Ultrathink; 220+ sources.
- `nikiforovall/claude-code-handbook` — daily-use patterns + distributable plugins.
- `FlorianBruniaux/claude-code-ultimate-guide` — 22K+ lines, 225 templates, 9 personas, 26 commands, 271 quiz questions.
- `Piebald-AI/claude-code-system-prompts` — all CC system prompts updated within minutes of release; 155+ versions.
- `wolfmcnally/Encyclopedia-of-Agentic-Coding-Patterns` — 190+ patterns.
- `RiyaParikh0112/claude-code-playbook` — TDD + integration patterns + CI configs.
- `iannuttall/claude-code-tips` — 40+ tips: status-line scripts, system-prompt halving, containers.
- `topics/awesome-claude-prompts` (GitHub topic) — community submissions.
- `disler/context-priming` — systematic priming approach.
- `shaharia-lab/my-claude-code-journey` — 2-week real-world workflow notes.

## 10. IDE Integrations & Desktop

- `coder/claudecode.nvim` — first Neovim IDE integration; Lua, zero deps, WebSocket MCP.
- `greggh/claude-code.nvim` — Neovim toggle terminal; `--continue` variants; auto-reload modified files.
- `manzaltu/claude-code-ide.el` — Emacs with ediff, LSP/flymake/flycheck, tree-sitter AST queries.
- `stevemolitor/claude-code.el` — minimal Emacs CLI wrapper.
- `Haleclipse/Claudix` — VS Code chat + session manager (Vue 3 + TS).
- `Ruller-Lulu/clawd-on-desk` — desktop pet for session awareness.
- `aaddrick/claude-desktop-debian` — unofficial Linux desktop app.
- `instructkr/claw-code` — Korean-built CC alternative tooling.

## 11. Specialized Workflows

- `nextlevelbuilder/ui-ux-pro-max-skill` — UI/UX design-pattern skill.
- `claudewave/claudewave` — real-time directory of 3800+ CC repos, 8 categories, refreshed every 12h.

## Additional Pointers

- `mattpocock/skills` (~23K ⭐) — Skills for Real Engineers, straight from Matt Pocock's `.claude` directory; high-leverage starting point for skill-design patterns.
- `codex-marketplace.com/skills` — Codex skill marketplace; notable: Dimillian's macOS/iOS skills for Apple-platform Codex work.
