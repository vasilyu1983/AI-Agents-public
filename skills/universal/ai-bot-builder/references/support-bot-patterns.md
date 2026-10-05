# Support Bot Patterns

Use this reference when building customer support bots with knowledge base grounding, ticket system integration, and resolution tracking.

## Table of Contents

- [Knowledge Base Grounding](#knowledge-base-grounding)
- [Ticket System Integration](#ticket-system-integration)
- [Order and Account Lookup Tools](#order-and-account-lookup-tools)
- [Resolution Tracking](#resolution-tracking)
- [CSAT Collection](#csat-collection)
- [Multi-Language Support](#multi-language-support)
- [Common Support Flows](#common-support-flows)
- [Integration Architecture](#integration-architecture)

## Multi-Tier Support Pipeline

For production support bots, use a tiered answer pipeline with quality gates between tiers:

```
User message
  → Spam filter (LLM + file_search on spam patterns VS)
  → Greeting fast-path (regex, no ML overhead)
  → Intent router fast-path (regex: "speak to human" → instant HANDOFF)
  → Intent router (LLM: SUPPORT / ACTION_REQUEST / NOT_IN_SCOPE / SPAM_SUSPECT)
  → Support Tier 1 (LLM + file_search on internal KB, max 5 results)
  → Quality gate (answer < 160 chars OR contains "not sure"/"can't find"?)
  → Support Tier 2 (LLM + web_search restricted to help.domain.com)
  → Compliance filter (regex: investment advice, tipping-off, PII leakage)
  → Reply
```

**Key design choices:**
- Deterministic fast-paths (greeting regex, "speak to human" regex) run before any LLM call — saves tokens and latency for ~15% of messages
- Spam filter and router are single-turn (no conversation history) to avoid history-bias; support tiers load last 5 messages for multi-turn context
- Quality gate between tiers uses both length threshold AND weak-signal phrases — catches short/uncertain T1 answers that need help center grounding
- Compliance filter runs after answer generation, before the response reaches the user — essential for regulated domains
- Every tier has a typed JSON schema for structured output (Pydantic model → OpenAI json_schema)

### Compliance Filter (Post-Generation)

For bots in regulated industries (finance, healthcare, legal), add a post-generation filter before any response reaches the user:

```python
import re

_INVESTMENT_RE = re.compile(r"good investment|will go up|you should buy|guaranteed return", re.I)
_TIPPING_OFF_RE = re.compile(r"under investigation|flagged for suspicious|SAR|fraud review", re.I)
_PII_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PII_CARD_RE = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")

def compliance_check(reply: str) -> tuple[bool, list[str]]:
    flags = []
    if _INVESTMENT_RE.search(reply): flags.append("Investment advice")
    if _TIPPING_OFF_RE.search(reply): flags.append("Tipping-off language")
    if _PII_EMAIL_RE.search(reply): flags.append("Unmasked email")
    if _PII_CARD_RE.search(reply): flags.append("Card number")
    return (len(flags) == 0, flags)
```

**On compliance failure:** Replace the response with a safe handoff message and route to a human agent. Log the violation flags for review. Do not send the original response.

### Channel Mirroring (Ghost Scribe)

When users can reach the bot via multiple channels (web + Telegram), mirror messages between channels:
- **Inbound mirroring (web → Telegram):** Prefix with channel label (`📝 *Web:* <message>`)
- **Outbound mirroring (bot → Telegram):** Send bot reply to the secondary channel
- **Critical:** Mirror sends must be async fire-and-forget — mirror failure must never block or delay the primary response path. Log failures at ERROR level with conversation_id, but don't retry.

## Knowledge Base Grounding

Ground bot responses in help center articles using retrieval-augmented generation. Never let the bot answer from general knowledge alone — every factual claim should trace to a source.

For RAG architecture decisions (chunking, hybrid search, reranking), see [`../ai-rag/SKILL.md`](../../ai-rag/SKILL.md).

**Retrieval pipeline:**

```python
from dataclasses import dataclass

@dataclass
class KBArticle:
    id: str
    title: str
    url: str
    content: str
    category: str
    last_updated: str               # ISO 8601

async def retrieve_relevant_articles(
    query: str,
    top_k: int = 3,
    min_score: float = 0.7,
) -> list[KBArticle]:
    """Retrieve top-k articles from the help center index."""
    results = await vector_store.search(query, top_k=top_k)
    return [r for r in results if r.score >= min_score]
```

**Grounded response generation:**

```python
KB_GROUNDING_PROMPT = """Answer the customer's question using ONLY the provided help center articles.

Rules:
1. If the articles contain the answer, respond with the answer and cite the source.
2. If the articles partially answer the question, give what you can and say what's missing.
3. If no article is relevant, say "I don't have information on that" — do NOT guess.
4. Always include a link to the most relevant article.

Articles:
{articles}

Customer question: {question}

Format your response as:
[Answer in 2-3 sentences]
📄 More details: [Article Title](article_url)
"""
```

**Citation pattern:**

```
Bot: "You can return items within 30 days of delivery for a full refund. Start
     your return from the Orders page in your account.
     📄 More details: Returns & Refunds Policy (https://help.acme.com/returns)"
```

**Rules:**
- Always cite the source article. Citations build trust and let users self-serve deeper.
- Re-index the knowledge base on a schedule (daily for active help centers).
- Track which articles are cited most frequently — these are candidates for improvement or bot flow integration.
- If no relevant article is found with score >= threshold, acknowledge the gap rather than hallucinating.

## Ticket System Integration

Connect the bot to the ticket system so it can read, create, and update tickets without human intervention.

**Zendesk integration:**

```python
import httpx

class ZendeskClient:
    def __init__(self, subdomain: str, email: str, api_token: str):
        self.base_url = f"https://{subdomain}.zendesk.com/api/v2"
        self.auth = (f"{email}/token", api_token)

    async def create_ticket(
        self,
        subject: str,
        description: str,
        requester_email: str,
        priority: str = "normal",
        tags: list[str] | None = None,
        custom_fields: list[dict] | None = None,
    ) -> dict:
        payload = {
            "ticket": {
                "subject": subject,
                "description": description,
                "requester": {"email": requester_email},
                "priority": priority,
                "tags": tags or ["bot_created"],
                "custom_fields": custom_fields or [],
            }
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/tickets.json",
                json=payload,
                auth=self.auth,
            )
            resp.raise_for_status()
            return resp.json()["ticket"]

    async def get_ticket(self, ticket_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/tickets/{ticket_id}.json",
                auth=self.auth,
            )
            resp.raise_for_status()
            return resp.json()["ticket"]

    async def add_comment(self, ticket_id: int, body: str, public: bool = True) -> dict:
        payload = {"ticket": {"comment": {"body": body, "public": public}}}
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.base_url}/tickets/{ticket_id}.json",
                json=payload,
                auth=self.auth,
            )
            resp.raise_for_status()
            return resp.json()["ticket"]
```

**Intercom integration:**

```python
class IntercomClient:
    def __init__(self, access_token: str):
        self.base_url = "https://api.intercom.io"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Intercom-Version": "2.11",
        }

    async def create_conversation(self, user_id: str, body: str) -> dict:
        payload = {"from": {"type": "user", "id": user_id}, "body": body}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/conversations",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def reply_to_conversation(
        self, conversation_id: str, body: str, message_type: str = "comment"
    ) -> dict:
        payload = {
            "type": "admin",
            "message_type": message_type,
            "body": body,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/conversations/{conversation_id}/reply",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()
```

**Freshdesk integration:**

```python
class FreshdeskClient:
    def __init__(self, domain: str, api_key: str):
        self.base_url = f"https://{domain}.freshdesk.com/api/v2"
        self.auth = (api_key, "X")

    async def create_ticket(
        self,
        subject: str,
        description: str,
        email: str,
        priority: int = 1,          # 1=Low, 2=Medium, 3=High, 4=Urgent
        status: int = 2,             # 2=Open
        tags: list[str] | None = None,
    ) -> dict:
        payload = {
            "subject": subject,
            "description": description,
            "email": email,
            "priority": priority,
            "status": status,
            "tags": tags or ["bot_created"],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/tickets",
                json=payload,
                auth=self.auth,
            )
            resp.raise_for_status()
            return resp.json()
```

**Rules:**
- Tag all bot-created tickets with `bot_created` for analytics.
- Include the bot conversation summary in the ticket description so agents have context.
- Never expose raw ticket IDs to users — use a friendly reference format (e.g., "REF-12345").

## Order and Account Lookup Tools

Define tools the bot can invoke to look up customer data. Wrap every external API in a tool function with validation and error handling.

```python
from pydantic import BaseModel

class OrderLookupInput(BaseModel):
    order_id: str | None = None
    email: str | None = None

class OrderLookupResult(BaseModel):
    order_id: str
    status: str                     # "processing", "shipped", "delivered", "cancelled"
    items: list[dict]
    total: float
    currency: str
    tracking_url: str | None
    estimated_delivery: str | None
    placed_at: str

async def lookup_order(input: OrderLookupInput) -> OrderLookupResult | str:
    """Look up an order by ID or email. Returns the order or an error message."""
    if not input.order_id and not input.email:
        return "I need either an order number or the email address used to place the order."

    try:
        order = await order_service.find(
            order_id=input.order_id,
            email=input.email,
        )
        if not order:
            return "I couldn't find an order with those details. Could you double-check?"
        return OrderLookupResult(**order)
    except ServiceUnavailableError:
        return "Our order system is temporarily unavailable. I can take your details and follow up."
```

**Security rules for account lookups:**
- Always verify identity before returning account data (email match, last 4 of phone, etc.).
- Never return full payment details — mask to last 4 digits.
- Log all account lookups for audit trail.
- Rate-limit lookups per session to prevent enumeration attacks.

## Resolution Tracking

Track how every conversation ends.

**Resolution categories:**

| Category | Definition | Trigger |
|----------|-----------|---------|
| Resolved by bot | Bot answered the question or completed the action | User confirms resolution or conversation closes naturally |
| Escalated | Handed off to a human agent | Escalation trigger fired |
| Abandoned | User left without resolution | No user message for > 10 minutes after bot response |
| Self-served | Bot provided a link/article and user clicked through | Link click detected + no follow-up question |
| Deflected | User's question was out of scope, redirected | Out-of-scope handler triggered |

**Implementation:**

```python
from enum import Enum
from datetime import datetime

class Resolution(str, Enum):
    RESOLVED_BY_BOT = "resolved_by_bot"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"
    SELF_SERVED = "self_served"
    DEFLECTED = "deflected"

async def close_conversation(
    session_id: str,
    resolution: Resolution,
    details: str | None = None,
):
    await analytics.track("conversation_closed", {
        "session_id": session_id,
        "resolution": resolution.value,
        "details": details,
        "closed_at": datetime.utcnow().isoformat(),
        "turn_count": state["turn_count"],
        "duration_seconds": _calculate_duration(state),
    })
```

**Rules:**
- Every conversation must have a resolution. No conversation should end in an unknown state.
- Abandonment detection should use inactivity timeout, not session close (users may close and reopen).
- Track resolution rate by intent — some intents are inherently harder to bot-resolve.

## CSAT Collection

Collect satisfaction feedback at the end of resolved conversations.

**Collection pattern:**

```
Bot: "Glad I could help! Before you go — how would you rate your experience?"
     ⭐ Great   😐 OK   👎 Not great

[If "Not great":]
Bot: "I'm sorry to hear that. Could you tell me what could have been better?
     Your feedback helps us improve."
```

**Implementation:**

```python
async def collect_csat(session_id: str) -> int | None:
    response = await send_with_buttons(
        session_id,
        text="How would you rate your experience?",
        buttons=[
            {"label": "Great (5)", "value": "5"},
            {"label": "Good (4)", "value": "4"},
            {"label": "OK (3)", "value": "3"},
            {"label": "Not great (2)", "value": "2"},
            {"label": "Poor (1)", "value": "1"},
        ],
    )
    if response and int(response) <= 2:
        await send_message(session_id, "Could you tell me what could have been better?")
        feedback = await wait_for_response(session_id, timeout=60)
        await store_feedback(session_id, int(response), feedback)
    return int(response) if response else None
```

**Rules:**
- Ask for CSAT only after resolution, never mid-conversation.
- Keep it to one question. Multi-question surveys in chat have near-zero completion.
- If the user ignores the CSAT prompt, don't re-ask. Record as "no response."
- For escalated conversations, collect CSAT after the human agent resolves (not at handoff).

## Multi-Language Support

**Detection and routing:**

```python
SUPPORTED_LANGUAGES = {"en", "es", "fr", "de", "pt", "ja"}

async def detect_and_route_language(user_message: str, state: dict) -> str:
    """Detect language and set for the conversation."""
    if state.get("language"):
        return state["language"]        # Already detected, don't re-detect

    detected = await detect_language(user_message)

    if detected in SUPPORTED_LANGUAGES:
        state["language"] = detected
        return detected
    else:
        # Unsupported language — respond in English with acknowledgment
        state["language"] = "en"
        return "en"
```

**Considerations:**
- Detect language from the first user message and lock it for the session.
- System prompts should have per-language variants for tone accuracy.
- Knowledge base should be indexed per language — don't rely on real-time translation of English articles.
- If a language isn't supported, acknowledge it: "I currently support English and Spanish. I'll do my best to help in English."
- Date, currency, and number formatting must match the user's locale.

## Common Support Flows

### Order status

```
User: "Where's my order?"
Bot:  [Extract order_id or email via slot filling]
Bot:  [Call lookup_order tool]
Bot:  "Your order ORD-123456 shipped on March 28 via FedEx.
       Tracking: [link]. Estimated delivery: April 2."
```

### Returns

```
User: "I want to return something"
Bot:  [Collect order_id, item, reason]
Bot:  [Check return eligibility via tool]
Bot:  "Your return is eligible. I've generated a return label — check your email.
       Drop it off at any FedEx location. Refund processes in 5-7 business days."
```

### Billing

```
User: "I was charged twice"
Bot:  [Collect order_id or email, verify identity]
Bot:  [Look up charges via billing tool]
Bot:  [If duplicate confirmed] "I can see the duplicate charge. I've initiated a refund
       of $29.99 to your card ending in 4321. It should appear in 3-5 business days."
Bot:  [If not confirmed] "I can see one charge of $29.99 on March 25. Could you share
       more details about the second charge — the amount and date?"
```

### Password reset

```
User: "I can't log in"
Bot:  [Collect email]
Bot:  [Trigger password reset via tool]
Bot:  "I've sent a password reset link to j***@email.com.
       Check your inbox (and spam folder). The link expires in 30 minutes."
```

### Technical troubleshooting

```
User: "The app keeps crashing"
Bot:  [Collect device, OS version, app version via slot filling]
Bot:  [Check known issues via KB]
Bot:  [If known issue] "There's a known issue with version 3.2.1 on iOS 18.
       Update to version 3.2.2 from the App Store and it should be fixed."
Bot:  [If unknown] "I've logged this for our technical team. In the meantime,
       try clearing the app cache: Settings → App → Clear Cache."
Bot:  [If not resolved after troubleshooting] → Escalate with device info
```

## Integration Architecture

**Standard support bot architecture:**

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Channels   │───▶│   Bot Core   │───▶│  Tool Backends  │
│  (web,      │    │  (LLM +      │    │                 │
│   WhatsApp, │    │   state +    │    │  • Order API    │
│   email)    │    │   routing)   │    │  • Billing API  │
└─────────────┘    └──────┬───────┘    │  • KB Search    │
                          │            │  • CRM API      │
                   ┌──────▼───────┐    │  • Ticket API   │
                   │  Ticket      │    └─────────────────┘
                   │  System      │
                   │  (Zendesk,   │
                   │   Intercom)  │
                   └──────────────┘
```

**Data flow:**
1. User message arrives via channel adapter.
2. Bot core classifies intent, manages state, generates response.
3. Tool calls go to backend APIs (order system, billing, KB).
4. If escalation triggers, bot packages context and routes to ticket system / agent queue.
5. All events logged to analytics pipeline.

**Rules:**
- Bot core should be channel-agnostic. Channel-specific formatting lives in adapters.
- Tool backends should be wrapped in a consistent interface. Don't scatter API calls across the bot logic.
- The ticket system is both an escalation target and a resolution tracker.
- For channel adapter patterns, see [channel-routing.md](channel-routing.md).
