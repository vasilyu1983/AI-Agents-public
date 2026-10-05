# Runtime Proof And Prompting

Use this reference when native Android work needs verified runtime execution, proof-first loops, or prompt-shape guidance for Codex, Claude Code, Android Studio, and CLI-first workflows.

## Table of Contents

- [AI-Agent Defaults](#ai-agent-defaults)
- [Proof-First Rules](#proof-first-rules)
- [Token Discipline](#token-discipline)
- [Agent Execution Loop](#agent-execution-loop)
- [High-Value Prompt Shape](#high-value-prompt-shape)

## AI-Agent Defaults

- Inside Android Studio, prefer the built-in Gemini coding assistant surface first.
- Outside Android Studio, use Gradle CLI plus ADB for build, install, launch, and inspection loops.
- Use repo-scoped project memory for the agent:
  - Codex: keep shared execution rules in `AGENTS.md`
  - Claude Code: keep shared rules in `AGENTS.md` and Claude-specific overlays in `CLAUDE.md` or `.claude/rules/`
- Keep project instructions lean and non-discoverable: encode only module paths, build variants, package names, emulator defaults, signing and release constraints, allowed SDKs, and other facts the agent cannot safely infer.
- Ask for one bounded vertical slice at a time and require proof artifacts after each slice.
- Prefer verification-first execution: build and install before debugger, screenshot or UI hierarchy before layout guesses, logcat before breakpoint sessions.
- In Claude Code, use focused subagents and hooks only where they add concrete leverage.
- For larger rewrite programs, use parallel worktrees only when slices are isolated enough to avoid file ownership conflicts.

## Proof-First Rules

- Separate platform facts from repo defaults. Platform facts need primary sources; repo defaults need explicit labels.
- Never invent module names, build variants, package names, emulator names, or store-policy dates.
- Never claim a library or package is the default choice unless it is Google-provided Jetpack or the user explicitly standardizes on it.
- Re-check volatile facts before using them in user-facing guidance:
  - Android Studio, AGP, and Compose behavior
  - Play Store submission requirements
  - Google privacy and SDK compliance requirements
  - Codex and Claude Code memory behavior
- Prefer smaller verified loops over large autonomous edits:
  - discover
  - build
  - install
  - launch
  - inspect
  - test
  - debug
  - hand off results with evidence

## Token Discipline

- Prove build, install, and launch before spending tokens on UI critique or feature debugging.
- If screenshots do not match source, assume stale install or stale launch first.
- If install fails, inspect the built APK or AAB before changing Kotlin or Compose feature code.
- Do not keep retrying a broken emulator path; switch to a working emulator or device as soon as tool reality is clear.
- Magic numbers in Canvas drawing code are geometric constants, not layout tokens. Do not extract them into the design system.
- Magic numbers in Compose layout code should use design-system tokens or shared `Dp` constants.

## Agent Execution Loop

- Start by checking current defaults and project identity before build or run commands.
- Use single-step build-install-launch commands when defaults are already configured.
- When runtime truth is in doubt, force a fresh uninstall -> install -> launch loop before diagnosing app behavior.
- Capture screenshots or UI hierarchy before guessing at UI bugs.
- Capture logcat before attaching a debugger.
- Use debugger flows only after you have a reproducible runtime failure.
- Keep acceptance criteria behavior-focused: build passes, app installs and launches, intended flow works, targeted tests pass, and no new release blockers appear.

## High-Value Prompt Shape

- `goal`: the user-visible outcome for one slice
- `repo facts`: module path, build variant, package name, emulator or device if already known
- `proof required`: build, install, launch, screenshot or UI hierarchy, targeted tests, residual risks
- `constraints`: minimum API level, keep or avoid specific SDKs, out-of-scope areas
- `active tool surface`: Android Studio Gemini, Gradle CLI plus ADB, or emulator CLI

Avoid prompts like “rewrite the app” or “fix everything wrong with this screen.” Force the agent to prove one bounded increment at a time.
