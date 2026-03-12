# MCP Filesystem Server Template

*Purpose: Production-ready MCP server for scoped filesystem access with Claude Code.*

---

## When to Use

Use this template when building:

- Project file browsers for Claude
- Document management integrations
- Log file viewers
- Configuration file editors
- Asset management systems

---

# TEMPLATE STARTS HERE

## 1. Project Overview

**Project Name:**
[mcp-server-filesystem]

**Description:**
[MCP server providing scoped filesystem access for Claude Code]

**Access Level:**
- [ ] Read-only
- [ ] Read-write
- [ ] Full access (with audit logging)

**Allowed Paths:**
- [ ] Single directory
- [ ] Multiple directories
- [ ] Pattern-based

---

## 2. Project Structure

```
mcp-server-filesystem/
  src/
    index.ts              # Server entry point
    config.ts             # Configuration
    tools/
      read.ts             # Read files
      write.ts            # Write files
      list.ts             # List directories
      search.ts           # Search files
    middleware/
      pathValidator.ts    # Path security
      audit.ts            # Audit logging
    types/
      fs.ts               # Type definitions
  tests/
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
  "name": "[mcp-server-filesystem]",
  "version": "1.0.0",
  "description": "[MCP server for filesystem access]",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "test": "vitest"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.22.0",
    "winston": "^3.11.0",
    "minimatch": "^9.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  }
}
```

---

## 4. Environment Variables

```bash
# .env.example

# Allowed Paths (comma-separated absolute paths)
ALLOWED_PATHS=/workspace,/data

# Blocked Patterns (glob patterns)
BLOCKED_PATTERNS=**/.env,**/*.key,**/.git/**,**/node_modules/**

# File Size Limits
MAX_FILE_SIZE_BYTES=10485760
MAX_DIRECTORY_DEPTH=10

# Write Access (set to 'true' to enable)
ALLOW_WRITE=false
ALLOW_DELETE=false

# Logging
LOG_LEVEL=info
AUDIT_LOG_PATH=./logs/audit.log
```

---

## 5. Server Implementation

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
import * as fs from 'fs/promises';
import * as path from 'path';
import { config } from './config.js';
import { PathValidator } from './middleware/pathValidator.js';
import { createAuditLogger } from './middleware/audit.js';

const pathValidator = new PathValidator(config);
const auditLogger = createAuditLogger(config.auditLogPath);

const server = new Server(
  {
    name: '[mcp-server-filesystem]',
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
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const tools = [
    {
      name: 'read_file',
      description: 'Read contents of a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: {
            type: 'string',
            description: 'Path to file (relative to allowed directories)',
          },
          encoding: {
            type: 'string',
            enum: ['utf-8', 'base64'],
            default: 'utf-8',
            description: 'File encoding',
          },
        },
        required: ['path'],
      },
    },
    {
      name: 'list_directory',
      description: 'List contents of a directory',
      inputSchema: {
        type: 'object',
        properties: {
          path: {
            type: 'string',
            description: 'Directory path',
          },
          recursive: {
            type: 'boolean',
            default: false,
            description: 'List recursively',
          },
          pattern: {
            type: 'string',
            description: 'Glob pattern to filter (e.g., *.ts)',
          },
        },
        required: ['path'],
      },
    },
    {
      name: 'search_files',
      description: 'Search for files by name or content',
      inputSchema: {
        type: 'object',
        properties: {
          directory: {
            type: 'string',
            description: 'Directory to search in',
          },
          pattern: {
            type: 'string',
            description: 'Filename glob pattern',
          },
          content: {
            type: 'string',
            description: 'Content to search for (regex)',
          },
          maxResults: {
            type: 'number',
            default: 50,
            description: 'Maximum results to return',
          },
        },
        required: ['directory'],
      },
    },
    {
      name: 'file_info',
      description: 'Get metadata about a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: {
            type: 'string',
            description: 'Path to file',
          },
        },
        required: ['path'],
      },
    },
  ];

  // Add write tools if enabled
  if (config.allowWrite) {
    tools.push(
      {
        name: 'write_file',
        description: 'Write content to a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to file',
            },
            content: {
              type: 'string',
              description: 'Content to write',
            },
            createDirectories: {
              type: 'boolean',
              default: false,
              description: 'Create parent directories if missing',
            },
          },
          required: ['path', 'content'],
        },
      },
      {
        name: 'create_directory',
        description: 'Create a new directory',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Directory path to create',
            },
          },
          required: ['path'],
        },
      }
    );
  }

  if (config.allowDelete) {
    tools.push({
      name: 'delete_file',
      description: 'Delete a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: {
            type: 'string',
            description: 'Path to file to delete',
          },
        },
        required: ['path'],
      },
    });
  }

  return { tools };
});

