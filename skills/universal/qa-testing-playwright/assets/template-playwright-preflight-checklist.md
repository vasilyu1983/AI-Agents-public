# Template: Playwright Preflight Checklist

Use this before running expensive Playwright suites.

## Run Context

- Workdir: `________________________`
- Command: `________________________`
- Target spec(s) or batch: `________________________`
- Operator: `________________________`
- Date: `YYYY-MM-DD`

## Server Topology

- [ ] Chosen one topology only: shared dev stack or Playwright `webServer`.
- [ ] If shared dev stack is used, start command is recorded: `________________________`.
- [ ] If shared dev stack is used, cleanup command is recorded: `________________________`.
- [ ] If Playwright `webServer` is used, target port `_____` is free before launch.

## Checklist

- [ ] Verified target specs exist (`rg --files <tests-root> | rg <pattern>`).
- [ ] Initial repro uses one exact spec or named batch plus `--workers=1`.
- [ ] Confirmed host binding requirement (`127.0.0.1` vs `0.0.0.0`).
- [ ] No stale `next`/`playwright` process conflicts.
- [ ] `.next/lock` checked and cleaned if stale.
- [ ] Webhook listeners, sidecars, or mock servers checked for stale processes.
- [ ] Per-test timeout set for long API-heavy steps (not global timeout inflation).
- [ ] Escalation decision recorded if sandbox/permission constraints detected.
- [ ] Trace/video/screenshot artifact path confirmed.
- [ ] Deploy-gate replay deferred until the targeted scope is green.

## Failure Classification

- Environment-level failure? `yes / no`
- Auth-state failure? `yes / no`
- State-sync failure? `yes / no`
- Optional-network noise? `yes / no`
- Degraded-mode or rate-limit behavior? `yes / no`
- Product-level failure? `yes / no`
- Evidence: `_____________________________________________`

## Next Action

- [ ] Targeted rerun
- [ ] Selector or oracle fix
- [ ] Auth/state recovery fix
- [ ] Escalate permissions
- [ ] Deploy-gate replay
- [ ] Stop and re-scope
