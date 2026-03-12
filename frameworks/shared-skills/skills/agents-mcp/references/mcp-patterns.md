# MCP Integration Patterns

Common patterns for building MCP servers that integrate Claude Code with external systems.

## Contents

- Database Integration Patterns
- API Integration Patterns
- Filesystem Patterns
- Resource Patterns
- Prompt Templates
- Idempotent Operations
- Error Handling
- Pagination Pattern
- Zero-Trust Security Pattern
- Multi-Agent Orchestration Pattern
- Related

---

## Database Integration Patterns

### PostgreSQL with Connection Pooling

```typescript
import { Pool } from 'pg';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  await pool.end();
  process.exit(0);
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'query_database',
      description: 'Execute read-only SQL query',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'SQL SELECT query' },
          params: {
            type: 'array',
            items: { type: 'string' },
            description: 'Query parameters for prepared statement'
          },
        },
        required: ['query'],
      },
    },
    {
      name: 'list_tables',
      description: 'List all tables in database',
      inputSchema: { type: 'object', properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'query_database') {
    const query = args?.query as string;
    const params = args?.params as string[] | undefined;

    // Security: Only allow SELECT queries
    if (!query.trim().toUpperCase().startsWith('SELECT')) {
      throw new Error('Only SELECT queries allowed');
    }

    // Use parameterized query to prevent SQL injection
    const result = await pool.query(query, params);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(result.rows, null, 2),
      }],
    };
  }

  if (name === 'list_tables') {
    const result = await pool.query(`
      SELECT table_name, table_type
      FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name
    `);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(result.rows, null, 2),
      }],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});
```

### Multi-Database Support

```typescript
// Support multiple database connections
interface DatabaseConfig {
  name: string;
  type: 'postgres' | 'mysql' | 'sqlite';
  connectionString: string;
}

const databases = new Map<string, Pool>();

function initializeDatabases(configs: DatabaseConfig[]) {
  for (const config of configs) {
    databases.set(config.name, new Pool({
      connectionString: config.connectionString,
    }));
  }
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'query') {
    const { database, query } = request.params.arguments as any;

    const pool = databases.get(database);
    if (!pool) {
      throw new Error(`Unknown database: ${database}`);
    }

    const result = await pool.query(query);
    return { content: [{ type: 'text', text: JSON.stringify(result.rows) }] };
  }
});
```

---

## API Integration Patterns

### REST API with Retry Logic

