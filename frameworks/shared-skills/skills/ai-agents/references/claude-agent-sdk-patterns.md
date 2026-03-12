# Claude Agent SDK — Production Patterns

**Version**: Python v0.1.47, TypeScript v0.2.69 (March 2026) | First release: Sep 2025 | Formerly "Claude Code SDK"

**What**: Official Anthropic agent SDK. Functional API (not class-based) — agents defined via `query()` with options. Custom tools are in-process MCP servers. Deep MCP integration, Computer Use, built-in tools (Bash, Read, Write, Edit, Grep, Glob), 18-event hook system for guardrails. Powers Claude Code. 1.85M+ weekly npm downloads.

**When to choose**: Building on Anthropic models, need Computer Use / desktop automation, want built-in coding tools, need fine-grained permission hooks, TypeScript or Python teams.

---

## Table of Contents

1. [Agent Definition](#agent-definition)
2. [Built-in Tools](#built-in-tools)
3. [Custom Tools](#custom-tools)
4. [MCP Integration](#mcp-integration)
5. [Multi-Agent (Subagents)](#multi-agent-subagents)
6. [Guardrails (Hooks & Permissions)](#guardrails-hooks--permissions)
7. [Streaming & Events](#streaming--events)
8. [Computer Use](#computer-use)
9. [Python vs TypeScript](#python-vs-typescript)
10. [Testing](#testing)
11. [Model Support](#model-support)

---

## Agent Definition

No `Agent` class. Agents are defined functionally via `query()` with an options object.

**Python**:

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant.",
    model="sonnet",
    allowed_tools=["Read", "Grep", "Glob", "mcp__my-server__*"],
    max_turns=20,
    max_budget_usd=1.0,
    effort="high",  # "low" | "medium" | "high" | "max"
)

async for message in query(prompt="Analyze this codebase", options=options):
    print(message)
```

**TypeScript**:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const q = query({
  prompt: "Analyze this codebase",
  options: {
    systemPrompt: "You are a helpful assistant.",
    model: "sonnet",
    allowedTools: ["Read", "Grep", "Glob"],
    maxTurns: 20,
    maxBudgetUsd: 1.0,
  },
});

for await (const message of q) {
  console.log(message);
}
```

**Multi-turn conversations** (Python): Use `ClaudeSDKClient` for stateful sessions:

```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient(options=options) as client:
    await client.connect()
    response = await client.query("First question")
    response = await client.query("Follow-up question")
```

**Auth**: `ANTHROPIC_API_KEY` env var. Also supports Bedrock (`CLAUDE_CODE_USE_BEDROCK=1`), Vertex AI (`CLAUDE_CODE_USE_VERTEX=1`), Azure (`CLAUDE_CODE_USE_FOUNDRY=1`).

---

## Built-in Tools

These tools are provided by the SDK — no implementation needed:

| Tool | Purpose |
|------|---------|
| `Read` | Read files from filesystem |
| `Write` | Create new files |
| `Edit` | Precise string replacements in files |
| `Bash` | Execute terminal commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents (ripgrep-based) |
| `WebSearch` | Web search |
| `WebFetch` | Fetch and parse web pages |
| `Task` | Invoke subagents |
| `AskUserQuestion` | Ask clarifying questions |

Control access via `allowed_tools` / `disallowed_tools`. `disallowed_tools` overrides everything including `bypassPermissions`.

---

## Custom Tools

Custom tools are defined as **in-process MCP servers** using `tool()` and `create_sdk_mcp_server()`.

**Python**:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("lookup_customer", "Look up customer by ID", {"customer_id": str})
async def lookup_customer(args: dict[str, Any]) -> dict[str, Any]:
    customer = await db.get(args["customer_id"])
    return {"content": [{"type": "text", "text": json.dumps(customer)}]}

server = create_sdk_mcp_server(
    name="my-tools", version="1.0.0", tools=[lookup_customer]
)

# Pass as MCP server in options
options = ClaudeAgentOptions(mcp_servers={"my-tools": server})
```

**TypeScript** (uses Zod for schemas):

```typescript
import { tool, z, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";

const lookupCustomer = tool(
  "lookup_customer",
  "Look up customer by ID",
  { customer_id: z.string() },
  async (args) => ({
    content: [{ type: "text", text: JSON.stringify(await db.get(args.customer_id)) }],
  })
);

const server = createSdkMcpServer({
  name: "my-tools",
  version: "1.0.0",
  tools: [lookupCustomer],
});
```

Tool names follow MCP convention: `mcp__<server-name>__<tool-name>`.

**Tool annotations**: `readOnlyHint`, `destructiveHint`, `openWorldHint` for permission hints.

---

## MCP Integration

**Four transport types**:

```python
mcp_servers = {
    # stdio — local subprocess
    "github": {"command": "npx", "args": ["@modelcontextprotocol/server-github"]},
    # SSE — remote server
    "remote": {"type": "sse", "url": "https://mcp.example.com/sse"},
    # HTTP — standard HTTP
    "api": {"type": "http", "url": "https://mcp.example.com/mcp"},
    # SDK — in-process (custom tools)
    "my-tools": server,  # from create_sdk_mcp_server()
}
```

**Tool wildcards**: `mcp__github__*` allows all tools from a server.

**Tool search**: Auto-activates when MCP tool definitions exceed 10% of context window. Requires Sonnet 4+ or Opus 4+.

**Config file**: Also loadable from `.mcp.json`.

---

## Multi-Agent (Subagents)

Subagents are defined via `AgentDefinition` objects:

```python
from claude_agent_sdk import AgentDefinition

agents = [
    AgentDefinition(
        description="Use for code review tasks",
        prompt="You are an expert code reviewer. Focus on bugs and security.",
        tools=["Read", "Grep", "Glob"],
        model="sonnet",
        max_turns=10,
    ),
    AgentDefinition(
        description="Use for writing tests",
        prompt="You are a test engineer. Write comprehensive tests.",
        tools=["Read", "Write", "Edit", "Bash"],
        model="sonnet",
    ),
]

options = ClaudeAgentOptions(
    allowed_tools=["Task"],  # Parent must include Task
    agents=agents,
)
```

**Key constraints**:

- Parent must include `"Task"` in `allowedTools`
- **Subagents cannot spawn sub-subagents** (no `Task` in subagent tools)
- Multiple subagents can run in parallel
- Subagents can be resumed via session ID + agent ID
- Dynamic agent factories supported (create definitions at runtime)

**Three creation methods**: programmatic `AgentDefinition` (recommended), filesystem (`.claude/agents/*.md`), or built-in `general-purpose`.

---

## Guardrails (Hooks & Permissions)

**Hooks** intercept agent events at every lifecycle point.

**Key hook events**:

| Event | When | Can Do |
|-------|------|--------|
| `PreToolUse` | Before tool execution | Allow, deny, modify input |
| `PostToolUse` | After tool execution | Add context, log |
| `PostToolUseFailure` | Tool failed | Error handling |
| `PermissionRequest` | Permission needed | Approve/deny/ask |
| `SubagentStart/Stop` | Subagent lifecycle | Control delegation |
| `Notification` | Agent notifications | Logging, alerts |
| `Stop` | Agent stopping | Cleanup |

**PreToolUse permission decisions**:

- `"allow"` — approve execution
- `"deny"` — block execution
- `"ask"` — prompt user for decision
- `updatedInput` — modify tool input (requires `"allow"`)
- Priority: deny > ask > allow

**Python example**:

```python
from claude_agent_sdk import HookMatcher

async def block_writes(input_data, tool_use_id, context):
    if "/production/" in str(input_data.get("file_path", "")):
        return {"permissionDecision": "deny", "reason": "Cannot write to production"}
    return {"permissionDecision": "allow"}

options = ClaudeAgentOptions(
    hooks=[HookMatcher(matcher="Write|Edit", hooks=[block_writes])],
)
```

**Permission modes**: `"default"`, `"acceptEdits"`, `"plan"` (no execution), `"bypassPermissions"`, `"dontAsk"` (TS only).

**`can_use_tool`** — custom permission callback for fine-grained per-tool control.

---

## Streaming & Events

**Default**: Yields complete `AssistantMessage` objects after each turn.

**Streaming mode**: Set `include_partial_messages=True` for real-time token streaming.

**Message types**:

| Type | Content |
|------|---------|
| `system` (init) | Session initialization, available tools, model |
| `assistant` | Claude's responses with content blocks |
| `result` | Final result: `duration_ms`, `total_cost_usd`, `usage`, `structured_output` |
| `stream_event` | Raw token-by-token streaming events |

**Result message fields**: `is_error`, `num_turns`, `total_cost_usd`, `usage`, `structured_output`.

**Note**: Streaming is incompatible with explicit `max_thinking_tokens` and structured output.

---

## Computer Use

Computer Use is available through the Claude API's `computer_20251124` tool (Opus 4.6, Sonnet 4.6, Opus 4.5). In the Agent SDK context, browser/screen automation is typically achieved via MCP:

```python
mcp_servers = {
    "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]},
}
```

The SDK supports `sandbox` / `SandboxSettings` for containerized execution when using Computer Use.

**Important**: Computer Use requires a sandboxed environment. Never use in production without proper containment.

---

## Python vs TypeScript

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Package | `claude-agent-sdk` | `@anthropic-ai/claude-agent-sdk` |
| Entry points | `query()` + `ClaudeSDKClient` | `query()` (returns `Query` object) |
| Multi-turn | `ClaudeSDKClient` context manager | `Query.streamInput()` or V2 `send()`/`stream()` |
| Tool schemas | Python types or JSON Schema dicts | Zod schemas |
| Hook events | 12 events | 18 events (6 TS-only) |
| Naming | `snake_case` | `camelCase` |

**TS-only hooks**: `SessionStart`, `SessionEnd`, `Setup`, `TeammateIdle`, `TaskCompleted`, `ConfigChange`.

---

## Testing

No built-in test framework. Recommended approaches:

- **Promptfoo**: Declarative YAML-based evaluation. Supports Claude Agent SDK as a provider. Assertion types from string matching to LLM-as-judge.
- **Hooks for testing**: Use `PreToolUse`/`PostToolUse` hooks to log, validate, or mock tool calls.
- **Result inspection**: Check `ResultMessage` fields: `is_error`, `num_turns`, `total_cost_usd`, `usage`.
- **Permission handlers**: Custom `can_use_tool` to sandbox or redirect operations in tests.

---

## Model Support

| Model | Value | Tool Search | Computer Use |
|-------|-------|-------------|--------------|
| Claude Sonnet (latest) | `"sonnet"` | Yes (4+) | `computer_20251124` (4.6) |
| Claude Opus (latest) | `"opus"` | Yes (4+) | `computer_20251124` (4.5+) |
| Claude Haiku (latest) | `"haiku"` | No | No |

Subagent models: `"sonnet"` / `"opus"` / `"haiku"` / `"inherit"` (from parent).

Third-party: Amazon Bedrock, Google Vertex AI, Microsoft Azure AI Foundry.

---

## Decision: When to Use Claude Agent SDK

**Choose Claude Agent SDK when**:

- Building on Anthropic models (Claude Sonnet/Opus/Haiku)
- Need Computer Use / desktop automation
- Want built-in coding tools (Read, Write, Edit, Bash, Grep, Glob)
- Need fine-grained permission hooks (18 lifecycle events)
- MCP-native tool ecosystem matters
- TypeScript team (more hook events, Zod schemas)

**Choose something else when**:

- Need model-agnostic framework → Pydantic AI, LangGraph
- Need visual workflow editor → LangGraph
- Need durable execution → Pydantic AI (Temporal/DBOS)
- Need A2A protocol → Pydantic AI (native `to_a2a()`)
- Non-Anthropic models required → LangGraph, Google ADK
