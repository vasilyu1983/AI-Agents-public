# LiveKit Agents Patterns

**Purpose**: Production patterns for building voice bots with LiveKit Agents — VoicePipelineAgent, room management, plugins, multi-participant calls, and deployment.

Use LiveKit Agents when you need room-based voice, built-in recording, multi-participant calls, or are already on LiveKit infrastructure. Otherwise, default to Pipecat.

> **Model ID freshness:** Code samples below use `<current-claude-model-id>` as a placeholder. Substitute your provider's current model identifier from its release notes at call time — model aliases and snapshot names drift faster than this file.

---
## Table of Contents

- [VoicePipelineAgent Setup](#voicepipelineagent-setup)
- [Minimal Agent](#minimal-agent)
- [Configuration Options](#configuration-options)
- [Room Management](#room-management)
- [Room Lifecycle](#room-lifecycle)
- [Participant Handling](#participant-handling)
- [STT/TTS Plugin Ecosystem](#stttts-plugin-ecosystem)
- [STT Plugins](#stt-plugins)
- [TTS Plugins](#tts-plugins)
- [LLM Plugins](#llm-plugins)
- [Multi-Participant Call Handling](#multi-participant-call-handling)
- [Conference Pattern](#conference-pattern)
- [Selective Processing](#selective-processing)
- [Recording and Transcription](#recording-and-transcription)
- [Recording Setup](#recording-setup)
- [Live Transcription](#live-transcription)
- [Deployment](#deployment)
- [LiveKit Cloud](#livekit-cloud)
- [Self-Hosted LiveKit Server](#self-hosted-livekit-server)
- [Agent Worker Deployment](#agent-worker-deployment)
- [Code Examples](#code-examples)
- [Simple Voice Agent](#simple-voice-agent)
- [Customer Service Bot with Tools](#customer-service-bot-with-tools)
- [Related References](#related-references)

---

## VoicePipelineAgent Setup

### Minimal Agent

```python
import asyncio
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice import VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, anthropic, silero

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for a participant to join
    participant = await ctx.wait_for_participant()

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=anthropic.LLM(
            model="<current-claude-model-id>",
            system_prompt="You are a helpful phone assistant. Keep responses to 1-2 sentences.",
        ),
        tts=elevenlabs.TTS(
            model="eleven_flash_v2_5",
            voice="your-voice-id",
        ),
    )

    agent.start(ctx.room, participant)
    await agent.say("Hello! How can I help you today?")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

### Configuration Options

```python
agent = VoicePipelineAgent(
    vad=silero.VAD.load(
        min_speech_duration=0.25,   # seconds
        min_silence_duration=0.3,   # seconds
        activation_threshold=0.5,
    ),
    stt=deepgram.STT(
        model="nova-2",
        language="en-US",
        interim_results=True,
    ),
    llm=anthropic.LLM(
        model="<current-claude-model-id>",
        temperature=0.7,
        max_tokens=256,
    ),
    tts=elevenlabs.TTS(
        model="eleven_flash_v2_5",
        voice="your-voice-id",
        optimize_streaming_latency=4,  # 1-4, higher = lower latency
    ),
    # Pipeline behavior
    allow_interruptions=True,            # Barge-in support
    interrupt_speech_duration=0.5,       # Seconds of speech before interrupting
    interrupt_min_words=2,               # Min words before allowing interrupt
    min_endpointing_delay=0.5,           # Seconds of silence before end-of-turn
    preemptive_synthesis=True,           # Start TTS before LLM finishes
)
```

---

## Room Management

### Room Lifecycle

```python
from livekit import api as livekit_api

async def create_room(room_name: str) -> str:
    """Create a LiveKit room and return a token for the agent."""
    lk = livekit_api.LiveKitAPI(
        url="wss://your-project.livekit.cloud",
        api_key="your-api-key",
        api_secret="your-api-secret",
    )

    # Create room
    room = await lk.room.create_room(
        livekit_api.CreateRoomRequest(
            name=room_name,
            empty_timeout=300,      # Close room after 5 min of no participants
            max_participants=10,
        )
    )

    # Generate participant token
    token = (
        livekit_api.AccessToken(api_key="your-api-key", api_secret="your-api-secret")
        .with_identity("user-123")
        .with_grants(
            livekit_api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        .to_jwt()
    )

    return token
```

### Participant Handling

```python
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Handle participant events
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        print(f"Participant joined: {participant.identity}")

    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant):
        print(f"Participant left: {participant.identity}")

    # Wait for first participant
    participant = await ctx.wait_for_participant()

    # Access participant metadata
    identity = participant.identity
    metadata = participant.metadata  # JSON string with custom data
```

---

## STT/TTS Plugin Ecosystem

### STT Plugins

| Plugin | Provider | Install | Notes |
|--------|----------|---------|-------|
| `livekit.plugins.deepgram` | Deepgram | `pip install livekit-plugins-deepgram` | Default. Best latency. |
| `livekit.plugins.azure` | Azure Cognitive | `pip install livekit-plugins-azure` | Best language coverage. |
| `livekit.plugins.google` | Google Cloud | `pip install livekit-plugins-google` | Good multilingual. |

```python
# Deepgram (default)
stt = deepgram.STT(model="nova-2", language="en-US")

# Azure
from livekit.plugins import azure
stt = azure.STT(language="en-US", region="eastus")
```

### TTS Plugins

| Plugin | Provider | Install | Notes |
|--------|----------|---------|-------|
| `livekit.plugins.elevenlabs` | ElevenLabs | `pip install livekit-plugins-elevenlabs` | Best quality. |
| `livekit.plugins.cartesia` | Cartesia | `pip install livekit-plugins-cartesia` | Lowest latency. |
| `livekit.plugins.azure` | Azure | `pip install livekit-plugins-azure` | Enterprise multilingual. |
| `livekit.plugins.google` | Google Cloud | `pip install livekit-plugins-google` | Good multilingual. |

```python
# ElevenLabs (default)
tts = elevenlabs.TTS(model="eleven_flash_v2_5", voice="your-voice-id")

# Cartesia (lowest latency)
from livekit.plugins import cartesia
tts = cartesia.TTS(model="sonic-english", voice="your-voice-id")
```

### LLM Plugins

| Plugin | Provider | Install | Notes |
|--------|----------|---------|-------|
| `livekit.plugins.anthropic` | Anthropic | `pip install livekit-plugins-anthropic` | Default for complex conversations. |
| `livekit.plugins.openai` | OpenAI | `pip install livekit-plugins-openai` | Current GPT-5.x-family flagship/mini, tool calling — verify current model IDs. |
| `livekit.plugins.google` | Google | `pip install livekit-plugins-google` | Gemini, long context. |

---

## Multi-Participant Call Handling

### Conference Pattern

```python
async def entrypoint(ctx: JobContext):
    """Voice bot that interacts with multiple participants in a room."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agents: dict[str, VoicePipelineAgent] = {}

    @ctx.room.on("participant_connected")
    async def on_participant_connected(participant):
        # Create a dedicated agent for each participant
        agent = VoicePipelineAgent(
            vad=silero.VAD.load(),
            stt=deepgram.STT(model="nova-2"),
            llm=anthropic.LLM(model="<current-claude-model-id>"),
            tts=elevenlabs.TTS(voice="your-voice-id"),
        )
        agent.start(ctx.room, participant)
        agents[participant.identity] = agent

    @ctx.room.on("participant_disconnected")
    async def on_participant_disconnected(participant):
        agent = agents.pop(participant.identity, None)
        if agent:
            await agent.close()
```

### Selective Processing

```python
async def entrypoint(ctx: JobContext):
    """Bot that only responds to specific participants."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Only interact with the primary caller, not other agents/supervisors
    participant = await ctx.wait_for_participant(
        identity="caller"  # Match specific participant identity
    )

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=anthropic.LLM(model="<current-claude-model-id>"),
        tts=elevenlabs.TTS(voice="your-voice-id"),
    )
    agent.start(ctx.room, participant)
```

---

## Recording and Transcription

### Recording Setup

```python
from livekit import api as livekit_api

async def start_recording(room_name: str) -> str:
    """Start recording a LiveKit room to cloud storage."""
    lk = livekit_api.LiveKitAPI(
        url="wss://your-project.livekit.cloud",
        api_key="your-api-key",
        api_secret="your-api-secret",
    )

    # Start egress (recording)
    egress = await lk.egress.start_room_composite_egress(
        livekit_api.RoomCompositeEgressRequest(
            room_name=room_name,
            file=livekit_api.EncodedFileOutput(
                file_type=livekit_api.EncodedFileType.OGG,
                filepath="recordings/{room_name}/{time}.ogg",
                s3=livekit_api.S3Upload(
                    bucket="your-bucket",
                    region="us-east-1",
                    access_key="AWS_KEY",
                    secret="AWS_SECRET",
                ),
            ),
            audio_only=True,
        )
    )

    return egress.egress_id
```

### Live Transcription

```python
async def entrypoint(ctx: JobContext):
    """Agent with real-time transcription logging."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=anthropic.LLM(model="<current-claude-model-id>"),
        tts=elevenlabs.TTS(voice="your-voice-id"),
    )

    # Listen for transcription events
    @agent.on("user_speech_committed")
    def on_user_speech(text: str):
        # Store user transcript
        print(f"User: {text}")
        # await save_transcript(call_id, "user", text)

    @agent.on("agent_speech_committed")
    def on_agent_speech(text: str):
        # Store agent transcript
        print(f"Agent: {text}")
        # await save_transcript(call_id, "agent", text)

    agent.start(ctx.room, participant)
```

---

## Deployment

### LiveKit Cloud

The managed option. LiveKit hosts the SFU (Selective Forwarding Unit); you deploy agent workers that connect to it.

```bash
# Install LiveKit CLI
pip install livekit-cli

# Deploy agent worker (connects to LiveKit Cloud)
LIVEKIT_URL=wss://your-project.livekit.cloud \
LIVEKIT_API_KEY=your-key \
LIVEKIT_API_SECRET=your-secret \
python agent.py start
```

**LiveKit Cloud pricing (May 2026; verify before budgeting):**
- ~$0.004/participant-minute for audio
- Recording egress: ~$0.02/minute
- Free tier: 5,000 participant-minutes/month

### Self-Hosted LiveKit Server

```bash
# Docker deployment of LiveKit server
docker run -d \
  --name livekit \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  -v /path/to/livekit.yaml:/etc/livekit.yaml \
  livekit/livekit-server \
  --config /etc/livekit.yaml
```

**livekit.yaml (minimal):**
```yaml
port: 7880
rtc:
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
keys:
  your-api-key: your-api-secret
```

### Agent Worker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "agent.py", "start"]
```

**requirements.txt:**
```
livekit-agents>=0.12.0
livekit-plugins-deepgram>=0.8.0
livekit-plugins-elevenlabs>=0.10.0
livekit-plugins-anthropic>=0.5.0
livekit-plugins-silero>=0.8.0
```

**Scaling:**

| Concurrent Calls | Agent Workers | LiveKit Server | Notes |
|-----------------|---------------|----------------|-------|
| 1-10 | 1 | LiveKit Cloud | Development/MVP |
| 10-50 | 2-5 | LiveKit Cloud | Small production |
| 50-200 | 5-20 | LiveKit Cloud or self-hosted | Monitor SFU capacity |
| 200+ | 20+ | Self-hosted cluster | Dedicated infrastructure |

Each agent worker handles ~5-10 concurrent calls depending on LLM/STT/TTS load.

---

## Code Examples

### Simple Voice Agent

```python
"""Complete LiveKit voice agent with Deepgram + Claude + ElevenLabs."""
import asyncio
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice import VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, anthropic, silero

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=anthropic.LLM(
            model="<current-claude-model-id>",
            system_prompt=(
                "You are a friendly voice assistant. "
                "Keep all responses under 2 sentences. "
                "Use natural spoken language."
            ),
        ),
        tts=elevenlabs.TTS(
            model="eleven_flash_v2_5",
            voice="your-voice-id",
        ),
        allow_interruptions=True,
    )

    agent.start(ctx.room, participant)
    await agent.say("Hi there! What can I help you with?")

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key="your-livekit-key",
            api_secret="your-livekit-secret",
            ws_url="wss://your-project.livekit.cloud",
        )
    )
```

### Customer Service Bot with Tools

```python
"""Customer service bot with tool calling via Claude."""
import asyncio
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice import VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, anthropic, silero

# Define tools for the LLM
TOOLS = [
    {
        "name": "lookup_order",
        "description": "Look up order status by order number",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number (e.g., ORD-12345)",
                },
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "transfer_to_human",
        "description": "Transfer the call to a human agent",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "enum": ["sales", "support", "billing"],
                },
                "reason": {"type": "string"},
            },
            "required": ["department", "reason"],
        },
    },
]

async def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute tool calls from the LLM."""
    if tool_name == "lookup_order":
        # Replace with actual database lookup
        return f"Order {tool_input['order_number']}: Shipped on March 28, arriving April 2."
    elif tool_name == "transfer_to_human":
        return f"Transferring to {tool_input['department']}. Reason: {tool_input['reason']}"
    return "Tool not found."

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    llm = anthropic.LLM(
        model="<current-claude-model-id>",
        system_prompt=(
            "You are a customer service agent for Acme Corp. "
            "Use the lookup_order tool when customers ask about orders. "
            "Transfer to a human if you cannot resolve the issue. "
            "Keep responses to 1-2 sentences."
        ),
        tools=TOOLS,
    )

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=llm,
        tts=elevenlabs.TTS(voice="your-voice-id"),
        allow_interruptions=True,
    )

    @agent.on("function_call")
    async def on_function_call(call):
        result = await handle_tool_call(call.name, call.arguments)
        await call.resolve(result)

    agent.start(ctx.room, participant)
    await agent.say(
        "Welcome to Acme Corp customer service. How can I help you today?"
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

---

## Related References

- [pipecat-patterns.md](pipecat-patterns.md) — Alternative framework (Pipecat, the default)
- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Architecture that LiveKit Agents implements
- [telephony-platform-selection.md](telephony-platform-selection.md) — Telephony integration (LiveKit SIP)
- [latency-engineering.md](latency-engineering.md) — Optimizing LiveKit pipeline latency
- [voice-quality-metrics.md](voice-quality-metrics.md) — Quality monitoring for LiveKit calls
