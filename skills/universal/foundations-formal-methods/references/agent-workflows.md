# Agent workflows: worked TLA+ example and reusable properties

Read this reference when an agent, tool loop, approval gate, retry, lease, or handoff protocol needs a correctness claim. The worked example was model checked with TLC (`tla2tools.jar` "Version 2.19 of 08 August 2024"). The traces below are copied from TLC output, not written by hand. The spec and config are in [assets/tla/](../assets/tla/IdempotentRetry.tla).

## Problem: an idempotent tool call with retries

An agent calls a side-effecting tool once per logical request. Examples are "charge card", "send email", and "create ticket". Requests and responses can be lost. The agent retries after a timeout, and the server runs more than one worker.

Model variables:

- `agent`: idle, waiting, done, or escalated.
- `retries`: how many times the agent has retried.
- `net`: requests in flight.
- `resp`: responses in flight.
- `wpc[w]`: each worker's program counter.
- `key`: the idempotency-key record, which is absent, reserved, or completed.
- `execs`: how many times the side effect ran.

Environment assumptions:

- The network can lose any request or response.
- The agent can time out at any moment while it waits. This models arbitrary delay.
- There are no crashes. Adding crashes is the next step, described below.

| Property | Formula | Class |
|---|---|---|
| No double side effect | `AtMostOnce == execs <= 1` | State invariant (safety) |
| No phantom success | `AckImpliesEffect == agent = "done" => execs >= 1` | State invariant (safety) |
| Good path reachable (vacuity probe) | `NeverDone == agent /= "done"` must be **violated** | Reachability witness |
| Retry path reachable (vacuity probe) | `NeverDoneAfterRetry == ~(agent = "done" /\ retries > 0)` must be **violated** | Reachability witness |

Every run used `MaxRetries = 1` and `-deadlock`. The deadlock check is off because `done` and `escalated` are intended terminal states, not deadlocks.

## Results, one protocol variant at a time

The constant `Mode` selects the server protocol.

| Mode | Server protocol | Workers | TLC result |
|---|---|---|---|
| `none` | No idempotency key | {w1} | `AtMostOnce` violated, 10-state trace |
| `check` | Check key, then execute, then record (three separate steps) | {w1} | **No error**. This is a small-scope artifact. |
| `check` | Same | {w1, w2} | `AtMostOnce` violated, 9-state trace |
| `reserve` | Reserve the key atomically at check; a duplicate replies at once | {w1, w2} | `AtMostOnce` holds; `AckImpliesEffect` violated, 9-state trace |
| `complete` | Reserve atomically; a duplicate replies only after the original's result is recorded | {w1, w2} | Both invariants hold (93 distinct states). Both vacuity probes are violated, so the success path and the retry path are reachable |

### Counterexample 1: check-then-act race (`Mode = "check"`, two workers)

```text
1 Initial   agent=idle     net=0 key=absent execs=0 wpc=(free, free)
2 Send      agent=waiting  net=1
3 Retry     net=2 retries=1              timeout fires while the original is still in flight
4 Deliver   wpc=(received, free)
5 Check     wpc=(owner, free)            w1 sees key=absent
6 Execute   execs=1 wpc=(executed, free) w1 has not recorded the key yet
7 Deliver   wpc=(executed, received)
8 Check     wpc=(executed, owner)        w2 also sees key=absent
9 Execute   execs=2                      AtMostOnce violated
```

With one worker, the same protocol passes, because the check-execute-record steps cannot interleave. **A model instance that is too small to exhibit the interleaving produces a false "holds".** Choose each constant so that it can express the bug class you are testing for. Two concurrent handlers is the minimum for check-then-act races.

### Counterexample 2: phantom acknowledgement (`Mode = "reserve"`)

```text
1-5  Initial, Send, Retry, Deliver(w1), Check(w1)   key=reserved, w1 is the owner, execs=0
6    Deliver(w2)
7    Check(w2)       w2 sees key=reserved and becomes the duplicate
8    ReplyDup(w2)    resp=1: the duplicate replies before w1 has executed
9    Receive         agent=done, execs=0   AckImpliesEffect violated
```

Fixing the double charge introduced a phantom success: the agent reports "charged" while nothing has run. Always check the progress/honesty property alongside the property you just fixed.

### Fixed protocol

In `Mode = "complete"`, the duplicate waits until `key = "completed"` and then replays the recorded result. TLC found no error for `TypeOK`, `AtMostOnce`, or `AckImpliesEffect` over 93 distinct states. The vacuity probes were violated in 7 and 8 states respectively, which shows that the result is not vacuous.

What this establishes: the three invariants hold in this finite model, with two workers, one retry, lossy links and no crashes. It does not establish:

- The same result for more retries or workers. Rerun with larger constants, or write an inductive invariant for an unbounded claim.
- Liveness. The waiting duplicate blocks forever if the owner never records.
- Correspondence with any real idempotency-key store.

## Next steps an expert would take

1. **Add `Crash(w)` together with a reservation lease or TTL.** A crashed owner leaves the key `reserved` forever. Either the request never completes (a liveness failure) or the lease expires and a second owner runs, which brings back the double-execution risk. At that point the side effect needs a fencing token or a server-side idempotency guarantee. Hand the lease and fencing design to [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md).
2. **State liveness with explicit fairness.** "Every request eventually reaches `done` or `escalated`" needs weak fairness on `Retry`, `Escalate`, and the worker actions. Do not assume fairness on `LoseRequest` or `LoseResponse`, because loss is adversarial. Check with a `PROPERTY` in TLC.
3. **Close the refinement gap with trace conformance.** Log each tool call as `(request_id, key_state, action)` and replay the logs against the `Next` relation. The first step with no matching transition is the finding. This is the PObserve approach: it validates structured service logs against P specifications post hoc (see [P case studies](https://p-org.github.io/P/casestudies/)).

## Other agent-shaped properties worth checking

| Protocol | Property | Modeling hint |
|---|---|---|
| Human approval gate | No irreversible call without an approval bound to the same action **and argument hash** | Model the approval as a `(action_id, args_hash)` pair. The agent is allowed to change the arguments after approval, which makes a time-of-check/time-of-use (TOCTOU) edit reachable |
| Cancellation | No side effect starts after the cancel is acknowledged | Treat cancel as a message that races with execute. Keep "ack cancel" and "effect stopped" as separate states |
| Subagent handoff or lease | At most one holder acts for each epoch | Add a holder crash and a lease expiry. Check it with fencing tokens and without them |
| Tool-permission policy | No combination of rules permits `delete` on production without approval | Encode the policy as SMT and ask the solver for a satisfying request. `sat` is a concrete bad request; `unsat` holds only for this encoding (see [tool-selection.md](tool-selection.md)) |
| Plan, approve, execute, retry, escalate loop | Terminates or escalates | Liveness under stated fairness. Retries need a bound or a decreasing variant |

For hazards the model cannot express, such as a wrong action whose effects are well-formed, use [foundations-safety-engineering](../../foundations-safety-engineering/SKILL.md) and its [agent STPA example](../../foundations-safety-engineering/references/agent-stpa-payments.md).
