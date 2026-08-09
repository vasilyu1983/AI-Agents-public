# SDK And CLI Checklist

Use this file when reviewing an SDK, CLI, or code generator.

## SDK

- Optimize for the common path first.
- Keep transport details behind typed abstractions.
- Version the public surface deliberately and document breaking changes.
- Include install, auth, pagination, retries, and error handling in the quickstart.

## CLI

- Support `--help`, `--version`, and machine-readable output.
- Keep flags consistent across subcommands.
- Make failure messages actionable.
- Honor non-interactive execution and shell-completion needs.

## Terminal Dashboards

When a CLI tool manages a pipeline with multiple items in flight, a terminal dashboard provides real-time status without requiring a web UI.

Design checklist:

- Show pipeline state at a glance (items in progress, completed, failed).
- Support keyboard navigation for item selection and detail drilldown.
- Update in place — do not scroll the terminal with repeated output.
- Keep the dashboard read-only; use separate commands or modes for mutations.
- Degrade gracefully in narrow terminals and non-interactive sessions.

Framework choices by language:

| Language | Library | Notes |
|----------|---------|-------|
| Go | Bubble Tea (charmbracelet/bubbletea) | Elm-style architecture, rich component ecosystem |
| Rust | Ratatui | Immediate-mode rendering, cross-platform |
| Node.js | Ink (React for CLI) | Component model familiar to React developers |
| Python | Textual (Textualize) | CSS-like styling, widget library |

**Reference:** career-ops (github.com/santifer/career-ops) uses a Go terminal dashboard built with Bubble Tea to display job application pipeline state — a real-world example of a developer tool combining Claude Code agent output with a structured terminal UI.

## Code Generation

- Generate deterministic output.
- Allow safe regeneration without clobbering handwritten code.
- Format generated code with the host ecosystem’s formatter.
