# Runtime Preflight Hooks

Use these patterns to validate local runtime/tool prerequisites at session start.

## Goal

Fail fast with actionable remediation when required tools or versions are missing, instead of discovering mismatch deep in execution.

## Recommended Events

- `SessionStart`: verify runtime versions and binary presence. `SessionStart` cannot block: report a failure to Claude through `hookSpecificOutput.additionalContext` on exit `0`; a non-zero exit only reaches the user as a hook-error notice.
- `Setup`: verify repo-local requirements (package managers, language toolchains).

## Checks to Include

- binary exists (`command -v node`)
- version satisfies the minimum the project declares (engines field, `.tool-versions`, `.nvmrc`); read it from there rather than hardcoding it in the hook
- configured path exists (for tool-specific runtime paths)

## Output Pattern

- success: concise pass log
- failure: explicit error + one-line remediation command, sent as `additionalContext` so the model sees it

## Example Failure Message

```text
Runtime preflight failed: node v<found> detected, requires >= v<project minimum>.
Run: nvm install <project minimum> && nvm use <project minimum>
```

## Safety Notes

- Keep preflight read-only by default.
- Avoid automatic installs in hooks unless explicitly approved by project policy.
- Keep execution fast enough that session start does not visibly stall; no official latency budget is published, so measure on your own runtime.
