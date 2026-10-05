---
description: AI Systems — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## AI Systems

**Typical scenario**

You need to design an AI assistant that reads repo context, retrieves supporting evidence, and exposes a safe multi-agent workflow.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "ai-systems"`.

Scenario: Design an internal engineering copilot that can answer repo questions, plan implementation work, and run bounded software-code-review-board agents with traceable evals.

Required context:
- Users: engineers and tech leads
- Constraints: answers must be grounded, permission boundaries must stay explicit, and rollout must start with one engineering org

Instructions:
- ai-agent-architect defines the agent topology and tool boundaries
- ai-context-architect defines hot, warm, and cold context layers
- ai-retrieval-architect defines retrieval, citation, and evidence freshness rules
- ai-evals-observer defines evals, trace capture, and regression gates
- Blind memos first, then one chaired synthesis of the architecture recommendation
- Include a rollout path and the minimum eval bar required before broader rollout
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn agent_architect, context_architect, retrieval_architect, and evals_observer.

Task: design an internal engineering copilot for repo Q&A, planning, and bounded software-code-review-board workflows.

Context:
- users are engineers and tech leads
- answers must stay grounded
- permissions and tool boundaries must be explicit

Run the analysis in parallel, then synthesize:
- recommended agent topology
- context and retrieval contract
- eval plan and rollout gate
```

**Debate-first variant**

Use when the key disagreement is "single orchestrator plus tools" versus "multi-agent specialist system."
