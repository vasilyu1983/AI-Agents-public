# Graph And Loop Engineering: Composition Router

## Scope And Terminology

**Graph engineering** and **loop engineering** are emerging, non-standard labels, not protocols or a settled architecture taxonomy. Use them as prompts to name the underlying design problem; do not select a framework or datastore from the label alone. LangChain describes graph engineering as constraining agent behaviour through a graph, and explicitly treats a loop as a directed cyclic graph; IBM likewise calls loop engineering an emerging practice. [LangChain: Graph Engineering](https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph), [IBM: Loop Engineering](https://www.ibm.com/think/topics/loop-engineering)

The terms overlap. A loop is often one cycle within an agent/workflow graph; an improvement graph can supervise many runs; and a knowledge/context graph can supply one node with evidence. They are not interchangeable.

## Choose The Graph's Job First

| If the question is... | It is this graph | Use it to model | Route for depth |
| --- | --- | --- | --- |
| "What may run next?", "Where do tools, agents, approval, retry, or a handoff go?" | **Agent/workflow graph** | Runtime state, nodes, transitions, branches, retries, pauses, and cycles | [`multi-agent-patterns.md`](multi-agent-patterns.md), [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md), `agents-subagents` |
| "How do recurring agents find, change, test, review, and promote work?" | **Networked improvement graph** | The feedback network across discovery, workers, evaluators, human gates, backlog, and durable evidence | [`autonomous-loop-patterns.md`](autonomous-loop-patterns.md), [`evaluation-and-observability.md`](evaluation-and-observability.md), [`../agents-hooks/SKILL.md`](../../agents-hooks/SKILL.md) |
| "What facts, documents, entities, decisions, and provenance should this run retrieve?" | **Knowledge/context graph** | Evidence relationships, retrieval routes, provenance, memory, and permissions—not runtime sequencing | [`context-graph-patterns.md`](context-graph-patterns.md), `ai-context-layer`, [`../ai-rag/SKILL.md`](../../ai-rag/SKILL.md), [`../ai-vector-brain/SKILL.md`](../../ai-vector-brain/SKILL.md) |

Do not call a workflow DAG a knowledge graph merely because it has nodes and edges. Do not use a knowledge graph as an execution plan. Do not treat the improvement graph as permission to release a change: evaluation and human approval remain explicit gates.

## Agent/Workflow Graph

Use an agent/workflow graph when the system's valid execution paths matter: deterministic code can sit beside model or agent nodes, while conditional edges express the permitted transitions. Production graphs commonly include cycles for tool retries, validation-and-revision, user input, or resumption; a DAG is only appropriate when cycles are genuinely unnecessary. [LangGraph overview](https://docs.langchain.com/oss/javascript/langgraph/overview), [LangChain: Graph Engineering](https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph)

For each node and edge, specify input/output state, authority, side effects, observability, and an exit or escalation condition. Keep deterministic routing in code where speed, cost, and predictability matter; use agentic routing only where the branch cannot be specified safely in advance. The OpenAI Agents SDK similarly distinguishes code-driven orchestration from LLM-driven orchestration and supports their combination. [OpenAI Agents SDK: multi-agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)

## Loop Engineering

Use a loop when a bounded goal needs repeated action and observation, not merely because an agent has tools. At minimum, state: goal and measurable acceptance criteria; action surface; independent observation/evaluation; adjustment or keep/revert rule; budget; and terminal, escalation, and kill conditions. IBM frames the basic cycle as goal, action, observation, and adjustment. [IBM: Loop Engineering](https://www.ibm.com/think/topics/loop-engineering)

An SDK's internal agent loop is not automatically a long-horizon improvement loop. For example, the OpenAI runner repeats model calls around tool calls and handoffs until final output or its turn limit; the surrounding system must still impose release controls, durable state, and an independent evaluator when it is changing code or production artifacts. [OpenAI Agents SDK: running agents](https://openai.github.io/openai-agents-python/running_agents/)

For coding-agent loop composition—automation, isolated worktrees, skills, connectors, subagents, and external state—use the practical account as a design input, not a normative standard. [Addy Osmani: Loop Engineering](https://addyosmani.com/blog/loop-engineering/)

## Minimal Composition Pattern

```text
knowledge/context graph --retrieves evidence--> workflow node
workflow graph --runs bounded loop--> action -> independent evaluation
networked improvement graph --records result--> backlog / human gate
human gate --permits promotion or stops the loop--> deployment
```

Keep the three graphs separately inspectable. A trace should answer what executed; a ledger should answer what improved and why; and a citation/provenance path should answer what evidence informed the action.
