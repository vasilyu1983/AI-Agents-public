---
name: claude-code-mcp
description: Configure and build Model Context Protocol (MCP) servers for Claude Code integration. Set up database, filesystem, git, and API connections. Build custom MCP servers with TypeScript/Python SDK, implement tools and resources, configure transports (stdio, HTTP), and deploy for production.
---

# Claude Code MCP — Complete Reference

This skill provides the definitive reference for configuring and building MCP servers in Claude Code. Use this when:

- Connecting Claude to databases, filesystems, APIs, or other external data sources
- Building custom MCP servers for proprietary integrations
- Deploying MCP servers to production

---

## Quick Reference

| Server | Package | Purpose |
|--------|---------|---------|
| PostgreSQL | `@modelcontextprotocol/server-postgres` | Database queries |
| Filesystem | `@modelcontextprotocol/server-filesystem` | File access |
| Git | `@modelcontextprotocol/server-git` | Repository operations |
| Brave Search | `@anthropic-ai/mcp-server-brave-search` | Web search |
| Slack | `@modelcontextprotocol/server-slack` | Slack integration |

## Configuration Location

```text
.claude/
└── .mcp.json    # MCP server configuration
```

---

## Configuration Schema

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@scope/package-name"],
      "env": {
        "VAR_NAME": "${ENV_VAR}"
      }
    }
  }
}
```

---

## Official MCP Servers

### PostgreSQL

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

**Capabilities**:
- Execute SELECT queries
- List tables and schemas
- Describe table structure

### Filesystem

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/allowed/path1",
        "/allowed/path2"
      ]
    }
  }
}
```

**Capabilities**:
- Read files in allowed paths
- List directory contents
- Search file contents

**Security**: Paths are allowlisted—Claude can only access specified directories.

### Git

```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "env": {
        "GIT_DIR": "${CLAUDE_PROJECT_DIR}"
      }
    }
  }
}
```

**Capabilities**:
- Git status and diff
- Commit history
- Branch information

### Brave Search

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

**Capabilities**:
- Web search
- News search
- Local search

### Slack

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    }
  }
}
```

**Capabilities**:
- List channels
- Read messages
- Search conversations

---

## Environment Variables

### Reference Syntax

```json
{
  "env": {
    "VAR_NAME": "${ENVIRONMENT_VARIABLE}"
  }
}
```

The `${VAR}` syntax references environment variables from your shell.

### Setting Variables

```bash
# .env file (project-level)
DATABASE_URL=postgresql://user:pass@localhost:5432/db
BRAVE_API_KEY=BSA...

# Export in shell
export DATABASE_URL="postgresql://..."
```

---

## Multiple Servers

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "POSTGRES_URL": "${DATABASE_URL}" }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    }
  }
}
```

---

## Custom MCP Servers

### Local Server

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["./mcp-servers/my-server/dist/index.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

### Python Server

```json
{
  "mcpServers": {
    "python-server": {
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": {}
    }
  }
}
```

---

## CLI Commands

Manage MCP servers from the command line:

```bash
# Add server (HTTP transport - recommended for remote)
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Add server (stdio transport - for local)
claude mcp add postgres --env POSTGRES_URL=postgresql://... -- npx -y @modelcontextprotocol/server-postgres

# List configured servers
claude mcp list

# Remove server
claude mcp remove notion

# Test server connection
claude mcp get notion
```

---

## Transport Types

| Transport | Use Case | Recommendation |
|-----------|----------|----------------|
| **HTTP** | Remote cloud servers | Recommended for remote |
| **SSE** | Real-time remote | Legacy, use HTTP |
| **stdio** | Local processes | Default for local |

### HTTP (Recommended for Remote)

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

Or in `.mcp.json`:
```json
{
  "mcpServers": {
    "notion": {
      "url": "https://mcp.notion.com/mcp",
      "transport": "http"
    }
  }
}
```

### stdio (Default for Local)

```text
Claude Code ←→ stdin/stdout ←→ MCP Server
```

Most common for local servers. Process runs as child of Claude Code.

### SSE (Legacy Remote)

```json
{
  "mcpServers": {
    "remote-server": {
      "url": "https://mcp.example.com/sse",
      "transport": "sse"
    }
  }
}
```

For networked MCP servers (prefer HTTP for new integrations).

---

## Token Limits

MCP tool outputs are monitored for size:

| Threshold | Behavior |
|-----------|----------|
| 10,000 tokens | Warning displayed |
| 25,000 tokens | Maximum (default) |

**Override maximum**:

```bash
MAX_MCP_OUTPUT_TOKENS=50000 claude
```

---

## Security Considerations

```text
MCP SECURITY CHECKLIST

[ ] Use environment variables for secrets (never hardcode)
[ ] Limit filesystem paths to necessary directories
[ ] Use read-only database credentials when possible
[ ] Validate all inputs in custom servers
[ ] Log access for auditing
[ ] Rotate API keys regularly
```

### Credential Management

```bash
# Use secret managers
export DATABASE_URL="$(aws secretsmanager get-secret-value --secret-id db-url | jq -r .SecretString)"

# Or use .env files (gitignored)
source .env
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not found | Check package name, run `npx -y @scope/package` manually |
| Permission denied | Check file/directory permissions |
| Connection failed | Verify credentials, check network |
| Timeout | Server may be slow, check logs |

### Debug Mode

```bash
# Test MCP server manually
npx -y @modelcontextprotocol/server-postgres

# Check server logs
CLAUDE_MCP_DEBUG=1 claude
```

---

## Navigation

**Resources**

- [resources/mcp-servers.md](resources/mcp-servers.md) — Complete server list
- [resources/mcp-custom.md](resources/mcp-custom.md) — Building custom servers
- [resources/mcp-patterns.md](resources/mcp-patterns.md) — Common integration patterns
- [resources/mcp-security.md](resources/mcp-security.md) — Security hardening guide

**Templates (Copy-Paste Ready)**

- [templates/database/template-mcp-database.md](templates/database/template-mcp-database.md) — PostgreSQL/MySQL MCP server
- [templates/api/template-mcp-api.md](templates/api/template-mcp-api.md) — REST/GraphQL API integration
- [templates/filesystem/template-mcp-filesystem.md](templates/filesystem/template-mcp-filesystem.md) — Scoped file access
- [templates/deployment/template-mcp-docker.md](templates/deployment/template-mcp-docker.md) — Docker + Kubernetes deployment

**Related Skills**

- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database patterns
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API integration
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Security patterns
