# Claim Ledger

A claim ledger keeps "one item, one owner" true when parallel agents or sessions take work from a shared backlog. It works with any tracker: a directory of files, an issue tracker, or a database table. The tracker only needs one operation that creates a claim or fails.

## Contents

- [Decide Whether You Need One](#decide-whether-you-need-one)
- [The Defect It Avoids](#the-defect-it-avoids)
- [Claim Record](#claim-record)
- [Protocol](#protocol)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)

## Decide Whether You Need One

1. **The lead assigns every item before dispatch.** The worker brief is the claim (`OWNED FILES`, Dispatch Workflow step 2). Use no ledger. This is the default.
2. **Workers pick their own items, or two or more lead sessions share one backlog or one tree.** Use a ledger. `foundations-team-theory` treats agents that assign themselves roles as a candidate form. It says reported gains need matched local validation ([SKILL.md:129](../../foundations-team-theory/SKILL.md)). So adopt self-claiming only when the lead cannot assign up front, and compare it with lead assignment on your own runs.
3. **Make each item own its shared state.** Before you add agents, team theory says to cut coupling first: modularize and give shared state a single owner ([SKILL.md:130](../../foundations-team-theory/SKILL.md)). If two items edit one file, merge them into one item before anyone claims. The ledger enforces ownership at run time; it does not repair a bad split.
4. **Prevent overlap; do not detect it later.** The research-team recipe says to avoid redundant assignment ([SKILL.md:160](../../foundations-team-theory/SKILL.md)). A ledger that only logs duplicate work after the fact fails this rule.

## The Defect It Avoids

A claim that reads the state and then writes it is not a claim. Two agents can both read "unclaimed", both pass the check, and both write. Each believes it owns the item.

The epic-claim command in [affaan-m/ECC](https://github.com/affaan-m/ECC) (commit `ef648e01`, MIT) has this shape. `scripts/lib/github-coordination/actions.js:46-70` reads the issue (`:51`), checks it is unclaimed (`:54`), and then edits the issue (`:71`). Nothing between the read and the write stops a second claimer. The comment at `:37-45` names the race and leaves it unfixed. Only the concept was adapted here; no code or thresholds.

## Claim Record

| Field | Holds |
|---|---|
| `item` | The backlog item ID |
| `owner` | The agent or session ID, plus the run ID from telemetry |
| `token` | Fencing token: 1 on the first claim, previous token + 1 on each reclaim |
| `lease_expires` | Absolute UTC time; the ledger's clock decides, not the worker's |
| `heartbeat_at` | Last renewal time |
| `branch` / `worktree` | Where the owner's partial work lives, so a reclaimer can find it |
| `status` | `claimed`, `done`, `failed`, or `released`, with a result or failure reference |

## Protocol

1. **Claim with one atomic create-or-fail step.**
   - Filesystem: `mkdir claims/<item>` fails when the directory exists. Or open `claims/<item>.lock` with `O_CREAT|O_EXCL`. Write the record inside after the create succeeds. Treat a claim with no readable record as held for one lease length from its file time.
   - Check that the filesystem honours exclusive create. Some network filesystems have not.
   - Tracker: use a conditional update (match on version, ETag or current status). A mismatch means the claim failed. If the tracker has no conditional write, it cannot be the authority. Keep the ledger in a store that has one and mirror the state to the tracker.
   - Check dependencies in the same step: an item is claimable only when all its dependencies are `done`. This read is safe because `done` never reverts.
2. **Hold a lease and renew it by heartbeat.** Set `lease_expires` from the longest silent step the worker runs, such as a full test suite. Do not take the length from another project; record your choice and tune it on your runs. A worker blocked in one long tool call cannot renew. So make the runner script heartbeat while the worker process is alive, or size the lease to cover that step. A renewal that finds a different token in the record means the worker lost the claim; it stops at once.
3. **Release on finish and on failure.** On finish, write the result reference and `done` in one write, then release. On failure, write `failed` with the reason, then release; the lead decides on a retry (escalate after one, as in Common Anti-Patterns). Put the release in a `trap` or `finally` so error paths release too. Lease expiry is the backstop for a killed process. Only the holder of the current token may release.
4. **Reclaim a stale lease, and only an expired one.** Move the stale claim aside in one atomic step, for example rename `claims/<item>` to `claims/.stale/<item>.<token>`. Rename on one filesystem lets only one reclaimer win. Then claim afresh with `token + 1`. The stale owner's branch keeps its partial work: the lead decides whether the new owner continues it or starts clean. Never delete it silently.
5. **Fence every write that matters.** Progress, result, merge request, and release each carry the token. The lead's merge step rejects any write whose token is lower than the ledger's current token. A worker that pauses, loses its lease, and wakes later holds an old token, so its result is refused and its branch is left for review. Git does not check tokens; the lead must check before it merges.

## Anti-Patterns

| Mistake | Fix |
|---|---|
| Read the status, then write the claim | One create-or-fail operation, or a conditional update |
| Lease with no fencing token | A paused worker overwrites the new owner; fence every write |
| Worker clock decides expiry | Compare against the ledger's clock only |
| Two items touch one file | Merge them into one item before claiming |
| Reclaim deletes the old branch | Move the claim aside; the lead decides what happens to the work |
| Ledger used when the lead already assigned everything | Drop it; the brief is the claim |

## Cross-References

- [../../foundations-team-theory/SKILL.md](../../foundations-team-theory/SKILL.md) — who should hold which item; centralized and decentralized forms
- [../../foundations-distributed-systems/SKILL.md](../../foundations-distributed-systems/SKILL.md) — lease and fencing theory (primitive #8, template `assets/templates/distributed-systems/08-leases-fencing.md`)
- [../../ai-coding-agents-state/SKILL.md](../../ai-coding-agents-state/SKILL.md) — runtime task lists and their built-in claiming (`references/task-list-coordination-and-teammate-routing.md`)
