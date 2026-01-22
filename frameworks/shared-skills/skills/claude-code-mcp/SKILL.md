---
name: claude-code-mcp
description: Configure and build Model Context Protocol (MCP) servers for Claude Code integration. Set up database, filesystem, git, and API connections. Build custom MCP servers with TypeScript/Python SDK, implement tools and resources, configure transports (stdio, HTTP), and deploy for production.
---

# Claude Code MCP — Complete Reference

**Specification**: [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) (November 2025)

This skill provides the definitive reference for configuring and building MCP servers in Claude Code. Use this when:

- Connecting Claude to databases, filesystems, APIs, or other external data sources
- Building custom MCP servers for proprietary integrations
- Deploying MCP servers to production (OAuth 2.1 + CIMD required for HTTP)

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

# Enable/disable servers (inside Claude Code session)
/mcp enable 1    # Enable server at index 1
/mcp disable 2   # Disable server at index 2
```

### Permission Management

```bash
# Allow all tools from a specific server (wildcard)
claude mcp add --allow "mcp__postgres__*" postgres -- npx -y @modelcontextprotocol/server-postgres

# Allow specific tools only
claude mcp add --allow "mcp__postgres__query,mcp__postgres__list_tables" postgres -- ...

# Deny specific tools
claude mcp add --deny "mcp__filesystem__write_file" filesystem -- ...
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

See [references/mcp-security.md](references/mcp-security.md) for the complete security hardening guide.

```text
MCP SECURITY CHECKLIST (November 2025)

Authentication (HTTP transports)
[ ] OAuth 2.1 mandatory for HTTP
[ ] Client ID Metadata Documents (CIMD) for registration
[ ] Resource Indicators (RFC 8707) for token scoping

Secrets Management
[ ] Use MCP Secret Wrapper or vault integration
[ ] No static secrets in config files
[ ] Environment variable injection at runtime

Access Control
[ ] Zero-trust model - validate every request
[ ] Minimal permissions (incremental scopes)
[ ] Scoped filesystem access
[ ] Read-only database by default
```

### Credential Management

```bash
# RECOMMENDED: Use MCP Secret Wrapper (no secrets in config)
mcp-secret-wrapper --vault aws-secrets-manager --secret-id mcp/db-url --server @modelcontextprotocol/server-postgres

# Alternative: Use secret managers
export DATABASE_URL="$(aws secretsmanager get-secret-value --secret-id db-url | jq -r .SecretString)"

# Development only: .env files (gitignored)
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

- [references/mcp-servers.md](references/mcp-servers.md) — Complete server list
- [references/mcp-custom.md](references/mcp-custom.md) — Building custom servers
- [references/mcp-patterns.md](references/mcp-patterns.md) — Common integration patterns
- [references/mcp-security.md](references/mcp-security.md) — Security hardening guide

**Templates (Copy-Paste Ready)**

- [assets/database/template-mcp-database.md](assets/database/template-mcp-database.md) — PostgreSQL/MySQL MCP server
- [assets/api/template-mcp-api.md](assets/api/template-mcp-api.md) — REST/GraphQL API integration
- [assets/filesystem/template-mcp-filesystem.md](assets/filesystem/template-mcp-filesystem.md) — Scoped file access
- [assets/deployment/template-mcp-docker.md](assets/deployment/template-mcp-docker.md) — Docker + Kubernetes deployment

**Related Skills**

- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database patterns
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API integration
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Security patterns
