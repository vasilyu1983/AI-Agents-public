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

Use [`claude-code-agent-runtime-patterns.md`](claude-code-agent-runtime-patterns.md) for the Claude Code implementation details that sit underneath the Claude Code column in this comparison.

---

## Platform Comparison Table

| Feature | Claude Code (.md) | Codex (.toml) | Agent SDK (Python/TS) |
|---------|-------------------|---------------|------------------------|
| File location (project) | `.claude/agents/*.md` | `.codex/agents/*.toml` | Source code |
| File location (personal) | `~/.claude/agents/*.md` | `~/.codex/agents/*.toml` | N/A |
| Invocation | Auto-delegated by description match | Explicit spawn by name | Programmatic call |
| System prompt | Markdown body after frontmatter | `developer_instructions` field | `ClaudeAgentOptions` / constructor arg |
| Tools | `tools` / `disallowedTools` arrays | Built-in sandbox tools | Custom + built-in tools |
| Multi-agent | Coordinator, Fork, Teams (native) | Limited (worker agents) | Full control (you build it) |
| Isolation | `isolation: worktree` | Sandbox modes | Custom (your responsibility) |
| Permission modes | `default` / `acceptEdits` / `bypassPermissions` | `sandbox_mode` | Hook-based permission control |
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
agentType: code-reviewer
whenToUse: >-
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
permissionMode: default
maxTurns: 15
memory: project
isolation: worktree
background: false
mcpServers: []
hooks: {}
---
```

### Description Writing for Coding Triggers

The `whenToUse` field determines when the agent is auto-delegated to. Be specific about the coding domain.

| Bad (too vague) | Good (specific trigger) |
|----------------|------------------------|
| "Reviews code" | "Reviews TypeScript code for security vulnerabilities, injection risks, and authentication bypass patterns" |
| "Helps with tests" | "Generates pytest unit tests for Python functions, including edge cases, mocking, and parametrized inputs" |
| "Fixes bugs" | "Diagnoses and fixes React hydration mismatches between server and client rendering" |

### Example: Complete Code Reviewer Agent

File: `.claude/agents/security-reviewer.md`

```markdown
---
agentType: security-reviewer
whenToUse: >-
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
| `network-off` | Isolated generation | Write but no network access |
| `full` | General purpose | All capabilities |

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

### ClaudeAgentOptions Configuration

```python
from claude_agent_sdk import ClaudeAgent, ClaudeAgentOptions, tool

options = ClaudeAgentOptions(
    model=DEFAULT_CODING_MODEL,  # resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
    system_prompt="""You are a code reviewer. Analyze the provided diff
    for correctness, security, and maintainability issues.""",
    tools=["Read", "Glob", "Grep", "Bash"],
    max_turns=15,
)

agent = ClaudeAgent(options)
result = agent.run("Review the changes in this PR: ...")
```

### Custom Tool Definition

```python
from claude_agent_sdk import tool
import subprocess

@tool(description="Run ESLint on a file and return findings")
def lint_file(file_path: str) -> str:
    """Run ESLint on the specified file."""
    result = subprocess.run(
        ["npx", "eslint", "--format", "json", file_path],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout or result.stderr

@tool(description="Run the project test suite for a specific module")
def run_tests(module_path: str) -> str:
    """Run pytest for the specified module path."""
    result = subprocess.run(
        ["pytest", "-v", "--tb=short", module_path],
        capture_output=True, text=True, timeout=120
    )
    return f"Exit code: {result.returncode}\n{result.stdout}\n{result.stderr}"
```

### Hook Setup for Protected Paths

```python
from claude_agent_sdk import ClaudeAgent, Hook

def block_protected_writes(tool_name: str, tool_input: dict) -> bool:
    """Return False to block the tool call."""
    protected = [".env", "credentials.json", "secrets/", "node_modules/"]
    if tool_name in ("Edit", "Write"):
        path = tool_input.get("file_path", "")
        for p in protected:
            if p in path:
                return False
    return True

agent = ClaudeAgent(
    options=options,
    hooks={"pre_tool_use": block_protected_writes}
)
```

### Streaming Output Handling

```python
for event in agent.stream("Review the auth module for vulnerabilities"):
    if event.type == "text":
        print(event.content, end="", flush=True)
    elif event.type == "tool_use":
        print(f"\n[Using {event.tool_name}...]")
    elif event.type == "tool_result":
        pass  # Handled internally
    elif event.type == "done":
        print(f"\nCompleted in {event.turns} turns, {event.tokens} tokens")
```

### Example: SDK Code Reviewer with Custom Linter

