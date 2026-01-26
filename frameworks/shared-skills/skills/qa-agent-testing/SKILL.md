---
name: qa-agent-testing
description: "QA harness for agentic systems: scenario suites, determinism/flake controls, tool sandboxing, scoring rubrics (including LLM-as-judge), and regression protocols covering success, safety, reliability, latency, and cost."
---

# QA Agent Testing (Jan 2026)

Design and run reliable evaluation suites for LLM agents/personas, including tool-using and multi-agent systems.

## Default QA Workflow

1. Define the Persona Under Test (PUT): scope, out-of-scope, and safety boundaries.
2. Define 10 representative tasks (Must Ace).
3. Define 5 refusal edge cases (Must Decline + redirect).
4. Define an output contract (format, tone, structure, citations).
5. Run the suite with determinism controls and tool tracing.
6. Score with the 6-dimension rubric; track variance across reruns.
7. Log baselines and regressions; gate merges/deploys on thresholds.

Use the copy-paste templates in `assets/` for day-0 setup.

## Determinism and Flake Control

- Control inputs: pin prompts/config, fixtures, stable tool responses, frozen time/timezone where possible.
- Control sampling: fixed seeds/temperatures where supported; log model/config versions.
- Record tool traces: tool name, args, outputs, latency, errors, retries, and side effects.

## Two-Layer Evaluation (2026)

Evaluate reasoning and action layers separately:

| Layer         | What to Test                        | Key Metrics                                         |
|---------------|-------------------------------------|-----------------------------------------------------|
| **Reasoning** | Planning, decision-making, intent   | Intent resolution, task adhesion, context retention |
| **Action**    | Tool calls, execution, side effects | Tool call accuracy, completion rate, error recovery |

## Evaluation Dimensions (Score What Matters)

| Dimension          | What to Measure                                  | Level    |
|--------------------|--------------------------------------------------|----------|
| Task success       | Correct outcome and constraints met              | Agent    |
| Safety/policy      | Correct refusals and safe alternatives           | Agent    |
| Reliability        | Stability across reruns and small prompt changes | Agent    |
| Latency/cost       | Budgets per task and per suite                   | Business |
| Debuggability      | Failures produce evidence (logs, traces)         | Agent    |
| Factual grounding  | Hallucination rate, citation accuracy            | Model    |
| Bias detection     | Fairness across demographic inputs               | Model    |

## CI Economics

- PR gate: small, high-signal smoke eval suite.
- Scheduled: full scenario suites, adversarial inputs, and cost/latency regression checks (track separately from quality scoring).

## Robustness and Security Tests (Recommended)

- Metamorphic tests: run small, meaning-preserving prompt/input rewrites; enforce invariants on outputs.
- Prompt injection tests: treat tool outputs, retrieved text, and user-provided documents as untrusted; verify the agent does not follow embedded instructions that conflict with system/developer constraints.
- Tool fault injection: simulate timeouts, retries, partial data, and tool errors; verify graceful recovery.
- Differential testing: compare behavior across model/config versions for regressions and unexpected shifts.

## Do / Avoid

Do:
- Use objective oracles (schema validation, golden traces, deterministic tool mocks) in addition to human review.
- Quarantine flaky evals with owners and expiry, just like flaky tests in CI.

Avoid:
- Evaluating only "happy prompts" with no tool failures and no adversarial inputs.
- Letting self-evaluations substitute for ground-truth checks.

## Quick Reference

| Need | Use | Location |
|------|-----|----------|
| Build the 10 tasks | Task patterns + examples | `references/test-case-design.md` |
| Design refusals | Refusal categories + templates | `references/refusal-patterns.md` |
| Score runs | Detailed rubric + thresholds | `references/scoring-rubric.md` |
| Compute suite math quickly | CLI utility script | `scripts/score_suite.py` |
| Manage regressions | Re-run workflow + baseline policy | `references/regression-protocol.md` |
| Sandbox tools | Isolation tiers + hardening | `references/tool-sandboxing.md` |
| Test multi-agent systems | Coordination patterns + suite template | `references/multi-agent-testing.md` |
| Use LLM-as-judge safely | Biases + mitigations | `references/llm-judge-limitations.md` |
| Start from templates | Harness + scoring sheet + log | `assets/` |

## Decision Tree

```text
Testing an agent?
  - New agent?
    - Create QA harness -> Define 10 tasks + 5 refusals -> Run baseline
  - Prompt changed?
    - Re-run full 15-check suite -> Compare to baseline
  - Tool/knowledge changed?
    - Re-run affected tests -> Log in regression log
  - Quality review?
    - Score against rubric -> Identify weak areas -> Fix prompt
```

## Scoring and Gates

- Score each run with the 6-dimension rubric (0-3 each; max 18 per task).
- Prefer suite-level gating that accounts for variance; avoid treating non-determinism as a free pass.
- Use `scripts/score_suite.py` to compute averages, normalized scores, and basic PASS/CONDITIONAL/FAIL classification.
- For detailed methodology (including judge calibration and variance metrics), see `references/scoring-rubric.md`.

## Navigation

### Resources

- `references/test-case-design.md` - 10-task patterns + validation + metamorphic add-ons
- `references/refusal-patterns.md` - refusal categories + response templates + test tactics
- `references/scoring-rubric.md` - scoring guide, thresholds, variance metrics, judge calibration
- `references/regression-protocol.md` - re-run scope, baseline policy, recovery procedures
- `references/tool-sandboxing.md` - sandbox tiers, tool hardening, injection/exfil test ideas
- `references/multi-agent-testing.md` - coordination testing patterns + suite template
- `references/llm-judge-limitations.md` - LLM-as-judge biases, limits, mitigations

### Templates

- `assets/qa-harness-template.md` - copy-paste harness
- `assets/scoring-sheet.md` - scoring tracker
- `assets/regression-log.md` - version tracking

### External Resources

See [data/sources.json](data/sources.json) for:
- LLM evaluation research
- Red-teaming methodologies
- Prompt testing frameworks

## Related Skills

- **qa-testing-strategy**: [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) - General testing strategies
- **ai-prompt-engineering**: [../ai-prompt-engineering/SKILL.md](../ai-prompt-engineering/SKILL.md) - Prompt design patterns

## Quick Start

1. Copy [assets/qa-harness-template.md](assets/qa-harness-template.md)
2. Fill in PUT (Persona Under Test) section
3. Define 10 representative tasks for your agent
4. Add 5 refusal edge cases
5. Specify output contracts
6. Run baseline test
7. Log results in regression log

> **Success Criteria:** Each of the 10 tasks scores >= 12/18 and each refusal scores >= 2/3 (or PASS by your policy oracle), with stable results across reruns and no new hard failures.
