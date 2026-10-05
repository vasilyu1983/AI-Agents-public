# Channel Routing

Use this reference when designing omnichannel bot architectures, channel-specific adapters, and cross-channel session continuity.

## Table of Contents

- [Channel Capability Matrix](#channel-capability-matrix)
- [Channel-Specific Constraints](#channel-specific-constraints)
- [Session Continuity Across Channels](#session-continuity-across-channels)
- [Channel Selection Strategy](#channel-selection-strategy)
- [Universal Bot Backend](#universal-bot-backend)
- [WhatsApp Business API](#whatsapp-business-api)
- [SMS via Twilio](#sms-via-twilio)
- [Web Chat Widget](#web-chat-widget)
- [Email Bot Patterns](#email-bot-patterns)

## Channel Capability Matrix

| Capability | Web chat | WhatsApp | SMS | Email | In-app | Messenger |
|-----------|----------|----------|-----|-------|--------|-----------|
| Rich text (bold, lists) | Yes | Yes | No | Yes | Yes | Yes |
| Buttons / quick replies | Yes | Yes (3 max) | No | No | Yes | Yes |
| Images | Yes | Yes | MMS | Yes | Yes | Yes |
| Files / attachments | Yes | Yes | No | Yes | Yes | Yes |
| Carousels | Yes | No | No | No | Yes | Yes |
| Typing indicator | Yes | Yes | No | No | Yes | Yes |
| Read receipts | Optional | Yes | No | No | Optional | Yes |
| Session persistence | Cookie/token | 24h window | Stateless | Stateless | Token | 24h window |
| Message length limit | ~4000 | 4096 | 160/1600 | None | ~4000 | 2000 |
| Proactive messaging | Yes | Template-based | Yes | Yes | Yes | 24h window |
| User identity | Optional | Phone number | Phone number | Email | Authenticated | PSID |

## Channel-Specific Constraints

### WhatsApp

- **24-hour window:** After the last user message, you have 24 hours to respond freely. After that, only pre-approved template messages are allowed.
- **Button limit:** Maximum 3 buttons per message. For longer option lists, use numbered text.
- **Template messages:** Must be pre-approved by Meta. Plan templates for common proactive scenarios (order updates, appointment reminders).
- **Media:** Max 16MB for documents, 5MB for images. No animated GIFs in some clients.

### SMS

- **160-character segments:** Messages over 160 characters are split into segments, each billed separately. Keep bot responses under 320 characters (2 segments) when possible.
- **No rich formatting:** No bold, no links that render as previews, no buttons. Use numbered options: "Reply 1 for order status, 2 for returns."
- **MMS:** Available in US/Canada for images and longer text (up to 1600 chars). Not universally supported internationally.
- **Opt-in required:** Must have explicit opt-in before sending. Include opt-out instructions.

### Email

- **Asynchronous:** Users don't expect instant responses. Set SLA expectations (e.g., "We'll get back to you within 2 hours").
- **Threading:** Parse the subject line and In-Reply-To header to maintain conversation context.
- **HTML rendering:** Responses can use rich HTML, but keep it simple — email clients render inconsistently.
- **Attachments:** Can send and receive files, which other channels struggle with.

### Facebook Messenger

- **24-hour window:** Similar to WhatsApp. After 24 hours, only subscription messaging (approved use cases) or one-time notification requests.
- **Persona API:** Can set a custom name and avatar per message — useful for handoff ("Sarah from Support is now helping you").
- **Persistent menu:** Always-visible menu of common actions. Configure this for top intents.

## Session Continuity Across Channels

Users switch channels. The bot should recognize them and continue the conversation.

**Identity resolution:**

```python
from dataclasses import dataclass

@dataclass
class UserIdentity:
    canonical_id: str               # Internal user ID
    identifiers: dict[str, str]     # channel → channel_user_id mapping

# Example:
# {
#     "canonical_id": "user_abc123",
#     "identifiers": {
#         "web_chat": "session_xyz",
#         "whatsapp": "+44712345678",
#         "email": "jane@example.com",
#         "sms": "+44712345678",
#     }
# }

async def resolve_identity(channel: str, channel_user_id: str) -> UserIdentity | None:
    """Find the canonical user from a channel-specific identifier."""
    return await identity_store.find_by_channel(channel, channel_user_id)

async def link_identity(canonical_id: str, channel: str, channel_user_id: str):
    """Link a new channel identifier to an existing user."""
    await identity_store.add_identifier(canonical_id, channel, channel_user_id)
```

**Cross-channel state merge:**

```python
async def resume_conversation(
    user_id: str,
    new_channel: str,
) -> dict | None:
    """Find the most recent active conversation for this user, regardless of channel."""
    active = await conversation_store.find_active(user_id)
    if active and active["channel"] != new_channel:
        # User switched channels — adapt state
        active["channel"] = new_channel
        active["channel_switch_count"] = active.get("channel_switch_count", 0) + 1
        return active
    return active
```

**Rules:**
- Phone number is the strongest cross-channel identifier (links WhatsApp and SMS).
- Email links web chat and email channel.
- Never assume two channels are the same user without an explicit link.
- When resuming on a new channel, acknowledge it: "I see we were chatting on WhatsApp earlier. I have your details — let's continue."

## Channel Selection Strategy

Choose the right channel for the right interaction.

| Scenario | Best channel | Why |
|----------|-------------|-----|
| Real-time troubleshooting | Web chat, in-app | Rich UI, typing indicators, session context |
| Order/shipping notifications | WhatsApp, SMS | High open rates, push delivery |
| Complex issue resolution | Email | Supports attachments, async, long-form |
| Post-purchase support | WhatsApp, in-app | Familiar, conversational |
| Lead qualification | Web chat | Embedded in the buying flow |
| Appointment reminders | SMS, WhatsApp | Reliable delivery, short messages |
| Internal workflow | Slack, Teams | Where the team already works |

**Proactive channel selection:**

```python
def select_notification_channel(
    user: UserIdentity,
    message_type: str,
    urgency: str,
) -> str:
    """Choose the best channel for a proactive message."""
    preferences = user.notification_preferences    # User-set preferences win

    if preferences and message_type in preferences:
        return preferences[message_type]

    # Default logic
    if urgency == "high" and "sms" in user.identifiers:
        return "sms"                                # SMS for urgent — high deliverability
    if "whatsapp" in user.identifiers:
        return "whatsapp"                           # WhatsApp for general — rich, high open rate
    if "email" in user.identifiers:
        return "email"                              # Email as fallback
    return "in_app"                                 # In-app as last resort
```

## Universal Bot Backend

Keep the bot logic channel-agnostic. Channel-specific formatting lives in adapters.

**Architecture:**

```
┌──────────────────────────────────────────┐
│              Channel Adapters            │
│  ┌─────┐ ┌────────┐ ┌────┐ ┌──────┐     │
│  │ Web │ │WhatsApp│ │SMS │ │Email │ ... │
│  └──┬──┘ └───┬────┘ └─┬──┘ └──┬───┘     │
│     │        │        │       │          │
│     ▼        ▼        ▼       ▼          │
│  ┌──────────────────────────────────┐    │
│  │     Canonical Message Format     │    │
│  └──────────────┬───────────────────┘    │
└─────────────────┼────────────────────────┘
                  │
          ┌───────▼───────┐
          │   Bot Core    │
          │  (LLM + state │
          │   + routing)  │
          └───────┬───────┘
                  │
          ┌───────▼───────┐
          │ Tool Backends  │
          └───────────────┘
```

**Canonical message format:**

```python
from dataclasses import dataclass, field

@dataclass
class CanonicalMessage:
    text: str
    channel: str
    sender: str                     # "user" or "bot"
    attachments: list[dict] = field(default_factory=list)
    buttons: list[dict] = field(default_factory=list)     # [{"label": "...", "value": "..."}]
    metadata: dict = field(default_factory=dict)

@dataclass
class CanonicalResponse:
    text: str
    buttons: list[dict] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)
    typing_delay_ms: int = 0
```

**Channel adapter interface:**

```python
from abc import ABC, abstractmethod

class ChannelAdapter(ABC):
    @abstractmethod
    async def receive(self, raw_event: dict) -> CanonicalMessage:
        """Convert channel-specific event to canonical format."""
        ...

    @abstractmethod
    async def send(self, channel_user_id: str, response: CanonicalResponse) -> None:
        """Convert canonical response to channel-specific format and send."""
        ...

    @abstractmethod
    def format_buttons(self, buttons: list[dict]) -> str | dict:
        """Format buttons for this channel. SMS: numbered text. WhatsApp: interactive buttons."""
        ...
```

**SMS adapter example (buttons as numbered text):**

```python
class SMSAdapter(ChannelAdapter):
    def format_buttons(self, buttons: list[dict]) -> str:
        lines = [f"{i+1}. {b['label']}" for i, b in enumerate(buttons)]
        return "\n".join(lines) + "\n\nReply with a number."

    async def send(self, phone: str, response: CanonicalResponse) -> None:
        text = response.text
        if response.buttons:
            text += "\n\n" + self.format_buttons(response.buttons)
        # Truncate to 2 SMS segments
        if len(text) > 320:
            text = text[:317] + "..."
        await twilio_client.send_sms(to=phone, body=text)
```

**Rules:**
- Bot core never references channel-specific APIs directly.
- All channel-specific formatting, length limits, and media constraints live in the adapter.
- Test every bot response on every supported channel — what looks fine on web can break on SMS.

## WhatsApp Business API

**Sending messages (Cloud API):**

```python
class WhatsAppClient:
    def __init__(self, phone_number_id: str, access_token: str):
        # Graph API versions deprecate on a rolling ~2-year clock (v25.0 is current as of
        # mid-2026; verify at developers.facebook.com/docs/graph-api/changelog/versions/
        # before pinning — an old version pin will start hard-failing on its sunset date).
        self.base_url = f"https://graph.facebook.com/v25.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def send_text(self, to: str, text: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def send_interactive_buttons(
        self, to: str, body: str, buttons: list[dict]
    ) -> dict:
        """Send message with up to 3 reply buttons."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": b["value"], "title": b["label"][:20]}}
                        for b in buttons[:3]
                    ]
                },
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def send_template(self, to: str, template_name: str, language: str = "en") -> dict:
        """Send a pre-approved template message (for out-of-window messaging)."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {"name": template_name, "language": {"code": language}},
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
```

## SMS via Twilio

```python
from twilio.rest import Client as TwilioRestClient

class TwilioSMSClient:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = TwilioRestClient(account_sid, auth_token)
        self.from_number = from_number

    async def send_sms(self, to: str, body: str) -> str:
        """Send an SMS. Returns the message SID."""
        message = self.client.messages.create(
            to=to,
            from_=self.from_number,
            body=body,
        )
        return message.sid

    async def handle_incoming(self, request_body: dict) -> CanonicalMessage:
        """Parse Twilio webhook payload into canonical format."""
        return CanonicalMessage(
            text=request_body["Body"],
            channel="sms",
            sender="user",
            metadata={
                "from": request_body["From"],
                "message_sid": request_body["MessageSid"],
            },
        )
```

**Rules:**
- Always include opt-out language in the first SMS: "Reply STOP to unsubscribe."
- Track per-number message counts for cost visibility.
- Use a dedicated number per bot to avoid mixing traffic.

## Web Chat Widget

**Embed pattern (FastAPI backend + frontend widget):**

```python
# Backend — FastAPI WebSocket endpoint
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    state = await load_or_create_session(session_id)

    try:
        while True:
            user_message = await websocket.receive_text()
            canonical = CanonicalMessage(text=user_message, channel="web_chat", sender="user")

            # Send typing indicator
            await websocket.send_json({"type": "typing", "visible": True})

            response = await bot_core.process(canonical, state)

            await websocket.send_json({"type": "typing", "visible": False})
            await websocket.send_json({
                "type": "message",
                "text": response.text,
                "buttons": response.buttons,
            })
    except Exception:
        await save_session(session_id, state)
```

**Rules:**
- Use WebSockets for real-time chat, not polling.
- Persist session across page navigations using a cookie or localStorage token.
- Show a typing indicator while the bot is generating — even brief delays feel broken without one.
- Provide a "minimize" and "close" control. Never trap users in the chat widget.

## Email Bot Patterns

**Inbound email parsing:**

```python
import email
from email.utils import parseaddr

def parse_inbound_email(raw_email: str) -> CanonicalMessage:
    msg = email.message_from_string(raw_email)

    sender_name, sender_email = parseaddr(msg["From"])
    subject = msg["Subject"] or ""
    in_reply_to = msg.get("In-Reply-To")

    # Extract plain text body
    body = ""
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode("utf-8", errors="replace")
            break

    # Strip quoted reply text (lines starting with >)
    new_content = "\n".join(
        line for line in body.splitlines()
        if not line.startswith(">") and not line.startswith("On ") and "wrote:" not in line
    ).strip()

    return CanonicalMessage(
        text=new_content or body,
        channel="email",
        sender="user",
        metadata={
            "email": sender_email,
            "subject": subject,
            "in_reply_to": in_reply_to,
            "has_attachments": any(
                part.get_content_disposition() == "attachment" for part in msg.walk()
            ),
        },
    )
```

**Outbound email response:**

```python
async def send_email_response(
    to: str,
    subject: str,
    body: str,
    in_reply_to: str | None = None,
):
    """Send a bot response via email, maintaining the thread."""
    headers = {}
    if in_reply_to:
        headers["In-Reply-To"] = in_reply_to
        headers["References"] = in_reply_to
        subject = f"Re: {subject}" if not subject.startswith("Re:") else subject

    await email_sender.send(
        to=to,
        subject=subject,
        text_body=body,
        headers=headers,
    )
```

**Rules:**
- Parse quoted replies carefully — only process new content, not the full thread.
- Maintain email threading via `In-Reply-To` and `References` headers.
- Set reply-to a monitored address so the conversation continues.
- For email infrastructure and deliverability, see [`../software-email-engineering/SKILL.md`](../../software-email-engineering/SKILL.md).
