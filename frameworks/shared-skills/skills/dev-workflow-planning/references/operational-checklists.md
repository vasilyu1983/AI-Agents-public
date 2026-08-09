# Operational Checklists

Pre-flight checks, verification protocols, and failure handling patterns for reliable dev sessions.

---
## Table of Contents

- [Command Preflight Protocol](#command-preflight-protocol)
- [60-Second Preflight](#60-second-preflight)
- [Git/Branch Safety Preflight](#gitbranch-safety-preflight)
- [E2E/Server Preflight](#e2eserver-preflight)
- [Shell Safety Gate](#shell-safety-gate)
- [CLI Compatibility Probe](#cli-compatibility-probe)
- [Tiered Verification Protocol](#tiered-verification-protocol)
- [Failure Ledger](#failure-ledger)
- [Done/Not Done Closure Contract](#donenot-done-closure-contract)
- [SDK Type Verification](#sdk-type-verification)
- [Example: verify Stripe SDK types before using planned API calls](#example-verify-stripe-sdk-types-before-using-planned-api-calls)
- [Bounded Parallelism](#bounded-parallelism)
- [Platform Note](#platform-note)
- [Practical Batch Pattern](#practical-batch-pattern)
- [Checkpoint Contract (every batch)](#checkpoint-contract-every-batch)
- [Navigation](#navigation)


## Command Preflight Protocol

Run this before broad edits, test runs, or multi-file reviews.

### 60-Second Preflight

1. Confirm context:
   - `pwd`
   - `git branch --show-current`
   - `ls -la`
2. Verify target paths before running heavy commands:
   - `test -e <path>` or `rg --files <root> | head`
   - Prefer discovery first, then exact-path commands.
3. Validate command flags against actual tool version:
   - Example: run `npx eslint --help` before assuming legacy flags like `--file`.
4. Quote glob-sensitive paths (especially App Router segments):
   - Use `'app/src/app/ask/[category]/page.tsx'` to avoid shell glob expansion errors.
5. Fail fast on path errors:
   - If command reports missing path/pattern, stop and re-derive repository shape before continuing.

### Git/Branch Safety Preflight

Run before `checkout`, `merge`, and `commit`:

- `git status --porcelain` (must be clean or intentionally scoped)
- `test -f .git/index.lock && ps aux | rg "[g]it"` (lock/process check)
- If switching branches with local changes, commit or stash first.

### E2E/Server Preflight

Before Playwright/full E2E:

- Verify target app dir exists (`test -d app`)
- Verify web server port is free (`lsof -i :3001`)
- Ensure test file/glob exists before running (`rg --files tests/e2e | rg <pattern>`)

---

## Shell Safety Gate

Run before any file/CLI operation:

1. Path check: `test -e <path>` (or `ls <path>`) before `sed/cat/rg` on a file.
2. Quote dynamic paths and patterns.
3. For multi-pattern ripgrep, always use `-e` form:

```bash
rg -n -e "pattern one" -e "pattern two" <targets>
```

4. For paths with glob chars (`[]`, `*`, `?`) or spaces, use quoting/escaping.

---

## CLI Compatibility Probe

Before first use in a session, run one capability probe and cache syntax for the rest of the task:

```bash
npx eslint --help
npx vitest --help
npx tsc --help
```

Use probed syntax, not assumed flags.

---

## Tiered Verification Protocol

Run checks in this order:

1. Edited-file lint/type checks.
2. Feature-scope tests.
3. Full lint/type/build gate once before handoff.

If the same baseline failure repeats unchanged twice, stop re-running broad checks and either:
- narrow scope, or
- record a baseline waiver in the handoff.

---

## Failure Ledger

After every failed command, capture:
- Command
- Failure class (path/glob/flag/env/baseline)
- What changed before retry

Do not retry an identical command without changing inputs/environment.

---

## Done/Not Done Closure Contract

Every execution summary must end with:
- `Done`: completed acceptance criteria
- `Not done`: remaining items/blockers
- `Checks run`: exact commands run + pass/fail/skip
- `Next required action`: one concrete next step

---

## SDK Type Verification

Plans written from documentation may reference APIs that don't match actual SDK TypeScript types. Before executing a plan step that calls an external SDK, grep the actual TypeScript definitions:

```bash
# Example: verify Stripe SDK types before using planned API calls
grep -r "total_count" node_modules/stripe/types/ || echo "NOT FOUND — check actual type"
```

Common mismatches found in production:
- `stripe.customers.list().total_count` → SDK has `data.length`
- `invoice.subscription` → API changed to `invoice.parent.subscription_details.subscription`

---

## Bounded Parallelism

- Max 3 active writer agents at once unless the repo already has proven orchestration discipline.
- Assign each writer a file ownership boundary.
- Prefer read-only discovery/planning agents before spawning writers.
- Merge or reconcile after each batch before spawning new writers.
- If tasks share mutable interfaces, pause fan-out and return to a single planner/owner.

### Platform Note

- Claude/local multi-actor workflows often need worktrees for isolation.
- Codex cloud execution already runs isolated; local worktrees are mainly for review or landing changes.

### Practical Batch Pattern

```text
Batch 1: discovery + plan
Batch 2: implementation in one domain
Batch 3: verification + fixups
Batch 4: handoff summary
```

### Checkpoint Contract (every batch)

Report in one block:
- what changed,
- what was verified,
- what is blocked,
- exact next command.

---

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Session Scope Budgeting](session-scope-budgeting.md)
- [Session Patterns](session-patterns.md)
