# MCP Servers — Complete Reference

Official and community MCP servers for Claude Code integration.

## Contents

- Official Anthropic Servers
- Database Servers
- Cloud Storage Servers
- Communication Servers
- Developer Tool Servers
- Search Servers
- Utility Servers
- Transport Comparison
- Server Discovery
- Related

---

## Official Anthropic Servers

| Server | Package | Transport | Purpose |
|--------|---------|-----------|---------|
| PostgreSQL | `@modelcontextprotocol/server-postgres` | stdio | Database queries |
| Filesystem | `@modelcontextprotocol/server-filesystem` | stdio | File access |
| Git | `@modelcontextprotocol/server-git` | stdio | Repository operations |
| GitHub | `@modelcontextprotocol/server-github` | stdio | GitHub API |
| Slack | `@modelcontextprotocol/server-slack` | stdio | Slack integration |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | stdio | Browser automation |
| Brave Search | `@anthropic-ai/mcp-server-brave-search` | stdio | Web search |
| Memory | `@modelcontextprotocol/server-memory` | stdio | Persistent memory |
| Fetch | `@modelcontextprotocol/server-fetch` | stdio | HTTP requests |

---

## Database Servers

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

**Capabilities**: SELECT queries, table listing, schema introspection

**CLI Setup**:
```bash
claude mcp add postgres \
  --env POSTGRES_URL=postgresql://user:pass@localhost:5432/db \
  -- npx -y @modelcontextprotocol/server-postgres
```

### SQLite

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "./data/app.db"]
    }
  }
}
```

### MySQL

```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": ["-y", "@planetscale/mcp-server-mysql"],
      "env": {
        "MYSQL_URL": "${MYSQL_URL}"
      }
    }
  }
}
```

---

## Cloud Storage Servers

### Google Drive

```json
{
  "mcpServers": {
    "gdrive": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-gdrive"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}"
      }
    }
  }
}
```

### AWS S3

```json
{
  "mcpServers": {
    "s3": {
      "command": "npx",
      "args": ["-y", "@aws/mcp-server-s3"],
      "env": {
        "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
        "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
        "AWS_REGION": "${AWS_REGION}"
      }
    }
  }
}
```

---

## Communication Servers

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

**Capabilities**: List channels, read messages, search conversations

### Notion (HTTP Transport)

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

Or in `.claude/.mcp.json`:
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

### Asana (SSE Transport)

```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

### PostHog (Regional MCP endpoints)

Use your workspace region:

- EU: `https://mcp-eu.posthog.com/mcp`
- US: `https://mcp.posthog.com/mcp`

```bash
# Codex (streamable HTTP)
codex mcp add posthog --url https://mcp-eu.posthog.com/mcp
codex mcp login posthog

# Codex fallback if initialize returns HTTP 500
codex mcp remove posthog
codex mcp add posthog -- npx -y mcp-remote@latest https://mcp-eu.posthog.com/sse
```

```bash
# Claude Code (HTTP transport)
claude mcp add --transport http posthog https://mcp-eu.posthog.com/mcp
```

---

## Developer Tool Servers

### GitHub

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Capabilities**: PRs, issues, repos, branches, commits

### Linear

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "@linear/mcp-server"],
      "env": {
        "LINEAR_API_KEY": "${LINEAR_API_KEY}"
      }
    }
  }
}
```

### Sentry

```json
{
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}"
      }
    }
  }
}
```

---

## Search Servers

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

### Perplexity

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    }
  }
}
```

---

## Utility Servers

### Memory (Persistent)

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Capabilities**: Store and retrieve information across sessions

### Sequential Thinking

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-sequential-thinking"]
    }
  }
}
```

**Capabilities**: Break down complex tasks into steps

### Fetch (HTTP Requests)

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

**Capabilities**: Make HTTP requests to APIs

---

## Transport Comparison

| Transport | Use Case | Configuration |
|-----------|----------|---------------|
| **HTTP** | Remote cloud servers | `--transport http` + URL |
| **SSE** | Real-time remote servers | `--transport sse` + URL |
| **stdio** | Local processes | Default, `command` + `args` |

### HTTP (Recommended for Remote)

```bash
claude mcp add --transport http server-name https://mcp.example.com/mcp
```

### SSE (Server-Sent Events)

```bash
claude mcp add --transport sse server-name https://mcp.example.com/sse
```

### stdio (Local Processes)

```bash
claude mcp add server-name -- npx -y @scope/package
```

---

## Server Discovery

Find MCP servers:
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [MCPcat Directory](https://mcpcat.io/)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

---

## Related

- [mcp-custom.md](mcp-custom.md) — Build custom MCP servers
- [../SKILL.md](../SKILL.md) — Quick reference
