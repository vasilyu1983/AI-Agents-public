# Pipecat Patterns

**Purpose**: Production patterns for building voice bots with the Pipecat framework — pipeline construction, processors, transports, state management, and deployment.

Pipecat is the default voice pipeline framework for this skill. Pure Python, composable processors, multi-transport.

> **Before copying code:** Pipecat's import paths and class names move between releases (services, transports, VAD, aggregators, and the runner have all been relocated at least once). Before pasting any block below, confirm each import against the installed package (`pip show pipecat-ai`, then `python -c "import <module>"`), the `examples/foundational/` folder of the pipecat-ai/pipecat repo, and docs.pipecat.ai. If a name below no longer imports, the repo examples are the source of truth, not this file.

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

The current shape: a shared `LLMContext` holds the conversation; `LLMContextAggregatorPair` produces the user-side and assistant-side aggregators that read and write it; VAD attaches to the user aggregator, not the transport; the pipeline runs inside a `PipelineWorker` driven by a `WorkerRunner`. `PipelineTask` / `PipelineRunner` still import but are deprecated aliases scheduled for removal — do not start new code on them.

```python
import os

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import DailyRunnerArguments, RunnerArguments
from pipecat.services.anthropic.llm import AnthropicLLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.transports.base_transport import BaseTransport
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.workers.runner import WorkerRunner


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    stt = DeepgramSTTService(api_key=os.environ["DEEPGRAM_API_KEY"])

    llm = AnthropicLLMService(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        settings=AnthropicLLMService.Settings(
            model="<current-claude-model-id>",
            system_instruction="You are a helpful phone assistant. Keep responses under 2 sentences.",
        ),
    )

    tts = ElevenLabsTTSService(
        api_key=os.environ["ELEVENLABS_API_KEY"],
        settings=ElevenLabsTTSService.Settings(voice=os.environ["ELEVENLABS_VOICE_ID"]),
    )

    context = LLMContext()
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline([
        transport.input(),     # Audio from user
        stt,                   # Speech-to-text
        user_aggregator,       # Turn detection + append user turn to context
        llm,                   # LLM streams response text
        tts,                   # Text-to-speech (aggregates sentences internally)
        transport.output(),    # Audio to user
        assistant_aggregator,  # Append what was actually spoken to context
    ])

    worker = PipelineWorker(pipeline, params=PipelineParams(enable_metrics=True))
    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
    await runner.add_workers(worker)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        context.add_message({"role": "user", "content": "Greet the caller briefly."})
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await runner.cancel()

    await runner.run()


async def bot(runner_args: DailyRunnerArguments):
    """Entry point for the Pipecat dev runner (`python bot.py -t daily`)."""
    transport = DailyTransport(
        room_url=runner_args.room_url,
        token=runner_args.token,
        bot_name="VoiceBot",
        params=DailyParams(audio_in_enabled=True, audio_out_enabled=True),
    )
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
```

The `pipecat.runner` dev runner (`pipecat-ai[runner]` extra) provides the `bot(runner_args)` convention, a local HTTP server, and transport selection. Check the exact `RunnerArguments` subclass fields for your transport (Daily vs WebSocket vs WebRTC) in `pipecat.runner.types` before relying on `room_url` / `token` / `websocket`.

### Pipeline Composition Pattern

Pipelines are lists of processors. Data flows left to right. Each processor receives frames, processes them, and emits frames downstream (and sometimes upstream, e.g. interruptions).

```python
pipeline = Pipeline([
    transport.input(),       # Source: produces audio frames
    noise_filter,            # Optional: audio filter (or use params.audio_in_filter on the transport)
    stt,                     # Audio frames -> TranscriptionFrame
    transcript_logger,       # Optional custom FrameProcessor
    user_aggregator,         # Turn end -> LLM context frame
    llm,                     # Context -> streamed LLMTextFrame
    tts,                     # Text -> audio frames
    transport.output(),      # Sink: sends audio to user
    assistant_aggregator,    # Records spoken text into context
])
```

