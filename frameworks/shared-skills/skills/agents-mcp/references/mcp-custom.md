# Building Custom MCP Servers

Create custom MCP servers to connect Claude Code to proprietary systems, internal APIs, or specialized tools.

## Contents

- Quick Start
- Server Types
- Python Server
- Configuration in Claude Code
- Project Structure
- Best Practices
- Security
- Testing
- Deployment
- Related

---

## Quick Start

### TypeScript Server (Recommended)

```bash
# Create project
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk

# Create server
touch src/index.ts
```

### Minimal Server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "my-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// Define a tool
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "hello",
      description: "Say hello",
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string", description: "Name to greet" }
        },
        required: ["name"]
      }
    }
  ]
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "hello") {
    const person = (args as { name?: string } | undefined)?.name ?? "world";
    return { content: [{ type: "text", text: `Hello, ${person}!` }] };
  }
  throw new Error(`Unknown tool: ${name}`);
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## Server Types

### Tool Server

Provides callable functions for Claude:

```typescript
import { ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "query_database",
      description: "Query the internal database",
      inputSchema: {
        type: "object",
        properties: {
          sql: { type: "string", description: "SQL query" }
        },
        required: ["sql"]
      }
    }
  ]
}));
```

### Resource Server

Provides data that Claude can read:

```typescript
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "internal://docs/api",
      name: "API Documentation",
      mimeType: "text/markdown"
    }
  ]
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  if (request.params.uri === "internal://docs/api") {
    return {
      contents: [{
        uri: request.params.uri,
        mimeType: "text/markdown",
        text: "# API Docs\n...",
      }]
    };
  }

  throw new Error(`Unknown resource: ${request.params.uri}`);
});
```

### Prompt Server

Provides reusable prompt templates:

```typescript
server.setRequestHandler("prompts/list", async () => ({
  prompts: [
    {
      name: "code_review",
      description: "Review code for issues",
      arguments: [
        { name: "code", description: "Code to review", required: true }
      ]
    }
  ]
}));
```

---

## Python Server

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

server = Server("my-python-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="calculate",
            description="Perform calculation",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "calculate":
        result = eval(arguments["expression"])  # Use safer eval in production
        return [types.TextContent(type="text", text=str(result))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Configuration in Claude Code

### Local TypeScript Server

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["tsx", "./mcp-servers/my-server/src/index.ts"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

### Local Python Server

```json
{
  "mcpServers": {
    "python-server": {
      "command": "python3",
      "args": ["-m", "my_mcp_server"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### Compiled Binary

```json
{
  "mcpServers": {
    "binary-server": {
      "command": "./bin/my-mcp-server",
      "args": ["--config", "./config.json"]
    }
  }
}
```

---

## Project Structure

```text
my-mcp-server/
  src/
    index.ts        # Entry point
    tools/          # Tool implementations
      query.ts
      transform.ts
    references/     # Resource providers
      docs.ts
    utils/          # Shared utilities
  package.json
  tsconfig.json
  README.md
```

---

## Best Practices

### Input Validation

```typescript
import { z } from "zod";
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const QuerySchema = z.object({
  sql: z.string().max(1000),
  params: z.array(z.string()).optional()
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const validated = QuerySchema.parse(request.params.arguments);
  // Safe to use validated.sql and validated.params
});
```

### Error Handling

```typescript
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await doWork(request.params);
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true
    };
  }
});
```

### Logging

```typescript
import { createLogger } from "./logger";
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const logger = createLogger("my-server");

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  logger.info("Tool called", { tool: request.params.name });
  // ...
});
```

---

## Security

```text
CUSTOM SERVER SECURITY CHECKLIST

[ ] Validate all inputs with schema
[ ] Sanitize SQL/command inputs
[ ] Use environment variables for secrets
[ ] Implement rate limiting
[ ] Log all operations for audit
[ ] Run with minimal permissions
[ ] Never expose internal errors to client
```

### Secure Environment Variables

```typescript
const apiKey = process.env.API_KEY;
if (!apiKey) {
  throw new Error("API_KEY environment variable required");
}
```

### SQL Injection Prevention

```typescript
// BAD - SQL injection risk
const query = `SELECT * FROM users WHERE id = ${userId}`;

// GOOD - Parameterized query
const query = "SELECT * FROM users WHERE id = $1";
const result = await db.query(query, [userId]);
```

---

## Testing

### Unit Tests

```typescript
import { describe, it, expect } from "vitest";
import { handleToolCall } from "./tools";

describe("hello tool", () => {
  it("greets by name", async () => {
    const result = await handleToolCall("hello", { name: "World" });
    expect(result.content[0].text).toBe("Hello, World!");
  });
});
```

### Integration Tests

```bash
# Test server manually
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | npx tsx src/index.ts
```

---

## Deployment

### As npm Package

```json
{
  "name": "@myorg/mcp-server",
  "bin": { "my-mcp-server": "./dist/index.js" },
  "files": ["dist"]
}
```

```bash
npm publish
# Users install with: npx @myorg/mcp-server
```

### As Docker Container

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist ./dist
CMD ["node", "dist/index.js"]
```

---

## Related

- [mcp-servers.md](mcp-servers.md) — Official server list
- [../SKILL.md](../SKILL.md) — Quick reference
- [MCP SDK](https://github.com/modelcontextprotocol/sdk) — Official SDK
