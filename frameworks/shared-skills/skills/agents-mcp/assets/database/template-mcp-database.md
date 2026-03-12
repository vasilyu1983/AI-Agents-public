# MCP Database Server Template

*Purpose: Production-ready MCP server for PostgreSQL/MySQL database integration with Claude Code.*

---

## When to Use

Use this template when building:

- Database query interfaces for Claude
- Read-only data exploration tools
- Schema inspection and documentation
- Analytics and reporting integrations
- Multi-database access gateways

---

# TEMPLATE STARTS HERE

## 1. Project Overview

**Project Name:**
[mcp-server-database]

**Description:**
[MCP server providing secure database access for Claude Code]

**Database:**
- [ ] PostgreSQL
- [ ] MySQL
- [ ] SQLite
- [ ] Multiple databases

**Access Level:**
- [ ] Read-only (SELECT only)
- [ ] Read-write (with audit logging)
- [ ] Admin (schema modifications)

---

## 2. Project Structure

```
mcp-server-database/
  src/
    index.ts              # Server entry point
    config.ts             # Configuration loader
    database/
      connection.ts       # Connection pool
      queries.ts          # Query whitelist (optional)
      validation.ts       # SQL validation
    tools/
      query.ts            # Execute queries
      schema.ts           # Inspect schema
      tables.ts           # List tables
    references/
      schema.ts           # Schema as resources
    middleware/
      audit.ts            # Audit logging
      rateLimit.ts        # Rate limiting
  tests/
    tools.test.ts
    security.test.ts
  package.json
  tsconfig.json
  .env.example
  Dockerfile
```

---

## 3. Package Configuration

```json
{
  "name": "[mcp-server-database]",
  "version": "1.0.0",
  "description": "[MCP server for database access]",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "test": "vitest",
    "lint": "eslint src/"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "pg": "^8.11.0",
    "zod": "^3.22.0",
    "winston": "^3.11.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/pg": "^8.10.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  }
}
```

---

## 4. TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 5. Environment Variables

```bash
# .env.example

# Database Connection
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10
DATABASE_TIMEOUT_MS=30000

# Security
ALLOWED_SCHEMAS=public
QUERY_TIMEOUT_MS=10000
MAX_ROWS_LIMIT=1000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_MS=60000

# Logging
LOG_LEVEL=info
LOG_QUERIES=true
AUDIT_LOG_PATH=./logs/audit.log
```

---

## 6. Server Implementation

```typescript
// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { Pool } from 'pg';
import { config } from './config.js';
import { createAuditLogger } from './middleware/audit.js';

// Initialize connection pool
const pool = new Pool({
  connectionString: config.databaseUrl,
  min: config.poolMin,
  max: config.poolMax,
  idleTimeoutMillis: config.timeout,
});

const auditLogger = createAuditLogger(config.auditLogPath);

const server = new Server(
  {
    name: '[mcp-server-database]',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'query_database',
      description: 'Execute a read-only SQL query against the database',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'SQL SELECT query to execute',
          },
          params: {
            type: 'array',
            items: { type: 'string' },
            description: 'Query parameters for prepared statement',
          },
          limit: {
            type: 'number',
            description: 'Maximum rows to return (default: 100, max: 1000)',
            default: 100,
          },
        },
        required: ['query'],
      },
    },
    {
      name: 'list_tables',
      description: 'List all tables in the database with row counts',
      inputSchema: {
        type: 'object',
        properties: {
          schema: {
            type: 'string',
            description: 'Schema name (default: public)',
            default: 'public',
          },
        },
      },
    },
    {
      name: 'describe_table',
      description: 'Get column definitions for a table',
      inputSchema: {
        type: 'object',
        properties: {
          table: {
            type: 'string',
            description: 'Table name to describe',
          },
          schema: {
            type: 'string',
            description: 'Schema name (default: public)',
            default: 'public',
          },
        },
        required: ['table'],
      },
    },
  ],
}));

// Implement tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  auditLogger.log('tool_call', { tool: name, args });

  try {
    switch (name) {
      case 'query_database': {
        const query = args?.query as string;
        const params = args?.params as string[] | undefined;
        const limit = Math.min((args?.limit as number) || 100, config.maxRowsLimit);

        // Security: Only allow SELECT queries
        const normalized = query.trim().toUpperCase();
        if (!normalized.startsWith('SELECT')) {
          throw new Error('Only SELECT queries are allowed');
        }

        // Security: Block dangerous patterns
        const dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE'];
        for (const keyword of dangerous) {
          if (normalized.includes(keyword)) {
            throw new Error(`Forbidden keyword: ${keyword}`);
          }
        }

        // Add LIMIT if not present
        const limitedQuery = normalized.includes('LIMIT')
          ? query
          : `${query} LIMIT ${limit}`;

        const result = await pool.query(limitedQuery, params);

        auditLogger.log('query_success', {
          query: limitedQuery,
          rowCount: result.rowCount,
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              columns: result.fields.map(f => f.name),
              rows: result.rows,
              rowCount: result.rowCount,
            }, null, 2),
          }],
        };
      }

      case 'list_tables': {
        const schema = (args?.schema as string) || 'public';

        // Validate schema is allowed
        if (!config.allowedSchemas.includes(schema)) {
          throw new Error(`Schema not allowed: ${schema}`);
        }

        const result = await pool.query(`
          SELECT
            t.table_name,
            t.table_type,
            pg_stat_user_tables.n_live_tup as row_count
          FROM information_schema.tables t
          LEFT JOIN pg_stat_user_tables
            ON t.table_name = pg_stat_user_tables.relname
          WHERE t.table_schema = $1
          ORDER BY t.table_name
        `, [schema]);

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(result.rows, null, 2),
          }],
        };
      }

      case 'describe_table': {
        const table = args?.table as string;
        const schema = (args?.schema as string) || 'public';

        // Validate inputs
        if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(table)) {
          throw new Error('Invalid table name');
        }
        if (!config.allowedSchemas.includes(schema)) {
          throw new Error(`Schema not allowed: ${schema}`);
        }

        const result = await pool.query(`
          SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
          FROM information_schema.columns
          WHERE table_schema = $1 AND table_name = $2
          ORDER BY ordinal_position
        `, [schema, table]);

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(result.rows, null, 2),
          }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    auditLogger.log('tool_error', {
      tool: name,
      error: (error as Error).message,
    });
    throw error;
  }
});

// Define resources (schema documentation)
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: 'schema://tables',
      name: 'Database Schema',
      mimeType: 'application/json',
      description: 'Complete database schema documentation',
    },
  ],
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  if (request.params.uri === 'schema://tables') {
    const result = await pool.query(`
      SELECT
        t.table_name,
        json_agg(json_build_object(
          'column', c.column_name,
          'type', c.data_type,
          'nullable', c.is_nullable
        ) ORDER BY c.ordinal_position) as columns
      FROM information_schema.tables t
      JOIN information_schema.columns c
        ON t.table_name = c.table_name
        AND t.table_schema = c.table_schema
      WHERE t.table_schema = 'public'
      GROUP BY t.table_name
      ORDER BY t.table_name
    `);

    return {
      contents: [{
        uri: request.params.uri,
        mimeType: 'application/json',
        text: JSON.stringify(result.rows, null, 2),
      }],
    };
  }

  throw new Error(`Unknown resource: ${request.params.uri}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  await pool.end();
  process.exit(0);
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('[mcp-server-database] Server started');
```

---

## 7. Configuration Loader

```typescript
// src/config.ts
import { z } from 'zod';

