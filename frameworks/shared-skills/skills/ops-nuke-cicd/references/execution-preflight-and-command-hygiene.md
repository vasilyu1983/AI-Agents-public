# Execution Preflight and Command Hygiene

## Purpose
Reduce avoidable CI/local failures caused by missing prerequisites, bad paths, shell quoting, and glob expansion.

## Preflight Checklist
- Confirm repository root and expected working directory before running path-sensitive commands.
- Confirm required SDK/runtime versions before build or test runs.
- Confirm Docker availability before running API/DB/component suites that need containers.
- Confirm target files/directories exist before running `sed`, `cat`, or `ls` against hardcoded paths.

## Shell Safety Rules
- Prefer `rg --files` and explicit file lists over broad shell globs.
- Quote command arguments that include special characters or whitespace.
- Avoid patterns that depend on shell-specific glob behavior.
- For complex commands, test a narrow path first before expanding scope.

## Test Scope Guardrails
- If user constraints exclude infra-dependent suites, do not run those suites implicitly.
- Run feasible targets first (`BuildAll`, `LocalUnitTest`, scoped API/DB tests when available).
- Report skipped targets with clear reason and exact follow-up command.

## Frequent Failure Patterns and Fixes
- `no such file or directory`: verify path from repo root and discover files with `rg --files`.
- `no matches found` (zsh glob): replace raw glob with `rg --files <dir> | rg <pattern>`.
- shell parse/syntax errors: simplify quoting and split compound commands.
- build log file locked: avoid concurrent NUKE runs that write to the same temp log file.

## Verification
- Run one narrow command successfully before batch command execution.
- Re-run failing target in isolation after fixing preflight issues.
- Keep final report explicit about prerequisites and skipped validations.
