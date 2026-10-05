# Claude Agent SDK — Production Patterns

**Version**: check `pip index versions claude-agent-sdk` / `npm view @anthropic-ai/claude-agent-sdk version` and the SDK reference before relying on an API shape below; the SDK changes quickly. Formerly "Claude Code SDK"

**What**: Official Anthropic agent SDK. Functional API (not class-based) — agents defined via `query()` with options. Custom tools are in-process MCP servers. Deep MCP integration, Computer Use, built-in tools (Bash, Read, Write, Edit, Grep, Glob), a multi-event hook system for guardrails. Powers Claude Code.

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
12. [Managed Agents (hosted harness)](#managed-agents-hosted-harness)

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

**Multi-turn conversations** (Python): Use `ClaudeSDKClient` for stateful sessions. `query()` sends and returns `None`; responses come from the separate `receive_response()` async iterator — it does not return the response directly, and `connect()` inside `async with` is redundant (the context manager already connects):

```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient(options=options) as client:
    await client.query("First question")
    async for message in client.receive_response():
        print(message)

    await client.query("Follow-up question")
    async for message in client.receive_response():
        print(message)
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
| `Agent` | Invoke subagents (current built-in name is `Agent`; older docs and code call it `Task`) |
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
    # SSE — legacy remote servers only (no longer a standard MCP transport)
    "remote": {"type": "sse", "url": "https://mcp.example.com/sse"},
    # HTTP — Streamable HTTP; the default for remote servers ("streamable-http" is a JSON-config alias)
    "api": {"type": "http", "url": "https://mcp.example.com/mcp"},
    # SDK — in-process (custom tools)
    "my-tools": server,  # from create_sdk_mcp_server()
}
```

**Tool wildcards**: `mcp__github__*` allows all tools from a server.

**Tool search**: on by default in current SDK releases; tool definitions are withheld and loaded on demand (up to five per search). `ENABLE_TOOL_SEARCH=auto` switches to the threshold rule (activate when deferrable definitions reach 10% of the context window; `auto:N` for another percentage); `false` loads everything upfront. Requires the Claude 4.5 generation or later (Sonnet 4.5, Haiku 4.5, Opus 4.5) and is forced off on Azure-hosted Foundry deployments and non-first-party `ANTHROPIC_BASE_URL` proxies. With under ~10 tools, upfront loading is usually faster. Source: <https://code.claude.com/docs/en/agent-sdk/tool-search>.

**Config file**: Also loadable from `.mcp.json`.

---

## Multi-Agent (Subagents)

Subagents are defined via `AgentDefinition` objects, keyed by agent name — `agents` is a `dict[str, AgentDefinition]`, not a list. `AgentDefinition` takes `maxTurns` (camelCase, matching the SDK's own field name — not the snake_case `max_turns`; passing `max_turns` raises a `TypeError`):

```python
from claude_agent_sdk import AgentDefinition

agents = {
    "code-reviewer": AgentDefinition(
        description="Use for code review tasks",
        prompt="You are an expert code reviewer. Focus on bugs and security.",
        tools=["Read", "Grep", "Glob"],
        model="sonnet",
        maxTurns=10,
    ),
    "test-writer": AgentDefinition(
        description="Use for writing tests",
        prompt="You are a test engineer. Write comprehensive tests.",
        tools=["Read", "Write", "Edit", "Bash"],
        model="sonnet",
    ),
}

options = ClaudeAgentOptions(
    allowed_tools=["Agent"],  # Parent must include the Agent tool
    agents=agents,
)
```

**Key constraints**:

- Parent must include `"Agent"` in `allowedTools`
- **Subagents can nest**: a subagent with `"Agent"` in its own `tools` can spawn further subagents, up to the runtime's spawn-depth limit (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`; check the Claude Code docs for the current default) — do not assume a hard one-level-deep restriction
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

**Python example**: `hooks` is a `dict[HookEvent, list[HookMatcher]]` keyed by event name, not a bare list of matchers:

```python
from claude_agent_sdk import HookMatcher

async def block_writes(input_data, tool_use_id, context):
    if "/production/" in str(input_data.get("file_path", "")):
        return {"permissionDecision": "deny", "reason": "Cannot write to production"}
    return {"permissionDecision": "allow"}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[block_writes])]},
)
```

**Permission modes**: `"default"`, `"acceptEdits"`, `"plan"` (no execution), `"bypassPermissions"`, `"auto"`, `"dontAsk"`. `"auto"` is a distinct mode from `"bypassPermissions"`. `"dontAsk"` is available from Python too, not TS-only. Check the SDK reference for the current list.

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

Computer Use is available through a Claude API computer-use tool. The tool version string and the specific models it supports change as models are released — verify the current tool name and supported-model list at the Claude API docs before citing either; do not trust a pinned tool-version/model list here. In the Agent SDK context, browser/screen automation is typically achieved via MCP:

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
| Hook events | A subset | Every event; many are TS-only |
| Naming | `snake_case` | `camelCase` |

**Hook coverage**: the Python SDK supports fewer hook events than TypeScript, and the set grows between releases. Check the per-SDK columns of the "Available hooks" table at <https://code.claude.com/docs/en/agent-sdk/hooks> before designing around one (for example, `SessionStart` and `PostCompact` are TypeScript-only).

---

## Testing

No built-in test framework. Recommended approaches:

- **Promptfoo**: Declarative YAML-based evaluation. Supports Claude Agent SDK as a provider. Assertion types from string matching to LLM-as-judge.
- **Hooks for testing**: Use `PreToolUse`/`PostToolUse` hooks to log, validate, or mock tool calls.
- **Result inspection**: Check `ResultMessage` fields: `is_error`, `num_turns`, `total_cost_usd`, `usage`.
- **Permission handlers**: Custom `can_use_tool` to sandbox or redirect operations in tests.

---

## Model Support

| Alias | Resolves to | Tool search |
|-------|-------------|-------------|
| `"sonnet"` | current Sonnet | Sonnet 4.5 and later |
| `"opus"` | current Opus | Opus 4.5 and later |
| `"haiku"` | current Haiku | Haiku 4.5 and later |

Aliases float: pin a full model id in production if a silent model change would invalidate your evals. Check the current alias targets and the tool-search compatibility list in the Claude platform docs before quoting them.

Computer Use tool versions and supported models: see the Computer Use paragraph above; look them up in the Claude API docs, not here.

Subagent models: `"sonnet"` / `"opus"` / `"haiku"` / `"inherit"` (from parent).

Third-party: Amazon Bedrock, Google Vertex AI, Microsoft Azure AI Foundry.

---

## Managed Agents (hosted harness)

Claude Managed Agents is Anthropic's hosted alternative to self-hosting the Agent SDK's loop: instead of running `query()`/`ClaudeSDKClient` in your own process, you run the agent in an Anthropic-managed sandbox and billing session (see the Managed Agents overview in the Claude platform docs and confirm its availability status before committing to it).

- Session-time billing accrues **only while a session is `running`**; idle time does not count. Check the current rate on the pricing page; the architectural point is the running-vs-idle distinction, not a number.
- The corresponding footgun is a session left in `running` state (e.g. forgetting to close it) rather than a forgotten idle session — idle does not bill.
- **Choose Managed Agents over the self-hosted SDK** when you want Anthropic to own sandboxing and session lifecycle and don't need custom infra (your own compute, custom sandboxing, or a non-Anthropic model in the same loop).
- **Choose the self-hosted SDK** when you need Bedrock/Vertex/Azure auth paths, custom sandbox tooling, or tight control over the process hosting the agent loop.

---

## Decision: When to Use Claude Agent SDK

**Choose Claude Agent SDK when**:

- Building on Anthropic models (Claude Sonnet/Opus/Haiku)
- Need Computer Use / desktop automation
- Want built-in coding tools (Read, Write, Edit, Bash, Grep, Glob)
- Need fine-grained permission hooks (30+ lifecycle events in TypeScript, a smaller subset in Python; count them in the hooks table, not from memory)
- MCP-native tool ecosystem matters
- TypeScript team (more hook events, Zod schemas)

**Choose something else when**:

- Need model-agnostic framework → Pydantic AI, LangGraph
- Need visual workflow editor → LangGraph
- Need durable execution → Pydantic AI (Temporal/DBOS)
- Need A2A protocol → Pydantic AI (native `to_a2a()`)
- Non-Anthropic models required → LangGraph, Google ADK
