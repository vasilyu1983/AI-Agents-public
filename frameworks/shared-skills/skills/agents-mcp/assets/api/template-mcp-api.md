# MCP API Integration Template

*Purpose: Production-ready MCP server for REST/GraphQL API integration with Claude Code.*

---

## When to Use

Use this template when building:

- REST API clients for Claude
- GraphQL integration servers
- Third-party service connectors (Stripe, Twilio, etc.)
- Internal API gateways
- Webhook handlers

---

# TEMPLATE STARTS HERE

## 1. Project Overview

**Project Name:**
[mcp-server-api]

**Description:**
[MCP server providing API integration for Claude Code]

**API Type:**
- [ ] REST API
- [ ] GraphQL API
- [ ] Multiple APIs

**Authentication:**
- [ ] API Key
- [ ] OAuth 2.0
- [ ] JWT
- [ ] Basic Auth

---

## 2. Project Structure

```
mcp-server-api/
  src/
    index.ts              # Server entry point
    config.ts             # Configuration
    clients/
      http.ts             # HTTP client with retry
      graphql.ts          # GraphQL client
    tools/
      get.ts              # GET requests
      post.ts             # POST requests
      graphql.ts          # GraphQL queries
    middleware/
      auth.ts             # Authentication
      retry.ts            # Retry logic
      rateLimit.ts        # Rate limiting
    types/
      api.ts              # Type definitions
  tests/
    tools.test.ts
  package.json
  tsconfig.json
  .env.example
  Dockerfile
```

---

## 3. Package Configuration

```json
{
  "name": "[mcp-server-api]",
  "version": "1.0.0",
  "description": "[MCP server for API integration]",
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
    "winston": "^3.11.0"
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

# API Configuration
API_BASE_URL=https://api.[service].com
API_VERSION=v1

# Authentication
API_KEY=[your-api-key]
# OR for OAuth
OAUTH_CLIENT_ID=[client-id]
OAUTH_CLIENT_SECRET=[client-secret]
OAUTH_TOKEN_URL=https://auth.[service].com/token

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_MS=60000

# Retry Configuration
MAX_RETRIES=3
RETRY_BASE_DELAY_MS=1000
RETRY_MAX_DELAY_MS=10000

# Allowed Endpoints (security)
ALLOWED_ENDPOINTS=/users,/products,/orders

# Logging
LOG_LEVEL=info
LOG_REQUESTS=true
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
} from '@modelcontextprotocol/sdk/types.js';
import { config } from './config.js';
import { HttpClient } from './clients/http.js';
import { createLogger } from './middleware/logger.js';

const httpClient = new HttpClient(config);
const logger = createLogger(config.logLevel);

const server = new Server(
  {
    name: '[mcp-server-api]',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'api_get',
      description: 'Make a GET request to the API',
      inputSchema: {
        type: 'object',
        properties: {
          endpoint: {
            type: 'string',
            description: 'API endpoint path (e.g., /users/123)',
          },
          query: {
            type: 'object',
            description: 'Query parameters',
            additionalProperties: { type: 'string' },
          },
        },
        required: ['endpoint'],
      },
    },
    {
      name: 'api_post',
      description: 'Make a POST request to the API',
      inputSchema: {
        type: 'object',
        properties: {
          endpoint: {
            type: 'string',
            description: 'API endpoint path',
          },
          body: {
            type: 'object',
            description: 'Request body',
          },
        },
        required: ['endpoint', 'body'],
      },
    },
    {
      name: 'api_put',
      description: 'Make a PUT request to the API',
      inputSchema: {
        type: 'object',
        properties: {
          endpoint: {
            type: 'string',
            description: 'API endpoint path',
          },
          body: {
            type: 'object',
            description: 'Request body',
          },
        },
        required: ['endpoint', 'body'],
      },
    },
    {
      name: 'api_delete',
      description: 'Make a DELETE request to the API',
      inputSchema: {
        type: 'object',
        properties: {
          endpoint: {
            type: 'string',
            description: 'API endpoint path',
          },
        },
        required: ['endpoint'],
      },
    },
    {
      name: 'list_endpoints',
      description: 'List available API endpoints',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
  ],
}));

// Implement tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  logger.info('Tool call', { tool: name, args });

  try {
    switch (name) {
      case 'api_get': {
        const endpoint = args?.endpoint as string;
        const query = args?.query as Record<string, string> | undefined;

        validateEndpoint(endpoint);

        const response = await httpClient.get(endpoint, query);
        return formatResponse(response);
      }

      case 'api_post': {
        const endpoint = args?.endpoint as string;
        const body = args?.body as Record<string, unknown>;

        validateEndpoint(endpoint);

        const response = await httpClient.post(endpoint, body);
        return formatResponse(response);
      }

      case 'api_put': {
        const endpoint = args?.endpoint as string;
        const body = args?.body as Record<string, unknown>;

        validateEndpoint(endpoint);

        const response = await httpClient.put(endpoint, body);
        return formatResponse(response);
      }

      case 'api_delete': {
        const endpoint = args?.endpoint as string;

        validateEndpoint(endpoint);

        const response = await httpClient.delete(endpoint);
        return formatResponse(response);
      }

      case 'list_endpoints': {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              baseUrl: config.apiBaseUrl,
              version: config.apiVersion,
              allowedEndpoints: config.allowedEndpoints,
            }, null, 2),
          }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    logger.error('Tool error', { tool: name, error: (error as Error).message });
    throw error;
  }
});

function validateEndpoint(endpoint: string): void {
  // Validate endpoint format
  if (!endpoint.startsWith('/')) {
    throw new Error('Endpoint must start with /');
  }

  // Check against allowlist
  const baseEndpoint = '/' + endpoint.split('/')[1];
  if (!config.allowedEndpoints.includes(baseEndpoint)) {
    throw new Error(`Endpoint not allowed: ${baseEndpoint}. Allowed: ${config.allowedEndpoints.join(', ')}`);
  }

  // Block path traversal
  if (endpoint.includes('..')) {
    throw new Error('Path traversal not allowed');
  }
}

function formatResponse(data: unknown) {
  return {
    content: [{
      type: 'text',
      text: JSON.stringify(data, null, 2),
    }],
  };
}

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('[mcp-server-api] Server started');
```

