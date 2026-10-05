# Agent Harness Hygiene (Operational Addendum)

This is agent-operating discipline for running commands inside a coding-agent harness while
debugging — not debugging expertise itself. Load it when the debugging session involves running
shell commands as an agent and you need a consistent way to classify and report failures.

## Fast Failure Taxonomy (Default)

Classify every failure first:
- `path/glob`: missing path, shell expansion, quoting
- `cli-contract`: invalid flag/unsupported option
- `baseline`: pre-existing repo failure unrelated to current change
- `logic`: regression introduced by current edits
- `env/toolchain`: missing runtime/binary/version mismatch
- `auth-state`: session or protected-route bootstrap failed
- `state-sync`: backend state changed, but visible state has not converged
- `optional-network`: non-oracle request failed, but core journey may still be valid
- `degraded-mode`: rate-limit or fallback path activated and should be asserted intentionally

## Nonzero Exit Handling Standard

On any nonzero command:
1. Record first failing line.
2. Classify with the taxonomy above.
3. Choose the smallest confirming command.
4. Retry only after changing one variable (command/path/env/input).

## Fix-Loop Stop Rules

An agent fixing build or test errors one at a time must stop and report, not keep editing, when:
- the same error survives repeated distinct fixes (the attempt budget is set in local policy);
- a fix produces more new errors than it removes;
- the next fix would touch files or modules unrelated to the failing error;
- the fix needs a design change, a new dependency, or a toolchain install rather than a code edit.

The report names the error, each attempted fix with its result, and the premise those fixes
shared. For agent loop and scope-creep failure modes, see
[debugging-guide.md](../../ai-coding-agents/references/debugging-guide.md).

## Path/Glob Guardrail

Before using bracketed/dynamic paths:

```bash
test -e "<path>" || echo "missing path"
```

Prefer quoted paths and explicit file discovery:

```bash
rg --files <root> | rg '<needle>'
```

## Baseline Noise Control

When broad checks fail due to unrelated baseline issues:
- isolate task-relevant errors,
- continue with targeted verification,
- report baseline errors separately as `pre-existing`.

## Debugging Output Minimum

Every debugging report includes:
- failure signature,
- reproduction status,
- root-cause class,
- artifact inspected first (trace/log/error-context/profile),
- fix verification command,
- prevention mechanism added.
