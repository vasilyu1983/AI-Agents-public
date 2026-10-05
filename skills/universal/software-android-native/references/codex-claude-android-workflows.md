# Codex and Claude Code Workflows for Android

Use this reference to keep agent-assisted Android work predictable and auditable.

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
  prefer exact module paths, package names, canonical Gradle commands, emulator defaults, signing constraints, release gates, and SDK allow or deny rules.
- Keep the agent on the smallest useful loop:
  build -> install -> launch -> inspect -> test -> debug
- Ask for proof artifacts after each slice:
  build result, install and launch result, one screenshot or logcat excerpt, targeted tests, residual risks.

## What to encode on disk

For Android repositories, encode these in `AGENTS.md` and mirror into Claude-only layers only when needed:

- root project path and app module path
- default build variant and flavor
- canonical build, test, and install commands
- default emulator AVD name or device serial
- minimum API level and target SDK
- package name and main Activity component name
- testing split:
  JUnit 5 vs Compose Testing vs Espresso
- release gates:
  data safety declarations, target SDK compliance, ProGuard/R8 rules, Play Integrity, deep links, push, device coverage

Do not encode directory listings, dependency inventories the agent can inspect, or broad architecture prose it can rediscover from the repo.

## Codex

Prefer Codex when:

- the task is implementation-heavy
- shell and repo-level execution matter
- the workflow depends on `AGENTS.md`
- you want a clear terminal-first loop with Gradle CLI + ADB

Codex is the better default for:

- execution-heavy Android tasks
- terminal-first Gradle + ADB flows
- repo-instruction-driven work where precise commands matter
- bounded implementation slices with explicit proof requirements

Default Codex Android prompt shape:

1. state the user-visible goal
2. name the module path / build variant if known
3. name the proof required
4. state the emulator or device target
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

Keep Claude-specific Android rules in the Claude layer only when they are truly non-portable. Shared Android repo policy still belongs in `AGENTS.md`.

## Claude-specific leverage

### Subagents

Use subagents for:

- focused review of one feature module
- parallel exploration of unrelated slices
- verification passes on a narrow concern such as ProGuard rules, data safety, tests, or release blockers

Do not create one giant "Android expert" subagent with broad tools and vague responsibility. Keep subagents single-purpose and least-privileged.

### Hooks

Use hooks only where they enforce a concrete boundary. Good Android examples:

- require a build or test reminder after source edits
- warn before signing config or Play Console changes
- inject release-check reminders when files affecting `AndroidManifest.xml`, ProGuard rules, or data safety declarations change

Do not rely on hooks as a substitute for repo instructions or acceptance criteria.

### Worktrees

Use parallel worktrees for larger rewrite programs only when slices are isolated enough to avoid merge churn. Good candidates:

- one worktree for settings module
- one for onboarding flow
- one for QA or release evidence

Avoid parallel worktrees when multiple agents would edit the same navigation graph, Hilt module, or Gradle build configuration surfaces.

## Approval boundaries

Require explicit approval for:

- destructive cleanup (deleting modules, removing dependencies)
- changes to signing or distribution config
- Play Store submission steps
- production telemetry / third-party SDK rollout
- dependency additions whose maintenance or privacy posture is unclear
- changes to `AndroidManifest.xml` permissions
- ProGuard/R8 rule modifications

## Prompting rules

- Ask for one bounded slice, not "rewrite the whole app."
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

"Implement the settings screen rewrite in Jetpack Compose for API 28+. Use the existing `:app` module and `debug` build variant. Build and install on the Pixel 8 emulator, capture one screenshot, run the targeted settings tests, and report any data safety or permissions implications."

## Recommended split of labor

Use this as the default split, not a hard rule:

- Codex:
  implementation-heavy slices, shell execution, Gradle CLI + ADB loops, deterministic repo tasks
- Claude Code:
  planning, repo comprehension, rule or hook design, subagent orchestration, scoped verification

If only one tool is available, keep the same proof-first workflow and do not compensate by making prompts broader.