---

## 6. HTTP Client with Retry

```typescript
// src/clients/http.ts
import { setTimeout } from 'timers/promises';
import { Config } from './config.js';

interface RetryConfig {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
}

export class HttpClient {
  private baseUrl: string;
  private headers: Record<string, string>;
  private retryConfig: RetryConfig;

  constructor(config: Config) {
    this.baseUrl = `${config.apiBaseUrl}/${config.apiVersion}`;
    this.headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.apiKey}`,
    };
    this.retryConfig = {
      maxRetries: config.maxRetries,
      baseDelayMs: config.retryBaseDelay,
      maxDelayMs: config.retryMaxDelay,
    };
  }

  async get(endpoint: string, query?: Record<string, string>): Promise<unknown> {
    const url = new URL(this.baseUrl + endpoint);
    if (query) {
      Object.entries(query).forEach(([k, v]) => url.searchParams.set(k, v));
    }
    return this.fetchWithRetry(url.toString(), { method: 'GET' });
  }

  async post(endpoint: string, body: unknown): Promise<unknown> {
    return this.fetchWithRetry(this.baseUrl + endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async put(endpoint: string, body: unknown): Promise<unknown> {
    return this.fetchWithRetry(this.baseUrl + endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  async delete(endpoint: string): Promise<unknown> {
    return this.fetchWithRetry(this.baseUrl + endpoint, {
      method: 'DELETE',
    });
  }

  private async fetchWithRetry(
    url: string,
    options: RequestInit
  ): Promise<unknown> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        const response = await fetch(url, {
          ...options,
          headers: this.headers,
        });

        // Handle rate limiting
        if (response.status === 429) {
          const retryAfter = response.headers.get('retry-after');
          const delay = retryAfter
            ? parseInt(retryAfter) * 1000
            : this.calculateDelay(attempt);
          await setTimeout(delay);
          continue;
        }

        // Handle server errors with retry
        if (response.status >= 500) {
          throw new Error(`Server error: ${response.status}`);
        }

        // Handle client errors without retry
        if (!response.ok) {
          const errorBody = await response.text();
          throw new Error(`API error ${response.status}: ${errorBody}`);
        }

        return await response.json();
      } catch (error) {
        lastError = error as Error;

        // Don't retry client errors (4xx except 429)
        if (lastError.message.includes('API error 4')) {
          throw lastError;
        }

        if (attempt < this.retryConfig.maxRetries) {
          const delay = this.calculateDelay(attempt);
          await setTimeout(delay);
        }
      }
    }

    throw lastError || new Error('Request failed after retries');
  }

  private calculateDelay(attempt: number): number {
    const delay = this.retryConfig.baseDelayMs * Math.pow(2, attempt);
    const jitter = Math.random() * 0.1 * delay;
    return Math.min(delay + jitter, this.retryConfig.maxDelayMs);
  }
}
```

---

## 7. OAuth 2.0 Support (Optional)

```typescript
// src/middleware/auth.ts
interface TokenResponse {
  access_token: string;
  expires_in: number;
  token_type: string;
}

