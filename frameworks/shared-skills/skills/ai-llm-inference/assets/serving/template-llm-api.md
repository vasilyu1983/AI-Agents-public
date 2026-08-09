# OpenAI-Compatible LLM API Template

Use an OpenAI-compatible surface unless there is a strong reason to invent a custom wire shape.

## 1. Endpoint

```text
POST /v1/chat/completions
```

## 2. Request Body

```json
{
  "model": "<model_id>",
  "messages": [
    {"role": "system", "content": "You are a structured extraction service."},
    {"role": "user", "content": "<prompt>"}
  ],
  "max_tokens": 256,
  "temperature": 0,
  "stream": false,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "result",
      "schema": {"type": "object"}
    }
  }
}
```

## 3. Response Expectations

```json
{
  "id": "<request_id>",
  "object": "chat.completion",
  "model": "<served_model>",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "<output>"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

## 4. Required Behavior

- reject requests that exceed input or output token policy
- return a request ID on every response
- support overload shedding with a clear error code
- keep structured-output validity observable
- keep streaming and non-streaming paths behaviorally aligned

## 5. Observability Fields

- request_id
- model
- adapter_id if applicable
- queue_delay_ms
- ttft_ms
- inter_token_latency_ms
- e2e_latency_ms
- prompt_tokens
- completion_tokens
- structured_output_valid

## 6. Security

- API auth required
- tenant isolation enforced
- prompt and output logging minimized or scrubbed
- rate limiting and overload protection enabled
