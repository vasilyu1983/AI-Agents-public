# Production Patterns from Claude Code Source

Real patterns extracted from Claude Code source code. These are the actual architectures used in production, distilled into reusable patterns for custom coding agents.

---

## Table of Contents

- [1. The Explore Agent Pattern](#1-the-explore-agent-pattern)
- [2. The Verification Agent Pattern](#2-the-verification-agent-pattern)
- [3. The General Purpose Agent Pattern](#3-the-general-purpose-agent-pattern)
- [4. The Plan Agent Pattern](#4-the-plan-agent-pattern)
- [5. BaseAgentDefinition Type System](#5-baseagentdefinition-type-system)
- [6. Agent Loading and Parsing](#6-agent-loading-and-parsing)
- [7. Coordinator Mode Architecture](#7-coordinator-mode-architecture)
- [8. Fork Subagent Mechanics](#8-fork-subagent-mechanics)
- [9. Agent Teams Infrastructure](#9-agent-teams-infrastructure)
- [10. Distilled Lessons for Custom Coding Agents](#10-distilled-lessons-for-custom-coding-agents)

Implementation-grounded companion references:
- [`claude-code-agent-runtime-patterns.md`](claude-code-agent-runtime-patterns.md)
- [`claude-code-swarm-and-worktree-patterns.md`](claude-code-swarm-and-worktree-patterns.md)
- [`claude-code-skill-and-plugin-loading.md`](claude-code-skill-and-plugin-loading.md)

---

## 1. The Explore Agent Pattern

A read-only agent designed for codebase investigation. The strongest constraint is the clearest one.

### Read-Only Enforcement

Write tools are blocked via `disallowedTools`:

```yaml
disallowedTools:
  - Edit
  - Write
  - NotebookEdit
```

The system prompt reinforces this with unmistakable language:

```
## READ-ONLY MODE

You are in READ-ONLY mode. You MUST NOT modify any files.
Your job is to investigate and report findings.
```

Both mechanisms work together. The tool restriction is the hard guard; the prompt instruction is the behavioral guide.

### Tool Usage Pattern

The explore agent uses tools in a specific progression:

1. **Glob** for broad pattern matching: find files by name
2. **Grep** for content search: find patterns within files
3. **Read** for specific files: examine targeted sections with offset/limit
4. **Bash** restricted to read-only commands: `ls`, `git status`, `git log`, `git diff`, `find`, `cat`, `head`, `tail`

Parallel tool calls for speed -- launch multiple Grep or Glob calls in one turn when searching for different patterns.

### Thoroughness Levels

| Level | Behavior | Use When |
|-------|----------|----------|
| quick | Glob + 1-2 Grep, minimal Read | Known file, need confirmation |
| medium | Glob + multiple Grep, Read key files | Investigating a specific area |
| very thorough | Systematic Glob across all directories, comprehensive Grep, Read all relevant files | Full codebase investigation |

The thoroughness level is set in the agent prompt:

```
Thoroughness: very thorough
Search ALL directories under src/. Do not stop after finding the first match.
Check test files, configuration files, and documentation as well.
```

### Key Lesson

The strongest constraint is the clearest one. "READ-ONLY MODE" in all caps, tool restrictions, and behavioral instructions all reinforce the same boundary. Redundant constraints are intentional.

---

## 2. The Verification Agent Pattern

An adversarial agent that assumes the implementation might be wrong. Its job is to find problems, not confirm success.

### Adversarial Posture

The system prompt establishes skepticism:

```
You are a verification agent. Your job is to independently check whether
an implementation is correct.

ASSUME the implementation might be wrong. Look for:
- Off-by-one errors
- Missing edge cases
- Incorrect assumptions
- Tests that pass for the wrong reason
- Regressions in existing behavior

Do NOT explain away failures. Report what you observe.
```

### Structured Output with VERDICT

The agent must produce a structured verdict:

```
## Verification Report

VERDICT: PASS | FAIL | NEEDS-REVIEW

### Evidence
- Test suite: [command run] -> [exit code] -> [relevant output]
- Manual check: [what was verified] -> [result]
- Edge case: [scenario tested] -> [outcome]

### Issues Found
1. [File:line] Description of issue
2. [File:line] Description of issue

### Files Checked
- src/db/pool.ts (lines 40-60)
- test/db/pool.test.ts (all)
```

### Command-Run Evidence

The verifier must actually run commands, not just read test files:

```
You MUST run verification commands. Do not just read test files.

Required commands:
1. Run the test suite: npm test
2. Run specific tests related to the change
3. Run the linter: npm run lint
4. Run the type checker: npx tsc --noEmit

Report the actual output of each command.
```

### Anti-Rationalization

The critical rule that prevents confirmation bias:

```
Do NOT explain away failures.
If a test fails, report it as a failure.
If behavior seems wrong, report it as suspicious.
Do NOT assume the implementer had a good reason.
Report what you observe, not what you think should be true.
```

### Key Lesson

Verification must be independent. Fresh context, fresh agent, no knowledge of implementation choices. A verifier that knows what the implementer intended will unconsciously confirm rather than challenge.

---

## 3. The General Purpose Agent Pattern

The default agent that handles broad coding tasks before specialization.

### SHARED_PREFIX and SHARED_GUIDELINES

The agent establishes identity and behavior norms:

```
# SHARED_PREFIX
You are an agent for Claude Code, Anthropic's official CLI for Claude.
Given the user's message, you should use the tools available to complete the task.

# SHARED_GUIDELINES
- For file searches: search broadly when you don't know where something lives
- For analysis: Start broad and narrow down
- Be thorough: Check multiple locations, consider different naming conventions
- NEVER create files unless absolutely necessary
```

### Full Tool Access

```yaml
tools: ['*']  # All available tools
```

Full access is appropriate for general-purpose agents. Specialized agents restrict from this baseline.

### Description-Driven Routing

The `whenToUse` field determines when the agent is invoked:

```yaml
whenToUse: >-
  General-purpose coding agent for tasks that don't match a specialized agent.
  Handles file editing, code generation, debugging, refactoring, and
  codebase exploration when no domain-specific agent is a better fit.
```

More specific agents win over general when their `whenToUse` matches better.

### Key Lesson

Start from general, then specialize by restricting tools and adding domain-specific instructions. The general agent is the fallback; specialized agents handle known patterns.

---

## 4. The Plan Agent Pattern

Read-only exploration followed by structured plan output. Plans before executing.

### Same Constraints, Different Output Contract

The Plan agent uses the same read-only tools as the Explore agent:

```yaml
tools: [Read, Glob, Grep, Bash]
disallowedTools: [Edit, Write, NotebookEdit]
```

But the output contract is different. Instead of findings, it produces a plan:

```
## Implementation Plan

### Goal
[One sentence description of what needs to be done]

### Files to Modify
1. src/auth/login.ts (lines 23-45) - Replace session.create() with token.issue()
2. src/auth/middleware.ts (lines 12-18) - Update session validation logic
3. test/auth/login.test.ts - Add tests for token-based flow

### Files to NOT Modify
- src/auth/types.ts (shared types, no changes needed)
- src/db/ (database layer unchanged)

### Steps
1. Read current session.create() implementation in login.ts
2. Replace with token.issue() call, preserving error handling
3. Update middleware to validate tokens instead of sessions
4. Add 3 new test cases for token flow
5. Run existing test suite to verify no regressions

### Risks
- middleware.ts is imported by 12 other files; changes must be backward-compatible
- Session cleanup cron job in src/jobs/cleanup.ts may need updating

### Verification
- npm test (full suite)
- npm test -- --grep "auth" (focused)
- Manual check: token expiration behavior
```

### Key Lesson

Separate planning from execution. The plan agent explores the codebase and produces a structured plan. A separate agent (or the user) executes the plan. This prevents the "explore then forget" problem where the agent exhausts context during research and produces poor implementation.

---

## 5. BaseAgentDefinition Type System

The canonical type from Claude Code source that defines all agent configuration fields.

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `agentType` | string | Unique identifier for the agent |
| `whenToUse` | string | Description-driven trigger text. Determines when the agent is auto-delegated to. |
| `tools` | string[] | Allowlist of tools the agent can use. `['*']` means all tools. |
| `disallowedTools` | string[] | Denylist of tools to block. Subtracted from the allowlist. |
| `skills` | string[] | Preloaded skill names available to the agent. |
| `mcpServers` | object[] | Agent-specific MCP server configurations. |
| `hooks` | object | Session-scoped hooks (PreToolUse, PostToolUse, Stop). |
| `model` | string | Model override. `"inherit"` uses the parent's model. |
| `effort` | string | Reasoning effort level: `"low"`, `"medium"`, `"high"`. |
| `permissionMode` | string | `"default"` (ask), `"acceptEdits"` (auto-approve edits), `"bypassPermissions"` (no approval needed). |
| `maxTurns` | number | Maximum number of turns before the agent must stop. |
| `memory` | string | Memory scope: `"user"` (global), `"project"` (per-repo), `"local"` (per-directory). |
| `isolation` | string | Execution isolation: `"worktree"` (separate git worktree). |
| `background` | boolean | Whether the agent runs in the background. |

### Tool Filtering Logic

```
Available tools for agent = (allowlist OR all_tools) MINUS denylist

If tools = ['*']:          available = all_tools - disallowedTools
If tools = ['Read','Bash']: available = ['Read','Bash'] - disallowedTools
```

The intersection ensures agents cannot access tools that are not available in the current environment, even if listed in the allowlist.

---

## 6. Agent Loading and Parsing

### Load Order

Agents are loaded from multiple sources with defined precedence:

1. `.claude/agents/` (project-level) -- highest precedence
2. `~/.claude/agents/` (personal/user-level)
3. Managed policies (organization-level)
4. Plugins (plugin-provided agents)

Project agents take precedence over personal agents with the same `agentType`.

### Markdown Frontmatter Parsing

```markdown
---
agentType: my-agent
whenToUse: Description here
tools:
  - Read
  - Grep
maxTurns: 10
---

System prompt body goes here.
Everything after the frontmatter closing --- is the system prompt.
```

The YAML frontmatter is parsed for structured fields. The Markdown body becomes the system prompt.

### Validation

Agent definitions are validated via JSON schema (Zod in the source). Invalid fields produce warnings, not hard errors. Unknown fields are ignored for forward compatibility.

Required fields:
- `agentType` (must be a valid identifier)
- System prompt body (must not be empty)

Optional but recommended:
- `whenToUse` (without this, the agent is never auto-delegated)
- `tools` or `disallowedTools` (without these, agent gets all tools)
- `maxTurns` (without this, agent runs until it decides to stop)

---

## 7. Coordinator Mode Architecture

### Leader Orchestration

The coordinator pattern is enabled via the agent configuration. The leader orchestrates workers through the Agent tool.

### Worker Lifecycle

```
Leader dispatches worker via Agent()
  -> Worker executes independently
  -> Worker produces result
  -> Leader receives <task-notification> XML
  -> Leader processes notification
  -> Leader dispatches next worker or reports to user
```

### Notification Structure

```xml
<task-notification>
  <task-id>worker-abc-123</task-id>
  <status>completed</status>
  <summary>Fixed race condition in connection pool</summary>
  <result>
    Modified src/db/pool.ts lines 47-52.
    Wrapped acquire() body in try/finally for mutex safety.
    All 14 pool tests pass. No regressions.
  </result>
  <usage>
    <tokens>8200</tokens>
    <tool_count>6</tool_count>
  </usage>
</task-notification>
```

The leader receives: task-id (for SendMessage follow-up), status, summary, result, and usage (tokens and tool count).

### The "Never Delegate Understanding" Principle

Codified in the coordinator architecture: the leader synthesizes findings before directing the next phase. This is enforced by prompting, not by code -- the leader's system prompt requires synthesis between research and implementation phases.

```
After receiving research results:
1. State the root cause in your own words
2. List affected files with line numbers
3. Write the exact implementation spec
4. Only then dispatch the implementation worker

Forwarding raw research output to an implementer is prohibited.
```

---

## 8. Fork Subagent Mechanics

### Context Inheritance

When `subagent_type` is omitted from the Agent call, the child receives the parent's full conversation history. This includes:
- All previous messages
- All tool calls and results (replaced with placeholder text)
- The parent's system prompt

### Prompt Cache Optimization

The key efficiency feature: all fork children receive identical placeholder text for inherited tool results. Only the final directive (the fork's prompt) differs. This enables prompt cache sharing across parallel forks.

```
Fork 1: [shared_prefix][shared_history][placeholder_tools]["Search src/auth/"]
Fork 2: [shared_prefix][shared_history][placeholder_tools]["Search src/api/"]
Fork 3: [shared_prefix][shared_history][placeholder_tools]["Search src/db/"]
```

The shared prefix is cached once and reused across all three forks. Cost is approximately: 1x full context + N x incremental prompt.

### Recursive Guard (depth-5 cap, not a single-level cap)

Forks are not limited to one level anymore. The runtime's constraint since v2.1.172 is a fixed 5-level depth cap counted from the main conversation — forks count toward that cap the same as named subagents (v2.1.187), and a subagent at depth 5 loses Agent-tool access outright. This keeps resource usage bounded (exponential fan-out per level is still possible, but the levels themselves are finite) without limiting forks to a single hop. Verify the current cap against `code.claude.com/docs/en/sub-agents` before depending on the exact number — it is a runtime constant, not a config value, and constants like this are exactly what drifts fastest.

### Structured Report Enforcement

Fork output is guided by boilerplate rules in the inherited system prompt:

```
When completing your task, report with:
Scope: [one sentence]
Result: [findings]
Key files: [paths]
Files changed: [paths + commit hash, or "None"]
Issues: [if any]
```

---

## 9. Agent Teams Infrastructure

### File-Based Mailbox Protocol

Location: `~/.claude/teams/{team_name}/inboxes/{agent_name}.json`

```json
{
  "messages": [
    {
      "from": "code-searcher",
      "text": "Found 3 instances of the deprecated API in src/auth/",
      "summary": "3 deprecated API instances in auth",
      "timestamp": "2025-01-15T10:30:00Z",
      "color": "blue",
      "read": false
    }
  ]
}
```

Concurrency control: lockfile at `{inbox}.lock`. Acquire before read-modify-write. Release after write. Timeout after 5 seconds; retry once.

### Permission Bridge

Teammates run with their own permission modes. When a teammate needs approval for a tool call:

1. Teammate writes permission request to lead's inbox
2. Lead's UI displays the request
3. Lead approves or denies
4. Response written to teammate's inbox
5. Teammate proceeds or skips based on response

This enables teammates to run in `default` permission mode while the lead manages approvals.

### Worktree Isolation Per Teammate

Each teammate can operate in its own git worktree:

```
~/.claude/teams/migration/worktrees/
  auth-migrator/     # full repo copy
  api-migrator/      # full repo copy
  test-updater/      # full repo copy
```

Worktrees share the same `.git` directory but have independent working trees. This enables concurrent file edits without conflicts. Merging happens after all teammates complete.

### Shared Task List Directory

Location: `~/.claude/teams/{team_name}/tasks/`

```json
{
  "id": "task-003",
  "description": "Migrate src/api/routes.ts to v3 API",
  "owner": "api-migrator",
  "owned_files": ["src/api/routes.ts", "src/api/middleware.ts"],
  "depends_on": ["task-001"],
  "verify": "npm test -- --grep api/routes",
  "status": "pending"
}
```

Task states flow: `pending` -> `in-progress` -> `done` | `failed` | `blocked`

Dependencies (`depends_on`) prevent a task from starting until its prerequisites are `done`.

### Idle Notification via Stop Hook

When a teammate finishes all assigned tasks, the Stop hook fires and sends a notification to the lead:

```json
{
  "from": "auth-migrator",
  "text": "All assigned tasks complete. 3/3 done, 0 failed.",
  "summary": "Auth migration complete",
  "timestamp": "2025-01-15T11:45:00Z"
}
```

The lead can then reassign the idle teammate to remaining work or initiate the merge phase.

---

## 10. Distilled Lessons for Custom Coding Agents

### Start Read-Only

Begin with write tools disabled. Let the agent prove it can analyze correctly before giving it edit access. Progression:

```
Phase 1: Explore agent (read-only) -> validates understanding
Phase 2: Plan agent (read-only) -> produces implementation plan  
Phase 3: Implement agent (read+write) -> executes the plan
Phase 4: Verify agent (read-only) -> checks the implementation
```

### Bound Turns

Always set `maxTurns`. Agents without turn limits will use every turn available, even when the task was done turns ago.

| Task Type | Recommended maxTurns |
|-----------|---------------------|
| Quick search / confirmation | 5-8 |
| Code analysis / review | 8-12 |
| Single-file implementation | 10-15 |
| Multi-file implementation | 15-20 |
| Large migration | 25-35 |

### Scope MCP Servers

Only include MCP servers the agent actually needs. Every MCP server adds latency (connection setup) and token cost (tool descriptions). A code reviewer does not need a deployment MCP server.

```yaml
# Good: only what's needed
mcpServers:
  - name: eslint-server

# Bad: everything available
mcpServers:
  - name: eslint-server
  - name: deploy-server
  - name: database-server
  - name: monitoring-server
```

### Use Structured Output Contracts

Define exactly what the agent must produce. Vague instructions produce vague output.

```
# Bad: vague
"Review this code and tell me what you think."

# Good: structured contract
"Review this code and produce a report with:
1. VERDICT: PASS | FAIL | NEEDS-REVIEW
2. FINDINGS: List of issues, each with file, line, severity, description
3. RECOMMENDATIONS: Prioritized list of improvements
4. EVIDENCE: Commands run and their output"
```

### Omit Unnecessary Context

Use the explore-then-act pattern to keep context focused. An implementation agent should receive:
- The implementation spec (exact changes)
- File paths and line numbers
- Constraints (what NOT to do)
- Verification commands

It should NOT receive:
- The full exploration history
- Dead-end searches that were tried and abandoned
- Discussion about alternative approaches
- User conversation context (unless directly relevant)

### Test with Adversarial Inputs

Before deploying a coding agent, test with inputs that break assumptions:

| Input | Why It Matters |
|-------|---------------|
| Empty file (0 bytes) | Agent should handle gracefully, not hallucinate content |
| File with 5000 lines | Agent should use offset/limit, not read the whole thing |
| Binary file | Agent should detect and skip, not try to parse |
| File with unusual encoding | Agent should report the issue, not produce garbled output |
| Circular imports | Agent should detect cycles, not follow them infinitely |
| File with prompt-injection comments | Agent should treat code as data, not follow embedded instructions |
| Syntactically invalid code | Agent should report parse errors, not silently skip sections |
| File outside the repo | Agent should respect boundaries, not traverse filesystem |

### The Minimal Viable Agent

The simplest useful coding agent has:

1. A clear `whenToUse` description (one specific task)
2. A focused tool set (5-7 tools)
3. A structured output contract (exact format)
4. A turn budget (`maxTurns`)
5. A stop condition ("if stuck after 2 retries, report and stop")
6. A verification step ("run tests before reporting completion")

Start here. Add complexity only when the minimal version fails at a specific task.

```yaml
---
agentType: minimal-reviewer
whenToUse: Reviews Python functions for type annotation completeness
tools: [Read, Glob, Grep, Bash]
disallowedTools: [Edit, Write, NotebookEdit]
maxTurns: 10
---

## Task
Check all Python functions in the specified module for missing type annotations.

## Process
1. Glob for all .py files in the target directory
2. Grep for function definitions (def keyword)
3. Read each function to check parameter and return type annotations
4. Run mypy on the module for automated checking

## Output
For each function missing annotations:
- File path and line number
- Function name
- Missing annotations (parameters and/or return type)

Summary: X of Y functions fully annotated. Z functions need attention.

## Rules
- READ-ONLY. Do not modify any files.
- If a function has *args or **kwargs, check that they are annotated too.
- Report even partially annotated functions (some params typed, some not).
- If stuck after 2 search attempts, report what you found and stop.
```
