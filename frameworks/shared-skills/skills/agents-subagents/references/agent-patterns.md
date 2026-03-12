# Agent Design Patterns

Detailed patterns for building effective Claude Code agents.

## Contents

- [Single-Responsibility Agent](#single-responsibility-agent)
- [Orchestrator Agent](#orchestrator-agent)
- [Verification Agent](#verification-agent)
- [Pipeline Agent](#pipeline-agent)
- [Research Agent](#research-agent)
- [Security Patterns](#security-patterns)
- [Context Management](#context-management)
- [Anti-Patterns](#anti-patterns)
- [Related](#related)

---

## Single-Responsibility Agent

**Purpose**: One agent, one job. Easier to debug, test, and maintain.

**Characteristics**:
- Focused scope (e.g., "optimize SQL queries" not "handle all database tasks")
- Minimal tool set (only what's needed)
- Clear success criteria
- Predictable behavior

**Template**:

```markdown
---
name: sql-optimizer
description: Analyze and optimize SQL queries for performance
tools: Read, Grep, Glob
model: sonnet
---

# SQL Optimizer

You optimize SQL queries. Focus on:

1. Index usage analysis
2. Query plan examination
3. Performance recommendations

Output optimization suggestions with before/after examples.
```

**When to Use**:
- Specific, well-defined tasks
- Quality-critical operations (security audits, code reviews)
- Tasks that benefit from deep expertise

---

## Orchestrator Agent

**Purpose**: Coordinate multiple specialized agents. Maintains high-level context while delegating details.

**Characteristics**:
- Uses `Task` tool to spawn subagents
- Maintains global plan/state
- Delegates implementation details
- Verifies integration between parts

**Template**:

```markdown
---
name: fullstack-builder
description: Coordinate frontend, backend, and database changes
tools: Read, Grep, Glob, Task
model: sonnet
---

# Fullstack Builder

You coordinate multi-layer changes by delegating to specialized agents:

1. Analyze requirements
2. Delegate database changes to sql-engineer
3. Delegate API changes to backend-engineer
4. Delegate UI changes to frontend-engineer
5. Verify integration

## Delegation Guidelines

- Provide clear, specific instructions to each subagent
- Include relevant context (file paths, constraints)
- Verify each agent's output before proceeding
```

**When to Use**:
- Multi-step workflows spanning domains
- Feature implementations touching multiple layers
- Complex refactoring across codebase

---

## Swarm Orchestrator

**Purpose**: Execute a plan using parallel subagents dispatched in dependency-aware waves or full parallelism.

**Characteristics**:
- Reads a plan with a task dependency graph
- Dispatches subagents with context-rich handoff prompts
- Tracks task state: pending → in_progress → completed/failed
- Validates each agent's output before marking done
- Resolves conflicts between parallel outputs

**Key responsibilities**:
1. Manage plan state (which tasks are done, blocked, or in-progress)
2. Dispatch subagents with full context (plan reference, goals, files, acceptance criteria)
3. Validate subagent work against acceptance criteria
4. Resolve merge conflicts between parallel agents
5. Ensure project moves forward toward plan completion

**Template**:

```markdown
---
name: swarm-orchestrator
description: Execute multi-task plans using parallel subagent dispatch with dependency tracking
tools: Read, Grep, Glob, Task, Bash
model: opus
---

# Swarm Orchestrator

Execute the plan by dispatching subagents in waves.

## Workflow

1. Load and parse the plan (task graph, dependencies, file ownership)
2. Identify Wave 1: all tasks with empty depends_on
3. For each unblocked task, dispatch a subagent with:
   - Plan reference and task goals
   - File ownership boundaries
   - Acceptance criteria
   - Implementation steps
4. Wait for wave completion
5. Validate each output (tests, lint, acceptance criteria)
6. Resolve any conflicts between parallel outputs
7. Update plan state, identify next wave
8. Repeat until all tasks complete

## Subagent Prompt Template

For each dispatched subagent, provide:

- Plan: [path to plan file]
- Goals: [what this task achieves in context of the plan]
- Dependencies: [completed prerequisite tasks and their outputs]
- Files to create/modify: [full paths, owned by this agent]
- Do-not-touch: [files owned by other agents]
- Acceptance criteria: [specific, testable conditions]
- Steps: [numbered implementation instructions]
```

**When to Use**:
- Executing plans with 3+ independent tasks
- Feature implementations that can be parallelized
- When speed matters but accuracy must be maintained

---

## Verification Agent

**Purpose**: Quality gates. Check work before it proceeds.

**Characteristics**:
- Read-only (never modifies code)
- Fast (use `haiku` model)
- Binary output (PASS/FAIL)
- Clear checklist

**Template**:

```markdown
---
name: pre-commit-checker
description: Verify code quality before commits
tools: Read, Grep, Bash
model: haiku
---

# Pre-Commit Checker

Run quality checks:

- [ ] Linting passes
- [ ] Tests pass
- [ ] No console.logs
- [ ] No TODO comments
- [ ] Types correct

Return PASS or FAIL with details.
```

**When to Use**:
- Pre-commit hooks
- PR review automation
- Continuous integration gates

---

## Pipeline Agent

**Purpose**: Sequential workflow stages with handoffs.

**Stages**:
1. **Spec** — Read requirements, write specification
2. **Architect** — Validate design, produce ADR
3. **Implement** — Write code and tests
4. **Verify** — Run checks, update docs

**Template**:

```markdown
---
name: feature-pipeline
description: End-to-end feature implementation from spec to deploy
tools: Read, Grep, Glob, Task
model: sonnet
---

# Feature Pipeline

## Stage 1: Specification
Invoke pm-spec agent to analyze requirements.
Status: READY_FOR_ARCH

## Stage 2: Architecture
Invoke architect-review agent to validate design.
Status: READY_FOR_BUILD

## Stage 3: Implementation
Invoke implementer-tester agent to write code.
Status: READY_FOR_VERIFY

## Stage 4: Verification
Run pre-commit-checker agent.
Status: DONE
```

---

## Research Agent

**Purpose**: Gather information from documentation, web, codebase.

**Characteristics**:
- Read-only with web access
- Returns structured findings
- Cites sources
- Never modifies code

**Template**:

```markdown
---
name: tech-researcher
description: Research technologies, frameworks, and best practices
tools: Read, Grep, Glob, WebFetch, WebSearch
model: sonnet
---

# Technology Researcher

You research technologies and provide structured analysis.

## Output Format

### Summary
[1-2 sentence overview]

### Key Findings
- Finding 1 (source: URL)
- Finding 2 (source: URL)

### Recommendations
- Recommendation 1
- Recommendation 2

### Sources
[List all URLs consulted]
```

---

## Security Patterns

### Deny-All Default

```yaml
# Start with no tools, add only what's needed
tools: Read, Grep  # Read-only by default
```

### Sensitive Action Confirmation

```markdown
## Before Destructive Actions

1. List what will be changed
2. Ask for confirmation
3. Proceed only with explicit approval

Never run without confirmation:
- git push
- rm -rf
- Database migrations
- Infrastructure changes
```

### Context Isolation

```markdown
## Context Management

- Each subagent has isolated context
- Orchestrator maintains global state (compact)
- Use CLAUDE.md for shared conventions
- Never pass full codebase to subagents
```

---

## Anti-Patterns

### Avoid: God Agent

```yaml
# BAD: Too many responsibilities
name: do-everything
description: Handle all development tasks
tools: Read, Write, Edit, Bash, WebSearch, Task, ...
```

**Problem**: Unpredictable, hard to debug, context bloat.

### Avoid: Tool Overload

```yaml
# BAD: All tools for a read-only task
name: code-reviewer
tools: Read, Write, Edit, Bash, WebSearch, Task
```

**Problem**: Security risk, unnecessary permissions.

### Avoid: Vague Descriptions

```yaml
# BAD: Unclear when to invoke
description: Help with code stuff
```

**Problem**: Claude can't determine when to use this agent.

---

## Related

- [agent-tools.md](agent-tools.md) — Tool capabilities reference
- [../SKILL.md](../SKILL.md) — Agent quick reference
