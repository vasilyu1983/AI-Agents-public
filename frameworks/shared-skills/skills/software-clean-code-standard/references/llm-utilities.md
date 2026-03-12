# LLM Utilities

Centralized patterns for token counting, streaming responses, cost estimation, and rate limiting.

**Updated**: January 2026
**Node.js**: 24 LTS | **Python**: 3.14+ | **TypeScript**: 5.7+

---

## File Structure

```text
src/
└── llm/
    ├── client.ts         # LLM client wrapper
    ├── tokens.ts         # Token counting/estimation
    ├── streaming.ts      # Stream handling
    └── costs.ts          # Cost calculation
```

---

## TypeScript/Node.js

### Dependencies

```bash
npm install @anthropic-ai/sdk@^0.35 openai@^4.75 tiktoken@^1.0
```

### Token Counting (`src/llm/tokens.ts`)

```typescript
import { Tiktoken, encodingForModel } from 'tiktoken';

// ============================================
// TOKEN COUNTING
// ============================================

// Cache encoders by model
const encoderCache = new Map<string, Tiktoken>();

const getEncoder = (model: string): Tiktoken => {
  // Map model names to tiktoken models
  const tiktokenModel = model.startsWith('gpt-4')
    ? 'gpt-4'
    : model.startsWith('gpt-3.5')
    ? 'gpt-3.5-turbo'
    : 'cl100k_base'; // Default for Claude, etc.

  if (!encoderCache.has(tiktokenModel)) {
    try {
      encoderCache.set(tiktokenModel, encodingForModel(tiktokenModel as any));
    } catch {
      // Fallback to cl100k_base
      encoderCache.set(tiktokenModel, encodingForModel('cl100k_base' as any));
    }
  }

  return encoderCache.get(tiktokenModel)!;
};

export const countTokens = (text: string, model = 'gpt-4'): number => {
  const encoder = getEncoder(model);
  return encoder.encode(text).length;
};

export const countMessageTokens = (
  messages: Array<{ role: string; content: string }>,
  model = 'gpt-4'
): number => {
  const encoder = getEncoder(model);
  let tokens = 0;

  for (const message of messages) {
    // Message overhead (role, separators)
    tokens += 4;
    tokens += encoder.encode(message.content).length;
    tokens += encoder.encode(message.role).length;
  }

  // Reply priming
  tokens += 2;

  return tokens;
};

// Estimate tokens for Claude (approximate - Claude uses different tokenizer)
export const estimateClaudeTokens = (text: string): number => {
  // Claude averages ~4 characters per token
  return Math.ceil(text.length / 4);
};

// Check if content fits in context window
export const fitsInContext = (
  tokens: number,
  model: string,
  reserveForResponse = 4096
): boolean => {
  const contextLimits: Record<string, number> = {
    'gpt-4': 8192,
    'gpt-4-turbo': 128000,
    'gpt-4o': 128000,
    'gpt-4o-mini': 128000,
    'gpt-3.5-turbo': 16385,
    'claude-3-opus': 200000,
    'claude-3-sonnet': 200000,
    'claude-3-haiku': 200000,
    'claude-3.5-sonnet': 200000,
    'claude-3.5-haiku': 200000,
  };

  const limit = contextLimits[model] || 8192;
  return tokens + reserveForResponse <= limit;
};
```

### Cost Estimation (`src/llm/costs.ts`)