```typescript
import { setTimeout } from 'timers/promises';

interface RetryConfig {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
}

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  config: RetryConfig = { maxRetries: 3, baseDelayMs: 1000, maxDelayMs: 10000 }
): Promise<Response> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      if (response.status === 429) {
        // Rate limited - extract retry-after if available
        const retryAfter = response.headers.get('retry-after');
        const delay = retryAfter
          ? parseInt(retryAfter) * 1000
          : Math.min(config.baseDelayMs * Math.pow(2, attempt), config.maxDelayMs);
        await setTimeout(delay);
        continue;
      }

      if (!response.ok && response.status >= 500) {
        throw new Error(`Server error: ${response.status}`);
      }

      return response;
    } catch (error) {
      lastError = error as Error;
      if (attempt < config.maxRetries) {
        const delay = Math.min(
          config.baseDelayMs * Math.pow(2, attempt),
          config.maxDelayMs
        );
        await setTimeout(delay);
      }
    }
  }

  throw lastError || new Error('Request failed after retries');
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'api_call') {
    const { endpoint, method = 'GET', body } = request.params.arguments as any;

    const response = await fetchWithRetry(
      `${process.env.API_BASE_URL}${endpoint}`,
      {
        method,
        headers: {
          'Authorization': `Bearer ${process.env.API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      }
    );

    const data = await response.json();
    return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
  }
});
```

### GraphQL Integration

```typescript
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'graphql_query',
      description: 'Execute GraphQL query',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'GraphQL query string' },
          variables: { type: 'object', description: 'Query variables' },
        },
        required: ['query'],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'graphql_query') {
    const { query, variables } = request.params.arguments as any;

    const response = await fetch(process.env.GRAPHQL_ENDPOINT!, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.GRAPHQL_TOKEN}`,
      },
      body: JSON.stringify({ query, variables }),
    });

    const result = await response.json();

    if (result.errors) {
      throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
    }

    return { content: [{ type: 'text', text: JSON.stringify(result.data, null, 2) }] };
  }
});
```

---

## Filesystem Patterns

### Scoped File Access

```typescript
import * as fs from 'fs/promises';
import * as path from 'path';

const ALLOWED_PATHS = [
  process.env.WORKSPACE_DIR || '/workspace',
  process.env.DATA_DIR || '/data',
];

function isPathAllowed(filePath: string): boolean {
  const resolved = path.resolve(filePath);
  return ALLOWED_PATHS.some(allowed =>
    resolved.startsWith(path.resolve(allowed))
  );
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'read_file') {
    const filePath = request.params.arguments?.path as string;

    if (!isPathAllowed(filePath)) {
      throw new Error(`Access denied: ${filePath} is outside allowed directories`);
    }

    const content = await fs.readFile(filePath, 'utf-8');
    return { content: [{ type: 'text', text: content }] };
  }

  if (request.params.name === 'write_file') {
    const { path: filePath, content } = request.params.arguments as any;

    if (!isPathAllowed(filePath)) {
      throw new Error(`Access denied: ${filePath} is outside allowed directories`);
    }

    await fs.writeFile(filePath, content, 'utf-8');
    return { content: [{ type: 'text', text: `File written: ${filePath}` }] };
  }

  if (request.params.name === 'list_directory') {
    const dirPath = request.params.arguments?.path as string;

    if (!isPathAllowed(dirPath)) {
      throw new Error(`Access denied: ${dirPath} is outside allowed directories`);
    }

    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    const result = entries.map(entry => ({
      name: entry.name,
      type: entry.isDirectory() ? 'directory' : 'file',
    }));

    return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
  }
});
```

---

## Resource Patterns

### Dynamic Resource Discovery

```typescript
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListResourceTemplatesRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

// List available resources
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: 'config://app',
      name: 'Application Configuration',
      mimeType: 'application/json',
      description: 'Current application settings',
    },
    {
      uri: 'metrics://current',
      name: 'Current Metrics',
      mimeType: 'application/json',
      description: 'Real-time application metrics',
    },
  ],
}));

// Resource templates for dynamic URIs
server.setRequestHandler(ListResourceTemplatesRequestSchema, async () => ({
  resourceTemplates: [
    {
      uriTemplate: 'user://{userId}/profile',
      name: 'User Profile',
      mimeType: 'application/json',
      description: 'Profile data for a specific user',
    },
    {
      uriTemplate: 'logs://{date}',
      name: 'Daily Logs',
      mimeType: 'text/plain',
      description: 'Application logs for a specific date (YYYY-MM-DD)',
    },
  ],
}));

// Read resources
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === 'config://app') {
    const config = await loadAppConfig();
    return {
      contents: [{
        uri,
        mimeType: 'application/json',
        text: JSON.stringify(config, null, 2),
      }],
    };
  }

  if (uri === 'metrics://current') {
    const metrics = await collectMetrics();
    return {
      contents: [{
        uri,
        mimeType: 'application/json',
        text: JSON.stringify(metrics, null, 2),
      }],
    };
  }

  // Handle templated URIs
  const userMatch = uri.match(/^user:\/\/(\w+)\/profile$/);
  if (userMatch) {
    const userId = userMatch[1];
    const profile = await loadUserProfile(userId);
    return {
      contents: [{
        uri,
        mimeType: 'application/json',
        text: JSON.stringify(profile, null, 2),
      }],
    };
  }

  throw new Error(`Unknown resource: ${uri}`);
});
```

---

## Prompt Templates

```typescript
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

server.setRequestHandler(ListPromptsRequestSchema, async () => ({
  prompts: [
    {
      name: 'analyze_data',
      description: 'Analyze dataset and provide insights',
      arguments: [
        { name: 'dataset', description: 'Name of dataset to analyze', required: true },
        { name: 'focus', description: 'Specific aspect to focus on', required: false },
      ],
    },
    {
      name: 'generate_report',
      description: 'Generate formatted report from data',
      arguments: [
        { name: 'type', description: 'Report type (summary, detailed, executive)', required: true },
        { name: 'period', description: 'Time period for report', required: true },
      ],
    },
  ],
}));

server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'analyze_data') {
    const dataset = args?.dataset;
    const focus = args?.focus || 'general trends';

    return {
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Please analyze the ${dataset} dataset, focusing on ${focus}.

Provide:
1. Key statistics and distributions
2. Notable patterns or anomalies
3. Actionable recommendations
4. Data quality observations`,
          },
        },
      ],
    };
  }

  throw new Error(`Unknown prompt: ${name}`);
});
```

---

## Idempotent Operations

```typescript
// Support client-generated request IDs for idempotency
const processedRequests = new Map<string, any>();

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const requestId = request.params.arguments?.requestId as string | undefined;

  // Check if already processed
  if (requestId && processedRequests.has(requestId)) {
    return processedRequests.get(requestId);
  }

  // Process the request
  const result = await processToolCall(request);

  // Cache result for idempotency
  if (requestId) {
    processedRequests.set(requestId, result);

    // Clean up old entries (keep last 1000)
    if (processedRequests.size > 1000) {
      const firstKey = processedRequests.keys().next().value;
      processedRequests.delete(firstKey);
    }
  }

  return result;
});
```

---

## Error Handling

```typescript
import { McpError, ErrorCode } from '@modelcontextprotocol/sdk/types.js';

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    return await processToolCall(request);
  } catch (error) {
    if (error instanceof McpError) {
      throw error;
    }

    // Map common errors to MCP error codes
    if (error instanceof TypeError) {
      throw new McpError(ErrorCode.InvalidParams, error.message);
    }

    if ((error as any).code === 'ENOENT') {
      throw new McpError(ErrorCode.InvalidParams, 'Resource not found');
    }

    if ((error as any).code === 'EACCES') {
      throw new McpError(ErrorCode.InvalidParams, 'Permission denied');
    }

    // Generic internal error
    throw new McpError(
      ErrorCode.InternalError,
      `Internal error: ${(error as Error).message}`
    );
  }
});
```

---

## Pagination Pattern

```typescript
interface PaginatedResult<T> {
  items: T[];
  nextCursor?: string;
  hasMore: boolean;
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'list_items') {
    const { cursor, limit = 50 } = request.params.arguments as any;

    const result = await fetchItems({ cursor, limit: limit + 1 });
    const hasMore = result.length > limit;
    const items = hasMore ? result.slice(0, limit) : result;
    const nextCursor = hasMore ? items[items.length - 1].id : undefined;

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          items,
          nextCursor,
          hasMore,
        }, null, 2),
      }],
    };
  }
});
```

---

## Zero-Trust Security Pattern

MCP servers must operate under a zero-trust model, treating every request as potentially malicious.

```typescript
import { z } from 'zod';
import { createHash } from 'crypto';

