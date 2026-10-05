# Agent Eval Datasets

What changes about eval-dataset design when the system under test is a tool-using agent. General method — composition, sampling, annotation, versioning, contamination, bias audits — lives in [ai-evals eval-dataset-design.md](../../ai-evals/references/eval-dataset-design.md); sizing in [ai-evals eval-statistics.md](../../ai-evals/references/eval-statistics.md#paired-binary-sizing-mcnemar); kappa bands in [ai-evals threshold-derivation.md](../../ai-evals/references/threshold-derivation.md#measure-judge-human-agreement).

## Task mix

- Tag every case with the tools it requires (`requires_tools`), including an empty list for cases the agent should answer without tools. Tool-free cases catch over-calling; tool-requiring cases catch skipped or wrong calls.
- Take the tool-usage share from production traces, then over-sample what traffic under-represents: multi-step tool chains, tool errors and timeouts, refusals, and injection-bearing tool outputs.
- Keep the expected trace (tools, argument constraints, allowed order) next to the expected answer, so grading covers what the agent did, not only what it said. See [test-case-design.md](test-case-design.md).

## Real-failure regression pack

- Every production or pre-release failure becomes a case: the input, the tool responses the agent saw, and the corrected expected trace.
- Keep the pack small (about 15-25 cases) and fast. It answers "did a known failure come back", not "is the candidate better" — a comparison needs a set sized by power.
- Rerun scope and baseline policy follow [regression-protocol.md](regression-protocol.md).

## Golden vs dynamic sets for agents

- **Golden set:** versioned cases with frozen tool fixtures, so a score change means the agent changed, not the environment. Keep a held-out slice that is never used for prompt iteration.
- **Dynamic set:** sampled from recent production traces to catch new failure shapes and tool or API drift. Promote a dynamic case into the golden set once its failure is understood and its fixtures are frozen.
- Agent A/B runs on one golden set are paired; size them with the paired method, not a per-arm formula.