```typescript
// ============================================
// COST CALCULATION (EXAMPLE PRICING - VERIFY CURRENT RATES)
// ============================================
//
// BEST PRACTICE (2026):
// - Do not hardcode provider pricing in application code.
// - Load pricing from config (env, remote config, or a periodically-updated JSON file).
// - Treat model names/context limits as data that changes over time.

interface ModelPricing {
  inputPer1M: number;   // $ per 1M input tokens
  outputPer1M: number;  // $ per 1M output tokens
  cachedInputPer1M?: number; // $ per 1M cached input tokens
}

// Example pricing table (VERIFY CURRENT RATES before using in production).
const PRICING: Record<string, ModelPricing> = {
  // OpenAI
  'gpt-4o': { inputPer1M: 2.50, outputPer1M: 10.00 },
  'gpt-4o-mini': { inputPer1M: 0.15, outputPer1M: 0.60 },
  'gpt-4-turbo': { inputPer1M: 10.00, outputPer1M: 30.00 },
  'gpt-3.5-turbo': { inputPer1M: 0.50, outputPer1M: 1.50 },

  // Anthropic
  'claude-3-opus': { inputPer1M: 15.00, outputPer1M: 75.00 },
  'claude-3-sonnet': { inputPer1M: 3.00, outputPer1M: 15.00 },
  'claude-3-haiku': { inputPer1M: 0.25, outputPer1M: 1.25 },
  'claude-3.5-sonnet': { inputPer1M: 3.00, outputPer1M: 15.00 },
  'claude-3.5-haiku': { inputPer1M: 0.80, outputPer1M: 4.00 },

  // With prompt caching
  'claude-3.5-sonnet-cached': {
    inputPer1M: 3.00,
    outputPer1M: 15.00,
    cachedInputPer1M: 0.30, // 90% discount
  },
};

export interface CostEstimate {
  inputCost: number;
  outputCost: number;
  totalCost: number;
  inputTokens: number;
  outputTokens: number;
}

export const estimateCost = (
  model: string,
  inputTokens: number,
  outputTokens: number,
  cachedInputTokens = 0
): CostEstimate => {
  const pricing = PRICING[model] || PRICING['gpt-4o'];

  const regularInputTokens = inputTokens - cachedInputTokens;
  const inputCost =
    (regularInputTokens / 1_000_000) * pricing.inputPer1M +
    (cachedInputTokens / 1_000_000) * (pricing.cachedInputPer1M || pricing.inputPer1M);

  const outputCost = (outputTokens / 1_000_000) * pricing.outputPer1M;

  return {
    inputCost,
    outputCost,
    totalCost: inputCost + outputCost,
    inputTokens,
    outputTokens,
  };
};

export const formatCost = (cost: number): string => {
  if (cost < 0.01) {
    return `$${(cost * 100).toFixed(3)}¢`;
  }
  return `$${cost.toFixed(4)}`;
};

// Monthly cost projection
export const projectMonthlyCost = (
  costPerRequest: number,
  requestsPerDay: number
): number => {
  return costPerRequest * requestsPerDay * 30;
};
```

### Streaming Handler (`src/llm/streaming.ts`)

