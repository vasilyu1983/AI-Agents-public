# Exercise: Verified Handoffs and Recovery

Use this exercise to practice a complete coding handoff, including rejection
and recovery. It is an original, runtime-neutral training example, not a new
agent API or a claim that these steps have run. For a task this small, one
implementer and one verifier normally suffice; split workers here to practice
ownership boundaries before using them on larger independent work.

## Table of Contents

- [Task and acceptance contract](#task-and-acceptance-contract)
- [Ownership and workspace](#ownership-and-workspace)
- [Stages and artifacts](#stages-and-artifacts)
- [Validate a handoff](#validate-a-handoff)
- [Independent verification](#independent-verification)
- [Recovery drill](#recovery-drill)
- [Completion and sources](#completion-and-sources)

## Task and acceptance contract

In a disposable Python project, implement
`validate_rows(rows: list[dict[str, str]]) -> list[dict]` in
`csv_validation.py`. Inputs are already-parsed CSV data records. Return one
error object per invalid field, each with exactly `row`, `field`, and `code`.
Do not mutate the input. This exercise uses only the Python standard library.

Freeze these acceptance cases before implementation:

| Input condition | Expected behavior |
| --- | --- |
| Empty list | Return `[]` |
| `sku=" A "`, `quantity="02"` | Trim surrounding whitespace; valid, no errors |
| Missing or whitespace-only `sku` | `field="sku"`, `code="required"` |
| A later nonempty SKU repeats a trimmed earlier SKU | `field="sku"`, `code="duplicate"`; matching is case-sensitive |
| Missing quantity, `-1`, `1.5`, or `two` | `field="quantity"`, `code="invalid_quantity"` |
| Trimmed quantity consists of one or more ASCII digits, including `0` | Valid quantity |
| A row has both invalid SKU and quantity | Emit both errors, SKU first |

Number records from 2, as logical CSV records after the header, independent
of physical newline counts. Return errors in record order. Ignore extra keys;
all input values are strings. Blank SKUs do not enter the duplicate set.
Record nonempty SKUs even when that record's quantity is invalid. For example,
`[{"sku":"A","quantity":"1"},{"sku":" A ","quantity":"-1"}]`
returns errors for row 3: `sku/duplicate`, then `quantity/invalid_quantity`.

## Ownership and workspace

The lead records the task ID, exact starting commit, acceptance-contract hash,
allowed paths, runtime configuration, and run-level time/cost/retry limits.
Use the installed runtime's verified dispatch and permission controls; the
contract below is application data, not a native `output_schema` option.

| Role | Owns | Must not change |
| --- | --- | --- |
| Lead | Frozen contract, integration, checkpoint ledger, artifact collection | Unrelated user work |
| Implementer | `csv_validation.py` in its isolated workspace | Tests, grader, acceptance contract, checkpoint ledger |
| Test author | `tests/test_csv_validation.py` in a separate workspace | Implementation, grader, acceptance contract |
| Independent verifier | Fresh inspection and test output for the integrated candidate | Source, tests, grading rules, acceptance decisions |

Tell writers they are not alone and must preserve others' changes. Start both
writers from the same base and contract; integrate only their owned changes.
File ownership is a coordination rule, not sandbox enforcement. Keep evaluator
inputs and the authoritative ledger outside worker-writable locations. Do not
share a writable checkout or ask a verifier to repair code to make tests pass.

## Stages and artifacts

| Stage | Action | Evidence required to advance |
| --- | --- | --- |
| Define | Freeze contract and ownership | Base revision, contract hash, explicit paths and budgets |
| Produce | Implementation and tests can proceed independently | Each worker's report and owned artifact bytes |
| Integrate | Validate reports, inspect diffs, combine owned changes | Exact integrated candidate revision and artifact hashes |
| Verify | Fresh verifier checks the candidate against the contract | Captured command, exit status, stdout/stderr, findings and candidate identity |
| Accept | Lead checks the complete evidence set | Every required case and boundary satisfied; no unresolved finding |

A worker's report never advances the stage by itself. The lead or trusted
runner validates it, then records a checkpoint. Keep stage outputs separate
from worker messages so a restart can inspect the actual artifacts.

## Validate a handoff

Example wire shape, deliberately incomplete: replace placeholders with real
identities and hashes from the runner. This object must fail validation as-is.

```json
{
  "schema_version": 1,
  "task_id": "csv-validation-exercise",
  "stage": "implementation",
  "status": "ready_for_verification",
  "base_commit": "REPLACE_WITH_ACTUAL_BASE",
  "candidate_commit": "REPLACE_WITH_ACTUAL_CANDIDATE",
  "contract_sha256": "REPLACE_WITH_CONTRACT_HASH",
  "artifacts": [
    {"path": "csv_validation.py", "sha256": "REPLACE_WITH_FILE_HASH"}
  ],
  "checks": [],
  "blockers": []
}
```

Enforce both structural and semantic validation before dispatching a dependent
stage. A JSON parser proves only that the text parses.

1. **Structure:** require exactly the keys shown; reject additional fields.
   Require `schema_version` to be integer `1`, nonempty string identities,
   and arrays for `artifacts`, `checks`, and `blockers`. Reject unknown stages
   or statuses. Supported statuses are `ready_for_verification`, `blocked`,
   and `failed`; none means accepted. Every artifact has exactly `path` and
   `sha256` strings. Each check has exactly `command` (nonempty string array),
   `exit_code` (integer or null), and `evidence_ref` (string).
   Each blocker is a nonempty string. Reject placeholders and malformed hashes.
2. **Identity:** resolve commit IDs in the declared repository, require the
   expected base, and bind the candidate to an immutable snapshot. Verify the
   contract hash against the lead's frozen copy. The integrated candidate may
   differ from individual workers' commits; bind final verification to it.
3. **Artifacts:** normalize paths, reject traversal or symlink escapes, enforce
   file ownership, inspect untracked files as well as tracked diffs, and compute
   hashes from actual bytes. A hash supplied by a worker is not proof of scope.
4. **Checks:** reconcile claimed checks with runner-captured command results
   and evidence. A null exit code means no terminal success evidence. Empty
   `checks` permits only the next verification stage, never final acceptance.
5. **Status:** a failed command or unresolved blocker prevents acceptance.
   A `blocked` report identifies the missing dependency and owner; a `failed`
   report identifies the observed failure. Reject inconsistent ready reports.

The lead's checkpoint additionally binds the configuration/instruction hash,
grader version/hash, completed stages and their input/output hashes, pending
stages, attempt count, and accumulated resource usage. Store it atomically in
an authorized lead-owned location. Never accept worker-edited checkpoint state.

## Independent verification

Give a fresh verifier the integrated candidate, contract, and relevant tests.
Check all frozen cases, including duplicate ordering, ASCII-only quantities,
and input immutability. In the disposable candidate workspace, the reviewed
test command for this standard-library exercise is:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

Record that tests were discovered, not just a zero exit code. Inspect the
tests against the contract and add evaluator-owned hidden cases outside the
implementation worker's access where independence is needed. Test success
does not by itself prove complete coverage or acceptable code quality.

A filesystem-read-only verifier returns its report on stdout. The lead or
runner captures stdout, stderr and the real exit status into an authorized
artifact directory; the verifier must not write into protected `.codex/`
paths. If checks need temporary files or build output, run them in a separate
authorized disposable workspace. Enforce source/grader integrity before and
after verification; do not silently widen the verifier's permissions.

## Recovery drill

Interrupt verification after the lead has validated integration. On resume,
compare the base, candidate, contract, instructions/configuration, grader and
artifact hashes with the lead-owned checkpoint before reusing any stage.

| Observed state | Next action |
| --- | --- |
| Worker JSON parses but required identity is missing | Reject before dependent dispatch; request a corrected report within the existing retry budget |
| Integration evidence is intact; verification timed out with no exit status | Keep completion pending and rerun verification only |
| Candidate changed after verification | Invalidate verification and any downstream acceptance; inspect the new candidate and verify again |
| Contract or another upstream input changed | Invalidate affected stages and their dependents; reuse only independently valid work |
| Test fails against the unchanged contract | Return the defect to its owning writer; integrate the fix and verify the new candidate |
| Required artifact is missing or cannot be authenticated | Treat the claimed checkpoint as unverified; rebuild the affected stage |
| Budget exhausted or unresolved ambiguity blocks progress | Stop new dispatch; retain artifacts and report the blocker and required decision |

Do not blindly restart the whole workflow, reuse stale green checks, extend
budgets without authority, or replay a side effect merely because its receipt
is missing. Reconcile any external operation before retrying; this exercise
requires no external writes.

## Completion and sources

The exercise is complete when the lead can show the integrated change, actual
verification evidence, and an interruption recovered from the first invalid
or incomplete stage. A paper walkthrough demonstrates understanding only;
executed recovery requires a trace and artifacts. Neither means merge or
deployment occurred.

For the reusable contracts and stop rules, see [output contracts](output-contracts.md)
and [operational guardrails](operational-guardrails.md). This original exercise
was informed by Daniel Vaughan, *Agentic Coding with OpenAI Codex CLI*,
chapters 12 and 27, and [OpenAI's best practices](https://learn.chatgpt.com/guides/best-practices).
[Symphony's specification](https://github.com/openai/symphony/blob/main/SPEC.md)
illustrates explicit workflow boundaries and restart recovery; it does not
make this exercise's JSON contract a native Symphony or Codex schema.