// Strict input validation for every request
const RequestValidator = z.object({
  method: z.string(),
  params: z.object({
    name: z.string().max(100),
    arguments: z.record(z.unknown()).optional(),
  }),
});

// Request fingerprinting for anomaly detection
function fingerprintRequest(request: any, clientId: string): string {
  const data = JSON.stringify({
    clientId,
    tool: request.params.name,
    timestamp: Math.floor(Date.now() / 60000), // 1-minute buckets
  });
  return createHash('sha256').update(data).digest('hex').slice(0, 16);
}

// Zero-trust middleware
async function zeroTrustMiddleware(
  request: any,
  clientId: string,
  handler: Function
) {
  // 1. Validate request structure
  const validated = RequestValidator.parse(request);

  // 2. Check rate limits per client
  const fingerprint = fingerprintRequest(request, clientId);
  const count = await redis.incr(`rate:${fingerprint}`);
  if (count === 1) await redis.expire(`rate:${fingerprint}`, 60);
  if (count > 100) throw new Error('Rate limit exceeded');

  // 3. Verify client has permission for this tool
  const allowedTools = await getClientPermissions(clientId);
  if (!allowedTools.includes(validated.params.name)) {
    throw new Error(`Tool not authorized: ${validated.params.name}`);
  }

  // 4. Log for audit trail
  await auditLog({
    clientId,
    tool: validated.params.name,
    fingerprint,
    timestamp: new Date().toISOString(),
  });

  // 5. Execute with timeout
  const timeoutMs = 30000;
  const result = await Promise.race([
    handler(validated),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), timeoutMs)
    ),
  ]);

  return result;
}
```

### Zero-Trust Checklist

```text
ZERO-TRUST IMPLEMENTATION