Placement rules that matter:

- Put the assistant aggregator **after** `transport.output()`, so the context only records text that was actually played; on barge-in the unspoken tail is dropped.
- Barge-in is handled by the VAD inside the user aggregator plus the transport output, not by a separate parallel branch. `ParallelPipeline` (`pipecat.pipeline.parallel_pipeline`) exists for genuinely parallel fan-out (e.g. a second STT stream for compliance logging), not for interruption.
- TTS services aggregate streamed LLM text into sentences themselves (see `text_aggregation_mode` / `aggregate_sentences` on the TTS constructor); a standalone sentence aggregator before TTS is no longer part of the standard pipeline.

---

## Built-In Processors

Each provider lives in its own subpackage: `pipecat.services.<provider>.stt|tts|llm`. Install the matching extra (`pipecat-ai[deepgram]`, `pipecat-ai[elevenlabs]`, …). Provider coverage, language lists, and model names change often — check the provider's page under docs.pipecat.ai and the provider's own docs rather than the notes here.

### STT Processors

| Processor | Provider | Streaming | Notes |
|-----------|----------|-----------|-------|
| `DeepgramSTTService` | Deepgram | Yes | Default. Strong latency/accuracy balance for English. |
| `AzureSTTService` | Azure | Yes | Broad language coverage; enterprise. |
| `GoogleSTTService` | Google Cloud | Yes | Strong for non-English. |
| `WhisperSTTService` | Whisper (local) | Segment-based | High accuracy, higher latency; no network. |
| `AssemblyAISTTService` | AssemblyAI | Yes | Good for US English. |

**Default**: `DeepgramSTTService`. Leave the model at Pipecat's default unless you have measured a reason to pin one; set a model via `settings=DeepgramSTTService.Settings(...)`.

### TTS Processors

| Processor | Provider | Streaming | Notes |
|-----------|----------|-----------|-------|
| `ElevenLabsTTSService` | ElevenLabs | Yes | Default. Best perceived quality, voice cloning. |
| `CartesiaTTSService` | Cartesia | Yes | Lowest latency in this group; pick when latency wins over quality. |
| `AzureTTSService` | Azure | Yes | Enterprise, multilingual. |
| `GoogleTTSService` | Google Cloud | Yes | Good multilingual. |

**Default**: `ElevenLabsTTSService`. Pass the voice through `settings=ElevenLabsTTSService.Settings(voice=...)` (the bare `voice_id=` kwarg is deprecated). Choose the model from the provider's current low-latency tier.

### LLM Processors

| Processor | Provider | Streaming | Tool Calling | Notes |
|-----------|----------|-----------|-------------|-------|
| `AnthropicLLMService` | Anthropic | Yes | Yes | Default. Best for complex conversations. |
| `OpenAILLMService` | OpenAI | Yes | Yes | Use the provider's current small/fast tier for cost-sensitive bots. |
| `GoogleLLMService` | Google | Yes | Yes | Gemini for long context. |

Model, system prompt, `max_tokens`, and `temperature` go in `settings=<Service>.Settings(...)`; the same `LLMContext` works across providers.

### Utility Processors

| Component | Purpose |
|-----------|---------|
| `LLMContextAggregatorPair` | Builds the user and assistant aggregators over one `LLMContext`; owns turn detection (VAD, idle timeouts, mute strategies via `LLMUserAggregatorParams`). |
| `LLMContext` | The conversation: messages, tools, tool choice. Provider-agnostic. |
| TTS sentence aggregation | Built into every TTS service; tune with `text_aggregation_mode`. |
| `TranscriptionLogObserver` (`pipecat.observers.loggers`) | Logs transcripts as an observer on the worker rather than a pipeline stage. |
| User idle handling | `user_idle_timeout` on `LLMUserAggregatorParams` and `pipecat.turns.user_idle_controller`; check the docs for the current hook to prompt a silent user. |
| `ParallelPipeline` | Fan-out to parallel branches for a second STT, recording, or analytics stream. |

