# Eval Tooling Patterns

Use this file when the user is choosing an evaluation toolchain, not just designing the rubric. For full platform comparison with code examples and a detailed decision tree, see [`eval-platform-selection.md`](eval-platform-selection.md).

## Promptfoo

- Best fit for config-driven prompt and agent regression packs.
- Strong starting point for:
  - red-team suites
  - refusal packs
  - side-by-side prompt or model comparisons
  - coding agent evaluation with trajectory assertions (`trajectory:tool-used`, `trajectory:tool-sequence`)
- Prefer it when the team wants quick, reviewable config files and CI-friendly runs.
- Supports OpenAI Agents SDK, Claude Agent SDK, and other multi-agent frameworks natively.

## lmnr

- Best fit when traces and execution graphs matter as much as final answers.
- Use it for:
  - workflow regression analysis
  - latency and step-by-step visibility
  - debugging tool-choice drift
- Prefer it when the failure is "the agent took the wrong path" rather than only "the answer was bad."

## Agent Governance Toolkit

- Best fit when approvals, authorization, and policy controls must be tested as part of the agent runtime.
- Use it when prompt-level guardrails are not enough and the system needs middleware or runtime enforcement.
- Prefer it for enterprise or regulated environments where auditability matters.

## DeepEval (v4.0+)

- Best fit for pytest-style unit evals that live next to CI tests.
- v4.0 (2026) adds agent-native metrics: Task Completion, Tool Correctness, Step Efficiency, Plan Quality.
- Use `@observe` decorator for trace-based evaluation without rewriting agent code.
- Strong for iterative patch-eval-retry workflows in coding agents.

## Langfuse

- Best fit for production observability paired with online evaluation.
- 2026: native OpenTelemetry ingestion, code evaluators in the UI, MCP server.
- Use for continuous monitoring when offline eval passes but production behavior is uncertain.
- Pair with DeepEval or Ragas for offline test coverage.

## Selection Rule

| Primary need | Start here |
|--------------|------------|
| Quick regression and red-team packs | Promptfoo |
| Trace visibility and execution analysis | lmnr |
| Policy, approval, and authorization enforcement tests | Agent Governance Toolkit |
| pytest-style unit evals with agent metrics | DeepEval |
| Production tracing + online evals on live traffic | Langfuse |

These tools are complements, not strict alternatives. Many teams end up with one regression runner, one trace/governance layer, and one production observability tool.