```python
from claude_agent_sdk import ClaudeAgent, ClaudeAgentOptions, tool
import subprocess

@tool(description="Run ESLint with security rules on a TypeScript file")
def security_lint(file_path: str) -> str:
    result = subprocess.run(
        ["npx", "eslint", "--config", ".eslintrc.security.json",
         "--format", "json", file_path],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout or result.stderr

@tool(description="Check for known vulnerable dependencies")
def audit_deps() -> str:
    result = subprocess.run(
        ["npm", "audit", "--json"],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout

options = ClaudeAgentOptions(
    model=DEFAULT_CODING_MODEL,  # resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
    system_prompt="""You are a security-focused code reviewer.

    For each file in the diff:
    1. Run security_lint to check for static issues
    2. Read the file to understand context
    3. Check for OWASP Top 10 patterns manually
    4. Run audit_deps once for dependency vulnerabilities

    Report findings with severity, file, line, and remediation.""",
    tools=["Read", "Glob", "Grep", "security_lint", "audit_deps"],
    max_turns=20,
)

agent = ClaudeAgent(options)
result = agent.run("Review all changed files in the current branch vs main")
print(result.output)
```

---

## Agent SDK (TypeScript)

### Equivalent TS Patterns

```typescript
import {
  ClaudeAgent,
  ClaudeAgentOptions,
} from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const options: ClaudeAgentOptions = {
  model: DEFAULT_CODING_MODEL, // resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
  systemPrompt: `You are a code reviewer...`,
  tools: ["Read", "Glob", "Grep", "Bash"],
  maxTurns: 15,
};

const agent = new ClaudeAgent(options);
const result = await agent.run("Review the auth module");
```

### Zod Schemas for Custom Tools

```typescript
import { defineTool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { execFileSync } from "child_process";

const lintTool = defineTool({
  name: "lint_file",
  description: "Run ESLint on a TypeScript file and return findings",
  inputSchema: z.object({
    filePath: z.string().describe("Absolute path to the file to lint"),
  }),
  handler: async ({ filePath }) => {
    const output = execFileSync(
      "npx",
      ["eslint", "--format", "json", filePath],
      { encoding: "utf-8", timeout: 30000 }
    );
    return output;
  },
});

const testTool = defineTool({
  name: "run_tests",
  description: "Run Jest tests for a specific module",
  inputSchema: z.object({
    testPath: z.string().describe("Path to test file or directory"),
  }),
  handler: async ({ testPath }) => {
    try {
      const output = execFileSync(
        "npx",
        ["jest", "--verbose", testPath],
        { encoding: "utf-8", timeout: 120000 }
      );
      return output;
    } catch (e: any) {
      return `Exit code: ${e.status}\n${e.stdout}\n${e.stderr}`;
    }
  },
});
```

### createSdkMcpServer for In-Process Tools

```typescript
import { createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";

const mcpServer = createSdkMcpServer({
  name: "project-tools",
  tools: [lintTool, testTool],
});

const agent = new ClaudeAgent({
  ...options,
  mcpServers: [mcpServer],
});
```

---

## Porting Between Platforms

### Mapping Table for Common Fields

| Concept | Claude Code (.md) | Codex (.toml) | Agent SDK |
|---------|-------------------|---------------|-----------|
| Agent name | filename stem | `name` field | variable name |
| Trigger description | `whenToUse` | `description` | Routing logic in code |
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
| Fork Subagent | Native | Agent tool without `subagent_type`, inherits parent context |
| Agent Teams | Native | Named agents, mailbox communication, worktree isolation |

Key advantages: prompt cache sharing for forks, built-in mailbox protocol, worktree isolation per agent, permission bridge for teammates.

### Codex

Limited multi-agent support:

| Pattern | Support | Mechanism |
|---------|---------|-----------|
| Worker agents | Basic | Explicit agent spawning from scripts |
| Coordination | Manual | File-based communication, no built-in protocol |
| Isolation | Strong | Sandbox modes provide reliable isolation |

Codex excels at isolated single-agent tasks with strong sandboxing. Multi-agent coordination requires custom scripting.

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
| Multi-agent coding team | Claude Code | Native coordinator/teams support |
| Rapid prototyping | Claude Code | Markdown file, instant availability |
| Production SaaS feature | Agent SDK | Custom UX, error handling, billing |
| Non-coding domain agent | Claude Code | Skill system generalizes beyond code (see below) |

### Non-Coding Domain Applications

Claude Code's skill/agent infrastructure is not limited to coding tasks. The same patterns — skills, parallel subagents, structured evaluation, pipeline state — transfer to any domain with structured workflows.

**Example:** career-ops (github.com/santifer/career-ops, 59K+ stars) uses Claude Code with 14 skill modes to run a complete job-search pipeline: portal scanning across 45+ company sites, structured job evaluation (A-F grading, 10 dimensions), ATS-optimized CV generation, and application tracking via a Go terminal dashboard.

**What transfers directly:**
- Skill decomposition (14 domain-specific modes vs. coding review/implement/test modes)
- Parallel subagent execution (batch-process 10+ job offers like batch-processing 10+ files)
- Structured evaluation with scoring rubrics
- Human-in-the-loop for high-stakes actions (apply vs. merge)

**What does not transfer:**
- Code-specific tools (Edit, Write, Bash) — domain agents need custom MCP tools or web scrapers
- Test-based verification — domain agents need domain-specific quality gates