[ ] Validate every request against schema
[ ] Authenticate every request (no implicit trust)
[ ] Authorize each tool invocation individually
[ ] Rate limit per client AND per tool
[ ] Timeout all operations
[ ] Log all access for audit
[ ] Sanitize all outputs before returning
[ ] Never trust client-provided metadata
```

---

## Multi-Agent Orchestration Pattern

For 2026 enterprise deployments, multi-agent systems coordinate across multiple MCP servers.

```typescript
// Agent Squad Pattern: Multiple specialized agents collaborate

interface AgentRole {
  name: string;
  mcpServer: string;
  capabilities: string[];
}

const agentSquad: AgentRole[] = [
  { name: 'diagnostician', mcpServer: 'mcp-diagnostics', capabilities: ['analyze', 'detect'] },
  { name: 'remediator', mcpServer: 'mcp-remediation', capabilities: ['fix', 'patch'] },
  { name: 'validator', mcpServer: 'mcp-validation', capabilities: ['test', 'verify'] },
  { name: 'documenter', mcpServer: 'mcp-docs', capabilities: ['log', 'report'] },
];

// Orchestrator coordinates agent handoffs
class AgentOrchestrator {
  private mcpClients: Map<string, MCPClient> = new Map();

  async initializeSquad(squad: AgentRole[]) {
    for (const agent of squad) {
      const client = await this.connectToServer(agent.mcpServer);
      this.mcpClients.set(agent.name, client);
    }
  }

  async executeWorkflow(task: string) {
    const results: any[] = [];

    // 1. Diagnostician analyzes the problem
    const diagnosis = await this.invokeAgent('diagnostician', 'analyze', { task });
    results.push({ agent: 'diagnostician', result: diagnosis });

    // 2. Remediator fixes based on diagnosis
    const remediation = await this.invokeAgent('remediator', 'fix', {
      diagnosis: diagnosis.findings,
    });
    results.push({ agent: 'remediator', result: remediation });

    // 3. Validator verifies the fix
    const validation = await this.invokeAgent('validator', 'verify', {
      original: task,
      fix: remediation.changes,
    });
    results.push({ agent: 'validator', result: validation });

    // 4. Documenter records everything
    const documentation = await this.invokeAgent('documenter', 'report', {
      workflow: results,
    });

    return {
      success: validation.passed,
      results,
      documentation,
    };
  }

  private async invokeAgent(agentName: string, tool: string, args: any) {
    const client = this.mcpClients.get(agentName);
    if (!client) throw new Error(`Agent not found: ${agentName}`);

    return await client.callTool({ name: tool, arguments: args });
  }
}
```

### Multi-Agent Security Considerations

```text
MULTI-AGENT SECURITY

[ ] Each agent has minimal permissions (principle of least privilege)
[ ] Cross-agent communication is authenticated
[ ] No agent can access another's credentials
[ ] Orchestrator validates all handoff data
[ ] Audit trail spans entire workflow
[ ] Timeouts prevent runaway agent chains
[ ] Circuit breaker stops cascading failures
```

---

## Related

- [mcp-security.md](mcp-security.md) — Security hardening guide
- [mcp-servers.md](mcp-servers.md) — Official server list
- [../SKILL.md](../SKILL.md) — Quick reference
