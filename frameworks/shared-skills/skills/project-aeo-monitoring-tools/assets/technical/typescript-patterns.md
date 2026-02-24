# TypeScript Patterns for AEO Monitoring

Architecture patterns and code examples for building AEO monitoring infrastructure with TypeScript/Next.js/Supabase.

## Project Structure

```text
src/
├── app/                      # Next.js App Router
│   ├── api/
│   │   ├── collect/route.ts  # Collection endpoint
│   │   ├── analyze/route.ts  # Analysis endpoint
│   │   └── health/route.ts   # Health check
│   ├── dashboard/page.tsx    # Main dashboard
│   ├── optimize/page.tsx     # Content optimization
│   └── layout.tsx
├── lib/
│   ├── collectors/           # Platform collectors
│   │   ├── types.ts          # Shared interfaces
│   │   ├── perplexity.ts     # Perplexity Sonar
│   │   ├── gemini.ts         # Google Gemini
│   │   ├── claude.ts         # Anthropic Claude
│   │   └── openai.ts         # OpenAI
│   ├── analysis/             # Analysis layer
│   │   ├── citations.ts      # Citation extraction
│   │   ├── brands.ts         # Brand detection
│   │   └── share-of-model.ts # SoM calculation
│   ├── recommendations/      # Content optimization
│   │   └── engine.ts         # Recommendation engine
│   ├── bot-analytics/        # Bot tracking
│   │   └── parser.ts         # Log parser
│   └── db/
│       └── supabase.ts       # Database client
├── components/               # React components
│   ├── dashboard/
│   ├── charts/
│   └── ui/
└── types/                    # Shared types
    └── index.ts
```

## Provider Abstraction Pattern

All collectors implement a common interface for consistent data collection:

```typescript
// src/lib/collectors/types.ts

export interface CollectorConfig {
  apiKey: string;
  rateLimit: { calls: number; periodMs: number };
  timeout: number;
  retries: number;
}

export interface AEOCollector {
  readonly platform: string;
  collect(query: string, options?: CollectOptions): Promise<AEOResponse>;
  extractCitations(response: unknown): Citation[];
  isAvailable(): Promise<boolean>;
  getUsage(): UsageStats;
}

export interface CollectOptions {
  model?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface UsageStats {
  totalCalls: number;
  totalTokens: number;
  estimatedCost: number;
  cacheHits: number;
}
```

## Layered Architecture

```text
┌─────────────────────────────────────────┐
│              API Routes                  │  Next.js endpoints
├─────────────────────────────────────────┤
│           Orchestrator                   │  Coordinates collection
├──────────┬──────────┬──────────┬────────┤
│Perplexity│  Gemini  │  Claude  │ OpenAI │  Platform collectors
├──────────┴──────────┴──────────┴────────┤
│          Analysis Layer                  │  Citations, brands, SoM
├─────────────────────────────────────────┤
│        Recommendation Engine             │  Content optimization
├─────────────────────────────────────────┤
│           Supabase DB                    │  Storage + auth
└─────────────────────────────────────────┘
```

## Error Handling Pattern

```typescript
// Consistent error handling across collectors
export class CollectorError extends Error {
  constructor(
    message: string,
    public platform: string,
    public statusCode?: number,
    public retryable: boolean = false,
  ) {
    super(message);
    this.name = 'CollectorError';
  }
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: { retries: number; backoffMs: number; platform: string }
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= options.retries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      if (error instanceof CollectorError && !error.retryable) {
        throw error;
      }

      if (attempt < options.retries) {
        const delay = options.backoffMs * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
```

## Cost Transparency Pattern

Display real-time cost information to users:

```typescript
// src/lib/collectors/cost-tracker.ts

interface CostEntry {
  platform: string;
  inputTokens: number;
  outputTokens: number;
  cost: number;
  timestamp: Date;
}

const PRICING: Record<string, { input: number; output: number }> = {
  'perplexity:sonar': { input: 1.0, output: 1.0 },      // per 1M tokens
  'gemini:flash': { input: 0.075, output: 0.30 },
  'claude:haiku': { input: 0.25, output: 1.25 },
  'claude:sonnet': { input: 3.0, output: 15.0 },
  'openai:gpt-4o-mini': { input: 0.15, output: 0.60 },
};

export class CostTracker {
  private entries: CostEntry[] = [];

  record(platform: string, model: string, inputTokens: number, outputTokens: number) {
    const key = `${platform}:${model}`;
    const pricing = PRICING[key];

    if (!pricing) return;

    const cost = (inputTokens * pricing.input + outputTokens * pricing.output) / 1_000_000;

    this.entries.push({
      platform,
      inputTokens,
      outputTokens,
      cost,
      timestamp: new Date(),
    });
  }

  getTotalCost(since?: Date): number {
    const filtered = since
      ? this.entries.filter(e => e.timestamp >= since)
      : this.entries;
    return filtered.reduce((sum, e) => sum + e.cost, 0);
  }

  getCostByPlatform(): Record<string, number> {
    return this.entries.reduce((acc, e) => {
      acc[e.platform] = (acc[e.platform] || 0) + e.cost;
      return acc;
    }, {} as Record<string, number>);
  }
}
```

## Database Patterns (Supabase)

