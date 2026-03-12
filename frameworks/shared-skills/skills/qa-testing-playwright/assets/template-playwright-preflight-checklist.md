# Template: Playwright Preflight Checklist

Use this before running expensive Playwright suites.

## Run Context

- Workdir: `________________________`
- Command: `________________________`
- Target spec(s): `________________________`
- Operator: `________________________`
- Date: `YYYY-MM-DD`

## Checklist

- [ ] Verified target specs exist (`rg --files e2e/tests | rg <pattern>`).
- [ ] Confirmed web server port `_____` is free or intentionally occupied.
- [ ] Confirmed host binding requirement (`127.0.0.1` vs `0.0.0.0`).
- [ ] No stale `next`/`playwright` process conflicts.
- [ ] `.next/lock` checked and cleaned if stale.
- [ ] Per-test timeout set for long API-heavy steps (not global timeout inflation).
- [ ] Escalation decision recorded if sandbox/permission constraints detected.
- [ ] Initial repro uses one test, one worker.
- [ ] Trace/video/screenshot artifacts path confirmed.

## Failure Classification

- Environment-level failure? `yes / no`
- Product-level failure? `yes / no`
- Evidence: `_____________________________________________`

## Next Action

- [ ] Targeted rerun
- [ ] Contract/selector fix
- [ ] Escalate permissions
- [ ] Stop and re-scope
