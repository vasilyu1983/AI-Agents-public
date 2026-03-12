# MCP Server Builder — Tooling for Agents

Use this when designing or implementing MCP servers for agent tools (Python or TypeScript SDKs).

## Planning Checklist
- Design for workflows, not raw endpoints; consolidate related actions (e.g., schedule_event that checks availability + creates event).
- Optimize for limited context: concise defaults, optional detail flags, human-readable identifiers.
- Make errors actionable: suggest next steps and correct parameters.
- Group tools with clear prefixes and natural task names.

## Research Before Coding
- Read MCP protocol spec (`modelcontextprotocol.io/llms-full.txt`).
- Load SDK docs (Python or TypeScript) and any target API docs (auth, rate limits, pagination, schemas).
- Define tool list, shared helpers (pagination, errors, formatting), and truncation strategy.

## Implementation Patterns
- Validate inputs (Pydantic v2 or Zod `.strict()`); avoid `any`.
- Async I/O; explicit return schemas; support concise vs. detailed responses.
- Annotations: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` where appropriate.
- Centralize API helpers, auth, error handling, and pagination.

## Review & Testing
- Create evaluation scenarios early; iterate based on agent feedback.
- Check character limits and truncation; handle rate limits and timeouts gracefully.
- Document tool usage, parameters, and error responses inside the server code.
