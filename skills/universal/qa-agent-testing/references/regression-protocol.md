# Regression Protocol

Procedures for rerunning agent evals after prompt, tool, model, or grader changes.

## Contents

- [When to Rerun](#when-to-rerun)
- [Suite Tiers](#suite-tiers)
- [Rerun Process](#rerun-process)
- [Baselines and Online Evals](#baselines-and-online-evals)
- [Flake Handling](#flake-handling)
- [Recovery Procedures](#recovery-procedures)

## When to Rerun

| Trigger | Minimum Scope |
|---|---|
| Prompt or system instruction change | Smoke suite + affected regression cases |
| Tool added, removed, or behavior changed | Smoke suite + affected regression + security pack |
| Model version change | Smoke suite + refusal pack + targeted regression set |
| Judge or grader change | Smoke suite + calibration set + affected regression cases |
| Retrieval or knowledge update | Affected regression cases + grounding checks |
| Multi-agent workflow change | Handoff tests + coordination faults + affected regression cases |

## Suite Tiers

### Smoke Suite

- 5-8 highest-signal cases
- Used for PR gating
- Must include at least one refusal and one tool or trace check if the agent uses tools

### Regression Suite

- 15-25 cases from real failures, support tickets, or production traces
- Re-run on risky changes, not every small edit
- Keep cases stable and versioned

### Security Pack

- Prompt injection
- Tool-output poisoning
- Tool argument smuggling
- Secret exfiltration attempts
- Approval-boundary violations
- Tool timeouts, malformed payloads, and permission failures

### Optional Online Evals

- Sampled live traffic or canary comparisons
- Use for rollout confidence, not as a substitute for offline regression
- Log model, prompt, grader, and tool versions alongside online metrics

## Rerun Process

### 1. Record the change

```text
Date: YYYY-MM-DD
Version: vX -> vY
Change type: prompt / tool / model / judge / retrieval / workflow
Description: [what changed]
Expected impact: [what should improve]
Risk areas: [what could regress]
```

### 2. Select the minimum valid rerun scope

Prefer the smallest scope that still covers the risk.

### 3. Run tests with the canonical rubric

- Task totals use the 6-dimension rubric in `scoring-rubric.md`
- Refusals use the refusal rubric
- Objective policy failures override numeric scores

### 4. Compare to baseline

Track:

- Task average
- Refusal average
- Hard fails
- `PASS / CONDITIONAL / FAIL`
- Normalized quality band if you use one
- Latency, cost, and stability as separate suite signals

### 5. Analyze regressions

For each regression, record:

- Affected case
- Previous result
- Current result
- Root cause hypothesis
- Whether the issue is prompt, tool, grader, or model related

### 6. Decide

| Outcome | Action |
|---|---|
| PASS | Approve or merge |
| CONDITIONAL | Review weak cases and decide if risk is acceptable |
| INCONCLUSIVE | Add the missing pack and rerun; do not merge on it |
| FAIL | Fix forward or rollback |

## Baselines and Online Evals

### Baseline policy

Create or refresh a baseline when:

- The model changes materially
- The prompt architecture changes materially
- Tool workflows are redesigned
- You have accumulated enough small changes that older comparisons are noisy

### Online eval policy

Use online or canary evals when:

- Offline tests pass but production behavior still carries uncertainty
- The agent operates on live traffic or long-running workflows
- You need to compare two prompts, tool policies, or model versions in practice

Keep online eval artifacts reproducible:

- Version identifiers
- Sample window
- Grader version
- Tool and approval policy version

## Flake Handling

A verdict that flips across runs is a finding about one of three things. Attribute it before changing anything.

1. Rerun the case alone, k=5, with the same pinned prompt, model, tools, and fixtures. Keep every trace.
2. Classify from the traces:

| Evidence | Class | Action |
|---|---|---|
| Traces identical (same tool calls, same output), verdicts differ | Judge instability | Fix or replace the grader; rerun the judge on its calibration slice; the agent is not at fault |
| Trace shows timeout, rate limit, network error, clock or locale drift, unpinned dependency | Harness flake | Fix the mock, fixture, or freeze; rerun; do not log against the agent |
| Same input, different tool choices or different refusal decision | Agent nondeterminism | Real finding. For a blocking case (refusal, policy, side effect) it is a `FAIL`: an agent that sometimes refuses has not learned the rule. For a quality case, record the pass rate and gate on pass^k |

3. Quarantine only what you cannot attribute in one sitting. A quarantine record has: case id, first-seen date, k and observed pass rate, suspected class, owner, expiry date. A quarantined blocking case makes the suite `INCONCLUSIVE`; the gate does not go green because a case was removed from it.
4. On expiry the case is either fixed and restored or deleted with a note; a quarantine list is not a permanent home.

Do not add automatic retries to gate runs. A retry converts "fails 1 in 5" into "passes", which is the exact failure mode a refusal or side-effect pack exists to catch. Rerun cadence and pass^k aggregation are owned by [ai-evals flake-and-reproducibility.md](../../ai-evals/references/flake-and-reproducibility.md#quarantine-dont-ignore).

## Recovery Procedures

### Fix forward

1. Isolate the failing cases
2. Apply the smallest plausible fix
3. Rerun affected cases
4. If fixed, rerun the required minimum scope

### Rollback

1. Revert to the last passing version
2. Run the smoke suite
3. Update the regression log with rollback context
4. Investigate before attempting a new change

### Never skip logging

Even if you only rerun a smoke suite, record:

- What changed
- Which tests ran
- Which cases failed or improved
- Whether the result is `PASS`, `CONDITIONAL`, or `FAIL`
