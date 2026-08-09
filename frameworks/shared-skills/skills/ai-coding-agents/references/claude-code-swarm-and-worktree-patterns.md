# Claude Code Swarm and Worktree Patterns

Curated implementation notes extracted from the local `claude_code` source snapshot. Use this file when you need operational detail for teammate spawning, team state, and worktree-backed sessions.

## Table of Contents

- [Team state model](#team-state-model)
- [Teammate spawn inheritance](#teammate-spawn-inheritance)
- [Worktree session lifecycle](#worktree-session-lifecycle)
- [Design implications for coding teams](#design-implications-for-coding-teams)
- [Source anchors](#source-anchors)

## Team state model

Claude Code persists team state in JSON rather than only in thread memory.

The team file includes:
- team name and optional description
- creation timestamp
- lead agent ID and optional lead session ID
- hidden pane IDs
- shared allowed-path rules for teammate edits
- a member list with agent ID, teammate name, agent type, model, prompt, color, plan-mode requirement, joined time, pane ID, cwd, optional worktree path, session ID, subscriptions, backend type, active flag, and permission mode

Operational helpers handle:
- sanitized team and teammate names for filesystem-safe identifiers
- sync and async team-file reads and writes
- teammate removal by agent ID or name
- hidden-pane bookkeeping

## Teammate spawn inheritance

Teammate processes inherit more than just the prompt.

The spawn helpers explicitly propagate:
- permission mode, except when plan mode is required
- model override
- CLI `--settings` path
- inline plugin directories
- teammate mode snapshot
- explicit Chrome flags

They also forward selected environment variables for:
- provider selection
- custom API endpoints
- config directory overrides
- remote-session markers
- remote memory configuration
- proxy and certificate settings

Two practical rules emerge:
- plan mode takes precedence over bypass-permissions inheritance
- teammate startup behavior is intentionally coupled to the leader’s runtime envelope, not just the leader’s prompt

## Worktree session lifecycle

The local setup flow treats worktrees as first-class session environments.

Observed lifecycle:
- capture hook configuration after `cwd` is set
- initialize file-changed watching before worktree creation
- allow worktree creation through git or through a custom WorktreeCreate hook
- resolve the canonical main repo root before creating a git worktree
- optionally create a tmux session for the new worktree
- switch `cwd` to the worktree path
- treat the worktree as the session project root
- persist worktree state
- clear memory-file caches
- refresh settings and hook snapshots after entering the worktree

This means a worktree session is not just a temporary checkout. It becomes the active project boundary for skills, hooks, and related session state.

## Design implications for coding teams

- Persist team topology in files when you need resumable coordination.
- Define teammate ownership explicitly because the runtime already models teammate-specific cwd and worktree paths.
- Be careful with inherited permission modes; plan-mode teammates should not quietly inherit dangerous bypass settings.
- Treat worktree entry as a context and policy boundary, not just a git convenience.
- If your design depends on live teammate orchestration, account for backend-specific behavior such as tmux, iTerm, or in-process runners.

## Source anchors

- `utils/swarm/teamHelpers.ts`
- `utils/swarm/spawnUtils.ts`
- `setup.ts`
