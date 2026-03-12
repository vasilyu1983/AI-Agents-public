# MCP Practical Implementation Guide

*Purpose: Hands-on patterns for building MCP servers, integrating MCP tools, and deploying Model Context Protocol in production.*

**When to use this guide**: User asks to build/integrate MCP servers, connect agents to data sources, or implement standardized tool access.

**For architecture deep-dive**: See `frameworks/shared-foundations/protocols/mcp/` for comprehensive protocol specification.

---

## Quick Decision: Do I Need MCP?

**Use MCP when**:
- Connecting agent to external data (databases, APIs, filesystems)
- Building reusable tools shared across multiple agents
- Standardizing tool access across team/organization
- Need secure, auditable tool execution

**Don't use MCP when**:
- Simple one-off script (just call API directly)
- Agent-to-agent communication (use A2A protocol instead)
- Pure LLM prompting without external tools

---

## MCP Architecture (Quick Reference)

```
┌─────────────────┐
│   MCP Host      │  (Claude Desktop, Claude Code, Custom App)
│   (AI App)      │
└────────┬────────┘
         │
┌────────┴────────┐
│   MCP Client    │  (Built into host or SDK)
└────────┬────────┘
         │
┌────────┴────────┐
│   MCP Server    │  (Your code: exposes tools/references/prompts)
└────────┬────────┘
         │
┌────────┴────────┐
│   Data Source   │  (Database, API, Filesystem, etc.)
└─────────────────┘
```

**Key concept**: MCP Server = adapter layer between AI app and your data/tools.

---

## Pattern 1: Filesystem MCP Server (Python)

**Use case**: Let agent read/write local files with permission controls.

### Setup (5 minutes)

```bash
# Install MCP SDK
uv pip install mcp

# Create server file
touch filesystem_server.py
```

### Implementation

```python
#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Filesystem Access")

@mcp.tool()
def read_file(path: str) -> str:
    """Read contents of a file from allowed directory"""
    # Security: validate path is within allowed directories
    allowed_dirs = ["/workspace", "/data"]
    abs_path = os.path.abspath(path)

    if not any(abs_path.startswith(d) for d in allowed_dirs):
        raise ValueError(f"Access denied: {path} not in allowed directories")

    with open(abs_path, 'r') as f:
        return f.read()

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file in allowed directory"""
    allowed_dirs = ["/workspace/output"]
    abs_path = os.path.abspath(path)

    if not any(abs_path.startswith(d) for d in allowed_dirs):
        raise ValueError(f"Access denied: {path} not in allowed directories")

    with open(abs_path, 'w') as f:
        f.write(content)
    return f"Wrote {len(content)} characters to {path}"

@mcp.tool()
def list_files(directory: str) -> list[str]:
    """List files in directory"""
    allowed_dirs = ["/workspace", "/data"]
    abs_dir = os.path.abspath(directory)

    if not any(abs_dir.startswith(d) for d in allowed_dirs):
        raise ValueError(f"Access denied: {directory}")

    return os.listdir(abs_dir)

if __name__ == "__main__":
    mcp.run()
```

### Configuration (Claude Desktop)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/server",
        "run",
        "filesystem_server.py"
      ]
    }
  }
}
```

**Security notes**:
- Always validate file paths against allowlist
- Never allow `..` or absolute paths from user input
- Log all file operations for audit trail
- Consider read-only vs read-write permissions

---

## Pattern 2: Database MCP Server (TypeScript)

**Use case**: Let agent query database with safe, parameterized queries.

### Setup

```bash
npm install @modelcontextprotocol/sdk
npm install pg  # or mysql2, sqlite3, etc.
```

### Implementation

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Pool } from 'pg';

// Database connection
const pool = new Pool({
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

// Initialize MCP server
const server = new Server(
  {
    name: "postgres-query",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define tool: safe SELECT query
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "query_users",
      description: "Query users table with filters",
      inputSchema: {
        type: "object",
        properties: {
          email: { type: "string" },
          status: { type: "string", enum: ["active", "inactive"] },
          limit: { type: "number", default: 100, maximum: 1000 }
        }
      }
    }
  ]
}));

server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "query_users") {
    const { email, status, limit = 100 } = request.params.arguments;

    // Build safe parameterized query
    let query = "SELECT id, email, status, created_at FROM users WHERE 1=1";
    const params = [];

    if (email) {
      params.push(email);
      query += ` AND email = $${params.length}`;
    }
    if (status) {
      params.push(status);
      query += ` AND status = $${params.length}`;
    }

    params.push(limit);
    query += ` LIMIT $${params.length}`;

    const result = await pool.query(query, params);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result.rows, null, 2)
        }
      ]
    };
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

**Security requirements**:
- NEVER concatenate user input into SQL
- Always use parameterized queries
- Whitelist allowed tables/columns
- Enforce row limits (prevent full table scans)
- Use read-only database user when possible
- Log all queries with user context

---

## Pattern 3: API Wrapper MCP Server

**Use case**: Wrap third-party API (GitHub, Slack, Jira) as MCP tools.

### GitHub API Example (Python)

```python
from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("GitHub Integration")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API = "https://api.github.com"

