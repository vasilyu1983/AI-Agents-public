---
description: Named harness patterns: orchestrator-worker, evaluator-optimizer, planner-generator-evaluator, manager-vs-handoff, MCP-wrapper subagent, blueprint.
last_verified: 2026-09-16
status: stable
---

# Harness Patterns

Reference for structured multi-agent execution patterns that `agents-subagents` can hand off into.

## Table of Contents

- [Named Patterns Overview](#named-patterns-overview)
- [Blueprint Pattern](#blueprint-pattern)
- [Planner-Generator-Evaluator](#planner-generator-evaluator)
- [Orchestrator-Worker](#orchestrator-worker)
- [Evaluator-Optimizer](#evaluator-optimizer)
- [Manager vs Handoff](#manager-vs-handoff)
- [Reflection / Self-Correction](#reflection--self-correction)
- [Debate-Before-Dispatch](#debate-before-dispatch)
- [Mixture-of-Agents (MoA)](#mixture-of-agents-moa)
- [MCP-Wrapper Subagent](#mcp-wrapper-subagent)
- [Isolation Rules](#isolation-rules)
- [LangChain Naming Map](#langchain-naming-map)

## Named Patterns Overview

| Pattern | Lead role | Worker role | Use when |
|---------|-----------|-------------|----------|
| Blueprint | Harness sequencer | Alternating deterministic + agentic nodes | Verification must be deterministic even though creative steps are agentic |
| Planner → Generator → Evaluator | Planner | Generator + Evaluator | One worker should not also own sequencing and review |
| Orchestrator-Worker | Lead planner + synthesizer | Isolated workers with owned files | Task decomposes cleanly; lead owns the final answer |
| Evaluator-Optimizer | Evaluator scoring a gate | Generator retrying against feedback | Output quality is hard to verify with deterministic tests alone |
| Manager vs Handoff | Manager keeps control OR specialist takes over | Depends on mode | Decide whether ownership stays central or moves by domain/queue |
| Reflection / Self-Correction | Single worker critiquing its own output | (self) | Second-pass review materially improves a single worker's quality |
| Debate-Before-Dispatch | Orchestrator running 2-4 perspective agents | Perspective agents + synthesizer | Early disagreement is cheaper than late integration failure |
| Mixture-of-Agents (MoA) | Aggregator(s) layered on top of N parallel proposers | Heterogeneous proposers (or Self-MoA single-model) + aggregator(s) | High-stakes single answer where you can afford 5-10× tokens for a single-digit-pp accuracy gain |
| MCP-Wrapper Subagent | Parent that delegates an MCP-heavy task | Subagent that owns the MCP server | One MCP server is bloating every parent turn; parent rarely needs the raw tools itself |

## Blueprint Pattern

Use a harness when the workflow must alternate deterministic steps with agentic loops.

```text
[Deterministic] checkout repo, install deps, run baseline tests
       ↓
[Agentic]       read spec, plan, implement
       ↓
[Deterministic] run tests, lint, type-check
       ↓
[Agentic]       diagnose failures and fix
       ↓
[Deterministic] package, format, deliver
```

Rules:
- Deterministic nodes own setup, verification, and delivery.
- Agentic nodes own understanding, planning, and creative implementation.
- Verification loops should be capped; do not let an agent retry indefinitely.
- Parent threads should keep the authoritative requirements and merge the results back into a final decision or delivery step.

## Planner-Generator-Evaluator

Use the three-agent harness when one worker should not also own review and sequencing.

| Role | Responsibility | Typical mapping |
|---|---|---|
| Planner | decomposes work, maintains the plan, decides sequencing | plan/research subagent |
| Generator | executes implementation against owned files | implementer worker |
| Evaluator | reviews output, verifies correctness, feeds back risks | reviewer or verifier |

When to prefer this pattern:
- the task is long enough to risk context drift
- multiple files or subsystems need coordination
- verification requires judgment, not just a green test run
- you want the implementer to start from a fresh, reduced context packet

The existing `dev-feature-delivery` team already follows this shape.

## Orchestrator-Worker

One lead plans and dispatches, workers execute in isolation on owned files, lead synthesizes. This is the Anthropic multi-agent research pattern and the default shape for any dependency-aware fan-out.

Rules:
- Workers receive self-contained briefs, not the lead's transcript (fresh context).
- Each worker returns a structured report, not raw intermediate output.
- Lead owns merge order, validation, and final synthesis.
- Cap edit-capable workers at 3 unless they run in isolated worktrees.

For full orchestration guidance, see [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md).

## Evaluator-Optimizer

A generator produces output; a separate evaluator scores it against an explicit rubric; the generator retries against the evaluator's feedback until the gate passes.

Use when:
- Output quality is hard to verify with deterministic tests alone (design, prose, prompts, complex refactors).
- Retry-on-feedback can reduce routine human review, but its cost and quality depend on retry count, evaluator reliability, and rework; compare them on the target workflow.
- A clear rubric or acceptance criteria exists.

Guardrails:
- Cap the retry count (2-3). If the gate still fails, escalate to the lead rather than looping.
- Freeze the rubric before the first generation attempt.
- Evaluator should not also be the generator — the split is load-bearing.

## Manager vs Handoff

From the OpenAI Agents SDK naming:

- **Manager / agents-as-tools** — one orchestrator keeps control of the conversation. Specialist agents are exposed as tools. The lead applies consistent policy before and after each specialist call, and always owns the final response.
- **Handoff** — a specialist agent receives the conversation history and takes over the interaction. Ownership moves to the specialist; control does not automatically return.

Pick by ownership:

| Question | Manager | Handoff |
|---|---|---|
| Should the user experience one coherent owner? | Yes | No |
| Should policy be applied before and after every specialist call? | Yes | No |
| Does the conversation route by domain, queue, or workflow stage? | No | Yes |
| Is decentralized control acceptable? | No | Yes |

For the full pattern description and cross-platform takeaway, see [../../agents-swarm-orchestration/references/platform-patterns.md](../../agents-swarm-orchestration/references/platform-patterns.md) §"OpenAI Agents SDK".

**Concrete implementations of the manager pattern**: Spring AI's `@Agent` orchestrator (Java), Composio's parallel-agents framework (Python), and the OpenAI Agents SDK's agents-as-tools mode all express the same shape — central orchestrator, specialists exposed as callable tools, lead owns final response.

## Reflection / Self-Correction

A single worker critiques its own output before returning. The worker runs two passes: a first pass to produce, a second pass to review and revise.

Use for:
- Bounded single-worker tasks where a second read materially improves quality.
- Cases where adding a separate reviewer is overkill but unreviewed output is risky.

Do not use when:
- A real evaluator-optimizer split would be more effective.
- The worker's self-critique is likely to be biased by the same context that produced the flaw.

## Debate-Before-Dispatch

Before fan-out on high-complexity work, run 2-4 perspective agents in one session to argue tradeoffs. Output is a decision log that becomes part of each worker's task brief. This is the `agents-subagents` debate overlay pattern — see [debate-quickstart.md](debate-quickstart.md) for full setup.

Use when:
- Architecture decisions affect multiple workers' implementations.
- Unclear tradeoffs need explicit adjudication before workers diverge.
- High-risk changes where early disagreement is cheaper than late integration failure.

Skip for routine parallel work where the interfaces are already stable.

## Mixture-of-Agents (MoA)

Source: Wang, Wang, Athiwaratkun, Zhang & Zou, *Mixture-of-Agents Enhances Large Language Model Capabilities* ([arXiv:2406.04692](https://arxiv.org/abs/2406.04692), 2024) — reports a higher AlpacaEval 2.0 length-controlled win rate than a single frontier model. Self-MoA variant: Li, Lin, Xia & Jin, *Rethinking Mixture-of-Agents* ([arXiv:2502.00674](https://arxiv.org/abs/2502.00674), 2025) — reports that mixing outputs of one strong model can beat standard MoA on AlpacaEval 2.0 and on average across MMLU, CRUX and MATH.

Layered topology where N proposer agents fan out in parallel on the same prompt, then one or more **aggregator** agents synthesize their outputs into a single answer. Distinct from Orchestrator-Worker because every proposer answers the *same* question (not decomposed sub-tasks), and from Debate-Before-Dispatch because aggregation is non-interactive (no rebuttal rounds).

```text
Layer 0:  Prompt
Layer 1:  Proposer-1, Proposer-2, ... Proposer-N   (parallel, no inter-agent comms)
Layer 2:  Aggregator reads all proposals, produces unified draft
Layer 3+: Optional second aggregator(s), each refining the prior layer's draft
Output:   Final layer's response
```

### Variants

| Variant | Shape | When to use |
|---|---|---|
| **Standard MoA** | Heterogeneous proposers (different model families) + 1 aggregator | Soft-judgment tasks (writing, design, strategy); model diversity is the main lift |
| **Self-MoA** | Same strong model sampled N times + 1 aggregator | Verifiable tasks (math, code, structured reasoning) — single best model + variance reduction beats heterogeneity |
| **Pyramid-MoA** | Wide proposer layer narrows over multiple aggregator layers | Open-ended generation where progressive refinement helps |
| **Attention-MoA** | Aggregator weights proposers by learned attention over proposal embeddings | When proposers vary widely in quality and you want soft selection rather than hard vote |

### When to use

- Single-answer tasks where final quality matters more than token cost (5-10× cost is the typical regime).
- Cases where an Orchestrator-Worker fan-out doesn't apply because the task can't be decomposed.
- High-stakes outputs (architecture proposals, security reviews, strategic recommendations) where the published single-digit-pp accuracy gain (see Source above) is worth the spend.
- Stack with **G18 (BMV)** or **G19 (RCS)** as the aggregator's selection rule when proposals diverge.

### When NOT to use

- Decomposable tasks — Orchestrator-Worker is cheaper and reaches better answers.
- Latency-sensitive paths — every layer adds a round-trip.
- Trivial tasks — single-shot is fine. MoA is for tasks where you'd otherwise run a debate.
- Highly correlated proposers (same model, same prompt, same temperature) — degrades to single-shot with overhead.

### Aggregator selection rule

The aggregator is the load-bearing role. Pick by task shape:

| Aggregator strategy | Task shape | Mechanism |
|---|---|---|
| Synthesize-and-rewrite | Soft, open-ended | Standard MoA — aggregator drafts a unified answer |
| Pick-best | Discrete answer space | G18 BMV (Optimal Weight + ISP) |
| Pick-centroid | Open-ended with semantic clustering | G19 RCS (embedding centroid) |
| Confidence-weighted merge | Mixed claim quality | G07 mechanism-design synthesis + G11 prediction-market stakes |

### Composition

- **Orchestrator-Worker over MoA**: each "worker" can itself be an MoA cluster for high-stakes sub-tasks.
- **Reflection inside MoA**: aggregator runs Reflection / Self-Correction before emitting final.
- **Debate-Before-Dispatch → MoA**: debate decides the strategy; MoA generates the artifact.

## MCP-Wrapper Subagent

When one MCP server bloats every parent turn (tool descriptions can take a large share of the context window, and vendor field reports describe tool-selection accuracy falling as tool counts grow — see [cost-control.md](cost-control.md) §"MCP server overhead per spawn"; no primary publication located, so treat as direction only), wrap the server inside a dedicated subagent.

```text
Parent (no MCP attached)
  └─ delegates a task → MCP-wrapper subagent
       └─ has the MCP server in its frontmatter
       └─ runs tools, returns a structured summary
Parent (still no MCP attached) ← receives summary only
```

Use when:

- One MCP server is responsible for most of the parent's context bloat (Linear, GitHub, Atlassian, Stripe, etc.).
- The parent rarely needs the raw tools — a summary or structured result is enough.
- Multiple parent turns trigger the same description tax even though the server is only used occasionally.

Guardrails:

- The wrapper subagent must own the MCP exclusively; the parent should not also reference it (defeats the purpose).
- Keep the wrapper's task brief explicit — it cannot ask the parent for clarification mid-call.
- For MCPs the parent uses *every* turn, inline frontmatter scoping is simpler than wrapping.

Source framing: Cra.mr, 2026. Cross-references: [traps-and-antipatterns.md](traps-and-antipatterns.md) §"MCP server token bloat", [cost-control.md](cost-control.md) §"MCP server overhead per spawn".

## Isolation Rules

Production harnesses isolate workers to prevent cross-contamination.

| Platform | Isolation mechanism |
|---|---|
| Claude Code | `isolation: worktree` for write-capable subagents |
| Codex | runtime-managed thread/workspace isolation; verify the target surface |
| Any runtime | explicit owned-file boundaries for write-capable workers |

Rules:
- Use isolated workers for parallel edits or risky changes.
- Keep review and research workers read-only whenever possible.
- On Codex, do not assume git-worktree semantics unless the runtime surface explicitly provides them.
- If isolation is unclear, reduce concurrency before expanding it.

## LangChain Naming Map

LangChain's `Choosing the Right Multi-Agent Architecture` taxonomy uses different names for the same shapes covered above. Map them when reading external material:

| LangChain term | This skill's name | Notes |
|---|---|---|
| Supervisor | Manager (§Manager vs Handoff) | Central orchestrator routes to specialists; same pattern, different label. |
| Swarm | Debate-Before-Dispatch (with synthesizer) or peer-handoff teams | Peer agents collaborate without a central supervisor; in this skill, debate-with-synthesis is the structured form. Hierarchical/recursive swarm specifically lives in [`../../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md#named-patterns). |
| Hierarchical | Orchestrator-Worker with sub-orchestrators | Multi-level supervisor tree; owned by the swarm-orchestration sibling skill. Bound nesting through prompts and repository policy; do not rely on an undocumented Codex `max_depth` key. |
| Network / handoff | Manager vs Handoff (handoff mode) | Conversation history transfers; ownership moves. |

Use this table when porting an external pattern (LangChain, LangGraph, Spring AI, OpenAI Agents SDK) into this skill's terminology — the underlying mechanics are the same, only the labels differ.
