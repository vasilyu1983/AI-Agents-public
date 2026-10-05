# Multi-session Planning State

Load this when a development task spans sessions or an agent run may outlast its current context. Use existing repository task artifacts when they already carry the same information.

## Select the state shape

| Work | Durable state | Update rule |
|---|---|---|
| Exploratory experiments with several viable approaches | `PLAN.md` for direction, `EXPERIMENTS.md` for curated attempts, `EXPERIMENT_NOTES.md` for raw chronological notes | Revise the plan when evidence changes; promote useful notes into the curated record. |
| Bounded implementation with a known outcome | `GOAL.md` for scope and success, `STANDARDS.md` for acceptance rules, `IMPLEMENT.md` for execution and verification, `PROGRESS.md` for decisions and completed work | Keep the goal stable unless scope changes; append evidence and decisions to progress. |

These are example layouts, not required file names. Do not create a new set if an issue, plan file, or task tracker already provides a durable handoff. Keep raw exploration separate from the concise state a new session must read.

## Resume and handoff

1. Read the goal or plan, current decisions, progress, and the next blocked dependency before editing.
2. Recheck the repository state and the last verification evidence; a prior report does not establish current completion.
3. Record the next bounded action, its owner, prerequisite, and success check at each session boundary.

For autonomous loop termination and checkpoint semantics, use [ai-coding-agents-state](../../ai-coding-agents-state/SKILL.md). For multi-wave worker dispatch, use [agents-swarm-orchestration](../../agents-swarm-orchestration/SKILL.md). This reference only chooses what planning state must survive a session boundary.

## Ambiguous initial requests

Before a long run, identify the outcome, intended user, success evidence, constraints, and unresolved decisions. Ask the human about a decision only when existing context cannot settle it; a short proposed answer can make the question easier to resolve. For an already-scoped agent-to-agent task, use its brief and return only specific blockers. Record settled decisions in the plan artifact before delegation.
