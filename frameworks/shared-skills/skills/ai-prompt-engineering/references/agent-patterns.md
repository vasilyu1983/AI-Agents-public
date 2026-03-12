# Agent Patterns

*Purpose: Operational patterns for planning, tool use, error handling, and multi-step workflows in Claude Code agents.*

## Contents
- Agent operating contract
- Selective planning pattern
- Tool-call pattern
- Post-tool completion pattern
- Tool decision pattern
- Multi-step workflow pattern
- Validation pattern
- Error handling patterns
- Table-filling agents
- Agent rewrite pattern
- Classification agents
- Quality gates
- Anti-patterns
- Multi-agent orchestration patterns

---

# 1. Agent Operating Contract

Agents must:
- **Bias to action**: Implement solutions using reasonable assumptions rather than requesting clarification
- Decide tool vs no-tool
- Prefer parallel tool execution when operations are independent
- Produce deterministic structures
- Hide reasoning unless requested
- Validate inputs + outputs
- **Deliver working code, not just plans**: Plans guide implementation; never end with only a plan

Checklist:
- [ ] Action taken (not just planned)
- [ ] Tools batched where independent
- [ ] No visible reasoning
- [ ] Output format exact
- [ ] All fields returned  

---

# 2. Selective Planning Pattern (2025)

## 2.1 When to Plan

**Skip planning for ~25% of tasks** - straightforward work that doesn't benefit from explicit planning.

| Task Type | Planning | Rationale |
|-----------|----------|-----------|
| Single file edit | Skip | Obvious next step |
| Simple lookup | Skip | Direct action |
| Multi-file refactor | Plan | Coordination needed |
| Complex debugging | Plan | Multiple hypotheses |
| Architecture changes | Plan | Dependencies to track |

## 2.2 Planning Rules

- **Never create single-step plans** - if only one step, just do it
- **Plans guide edits; deliverable is working code** - never end with only a plan
- **Update plans after subtasks** - keep plan current with progress
- Use imperative verbs (find, compute, call, check)
- Short, operational sentences

## 2.3 Plan Structure (When Needed)

```text
Plan:
- step 1
- step 2
- step 3

Action:
null

Answer:
"final answer here"
```

Checklist:

- [ ] Plan has 2+ steps (or skip planning)
- [ ] Plan leads to implementation, not just analysis
- [ ] No narrative explanation
- [ ] Deterministic verbs  

---

# 3. Tool-Call Pattern

## 3.1 Single Tool Structure

```

Plan:

- determine if tool needed
- prepare arguments
- call tool

Action:
{
  "tool": "tool_name",
  "input": { ... }
}

Answer:
null

```

Rules:

- Action object must match tool signature
- Answer must be null when using a tool

Checklist:

- [ ] Tool name correct
- [ ] Input object matches schema
- [ ] No extra keys
- [ ] Answer = null

## 3.2 Tool Preference Hierarchy (2025)

When multiple options exist for an operation, prefer in order:

| Priority | Tool Type | Examples | When to Use |
|----------|-----------|----------|-------------|
| 1 | Dedicated tools | `read_file`, `apply_patch`, `git` | Always prefer when available |
| 2 | Solver tools | `rg`, `grep`, file operations | When dedicated tool unavailable |
| 3 | Terminal commands | Shell, bash | Last resort only |

**Rationale**: Dedicated tools have better error handling, are more predictable, and integrate better with the agent framework.

## 3.3 Parallel Tool Execution (2025 - Batch-First)

**Core Strategy**: Think first. Before any tool call, decide ALL files/resources you will need. Batch everything.

```text
Parallel Batching Workflow:
1. Plan all reads/operations upfront
2. Issue ONE parallel batch
3. Analyze all results together
4. Repeat only if unpredictable results emerge
```

**Anti-Pattern**: Sequential file reading (one-by-one) - always batch independent reads.

**Parallel Structure**:

```json
{
  "actions": [
    {"tool": "read_file", "input": {"path": "file1.ts"}},
    {"tool": "read_file", "input": {"path": "file2.ts"}},
    {"tool": "read_file", "input": {"path": "file3.ts"}}
  ]
}
```

**Parallel Execution Rules**:

- Only parallelize truly independent operations
- Each tool input must be determinable before execution
- No tool can depend on another tool's output
- All tools must complete before proceeding

**When to Parallelize**:

- Multiple file reads for context gathering
- Multiple API calls with different endpoints
- Multiple validation checks that don't interact
- Batch operations on independent items

**When NOT to Parallelize**:

- Tool B needs output from Tool A
- Sequential dependencies exist
- Order of execution matters

Checklist:

- [ ] Batched all independent operations upfront
- [ ] No cross-dependencies in inputs
- [ ] All tool schemas match
- [ ] Avoided sequential reads when parallel possible  

---

# 4. Post-Tool Completion Pattern

## 4.1 Structure
```

Plan:

- review tool results
- compute final answer

Action:
null

Answer:
"final answer"

```

Rules:
- Interpret tool output strictly  
- No hallucinated fields  
- No re-calling tool unless needed  

Checklist:
- [ ] Tool result referenced directly  
- [ ] Answer matches required format  

---

# 5. Tool Decision Pattern (Binary)

## 5.1 Logic
```

If direct answer possible → no tool.
If data required → tool.
If uncertainty about data → tool.

```

Checklist:
- [ ] Explicit binary choice  
- [ ] Avoid tool use for trivial tasks  
- [ ] Avoid speculation  

---

# 6. Multi-Step Workflow Pattern

## 6.1 Generic Workflow

1. Interpret user request
2. Build plan
3. Retrieve information (tool or no-tool)
4. Transform data
5. Produce final answer

## 6.2 Rules

- Never skip planning
- Each step explicit and testable
- No invisible branching

## 6.3 Long-Horizon Task Management (Claude 4+)

For complex multi-window workflows that may span context compaction:

**State Tracking Strategy**:

- Create structured progress files (JSON/markdown) to track task state
- Use setup scripts (e.g., `init.sh`) to prevent repeated work
- Leverage git commits as state checkpoints
- Maintain both structured data (progress.json) and unstructured notes (dev-notes.md)

**Test-First Implementation**:

- Define test cases in JSON format before implementation
- Prevents rework after context compaction
- Provides clear success criteria
- Example: Create `tests.json` with expected inputs/outputs before coding

**Incremental Progress Pattern**:

```

Plan:

- focus on completing one feature fully
- commit working state to git
- update progress.json with completion status
- move to next incremental task

Approach:
- Steady incremental advancement over attempting everything at once
- Each commit represents a stable checkpoint
- Progress tracking survives context compaction

```

**Persistence Instructions**:

Include in system prompt for long-running tasks:

"Do not stop tasks early due to token budget concerns. Use progress files and git to maintain state across sessions. Always be as persistent and autonomous as possible."

**File Structure for Long Tasks**:

```
project/
├── progress.json          # Structured: completed tasks, current step, next actions
├── dev-notes.md          # Unstructured: context, decisions, issues
├── init.sh               # Setup: dependencies, environment, prevent re-runs
├── tests.json            # Definitions: test cases before implementation
└── src/                  # Implementation
```

Checklist:

- [ ] Progress file created and updated
- [ ] Init script prevents duplicate setup
- [ ] Tests defined before implementation
- [ ] Git commits mark stable checkpoints
- [ ] Clear "next action" documented in progress file

---

# 7. Validation Pattern

## 7.1 Input Validation
```

If input missing or invalid → return error object.

```

Example:
```

{
  "error": "missing_field",
  "field": "user_query"
}

```

Checklist:
- [ ] Error shape deterministic  
- [ ] No stack traces  
- [ ] No extra commentary  

---

## 7.2 Output Validation
Before returning:
- Check against output schema  
- Ensure no hidden reasoning  
- Ensure deterministic completion  
- Ensure required keys present  

