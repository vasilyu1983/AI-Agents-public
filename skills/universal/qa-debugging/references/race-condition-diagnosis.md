# Race Condition Diagnosis

How to prove a concurrency bug exists, reproduce it on purpose, and know the fix is real.
Textbook patterns (double-checked locking, read-modify-write, lost update) are assumed
knowledge; this file covers the decisions around them.

## Contents

- [Decision Flow](#decision-flow)
- [Detectors and Their Blind Spots](#detectors-and-their-blind-spots)
- [Reproduce on Purpose](#reproduce-on-purpose)
- [Hangs and Deadlocks](#hangs-and-deadlocks)
- [Async and Database Races](#async-and-database-races)
- [UI State Races](#ui-state-races)
- [Proving the Fix](#proving-the-fix)

---

## Decision Flow

1. **Classify the symptom.** Corrupt or lost value suggests a data race or atomicity violation.
   A hang suggests deadlock or a lost wakeup. Wrong order suggests an order violation. Duplicate
   side effect suggests a retry without idempotency.
2. **Run the detector for the language before theorizing** (table below). A detector report
   with two stacks is stronger evidence than any amount of reasoning about interleavings.
3. **Detector is clean but the symptom persists:** the race is outside its view (across
   processes, in the database, across async yield points, or in uninstrumented code). Move to
   delay injection or forced interleaving.
4. **Failure rate is low and re-runs are not converging:** stop re-running. Capture one failing
   execution (rr, core dump, tail-sampled trace) per `systems-debugging-tools.md`.

## Detectors and Their Blind Spots

| Runtime | Default detector | Blind spot |
|---------|------------------|-----------|
| C / C++ | ThreadSanitizer: `-fsanitize=thread -g -O1` | Only sees races that actually execute in this run; uninstrumented libraries cause false negatives |
| Rust | TSan on nightly: `RUSTFLAGS="-Zsanitizer=thread" cargo +nightly test -Zbuild-std --target <triple>` | Without `-Zbuild-std` the uninstrumented std produces false positives; `unsafe`-free code rarely has data races, so look for logic races instead |
| Go | `go test -race` / `go run -race` | Same "must execute" limit; channel-ordering logic bugs are not data races and are not reported |
| JVM | Static analysis (SpotBugs concurrency patterns) plus stress tests; no mainstream dynamic detector in CI | Static tools flag inconsistent synchronization, not actual interleavings |
| Python | No data-race detector; the GIL hides many races but not check-then-act across I/O or across processes | Free-threaded builds remove GIL protection that old code silently relied on |
| Node.js / asyncio | None; races are logical, at `await` points | Every `await` is a possible interleaving point |

For Rust, install the nightly `rust-src` component before `-Zbuild-std`, choose a supported
target, and verify the [Unstable Book's sanitizer requirements](https://doc.rust-lang.org/unstable-book/compiler-flags/sanitizer.html).
`--target` keeps sanitizer flags off host build scripts/procedural macros. TSan cannot observe
atomic fences or synchronization implemented with inline assembly.

- **TSan adaptive delay.** When a race is suspected but a normal TSan run does not trigger it,
  `TSAN_OPTIONS=enable_adaptive_delay=1` injects delays at synchronization points to perturb
  scheduling (tunable aggressiveness). It is off by default and newer than most TSan docs; check
  that your Clang has it (clang.llvm.org ThreadSanitizer docs).
- **TSan cost** is large (multi-x CPU and memory). Run it as a dedicated CI job on the
  concurrency-heavy suite, not on every test.
- **A clean detector run is not proof of absence.** It proves no race occurred on the paths and
  schedules that ran.

## Reproduce on Purpose

Pick the cheapest technique that makes the failure deterministic:

| Technique | Use when | Note |
|-----------|----------|------|
| Barrier-start stress test (all workers released at once, many iterations) | First attempt; cheap | Report the failure rate (for example 3/1000), not pass/fail |
| Delay injection around the suspect read/write | You have a hypothesis about which window matters | Widening the window should raise the failure rate; if it does not, the hypothesis is wrong. That is the disconfirming test |
| Forced interleaving (events/latches making thread A pause after its read until B writes) | You need a deterministic regression test | This is the test that should ship with the fix |
| rr `--chaos` or TSan adaptive delay | Rare native interleavings | See `systems-debugging-tools.md` for rr limits (single core) |
| Deterministic simulation or model checking (loom for Rust, Jepsen-style fault injection for distributed systems) | Protocol-level or distributed races | Expensive to set up; justified for core coordination code |

Rules:

- Never add a `sleep` to *fix* a race. A sleep in a *test* to force an interleaving is fine only
  if the test also asserts on the forced ordering (use latches, not timing, where possible).
- A stress test that "passed 1000 times" gives a bound, not a guarantee. If the original failure
  rate was 1/200, 1000 clean runs is meaningful; if it was 1/100000, it is not.
- For CI-only flakes, first rule out shared state between tests (ports, temp dirs, global
  singletons, test ordering) before assuming a production race.

## Hangs and Deadlocks

- **Get all-thread stacks from the live process before killing it**: `py-spy dump --pid`,
  `jcmd <PID> Thread.print`, `gdb -p <PID> -batch -ex 'thread apply all bt'`, the Go pprof
  goroutine endpoint. For Python, `faulthandler.enable()` alone does not handle SIGUSR1;
  `kill -USR1` without `faulthandler.register(signal.SIGUSR1, all_threads=True)` kills the
  process. Details in `systems-debugging-tools.md`.
- Two threads each waiting on a lock the other holds is a lock-ordering bug: fix by a global
  acquisition order, not by timeouts. A timeout converts a deadlock into a latent retry storm.
- All threads idle and no lock cycle usually means a lost wakeup (condition signalled before
  the waiter started waiting) or pool starvation (every worker blocked on a task queued behind
  it). Check pool size against nested submissions.
- Livelock looks like high CPU with no progress; stacks change on every sample but return to
  the same retry loop.

## Async and Database Races

- **Async check-then-act.** Any `await` between reading state and acting on it is a race window,
  even in single-threaded runtimes. The fix belongs at the data layer (transaction, conditional
  write), not in an in-process lock, because the next instance of the service does not share
  that lock.
- **Database races, in order of preference:**
  1. Single atomic statement (`UPDATE ... SET n = n + 1`, `INSERT ... ON CONFLICT`).
  2. Unique constraint as the invariant, plus handling of the violation.
  3. Optimistic concurrency (version column, conditional update, bounded retries) when
     contention is low.
  4. Pessimistic row lock (`SELECT ... FOR UPDATE`) when contention is high or the
     read-then-write spans logic.
  5. Raising isolation level: last, and only with a retry loop, because SERIALIZABLE aborts
     transactions rather than blocking them.
- **Distributed races** (split brain, lock TTL expiring mid-work, out-of-order events, duplicate
  delivery): a distributed lock without a fencing token checked by the resource is not safe. For
  duplicates, require idempotency keys at the side-effect boundary; "exactly once" delivery
  claims usually mean at-least-once plus deduplication.

## UI State Races

When a button, toggle, or submit "does nothing" or shows the wrong state, the cause is often
one handler call silently undoing another. Before reading any handler, map every store action
and context setter in scope: what it sets, and what it resets as a side effect
(`selectItem -> sets {selected, details}; resets {editMode}`). Flag resets of fields the action
does not own; most of these bugs are invisible without that map.

Then trace each touchpoint (handler, calls in order, fields each call sets and resets, what the
label promises, what the user sees) and check these patterns:

| Pattern | Signature |
|---------|-----------|
| Sequential undo | A later call in the same handler resets a field an earlier call set |
| Async race | Two promises write the same field; the final value depends on resolution order |
| Stale closure | A memoized callback reads state captured at an older render; repeated updates collapse into one |
| Missing transition | The label promises an effect (save, delete, send) the handler never performs |
| Dead branch | The guard on the real work is always false at the moment the handler runs |
| Effect interference | An effect watching the field resets it right after the handler sets it |

Confirm with a component test that clicks the control and asserts the user-visible result, not
the setter call. That test fails before the fix and passes after it.

## Proving the Fix

- The fix is verified only when the **forced-interleaving test fails before and passes after**,
  or the detector report disappears with a stated mechanism. "The flake stopped" after a change
  is symptom remission; see SKILL.md Cognitive Traps.
- Re-run the barrier stress test at the original measured failure rate and report the new rate
  with the number of runs.
- If the fix narrows the window rather than closing it (added lock on one path, not all),
  say so and label the result `probable`.
