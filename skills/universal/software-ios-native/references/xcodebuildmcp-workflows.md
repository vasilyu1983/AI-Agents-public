# XcodeBuildMCP Workflows

Use this reference when the user wants an external-agent workflow for iOS work through Codex CLI or Claude Code.

## Table of Contents

- [What to verify first](#what-to-verify-first)
- [Install options](#install-options)
- [CLI or MCP via `npx`](#cli-or-mcp-via-npx)
- [Repo-scoped config](#repo-scoped-config)
- [First-call rule](#first-call-rule)
- [Canonical loops](#canonical-loops)
- [Build and run on simulator](#build-and-run-on-simulator)
- [Targeted test pass](#targeted-test-pass)
- [UI verification](#ui-verification)
- [Log-first debugging](#log-first-debugging)
- [Debugger attach](#debugger-attach)
- [CLI mode](#cli-mode)
- [Skills support](#skills-support)

## What to verify first

- `xcodebuildmcp` is installed or invokable through `npx`
- the repo has `.xcodebuildmcp/config.yaml` or an explicit reason not to
- the active scheme and project or workspace path are known
- the intended workflows are enabled

## Install options

### CLI or MCP via `npx`

```bash
npx -y xcodebuildmcp@latest mcp
```

If you prefer a packaged install path such as Homebrew, follow the current upstream README instead of hardcoding commands from memory.

## Repo-scoped config

Create config at:

```text
/.xcodebuildmcp/config.yaml
```

Minimal safe example:

```yaml
schemaVersion: 1
enabledWorkflows: ["simulator", "ui-automation", "debugging"]
sessionDefaults:
  workspacePath: "./MyApp.xcworkspace"
  scheme: "MyApp"
  configuration: "Debug"
  simulatorName: "iPhone 17"
  platform: "iOS"
  useLatestOS: true
```

Notes:

- `schemaVersion` is required and currently must be `1`.
- Keep either `workspacePath` or `projectPath` as the primary entrypoint for the repo. If you use both, verify the current precedence in the upstream config docs.
- Do not enable every workflow unless you need them.

## First-call rule

Do not assume defaults exist.

Preferred first checks:

- `session_show_defaults`
- `sync_xcode_defaults` when Xcode already has the right scheme and simulator selected

Only fall back to discovery calls such as `discover_projs`, `list_schemes`, or `list_sims` when defaults are missing or stale.

## Canonical loops

### Build and run on simulator

- use `build_run_sim` when defaults are set
- use `build_sim` only when compile proof is enough
- do not open with debugger first unless the problem is already runtime-specific

### Targeted test pass

- use `test_sim` for the smallest relevant test scope
- route deep `xcresult` interpretation and flake work to `qa-testing-ios`

### UI verification

- use `screenshot` for fast visual proof
- use `snapshot_ui` when you need structured UI hierarchy and coordinates

### Log-first debugging

- use `start_sim_log_cap`
- reproduce
- use `stop_sim_log_cap`
- only then decide whether debugger attach is needed

### Debugger attach

- use `debug_attach_sim` only after you have a reproducible runtime failure
- keep the debugging session narrow: breakpoint, stack, variables, continue, detach

## CLI mode

Use the CLI when shell execution is simpler than full MCP wiring.

Useful patterns:

```bash
xcodebuildmcp tools
xcodebuildmcp setup
```

Use `xcodebuildmcp tools` as the source of truth for the currently available CLI workflows in your installed version. The CLI and MCP server share the same config file.

## Skills support

XcodeBuildMCP includes optional CLI and MCP skills installable via:

```bash
xcodebuildmcp init
```

Use the CLI skill when the workflow is terminal-first. The MCP skill is optional and most useful when the client benefits from extra server-specific guidance.