const configSchema = z.object({
  databaseUrl: z.string().url(),
  poolMin: z.number().default(2),
  poolMax: z.number().default(10),
  timeout: z.number().default(30000),
  allowedSchemas: z.array(z.string()).default(['public']),
  queryTimeout: z.number().default(10000),
  maxRowsLimit: z.number().default(1000),
  rateLimitRequests: z.number().default(100),
  rateLimitWindow: z.number().default(60000),
  logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  logQueries: z.boolean().default(true),
  auditLogPath: z.string().default('./logs/audit.log'),
});

export const config = configSchema.parse({
  databaseUrl: process.env.DATABASE_URL,
  poolMin: parseInt(process.env.DATABASE_POOL_MIN || '2'),
  poolMax: parseInt(process.env.DATABASE_POOL_MAX || '10'),
  timeout: parseInt(process.env.DATABASE_TIMEOUT_MS || '30000'),
  allowedSchemas: (process.env.ALLOWED_SCHEMAS || 'public').split(','),
  queryTimeout: parseInt(process.env.QUERY_TIMEOUT_MS || '10000'),
  maxRowsLimit: parseInt(process.env.MAX_ROWS_LIMIT || '1000'),
  rateLimitRequests: parseInt(process.env.RATE_LIMIT_REQUESTS || '100'),
  rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000'),
  logLevel: process.env.LOG_LEVEL || 'info',
  logQueries: process.env.LOG_QUERIES !== 'false',
  auditLogPath: process.env.AUDIT_LOG_PATH || './logs/audit.log',
});
```

---

## 8. Audit Logger

```typescript
// src/middleware/audit.ts
import { createLogger, format, transports } from 'winston';
import * as fs from 'fs';
import * as path from 'path';

export function createAuditLogger(logPath: string) {
  const logDir = path.dirname(logPath);
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const logger = createLogger({
    level: 'info',
    format: format.combine(
      format.timestamp(),
      format.json()
    ),
    transports: [
      new transports.File({ filename: logPath }),
    ],
  });

  return {
    log(event: string, data: Record<string, unknown>) {
      logger.info({ event, ...data });
    },
  };
}
```

---

## 9. Claude Code Configuration

```json
// .claude/.mcp.json
{
  "mcpServers": {
    "[server-name]": {
      "command": "node",
      "args": ["./mcp-server-database/dist/index.js"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}",
        "ALLOWED_SCHEMAS": "public",
        "MAX_ROWS_LIMIT": "1000"
      }
    }
  }
}
```

---

## 10. Security Checklist

```text
[ ] DATABASE_URL uses SSL (?sslmode=require)
[ ] Connection uses minimal-privilege database user
[ ] Only SELECT queries allowed (enforced in code)
[ ] Dangerous keywords blocked (DROP, DELETE, etc.)
[ ] Schema access restricted via ALLOWED_SCHEMAS
[ ] Row limits enforced (MAX_ROWS_LIMIT)
[ ] Query timeout configured
[ ] Audit logging enabled
[ ] Rate limiting configured
[ ] Credentials in environment variables only
```

---

## 11. Testing

```typescript
// tests/tools.test.ts
import { describe, it, expect } from 'vitest';

describe('query_database', () => {
  it('should allow SELECT queries', async () => {
    // Test implementation
  });

  it('should block DROP statements', async () => {
    // Test implementation
  });

  it('should enforce row limits', async () => {
    // Test implementation
  });

  it('should use parameterized queries', async () => {
    // Test implementation
  });
});

describe('security', () => {
  it('should validate schema names', async () => {
    // Test implementation
  });

  it('should validate table names', async () => {
    // Test implementation
  });

  it('should log all queries', async () => {
    // Test implementation
  });
});
```

---

## 12. Build and Run

```bash
# Install dependencies
npm install

# Build
npm run build

# Run locally
DATABASE_URL="postgresql://user:pass@localhost:5432/mydb" npm start

# Test with Claude Code
claude --mcp-config .claude/.mcp.json
```
