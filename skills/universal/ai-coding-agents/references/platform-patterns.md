# Platform Patterns for Coding Agents

Side-by-side comparison of creating coding agents on Claude Code, Codex, and Agent SDK. Same concepts, different file formats and invocation mechanisms.

---

## Table of Contents

- [Platform Comparison Table](#platform-comparison-table)
- [Claude Code .md Agents](#claude-code-md-agents)
- [Codex .toml Agents](#codex-toml-agents)
- [Agent SDK (Python)](#agent-sdk-python)
- [Agent SDK (TypeScript)](#agent-sdk-typescript)
- [Porting Between Platforms](#porting-between-platforms)
- [Multi-Agent Capabilities by Platform](#multi-agent-capabilities-by-platform)

Field names, allowed values, and precedence for each platform change between releases; check [`../../agents-subagents/references/runtime-surfaces.md`](../../agents-subagents/references/runtime-surfaces.md) before depending on a cell in this comparison.

---

## Platform Comparison Table

| Feature | Claude Code (.md) | Codex (.toml) | Agent SDK (Python/TS) |
|---------|-------------------|---------------|------------------------|
| File location (project) | `.claude/agents/*.md` | `.codex/agents/*.toml` | Source code |
| File location (personal) | `~/.claude/agents/*.md` | `~/.codex/agents/*.toml` | N/A |
| Invocation | Auto-delegated by description match | Explicit spawn by name | Programmatic call |
| System prompt | Markdown body after frontmatter | `developer_instructions` field | `ClaudeAgentOptions` / `options` |
| Tools | `tools` / `disallowedTools` arrays | Built-in sandbox tools | Custom + built-in tools |
| Multi-agent | Subagents, fork, agent teams (coordinator is a prompting pattern) | Native subagents | Full control (you build it) |
| Isolation | `isolation: worktree` | Sandbox modes | Custom (your responsibility) |
| Permission modes | `permissionMode` (values change by release; read them in the [Claude Code permission-modes docs](https://code.claude.com/docs/en/permission-modes)) | `sandbox_mode` | Hook-based permission control |
| Memory | `user` / `project` / `local` scopes | N/A | Custom persistence |
| MCP servers | `mcpServers` array in frontmatter | `[mcp_servers]` TOML section | Custom MCP client setup |
| Model override | `model` field | `model` field | Constructor parameter |
| Turn budget | `maxTurns` field | N/A (timeout-based) | Loop control in code |
| Hooks | `hooks` in frontmatter | N/A | Event handlers in code |
| Background execution | `background: true` | N/A | Async/thread control |

---

## Claude Code .md Agents

### Creation Path

1. Create the file at `.claude/agents/my-agent.md` (project) or `~/.claude/agents/my-agent.md` (personal)
2. Add YAML frontmatter with structured fields
3. Write the system prompt as the Markdown body after frontmatter
4. The agent becomes available immediately -- no restart needed

### Frontmatter Fields for Coding Agents

```yaml
---
name: code-reviewer
description: >-
  Reviews TypeScript code for security vulnerabilities, injection risks,
  and authentication bypass patterns. Use for PRs touching auth or API layers.
tools:
  - Read
  - Glob
  - Grep
  - Bash
disallowedTools:
  - Edit
  - Write
  - NotebookEdit
model: inherit
effort: medium
maxTurns: 15
---
```

### Description Writing for Coding Triggers

The `description` field determines when the agent is auto-delegated to. Be specific about the coding domain.

| Bad (too vague) | Good (specific trigger) |
|----------------|------------------------|
| "Reviews code" | "Reviews TypeScript code for security vulnerabilities, injection risks, and authentication bypass patterns" |
| "Helps with tests" | "Generates pytest unit tests for Python functions, including edge cases, mocking, and parametrized inputs" |
| "Fixes bugs" | "Diagnoses and fixes React hydration mismatches between server and client rendering" |

### Example: Complete Code Reviewer Agent

File: `.claude/agents/security-reviewer.md`

```markdown
---
name: security-reviewer
description: >-
  Reviews code changes for security vulnerabilities including SQL injection,
  XSS, CSRF, authentication bypass, insecure deserialization, and secret
  exposure. Triggered on PRs touching auth, API, or database layers.
tools:
  - Read
  - Glob
  - Grep
  - Bash
disallowedTools:
  - Edit
  - Write
  - NotebookEdit
model: inherit
effort: high
permissionMode: default
maxTurns: 12
---

You are a security code reviewer. Your role is READ-ONLY analysis.

## Task

Review the provided code changes for security vulnerabilities.

## Checklist

For each file, check:
1. SQL injection: parameterized queries only, no string concatenation
2. XSS: output encoding on all user-controlled data
3. CSRF: token validation on state-changing endpoints
4. Auth bypass: verify authentication checks on every protected route
5. Secret exposure: no hardcoded credentials, API keys, or tokens
6. Deserialization: no unsafe deserialization of user input
7. Path traversal: sanitized file paths, no user-controlled path components

## Output Format

For each finding:
- File and line number
- Vulnerability type (from checklist above)
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Evidence: the vulnerable code
- Fix: specific remediation

If no vulnerabilities found, state "No security issues identified" with a
summary of what was checked.

## Rules

- Do NOT edit any files. You are read-only.
- Do NOT explain away potential issues. Flag them for human review.
- Check ALL changed files, not just the ones that look security-relevant.
```

---

## Codex .toml Agents

### Creation Path

1. Create `.codex/agents/my-agent.toml` (project) or `~/.codex/agents/my-agent.toml` (personal)
2. Define agent fields in TOML format
3. Write developer instructions inline or reference a file
4. Agent is available via explicit spawn

### TOML Structure

```toml
name = "test-generator"
description = "Generates comprehensive test suites for Python modules"
model = "<current-codex-model>"  # resolve via the Codex model picker (developers.openai.com/codex/models); avoid pinning a snapshot
sandbox_mode = "workspace-write"

developer_instructions = """
You are a test generator for Python projects.

## Task
Given a Python module, generate a comprehensive pytest test suite.

## Process
1. Read the source module to understand all public functions and classes
2. Identify edge cases: empty inputs, None, boundary values, type errors
3. Generate parametrized tests where applicable
4. Use mocking for external dependencies (database, HTTP, filesystem)
5. Write the test file to tests/ mirroring the source path

## Output
- Test file written to the correct location
- All tests passing when run with pytest
- Coverage report showing which lines are covered

## Rules
- Use pytest, not unittest
- Use fixtures for shared setup
- Mock external dependencies, never real network or database calls
- Name test functions descriptively: test_login_with_expired_token_returns_401
"""
```

### Sandbox Mode Options for Coding Agents

| Mode | Use Case | What It Allows |
|------|----------|----------------|
| `workspace-write` | Editors, generators, fixers | Read + write to workspace files |
| `read-only` | Reviewers, analyzers | Read only, no file modifications |
| `danger-full-access` | Only inside an external sandbox | No filesystem or network restriction |

Network access is not a sandbox mode. Inside `workspace-write` it is the `[sandbox_workspace_write] network_access` boolean (checked 2026-10-10 against the Codex config reference, https://learn.chatgpt.com/docs/config-file/config-reference).

### Example: Codex Test Generator

```toml
name = "test-generator"
description = "Generates pytest test suites with edge cases and mocking"
model = "<current-codex-model>"  # resolve via the Codex model picker (developers.openai.com/codex/models); avoid pinning a snapshot
sandbox_mode = "workspace-write"

[mcp_servers.coverage]
command = "coverage-mcp-server"
args = ["--format", "json"]

developer_instructions = """
Generate comprehensive pytest tests for the specified Python module.

Steps:
1. Read the target module
2. List all public functions and classes
3. For each function: happy path + 3 edge cases + error cases
4. Use @pytest.mark.parametrize for multiple inputs
5. Mock all external calls (requests, database, file I/O)
6. Write test file to tests/{module_path}/test_{module_name}.py
7. Run pytest on the new file
8. If failures, fix and re-run (max 2 attempts)
9. Run coverage and report uncovered lines
"""
```

---

## Agent SDK (Python)

Checked 2026-10-10 against https://code.claude.com/docs/en/agent-sdk/python and https://code.claude.com/docs/en/agent-sdk/hooks. Re-check the page before relying on a signature; the SDK changes between releases. The snippets below were not executed.

### query() with ClaudeAgentOptions

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

options = ClaudeAgentOptions(
    model=DEFAULT_CODING_MODEL,  # resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
    system_prompt="You are a code reviewer. Analyze the diff for correctness, security, and maintainability.",
    allowed_tools=["Read", "Glob", "Grep"],
    max_turns=15,
)

async def main():
    async for message in query(prompt="Review the changes in this PR: ...", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(message.subtype, message.num_turns)

asyncio.run(main())
```

`allowed_tools` pre-approves tools; it does not restrict the set. Use `ClaudeSDKClient` (`async with ClaudeSDKClient(options=options) as client`, then `client.query(...)` and `client.receive_response()`) for multi-turn sessions, and let its message loop finish rather than `break`.

### Custom Tools in an In-Process MCP Server

```python
import subprocess
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("run_tests", "Run pytest for a module path", {"module_path": str})
async def run_tests(args):
    r = subprocess.run(["pytest", "-v", "--tb=short", args["module_path"]],
                       capture_output=True, text=True, timeout=120)
    return {"content": [{"type": "text", "text": f"Exit code: {r.returncode}\n{r.stdout}{r.stderr}"}]}

server = create_sdk_mcp_server(name="project-tools", tools=[run_tests])
options = ClaudeAgentOptions(
    mcp_servers={"project": server},
    allowed_tools=["mcp__project__run_tests"],  # mcp__<server key>__<tool name>
)
```

### Hook to Block Protected Paths

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def block_protected_writes(input_data, tool_use_id, context):
    path = input_data["tool_input"].get("file_path", "")
    if any(p in path for p in (".env", "credentials.json", "secrets/")):
        return {"hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],
            "permissionDecision": "deny",
            "permissionDecisionReason": "Protected path",
        }}
    return {}  # empty object allows the call

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[block_protected_writes])]}
)
```

Matchers match tool names, not paths; filter paths inside the callback. A single `deny` from any hook blocks the call.

---

## Agent SDK (TypeScript)

Checked 2026-10-10 against https://code.claude.com/docs/en/agent-sdk/typescript and the hooks page above. The snippet was not executed.

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { execFileSync } from "child_process";

const lint = tool(
  "lint_file",
  "Run ESLint on a file and return findings",
  { filePath: z.string() },
  async ({ filePath }) => {
    const out = execFileSync("npx", ["eslint", "--format", "json", filePath], {
      encoding: "utf-8",
      timeout: 30000,
    });
    return { content: [{ type: "text", text: out }] };
  },
);

const server = createSdkMcpServer({ name: "project", tools: [lint] });

for await (const message of query({
  prompt: "Review the auth module",
  options: {
    model: DEFAULT_CODING_MODEL, // resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
    systemPrompt: "You are a code reviewer.",
    allowedTools: ["Read", "Glob", "Grep", "mcp__project__lint_file"],
    maxTurns: 15,
    mcpServers: { project: server }, // a record keyed by server name, not an array
  },
})) {
  if (message.type === "result") console.log(message);
}
```

Hooks use the same shape as Python: `hooks: { PreToolUse: [{ matcher: "Write|Edit", hooks: [cb] }] }`, with `cb` returning `{ hookSpecificOutput: { hookEventName, permissionDecision: "deny", permissionDecisionReason } }` to block. Look up the `HookCallback` type in the TypeScript reference before writing one.

---

## Porting Between Platforms

### Mapping Table for Common Fields

| Concept | Claude Code (.md) | Codex (.toml) | Agent SDK |
|---------|-------------------|---------------|-----------|
| Agent name | `name` field | `name` field | variable name |
| Trigger description | `description` | `description` | Routing logic in code |
| System prompt | Markdown body | `developer_instructions` | `system_prompt` / `systemPrompt` |
| Allowed tools | `tools: [...]` | Built-in by sandbox_mode | `tools: [...]` |
| Blocked tools | `disallowedTools: [...]` | Implicit by sandbox_mode | Hook-based blocking |
| Model | `model` | `model` | Constructor param |
| Turn limit | `maxTurns` | N/A | Loop control |
| File isolation | `isolation: worktree` | Sandbox | Custom worktree logic |
| MCP servers | `mcpServers: [...]` | `[mcp_servers]` | `mcpServers` array |
| Permission level | `permissionMode` | `sandbox_mode` | Hook returns |

### What Changes When Porting

- **File format**: YAML frontmatter + Markdown vs TOML vs code
- **Invocation mechanism**: Auto-delegation vs explicit spawn vs programmatic call
- **Tool access model**: Allowlist/denylist vs sandbox modes vs hook-based filtering
- **Multi-agent coordination**: Built-in patterns vs limited vs custom

### What Stays the Same

- **System prompt logic**: The core instructions transfer directly
- **Tool concepts**: Read, Write, Edit, Bash, Glob, Grep exist on all platforms
- **Verification approach**: "Run tests, check output, report findings" is universal
- **Structured output contracts**: Define expected output format in the prompt
- **Constraint patterns**: "Do NOT modify files outside [list]" works everywhere

---

## Multi-Agent Capabilities by Platform

### Claude Code

All three patterns are native and built into the platform:

| Pattern | Support | Mechanism |
|---------|---------|-----------|
| Coordinator-Led | Native | Agent tool with `subagent_type`, worker prompts, notifications |
| Fork Subagent | Native | Agent tool with subagent type `fork`, inherits parent context (no type gives general-purpose) |
| Agent Teams | Native | Named agents, mailbox communication, shared checkout with owned files |

Key advantages: prompt cache sharing for forks, built-in mailbox protocol, worktree isolation for subagents and background sessions (teammates share the lead's checkout), permission bridge for teammates.

### Codex

Codex has native subagents: built-in `default`, `worker` and `explorer` agents, custom agents in `.codex/agents/*.toml` (required fields `name`, `description`, `developer_instructions`), and an `[agents]` config table for limits (checked 2026-10-10 against https://learn.chatgpt.com/docs/agent-configuration/subagents). Codex spawns by explicit request, not description match, and the topology is hub-and-spoke. Sandbox modes give strong isolation. For current keys and limits, read [`../../agents-subagents/references/runtime-surfaces.md`](../../agents-subagents/references/runtime-surfaces.md).

### Agent SDK

Full control -- you build the coordination layer:

| Pattern | Support | Mechanism |
|---------|---------|-----------|
| Any pattern | Custom | You implement coordination in code |
| Tool sharing | Custom | Pass tools to agent constructors |
| Communication | Custom | Shared state, queues, files -- your choice |
| Isolation | Custom | Threads, processes, containers -- your choice |

Agent SDK is best when you need custom orchestration logic that does not fit the built-in patterns. The tradeoff is implementation effort.

### Platform Selection Guide

| Scenario | Best Platform | Reason |
|----------|---------------|--------|
| Developer tool in a repo | Claude Code | Zero-config, auto-delegation |
| CI/CD pipeline agent | Codex | Strong sandbox, deterministic |
| Custom product with agents | Agent SDK | Full control, embeddable |
| Multi-agent coding team | Claude Code | Native subagent and agent-team support |
| Rapid prototyping | Claude Code | Markdown file, instant availability |
| Production SaaS feature | Agent SDK | Custom UX, error handling, billing |
| Non-coding domain agent | Claude Code | Skill system generalizes beyond code (see below) |

### Non-Coding Domain Applications

Claude Code's skill/agent infrastructure is not limited to coding tasks. The same patterns — skills, parallel subagents, structured evaluation, pipeline state — transfer to any domain with structured workflows.

**Example:** a community job-search project (career-ops) runs a complete pipeline on Claude Code skill modes: portal scanning, structured job evaluation, CV generation, and application tracking. Treat it as an illustration, not a benchmark; popularity figures are unsourced and omitted.

**What transfers directly:**
- Skill decomposition (14 domain-specific modes vs. coding review/implement/test modes)
- Parallel subagent execution (batch-process 10+ job offers like batch-processing 10+ files)
- Structured evaluation with scoring rubrics
- Human-in-the-loop for high-stakes actions (apply vs. merge)

**What does not transfer:**
- Code-specific tools (Edit, Write, Bash) — domain agents need custom MCP tools or web scrapers
- Test-based verification — domain agents need domain-specific quality gates