---

# 8. Error Handling Patterns

## 8.1 Tool Error Pattern
```

Plan:

- tool failed
- propose fallback

Action:
null

Answer:
"Tool failed: short deterministic reason"

```

Rules:
- Expose only the failure state  
- No internal logs  
- No visible reasoning  

---

## 8.2 Missing Data Pattern
```

Answer:
"Required data not found in tool output"

```

Use cases:
- Empty responses  
- Missing IDs  
- Non-overlapping data sources  

---

## 8.3 Ambiguous Results Pattern
```

Answer:
"Ambiguous result. Provide one of: A, B, C."

```

Checklist:
- [ ] Never guess  
- [ ] State ambiguity explicitly  

---

# 9. Table-Filling Agents

## 9.1 Structure
```

Return a table with fixed columns:
Column A | Column B | Column C
...rows...

```

Rules:
- All rows must satisfy schema  
- Empty cells = `N/A`  
- Never create rows without evidence  

---

# 10. Agent Rewrite Pattern

## 10.1 Structure
```

Rewrite according to RULES:

- preserve meaning
- operational tone
- short sentences
- no added content

Input:
{{text}}

```

Checklist:
- [ ] Meaning preserved  
- [ ] Style enforced  
- [ ] Forbidden transformations avoided  

---

# 11. Classification Agents

## 11.1 Structure
```

{
  "class": "A|B|C",
  "reason": "short explanation"
}

```

Rules:
- Classes closed set  
- Reason 1–2 sentences  
- No hidden reasoning leaks  

---

# 12. Quality Gates

## 12.1 Pre-Execution Gate
- Task parsed correctly  
- Tool decision made  
- Plan stable  

## 12.2 Output Gate
- Format matches  
- No reasoning exposed  
- No hallucinations  
- All keys present  

---

# 13. Anti-Patterns (Avoid)

**Planning Anti-Patterns**:

- Single-step plans (just do the action)
- Ending with only a plan (deliver working code)
- Narrative planning (use imperative verbs)
- Excessive status updates (let the agent work autonomously)

**Tool Use Anti-Patterns**:

- Sequential file reading when parallel possible (batch upfront)
- Terminal commands when dedicated tools exist (use tool hierarchy)
- Answer + tool call in same turn
- Guessing missing values

**Error Handling Anti-Patterns (2025)**:

- Broad try/catch blocks that swallow errors
- Success-shaped fallbacks that hide failures
- Silent failures without logging
- Returning default values instead of propagating errors

**Output Anti-Patterns**:

- Visible chain-of-thought (hide unless requested)
- JSON + prose mixing
- Long paragraphs
- Hidden assumptions
- Ambiguous instructions

**TypeScript/JavaScript Anti-Patterns**:

- Unnecessary type casts (`as any`, `as unknown as`)
- Missing proper types and guard clauses
- Not reusing existing type helpers  

---

# 14. Multi-Agent Orchestration Patterns (2026)

As agentic systems scale, single-agent architectures give way to orchestrated teams of specialized agents. Gartner reported 1,445% surge in multi-agent system inquiries from Q1 2024 to Q2 2025.

## 14.1 Orchestration Architectures

| Pattern | Structure | Best For |
|---------|-----------|----------|
| **Centralized** | Single manager assigns tasks, controls workflow | Clear hierarchy, predictable workflows |
| **Handoff** | Agents delegate dynamically without central manager | Flexible routing, expertise-based delegation |
| **Federated** | Distributed coordination with governance controls | Regulated environments, cross-org collaboration |

### Centralized Orchestration

```text
┌─────────────────┐
│   Orchestrator  │
│   (Manager)     │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Researcher│ │Coder│ │Analyst│ │Writer│
└───────┘ └───────┘ └───────┘ └───────┘
```

**Orchestrator Prompt Pattern**:

```text
You are a task orchestrator. Given a user request:
1. Decompose into subtasks
2. Assign each subtask to the appropriate specialist agent
3. Collect and synthesize results
4. Return unified response

Available agents:
- researcher: Gathers information, searches documents
- coder: Writes and reviews code
- analyst: Validates results, runs tests
- writer: Formats final output

For each subtask, output:
{"agent": "agent_name", "task": "specific instruction", "depends_on": []}
```

### Handoff Orchestration

Agents dynamically delegate without central control:

```text
Agent A receives task
  → Can handle? → Execute
  → Cannot handle? → Identify best agent → Handoff with context
```

**Handoff Prompt Pattern**:

```text
You are a specialist in [domain]. When you receive a task:

1. Assess if this is within your expertise
2. If YES: Execute the task fully
3. If NO: Identify the appropriate specialist and hand off

To hand off, output:
{"handoff_to": "agent_name", "context": "relevant info", "task": "what to do"}

Never attempt tasks outside your expertise. Always hand off with full context.
```

### Plan-and-Execute Pattern (90% Cost Reduction)

Use frontier model for planning, cheaper models for execution:

```text
┌─────────────────────────┐
│   Planner (Claude/GPT)  │  ← Frontier model creates strategy
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Executor (Haiku/Mini) │  ← Cheaper model executes steps
└─────────────────────────┘
```

**Implementation**:

```python
# Planner: Frontier model (expensive, used once)
plan = frontier_model.generate("""
Create a step-by-step plan to accomplish: {task}
Output as JSON array of steps with clear instructions.
""")

# Executor: Cheap model (used for each step)
results = []
for step in plan:
    result = cheap_model.generate(f"Execute: {step['instruction']}")
    results.append(result)
```

## 14.2 Core Multi-Agent Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Manager-Worker** | One agent delegates, others execute | Task decomposition |
| **Swarm** | Agents collaborate on shared problem | Complex problem solving |
| **Debate** | Agents argue positions to reach consensus | Decision making, verification |
| **Pipeline** | Sequential handoff between specialists | Staged processing |

### Debate Pattern (Consensus Building)

```text
Agent Roles:
- Proposer: Suggests solution
- Critic: Identifies flaws
- Synthesizer: Combines best elements

Workflow:
1. Proposer generates initial solution
2. Critic evaluates and raises objections
3. Proposer addresses concerns
4. Synthesizer combines into final answer
5. All agents vote on acceptance
```

## 14.3 Human-Agent Collaboration Spectrum

| Mode | Description | Use When |
|------|-------------|----------|
| **Human-in-the-loop** | Human approves every action | High-risk, learning phase |
| **Human-on-the-loop** | Human monitors, intervenes if needed | Medium-risk, trusted agents |
| **Human-out-of-the-loop** | Fully autonomous operation | Low-risk, proven workflows |

**Autonomy Progression Pattern**:

```text
Start: Human-in-the-loop for all decisions
  ↓ (After N successful executions)
Progress: Human-on-the-loop for routine tasks
  ↓ (After demonstrated reliability)
Goal: Human-out-of-the-loop for specific workflows
```

## 14.4 Multi-Agent Checklist

- [ ] Orchestration pattern selected (centralized/handoff/federated)
- [ ] Clear agent specializations defined
- [ ] Handoff protocols with context preservation
- [ ] Human oversight level determined per task type
- [ ] Cost optimization (plan-and-execute) considered
- [ ] Error handling for inter-agent communication
- [ ] Logging and observability across agent boundaries

---

# 15. Quick Reference Table

| Task Type | Pattern | Template |
|-----------|---------|----------|
| Tool-based | Tool-Call | template-agent.md |
| Direct-answer | Plan-First | template-standard.md |
| Multi-step | Workflow Pattern | template-agent.md |
| Classification | Closed-Set Class | template-standard.md |
| Table filling | Table Pattern | template-standard.md |
| Error handling | Tool Error / Missing Data | template-agent.md |
| Multi-agent | Orchestration Patterns | See Section 14 |

