# Streaming Patterns

> Operational reference for LLM response streaming — SSE and WebSocket delivery, token-by-token rendering, backpressure handling, partial response recovery, function calling with streaming, and load balancer configuration.

**Freshness anchor:** January 2026 — covers OpenAI streaming (SSE), Anthropic streaming (SSE), Gemini streaming, Vercel AI SDK 4.x, LangChain streaming, and NGINX/Cloudflare streaming proxy configuration.

---

## Streaming Protocol Decision Tree

```
Need to stream LLM responses
│
├── Client type?
│   ├── Web browser
│   │   ├── Simple text streaming → Server-Sent Events (SSE)
│   │   ├── Bidirectional communication → WebSocket
│   │   └── React/Next.js app → Vercel AI SDK (SSE under the hood)
│   │
│   ├── Mobile app
│   │   ├── iOS/Android native → SSE or WebSocket
│   │   ├── React Native → SSE via fetch or WebSocket
│   │   └── Flutter → WebSocket (better library support)
│   │
│   ├── Server-to-server
│   │   ├── Simple forwarding → SSE passthrough
│   │   ├── Processing stream → Async iterator
│   │   └── Fan-out to multiple clients → WebSocket pub/sub
│   │
│   └── CLI / terminal
│       ├── Direct stdout → Async iterator, print token by token
│       └── TUI framework → Event-based stream consumption
│
├── Need bidirectional?
│   ├── YES → WebSocket (user can send while receiving)
│   └── NO → SSE (simpler, auto-reconnect, HTTP/2 multiplexing)
│
└── Need to stream tool calls?
    ├── YES → Provider-specific streaming events
    └── NO → Standard text delta streaming
```

---

## SSE (Server-Sent Events) Implementation

### Server-Side (Python/FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import json

app = FastAPI()
client = AsyncOpenAI()

@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    async def generate():
        stream = await client.chat.completions.create(
            model="gpt-4o",
            messages=request.messages,
            stream=True
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield f"data: {json.dumps({'content': delta.content})}\n\n"

            # Handle tool calls in stream
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    yield f"data: {json.dumps({'tool_call': {
                        'id': tool_call.id,
                        'function': tool_call.function.name,
                        'arguments': tool_call.function.arguments
                    }})}\n\n"

            if chunk.choices[0].finish_reason:
                yield f"data: {json.dumps({'done': True, 'reason': chunk.choices[0].finish_reason})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable NGINX buffering
        }
    )
```

### Client-Side (JavaScript)

```javascript
async function streamChat(messages) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const data = line.slice(6);
      if (data === '[DONE]') return;
      const parsed = JSON.parse(data);
      if (parsed.content) appendToUI(parsed.content);
    }
  }
}
```

---

## WebSocket Streaming

### Use When
- Bidirectional communication needed (user types while receiving)
- Voice agents (audio in + text/audio out simultaneously)
- Need to cancel/interrupt generation mid-stream

### WebSocket vs SSE Comparison

| Feature | SSE | WebSocket |
|---|---|---|
| Direction | Server→client only | Bidirectional |
| Cancel mid-stream | Close connection | Send cancel message |
| Auto-reconnect | Built-in | Manual implementation |
| HTTP/2 multiplexing | Yes | No |
| Protocol overhead | Lower | Higher |
| Best for | Standard chat streaming | Voice, real-time collab |

---

## Backpressure Handling

### Problem: Client Cannot Consume Tokens as Fast as They Arrive

| Scenario | Symptom | Solution |
|---|---|---|
| Slow client connection | Server memory grows, eventual OOM | Buffer with size limit + drop |
| Client doing heavy DOM updates | UI freezes, batch arrives at once | RequestAnimationFrame batching |
| Multiple concurrent streams | Memory pressure | Limit concurrent streams per client |
| Large tool call arguments | Single massive chunk | Chunk large arguments |

### Backpressure Solutions

| Strategy | Server/Client | Implementation |
|---|---|---|
| Bounded queue | Server | `asyncio.Queue(maxsize=100)` — drop oldest on overflow |
| RAF batching | Client (React) | Buffer tokens, flush via `requestAnimationFrame` |
| Concurrent stream limit | Server | Max 5 concurrent streams per client |
| Chunk large payloads | Server | Split tool call args into smaller events |

---

## Partial Response Recovery

### Mid-Stream Error Handling

```python
class ResilientStream:
    """Handle errors during streaming with partial response recovery."""

    async def stream_with_recovery(self, messages, max_retries=2):
        accumulated_text = ""
        retry_count = 0

        while retry_count <= max_retries:
            try:
                stream = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    stream=True
                )

                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        accumulated_text += token
                        yield {"type": "delta", "content": token}

                    if chunk.choices[0].finish_reason:
                        yield {"type": "done", "full_text": accumulated_text}
                        return

            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    yield {
                        "type": "error",
                        "partial_text": accumulated_text,
                        "error": str(e)
                    }
                    return

                # Resume from where we left off
                yield {"type": "retry", "attempt": retry_count}

                # Add partial response as context for continuation
                if accumulated_text:
                    messages = messages + [
                        {"role": "assistant", "content": accumulated_text},
                        {"role": "user", "content": "Continue from where you left off."}
                    ]