```typescript
// src/lib/db/supabase.ts

import { createClient } from '@supabase/supabase-js';
import type { Database } from '@/types/supabase';

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

// Query with type safety
export async function getActiveQueries() {
  const { data, error } = await supabase
    .from('queries')
    .select('*')
    .eq('active', true)
    .order('priority', { ascending: false });

  if (error) throw error;
  return data;
}

// Insert response with citations
export async function storeResponse(response: AEOResponse, queryId: string) {
  const { data: responseRow, error: responseError } = await supabase
    .from('responses')
    .insert({
      query_id: queryId,
      platform: response.platform,
      response_text: response.responseText,
      citations: response.citations,
      model_version: response.modelVersion,
      tokens_used: response.tokensUsed,
      latency_ms: response.latencyMs,
    })
    .select()
    .single();

  if (responseError) throw responseError;

  // Insert normalized citations
  if (response.citations.length > 0) {
    await supabase.from('citations').insert(
      response.citations.map(c => ({
        response_id: responseRow.id,
        url: c.url,
        title: c.title,
        domain: c.domain,
        position: c.position,
        source: c.source,
      }))
    );
  }

  return responseRow;
}
```

## Advanced Feature Patterns

### Bot Analytics

```typescript
// src/lib/bot-analytics/parser.ts

interface BotVisit {
  bot: string;
  path: string;
  timestamp: Date;
  statusCode: number;
  userAgent: string;
}

const AI_BOTS: Record<string, string> = {
  'GPTBot': 'openai',
  'ClaudeBot': 'anthropic',
  'PerplexityBot': 'perplexity',
  'GoogleOther': 'google',
  'Google-Extended': 'google',
  'Bytespider': 'bytedance',
  'CCBot': 'commoncrawl',
};

export function parseAccessLog(line: string): BotVisit | null {
  // Standard Apache/Nginx combined log format
  const match = line.match(
    /(\S+) \S+ \S+ \[(.+?)\] "(\S+) (\S+) \S+" (\d+) \S+ ".*?" "(.+?)"/
  );

  if (!match) return null;

  const [, , timestamp, , path, statusCode, userAgent] = match;

  const botName = Object.keys(AI_BOTS).find(bot => userAgent.includes(bot));
  if (!botName) return null;

  return {
    bot: AI_BOTS[botName],
    path,
    timestamp: new Date(timestamp),
    statusCode: parseInt(statusCode),
    userAgent,
  };
}
```

### Citation Graph

```typescript
// src/lib/analysis/citation-graph.ts

interface CitationNode {
  url: string;
  domain: string;
  citedBy: { platform: string; query: string; date: Date }[];
  coOccurrences: Map<string, number>; // URLs that appear alongside
}

export function buildCitationGraph(responses: AEOResponse[]): Map<string, CitationNode> {
  const graph = new Map<string, CitationNode>();

  for (const response of responses) {
    const urls = response.citations.map(c => c.url);

    for (const citation of response.citations) {
      const node = graph.get(citation.url) || {
        url: citation.url,
        domain: citation.domain,
        citedBy: [],
        coOccurrences: new Map(),
      };

      node.citedBy.push({
        platform: response.platform,
        query: response.query,
        date: response.timestamp,
      });

      // Track co-occurrences
      for (const otherUrl of urls) {
        if (otherUrl !== citation.url) {
          node.coOccurrences.set(
            otherUrl,
            (node.coOccurrences.get(otherUrl) || 0) + 1
          );
        }
      }

      graph.set(citation.url, node);
    }
  }

  return graph;
}
```

### Recommendation Engine

```typescript
// src/lib/recommendations/engine.ts

interface Recommendation {
  type: 'structure' | 'content' | 'entity' | 'freshness';
  priority: 'high' | 'medium' | 'low';
  description: string;
  impact: string;
}

export function analyzePageForOptimization(
  pageContent: string,
  citationData: CitationNode | undefined,
  competitorPages: string[]
): Recommendation[] {
  const recommendations: Recommendation[] = [];

  // Check for TL;DR / answer block
  if (!pageContent.match(/^#{1,2}\s*(tl;?dr|summary|key takeaway)/im)) {
    recommendations.push({
      type: 'structure',
      priority: 'high',
      description: 'Add a TL;DR or summary block in the first screenful',
      impact: 'Improves citation probability by making key points extractable',
    });
  }

  // Check for comparison tables
  if (!pageContent.includes('|') || !pageContent.match(/\|.*\|.*\|/)) {
    recommendations.push({
      type: 'structure',
      priority: 'medium',
      description: 'Add comparison tables for features, pricing, or alternatives',
      impact: 'Tables are frequently extracted by AI for comparison queries',
    });
  }

  // Check for primary source citations
  const urlCount = (pageContent.match(/https?:\/\//g) || []).length;
  if (urlCount < 3) {
    recommendations.push({
      type: 'content',
      priority: 'medium',
      description: 'Add more primary source citations (research, official docs, standards)',
      impact: 'Pages with verifiable sources are cited more often',
    });
  }

  return recommendations;
}
```

## Testing Patterns

```typescript
// __tests__/collectors/perplexity.test.ts

import { PerplexityCollector } from '@/lib/collectors/perplexity';

describe('PerplexityCollector', () => {
  const collector = new PerplexityCollector('test-key');

  it('extracts native citations', () => {
    const mockResponse = {
      citations: ['https://example.com/a', 'https://example.com/b'],
      choices: [{ message: { content: 'Test response' } }],
      model: 'sonar',
    };

    const citations = collector.extractCitations(mockResponse);

    expect(citations).toHaveLength(2);
    expect(citations[0]).toMatchObject({
      url: 'https://example.com/a',
      position: 1,
      source: 'native',
    });
  });
});
```
