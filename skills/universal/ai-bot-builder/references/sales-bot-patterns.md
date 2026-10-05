# Sales Bot Patterns

Use this reference when building sales bots with CRM integration, lead qualification, demo booking, and handoff to sales reps.

## Table of Contents

- [CRM Integration](#crm-integration)
- [Lead Qualification Frameworks](#lead-qualification-frameworks)
- [Demo and Meeting Booking](#demo-and-meeting-booking)
- [Objection Handling](#objection-handling)
- [Follow-Up Automation](#follow-up-automation)
- [Sales Bot Conversation Flows](#sales-bot-conversation-flows)
- [Handoff to Sales Rep](#handoff-to-sales-rep)

## CRM Integration

The sales bot must create, read, and update CRM records as the conversation progresses — not after it ends.

**HubSpot integration:**

```python
import httpx

class HubSpotClient:
    def __init__(self, access_token: str):
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def create_contact(self, email: str, properties: dict) -> dict:
        payload = {"properties": {"email": email, **properties}}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/crm/v3/objects/contacts",
                json=payload,
                headers=self.headers,
            )
            if resp.status_code == 409:
                # Contact exists — update instead
                return await self.update_contact_by_email(email, properties)
            resp.raise_for_status()
            return resp.json()

    async def create_deal(
        self,
        deal_name: str,
        pipeline: str,
        stage: str,
        contact_id: str,
        amount: float | None = None,
    ) -> dict:
        payload = {
            "properties": {
                "dealname": deal_name,
                "pipeline": pipeline,
                "dealstage": stage,
                "amount": str(amount) if amount else None,
            },
            "associations": [
                {
                    "to": {"id": contact_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}],
                }
            ],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/crm/v3/objects/deals",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def log_activity(self, contact_id: str, body: str) -> dict:
        """Log bot conversation as a CRM activity/note."""
        payload = {
            "properties": {"hs_note_body": body, "hs_timestamp": _now_ms()},
            "associations": [
                {
                    "to": {"id": contact_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}],
                }
            ],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/crm/v3/objects/notes",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()
```

**Salesforce integration:**

```python
class SalesforceClient:
    def __init__(self, instance_url: str, access_token: str):
        self.base_url = f"{instance_url}/services/data/v60.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def create_lead(self, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/sobjects/Lead",
                json=data,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def create_opportunity(
        self,
        name: str,
        stage: str,
        close_date: str,
        account_id: str | None = None,
        amount: float | None = None,
    ) -> dict:
        payload = {
            "Name": name,
            "StageName": stage,
            "CloseDate": close_date,
            "AccountId": account_id,
            "Amount": amount,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/sobjects/Opportunity",
                json={k: v for k, v in payload.items() if v is not None},
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def log_task(self, who_id: str, subject: str, description: str) -> dict:
        payload = {
            "WhoId": who_id,
            "Subject": subject,
            "Description": description,
            "Status": "Completed",
            "Type": "Bot Conversation",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/sobjects/Task",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()
```

**CRM activity logging:**

Log every meaningful bot interaction to the CRM:

| Event | What to log | When |
|-------|------------|------|
| Contact created | Source: bot, channel, landing page | On first identification |
| Qualification data | BANT/MEDDPICC answers | As slots are collected |
| Demo booked | Date, time, attendees | On booking confirmation |
| Objection raised | Objection type, bot response | On detection |
| Conversation summary | Full summary with outcome | On conversation close |

**Rules:**
- Create or update the CRM contact at the start of the conversation, not the end. If the user drops off, you still have the data.
- Use `bot_qualified` or similar tags to distinguish bot-sourced leads from other channels.
- Never store raw conversation history in CRM — summarize into structured notes.

## Lead Qualification Frameworks

Convert qualification frameworks into bot conversation flows. The bot asks the questions; the framework scores the answers.

### BANT (simpler, good for SMB / PLG)

| Dimension | Bot question | Scoring |
|-----------|-------------|---------|
| **B**udget | "Do you have a budget allocated for this?" | Has budget: +3, Exploring: +1, No budget: 0 |
| **A**uthority | "Are you the decision-maker for this purchase?" | Decision-maker: +3, Influencer: +2, Researcher: +1 |
| **N**eed | "What problem are you trying to solve?" | Clear pain: +3, Nice-to-have: +1, Browsing: 0 |
| **T**imeline | "When are you looking to have a solution in place?" | < 30 days: +3, 1-3 months: +2, No timeline: 0 |

### MEDDPICC (enterprise sales)

| Dimension | Bot question | Scoring |
|-----------|-------------|---------|
| **M**etrics | "What would success look like? Any specific targets?" | Quantified: +3, Qualitative: +1 |
| **E**conomic buyer | "Who signs off on purchases like this?" | Identified: +3, Unknown: 0 |
| **D**ecision criteria | "What are you evaluating solutions on?" | Clear criteria: +3, Vague: +1 |
| **D**ecision process | "Walk me through your evaluation process?" | Defined: +3, Ad hoc: +1 |
| **P**aper process | "Is there a procurement or legal review needed?" | Known: +2, Unknown: 0 |
| **I**dentify pain | "What's the cost of not solving this?" | Quantified: +3, Felt: +1 |
| **C**hampion | "Is there someone internally advocating for this?" | Yes: +3, Maybe: +1 |
| **C**ompetition | "Are you evaluating other solutions?" | Exclusive: +3, Comparing: +1 |

**Qualification scoring:**

```python
from dataclasses import dataclass

@dataclass
class QualificationScore:
    framework: str                  # "bant" or "meddpicc"
    scores: dict[str, int]          # Dimension → score
    total: int
    tier: str                       # "hot", "warm", "cold"

def score_bant(slots: dict) -> QualificationScore:
    scores = {
        "budget": _score_budget(slots.get("budget")),
        "authority": _score_authority(slots.get("authority")),
        "need": _score_need(slots.get("need")),
        "timeline": _score_timeline(slots.get("timeline")),
    }
    total = sum(scores.values())
    tier = "hot" if total >= 9 else "warm" if total >= 5 else "cold"
    return QualificationScore("bant", scores, total, tier)
```

**Rules:**
- Ask qualification questions naturally, not as a survey. Weave them into conversation.
- Don't ask all questions if early answers disqualify. A "no budget, no timeline" lead doesn't need MEDDPICC.
- Score in real time so the bot can adjust behavior — hot leads get demo offers, cold leads get content.

## Demo and Meeting Booking

**Calendly integration:**

```python
class CalendlyClient:
    def __init__(self, api_token: str):
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    async def get_available_slots(
        self,
        event_type_uri: str,
        start: str,
        end: str,
    ) -> list[dict]:
        """Get available time slots for an event type."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/event_type_available_times",
                params={
                    "event_type": event_type_uri,
                    "start_time": start,
                    "end_time": end,
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()["collection"]

    async def create_scheduling_link(self, event_type_uri: str) -> str:
        """Create a one-time scheduling link for the prospect."""
        payload = {
            "max_event_count": 1,
            "owner": event_type_uri,
            "owner_type": "EventType",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/scheduling_links",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()["resource"]["booking_url"]
```

**Cal.com integration:**

```python
class CalComClient:
    def __init__(self, api_key: str, base_url: str = "https://api.cal.com/v2"):
        self.base_url = base_url
        self.headers = {
            "cal-api-version": "2024-08-13",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def get_available_slots(
        self,
        event_type_id: int,
        start: str,
        end: str,
    ) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/slots/available",
                params={
                    "startTime": start,
                    "endTime": end,
                    "eventTypeId": event_type_id,
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()["data"]["slots"]

    async def create_booking(
        self,
        event_type_id: int,
        start: str,
        attendee_name: str,
        attendee_email: str,
    ) -> dict:
        payload = {
            "start": start,
            "eventTypeId": event_type_id,
            "attendee": {
                "name": attendee_name,
                "email": attendee_email,
                "timeZone": "UTC",
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/bookings",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()["data"]
```

**Booking conversation pattern:**

```
Bot: "Want to see it in action? I can set up a quick 30-minute demo with our team."
User: "Sure"
Bot: "Great! I have slots available this week:
     • Tuesday March 31, 2:00 PM
     • Wednesday April 1, 10:00 AM
     • Thursday April 2, 3:00 PM
     Which works best? Or I can send you a link to pick your own time."
```

**Rules:**
- Always offer a scheduling link as an alternative to bot-proposed times.
- Collect the attendee's timezone before showing slots.
- Send a calendar invite and confirmation immediately after booking.
- Log the booking to the CRM as a deal activity.

## Objection Handling

Map common objections to response patterns. The bot should address the objection, not dismiss it.

**Objection response matrix:**

| Objection | Response strategy | Example response |
|-----------|------------------|------------------|
| **Price** | Acknowledge, reframe value, offer comparison | "That's a fair question. Most of our customers find the ROI comes from [specific value]. Want me to walk through the pricing options?" |
| **Timing** | Understand why, create urgency without pressure | "No rush at all. What would need to change for this to become a priority? I can send you some resources in the meantime." |
| **Competitor** | Differentiate on strengths, don't disparage | "Great that you're evaluating options. Where we tend to stand out is [differentiator]. Would a comparison be helpful?" |
| **Authority** | Offer to help champion | "Makes sense. Would it help if I prepared a one-pager for your team? I can include the key points to share with [decision-maker]." |
| **Already have a solution** | Find the gap | "Got it. Out of curiosity, is there anything about your current setup you wish worked differently?" |
| **Just browsing** | Provide value, keep the door open | "No problem. Here's a quick overview: [link]. Feel free to come back when you're ready — I'll be here." |

**Objection detection:**

```python
OBJECTION_CLASSIFIER_PROMPT = """Classify whether the user's message contains a sales objection.

Categories:
- price: Cost, budget, too expensive, pricing concern
- timing: Not now, too early, not a priority, bad timing
- competitor: Using another solution, evaluating alternatives
- authority: Not the decision-maker, need to check with someone
- existing_solution: Already have something that works
- browsing: Just looking, not ready to buy
- none: No objection detected

Respond with only the category name.

User message: {message}"""
```

**Rules:**
- Acknowledge the objection before responding. Never jump straight to a counter.
- Limit to one follow-up after an objection. Pushing harder is a disqualifier.
- If the same objection comes up twice, respect it and offer a lower-commitment next step (content, follow-up email).
- Log all objection types and outcomes for sales enablement insights.

## Follow-Up Automation

Trigger automated follow-ups based on conversation outcomes.

**Follow-up triggers:**

| Outcome | Follow-up action | Timing |
|---------|-----------------|--------|
| Demo booked | Confirmation email + calendar invite | Immediate |
| Qualified but no demo | Value email with case studies | 1 hour |
| Objection — timing | Check-in email | 2 weeks |
| Objection — authority | Champion kit email | 24 hours |
| Cold / browsing | Nurture drip sequence | 3 days |
| No response mid-conversation | Re-engagement message | 24 hours |

**Implementation:**

```python
from enum import Enum

class FollowUpType(str, Enum):
    DEMO_CONFIRMATION = "demo_confirmation"
    VALUE_EMAIL = "value_email"
    TIMING_CHECKIN = "timing_checkin"
    CHAMPION_KIT = "champion_kit"
    NURTURE_DRIP = "nurture_drip"
    RE_ENGAGEMENT = "re_engagement"

async def schedule_follow_up(
    contact_email: str,
    follow_up_type: FollowUpType,
    delay_minutes: int,
    context: dict,
):
    """Schedule an automated follow-up via the email/CRM system."""
    await task_queue.enqueue(
        task="send_follow_up",
        payload={
            "email": contact_email,
            "type": follow_up_type.value,
            "context": context,     # Qualification data, objection notes, etc.
        },
        delay_minutes=delay_minutes,
    )
```

**Rules:**
- Follow-up emails should reference the bot conversation ("Following up on our chat earlier...").
- Include the sales rep's name and contact info in follow-ups for warm leads.
- Never send more than 3 automated follow-ups per lead. After that, the rep should take over.
- For email engineering patterns, see [`../software-email-engineering/SKILL.md`](../../software-email-engineering/SKILL.md).

## Sales Bot Conversation Flows

### Inbound lead qualification

```
Bot:  "Hi! Welcome to [Product]. What brings you here today?"
User: "I'm looking for a project management tool for my team"
Bot:  "Great — how big is your team?"
User: "About 25 people"
Bot:  "Got it. Are you using anything currently, or starting fresh?"
User: "We're using Notion but it's not scaling well"
Bot:  "That's a common pain point. [Product] is built for teams your size.
       Want to see a quick demo? I can set one up for this week."
```

### Outbound reactivation

```
Bot:  "Hi [Name], we chatted a few weeks ago about [Product].
       You mentioned timing wasn't right. Just checking in —
       has anything changed on your end?"
User: "Actually, yes — we're starting to evaluate tools now"
Bot:  "Great timing. Last time you mentioned [pain point].
       We just shipped [relevant feature]. Want to pick up where we left off?"
```

### Pricing discussion

```
User: "How much does it cost?"
Bot:  "Our pricing depends on team size and features. A few quick questions
       so I can give you an accurate number:
       1. How many team members would use it?
       2. Do you need [premium feature] or [premium feature]?"
User: "15 people, and yes we'd need [premium feature]"
Bot:  "For 15 users with [premium feature], you'd be on our Growth plan at
       $X/user/month. That comes to $Y/month total. Want to try it free for 14 days,
       or shall I set up a demo with our team?"
```

## Handoff to Sales Rep

When the bot has qualified a lead, hand off to a human rep with all collected data.

**Handoff payload:**

```python
from dataclasses import dataclass

@dataclass
class SalesHandoffContext:
    # Lead data
    contact_name: str
    contact_email: str
    company: str | None
    team_size: str | None

    # Qualification
    qualification_score: dict       # Framework scores
    qualification_tier: str         # "hot", "warm", "cold"

    # Conversation insights
    pain_points: list[str]          # Identified pain points
    current_solution: str | None    # What they use today
    objections_raised: list[str]    # Objection types encountered
    decision_timeline: str | None   # When they want to decide
    decision_maker: str | None      # Who decides

    # Actions taken
    demo_booked: bool
    demo_datetime: str | None
    content_sent: list[str]         # Links/resources shared

    # Conversation
    summary: str                    # 3-4 sentence summary
    conversation_history: list[dict]
```

**Handoff message to rep (via Slack, email, or CRM notification):**

```python
HANDOFF_TEMPLATE = """
🔥 New {tier} lead from bot conversation

**Contact:** {name} ({email})
**Company:** {company} | **Team size:** {team_size}
**Score:** {score}/12 (BANT)

**Pain points:** {pain_points}
**Current solution:** {current_solution}
**Timeline:** {timeline}
**Objections:** {objections}

**Demo:** {"Booked for " + demo_datetime if demo_booked else "Not booked — follow up"}

**Summary:** {summary}

[View full conversation →]({conversation_link})
"""
```

**Rules:**
- Hot leads get immediate notification (Slack DM to assigned rep).
- Warm leads get CRM task assigned to next available rep.
- Cold leads go to nurture queue — no rep handoff needed.
- Include the conversation link so the rep can review the full context.
- The bot should tell the user what happens next: "I'm connecting you with [Rep Name] who'll be your main contact. They'll reach out within [timeframe]."
