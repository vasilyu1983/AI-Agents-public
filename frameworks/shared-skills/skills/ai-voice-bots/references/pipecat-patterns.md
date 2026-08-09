# Pipecat Patterns

**Purpose**: Production patterns for building voice bots with the Pipecat framework — pipeline construction, processors, transports, state management, and deployment.

Pipecat is the default voice pipeline framework for this skill. Pure Python, composable processors, multi-transport.

> **Model ID freshness:** Code samples below use `<current-claude-model-id>` as a placeholder. Substitute your provider's current model identifier from its release notes at call time — model aliases and snapshot names drift faster than this file.

---
## Table of Contents

- [Pipeline Construction](#pipeline-construction)
- [Minimal Pipeline](#minimal-pipeline)
- [Pipeline Composition Pattern](#pipeline-composition-pattern)
- [Built-In Processors](#built-in-processors)
- [STT Processors](#stt-processors)
- [TTS Processors](#tts-processors)
- [LLM Processors](#llm-processors)
- [Utility Processors](#utility-processors)
- [Transport Layers](#transport-layers)
- [Transport Comparison](#transport-comparison)
- [Twilio Transport Setup](#twilio-transport-setup)
- [Daily Transport Setup](#daily-transport-setup)
- [WebSocket Transport Setup](#websocket-transport-setup)
- [Custom Processor Development](#custom-processor-development)
- [Processor Anatomy](#processor-anatomy)
- [Common Custom Processors](#common-custom-processors)
- [State Management](#state-management)
- [Pipeline Context](#pipeline-context)
- [Conversation State Machine](#conversation-state-machine)
- [Integration with LLM Frameworks](#integration-with-llm-frameworks)
- [Claude as the Brain](#claude-as-the-brain)
- [LangGraph Integration](#langgraph-integration)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Scaling Patterns](#scaling-patterns)
- [Code Examples](#code-examples)
- [Simple Voice Bot](#simple-voice-bot)
- [IVR with DTMF](#ivr-with-dtmf)
- [Outbound Dialer](#outbound-dialer)
- [Related References](#related-references)

---

## Pipeline Construction

### Minimal Pipeline

```python
import asyncio
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.transports.services.daily import DailyTransport, DailyParams
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.anthropic import AnthropicLLMService
from pipecat.processors.aggregators.llm_response import LLMResponseAggregator
from pipecat.processors.aggregators.sentence import SentenceAggregator
from pipecat.vad.silero import SileroVADAnalyzer

async def main():
    transport = DailyTransport(
        room_url="https://your-domain.daily.co/room",
        token="your-token",
        bot_name="VoiceBot",
        params=DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    stt = DeepgramSTTService(api_key="your-key", model="nova-2")

    llm = AnthropicLLMService(
        api_key="your-key",
        model="<current-claude-model-id>",
        system_prompt="You are a helpful phone assistant. Keep responses under 2 sentences.",
    )

    tts = ElevenLabsTTSService(
        api_key="your-key",
        voice_id="your-voice-id",
        model="eleven_flash_v2_5",
    )

    pipeline = Pipeline([
        transport.input(),    # Audio from user
        stt,                  # Speech-to-text
        LLMResponseAggregator(),  # Buffer transcript for LLM
        llm,                  # LLM generates response
        SentenceAggregator(), # Buffer text by sentence for TTS
        tts,                  # Text-to-speech
        transport.output(),   # Audio to user
    ])

    task = PipelineTask(pipeline)
    runner = PipelineRunner()
    await runner.run(task)

if __name__ == "__main__":
    asyncio.run(main())
```

### Pipeline Composition Pattern

Pipelines are lists of processors. Data flows left to right. Each processor receives frames, processes them, and emits frames downstream.

```python
# Processors are composed in order
pipeline = Pipeline([
    transport.input(),         # Source: produces audio frames
    noise_filter,              # Optional: clean audio before STT
    stt,                       # STT: audio frames → text frames
    transcript_logger,         # Optional: log transcripts
    llm_aggregator,            # Buffer transcripts into LLM messages
    llm,                       # LLM: text → response text
    sentence_aggregator,       # Buffer response text by sentence
    tts,                       # TTS: text → audio frames
    transport.output(),        # Sink: sends audio frames to user
])

# Parallel pipelines for barge-in
pipeline = Pipeline([
    transport.input(),
    ParallelPipeline(          # Run STT and VAD in parallel
        [stt],
        [vad_barge_in],        # Barge-in processor cancels TTS
    ),
    llm_aggregator,
    llm,
    sentence_aggregator,
    tts,
    transport.output(),
])
```

---

## Built-In Processors

### STT Processors

| Processor | Provider | Streaming | Languages | Notes |
|-----------|----------|-----------|-----------|-------|
| `DeepgramSTTService` | Deepgram | Yes | 30+ | Default. Best latency/accuracy. |
| `AzureSTTService` | Azure Cognitive | Yes | 100+ | Best language coverage. |
| `GoogleSTTService` | Google Cloud | Yes | 125+ | Best for non-English. |
| `WhisperSTTService` | OpenAI Whisper | Batch only | 99 | High accuracy, higher latency. |
| `AssemblyAISTTService` | AssemblyAI | Yes | 20+ | Good for US English. |

**Default**: `DeepgramSTTService` with `nova-2` model — best latency/accuracy balance for English.

### TTS Processors

| Processor | Provider | Streaming | Voices | Notes |
|-----------|----------|-----------|--------|-------|
| `ElevenLabsTTSService` | ElevenLabs | Yes | 1000+ (cloned) | Default. Best quality. |
| `CartesiaTTSService` | Cartesia | Yes | 50+ | Lowest latency. |
| `AzureTTSService` | Azure | Yes | 400+ | Enterprise, multilingual. |
| `GoogleTTSService` | Google Cloud | Batch | 200+ | Good multilingual. |
| `PlayHTTTSService` | PlayHT | Yes | Custom | Voice cloning focus. |

**Default**: `ElevenLabsTTSService` with `eleven_flash_v2_5` (or the functionally-equivalent `eleven_turbo_v2_5` — both work) — best quality with streaming. Use `CartesiaTTSService` when latency is the top priority.

### LLM Processors

| Processor | Provider | Streaming | Tool Calling | Notes |
|-----------|----------|-----------|-------------|-------|
| `AnthropicLLMService` | Anthropic | Yes | Yes | Default. Best for complex conversations. |
| `OpenAILLMService` | OpenAI | Yes | Yes | Current GPT-5.x-family mini tier for cost-sensitive — verify current model IDs. |
| `GoogleLLMService` | Google | Yes | Yes | Gemini for long context. |

### Utility Processors

| Processor | Purpose |
|-----------|---------|
| `LLMResponseAggregator` | Buffers STT transcripts into complete messages for LLM |
| `SentenceAggregator` | Buffers LLM output into sentences for TTS (reduces choppiness) |
| `UserIdleProcessor` | Detects user silence and triggers prompts |
| `TranscriptionProcessor` | Logs full conversation transcript |
| `AudioVolumeProcessor` | Adjusts audio gain |

---

## Transport Layers

### Transport Comparison

| Transport | Protocol | Use Case | Phone Support | Multi-Party |
|-----------|----------|----------|---------------|-------------|
| `DailyTransport` | WebRTC | Web/mobile voice, internal tools | Via Daily SIP | Yes |
| `TwilioTransport` | WebSocket | PSTN phone calls | Native | Via conference |
| `WebSocketTransport` | WebSocket | Custom clients, browser | No | No |
| `LiveKitTransport` | WebRTC | Room-based, recording | Via SIP | Yes |

### Twilio Transport Setup

```python
from pipecat.transports.services.twilio import TwilioTransport, TwilioParams

transport = TwilioTransport(
    params=TwilioParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        audio_in_sample_rate=8000,   # PSTN: 8kHz
        audio_out_sample_rate=8000,
        vad_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
)

# FastAPI webhook to handle Twilio call
from fastapi import FastAPI, WebSocket
app = FastAPI()

@app.websocket("/ws/twilio")
async def twilio_websocket(ws: WebSocket):
    await ws.accept()
    transport.set_websocket(ws)
    # Pipeline runs on this WebSocket connection
    task = PipelineTask(pipeline)
    runner = PipelineRunner()
    await runner.run(task)
```

**TwiML to connect Twilio to your WebSocket:**
```xml
<Response>
    <Connect>
        <Stream url="wss://your-server.com/ws/twilio" />
    </Connect>
</Response>
```

### Daily Transport Setup

```python
from pipecat.transports.services.daily import DailyTransport, DailyParams

transport = DailyTransport(
    room_url="https://your-domain.daily.co/room-name",
    token="your-meeting-token",
    bot_name="VoiceBot",
    params=DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        audio_in_sample_rate=16000,  # WebRTC: 16kHz
        audio_out_sample_rate=16000,
        vad_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
)
```

### WebSocket Transport Setup

```python
from pipecat.transports.services.websocket import WebSocketTransport, WebSocketParams

transport = WebSocketTransport(
    params=WebSocketParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        audio_in_sample_rate=16000,
        audio_out_sample_rate=16000,
        vad_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
)
```

---

## Custom Processor Development

### Processor Anatomy

```python
from pipecat.frames.frames import Frame, TextFrame, AudioRawFrame
from pipecat.processors.frame_processor import FrameProcessor

class CustomProcessor(FrameProcessor):
    """All custom processors extend FrameProcessor."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize your state here

    async def process_frame(self, frame: Frame, direction: str):
        """Process a single frame. Called for every frame that passes through."""

        if isinstance(frame, TextFrame):
            # Transform text frames
            modified_text = self._transform(frame.text)
            await self.push_frame(TextFrame(text=modified_text))
        else:
            # Pass through frames you don't handle
            await self.push_frame(frame)

    def _transform(self, text: str) -> str:
        # Your transformation logic
        return text
```

### Common Custom Processors

```python
class ProfanityFilter(FrameProcessor):
    """Filter profanity from STT output before sending to LLM."""

    BLOCKED_WORDS = {"damn", "hell"}  # Extend as needed

    async def process_frame(self, frame: Frame, direction: str):
        if isinstance(frame, TextFrame):
            clean = frame.text
            for word in self.BLOCKED_WORDS:
                clean = clean.replace(word, "***")
            await self.push_frame(TextFrame(text=clean))
        else:
            await self.push_frame(frame)


class ConversationLogger(FrameProcessor):
    """Log all text frames for transcript storage."""

    def __init__(self, call_id: str, **kwargs):
        super().__init__(**kwargs)
        self.call_id = call_id
        self.transcript: list[dict] = []

    async def process_frame(self, frame: Frame, direction: str):
        if isinstance(frame, TextFrame):
            self.transcript.append({
                "call_id": self.call_id,
                "speaker": "user" if direction == "downstream" else "bot",
                "text": frame.text,
                "timestamp": time.time(),
            })
        await self.push_frame(frame)  # Always pass through


class ResponseLengthGuard(FrameProcessor):
    """Truncate LLM responses that exceed a character limit."""

    def __init__(self, max_chars: int = 500, **kwargs):
        super().__init__(**kwargs)
        self.max_chars = max_chars
        self._char_count = 0

    async def process_frame(self, frame: Frame, direction: str):
        if isinstance(frame, TextFrame):
            remaining = self.max_chars - self._char_count
            if remaining <= 0:
                return  # Drop excess text
            truncated = frame.text[:remaining]
            self._char_count += len(truncated)
            await self.push_frame(TextFrame(text=truncated))
        else:
            await self.push_frame(frame)
```

---

## State Management

### Pipeline Context

```python
from pipecat.pipeline.pipeline import Pipeline

class VoiceBotContext:
    """Shared state across all processors in a pipeline."""

    def __init__(self, call_id: str):
        self.call_id = call_id
        self.conversation_history: list[dict] = []
        self.user_profile: dict | None = None
        self.current_intent: str | None = None
        self.transfer_requested: bool = False
        self.dtmf_buffer: str = ""

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def get_llm_messages(self) -> list[dict]:
        return self.conversation_history[-20:]  # Keep last 20 turns for context window
```

### Conversation State Machine

```python
from enum import Enum

class CallState(Enum):
    GREETING = "greeting"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    DTMF_MENU = "dtmf_menu"
    TRANSFERRING = "transferring"
    ENDING = "ending"

class CallStateMachine:
    """Manages call state transitions."""

    VALID_TRANSITIONS = {
        CallState.GREETING: {CallState.LISTENING, CallState.DTMF_MENU},
        CallState.LISTENING: {CallState.PROCESSING, CallState.DTMF_MENU, CallState.ENDING},
        CallState.PROCESSING: {CallState.RESPONDING, CallState.TRANSFERRING},
        CallState.RESPONDING: {CallState.LISTENING, CallState.ENDING},
        CallState.DTMF_MENU: {CallState.LISTENING, CallState.TRANSFERRING, CallState.ENDING},
        CallState.TRANSFERRING: {CallState.ENDING},
        CallState.ENDING: set(),
    }

    def __init__(self):
        self.state = CallState.GREETING

    def transition(self, new_state: CallState) -> bool:
        if new_state in self.VALID_TRANSITIONS.get(self.state, set()):
            self.state = new_state
            return True
        return False
```

---

## Integration with LLM Frameworks

### Claude as the Brain

```python
from pipecat.services.anthropic import AnthropicLLMService

llm = AnthropicLLMService(
    api_key="your-key",
    model="<current-claude-model-id>",
    system_prompt="""You are a customer service phone agent for Acme Corp.
Rules:
- Keep responses under 2 sentences for voice delivery
- Never say "as an AI" or "I'm a language model"
- If you cannot help, say "Let me transfer you to a specialist"
- Use natural conversational language, not written-text style
- Spell out numbers: "twenty three", not "23"
- Avoid parenthetical asides — they sound unnatural when spoken""",
    params={
        "max_tokens": 256,
        "temperature": 0.7,
    },
)

# With tool calling
llm = AnthropicLLMService(
    api_key="your-key",
    model="<current-claude-model-id>",
    system_prompt="You are a phone agent. Use tools to look up orders.",
    tools=[
        {
            "name": "lookup_order",
            "description": "Look up an order by order number",
            "input_schema": {
                "type": "object",
                "properties": {
                    "order_number": {"type": "string"},
                },
                "required": ["order_number"],
            },
        },
    ],
)
```

### LangGraph Integration

```python
from langgraph.graph import StateGraph
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.frames.frames import TextFrame

class LangGraphProcessor(FrameProcessor):
    """Use a LangGraph agent as the LLM brain in a Pipecat pipeline."""

    def __init__(self, graph: StateGraph, **kwargs):
        super().__init__(**kwargs)
        self.graph = graph.compile()

    async def process_frame(self, frame: Frame, direction: str):
        if isinstance(frame, TextFrame):
            # Run the LangGraph agent
            result = await self.graph.ainvoke({
                "messages": [{"role": "user", "content": frame.text}],
            })
            # Extract the response text
            response = result["messages"][-1].content
            await self.push_frame(TextFrame(text=response))
        else:
            await self.push_frame(frame)

# Use in pipeline
pipeline = Pipeline([
    transport.input(),
    stt,
    LLMResponseAggregator(),
    LangGraphProcessor(graph=my_agent_graph),
    SentenceAggregator(),
    tts,
    transport.output(),
])
```

---

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# System deps for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

**requirements.txt** (core):
```
pipecat-ai[daily,twilio,deepgram,elevenlabs,anthropic,silero]>=0.0.50
fastapi>=0.115.0
uvicorn>=0.34.0
websockets>=13.0
```

### Cloud Deployment

| Provider | Service | Notes |
|----------|---------|-------|
| **AWS** | ECS Fargate or EC2 | Fargate for simplicity; EC2 for GPU if running local STT |
| **GCP** | Cloud Run or GKE | Cloud Run for auto-scaling; GKE for persistent connections |
| **Fly.io** | Machines | Good for WebSocket-heavy workloads, global edge |
| **Railway** | Container | Simple deploy, good for MVPs |

**Key deployment considerations:**
- WebSocket connections are long-lived (duration of call). Use services that support persistent connections.
- Cloud Run and Lambda have WebSocket timeout limits. Verify they meet your max call duration.
- Deploy close to your STT/TTS providers to minimize network latency (US East for Deepgram/ElevenLabs).

### Scaling Patterns

```python
# One pipeline task per call — scale by running more instances
# Each call = ~50MB RAM + 1 CPU core (with Silero VAD)

# Horizontal scaling: run N container instances
# Vertical: not needed unless running local STT/TTS models

# Connection routing: use a load balancer that supports WebSocket affinity
# (sticky sessions — the same call must stay on the same instance)
```

| Concurrent Calls | Instances (2 vCPU, 4GB) | Notes |
|-----------------|-------------------------|-------|
| 1-5 | 1 | MVP/development |
| 5-20 | 2-4 | Small production |
| 20-100 | 5-15 | Scale with load balancer |
| 100-500 | 15-60 | Dedicated cluster, monitoring critical |
| 500+ | 60+ | Contact provider for volume discounts |

---

## Code Examples

### Simple Voice Bot

```python
"""Minimal voice bot: Twilio phone → Deepgram STT → Claude → ElevenLabs TTS → phone."""
import asyncio
from fastapi import FastAPI, WebSocket, Response
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.transports.services.twilio import TwilioTransport, TwilioParams
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.anthropic import AnthropicLLMService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.processors.aggregators.llm_response import LLMResponseAggregator
from pipecat.processors.aggregators.sentence import SentenceAggregator
from pipecat.vad.silero import SileroVADAnalyzer

app = FastAPI()

@app.post("/twiml")
async def twiml():
    return Response(
        content='<Response><Connect><Stream url="wss://your-server.com/ws" /></Connect></Response>',
        media_type="application/xml",
    )

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    transport = TwilioTransport(
        params=TwilioParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )
    transport.set_websocket(ws)

    pipeline = Pipeline([
        transport.input(),
        DeepgramSTTService(api_key="DEEPGRAM_KEY", model="nova-2"),
        LLMResponseAggregator(),
        AnthropicLLMService(
            api_key="ANTHROPIC_KEY",
            model="<current-claude-model-id>",
            system_prompt="You are a helpful phone assistant. Keep answers to 1-2 sentences.",
        ),
        SentenceAggregator(),
        ElevenLabsTTSService(api_key="ELEVENLABS_KEY", voice_id="VOICE_ID"),
        transport.output(),
    ])

    await PipelineRunner().run(PipelineTask(pipeline))
```

### IVR with DTMF

```python
"""IVR menu with DTMF input handling in Pipecat."""
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.frames.frames import Frame, TextFrame, DTMFFrame

IVR_MENU = {
    "1": {"text": "Connecting you to sales.", "action": "transfer_sales"},
    "2": {"text": "Let me look up your order.", "action": "order_lookup"},
    "3": {"text": "I'll connect you with support.", "action": "transfer_support"},
    "0": {"text": "Transferring to an operator.", "action": "transfer_operator"},
}

GREETING = (
    "Welcome to Acme Corp. "
    "Press 1 for sales, 2 for order status, 3 for support, "
    "or say what you need and I'll help you directly."
)

class DTMFRouter(FrameProcessor):
    """Route calls based on DTMF keypress."""

    async def process_frame(self, frame: Frame, direction: str):
        if isinstance(frame, DTMFFrame):
            digit = frame.digit
            menu_item = IVR_MENU.get(digit)
            if menu_item:
                await self.push_frame(TextFrame(text=menu_item["text"]))
                # Trigger action (transfer, lookup, etc.)
            else:
                await self.push_frame(
                    TextFrame(text="I didn't recognize that option. " + GREETING)
                )
        else:
            # Non-DTMF frames pass through to LLM for voice handling
            await self.push_frame(frame)

# Pipeline: DTMF gets routed, voice input goes to LLM
pipeline = Pipeline([
    transport.input(),
    DTMFRouter(),       # Intercept DTMF, pass voice through
    stt,
    llm_aggregator,
    llm,
    sentence_aggregator,
    tts,
    transport.output(),
])
```

### Outbound Dialer

```python
"""Outbound dialer: initiate calls and run voice bot pipeline."""
import asyncio
from twilio.rest import Client as TwilioClient

twilio_client = TwilioClient("ACCOUNT_SID", "AUTH_TOKEN")

async def initiate_outbound_call(
    to_number: str,
    from_number: str,
    webhook_url: str,
) -> str:
    """Start an outbound call that connects to our voice bot pipeline."""
    call = twilio_client.calls.create(
        to=to_number,
        from_=from_number,
        url=webhook_url,  # TwiML endpoint that streams to our WebSocket
        status_callback=f"{webhook_url}/status",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
        machine_detection="Enable",  # Detect answering machines
        machine_detection_timeout=5,
    )
    return call.sid

async def batch_dial(
    numbers: list[str],
    from_number: str,
    webhook_url: str,
    max_concurrent: int = 10,
):
    """Batch dial with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def dial_one(number: str):
        async with semaphore:
            try:
                sid = await initiate_outbound_call(number, from_number, webhook_url)
                return {"number": number, "sid": sid, "status": "initiated"}
            except Exception as e:
                return {"number": number, "error": str(e), "status": "failed"}

    results = await asyncio.gather(*[dial_one(n) for n in numbers])
    return results
```

---

## Related References

- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Architecture that Pipecat implements
- [telephony-platform-selection.md](telephony-platform-selection.md) — Telephony platform (Pipecat transport layer)
- [latency-engineering.md](latency-engineering.md) — Optimizing Pipecat pipeline latency
- [livekit-agents-patterns.md](livekit-agents-patterns.md) — Alternative framework (LiveKit Agents)
- [ivr-design.md](ivr-design.md) — IVR flow design patterns