// Implement tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  auditLogger.log('tool_call', { tool: name, args });

  try {
    switch (name) {
      case 'read_file': {
        const filePath = args?.path as string;
        const encoding = (args?.encoding as BufferEncoding) || 'utf-8';

        const resolvedPath = pathValidator.validate(filePath);

        // Check file size
        const stats = await fs.stat(resolvedPath);
        if (stats.size > config.maxFileSize) {
          throw new Error(`File too large: ${stats.size} bytes (max: ${config.maxFileSize})`);
        }

        const content = await fs.readFile(resolvedPath, encoding);

        auditLogger.log('file_read', { path: resolvedPath, size: stats.size });

        return {
          content: [{
            type: 'text',
            text: content,
          }],
        };
      }

      case 'list_directory': {
        const dirPath = args?.path as string;
        const recursive = args?.recursive as boolean || false;
        const pattern = args?.pattern as string | undefined;

        const resolvedPath = pathValidator.validate(dirPath);

        const entries = await listDirectory(resolvedPath, recursive, pattern, 0);

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(entries, null, 2),
          }],
        };
      }

      case 'search_files': {
        const directory = args?.directory as string;
        const filePattern = args?.pattern as string | undefined;
        const contentSearch = args?.content as string | undefined;
        const maxResults = Math.min((args?.maxResults as number) || 50, 100);

        const resolvedPath = pathValidator.validate(directory);

        const results = await searchFiles(
          resolvedPath,
          filePattern,
          contentSearch,
          maxResults
        );

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(results, null, 2),
          }],
        };
      }

      case 'file_info': {
        const filePath = args?.path as string;
        const resolvedPath = pathValidator.validate(filePath);

        const stats = await fs.stat(resolvedPath);

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              path: resolvedPath,
              size: stats.size,
              created: stats.birthtime,
              modified: stats.mtime,
              isDirectory: stats.isDirectory(),
              isFile: stats.isFile(),
              permissions: stats.mode.toString(8),
            }, null, 2),
          }],
        };
      }

      case 'write_file': {
        if (!config.allowWrite) {
          throw new Error('Write access is disabled');
        }

        const filePath = args?.path as string;
        const content = args?.content as string;
        const createDirs = args?.createDirectories as boolean || false;

        const resolvedPath = pathValidator.validate(filePath);

        if (createDirs) {
          await fs.mkdir(path.dirname(resolvedPath), { recursive: true });
        }

        await fs.writeFile(resolvedPath, content, 'utf-8');

        auditLogger.log('file_write', { path: resolvedPath, size: content.length });

        return {
          content: [{
            type: 'text',
            text: `File written: ${resolvedPath}`,
          }],
        };
      }

      case 'create_directory': {
        if (!config.allowWrite) {
          throw new Error('Write access is disabled');
        }

        const dirPath = args?.path as string;
        const resolvedPath = pathValidator.validate(dirPath);

        await fs.mkdir(resolvedPath, { recursive: true });

        auditLogger.log('directory_create', { path: resolvedPath });

        return {
          content: [{
            type: 'text',
            text: `Directory created: ${resolvedPath}`,
          }],
        };
      }

      case 'delete_file': {
        if (!config.allowDelete) {
          throw new Error('Delete access is disabled');
        }

        const filePath = args?.path as string;
        const resolvedPath = pathValidator.validate(filePath);

        await fs.unlink(resolvedPath);

        auditLogger.log('file_delete', { path: resolvedPath });

        return {
          content: [{
            type: 'text',
            text: `File deleted: ${resolvedPath}`,
          }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    auditLogger.log('tool_error', { tool: name, error: (error as Error).message });
    throw error;
  }
});

// Helper functions
async function listDirectory(
  dirPath: string,
  recursive: boolean,
  pattern: string | undefined,
  depth: number
): Promise<Array<{ name: string; type: string; path: string }>> {
  if (depth > config.maxDirectoryDepth) {
    return [];
  }

  const entries = await fs.readdir(dirPath, { withFileTypes: true });
  const results: Array<{ name: string; type: string; path: string }> = [];

  for (const entry of entries) {
    const entryPath = path.join(dirPath, entry.name);

    // Skip blocked patterns
    if (pathValidator.isBlocked(entryPath)) {
      continue;
    }

    // Apply filename pattern filter
    if (pattern && !minimatch(entry.name, pattern)) {
      continue;
    }

    results.push({
      name: entry.name,
      type: entry.isDirectory() ? 'directory' : 'file',
      path: entryPath,
    });

    if (recursive && entry.isDirectory()) {
      const subEntries = await listDirectory(entryPath, true, pattern, depth + 1);
      results.push(...subEntries);
    }
  }

  return results;
}

