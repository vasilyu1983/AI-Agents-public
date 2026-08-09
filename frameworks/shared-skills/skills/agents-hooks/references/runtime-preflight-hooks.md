# Runtime Preflight Hooks

Use these patterns to validate local runtime/tool prerequisites at session start.

## Goal

Fail fast with actionable remediation when required tools or versions are missing, instead of discovering mismatch deep in execution.

## Recommended Events

- `SessionStart`: verify runtime versions and binary presence.
- `Setup`: verify repo-local requirements (package managers, language toolchains).

## Checks to Include

- binary exists (`command -v node`)
- version satisfies minimum (`node -v >= v22.22.0`)
- configured path exists (for tool-specific runtime paths)

## Output Pattern

- success: concise pass log
- failure: explicit error + one-line remediation command

## Example Failure Message

```text
Runtime preflight failed: node v20.19.5 detected, requires >= v22.22.0.
Run: nvm install 22.22.0 && nvm use 22.22.0
```

## Safety Notes

- Keep preflight read-only by default.
- Avoid automatic installs in hooks unless explicitly approved by project policy.
- Keep execution under 1 second where possible.
