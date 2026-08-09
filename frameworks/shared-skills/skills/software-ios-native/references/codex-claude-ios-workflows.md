# Codex and Claude Code Workflows for iOS

Use this reference to keep agent-assisted iOS work predictable and auditable.

## Table of Contents

- [Shared rules](#shared-rules)
- [What to encode on disk](#what-to-encode-on-disk)
- [Codex](#codex)
- [Claude Code](#claude-code)
- [Claude-specific leverage](#claude-specific-leverage)
- [Subagents](#subagents)
- [Hooks](#hooks)
- [Worktrees](#worktrees)
- [Approval boundaries](#approval-boundaries)
- [Prompting rules](#prompting-rules)
- [Good request shape](#good-request-shape)
- [Recommended split of labor](#recommended-split-of-labor)

## Shared rules

- Keep shared project rules in `AGENTS.md`.
- Keep Claude-only overlays in `CLAUDE.md` or `.claude/rules/`.
- Do not duplicate the same repo facts across multiple context files.
- Keep instructions short and non-discoverable:
  prefer exact scheme names, canonical commands, simulator defaults, signing constraints, release gates, and SDK allow or deny rules.
- Keep the agent on the smallest useful loop:
  inspect -> build -> run -> inspect -> test -> debug
- Ask for proof artifacts after each slice:
  build result, launch result, one screenshot or UI snapshot, targeted tests, residual risks.

## What to encode on disk

For iOS repositories, encode these in `AGENTS.md` and mirror into Claude-only layers only when needed:

- workspace or project path
- default scheme and target names
- canonical build, test, and archive commands
- default simulator or device targets
- minimum iOS and UI defaults
- testing split:
  Swift Testing vs XCTest or XCUITest
- release gates:
  privacy manifest, required-reason APIs, entitlements, third-party SDK review, deep links, push, device coverage

Do not encode directory listings, dependency inventories the agent can inspect, or broad architecture prose it can rediscover from the repo.

## Codex

Prefer Codex when:

- the task is implementation-heavy
- shell and repo-level execution matter
- the workflow depends on `AGENTS.md`
- you want a clear terminal-first loop with MCP tools or CLI fallbacks

Codex is the better default for:

- execution-heavy iOS tasks
- terminal-first XcodeBuildMCP flows
- repo-instruction-driven work where precise commands matter
- bounded implementation slices with explicit proof requirements

Default Codex iOS prompt shape:

1. state the user-visible goal
2. name the intended scheme / project if known
3. name the proof required
4. state whether XcodeBuildMCP is configured
5. state what is out of scope

Strong Codex request pattern:

- one slice only
- exact repo facts if known
- explicit proof required
- no permission to guess missing identifiers
- report residual risks and release implications

## Claude Code

Prefer Claude Code when:

- the user is already operating inside a Claude-local repo workflow
- the repo uses `CLAUDE.md`, rules, hooks, or subagents
- the task benefits from a stronger planning / memory loop before coding

Claude Code is the better default for:

- repository understanding before a rewrite
- designing the slice plan and invariants
- running focused subagents for non-overlapping exploration or review
- adding guardrails through hooks or rule files

Keep Claude-specific iOS rules in the Claude layer only when they are truly non-portable. Shared iOS repo policy still belongs in `AGENTS.md`.

## Claude-specific leverage

### Subagents

Use subagents for:

- focused review of one feature area
- parallel exploration of unrelated slices
- verification passes on a narrow concern such as privacy, tests, or release blockers

Do not create one giant “iOS expert” subagent with broad tools and vague responsibility. Keep subagents single-purpose and least-privileged.

### Hooks

Use hooks only where they enforce a concrete boundary. Good iOS examples:

- require a test or build reminder after source edits
- warn before archive, signing, or distribution commands
- inject release-check reminders when files affecting entitlements or manifests change

Do not rely on hooks as a substitute for repo instructions or acceptance criteria.

### Worktrees

Use parallel worktrees for larger rewrite programs only when slices are isolated enough to avoid merge churn. Good candidates:

- one worktree for settings
- one for onboarding
- one for QA or release evidence

Avoid parallel worktrees when multiple agents would edit the same navigation, dependency, or build configuration surfaces.

## Approval boundaries

Require explicit approval for:

- destructive cleanup
- changes to signing or distribution config
- store submission steps
- production telemetry / third-party SDK rollout
- dependency additions whose maintenance or privacy posture is unclear

## Prompting rules

- Ask for one bounded slice, not “rewrite the whole app.”
- Ask for proof artifacts, not only code changes.
- Ask the agent to report residual risks.
- If a tool or package is not verified, require the agent to say so.
- Do not ask the agent to decide the stack if the repo already defines it.
- Do not ask for hidden reasoning; ask for decisions, evidence, and risks.

## Good request shape

- goal
- scope
- proof required
- constraints
- active tool surface

Example:

“Implement the settings screen rewrite in SwiftUI for iOS 17+. Use the existing workspace and `MyApp` scheme. Build and run on simulator, capture one screenshot, run the targeted settings tests, and report any privacy or entitlement implications.”

## Recommended split of labor

Use this as the default split, not a hard rule:

- Codex:
  implementation-heavy slices, shell execution, XcodeBuildMCP loops, deterministic repo tasks
- Claude Code:
  planning, repo comprehension, rule or hook design, subagent orchestration, scoped verification

If only one tool is available, keep the same proof-first workflow and do not compensate by making prompts broader.