async function searchFiles(
  directory: string,
  filePattern: string | undefined,
  contentSearch: string | undefined,
  maxResults: number
): Promise<Array<{ path: string; matches?: string[] }>> {
  const results: Array<{ path: string; matches?: string[] }> = [];
  const entries = await listDirectory(directory, true, filePattern, 0);

  for (const entry of entries) {
    if (results.length >= maxResults) break;
    if (entry.type !== 'file') continue;

    if (contentSearch) {
      try {
        const content = await fs.readFile(entry.path, 'utf-8');
        const regex = new RegExp(contentSearch, 'gi');
        const matches = content.match(regex);
        if (matches) {
          results.push({ path: entry.path, matches: matches.slice(0, 5) });
        }
      } catch {
        // Skip files that can't be read
      }
    } else {
      results.push({ path: entry.path });
    }
  }

  return results;
}

// Import minimatch for glob pattern matching
import { minimatch } from 'minimatch';

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('[mcp-server-filesystem] Server started');
```

---

## 6. Path Validator

```typescript
// src/middleware/pathValidator.ts
import * as path from 'path';
import { minimatch } from 'minimatch';

export interface PathValidatorConfig {
  allowedPaths: string[];
  blockedPatterns: string[];
}

export class PathValidator {
  private allowedPaths: string[];
  private blockedPatterns: string[];

  constructor(config: PathValidatorConfig) {
    this.allowedPaths = config.allowedPaths.map(p => path.resolve(p));
    this.blockedPatterns = config.blockedPatterns;
  }

  validate(requestedPath: string): string {
    // Resolve to absolute path
    const resolved = path.resolve(requestedPath);

    // Check if path is within allowed directories
    const isAllowed = this.allowedPaths.some(allowed =>
      resolved.startsWith(allowed + path.sep) || resolved === allowed
    );

    if (!isAllowed) {
      throw new Error(
        `Access denied: ${resolved} is outside allowed directories`
      );
    }

    // Check against blocked patterns
    if (this.isBlocked(resolved)) {
      throw new Error(`Access denied: ${resolved} matches blocked pattern`);
    }

    // Block path traversal attempts
    if (requestedPath.includes('..')) {
      throw new Error('Path traversal not allowed');
    }

    return resolved;
  }

  isBlocked(filePath: string): boolean {
    return this.blockedPatterns.some(pattern =>
      minimatch(filePath, pattern, { dot: true })
    );
  }
}
```

---

## 7. Claude Code Configuration

```json
// .claude/.mcp.json
{
  "mcpServers": {
    "[server-name]": {
      "command": "node",
      "args": ["./mcp-server-filesystem/dist/index.js"],
      "env": {
        "ALLOWED_PATHS": "/workspace,/data",
        "BLOCKED_PATTERNS": "**/.env,**/*.key,**/.git/**",
        "ALLOW_WRITE": "false",
        "ALLOW_DELETE": "false",
        "MAX_FILE_SIZE_BYTES": "10485760"
      }
    }
  }
}
```

---

## 8. Security Checklist

```text
[ ] ALLOWED_PATHS configured with minimal necessary access
[ ] BLOCKED_PATTERNS includes sensitive files (.env, *.key, etc.)
[ ] ALLOW_WRITE disabled unless explicitly needed
[ ] ALLOW_DELETE disabled unless explicitly needed
[ ] MAX_FILE_SIZE_BYTES limits memory usage
[ ] MAX_DIRECTORY_DEPTH prevents infinite recursion
[ ] Path traversal blocked (.. detection)
[ ] Symlink following disabled or validated
[ ] Audit logging enabled
[ ] File permissions checked before operations
```

---

## 9. Build and Run

```bash
# Install dependencies
npm install

# Build
npm run build

# Run locally (read-only)
ALLOWED_PATHS="/workspace" npm start

# Run with write access
ALLOWED_PATHS="/workspace" ALLOW_WRITE=true npm start

# Test with Claude Code
claude --mcp-config .claude/.mcp.json
```