```typescript
import Anthropic from '@anthropic-ai/sdk';
import OpenAI from 'openai';

// ============================================
// STREAMING UTILITIES
// ============================================

export interface StreamChunk {
  type: 'text' | 'tool_use' | 'stop';
  content?: string;
  toolCall?: {
    id: string;
    name: string;
    input: unknown;
  };
}

export type StreamCallback = (chunk: StreamChunk) => void;

// Stream text chunks with callback
export const streamWithCallback = async (
  stream: AsyncIterable<unknown>,
  onChunk: StreamCallback
): Promise<string> => {
  let fullText = '';

  for await (const event of stream) {
    // Handle Anthropic events
    if ('type' in (event as any)) {
      const anthropicEvent = event as Anthropic.MessageStreamEvent;

      if (anthropicEvent.type === 'content_block_delta') {
        const delta = anthropicEvent.delta as any;
        if (delta.type === 'text_delta') {
          fullText += delta.text;
          onChunk({ type: 'text', content: delta.text });
        }
      }

      if (anthropicEvent.type === 'message_stop') {
        onChunk({ type: 'stop' });
      }
    }

    // Handle OpenAI events
    if ('choices' in (event as any)) {
      const openaiEvent = event as OpenAI.ChatCompletionChunk;
      const delta = openaiEvent.choices[0]?.delta;

      if (delta?.content) {
        fullText += delta.content;
        onChunk({ type: 'text', content: delta.content });
      }

      if (openaiEvent.choices[0]?.finish_reason === 'stop') {
        onChunk({ type: 'stop' });
      }
    }
  }

  return fullText;
};

// Convert stream to async generator
export async function* streamToGenerator(
  stream: AsyncIterable<unknown>
): AsyncGenerator<string> {
  for await (const event of stream) {
    if ('type' in (event as any)) {
      const anthropicEvent = event as Anthropic.MessageStreamEvent;
      if (anthropicEvent.type === 'content_block_delta') {
        const delta = anthropicEvent.delta as any;
        if (delta.type === 'text_delta') {
          yield delta.text;
        }
      }
    }

    if ('choices' in (event as any)) {
      const openaiEvent = event as OpenAI.ChatCompletionChunk;
      if (openaiEvent.choices[0]?.delta?.content) {
        yield openaiEvent.choices[0].delta.content;
      }
    }
  }
}

// Collect stream to string
export const collectStream = async (
  stream: AsyncIterable<unknown>
): Promise<string> => {
  let result = '';
  for await (const chunk of streamToGenerator(stream)) {
    result += chunk;
  }
  return result;
};
```

### LLM Client Wrapper (`src/llm/client.ts`)

```typescript
import Anthropic from '@anthropic-ai/sdk';
import OpenAI from 'openai';
import { countMessageTokens, estimateClaudeTokens } from './tokens';
import { estimateCost, type CostEstimate } from './costs';
import { streamWithCallback, type StreamCallback } from './streaming';

// ============================================
// UNIFIED LLM CLIENT
// ============================================

export interface LLMMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface LLMOptions {
  model: string;
  maxTokens?: number;
  temperature?: number;
  stream?: boolean;
  onChunk?: StreamCallback;
}

export interface LLMResponse {
  content: string;
  usage: {
    inputTokens: number;
    outputTokens: number;
  };
  cost: CostEstimate;
  model: string;
}

export class LLMClient {
  private anthropic?: Anthropic;
  private openai?: OpenAI;

  constructor() {
    if (process.env.ANTHROPIC_API_KEY) {
      this.anthropic = new Anthropic();
    }
    if (process.env.OPENAI_API_KEY) {
      this.openai = new OpenAI();
    }
  }

  async chat(messages: LLMMessage[], options: LLMOptions): Promise<LLMResponse> {
    const isAnthropic = options.model.startsWith('claude');

    if (isAnthropic) {
      return this.chatAnthropic(messages, options);
    }
    return this.chatOpenAI(messages, options);
  }

  private async chatAnthropic(
    messages: LLMMessage[],
    options: LLMOptions
  ): Promise<LLMResponse> {
    if (!this.anthropic) {
      throw new Error('Anthropic client not initialized');
    }

    // Extract system message
    const systemMessage = messages.find((m) => m.role === 'system')?.content;
    const chatMessages = messages
      .filter((m) => m.role !== 'system')
      .map((m) => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }));

    if (options.stream && options.onChunk) {
      const stream = await this.anthropic.messages.stream({
        model: options.model,
        max_tokens: options.maxTokens || 4096,
        temperature: options.temperature,
        system: systemMessage,
        messages: chatMessages,
      });

      const content = await streamWithCallback(stream, options.onChunk);
      const finalMessage = await stream.finalMessage();

      return {
        content,
        usage: {
          inputTokens: finalMessage.usage.input_tokens,
          outputTokens: finalMessage.usage.output_tokens,
        },
        cost: estimateCost(
          options.model,
          finalMessage.usage.input_tokens,
          finalMessage.usage.output_tokens
        ),
        model: options.model,
      };
    }

    const response = await this.anthropic.messages.create({
      model: options.model,
      max_tokens: options.maxTokens || 4096,
      temperature: options.temperature,
      system: systemMessage,
      messages: chatMessages,
    });

    const content = response.content
      .filter((block) => block.type === 'text')
      .map((block) => (block as any).text)
      .join('');

    return {
      content,
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
      },
      cost: estimateCost(
        options.model,
        response.usage.input_tokens,
        response.usage.output_tokens
      ),
      model: options.model,
    };
  }

  private async chatOpenAI(
    messages: LLMMessage[],
    options: LLMOptions
  ): Promise<LLMResponse> {
    if (!this.openai) {
      throw new Error('OpenAI client not initialized');
    }

    if (options.stream && options.onChunk) {
      const stream = await this.openai.chat.completions.create({
        model: options.model,
        max_tokens: options.maxTokens || 4096,
        temperature: options.temperature,
        messages: messages.map((m) => ({
          role: m.role,
          content: m.content,
        })),
        stream: true,
        stream_options: { include_usage: true },
      });

      const content = await streamWithCallback(stream, options.onChunk);

      // Get usage from final chunk
      let inputTokens = 0;
      let outputTokens = 0;
      for await (const chunk of stream) {
        if (chunk.usage) {
          inputTokens = chunk.usage.prompt_tokens;
          outputTokens = chunk.usage.completion_tokens;
        }
      }

      return {
        content,
        usage: { inputTokens, outputTokens },
        cost: estimateCost(options.model, inputTokens, outputTokens),
        model: options.model,
      };
    }

    const response = await this.openai.chat.completions.create({
      model: options.model,
      max_tokens: options.maxTokens || 4096,
      temperature: options.temperature,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });

    return {
      content: response.choices[0]?.message?.content || '',
      usage: {
        inputTokens: response.usage?.prompt_tokens || 0,
        outputTokens: response.usage?.completion_tokens || 0,
      },
      cost: estimateCost(
        options.model,
        response.usage?.prompt_tokens || 0,
        response.usage?.completion_tokens || 0
      ),
      model: options.model,
    };
  }
}

// Singleton instance
export const llm = new LLMClient();
```

