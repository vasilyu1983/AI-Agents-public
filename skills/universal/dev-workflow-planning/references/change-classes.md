# Change Classes and First Moves

Load this when a change does not fit one class cleanly, when no automated test can show the failure, or when you must decide how much process a change needs. The class table itself is in [SKILL.md](../SKILL.md#change-classes-and-first-moves).

## Contents

- [Telling the classes apart](#telling-the-classes-apart)
- [Mixed requests](#mixed-requests)
- [When no red test is possible](#when-no-red-test-is-possible)
- [Depth of process: the cost of being wrong](#depth-of-process-the-cost-of-being-wrong)
- [Scaling each class up or down](#scaling-each-class-up-or-down)

## Telling the classes apart

Classify by what happens to observable behavior, not by the size of the diff or the word the requester used.

- **Fix vs change.** A fix needs an agreed statement that the current behavior is wrong: a spec, an acceptance criterion, a contract, or the requester's explicit confirmation. Without one, treat it as a change. The existing tests then encode the old intent, and editing them is a decision someone must see. If a "fix" has to edit an existing assertion, stop: either the test was wrong (say so and name it) or the request is a change.
- **Refactor vs everything else.** A refactor edits no test assertion and adds no behavior test. If either becomes necessary, the work is no longer a refactor; split it.
- **Add vs change.** An add leaves every existing test passing unedited. If an existing test must change for the new capability to fit, part of the work is a change; list that test in the plan.

## Mixed requests

Split a mixed request into one step per class, each with its own verification. Default order: refactor first, then the behavior step. The behavior change then lands on a green, already-restructured base, and a failure points at one step. Deviate when the refactor is only justified by the new behavior and the behavior may still be dropped; then do the behavior step first behind its tests and refactor after.

Never combine a refactor and a behavior change in one step. The suite that should prove "nothing changed" cannot tell which edit broke it.

## When no red test is possible

Some failures resist an automated test at first: rendering, timing and concurrency, environment or infrastructure faults. Do not skip the first move. Record a reproduction instead: the exact steps or script, the observed output on the current code, and the expected output. Re-run the same reproduction after the change. State in the handoff that no automated guard exists and why, so the gap is visible. For a fix whose cause is still unknown, route to [qa-debugging](../../qa-debugging/SKILL.md) before planning the fix.

## Depth of process: the cost of being wrong

The class decides the first move. Risk decides how much process surrounds it: research, a written plan, a review gate, extra reviewers, staged rollout. Each extra step buys information about whether the change is wrong. Decide with these four checks, taken from [foundations-decision-theory](../../foundations-decision-theory/SKILL.md):

1. **Name the cost of being wrong.** What breaks, who notices, and how it is undone: one revert or a flag toggle, or a data repair, a broken consumer, exposed data, moved money.
2. **Reversible and cheap: act.** The foundation's skip rule is "reversible and cheap: just try it" (`foundations-decision-theory/SKILL.md:22`). Use the lowest planning depth. The class's test-first rule still applies at every depth: it is the check, not the ceremony. Where a test can settle correctness, let it decide; the foundation also skips formal analysis when an oracle such as a test suite exists (`:26`).
3. **Buy a step only if its result could change the plan.** The foundation treats spikes, pilots and clarifying questions as information to price (`:15`), runs a study only when its net value beats acting now (`:102-104`), and gives zero value to a question whose every answer leads to the same next step (`:132`). Apply the same test to a research spike, a plan review or a second reviewer: if every outcome leads to the same next action, skip it.
4. **Irreversible harm is a gate, not a tradeoff.** The foundation treats ruin as a constraint, gated before any expected-utility calculation (`:72`). Data loss, security exposure, money movement and a broken public contract get the highest depth whatever the diff size, and speed is not traded against them.

Map the result onto the [Planning Depth](../SKILL.md#planning-depth) table. When the cost of being wrong is unclear, that uncertainty is the first thing to retire (Workflow step 3 in SKILL.md).

## Scaling each class up or down

| Class | Scale up when | Scale down when |
|---|---|---|
| fix | The defect sits in auth, data writes, payments or another irreversible path; the root cause is unknown; the fix alters a public contract (then part of it is a change) | The cause is clear, the fix is local, and one revert undoes it |
| change | Other callers, stored data or external consumers depend on the old behavior: plan expand → migrate → contract milestones ([Execution Model](../SKILL.md#execution-model)) | One internal consumer and no persisted format |
| refactor | Coverage is thin, so characterization tests come first; the move crosses module boundaries or files other workers own | The code is inside one unit whose existing tests already pin its behavior |
| add | It brings a new external dependency, a public interface, or newly stored data | It is internal, off by default behind a flag, and removable in one revert |

Test design for any class belongs to [qa-testing-strategy](../../qa-testing-strategy/SKILL.md); structural refactoring technique belongs to [qa-refactoring](../../qa-refactoring/SKILL.md).
