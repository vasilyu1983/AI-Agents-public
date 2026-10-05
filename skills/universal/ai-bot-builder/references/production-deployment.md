# Production Deployment

Use this reference when serving, scaling, monitoring, and securing a bot in production.

## Table of Contents

- [Serving Architecture](#serving-architecture)
- [Scaling Patterns](#scaling-patterns)
- [Canary Deployment](#canary-deployment)
- [Cost Model](#cost-model)
- [Rate Limiting and Abuse Prevention](#rate-limiting-and-abuse-prevention)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Disaster Recovery](#disaster-recovery)
- [Security Considerations](#security-considerations)

## Serving Architecture

**Standard bot serving stack:**

```
                    ┌─────────────────────────┐
                    │     Load Balancer        │
                    │   (sticky sessions)      │
                    └───────────┬──────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
       ┌──────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
       │  Bot Worker  │  │  Bot Worker  │  │  Bot Worker  │
       │  (FastAPI)   │  │  (FastAPI)   │  │  (FastAPI)   │
       └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
              │                 │                  │
       ┌──────▼─────────────────▼──────────────────▼──────┐
       │                Shared Services                    │
       │  ┌──────────┐  ┌───────────┐  ┌───────────────┐ │
       │  │  State    │  │  LLM      │  │  Tool         │ │
       │  │  Store    │  │  Gateway   │  │  Backends     │ │
       │  │  (Redis)  │  │           │  │               │ │
       │  └──────────┘  └───────────┘  └───────────────┘ │
       └──────────────────────────────────────────────────┘
```

**FastAPI bot server:**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize connections
    app.state.redis = redis.Redis(host="redis", port=6379, decode_responses=True)
    app.state.llm_client = LLMGateway()
    app.state.tool_registry = ToolRegistry()
    yield
    # Shutdown: clean up
    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)

class MessageRequest(BaseModel):
    session_id: str
    channel: str
    text: str
    metadata: dict = {}

class MessageResponse(BaseModel):
    text: str
    buttons: list[dict] = []
    session_id: str

@app.post("/api/v1/message", response_model=MessageResponse)
async def handle_message(request: MessageRequest):
    # Load or create session state
    state = await load_state(app.state.redis, request.session_id)
    if not state:
        state = create_initial_state(request.session_id, request.channel)

    # Process through bot core
    response = await bot_core.process(
        message=request.text,
        state=state,
        llm=app.state.llm_client,
        tools=app.state.tool_registry,
    )

    # Persist state
    await save_state(app.state.redis, request.session_id, state)

    return MessageResponse(
        text=response.text,
        buttons=response.buttons,
        session_id=request.session_id,
    )

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    state = await load_state(app.state.redis, session_id)
    if not state:
        state = create_initial_state(session_id, "web_chat")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "typing", "visible": True})

            response = await bot_core.process(
                message=data,
                state=state,
                llm=app.state.llm_client,
                tools=app.state.tool_registry,
            )

            await save_state(app.state.redis, session_id, state)
            await websocket.send_json({"type": "typing", "visible": False})
            await websocket.send_json({
                "type": "message",
                "text": response.text,
                "buttons": response.buttons,
            })
    except Exception:
        await save_state(app.state.redis, session_id, state)

@app.get("/health")
async def health():
    # Check critical dependencies
    try:
        await app.state.redis.ping()
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable")
```

**Rules:**
- Use a shared state store (Redis) so any worker can handle any session.
- Health checks must verify critical dependencies (Redis, LLM gateway), not just return 200.
- Separate the HTTP/WebSocket layer from bot logic — the bot core should be framework-agnostic.

## Scaling Patterns

**Horizontal scaling:**

```python
# Docker Compose example for local dev / small deployments
# docker-compose.yml
"""
services:
  bot:
    build: .
    deploy:
      replicas: 3
    environment:
      - REDIS_URL=redis://redis:6379
      - LLM_GATEWAY_URL=http://llm-gateway:8080
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - bot
"""
```

**Session affinity (sticky sessions):**

WebSocket connections require session affinity — the same client must connect to the same worker for the duration of the connection. For HTTP-based message endpoints, any worker can handle any request if state is externalized to Redis.

```nginx
# nginx.conf — sticky sessions for WebSocket
upstream bot_workers {
    ip_hash;  # Route based on client IP
    server bot:8000;
}
```

**Connection pooling:**

```python
# Shared HTTP client for outbound API calls — reuse connections
import httpx

# Create once at startup, share across requests
http_pool = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=30,
    ),
    timeout=httpx.Timeout(30.0, connect=5.0),
)
```

**Auto-scaling signals:**

| Signal | Scale up when | Scale down when |
|--------|--------------|----------------|
| CPU | > 70% for 2 minutes | < 30% for 10 minutes |
| Active WebSocket connections | > 500 per worker | < 100 per worker |
| Response latency (p95) | > 3 seconds | < 1 second |
| Queue depth | > 50 pending messages | Queue empty for 5 minutes |

## Canary Deployment

Deploy bot changes to a small percentage of traffic before full rollout.

**Canary strategy:**

```
Stage 1: 5% of traffic for 1 hour    → Monitor error rate, latency, CSAT
Stage 2: 25% of traffic for 4 hours  → Monitor containment rate, escalation rate
Stage 3: 50% of traffic for 24 hours → Monitor all metrics
Stage 4: 100% rollout                → Continue monitoring for 48 hours
```

**Implementation:**

```python
import hashlib

class CanaryRouter:
    def __init__(self, canary_percentage: int, canary_config: dict, stable_config: dict):
        self.canary_pct = canary_percentage
        self.canary_config = canary_config
        self.stable_config = stable_config

    def route(self, session_id: str) -> dict:
        """Route session to canary or stable config."""
        bucket = int(hashlib.sha256(session_id.encode()).hexdigest(), 16) % 100
        if bucket < self.canary_pct:
            return self.canary_config
        return self.stable_config

# Usage — model ID comes from config, not a hardcoded string; canary usually
# tests a prompt/logic change against the SAME model, not a model change
# (a model swap is its own migration with its own eval gate, not a canary flag)
router = CanaryRouter(
    canary_percentage=5,
    canary_config={"system_prompt": new_prompt, "model": settings.MODEL_ID},
    stable_config={"system_prompt": current_prompt, "model": settings.MODEL_ID},
)
```

**Rollback criteria (automatic):**

```python
ROLLBACK_THRESHOLDS = {
    "error_rate": 0.05,             # > 5% errors → rollback
    "escalation_rate_increase": 0.10, # > 10% increase vs baseline → rollback
    "p95_latency_ms": 5000,         # > 5s p95 → rollback
    "csat_decrease": 0.5,           # > 0.5 point CSAT drop → rollback
}

async def check_canary_health(canary_metrics: dict, baseline_metrics: dict) -> bool:
    """Returns False if canary should be rolled back."""
    if canary_metrics["error_rate"] > ROLLBACK_THRESHOLDS["error_rate"]:
        return False
    if (canary_metrics["escalation_rate"] - baseline_metrics["escalation_rate"]
            > ROLLBACK_THRESHOLDS["escalation_rate_increase"]):
        return False
    if canary_metrics["p95_latency_ms"] > ROLLBACK_THRESHOLDS["p95_latency_ms"]:
        return False
    return True
```

## Cost Model

**Cost components per conversation:**

| Component | Cost driver | Where the rate comes from |
|-----------|-----------|---------------------------|
| LLM input tokens | System prompt + history + tool results | Model provider's pricing page, per 1M input tokens |
| LLM output tokens | Bot responses | Model provider's pricing page, per 1M output tokens |
| Tool call costs | External API calls (Zendesk, Twilio, etc.) | Each API vendor's price list or your contract |
| Infrastructure | Compute, Redis, networking | Your cloud bill, amortized per conversation |
| Channel costs | WhatsApp per message, SMS per segment | The channel provider's pricing page (rates vary by country and message category) |

Look the rates up on the day you budget and record the date next to them; the decision they feed is model tier per node and whether a channel is affordable at your volume. Output tokens cost several times input tokens at every major provider, so response length is usually the biggest lever. For a quick per-conversation number, fill [`../assets/pricing-template.json`](../assets/pricing-template.json) and run `scripts/bot_cost_estimator.py --pricing <file>`.

**Cost estimation:**

```python
@dataclass
class CostEstimate:
    llm_input_cost: float
    llm_output_cost: float
    tool_costs: float
    channel_cost: float
    infra_cost: float

    @property
    def total(self) -> float:
        return (
            self.llm_input_cost
            + self.llm_output_cost
            + self.tool_costs
            + self.channel_cost
            + self.infra_cost
        )

def estimate_conversation_cost(
    prompt_tokens: int,
    completion_tokens: int,
    tool_calls: int,
    channel: str,
    message_count: int,
    model_tier: str = "flagship",
) -> CostEstimate:
    # Rates by capability tier, not hardcoded model IDs — vendors rename and
    # reprice model families every few months. MODEL_RATES and CHANNEL_RATES
    # come from config that you fill in from the vendors' pricing pages
    # ({"flagship": {"input": <USD per 1M>, "output": <USD per 1M>}, ...}).
    # A missing tier or channel is an error, never a default rate.
    model_rate = MODEL_RATES[model_tier]
    channel_rates = CHANNEL_RATES  # {"web_chat": 0.0, "whatsapp": <per msg>, ...}

    return CostEstimate(
        llm_input_cost=prompt_tokens * model_rate["input"] / 1_000_000,
        llm_output_cost=completion_tokens * model_rate["output"] / 1_000_000,
        tool_costs=tool_calls * TOOL_CALL_RATE,       # from your API vendors
        channel_cost=message_count * channel_rates[channel],
        infra_cost=INFRA_COST_PER_CONVERSATION,      # from your cloud bill
    )
```

**Cost optimization levers:**
- Use a cheaper/faster tier model for intent classification and routing, reserve the flagship-tier model for generation and complex reasoning.
- Cache common responses (FAQ answers that don't depend on user-specific data).
- Summarize long history only at a planned cache break: a summary rewrites the prompt prefix and discards the cached tokens, so an unplanned one can cost more than it saves.
- Set a token budget per conversation and truncate/summarize when approaching it.

## Rate Limiting and Abuse Prevention

**Per-user rate limits:**

```python
from datetime import datetime

class RateLimiter:
    def __init__(self, redis_client, max_messages_per_minute: int = 20, max_conversations_per_hour: int = 10):
        self.redis = redis_client
        self.msg_limit = max_messages_per_minute
        self.conv_limit = max_conversations_per_hour

    async def check_rate_limit(self, user_id: str) -> bool:
        """Returns True if the request is allowed."""
        now = datetime.utcnow()
        minute_key = f"rate:{user_id}:msg:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"rate:{user_id}:conv:{now.strftime('%Y%m%d%H')}"

        msg_count = await self.redis.incr(minute_key)
        if msg_count == 1:
            await self.redis.expire(minute_key, 60)

        if msg_count > self.msg_limit:
            return False

        return True

    async def check_conversation_limit(self, user_id: str) -> bool:
        now = datetime.utcnow()
        hour_key = f"rate:{user_id}:conv:{now.strftime('%Y%m%d%H')}"

        conv_count = await self.redis.incr(hour_key)
        if conv_count == 1:
            await self.redis.expire(hour_key, 3600)

        return conv_count <= self.conv_limit
```

**Abuse patterns to detect:**

| Pattern | Detection | Response |
|---------|-----------|----------|
| Message flooding | > 20 messages/minute | Throttle with "Please slow down" message |
| Prompt injection | Pattern matching + LLM classifier | Log, reject, continue in persona |
| Conversation farming | > 50 conversations/day from same IP | Block IP, require authentication |
| Data extraction | Repeated probing for system info or other users' data | Log, alert security team |
| Gibberish/testing | Multiple messages with no meaningful content | After 3, offer: "Can I help with something specific?" |

## Monitoring and Alerting

**Key health signals:**

```python
import time
from contextlib import asynccontextmanager

# Instrument every conversation turn
@asynccontextmanager
async def track_turn(session_id: str, intent: str):
    start = time.monotonic()
    error = None
    try:
        yield
    except Exception as e:
        error = e
        raise
    finally:
        duration_ms = (time.monotonic() - start) * 1000
        await metrics.emit({
            "metric": "bot_turn_duration_ms",
            "value": duration_ms,
            "tags": {"intent": intent, "error": str(type(error).__name__) if error else "none"},
        })

# Tool call monitoring
async def monitored_tool_call(tool_name: str, *args, **kwargs):
    start = time.monotonic()
    try:
        result = await tool_registry.call(tool_name, *args, **kwargs)
        duration = (time.monotonic() - start) * 1000
        await metrics.emit({
            "metric": "tool_call_duration_ms",
            "value": duration,
            "tags": {"tool": tool_name, "status": "success"},
        })
        return result
    except Exception as e:
        duration = (time.monotonic() - start) * 1000
        await metrics.emit({
            "metric": "tool_call_duration_ms",
            "value": duration,
            "tags": {"tool": tool_name, "status": "error", "error_type": type(e).__name__},
        })
        raise
```

**Alert rules:**

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High error rate | > 5% of turns error in 5 min | Critical | Page on-call |
| LLM latency spike | p95 > 5s for 5 min | High | Check provider status |
| Tool failure | Any tool > 20% error rate in 10 min | High | Check backend, activate fallback |
| Containment drop | Containment rate < 50% for 1 hour | Medium | Review recent conversations |
| Redis connection failure | Health check fails | Critical | Activate fallback, page on-call |
| Cost spike | Daily cost > 2x 7-day average | Medium | Investigate traffic or abuse |

## Disaster Recovery

**Fallback hierarchy:**

```
Level 1: Primary bot (full LLM + tools)
    ↓ (LLM unavailable)
Level 2: Simplified bot (cached responses for top intents + basic tools)
    ↓ (tools unavailable)
Level 3: Static bot (pre-written responses for top 10 questions)
    ↓ (bot infrastructure unavailable)
Level 4: Direct to human queue with apology message
```

**Fallback implementation:**

```python
class FallbackBotCore:
    """Simplified bot for when the LLM is unavailable."""

    CACHED_RESPONSES = {
        "order_status": "To check your order status, visit {order_tracking_url} or reply with your order number and I'll try to look it up.",
        "returns": "To start a return, visit {returns_url}. Returns are accepted within 30 days of delivery.",
        "billing": "For billing questions, visit {billing_url} or I can connect you with our billing team.",
        "default": "I'm having some technical difficulties right now. Let me connect you with a team member who can help.",
    }

    async def process(self, message: str, state: dict) -> dict:
        intent = self._simple_classify(message)
        response = self.CACHED_RESPONSES.get(intent, self.CACHED_RESPONSES["default"])

        if intent == "default":
            # Escalate to human
            await trigger_escalation(state["session_id"], reason="bot_degraded")

        return {"text": response, "buttons": []}

    def _simple_classify(self, message: str) -> str:
        """Keyword-based classification — no LLM needed."""
        message_lower = message.lower()
        if any(w in message_lower for w in ["order", "shipping", "delivery", "track"]):
            return "order_status"
        if any(w in message_lower for w in ["return", "refund", "exchange"]):
            return "returns"
        if any(w in message_lower for w in ["bill", "charge", "payment", "invoice"]):
            return "billing"
        return "default"
```

**Rules:**
- Test fallback modes regularly — don't discover they're broken during an outage.
- Each fallback level should be self-contained and not depend on the level above.
- Always prefer routing to humans over giving degraded bot responses.
- Log all fallback activations and durations for post-incident review.

## Security Considerations

### PII handling

**Regex ordering matters.** Phone number patterns (e.g., `\+?\d[\d\s\-()]{8,}\d`) are greedy and will match card numbers like `4242 4242 4242 4242` if run first. Always apply PII patterns in this order: URLs → emails → **card numbers → phone numbers**. This was discovered in production — phone regex consumed card numbers, producing `***` instead of `4242 **** **** 4242`.

```python
import re

# Order matters: card regex MUST run before phone regex
PII_PATTERNS = [
    ("url", re.compile(r"https?://\S+")),
    ("email", re.compile(r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")),
    ("credit_card", re.compile(r"\b(\d{4})[\s-]?\d{4}[\s-]?\d{4}[\s-]?(\d{4})\b")),
    ("phone", re.compile(r"\+?\d[\d\s\-()]{8,}\d")),
]

def redact_pii(text: str) -> str:
    """Redact PII from text. Order: URLs → emails → cards → phones."""
    for name, pattern in PII_PATTERNS:
        if name == "url":
            text = pattern.sub("[link removed]", text)
        elif name == "email":
            text = pattern.sub(lambda m: f"{m.group(1)[0]}***@{m.group(2)}", text)
        elif name == "credit_card":
            text = pattern.sub(r"\1 **** **** \2", text)
        elif name == "phone":
            text = pattern.sub("***", text)
    return text
```

### Conversation storage

| Data | Storage | Retention | Access |
|------|---------|-----------|--------|
| Active session state | Redis (encrypted at rest) | TTL: 24 hours | Bot workers only |
| Conversation history | Database (encrypted) | 90 days default | Analytics team, support leads |
| PII fields | Separate encrypted store | Per privacy policy | Authorized personnel only |
| Analytics (aggregated) | Data warehouse | Indefinite | Product, engineering |
| Audit logs | Immutable log store | 1 year minimum | Security, compliance |

### Access control

```python
# API key authentication for channel adapters
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    valid_keys = await get_valid_api_keys()         # From secrets manager
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Apply to endpoints
@app.post("/api/v1/message", dependencies=[Security(verify_api_key)])
async def handle_message(request: MessageRequest):
    ...
```

**Rules:**
- Redact PII before writing to logs or analytics. Redact in the logging layer, not the bot logic.
- Encrypt conversation storage at rest and in transit.
- Rotate API keys for channel integrations on a regular cadence.
- Implement audit logging for all data access — who viewed which conversations and when.
- Follow data retention policies — auto-delete conversations after the retention period.
- For application security patterns, see [`../software-security-appsec/SKILL.md`](../../software-security-appsec/SKILL.md).

### Docker hardening for bot containers

Production bot containers should follow these security defaults:

```dockerfile
FROM python:3.13-alpine AS builder
WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.13-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=builder /build/.venv /app/.venv
COPY src/ /app/src/
USER appuser
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml hardening
services:
  bot:
    read_only: true          # Read-only root filesystem
    tmpfs: [/tmp]            # Writable temp only where needed
    security_opt:
      - no-new-privileges:true  # Prevent privilege escalation
    # No cap_add, no privileged
```

**Rules:**
- Non-root user (`USER appuser`), never `--privileged`
- Minimal base image (`python:3.13-alpine` or distroless) — not `python:3.13` (Debian full)
- Read-only root filesystem with `tmpfs` for `/tmp` only
- `no-new-privileges` security opt
- All secrets from secret manager (AWS SM / GCP SM / Vault) — `.env` for local dev only, never in images
- Pin Python 3.13 in the base image — do not use `python:3-alpine` (floats to latest; LangGraph 3.14 support is still landing)