### Usage

```typescript
import { llm } from '@/llm/client';
import { countTokens, fitsInContext } from '@/llm/tokens';
import { estimateCost, formatCost } from '@/llm/costs';

// Count tokens before sending
const inputTokens = countTokens(userMessage);
if (!fitsInContext(inputTokens, 'claude-3.5-sonnet')) {
  throw new Error('Message too long');
}

// Estimate cost
const estimate = estimateCost('claude-3.5-sonnet', 1000, 500);
console.log(`Estimated cost: ${formatCost(estimate.totalCost)}`);

// Chat with streaming
const response = await llm.chat(
  [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Hello!' },
  ],
  {
    model: 'claude-3.5-sonnet',
    stream: true,
    onChunk: (chunk) => {
      if (chunk.type === 'text') {
        process.stdout.write(chunk.content || '');
      }
    },
  }
);

console.log(`\nTokens: ${response.usage.inputTokens}/${response.usage.outputTokens}`);
console.log(`Cost: ${formatCost(response.cost.totalCost)}`);
```

---

## Python

### Dependencies

```bash
pip install anthropic>=0.40 openai>=1.58 tiktoken>=0.8
```

### Token Counting (`src/llm/tokens.py`)

```python
import tiktoken


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens for OpenAI models."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def estimate_claude_tokens(text: str) -> int:
    """Estimate tokens for Claude (approximate)."""
    return len(text) // 4


def count_message_tokens(
    messages: list[dict[str, str]], model: str = "gpt-4"
) -> int:
    """Count tokens for chat messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = 0
    for message in messages:
        tokens += 4  # Message overhead
        tokens += len(encoding.encode(message["content"]))
        tokens += len(encoding.encode(message["role"]))
    tokens += 2  # Reply priming

    return tokens


CONTEXT_LIMITS = {
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "claude-3.5-sonnet": 200000,
    "claude-3.5-haiku": 200000,
}


def fits_in_context(
    tokens: int, model: str, reserve_for_response: int = 4096
) -> bool:
    """Check if content fits in context window."""
    limit = CONTEXT_LIMITS.get(model, 8192)
    return tokens + reserve_for_response <= limit
```

