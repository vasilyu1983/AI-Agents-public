# Claude Code Agent Template

> Universal starting point for building Claude Code agents.
> Copy this file to `.claude/agents/your-agent-name.md` and fill in each placeholder.

---

## Template

````markdown
---
# IDENTITY — How the agent appears and when it triggers
name: {agent-name}
description: "{What it does in one sentence}. Use when {specific trigger phrases}."

# TOOLS — What the agent can use
# Core tools: Read, Write, Edit, Bash, Grep, Glob, Agent
# Uncomment disallowedTools to make the agent read-only
tools: [{tool-list}]
# disallowedTools: [Agent, ExitPlanMode, Edit, Write, NotebookEdit]

# EXECUTION LIMITS — How long the agent runs
# 6-8 for analysis, 10-15 for implementation, 20-25 for complex multi-step work
maxTurns: {10-25}

# MODEL — Which model powers this agent
# Options: haiku (fast/cheap), sonnet (balanced), opus (complex reasoning)
model: sonnet

# OPTIONAL FIELDS — Uncomment as needed:

# permissionMode: acceptEdits       # Auto-approve file edits (skip confirmation prompts)
# isolation: worktree               # Run in a git worktree (safe branch isolation)
# background: true                  # Run as a background task (non-blocking)
# memory: project                   # Persist memory across sessions for this project
# skills: skill-1, skill-2         # Load additional skills into this agent
# mcpServers:                       # Connect to MCP servers for external tool access
#   - server-name
---

# {Agent Name}

<!-- PURPOSE: One-line statement explaining what this agent does and why it exists.
     This is the agent's north star — every decision should trace back to this. -->
{One-line purpose statement explaining what this agent does and why it exists.}

## Constraints

<!-- CONSTRAINTS: Explicit boundaries prevent the agent from going off-track.
     Be specific. Vague constraints like "be careful" are useless.
     Good constraints name exact files, directories, or operations. -->
- {What the agent must NOT do — be explicit about forbidden actions}
- {Files or directories it must NOT touch — use exact paths}
- {Operations that require escalation to the user instead of autonomous action}
- Do not modify files outside the scope of the assigned task
- If uncertain about a change, stop and ask the user rather than guessing

## Workflow

<!-- WORKFLOW: The step-by-step process the agent follows.
     Every agent should have a discovery phase before an action phase.
     Read-only agents skip step 3. All agents need verification. -->
1. **Discovery** — {Read and search phase: what to look for and where}
2. **Analysis** — {Understand what you found: patterns, dependencies, risks}
3. **Action** — {Make changes: what to create, modify, or delete. Remove for read-only agents.}
4. **Verification** — {Check your work: run tests, validate output, confirm constraints}

## Output Contract

<!-- OUTPUT CONTRACT: What the agent must produce before completing.
     Structured output makes agents composable — other agents or scripts
     can parse the results. Be specific about required fields. -->
Produce a structured report with:
- **Summary**: {One-paragraph description of what was done}
- **Changes**: {List of files created, modified, or analyzed}
- **Findings**: {Key observations, issues found, or decisions made}
- **Verification**: {Evidence that the work is correct — test results, checks passed}

## Self-Verification

<!-- SELF-VERIFICATION: Checks the agent runs before declaring completion.
     These prevent premature completion and catch common mistakes.
     Each check should be concrete and testable. -->
Before completing:
- [ ] {All constraints were respected — no forbidden files touched, no unauthorized operations}
- [ ] {Output contract is fully satisfied — all required fields present}
- [ ] {Verification step passed — tests green, no regressions, output valid}
- [ ] {No unfinished work — if something could not be completed, it is documented}
````

---

## Customization Guide

### Making It Read-Only

Add `disallowedTools` and remove write tools:

```yaml
tools: [Read, Grep, Glob, Bash]
disallowedTools: [Agent, ExitPlanMode, Edit, Write, NotebookEdit]
```

Add to the system prompt: "You are STRICTLY PROHIBITED from creating or modifying any files."

### Adding Background Execution

```yaml
background: true
maxTurns: 15
```

Background agents run without blocking the main conversation. Use for long-running tasks like test suites or large searches.

### Adding Git Isolation

```yaml
isolation: worktree
```

The agent runs in a separate git worktree. Changes are on a branch and do not affect your working directory until you merge.

### Connecting External Tools via MCP

```yaml
mcpServers:
  - postgres-server
  - github-server
```

MCP servers give the agent access to databases, APIs, and other external systems.
