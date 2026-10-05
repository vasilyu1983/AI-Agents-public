# Runtime Proof And Prompting

Use this reference when native iOS work needs verified runtime execution, proof-first loops, or prompt shape guidance for Codex, Claude Code, or Xcode-native assistants.

## Table of Contents

- [AI-Agent Defaults](#ai-agent-defaults)
- [Proof-First Rules](#proof-first-rules)
- [Token Discipline](#token-discipline)
- [Agent Execution Loop](#agent-execution-loop)
- [High-Value Prompt Shape](#high-value-prompt-shape)

## AI-Agent Defaults

- Inside current-stable Xcode (26.x — re-verify the point release each session), prefer Xcode's native coding assistant or agent surface first.
- Outside Xcode, check whether XcodeBuildMCP is actually callable before assuming it is available.
- If XcodeBuildMCP is callable, use it for build, launch, screenshot, and UI inspection loops.
- If XcodeBuildMCP is unavailable, blocked, or not exposed in the current runtime, fall back immediately to `xcodebuild`, `simctl`, and `xcresulttool`.
- Use repo-scoped project memory for the agent:
  - Codex: keep shared execution rules in `AGENTS.md`
  - Claude Code: keep shared rules in `AGENTS.md` and Claude-specific overlays in `CLAUDE.md` or `.claude/rules/`
- Keep project instructions lean and non-discoverable: encode only scheme names, build and test commands, simulator defaults, signing and release constraints, allowed SDKs, and other facts the agent cannot safely infer.
- Ask for one bounded vertical slice at a time and require proof artifacts after each slice.
- Prefer verification-first execution: build and run before debugger, screenshot or UI snapshot before layout guesses, logs before breakpoint sessions.
- In Claude Code, use focused subagents and hooks only where they add concrete leverage.
- For larger rewrite programs, use parallel worktrees only when slices are isolated enough to avoid file ownership conflicts.

## Proof-First Rules

- Separate platform facts from repo defaults. Platform facts need primary sources; repo defaults need explicit labels.
- Never invent scheme names, targets, bundle IDs, simulator names, project paths, or store-policy dates.
- Never claim a library or package is the default choice unless it is Apple-provided or the user explicitly standardizes on it.
- Re-check volatile facts before using them in user-facing guidance:
  - Xcode and SDK behavior
  - App Store submission requirements
  - Apple privacy and SDK compliance requirements
  - XcodeBuildMCP commands and config shape
  - Codex and Claude Code memory behavior
- Prefer smaller verified loops over large autonomous edits:
  - discover
  - build
  - run
  - inspect
  - test
  - debug
  - hand off results with evidence

## Token Discipline

- Prove build, install, and launch before spending tokens on UI critique or feature debugging.
- If screenshots do not match source, assume stale install or stale launch first.
- If install fails, inspect the built `.app` bundle before changing Swift or SwiftUI feature code.
- Do not keep retrying an unavailable MCP path; switch to Apple CLI as soon as tool reality is clear.
- Route simulator drift, packaging failures, missing executables, and stale-app suspicion to [software-ios-runtime-debugging](../../software-ios-runtime-debugging/SKILL.md).
- Magic numbers in Canvas drawing code are geometric constants, not layout tokens. Do not extract them into the design system.
- Magic numbers in SwiftUI layout code should use design-system tokens such as `AppSpacing` and `AppRadius`.
- On a dirty git tree, prefer a stash -> narrow edit -> commit -> pop workflow over manual hunk juggling when landing a surgical fix.
- If the project uses XcodeGen and the target declares `sources: [path: ...]`, regenerate the project after adding new Swift files instead of editing `.pbxproj`.

## Agent Execution Loop

- Start by checking current defaults and project identity before build or run commands.
- Use single-step build-and-run commands when defaults are already configured.
- When runtime truth is in doubt, force a fresh uninstall -> install -> launch loop before diagnosing app behavior.
- Capture screenshots or UI hierarchy before guessing at UI bugs.
- Capture logs before attaching a debugger.
- Use debugger flows only after you have a reproducible runtime failure.
- Keep acceptance criteria behavior-focused: build passes, app launches, intended flow works, targeted tests pass, and no new release blockers appear.

## High-Value Prompt Shape

- `goal`: the user-visible outcome for one slice
- `repo facts`: workspace or project path, scheme, target, simulator if already known
- `proof required`: build, launch, screenshot or UI snapshot, targeted tests, residual risks
- `constraints`: minimum iOS, keep or avoid specific SDKs, out-of-scope areas
- `active tool surface`: Xcode, XcodeBuildMCP, or Apple CLI fallback

Avoid prompts like “rewrite the app” or “fix everything wrong with this screen.” Force the agent to prove one bounded increment at a time.