### Cost Estimation (`src/llm/costs.py`)

```python
from dataclasses import dataclass


@dataclass
class CostEstimate:
    input_cost: float
    output_cost: float
    total_cost: float
    input_tokens: int
    output_tokens: int


# Example pricing table ($ per 1M tokens). VERIFY CURRENT RATES before using in production.
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3.5-haiku": {"input": 0.80, "output": 4.00},
}


def estimate_cost(
    model: str, input_tokens: int, output_tokens: int
) -> CostEstimate:
    """Calculate cost for API call."""
    pricing = PRICING.get(model, PRICING["gpt-4o"])

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return CostEstimate(
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=input_cost + output_cost,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def format_cost(cost: float) -> str:
    """Format cost for display."""
    if cost < 0.01:
        return f"${cost * 100:.3f}¢"
    return f"${cost:.4f}"
```

### Streaming Handler (`src/llm/streaming.py`)

```python
from collections.abc import AsyncIterator
from typing import Any

import anthropic
import openai


async def stream_anthropic(
    stream: anthropic.AsyncStream,
) -> AsyncIterator[str]:
    """Yield text chunks from Anthropic stream."""
    async for event in stream:
        if event.type == "content_block_delta":
            if hasattr(event.delta, "text"):
                yield event.delta.text


async def stream_openai(
    stream: openai.AsyncStream,
) -> AsyncIterator[str]:
    """Yield text chunks from OpenAI stream."""
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def collect_stream(stream: AsyncIterator[str]) -> str:
    """Collect stream into single string."""
    result = ""
    async for chunk in stream:
        result += chunk
    return result
```

### Usage

```python
from src.llm.tokens import count_tokens, fits_in_context
from src.llm.costs import estimate_cost, format_cost

# Count tokens
tokens = count_tokens(user_message)
if not fits_in_context(tokens, "claude-3.5-sonnet"):
    raise ValueError("Message too long")

# Estimate cost
cost = estimate_cost("claude-3.5-sonnet", 1000, 500)
print(f"Estimated cost: {format_cost(cost.total_cost)}")
```

---

## Rate Limiting

```typescript
// Token bucket rate limiter for API calls
export class LLMRateLimiter {
  private tokens: number;
  private lastRefill: number;
  private readonly maxTokens: number;
  private readonly refillRate: number; // tokens per second

  constructor(maxTokens: number, refillRate: number) {
    this.maxTokens = maxTokens;
    this.tokens = maxTokens;
    this.refillRate = refillRate;
    this.lastRefill = Date.now();
  }

  async acquire(tokensNeeded = 1): Promise<void> {
    this.refill();

    while (this.tokens < tokensNeeded) {
      const waitTime = ((tokensNeeded - this.tokens) / this.refillRate) * 1000;
      await new Promise((r) => setTimeout(r, waitTime));
      this.refill();
    }

    this.tokens -= tokensNeeded;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.maxTokens, this.tokens + elapsed * this.refillRate);
    this.lastRefill = now;
  }
}

// Usage
const rateLimiter = new LLMRateLimiter(60, 1); // 60 requests/minute
await rateLimiter.acquire();
const response = await llm.chat(messages, options);
```

---

## References

- [Anthropic SDK](https://docs.anthropic.com/en/api/client-sdks)
- [OpenAI SDK](https://platform.openai.com/docs/libraries)
- [tiktoken](https://github.com/openai/tiktoken)
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [OpenAI Pricing](https://openai.com/pricing)
