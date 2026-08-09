# Agentic iOS Tooling

Choose the narrowest tool surface that can prove the next step.

## Default tool selection

| Situation | Default |
|-----------|---------|
| Working inside current-stable Xcode (26.x — check developer.apple.com/news/releases for the exact point release) | Xcode's built-in coding assistant / coding agents |
| Working from Codex CLI or Claude Code outside Xcode | XcodeBuildMCP |
| No MCP available or tooling is unstable | `xcodebuild` + `simctl` + `xcresulttool` |

## Xcode's native coding agent

Use Xcode directly when the developer already lives inside the IDE and wants the shortest edit-build-run loop. Point-release capabilities here have moved every few weeks since introduction (Xcode 26.0 through 26.6 and into the Xcode 27 beta line from WWDC26); re-check the current point release before quoting one in review output.

Verified Apple guidance, current as of Xcode 26.x (re-verify against the latest release notes each session):

- coding agents can build projects
- coding agents can run tests
- coding agents can search Apple documentation
- Xcode exposes these capabilities through MCP-related integrations

Do not assume parity with every external agent client. If the workflow depends on repo memory, tool approval, or shell behavior, document the difference between Xcode, Codex CLI, and Claude Code.

Maximum-value use:

- keep Xcode as the inner loop for edit, build, run, and UI inspection
- keep Codex or Claude Code as the outer loop for scoped implementation, planning, and verification
- do not bounce between multiple tool surfaces for the same small change unless one of them is blocked

## XcodeBuildMCP

Use XcodeBuildMCP as the default external agent bridge when you need:

- simulator build, run, and test loops
- UI snapshots and screenshots
- log capture
- debugger attach on reproducible failures
- Xcode IDE bridge tools from outside the IDE
- a shared repo-scoped config for repeated sessions

Prefer repo-local config over repeating scheme and simulator arguments in every prompt.

Maximum-value use:

- put default scheme, path, simulator, and configuration in repo-scoped config
- check defaults first, then build and run
- use screenshot or UI snapshot before guessing
- use log capture before debugger attach
- keep workflows minimal to reduce tool sprawl

## CLI fallback

Use plain Apple CLI tools when:

- MCP is not installed
- approvals are constrained
- the environment is unstable
- you need a minimal, auditable build or test proof

Default fallback tools:

- `xcodebuild`
- `xcrun simctl`
- `xcrun xcresulttool`

Maximum-value use:

- use CLI fallback as the clean-room proof path when agent tooling is unstable
- keep the CLI commands version-controlled in `AGENTS.md`
- treat the CLI path as the auditing baseline even if the day-to-day loop uses agents

## Optional fast-path tools

XcodeBuildMCP also exposes project scaffolding tools. Use them only when the user explicitly wants a fresh starter app or disposable experiment. For a rewrite of an existing app, prefer working inside the existing project structure.

## Avoid

- Running multiple overlapping Xcode MCP servers by default.
- Using debugger or UI automation before a simpler build, run, or log-based proof exists.
- Treating tool availability as guaranteed without checking install and config state.