---

## Transport Layers

### Transport Comparison

| Transport | Protocol | Use Case | Phone Support | Multi-Party |
|-----------|----------|----------|---------------|-------------|
| `DailyTransport` | WebRTC | Web/mobile voice, internal tools | Via Daily SIP / dial-in | Yes |
| `FastAPIWebsocketTransport` + `TwilioFrameSerializer` | WebSocket | PSTN phone calls (Twilio Media Streams; Telnyx/Plivo/Exotel have serializers too) | Native | Via conference |
| `FastAPIWebsocketTransport` + `ProtobufFrameSerializer` | WebSocket | Custom clients, browser | No | No |
| `SmallWebRTCTransport` | WebRTC (peer) | Local dev, single-client browser demos; needs `pipecat-ai[webrtc]` | No | No |
| `LiveKitTransport` | WebRTC | Room-based, recording | Via SIP | Yes |

There is no `TwilioTransport` class: telephony is a generic WebSocket transport plus a provider-specific frame serializer. Modules: `pipecat.transports.daily.transport`, `pipecat.transports.websocket.fastapi`, `pipecat.transports.websocket.server`, `pipecat.serializers.twilio`.

### Twilio Transport Setup

```python
import os

from fastapi import FastAPI, WebSocket
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

app = FastAPI()


@app.websocket("/ws/twilio")
async def twilio_websocket(ws: WebSocket):
    await ws.accept()
    # Reads Twilio's "connected"/"start" messages and returns the stream/call SIDs.
    transport_type, call_data = await parse_telephony_websocket(ws)

    serializer = TwilioFrameSerializer(
        stream_sid=call_data["stream_id"],
        call_sid=call_data["call_id"],
        account_sid=os.environ["TWILIO_ACCOUNT_SID"],
        auth_token=os.environ["TWILIO_AUTH_TOKEN"],
    )
    transport = FastAPIWebsocketTransport(
        websocket=ws,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,   # Twilio wants raw mulaw, not WAV-framed audio
            serializer=serializer,  # Handles 8 kHz mulaw <-> PCM and Twilio JSON envelopes
        ),
    )
    # Build the pipeline and run the worker on this transport (see Simple Voice Bot).
```

`parse_telephony_websocket` returns a provider name and a dict; confirm the current key names (`stream_id`, `call_id`, …) in `pipecat.runner.utils` before relying on them. Passing `account_sid` / `auth_token` lets the serializer hang up the Twilio call when the pipeline ends. The serializer sets the 8 kHz sample rate for you; do not set `audio_in_sample_rate` to override it unless you have measured a reason.

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
from pipecat.transports.daily.transport import DailyParams, DailyTransport

transport = DailyTransport(
    room_url="https://your-domain.daily.co/room-name",
    token="your-meeting-token",
    bot_name="VoiceBot",
    params=DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
    ),
)
```

VAD is no longer configured on transport params; it belongs to `LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer())`. Daily's own transcription and dial-in settings are also `DailyParams` fields — check the model for the current names.

### WebSocket Transport Setup

For a custom (non-telephony) client, use the same FastAPI transport with the protobuf serializer, which is what the Pipecat client SDKs speak. For a standalone server without FastAPI, `WebsocketServerTransport` in `pipecat.transports.websocket.server` listens on its own port.

```python
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

