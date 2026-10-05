# Voice Pipeline Architecture

**Purpose**: Design production STT→LLM→TTS pipelines for voice bots — topology, codecs, streaming, VAD, barge-in, turn-taking, and error handling.

No narrative. Architecture decisions and implementation patterns only.

> **Model ID freshness:** Code samples below use `<current-claude-model-id>` as a placeholder. Substitute your provider's current model identifier from its release notes at call time — model aliases and snapshot names drift faster than this file.

---
## Table of Contents

- [Pipeline Topology](#pipeline-topology)
- [Serial Streaming Pipeline](#serial-streaming-pipeline)
- [Parallel Processing Pipeline](#parallel-processing-pipeline)
- [Choosing a Topology](#choosing-a-topology)
- [Audio Codec Selection](#audio-codec-selection)
- [Codec Comparison](#codec-comparison)
- [Codec Selection Rules](#codec-selection-rules)
- [WebSocket Connection Management](#websocket-connection-management)
- [Connection Lifecycle](#connection-lifecycle)
- [Keepalive Strategy](#keepalive-strategy)
- [Reconnection Pattern](#reconnection-pattern)
- [Graceful Degradation](#graceful-degradation)
- [Voice Activity Detection (VAD)](#voice-activity-detection-vad)
- [VAD Strategy Comparison](#vad-strategy-comparison)
- [VAD Configuration Defaults](#vad-configuration-defaults)
- [Production VAD Pattern (Python)](#production-vad-pattern-python)
- [Barge-In Support](#barge-in-support)
- [Barge-In Architecture](#barge-in-architecture)
- [Implementation Pattern](#implementation-pattern)
- [Turn-Taking Patterns](#turn-taking-patterns)
- [Pattern Comparison](#pattern-comparison)
- [VAD-Based Turn-Taking (Default)](#vad-based-turn-taking-default)
- [Streaming Architecture](#streaming-architecture)
- [Chunk-by-Chunk Processing](#chunk-by-chunk-processing)
- [Waterfall vs Parallel](#waterfall-vs-parallel)
- [Streaming STT→LLM→TTS Pattern (Python)](#streaming-sttllmtts-pattern-python)
- [Pipeline Error Handling](#pipeline-error-handling)
- [Failure Modes and Fallbacks](#failure-modes-and-fallbacks)
- [Circuit Breaker Pattern](#circuit-breaker-pattern)
- [Production Error Handler (Python)](#production-error-handler-python)
- [Pipeline Configuration Template](#pipeline-configuration-template)
- [Related References](#related-references)

---

## Pipeline Topology

### Serial Streaming Pipeline

The default architecture. Each stage streams its output to the next as chunks arrive.

```
Mic → Transport → [VAD] → STT (streaming) → LLM (streaming) → TTS (streaming) → Transport → Speaker
         │                    │                   │                  │
         │                    │                   │                  └─ Audio chunks out
         │                    │                   └─ Token stream
         │                    └─ Partial transcript stream
         └─ Audio frames (20ms chunks)
```

**Latency profile**: Fastest for single-turn. Each stage starts emitting as soon as it receives the first input chunk. Total turn latency is dominated by the slowest stage, not the sum of all stages.

**When to use**: Default. Works for 90% of voice bots. Simple, debuggable, predictable.

### Parallel Processing Pipeline

Advanced topology for when you need to reduce perceived latency below what serial allows.

```
                    ┌─ STT (streaming) ─┐
Mic → Transport ──► │                    ├──► LLM ──► TTS → Transport → Speaker
                    └─ VAD ─────────────┘

                    ┌─ Speculative TTS (filler phrase) ──────────► Speaker
                    │
LLM (streaming) ───┤
                    │
                    └─ Full TTS (actual response) ──────────────► Speaker (replace filler)
```

**Latency profile**: Lower perceived latency. Filler phrases ("Let me check that...") play immediately while the full response generates.

**When to use**: When p90 latency exceeds 800ms in serial mode. Complex queries where LLM thinking time is > 500ms.

### Choosing a Topology

| Factor | Serial | Parallel |
|--------|--------|----------|
| Complexity | Low | High |
| Debuggability | Easy | Hard |
| Latency (simple queries) | Good | Same |
| Latency (complex queries) | Acceptable | Better |
| Resource usage | Lower | Higher |
| Default recommendation | Yes | Only if serial fails latency targets |

---

## Audio Codec Selection

### Codec Comparison

| Codec | Bitrate | Quality | Latency | Use Case |
|-------|---------|---------|---------|----------|
| **G.711 u-law** | 64 kbps | Telephone-grade | Minimal | PSTN telephony (Twilio, Telnyx) |
| **G.711 A-law** | 64 kbps | Telephone-grade | Minimal | PSTN telephony (EU standard) |
| **Opus** | 6-510 kbps | Excellent | 2.5-60ms frame | WebRTC, high-quality voice |
| **PCM 16-bit** | 256 kbps (16kHz) | Lossless | None | Internal pipeline processing |
| **MP3** | 32-320 kbps | Good | High (buffering) | Recorded prompts only, never live |
| **AAC** | 32-320 kbps | Good | Medium | iOS playback, not real-time |

### Codec Selection Rules

1. **PSTN calls (Twilio/Telnyx)**: G.711 u-law (PCMU), 8kHz sample rate. This is non-negotiable — PSTN requires it.
2. **WebRTC calls (browser/mobile)**: Opus, 16-48kHz. Best quality and lowest latency for internet audio.
3. **Internal pipeline**: PCM 16-bit, 16kHz. Most STT/TTS engines expect linear PCM.
4. **Recording**: Opus or WAV. Store recordings in a format that preserves quality for review.

**Conversion pattern**: Always transcode at the transport boundary, not inside the pipeline.

```python
# Transport layer handles codec conversion
# Pipeline internals always use PCM 16-bit, 16kHz mono
PIPELINE_SAMPLE_RATE = 16000
PIPELINE_SAMPLE_WIDTH = 2  # 16-bit
PIPELINE_CHANNELS = 1  # mono
```

---

## WebSocket Connection Management

### Connection Lifecycle

```
Client                                Server (STT/TTS provider)
  │                                       │
  ├── WebSocket CONNECT ────────────────► │
  │                                       │
  ├── Auth token in headers ────────────► │
  │                                       │
  │ ◄──────────────── Connection ACK ─────┤
  │                                       │
  ├── Audio frames (20ms) ──────────────► │ (STT)
  │ ◄──────────────── Partial results ────┤
  │                                       │
  ├── Text chunks ──────────────────────► │ (TTS)
  │ ◄──────────────── Audio chunks ───────┤
  │                                       │
  ├── CLOSE frame ──────────────────────► │
  │ ◄──────────────── CLOSE ACK ──────────┤
```

### Keepalive Strategy

```python
import asyncio
import websockets

KEEPALIVE_INTERVAL = 20  # seconds
KEEPALIVE_TIMEOUT = 10   # seconds

async def keepalive_loop(ws: websockets.WebSocketClientProtocol):
    """Send periodic pings to keep the connection alive."""
    while True:
        try:
            pong = await ws.ping()
            await asyncio.wait_for(pong, timeout=KEEPALIVE_TIMEOUT)
        except asyncio.TimeoutError:
            # Pong not received — connection is dead
            await ws.close()
            break
        await asyncio.sleep(KEEPALIVE_INTERVAL)
```

### Reconnection Pattern

```python
import asyncio
import random

MAX_RETRIES = 5
BASE_DELAY = 0.5  # seconds

async def connect_with_retry(url: str, headers: dict) -> websockets.WebSocketClientProtocol:
    """Exponential backoff with jitter for WebSocket reconnection."""
    for attempt in range(MAX_RETRIES):
        try:
            ws = await websockets.connect(url, extra_headers=headers)
            return ws
        except (ConnectionRefusedError, websockets.exceptions.WebSocketException):
            if attempt == MAX_RETRIES - 1:
                raise
            delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.5)
            await asyncio.sleep(delay)
```

### Graceful Degradation

| Failure | Degraded Mode | User Experience |
|---------|--------------|-----------------|
| STT WebSocket drops | Buffer audio, reconnect, replay | Brief silence, then "Sorry, could you repeat that?" |
| TTS WebSocket drops | Fall back to pre-recorded audio | Generic response in fallback voice |
| LLM timeout | Return canned response | "Let me transfer you to an agent." |
| All providers down | Play recorded message, offer callback | "We're experiencing issues. Press 1 for a callback." |

---

## Voice Activity Detection (VAD)

### VAD Strategy Comparison

| Strategy | Accuracy | Latency | CPU Cost | Best For |
|----------|----------|---------|----------|----------|
| **Energy-based** | Low | Minimal | Minimal | Simple environments, push-to-talk backup |
| **WebRTC VAD** | Medium | Low (10-30ms frames) | Low | General use, browser-based |
| **Silero VAD** | High | Medium (30-60ms) | Medium | Production default, noisy environments |
| **Combined (Silero + Energy)** | Highest | Medium | Medium | Enterprise, high-accuracy requirement |

### Turn Detection Options (2026)

Silence-based VAD answers "is the user speaking?" — not "has the user finished their turn?" Two newer approaches close that gap:

| Approach | Model | Latency | Tradeoff |
|----------|-------|---------|----------|
| Silence-based VAD | Silero VAD | ~0ms added | Adds 300–800ms wait per turn; misreads mid-utterance pauses as end-of-turn |
| Semantic turn model (client-side) | Pipecat Smart Turn v3.x (`LocalSmartTurnAnalyzerV3`) | ~12–65ms CPU | ~8M params / 8MB int8, ~23 languages, open weights; runs after VAD silence to confirm end-of-turn |
| Fused CSR + turn detection (server-side) | Deepgram Flux (`flux-general-en` / `flux-general-multi`) | ~260ms median EoT | Replaces STT+VAD+endpointing in one `/v2/listen` call; vendor-reported 200–600ms response-latency reduction vs the stacked pipeline. Vendor benchmark (VAQI) — corroborated by Vapi/Twilio/Pipecat integrations |
| Native S2S turn-taking | OpenAI Realtime API (current `gpt-realtime-2.1` generation) | model-internal | No separate turn model; the S2S session-state-loss trap (see SKILL.md Known Traps) applies |

**Recommendation:** For cascading pipelines, Deepgram Flux fused CSR is the highest-leverage turn-detection upgrade. Pipecat Smart Turn v3.x is the open-weight fallback for self-hosted or non-Deepgram stacks. Plain Silero VAD remains the floor when neither is available.

### VAD Configuration Defaults

```python
# Silero VAD — production defaults
VAD_CONFIG = {
    "model": "silero_vad",
    "threshold": 0.5,            # Speech probability threshold (0.0-1.0)
    "min_speech_ms": 250,        # Minimum speech duration to register
    "min_silence_ms": 300,       # Silence duration to trigger end-of-speech
    "speech_pad_ms": 30,         # Padding around detected speech
    "sample_rate": 16000,        # Must match pipeline sample rate
    "window_size_samples": 512,  # ~32ms at 16kHz
}

# Adjust for use case:
# - Call center (noisy):     threshold=0.6, min_silence_ms=400
# - Quiet environment:       threshold=0.4, min_silence_ms=250
# - Fast-paced conversation: threshold=0.5, min_silence_ms=200
```

### Production VAD Pattern (Python)

```python
import numpy as np
import torch

class SileroVADProcessor:
    """Production-grade VAD using Silero model."""

    def __init__(self, threshold: float = 0.5, min_silence_ms: int = 300):
        self.model, _ = torch.hub.load(
            "snakers4/silero-vad", "silero_vad", trust_repo=True
        )
        self.threshold = threshold
        self.min_silence_samples = int(16000 * min_silence_ms / 1000)
        self.silence_counter = 0
        self.is_speaking = False

    def process_frame(self, audio_chunk: bytes) -> str | None:
        """Process a 512-sample audio frame. Returns 'speech_start', 'speech_end', or None."""
        audio = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        tensor = torch.from_numpy(audio)

        prob = self.model(tensor, 16000).item()

        if prob >= self.threshold:
            self.silence_counter = 0
            if not self.is_speaking:
                self.is_speaking = True
                return "speech_start"
        else:
            self.silence_counter += len(audio)
            if self.is_speaking and self.silence_counter >= self.min_silence_samples:
                self.is_speaking = False
                self.silence_counter = 0
                return "speech_end"

        return None
```

---

## Barge-In Support

### Barge-In Architecture

Barge-in lets the user interrupt the bot's TTS output by speaking. Essential for natural conversation.

```
User starts speaking during TTS playback:

1. VAD detects speech_start
2. Pipeline sends TTS STOP command
3. Audio output buffer is flushed
4. STT begins capturing new user utterance
5. Previous LLM generation is cancelled
6. New pipeline turn starts from the user's interruption
```

### Implementation Pattern

```python
class BargeInController:
    """Manages barge-in: stop TTS and cancel LLM when user interrupts."""

    def __init__(self, tts_player, llm_client, stt_engine):
        self.tts_player = tts_player
        self.llm_client = llm_client
        self.stt_engine = stt_engine
        self._is_bot_speaking = False

    async def on_tts_start(self):
        self._is_bot_speaking = True

    async def on_tts_end(self):
        self._is_bot_speaking = False

    async def on_vad_speech_start(self):
        if self._is_bot_speaking:
            # Barge-in detected — interrupt everything
            await self.tts_player.stop_and_flush()
            await self.llm_client.cancel_generation()
            self._is_bot_speaking = False
            # STT is already capturing — let it proceed
```

**Barge-in sensitivity tuning:**
- **Aggressive** (min_speech_ms=100): Interrupts on any sound. Risk of false positives from background noise.
- **Default** (min_speech_ms=250): Balanced. Handles most conversational interruptions.
- **Conservative** (min_speech_ms=500): Only interrupts on sustained speech. Use for noisy call centers.

---

## Turn-Taking Patterns

### Pattern Comparison

| Pattern | Mechanism | Latency | Use Case |
|---------|-----------|---------|----------|
| **VAD-based** (default) | Silence detection triggers turn end | 200-400ms silence gap | General voice bots |
| **Push-to-talk** | User presses button to speak | Minimal | Noisy environments, WebRTC apps |
| **Backchannel** | Bot emits "mm-hmm" during user speech | N/A (concurrent) | Long-form user input (stories, descriptions) |
| **Endpointing heuristic** | Combine VAD + grammar + prosody | 100-300ms | Advanced, low-latency voice agents |

### VAD-Based Turn-Taking (Default)

```python
class TurnManager:
    """Manages conversation turns using VAD signals."""

    def __init__(self, end_of_turn_silence_ms: int = 300):
        self.end_of_turn_silence_ms = end_of_turn_silence_ms
        self.current_turn = "bot"  # or "user"
        self.transcript_buffer = ""

    async def on_speech_start(self):
        self.current_turn = "user"
        self.transcript_buffer = ""

    async def on_partial_transcript(self, text: str):
        self.transcript_buffer = text

    async def on_speech_end(self) -> str:
        """Returns the final transcript for this turn."""
        self.current_turn = "bot"
        final = self.transcript_buffer
        self.transcript_buffer = ""
        return final
```

---

## Streaming Architecture

### Chunk-by-Chunk Processing

Every pipeline stage operates on small chunks, not full utterances.

| Stage | Input Chunk | Output Chunk | Typical Size |
|-------|-------------|--------------|-------------|
| Transport → VAD | 20ms audio frame | VAD event | 640 bytes (16kHz PCM) |
| VAD → STT | Audio frames | Partial transcript | Variable text |
| STT → LLM | Final transcript | Token stream | 1-4 tokens at a time |
| LLM → TTS | Text chunk (sentence) | Audio chunk | 100-500ms of audio |
| TTS → Transport | Audio chunk | Encoded frame | Codec-dependent |

### Waterfall vs Parallel

**Waterfall** (default): Each stage waits for the previous stage to emit before starting.

```
STT final ──► LLM starts ──► LLM first token ──► TTS starts ──► First audio out
     │              │                │                  │               │
     0ms          +10ms          +150ms             +160ms          +220ms
```

**Parallel (speculative)**: TTS starts on first LLM sentence boundary, not end of response.

```
LLM token stream:  "Sure, │ I can help with that. │ Let me check your account."
                          │                        │
TTS chunk 1 starts: ──────┘                        │
TTS chunk 2 starts: ───────────────────────────────┘
```

The parallel approach sends text to TTS at sentence boundaries as the LLM streams. This reduces perceived latency by 100-300ms.

### Streaming STT→LLM→TTS Pattern (Python)

```python
import asyncio

async def streaming_pipeline(
    stt_stream,      # async generator yielding transcripts
    llm_client,      # streaming LLM client
    tts_client,      # streaming TTS client
    audio_output,    # async queue for output audio
):
    """Core streaming pipeline: STT → LLM → TTS with sentence-level chunking."""

    async for transcript in stt_stream:
        if not transcript.is_final:
            continue

        # Stream LLM response, buffer by sentence
        sentence_buffer = ""
        async for token in llm_client.stream(transcript.text):
            sentence_buffer += token.text

            # Flush to TTS at sentence boundaries
            if sentence_buffer.rstrip().endswith((".", "!", "?", ":")):
                audio_chunks = tts_client.synthesize_stream(sentence_buffer.strip())
                async for chunk in audio_chunks:
                    await audio_output.put(chunk)
                sentence_buffer = ""

        # Flush any remaining text
        if sentence_buffer.strip():
            async for chunk in tts_client.synthesize_stream(sentence_buffer.strip()):
                await audio_output.put(chunk)
```

---

## Pipeline Error Handling

### Failure Modes and Fallbacks

| Component | Failure Mode | Detection | Fallback |
|-----------|-------------|-----------|----------|
| **STT** | WebSocket disconnect | Connection closed event | Reconnect + "Could you repeat that?" |
| **STT** | Timeout (no result in 10s) | Timer | Reset STT session, prompt user |
| **STT** | Garbage output (WER spike) | WER monitoring | Switch to backup STT provider |
| **LLM** | Timeout (no first token in 5s) | TTFB timer | Canned response + escalate |
| **LLM** | Rate limit (429) | HTTP status | Queue + retry with backoff |
| **LLM** | Context too long | Token count | Truncate/summarize context |
| **TTS** | WebSocket disconnect | Connection closed event | Fall back to pre-recorded audio |
| **TTS** | Audio quality degradation | MOS monitoring | Switch to backup TTS provider |
| **Transport** | Call dropped | SIP BYE / WebSocket close | Log, no recovery possible |
| **Transport** | Audio jitter/loss | Jitter buffer metrics | Increase jitter buffer size |

### Circuit Breaker Pattern

```python
import time
from dataclasses import dataclass

@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    reset_timeout: float = 30.0
    _failures: int = 0
    _last_failure: float = 0.0
    _state: str = "closed"  # closed, open, half-open

    def record_failure(self):
        self._failures += 1
        self._last_failure = time.monotonic()
        if self._failures >= self.failure_threshold:
            self._state = "open"

    def record_success(self):
        self._failures = 0
        self._state = "closed"

    def can_proceed(self) -> bool:
        if self._state == "closed":
            return True
        if self._state == "open":
            if time.monotonic() - self._last_failure > self.reset_timeout:
                self._state = "half-open"
                return True
            return False
        # half-open: allow one request
        return True
```

### Production Error Handler (Python)

```python
import logging

logger = logging.getLogger("voice_pipeline")

FALLBACK_RESPONSES = {
    "stt_failure": "I'm sorry, I didn't catch that. Could you please repeat?",
    "llm_timeout": "Let me transfer you to someone who can help. One moment please.",
    "tts_failure": None,  # Use pre-recorded audio
    "general_error": "I'm experiencing a technical issue. Please hold.",
}

async def handle_pipeline_error(
    error_type: str,
    tts_client,
    audio_output,
    fallback_audio_path: str = "assets/fallback_sorry.wav",
):
    """Handle pipeline errors with graceful degradation."""
    logger.error(f"Pipeline error: {error_type}")

    fallback_text = FALLBACK_RESPONSES.get(error_type)

    if fallback_text and tts_client.is_connected:
        # TTS is available — synthesize the fallback
        async for chunk in tts_client.synthesize_stream(fallback_text):
            await audio_output.put(chunk)
    else:
        # TTS is down — play pre-recorded audio
        await play_prerecorded(fallback_audio_path, audio_output)
```

---

## Pipeline Configuration Template

```python
PIPELINE_CONFIG = {
    "transport": {
        "type": "twilio_media_stream",  # or "websocket", "daily", "livekit"
        "sample_rate": 8000,             # 8kHz for PSTN, 16kHz for WebRTC
        "codec": "pcmu",                 # G.711 u-law for PSTN
        "frame_size_ms": 20,
    },
    "vad": {
        "engine": "silero",
        "threshold": 0.5,
        "min_speech_ms": 250,
        "min_silence_ms": 300,
    },
    "stt": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "en-US",
        "streaming": True,
        "interim_results": True,
        "endpointing_ms": 300,
    },
    "llm": {
        "provider": "anthropic",
        "model": "<current-claude-model-id>",
        "max_tokens": 256,
        "temperature": 0.7,
        "streaming": True,
        "timeout_ms": 5000,
    },
    "tts": {
        "provider": "elevenlabs",
        "model": "eleven_flash_v2_5",
        "voice_id": "your-voice-id",
        "streaming": True,
        "output_format": "pcm_16000",
        "optimize_streaming_latency": 4,
    },
    "barge_in": {
        "enabled": True,
        "min_speech_ms": 250,
    },
    "error_handling": {
        "stt_circuit_breaker_threshold": 3,
        "llm_timeout_ms": 5000,
        "tts_fallback_audio": "assets/fallback_sorry.wav",
    },
}
```

---

## Related References

- [telephony-platform-selection.md](telephony-platform-selection.md) — Platform that provides the transport layer
- [pipecat-patterns.md](pipecat-patterns.md) — Pipecat implementation of this architecture
- [livekit-agents-patterns.md](livekit-agents-patterns.md) — LiveKit Agents implementation
- [latency-engineering.md](latency-engineering.md) — Optimizing each pipeline stage
- [voice-quality-metrics.md](voice-quality-metrics.md) — Measuring pipeline output quality