```

### Partial JSON Recovery

- Use incremental JSON parser that tracks bracket depth and string state
- Feed tokens as they arrive, emit complete objects when depth returns to 0
- Libraries: `ijson` (Python), `clarinet` (Node.js)
- For structured output streams: accumulate full response, parse at `finish_reason`

---

## Streaming with Function Calling

### Provider-Specific Streaming Events

| Provider | Tool Call Start Event | Tool Call Argument Chunks | Tool Call Complete |
|---|---|---|---|
| OpenAI | `delta.tool_calls[i].id` + `function.name` | `delta.tool_calls[i].function.arguments` (chunks) | `finish_reason: "tool_calls"` |
| Anthropic | `content_block_start` type `tool_use` | `content_block_delta` with `partial_json` | `content_block_stop` |
| Gemini | `functionCall` in parts | Not chunked (full at once) | Part complete |

### Tool Call Accumulation Pattern

- Maintain a dict of in-progress tool calls indexed by `tool_calls[i].index`
- Concatenate `function.arguments` chunks as strings
- On `finish_reason: "tool_calls"`, parse accumulated JSON and dispatch
- For Anthropic: listen for `content_block_start` (tool_use type), accumulate `content_block_delta`, parse on `content_block_stop`
- Always validate the accumulated JSON before executing the tool call

---

## Load Balancer Configuration for Streaming

### NGINX Configuration

```nginx
# /etc/nginx/conf.d/llm-streaming.conf

upstream llm_backend {
    server backend1:8000;
    server backend2:8000;
    keepalive 32;
}

server {
    listen 443 ssl http2;

    location /api/chat/stream {
        proxy_pass http://llm_backend;

        # Critical for SSE streaming
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;

        # Timeouts for long-running streams
        proxy_read_timeout 300s;  # 5 minutes max stream
        proxy_send_timeout 300s;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Accel-Buffering no;

        # SSE-specific
        add_header Content-Type text/event-stream;
        add_header Cache-Control no-cache;
    }

    location /ws/chat {
        proxy_pass http://llm_backend;

        # WebSocket upgrade
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
    }
}
```

### Other Load Balancer Notes

| Platform | Key Setting |
|---|---|
| Cloudflare | Disable Rocket Loader + Auto Minify; Response Buffering OFF; Free/Pro 100s timeout |
| AWS ALB | Idle timeout 300s; HTTP/2 enabled; sticky sessions for WebSocket |
| GCP Cloud Run | Request timeout 300s; streaming supported natively |

---

## Client SDK Quick Reference

| SDK | Language | Usage |
|---|---|---|
| Vercel AI SDK | React/Next.js | `useChat()` hook — handles SSE, cancel, error recovery |
| LangChain | Python | `astream()` — async iterator with callbacks |
| OpenAI SDK | Python/Node | `stream=True` — returns async iterator |
| Anthropic SDK | Python/Node | `stream=True` — returns event stream with typed events |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Buffering entire response then sending | Defeats purpose of streaming, high TTFB | Stream token by token |
| No timeout on streams | Hung connections consume resources | 5-min max stream timeout |
| Proxy buffering enabled | Response held until complete | Disable proxy_buffering in NGINX |
| No client-side error handling | Stream silently fails | Handle errors + show partial response |
| Ignoring backpressure | Server OOM on slow clients | Bounded buffer + drop policy |
| No cancel/abort mechanism | Wasted tokens on abandoned requests | Implement abort controller |
| Polling instead of streaming | High latency, wasted requests | Use SSE or WebSocket |
| Accumulating tool args without validation | Malformed JSON causes crash | Validate after complete accumulation |

---

## Cross-References

- `cost-optimization-patterns.md` — streaming does not reduce cost but improves perceived latency
- `multi-model-routing.md` — routing decisions before streaming begins
- `../ai-llm/references/structured-output-patterns.md` — streaming structured outputs
- `../ai-agents/references/voice-multimodal-agents.md` — streaming for voice pipelines
- `../ai-agents/references/agent-debugging-patterns.md` — debugging stream failures