export class OAuthClient {
  private clientId: string;
  private clientSecret: string;
  private tokenUrl: string;
  private accessToken: string | null = null;
  private tokenExpiry: number = 0;

  constructor(clientId: string, clientSecret: string, tokenUrl: string) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.tokenUrl = tokenUrl;
  }

  async getAccessToken(): Promise<string> {
    // Return cached token if valid
    if (this.accessToken && Date.now() < this.tokenExpiry - 60000) {
      return this.accessToken;
    }

    // Fetch new token
    const response = await fetch(this.tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
    });

    if (!response.ok) {
      throw new Error(`OAuth token request failed: ${response.status}`);
    }

    const data: TokenResponse = await response.json();
    this.accessToken = data.access_token;
    this.tokenExpiry = Date.now() + data.expires_in * 1000;

    return this.accessToken;
  }
}
```

---

## 8. GraphQL Support (Optional)

```typescript
// src/clients/graphql.ts
export class GraphQLClient {
  private endpoint: string;
  private headers: Record<string, string>;

  constructor(endpoint: string, apiKey: string) {
    this.endpoint = endpoint;
    this.headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    };
  }

  async query<T = unknown>(
    query: string,
    variables?: Record<string, unknown>
  ): Promise<T> {
    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ query, variables }),
    });

    if (!response.ok) {
      throw new Error(`GraphQL request failed: ${response.status}`);
    }

    const result = await response.json();

    if (result.errors) {
      throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
    }

    return result.data;
  }
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
      "args": ["./mcp-server-api/dist/index.js"],
      "env": {
        "API_BASE_URL": "https://api.example.com",
        "API_VERSION": "v1",
        "API_KEY": "${API_KEY}",
        "ALLOWED_ENDPOINTS": "/users,/products,/orders"
      }
    }
  }
}
```

---

## 10. Security Checklist

```text
[ ] API keys stored in environment variables only
[ ] HTTPS enforced for all API calls
[ ] Endpoint allowlist configured (ALLOWED_ENDPOINTS)
[ ] Rate limiting configured
[ ] Request/response logging enabled
[ ] OAuth tokens refreshed before expiry
[ ] Sensitive data not logged
[ ] Error messages don't expose internal details
[ ] Path traversal blocked in endpoints
[ ] Request timeout configured
```

---

## 11. Build and Run

```bash
# Install dependencies
npm install

# Build
npm run build

# Run locally
API_BASE_URL="https://api.example.com" \
API_KEY="your-key" \
ALLOWED_ENDPOINTS="/users,/products" \
npm start

# Test with Claude Code
claude --mcp-config .claude/.mcp.json
```
