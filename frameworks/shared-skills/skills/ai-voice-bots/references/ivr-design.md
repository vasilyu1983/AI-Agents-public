# IVR Design

**Purpose**: Design production IVR (Interactive Voice Response) flows — state machines, DTMF handling, hybrid voice+keypad, queue management, outbound dialing, agent handoff, and analytics.

No narrative. Patterns, code, and decision tables only.

> **Model ID freshness:** Code samples below use `<current-claude-model-id>` as a placeholder. Substitute your provider's current model identifier from its release notes at call time — model aliases and snapshot names drift faster than this file.

---
## Table of Contents

- [IVR State Machine Design](#ivr-state-machine-design)
- [State Machine Pattern](#state-machine-pattern)
- [State Transition Table](#state-transition-table)
- [Implementation (Python)](#implementation-python)
- [Hybrid Voice+Keypad Flows](#hybrid-voicekeypad-flows)
- [Dual-Modality Pattern](#dual-modality-pattern)
- [Implementation Pattern](#implementation-pattern)
- [Multi-Level Menu Design](#multi-level-menu-design)
- [Menu Design Rules](#menu-design-rules)
- [Menu Tree Template](#menu-tree-template)
- [Voice Prompt Best Practices](#voice-prompt-best-practices)
- [Queue Management](#queue-management)
- [Queue Configuration](#queue-configuration)
- [Position Announcements](#position-announcements)
- [Callback Offer Pattern](#callback-offer-pattern)
- [Outbound Dialing Patterns](#outbound-dialing-patterns)
- [Campaign Management](#campaign-management)
- [Retry Logic](#retry-logic)
- [Answering Machine Detection](#answering-machine-detection)
- [DNC List Compliance](#dnc-list-compliance)
- [IVR-to-Agent Handoff](#ivr-to-agent-handoff)
- [Warm Transfer with Context](#warm-transfer-with-context)
- [Handoff Data Payload](#handoff-data-payload)
- [IVR Analytics](#ivr-analytics)
- [Menu Path Analysis](#menu-path-analysis)
- [Key IVR Metrics](#key-ivr-metrics)
- [DTMF Integration with Pipecat/LiveKit](#dtmf-integration-with-pipecatlivekit)
- [Pipecat DTMF Handling](#pipecat-dtmf-handling)
- [LiveKit DTMF Handling](#livekit-dtmf-handling)
- [Related References](#related-references)

---

## IVR State Machine Design

### State Machine Pattern

Every IVR flow is a finite state machine. States represent what the system is doing. Transitions are triggered by user input (voice or DTMF) or timeouts.

```
┌─────────────┐    greeting    ┌─────────────┐
│   GREETING  │ ──────────────►│  MAIN_MENU  │
└─────────────┘    auto-play   └──────┬──────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                  │
                  DTMF 1           DTMF 2            DTMF 3
                    │                 │                  │
              ┌─────▼─────┐    ┌─────▼─────┐     ┌─────▼─────┐
              │   SALES   │    │  SUPPORT   │     │  BILLING  │
              └─────┬─────┘    └─────┬─────┘     └─────┬─────┘
                    │                │                  │
              ┌─────▼─────┐    ┌─────▼─────┐     ┌─────▼─────┐
              │ VOICE_BOT  │    │ VOICE_BOT │     │ VOICE_BOT │
              │ (AI agent) │    │ (AI agent)│     │ (AI agent)│
              └─────┬─────┘    └─────┬─────┘     └─────┬─────┘
                    │                │                  │
              ┌─────▼─────────────────▼──────────────────▼─────┐
              │              TRANSFER / END                      │
              └─────────────────────────────────────────────────┘
```

### State Transition Table

| Current State | Input | Next State | Action |
|--------------|-------|-----------|--------|
| GREETING | auto (after play) | MAIN_MENU | Play menu prompt |
| MAIN_MENU | DTMF 1 | SALES | Route to sales voice bot |
| MAIN_MENU | DTMF 2 | SUPPORT | Route to support voice bot |
| MAIN_MENU | DTMF 3 | BILLING | Route to billing voice bot |
| MAIN_MENU | DTMF 0 | OPERATOR | Transfer to human operator |
| MAIN_MENU | voice "sales" | SALES | NLU intent detection |
| MAIN_MENU | voice "help" | SUPPORT | NLU intent detection |
| MAIN_MENU | timeout (8s) | MAIN_MENU | Replay menu prompt |
| MAIN_MENU | timeout x3 | OPERATOR | Too many timeouts — transfer |
| VOICE_BOT | "transfer" intent | TRANSFER | Warm transfer to human |
| VOICE_BOT | call end | END | Log call, save transcript |
| ANY | DTMF * | MAIN_MENU | Return to main menu (escape hatch) |

### Implementation (Python)

```python
from enum import Enum
from dataclasses import dataclass, field

class IVRState(Enum):
    GREETING = "greeting"
    MAIN_MENU = "main_menu"
    SALES = "sales"
    SUPPORT = "support"
    BILLING = "billing"
    VOICE_BOT = "voice_bot"
    QUEUE = "queue"
    TRANSFER = "transfer"
    END = "end"

@dataclass
class IVRContext:
    state: IVRState = IVRState.GREETING
    department: str = ""
    timeout_count: int = 0
    dtmf_buffer: str = ""
    transcript: list[dict] = field(default_factory=list)
    caller_id: str = ""
    call_id: str = ""

class IVRStateMachine:
    """IVR state machine with DTMF and voice input handling."""

    MAX_TIMEOUTS = 3

    DTMF_ROUTES = {
        IVRState.MAIN_MENU: {
            "1": (IVRState.SALES, "sales"),
            "2": (IVRState.SUPPORT, "support"),
            "3": (IVRState.BILLING, "billing"),
            "0": (IVRState.TRANSFER, "operator"),
            "*": (IVRState.MAIN_MENU, ""),
        },
    }

    VOICE_INTENTS = {
        IVRState.MAIN_MENU: {
            "sales": IVRState.SALES,
            "buy": IVRState.SALES,
            "support": IVRState.SUPPORT,
            "help": IVRState.SUPPORT,
            "billing": IVRState.BILLING,
            "payment": IVRState.BILLING,
            "operator": IVRState.TRANSFER,
            "human": IVRState.TRANSFER,
        },
    }

    def __init__(self):
        self.ctx = IVRContext()

    def handle_dtmf(self, digit: str) -> tuple[IVRState, str]:
        """Process DTMF input. Returns (new_state, action)."""
        routes = self.DTMF_ROUTES.get(self.ctx.state, {})
        if digit in routes:
            new_state, department = routes[digit]
            self.ctx.state = new_state
            self.ctx.department = department
            self.ctx.timeout_count = 0
            return new_state, f"route_to_{department}" if department else "replay_menu"
        return self.ctx.state, "invalid_input"

    def handle_voice_intent(self, intent: str) -> tuple[IVRState, str]:
        """Process voice intent. Returns (new_state, action)."""
        intents = self.VOICE_INTENTS.get(self.ctx.state, {})
        if intent.lower() in intents:
            new_state = intents[intent.lower()]
            self.ctx.state = new_state
            self.ctx.timeout_count = 0
            return new_state, f"route_to_{intent.lower()}"
        return self.ctx.state, "unrecognized_intent"

    def handle_timeout(self) -> tuple[IVRState, str]:
        """Handle input timeout. Returns (new_state, action)."""
        self.ctx.timeout_count += 1
        if self.ctx.timeout_count >= self.MAX_TIMEOUTS:
            self.ctx.state = IVRState.TRANSFER
            return IVRState.TRANSFER, "timeout_transfer"
        return self.ctx.state, "replay_prompt"
```

---

## Hybrid Voice+Keypad Flows

### Dual-Modality Pattern

Always offer both voice and DTMF input. Users in noisy environments or with accents may prefer keypad. Users in quiet environments prefer voice.

**Prompt template:**
```
"Press 1 or say 'sales' for our sales team.
 Press 2 or say 'support' for technical support.
 Press 3 or say 'billing' for billing questions.
 Press 0 or say 'operator' for a live agent."
```

**Rules:**
- Always mention DTMF option first (faster for experienced callers)
- Keep voice alternative natural ("say 'sales'", not "say the word sales")
- Accept both modalities simultaneously (first valid input wins)
- If voice recognition fails, offer DTMF: "I didn't catch that. You can also press 1 for sales."

### Implementation Pattern

```python
import asyncio

async def wait_for_input(
    dtmf_queue: asyncio.Queue,
    voice_queue: asyncio.Queue,
    timeout_seconds: float = 8.0,
) -> tuple[str, str]:
    """
    Wait for either DTMF or voice input.
    Returns (input_type, value) — ("dtmf", "1") or ("voice", "sales").
    """
    dtmf_task = asyncio.create_task(dtmf_queue.get())
    voice_task = asyncio.create_task(voice_queue.get())

    done, pending = await asyncio.wait(
        {dtmf_task, voice_task},
        timeout=timeout_seconds,
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    if not done:
        return ("timeout", "")

    result_task = done.pop()
    if result_task is dtmf_task:
        return ("dtmf", result_task.result())
    else:
        return ("voice", result_task.result())
```

---

## Multi-Level Menu Design

### Menu Design Rules

| Rule | Guideline | Rationale |
|------|-----------|-----------|
| **Max depth** | 3 levels | Users lose context beyond 3 levels |
| **Max options per level** | 5 | More than 5 options → cognitive overload |
| **Escape hatch** | `*` returns to main menu, `0` always reaches operator | Users must never be trapped |
| **Timeout** | 8 seconds, replay prompt, transfer after 3 timeouts | Don't leave users in silence |
| **Confirmation** | Confirm before irreversible actions (transfer, cancel) | Prevent accidental actions |
| **Position** | Most popular option first, operator last | Optimize for common paths |

### Menu Tree Template

```
Level 0: Greeting
  "Thank you for calling Acme Corp."

Level 1: Main Menu
  [1] Sales → Level 2: Sales Submenu
  [2] Support → Level 2: Support Submenu
  [3] Billing → Voice Bot (billing agent)
  [0] Operator → Queue (human agent)

Level 2: Sales Submenu
  [1] New account → Voice Bot (sales agent)
  [2] Existing account → Voice Bot (account agent)
  [*] Main menu → Level 1

Level 2: Support Submenu
  [1] Technical issue → Voice Bot (support agent)
  [2] Returns → Voice Bot (returns agent)
  [3] Order status → Voice Bot (order agent)
  [*] Main menu → Level 1
```

### Voice Prompt Best Practices

| Practice | Bad | Good |
|----------|-----|------|
| Length | "Thank you for calling Acme Corporation, the world's leading provider of widgets and gadgets. We value your call." | "Thanks for calling Acme Corp." |
| Option count | 7 options in one prompt | Max 5, split into submenus |
| Option order | Random/alphabetical | Most popular first |
| Repeat info | Repeat the full greeting on replay | Only replay the menu options |
| Confirmation | "You said sales. Is that correct? Press 1 for yes, 2 for no." | "Connecting you to sales." (Only confirm irreversible actions) |

---

## Queue Management

### Queue Configuration

```python
@dataclass
class QueueConfig:
    max_wait_seconds: int = 300          # 5 minutes max wait
    position_announce_interval: int = 60  # Announce position every 60s
    callback_offer_after: int = 120       # Offer callback after 2 min
    hold_music_url: str = "https://example.com/hold-music.mp3"
    estimated_wait_formula: str = "avg_handle_time * queue_position / available_agents"
```

### Position Announcements

```python
POSITION_TEMPLATES = {
    1: "You're next in line. An agent will be with you shortly.",
    2: "There is one caller ahead of you. Estimated wait: about {wait} minutes.",
    3: "There are {position} callers ahead of you. Estimated wait: about {wait} minutes.",
}

def position_announcement(position: int, avg_wait_per_caller_s: int = 90) -> str:
    """Generate queue position announcement."""
    wait_minutes = max(1, round(position * avg_wait_per_caller_s / 60))

    if position <= 1:
        return POSITION_TEMPLATES[1]
    elif position == 2:
        return POSITION_TEMPLATES[2].format(wait=wait_minutes)
    else:
        return POSITION_TEMPLATES[3].format(position=position - 1, wait=wait_minutes)
```

### Callback Offer Pattern

```python
async def offer_callback(
    caller_number: str,
    queue_position: int,
    wait_estimate_s: int,
    dtmf_queue: asyncio.Queue,
    tts_client,
    audio_output,
):
    """Offer the caller a callback instead of waiting on hold."""
    if wait_estimate_s < 120:
        return False  # Don't offer callback for short waits

    prompt = (
        f"Your estimated wait is about {wait_estimate_s // 60} minutes. "
        "Press 1 to keep waiting, or press 2 and we'll call you back "
        "when an agent is available. You won't lose your place in line."
    )

    async for chunk in tts_client.synthesize_stream(prompt):
        await audio_output.put(chunk)

    try:
        digit = await asyncio.wait_for(dtmf_queue.get(), timeout=10.0)
        if digit == "2":
            # Schedule callback
            await schedule_callback(caller_number, queue_position)
            goodbye = "Got it. We'll call you back shortly. Goodbye!"
            async for chunk in tts_client.synthesize_stream(goodbye):
                await audio_output.put(chunk)
            return True
    except asyncio.TimeoutError:
        pass  # No response — keep them in queue

    return False
```

---

## Outbound Dialing Patterns

### Campaign Management

```python
from dataclasses import dataclass
from datetime import datetime, time

@dataclass
class DialingCampaign:
    campaign_id: str
    name: str
    numbers: list[str]
    max_concurrent: int = 10
    max_retries: int = 3
    retry_delay_minutes: int = 60
    calling_hours_start: time = time(9, 0)   # 9:00 AM local
    calling_hours_end: time = time(20, 0)     # 8:00 PM local
    voicemail_message: str = ""
    dnc_list_path: str = ""

    def is_within_calling_hours(self, local_time: datetime) -> bool:
        """Check if current time is within allowed calling hours."""
        current = local_time.time()
        return self.calling_hours_start <= current <= self.calling_hours_end
```

### Retry Logic

| Outcome | Retry? | Delay | Max Retries |
|---------|--------|-------|-------------|
| **No answer** | Yes | 60 min | 3 |
| **Busy** | Yes | 30 min | 3 |
| **Voicemail** | Yes (if no VM message) | 120 min | 2 |
| **Answered** | No | N/A | N/A |
| **Invalid number** | No | N/A | 0 |
| **DNC match** | No | N/A | 0 |
| **TCPA violation risk** | No | N/A | 0 |

```python
from enum import Enum

class DialOutcome(Enum):
    ANSWERED = "answered"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    VOICEMAIL = "voicemail"
    INVALID = "invalid"
    DNC = "dnc"
    ERROR = "error"

RETRY_CONFIG = {
    DialOutcome.NO_ANSWER: {"retry": True, "delay_min": 60, "max_retries": 3},
    DialOutcome.BUSY: {"retry": True, "delay_min": 30, "max_retries": 3},
    DialOutcome.VOICEMAIL: {"retry": True, "delay_min": 120, "max_retries": 2},
    DialOutcome.ANSWERED: {"retry": False},
    DialOutcome.INVALID: {"retry": False},
    DialOutcome.DNC: {"retry": False},
    DialOutcome.ERROR: {"retry": True, "delay_min": 15, "max_retries": 1},
}
```

### Answering Machine Detection

```python
async def handle_amd_result(
    amd_result: str,
    call_sid: str,
    campaign: DialingCampaign,
    tts_client,
    audio_output,
):
    """Handle Twilio AMD (Answering Machine Detection) result."""
    if amd_result == "human":
        # Human answered — run the voice bot pipeline
        return "start_conversation"
    elif amd_result == "machine_start":
        # Answering machine — leave voicemail if configured
        if campaign.voicemail_message:
            async for chunk in tts_client.synthesize_stream(campaign.voicemail_message):
                await audio_output.put(chunk)
            return "voicemail_left"
        return "voicemail_skip"
    elif amd_result == "fax":
        return "fax_detected"
    else:
        return "unknown"
```

### DNC List Compliance

```python
class DNCChecker:
    """Check numbers against Do-Not-Call lists."""

    def __init__(self, dnc_file: str):
        self._dnc_numbers: set[str] = set()
        self._load(dnc_file)

    def _load(self, path: str):
        with open(path) as f:
            for line in f:
                number = line.strip().replace("-", "").replace(" ", "")
                if number:
                    self._dnc_numbers.add(number)

    def is_blocked(self, number: str) -> bool:
        """Return True if the number is on the DNC list."""
        clean = number.replace("-", "").replace(" ", "").replace("+1", "")
        return clean in self._dnc_numbers

    def filter_campaign(self, numbers: list[str]) -> tuple[list[str], list[str]]:
        """Split numbers into dialable and blocked."""
        dialable = [n for n in numbers if not self.is_blocked(n)]
        blocked = [n for n in numbers if self.is_blocked(n)]
        return dialable, blocked
```

---

## IVR-to-Agent Handoff

### Warm Transfer with Context

A warm transfer passes conversation context to the human agent so the caller does not have to repeat themselves.

```python
async def warm_transfer(
    call_context: IVRContext,
    agent_queue: str,
    twilio_client,
):
    """Transfer call to human agent with full conversation context."""

    # Build context summary for the agent's screen
    handoff_data = {
        "call_id": call_context.call_id,
        "caller_id": call_context.caller_id,
        "department": call_context.department,
        "transcript_summary": summarize_transcript(call_context.transcript),
        "intent": call_context.transcript[-1].get("intent", "unknown") if call_context.transcript else "unknown",
        "ivr_path": [t.get("state") for t in call_context.transcript],
        "call_duration_s": call_context.transcript[-1].get("timestamp", 0) - call_context.transcript[0].get("timestamp", 0) if len(call_context.transcript) > 1 else 0,
    }

    # Send context to agent desktop via API/webhook
    await push_to_agent_desktop(agent_queue, handoff_data)

    # Transfer the call
    twilio_client.calls(call_context.call_id).update(
        twiml=f'<Response><Dial><Queue>{agent_queue}</Queue></Dial></Response>'
    )
```

### Handoff Data Payload

| Field | Source | Purpose |
|-------|--------|---------|
| `call_id` | Transport | Link to call recording |
| `caller_id` | Transport | Phone number / CRM lookup |
| `department` | IVR routing | Which team to transfer to |
| `transcript_summary` | LLM summarization | 2-3 sentence summary |
| `intent` | Voice bot NLU | What the caller wants |
| `ivr_path` | State machine | Menu path the caller took |
| `call_duration_s` | Timestamps | How long they've been waiting |
| `sentiment` | Voice bot analysis | Frustrated / neutral / positive |

---

## IVR Analytics

### Menu Path Analysis

```python
from collections import Counter

class IVRAnalytics:
    """Analyze IVR menu paths and abandonment."""

    def __init__(self):
        self.paths: list[list[str]] = []
        self.abandonment_states: list[str] = []

    def record_path(self, states: list[str], completed: bool):
        self.paths.append(states)
        if not completed:
            self.abandonment_states.append(states[-1])

    def top_paths(self, n: int = 10) -> list[tuple[str, int]]:
        """Most common menu paths."""
        path_strings = [" → ".join(p) for p in self.paths]
        return Counter(path_strings).most_common(n)

    def abandonment_by_state(self) -> dict[str, int]:
        """Where callers abandon."""
        return dict(Counter(self.abandonment_states))

    def option_popularity(self, state: str) -> dict[str, float]:
        """How often each option is selected at a given menu state."""
        transitions = []
        for path in self.paths:
            for i, s in enumerate(path):
                if s == state and i + 1 < len(path):
                    transitions.append(path[i + 1])
        counts = Counter(transitions)
        total = sum(counts.values()) or 1
        return {k: v / total for k, v in counts.most_common()}
```

### Key IVR Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Containment rate** | % of calls resolved by IVR/voice bot without human | > 60% |
| **Menu completion rate** | % of callers who successfully navigate to a destination | > 90% |
| **Avg. time to route** | Seconds from greeting to department/voice bot | < 30s |
| **Repeat menu plays** | % of callers hearing the menu more than once | < 20% |
| **Zero-out rate** | % of callers pressing 0 for operator | < 15% |
| **Abandonment rate** | % of callers hanging up during IVR | < 10% |
| **Top abandonment point** | State where most callers hang up | Investigate |

---

## DTMF Integration with Pipecat/LiveKit

### Pipecat DTMF Handling

```python
from pipecat.frames.frames import Frame, DTMFFrame
from pipecat.processors.frame_processor import FrameProcessor

class PipecatDTMFRouter(FrameProcessor):
    """Handle DTMF tones in a Pipecat pipeline."""

    def __init__(self, ivr: IVRStateMachine, **kwargs):
        super().__init__(**kwargs)
        self.ivr = ivr

    async def process_frame(self, frame: Frame, direction: str):
        if isinstance(frame, DTMFFrame):
            new_state, action = self.ivr.handle_dtmf(frame.digit)
            # Emit appropriate response based on action
            if action.startswith("route_to_"):
                department = action.replace("route_to_", "")
                await self.push_frame(
                    TextFrame(text=f"Connecting you to {department}.")
                )
            elif action == "replay_menu":
                await self.push_frame(
                    TextFrame(text="Press 1 for sales, 2 for support, 3 for billing.")
                )
            elif action == "invalid_input":
                await self.push_frame(
                    TextFrame(text="I didn't recognize that option. Please try again.")
                )
        else:
            await self.push_frame(frame)
```

### LiveKit DTMF Handling

```python
from livekit.agents.voice import VoicePipelineAgent

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=anthropic.LLM(model="<current-claude-model-id>"),
        tts=elevenlabs.TTS(voice="your-voice-id"),
    )

    ivr = IVRStateMachine()

    @ctx.room.on("sip_dtmf_received")
    async def on_dtmf(dtmf_event):
        digit = dtmf_event.digit
        new_state, action = ivr.handle_dtmf(digit)
        if action.startswith("route_to_"):
            department = action.replace("route_to_", "")
            await agent.say(f"Connecting you to {department}.")

    agent.start(ctx.room, participant)
    await agent.say(
        "Welcome. Press 1 for sales, 2 for support, "
        "3 for billing, or tell me how I can help."
    )
```

---

## Related References

- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Pipeline that powers the voice bot behind the IVR
- [pipecat-patterns.md](pipecat-patterns.md) — Pipecat IVR integration patterns
- [livekit-agents-patterns.md](livekit-agents-patterns.md) — LiveKit IVR integration patterns
- [voice-safety-compliance.md](voice-safety-compliance.md) — TCPA compliance for outbound dialing
- [telephony-platform-selection.md](telephony-platform-selection.md) — Platform for IVR telephony
- [voice-quality-metrics.md](voice-quality-metrics.md) — IVR analytics and call metrics