transport = FastAPIWebsocketTransport(
    websocket=ws,
    params=FastAPIWebsocketParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        serializer=ProtobufFrameSerializer(),
    ),
)
```

---

## Custom Processor Development

### Processor Anatomy

```python
from pipecat.frames.frames import Frame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class CustomProcessor(FrameProcessor):
    """All custom processors extend FrameProcessor."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Required
        # Initialize your state here

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)  # Required: base class handles Start/End/Interruption

        if isinstance(frame, TranscriptionFrame):
            frame.text = self._transform(frame.text)

        await self.push_frame(frame, direction)  # Forward everything, in the same direction

    def _transform(self, text: str) -> str:
        return text
```

Three rules the base class relies on: call `super().__init__()`, call `await super().process_frame(frame, direction)` first, and push every frame you do not deliberately drop with its original `direction`. Frames to key on: `TranscriptionFrame` (final user text from STT), `InterimTranscriptionFrame`, `LLMTextFrame` (streamed bot text), `TTSSpeakFrame` (inject speech), `InputDTMFFrame`, `UserStartedSpeakingFrame` / `UserStoppedSpeakingFrame`, `InterruptionFrame`.

### Common Custom Processors

```python
import time

from pipecat.frames.frames import Frame, LLMTextFrame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class ProfanityFilter(FrameProcessor):
    """Mask blocked words in user transcripts before they reach the LLM."""

    BLOCKED_WORDS = {"damn", "hell"}  # Extend as needed

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame):
            for word in self.BLOCKED_WORDS:
                frame.text = frame.text.replace(word, "***")
        await self.push_frame(frame, direction)


class ConversationLogger(FrameProcessor):
    """Collect user and bot text for transcript storage."""

    def __init__(self, call_id: str, **kwargs):
        super().__init__(**kwargs)
        self.call_id = call_id
        self.transcript: list[dict] = []

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame):
            self._record("user", frame.text)
        elif isinstance(frame, LLMTextFrame):
            self._record("bot", frame.text)  # Streamed chunks; join per turn downstream
        await self.push_frame(frame, direction)

    def _record(self, speaker: str, text: str):
        self.transcript.append(
            {"call_id": self.call_id, "speaker": speaker, "text": text, "timestamp": time.time()}
        )
```

For production transcripts prefer `TranscriptionLogObserver` or your own observer attached to the `PipelineWorker`; observers see every frame without sitting in the data path. To cap response length, set `max_tokens` in the LLM `Settings` rather than dropping `LLMTextFrame`s in a processor — a dropping processor must also reset its counter on each new LLM response, and the context would still record the full text.

---

## State Management

### Pipeline Context

Conversation history lives in `LLMContext` (`context.messages`, `context.add_message(...)`); do not keep a second copy. Application state that is not part of the prompt — caller identity, intent, transfer flags, DTMF buffer — belongs in a plain object shared by your processors and tool handlers (pass it as `app_resources` on the `PipelineWorker`, which reaches tool handlers as `params.app_resources`).

```python
class VoiceBotState:
    """Non-prompt state shared across processors and tool handlers for one call."""

    def __init__(self, call_id: str):
        self.call_id = call_id
        self.user_profile: dict | None = None
        self.current_intent: str | None = None
        self.transfer_requested: bool = False
        self.dtmf_buffer: str = ""
```

Trim long conversations by editing `context` messages on a turn boundary, or enable the assistant aggregator's auto context summarization (`LLMAssistantAggregatorParams`) — check the current parameter name before enabling.

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

For multi-node scripted conversations (intake forms, qualification flows), evaluate Pipecat Flows before hand-rolling a state machine on top of the LLM context.

---

## Integration with LLM Frameworks

### Claude as the Brain

```python
import os

from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.services.anthropic.llm import AnthropicLLMService
from pipecat.services.llm_service import FunctionCallParams

SYSTEM_PROMPT = """You are a customer service phone agent for Acme Corp.
Rules:
- Keep responses under 2 sentences for voice delivery
- Never say "as an AI" or "I'm a language model"
- If you cannot help, say "Let me transfer you to a specialist"
- Use natural conversational language, not written-text style
- Spell out numbers: "twenty three", not "23"
- Avoid parenthetical asides — they sound unnatural when spoken"""

llm = AnthropicLLMService(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    settings=AnthropicLLMService.Settings(
        model="<current-claude-model-id>",
        system_instruction=SYSTEM_PROMPT,
        max_tokens=256,
        temperature=0.7,
    ),
)


# Tool calling: tools live on the context, handlers on the schema (or llm.register_function)
async def lookup_order(params: FunctionCallParams):
    order_number = params.arguments["order_number"]
    await params.llm.push_frame(TTSSpeakFrame("One moment while I look that up."))  # Filler speech
    order = await fetch_order(order_number)  # Your backend call
    await params.result_callback({"status": order.status, "eta": order.eta})


lookup_order_tool = FunctionSchema(
    name="lookup_order",
    description="Look up an order by order number",
    properties={"order_number": {"type": "string"}},
    required=["order_number"],
    handler=lookup_order,
)

context = LLMContext(tools=[lookup_order_tool])
```

Tool results go back through `params.result_callback(...)`; the LLM service then re-runs the model with the result in context. Keep handlers fast or speak a filler first — the caller hears silence while a tool runs.

### LangGraph Integration

Two workable shapes; pick by how much of the conversation the graph owns:

- **Graph as a tool.** Keep `AnthropicLLMService` as the conversational layer and expose the LangGraph agent as a `FunctionSchema` handler (above). Claude decides when to invoke it, the graph does the multi-step work, and the result comes back through `result_callback`. Lowest risk; latency is additive per invocation.
- **Graph as the LLM.** Replace the LLM stage with a custom service that consumes the frame the user aggregator emits and streams `LLMTextFrame`s back, bracketed by the LLM response start/end frames the TTS and assistant aggregator expect. The frame contract here has changed across releases, so build it from the current `examples/` and `pipecat.services.llm_service.LLMService` source rather than from memory. Also look at the `pipecat-ai[langchain]` extra, which ships an adapter for this shape.

Do not hand `TranscriptionFrame`s straight to a graph and push plain `TextFrame`s back: that bypasses turn detection, interruption handling, and the context aggregators.

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

**requirements.txt** (core — pin exact versions in your lockfile, not here):
```
pipecat-ai[daily,deepgram,elevenlabs,anthropic,silero,websocket,runner]
fastapi
uvicorn
twilio            # only for outbound dialing / REST; Media Streams need no SDK
```

There is no `twilio` extra on `pipecat-ai`; the `websocket` extra covers the FastAPI transport and serializers. Pipecat requires a current Python 3 (check `requires-python` in the package metadata). Confirm the extras list against `pip show pipecat-ai` or the repo's `pyproject.toml` — extras are added and renamed as providers are added.

### Cloud Deployment

| Provider | Service | Notes |
|----------|---------|-------|
| **Pipecat Cloud** | Managed | Runs `bot(runner_args)` as-is; lowest ops for Pipecat-native teams. |
| **AWS** | ECS Fargate or EC2 | Fargate for simplicity; EC2 for GPU if running local STT |
| **GCP** | Cloud Run or GKE | Cloud Run for auto-scaling; GKE for persistent connections |
| **Fly.io** | Machines | Good for WebSocket-heavy workloads, global edge |
| **Railway** | Container | Simple deploy, good for MVPs |

**Key deployment considerations:**
- WebSocket / WebRTC connections are long-lived (duration of call). Use services that support persistent connections.
- Serverless platforms have connection timeout limits. Verify they meet your max call duration.
- Deploy close to your STT/TTS providers to minimize network latency; check each provider's current region list.

### Scaling Patterns

- One `PipelineWorker` per call. Scale horizontally by running more instances; vertical scaling only matters if you host STT/TTS models locally.
- Per-call CPU and memory depend on the VAD, any local models, and the transport. Measure under your own load with realistic audio before sizing instances; do not size from a rule of thumb.
- Use a load balancer with WebSocket affinity (sticky sessions): a call must stay on the instance that owns its worker for its whole life.
- Drain instances on deploy instead of killing them: a rolling restart that cuts active calls is the most common self-inflicted outage.
- Enable `PipelineParams(enable_metrics=True, enable_usage_metrics=True)` from day one so TTFB, processing time, and token usage per stage are visible before you need them.

---

## Code Examples

### Simple Voice Bot

```python
"""Minimal phone bot: Twilio Media Streams -> Deepgram STT -> Claude -> ElevenLabs TTS -> phone."""
import os

from fastapi import FastAPI, Response, WebSocket
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.anthropic.llm import AnthropicLLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from pipecat.workers.runner import WorkerRunner

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
    _, call_data = await parse_telephony_websocket(ws)

    transport = FastAPIWebsocketTransport(
        websocket=ws,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            serializer=TwilioFrameSerializer(
                stream_sid=call_data["stream_id"],
                call_sid=call_data["call_id"],
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),
        ),
    )

    context = LLMContext()
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline([
        transport.input(),
        DeepgramSTTService(api_key=os.environ["DEEPGRAM_API_KEY"]),
        user_aggregator,
        AnthropicLLMService(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            settings=AnthropicLLMService.Settings(
                model="<current-claude-model-id>",
                system_instruction="You are a helpful phone assistant. Keep answers to 1-2 sentences.",
            ),
        ),
        ElevenLabsTTSService(
            api_key=os.environ["ELEVENLABS_API_KEY"],
            settings=ElevenLabsTTSService.Settings(voice=os.environ["ELEVENLABS_VOICE_ID"]),
        ),
        transport.output(),
        assistant_aggregator,
    ])

    worker = PipelineWorker(pipeline, params=PipelineParams(enable_metrics=True))
    runner = WorkerRunner(handle_sigint=False)
    await runner.add_workers(worker)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        context.add_message({"role": "user", "content": "Greet the caller in one sentence."})
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await runner.cancel()

    await runner.run()
```

Use `handle_sigint=False` inside a web server: the server owns signal handling, and one runner per request must not install process-wide handlers.

### IVR with DTMF

```python
"""IVR menu with DTMF input handling in Pipecat."""
from pipecat.frames.frames import Frame, InputDTMFFrame, TTSSpeakFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

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
    """Route calls based on DTMF keypress; let voice frames flow to the LLM untouched."""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, InputDTMFFrame):
            digit = frame.button.value  # KeypadEntry enum: "0"-"9", "*", "#"
            menu_item = IVR_MENU.get(digit)
            if menu_item:
                await self.push_frame(TTSSpeakFrame(menu_item["text"]))
                # Trigger action (transfer, lookup, etc.) via your state object
            else:
                await self.push_frame(TTSSpeakFrame("I didn't recognize that option. " + GREETING))
            return  # Consumed: do not forward the DTMF frame

        await self.push_frame(frame, direction)


# Pipeline: DTMF gets routed, voice input goes to LLM
pipeline = Pipeline([
    transport.input(),
    DTMFRouter(),          # Intercept DTMF, pass voice through
    stt,
    user_aggregator,
    llm,
    tts,
    transport.output(),
    assistant_aggregator,
])
```

`InputDTMFFrame` is a system frame emitted by telephony transports (Twilio, Daily dial-in) when the caller presses a key; `TTSSpeakFrame` speaks fixed text without a model call. To send tones (e.g. navigating a downstream IVR), push `OutputDTMFFrame`.

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

The Twilio REST client is synchronous; in a real dialer run `calls.create` in a thread (`asyncio.to_thread`) so the semaphore actually limits concurrency. The Pipecat dev runner also supports Daily dial-out (`DailyDialinRequest` / dial-out settings in `pipecat.runner.types`) if you would rather stay on Daily's telephony.

---

## Related References

- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Architecture that Pipecat implements
- [telephony-platform-selection.md](telephony-platform-selection.md) — Telephony platform (Pipecat transport layer)
- [latency-engineering.md](latency-engineering.md) — Optimizing Pipecat pipeline latency
- [livekit-agents-patterns.md](livekit-agents-patterns.md) — Alternative framework (LiveKit Agents)
- [ivr-design.md](ivr-design.md) — IVR flow design patterns