@mcp.tool()
def list_repos(username: str, limit: int = 10) -> str:
    """List public repositories for a GitHub user"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = httpx.get(
        f"{GITHUB_API}/users/{username}/repos",
        headers=headers,
        params={"per_page": min(limit, 100)}
    )
    response.raise_for_status()

    repos = response.json()
    return "\n".join([f"- {r['name']}: {r['description']}" for r in repos])

@mcp.tool()
def create_issue(
    repo: str,
    title: str,
    body: str,
    labels: list[str] = None
) -> str:
    """Create GitHub issue in specified repo (format: owner/repo)"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "title": title,
        "body": body,
        "labels": labels or []
    }

    response = httpx.post(
        f"{GITHUB_API}/repos/{repo}/issues",
        headers=headers,
        json=payload
    )
    response.raise_for_status()

    issue = response.json()
    return f"Created issue #{issue['number']}: {issue['html_url']}"

@mcp.tool()
def search_code(query: str, language: str = None) -> str:
    """Search code across GitHub repositories"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"q": query}

    if language:
        params["q"] += f" language:{language}"

    response = httpx.get(
        f"{GITHUB_API}/search/code",
        headers=headers,
        params=params
    )
    response.raise_for_status()

    results = response.json()
    items = results["items"][:5]  # Top 5 results

    return "\n".join([
        f"- {item['repository']['full_name']}/{item['path']}"
        for item in items
    ])
```

**Best practices**:
- Store API keys in environment variables
- Implement rate limiting (respect API quotas)
- Add retry logic with exponential backoff
- Return structured data (JSON) when possible
- Include error context in responses

---

## Pattern 4: Resources (Data Access)

**MCP Resources** = Read-only data that agent can retrieve.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Documentation Server")

@mcp.resource("docs://api/authentication")
def get_auth_docs() -> str:
    """Authentication documentation"""
    return """
    # API Authentication

    Use Bearer token in Authorization header:
    Authorization: Bearer YOUR_TOKEN

    Obtain token via POST /auth/login
    """

@mcp.resource("docs://api/users/{user_id}")
def get_user_docs(user_id: str) -> str:
    """User endpoint documentation"""
    return f"""
    # GET /api/users/{user_id}

    Retrieve user profile by ID.

    Response:
    {{
      "id": "{user_id}",
      "email": "user@example.com",
      "status": "active"
    }}
    """

# Agent can read these via:
# - "Show me auth docs" → retrieves docs://api/authentication
# - "User endpoint for ID 123" → retrieves docs://api/users/123
```

**Use resources for**:
- API documentation
- Configuration files
- Static data (country codes, timezones)
- Templates
- Schema definitions

---

## Pattern 5: Prompts (Reusable Templates)

**MCP Prompts** = Pre-written prompts with parameters.

```python
@mcp.prompt()
def code_review_prompt(language: str, code: str) -> str:
    """Generate code review prompt"""
    return f"""
    Review the following {language} code for:
    - Security vulnerabilities
    - Performance issues
    - Best practices violations
    - Potential bugs

    Code:
    ```{language}
    {code}
    ```

    Provide specific, actionable feedback.
    """

@mcp.prompt()
def test_generation_prompt(function_signature: str) -> str:
    """Generate test cases for function"""
    return f"""
    Generate comprehensive unit tests for:
    {function_signature}

    Include:
    - Happy path test
    - Edge cases
    - Error handling
    - Input validation
    """
```

---

## Testing Your MCP Server

### Local Testing (Python)

```bash
# Test server directly
python server.py

# Use MCP Inspector (official tool)
npx @modelcontextprotocol/inspector python server.py
```

### Testing with Claude Desktop

1. Add server to config (see configuration examples above)
2. Restart Claude Desktop
3. Check logs: `tail -f ~/Library/Logs/Claude/mcp*.log`
4. Test tool: "Use the [tool_name] tool to [action]"

### Debugging Checklist

- [ ] Server starts without errors
- [ ] Tools appear in Claude's tool list
- [ ] Tool descriptions are clear and actionable
- [ ] Input validation works (try invalid inputs)
- [ ] Error messages are helpful
- [ ] Logs show tool execution
- [ ] Performance is acceptable (<2s per tool call)

---

## Production Deployment

### Security Checklist

- [ ] Input validation on all parameters
- [ ] Output sanitization (no secrets in responses)
- [ ] Rate limiting per user/session
- [ ] Audit logging (who called what, when)
- [ ] Principle of least privilege (minimal permissions)
- [ ] Secrets in environment variables (never hardcoded)
- [ ] TLS for network communication
- [ ] Tool signature verification (Sigstore/Cosign)

### Monitoring

```python
import logging
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@mcp.tool()
def monitored_tool(param: str) -> str:
    """Tool with observability"""
    with tracer.start_as_current_span("tool_execution") as span:
        span.set_attribute("tool.name", "monitored_tool")
        span.set_attribute("tool.param", param)

        try:
            result = do_work(param)
            span.set_attribute("tool.success", True)
            return result
        except Exception as e:
            span.set_attribute("tool.success", False)
            span.set_attribute("tool.error", str(e))
            logging.error(f"Tool failed: {e}")
            raise
```

### Performance Optimization

- **Cache responses**: Use Redis/memcached for expensive operations
- **Batch operations**: Group multiple requests when possible
- **Async execution**: Use `async/await` for I/O-bound operations
- **Connection pooling**: Reuse database/API connections
- **Timeouts**: Set reasonable timeouts (5-30s)

---

## Common Patterns & Anti-Patterns

### [check] Good Patterns

**Clear tool descriptions**:
```python
@mcp.tool()
def search_documents(query: str, limit: int = 10) -> str:
    """Search internal documents using semantic search.

    Returns top matching documents with relevance scores.
    Use for: finding policies, procedures, technical docs.
    """
```

**Structured responses**:
```python
return json.dumps({
    "status": "success",
    "results": [...],
    "total_found": 42,
    "execution_time_ms": 123
})
```

**Granular tools** (not monolithic):
```python
# Good: Specific tools
@mcp.tool()
def create_user(...): pass

@mcp.tool()
def update_user(...): pass

# Bad: Generic "do anything" tool
@mcp.tool()
def manage_users(action: str, ...): pass  # Too broad
```

### [x] Anti-Patterns

**Vague descriptions**:
```python
@mcp.tool()
def process_data(data: str) -> str:
    """Process some data"""  # What does this do?
```

**Unsafe input handling**:
```python
# NEVER DO THIS
query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
os.system(f"rm {filename}")  # Command injection
```

**No error context**:
```python
# Bad
return "Error"

# Good
return json.dumps({
    "error": "Database connection failed",
    "details": "Connection timeout after 30s",
    "retry_after": 60
})
```

---

## MCP vs Direct API Calls

| Consideration | Use MCP | Use Direct API |
|---------------|---------|----------------|
| Multiple agents need same tool | [check] | |
| Need audit/governance | [check] | |
| Complex permission model | [check] | |
| One-off script | | [check] |
| Maximum performance critical | | [check] |
| Sharing tools across team | [check] | |

---

## Next Steps

**After building your MCP server**:
1. Test locally with MCP Inspector
2. Add comprehensive logging
3. Write integration tests
4. Document all tools (description + examples)
5. Deploy with monitoring
6. Share with team via config

**Related guides**:
- `frameworks/shared-foundations/protocols/mcp/mcp-server-development.md` - Full protocol specification
- `frameworks/shared-foundations/protocols/mcp/mcp-claude-integration.md` - Claude-specific patterns
- `a2a-handoff-patterns.md` - For agent-to-agent coordination (complementary to MCP)
- `tool-design-specs.md` - General tool design best practices

**Official resources**:
- MCP Specification: https://spec.modelcontextprotocol.io/
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
