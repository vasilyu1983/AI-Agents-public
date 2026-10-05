# Playwright Preflight: Sandbox, Port, Timeout, Lock

Use this preflight before running expensive E2E suites in local sandboxes or CI containers.

## 1) Verify Target Specs and Working Directory

```bash
pwd
rg --files e2e/tests | rg "<target-spec-or-pattern>"
```

If spec paths are missing, stop and fix path assumptions first.

## 2) Port and Host Binding Check

```bash
# Replace 3000 with configured webServer port
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

Decision rules:
- `EADDRINUSE`: free the port or choose a different port.
- `EPERM` / `EACCES` bind errors: escalate immediately; do not retry loops.
- If environment disallows `0.0.0.0`, force `127.0.0.1` for local-only runs.

## 2b) Server Topology and Command Validity

- Pick one topology: a shared dev server (run Playwright with `--no-server`) or Playwright-managed `webServer`. Never run both by accident.
- Validate CLI flags against the installed Playwright version before a batch run (`npx playwright --version`).
- During triage prefer exact spec paths, named batches, or `--grep` over broad globs; quote bracketed route segments (`'app/[id]/page.spec.ts'`) so the shell does not expand them.
- Record the cleanup/kill command for the chosen stack before starting a long replay.

## 3) Build Lock and Stale Process Hygiene

```bash
# Find stale Next.js / test runners
ps aux | rg "next build|next dev|playwright"

# Inspect lock file
ls -la .next/lock
```

If lock exists and no active build owns it, remove lock and rerun.

## 3b) Artifact Expectations

- Confirm result artifact paths exist before reading them (`test -f <error-context.md>`).
- If an artifact path is missing, inspect the latest `test-results/` index first instead of assuming the run produced nothing.

## 4) Timeout Budget (Per-Test, Not Global)

Default policy:
- smoke tests: 30-60s/test
- API-heavy flows (generation/checkout/report): 90-180s/test

(Starting heuristics, not vendor defaults; Playwright's default test timeout is 30s.)

Apply timeout only to affected tests/steps. Avoid raising global timeout for the whole suite.

## 5) Escalation Decision

Escalate run permissions when all are true:
- failure is environment-level (`EPERM`, restricted bind, blocked process inspection), and
- command is required for requested validation, and
- no safe non-escalated alternative exists.

## 6) Execution Sequence

1. Reproduce one failing test with `--workers=1`.
2. Capture trace artifacts.
3. Fix determinism cause.
4. Rerun targeted suite.
5. Run broader regression last.
