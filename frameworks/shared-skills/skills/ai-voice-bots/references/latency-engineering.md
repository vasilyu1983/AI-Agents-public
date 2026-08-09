# Latency Engineering

**Purpose**: Measure and optimize every stage of the voice pipeline to hit production latency targets — STT, LLM, TTS, network, and end-to-end.

Benchmark targets: **p50 < 500ms, p90 < 700ms, p99 < 1200ms** total turn latency.

> **Model ID freshness:** Code samples below use `<current-claude-model-id>` as a placeholder. Substitute your provider's current model identifier from its release notes at call time — model aliases and snapshot names drift faster than this file.

---
## Table of Contents

- [Component-Level Measurement](#component-level-measurement)
- [Instrumentation Pattern](#instrumentation-pattern)
- [Measurement Points](#measurement-points)
- [Latency Budget Allocation](#latency-budget-allocation)
- [STT Latency Optimization](#stt-latency-optimization)
- [Provider Latency Comparison](#provider-latency-comparison)
- [STT Optimization Techniques](#stt-optimization-techniques)
- [LLM Latency Optimization](#llm-latency-optimization)
- [TTFB Benchmarks by Model](#ttfb-benchmarks-by-model)
- [LLM Optimization Techniques](#llm-optimization-techniques)
- [Prompt Caching for Voice](#prompt-caching-for-voice)
- [TTS Latency Optimization](#tts-latency-optimization)
- [Provider Latency Comparison](#provider-latency-comparison-1)
- [TTS Optimization Techniques](#tts-optimization-techniques)
- [Network Optimization](#network-optimization)
- [Edge Deployment](#edge-deployment)
- [Connection Pre-Warming](#connection-pre-warming)
- [Speculative Generation](#speculative-generation)
- [Filler Phrase Pattern](#filler-phrase-pattern)
- [Sentence-Boundary TTS](#sentence-boundary-tts)
- [Caching Strategies](#caching-strategies)
- [What to Cache](#what-to-cache)
- [Audio Cache Implementation](#audio-cache-implementation)
- [Load Testing](#load-testing)
- [Load Test Setup](#load-test-setup)
- [Concurrent Call Scaling](#concurrent-call-scaling)
- [Latency Monitoring Dashboard](#latency-monitoring-dashboard)
- [Related References](#related-references)

---

## Component-Level Measurement

### Instrumentation Pattern

```python
import time
import logging
from dataclasses import dataclass, field

logger = logging.getLogger("latency")

@dataclass
class TurnLatency:
    """Measure latency for a single conversation turn."""
    turn_id: str
    vad_end_ts: float = 0.0          # When VAD detected end-of-speech
    stt_final_ts: float = 0.0        # When STT emitted final transcript
    llm_first_token_ts: float = 0.0  # When LLM emitted first token (TTFB)
    llm_complete_ts: float = 0.0     # When LLM finished generating
    tts_first_audio_ts: float = 0.0  # When TTS emitted first audio chunk
    tts_complete_ts: float = 0.0     # When TTS finished synthesis
    audio_play_ts: float = 0.0       # When first audio was sent to transport

    @property
    def stt_latency_ms(self) -> float:
        return (self.stt_final_ts - self.vad_end_ts) * 1000

    @property
    def llm_ttfb_ms(self) -> float:
        return (self.llm_first_token_ts - self.stt_final_ts) * 1000

    @property
    def tts_latency_ms(self) -> float:
        return (self.tts_first_audio_ts - self.llm_first_token_ts) * 1000

    @property
    def total_turn_ms(self) -> float:
        return (self.audio_play_ts - self.vad_end_ts) * 1000

    def log(self):
        logger.info(
            "turn=%s stt=%.0fms llm_ttfb=%.0fms tts=%.0fms total=%.0fms",
            self.turn_id,
            self.stt_latency_ms,
            self.llm_ttfb_ms,
            self.tts_latency_ms,
            self.total_turn_ms,
        )
```

### Measurement Points

```
User stops speaking
    │
    ├──► [VAD end-of-speech] ─── t0 (vad_end_ts)
    │
    ├──► [STT final transcript] ─── t1 (stt_final_ts)
    │         STT latency = t1 - t0
    │
    ├──► [LLM first token] ─── t2 (llm_first_token_ts)
    │         LLM TTFB = t2 - t1
    │
    ├──► [TTS first audio chunk] ─── t3 (tts_first_audio_ts)
    │         TTS latency = t3 - t2
    │
    ├──► [Audio sent to transport] ─── t4 (audio_play_ts)
    │         Network/encode = t4 - t3
    │
    └──► Total turn latency = t4 - t0
```

### Latency Budget Allocation

| Component | Target (p50) | Target (p90) | Target (p99) | Optimization lever |
|-----------|-------------|-------------|-------------|-------------------|
| VAD end-of-speech | 200ms | 300ms | 400ms | min_silence_ms tuning |
| STT (streaming) | 50ms | 100ms | 200ms | Provider, model, language |
| LLM TTFB | 100ms | 200ms | 400ms | Model, caching, prompt size |
| TTS first audio | 80ms | 150ms | 300ms | Provider, streaming mode |
| Network/encode | 20ms | 30ms | 50ms | Edge deployment |
| **Total** | **< 500ms** | **< 700ms** | **< 1200ms** | |

---

## STT Latency Optimization

### Provider Latency Comparison

> **Verification required:** Provider model names, latency, accuracy, and pricing are volatile. Use this comparison as a starting point only; verify current docs or live benchmarks before making a vendor recommendation.

| Provider | Model | p50 Latency | p90 Latency | Accuracy (WER) | Cost/min |
|----------|-------|------------|------------|----------------|----------|
| **Deepgram** | Nova-3 | 50ms | 100ms | 4-7% | $0.0077 |
| **Deepgram** | Nova-3 (enhanced) | 70ms | 120ms | 3-6% | $0.0145 |
| **Azure** | Whisper v3 | 200ms | 400ms | 5-8% | $0.01 |
| **Azure** | Real-time | 100ms | 200ms | 8-12% | $0.01 |
| **Google** | Chirp 2 | 80ms | 150ms | 7-10% | $0.012 |
| **AssemblyAI** | Universal-2 | 150ms | 300ms | 6-9% | $0.015 |

> **Default**: Deepgram Nova-3 — best latency for streaming voice bots with 54% WER improvement over Nova-2. Switch to Azure/Google for non-English languages where Deepgram accuracy drops.

### STT Optimization Techniques

| Technique | Latency Reduction | Implementation |
|-----------|------------------|----------------|
| **Streaming mode** | 200-500ms vs batch | Use `interim_results=True`, process partials |
| **Endpointing** | 100-300ms | Set `endpointing_ms=300` (match VAD) |
| **Language hint** | 20-50ms | Set `language="en-US"` (skip auto-detect) |
| **Vocabulary boost** | Accuracy, not latency | Add domain-specific keywords |
| **Model selection** | Varies | `nova-2` for English, `whisper` for accuracy |
| **Keep connection warm** | 50-100ms first request | Reuse WebSocket across turns |

```python
# Deepgram optimized config
stt_config = {
    "model": "nova-2",
    "language": "en-US",
    "smart_format": False,      # Disable — adds latency, not needed for voice
    "interim_results": True,
    "endpointing": 300,         # ms of silence before finalizing
    "vad_events": True,
    "utterance_end_ms": 1000,   # Backup timeout for very long pauses
}
```

---

## LLM Latency Optimization

### TTFB Benchmarks by Model

> **Verification required:** LLM model availability, prices, and TTFB move quickly. Re-benchmark on the target region, prompt shape, and traffic pattern before treating these numbers as launch gates.

| Model tier | Median TTFB | p90 TTFB | Relative cost | Best For |
|-------|------------|----------|---------------------|----------|
| **Claude — small/fast tier** (e.g. Haiku family) | 80ms | 150ms | Lowest | Simple routing, FAQ |
| **Claude — mid tier** (e.g. Sonnet family) | 150ms | 300ms | Mid | Complex conversations |
| **OpenAI — small/fast tier** (e.g. current GPT-5.6-family mini/nano tier) | 80ms | 150ms | Lowest | High-volume, simple |
| **OpenAI — flagship tier** (e.g. current GPT-5.6-family top tier) | 150ms | 300ms | Mid-high | Complex conversations |
| **Gemini — flash-lite tier** | 60ms | 120ms | Lowest | Cheapest, fast |

> **Default**: mid-tier reasoning model for conversations needing reasoning; small/fast tier for simple routing/FAQ. Switch to the cheapest small-tier model across providers if cost is the top priority. Model family names and generations change every few months — resolve the current small/mid/flagship tier per provider at implementation time rather than trusting a hardcoded name here.

### LLM Optimization Techniques

| Technique | TTFB Reduction | Implementation |
|-----------|---------------|----------------|
| **Streaming** | N/A (required) | Always stream; never wait for full response |
| **Shorter system prompt** | 10-30ms | Keep system prompt under 500 tokens |
| **Limit max_tokens** | 10-20ms | Set `max_tokens=256` for voice (short responses) |
| **Model routing** | 50-100ms | Use Haiku for simple queries, Sonnet for complex |
| **Prompt caching** | 30-50ms | Cache system prompt + conversation prefix |
| **Context pruning** | 10-30ms | Keep last 10-20 turns, summarize older context |
| **Parallel tool calls** | 100-300ms | Run independent tool calls concurrently |

### Prompt Caching for Voice

```python
# Anthropic prompt caching — system prompt is cached across turns
# Reduces TTFB by avoiding re-processing the same system prompt

from anthropic import Anthropic

client = Anthropic()

# First call: system prompt goes into cache
response = client.messages.create(
    model="<current-claude-model-id>",
    max_tokens=256,
    system=[
        {
            "type": "text",
            "text": "You are a customer service agent for Acme Corp...",  # Long system prompt
            "cache_control": {"type": "ephemeral"},  # Cache this block
        }
    ],
    messages=[{"role": "user", "content": transcript}],
)
# Subsequent calls reuse the cached system prompt — lower TTFB
```

---

## TTS Latency Optimization

### Provider Latency Comparison

> **Verification required:** TTS first-audio latency varies by region, voice, streaming settings, cache state, and provider release. Confirm with current provider docs and a small production-like benchmark.

| Provider | Model | First Chunk (p50) | First Chunk (p90) | Quality | Cost/1K chars |
|----------|-------|-------------------|-------------------|---------|-------------|
| **Cartesia** | Sonic-3 | 40ms | 80ms | Good | $0.015 |
| **ElevenLabs** | Flash v2.5 (`eleven_flash_v2_5`) | 75ms | 140ms | Excellent | $0.024 |
| **ElevenLabs** | Turbo v2.5 (`eleven_turbo_v2_5`) | 80ms | 150ms | Excellent | $0.024 |
| **ElevenLabs** | Multilingual v2 | 120ms | 250ms | Best multilingual | $0.024 |
| **Azure** | Neural | 100ms | 200ms | Good | $0.016 |
| **Google** | Neural2 | 120ms | 250ms | Good | $0.016 |
| **PlayHT** | PlayHT 2.0 | 100ms | 200ms | Good | $0.020 |

> **Default**: ElevenLabs Flash v2.5 (`eleven_flash_v2_5`) for best quality with the lowest average latency; `eleven_turbo_v2_5` is functionally equivalent, so existing Turbo code samples remain valid. Cartesia Sonic-3 when latency is the absolute top priority (~40ms TTFA). Note: ElevenLabs v3 (GA Mar 2026) is their expressive flagship but is **not** suitable for real-time/conversational use — use Flash/Turbo v2.5 for real-time.

### TTS Optimization Techniques

| Technique | Latency Reduction | Implementation |
|-----------|------------------|----------------|
| **Streaming synthesis** | 200-500ms vs batch | Always stream — never wait for full audio |
| **Optimize latency setting** | 20-50ms | `optimize_streaming_latency=4` (ElevenLabs) |
| **Sentence-boundary sends** | 100-200ms | Send text to TTS per sentence, not per LLM response |
| **Short first sentence** | Perceived 200ms | Instruct LLM to start with short confirmation |
| **Pre-warm connection** | 50-100ms | Open TTS WebSocket before first TTS request |
| **Voice selection** | 10-30ms | Some voices have lower latency (fewer parameters) |
| **Output format** | 10-20ms | Use PCM for pipeline, avoid MP3 encoding overhead |

```python
# ElevenLabs optimized config
tts_config = {
    "model": "eleven_flash_v2_5",
    "voice_id": "your-voice-id",
    "output_format": "pcm_16000",  # PCM for pipeline (no decode overhead)
    "optimize_streaming_latency": 4,  # 1-4, higher = lower latency
}
```

---

## Network Optimization

### Edge Deployment

| Strategy | Latency Reduction | Complexity |
|----------|------------------|------------|
| **Deploy in same region as providers** | 20-50ms | Low |
| **US East (Virginia)** | Best for Deepgram + ElevenLabs + Anthropic | Recommended default |
| **Multi-region** | 50-100ms for global users | High |
| **Edge workers** | 10-30ms for WebSocket routing | Medium |

**Provider region map (May 2026; verify before deployment):**
- Deepgram: US East primary
- ElevenLabs: US East, EU West
- Anthropic: US East, EU West
- Cartesia: US East

**Default deployment region**: US East (us-east-1 / us-east1) — minimizes network hops to all default providers.

### Connection Pre-Warming

```python
class ConnectionPool:
    """Pre-warm WebSocket connections to STT/TTS providers."""

    def __init__(self):
        self._stt_ws: websockets.WebSocketClientProtocol | None = None
        self._tts_ws: websockets.WebSocketClientProtocol | None = None

    async def warm(self, stt_url: str, tts_url: str, headers: dict):
        """Call during app startup or before first call."""
        self._stt_ws = await websockets.connect(stt_url, extra_headers=headers)
        self._tts_ws = await websockets.connect(tts_url, extra_headers=headers)

    async def get_stt_ws(self) -> websockets.WebSocketClientProtocol:
        if self._stt_ws is None or self._stt_ws.closed:
            raise RuntimeError("STT connection not warmed")
        return self._stt_ws

    async def get_tts_ws(self) -> websockets.WebSocketClientProtocol:
        if self._tts_ws is None or self._tts_ws.closed:
            raise RuntimeError("TTS connection not warmed")
        return self._tts_ws
```

---

## Speculative Generation

### Filler Phrase Pattern

Play a short filler phrase while the LLM generates the full response. Reduces perceived latency by 200-400ms.

```python
import asyncio

FILLER_PHRASES = [
    "Let me check that for you.",
    "One moment please.",
    "Sure, looking into that.",
    "Got it, let me see.",
]

async def speculative_response(
    transcript: str,
    llm_client,
    tts_client,
    audio_output,
    filler_audio_cache: dict[str, bytes],
):
    """Play filler audio while LLM generates real response."""

    # Start LLM generation
    llm_task = asyncio.create_task(llm_client.generate(transcript))

    # Play filler immediately (pre-cached audio)
    filler = FILLER_PHRASES[hash(transcript) % len(FILLER_PHRASES)]
    if filler in filler_audio_cache:
        await audio_output.put(filler_audio_cache[filler])

    # Wait for LLM response
    response = await llm_task

    # Synthesize and play the real response
    async for chunk in tts_client.synthesize_stream(response):
        await audio_output.put(chunk)
```

### Sentence-Boundary TTS

Start TTS on the first complete sentence from the LLM, while remaining tokens continue generating.

```python
import re

async def sentence_streaming_tts(llm_stream, tts_client, audio_output):
    """Send text to TTS at sentence boundaries, not end-of-response."""
    buffer = ""

    async for token in llm_stream:
        buffer += token.text

        # Check for sentence boundary
        match = re.match(r"^(.*?[.!?:]\s)(.*)", buffer, re.DOTALL)
        if match:
            sentence = match.group(1).strip()
            buffer = match.group(2)

            # Send sentence to TTS immediately
            async for audio_chunk in tts_client.synthesize_stream(sentence):
                await audio_output.put(audio_chunk)

    # Flush remaining buffer
    if buffer.strip():
        async for audio_chunk in tts_client.synthesize_stream(buffer.strip()):
            await audio_output.put(audio_chunk)
```

---

## Caching Strategies

### What to Cache

| Cacheable Item | Hit Rate | Latency Savings | Storage |
|----------------|----------|-----------------|---------|
| **Greeting audio** | 100% | 300-500ms (skip TTS) | ~50KB per phrase |
| **Menu prompt audio** | 100% | 300-500ms | ~200KB per menu |
| **Filler phrase audio** | 95%+ | 200-400ms | ~30KB per phrase |
| **FAQ response audio** | 60-80% | 500-1000ms (skip LLM+TTS) | ~500KB per response |
| **LLM system prompt** | 100% | 30-50ms (prompt caching) | API-managed |

### Audio Cache Implementation

```python
import hashlib
from pathlib import Path

class AudioCache:
    """Cache pre-synthesized audio for common phrases."""

    def __init__(self, cache_dir: str = "/tmp/audio_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: dict[str, bytes] = {}

    def _key(self, text: str, voice_id: str) -> str:
        return hashlib.sha256(f"{text}:{voice_id}".encode()).hexdigest()

    async def get(self, text: str, voice_id: str) -> bytes | None:
        key = self._key(text, voice_id)
        if key in self._memory_cache:
            return self._memory_cache[key]
        cache_file = self.cache_dir / f"{key}.pcm"
        if cache_file.exists():
            data = cache_file.read_bytes()
            self._memory_cache[key] = data
            return data
        return None

    async def put(self, text: str, voice_id: str, audio: bytes):
        key = self._key(text, voice_id)
        self._memory_cache[key] = audio
        cache_file = self.cache_dir / f"{key}.pcm"
        cache_file.write_bytes(audio)

    async def warm(self, phrases: list[str], voice_id: str, tts_client):
        """Pre-synthesize and cache common phrases at startup."""
        for phrase in phrases:
            if await self.get(phrase, voice_id) is None:
                audio = await tts_client.synthesize(phrase)
                await self.put(phrase, voice_id, audio)
```

---

## Load Testing

### Load Test Setup

```python
"""Load test: simulate concurrent voice bot calls."""
import asyncio
import time
import statistics

async def simulate_call(call_id: int, pipeline_factory) -> dict:
    """Simulate a single voice bot call with multiple turns."""
    pipeline = pipeline_factory()
    latencies = []

    test_utterances = [
        "Hi, I need help with my order.",
        "The order number is twelve thirty four.",
        "When will it arrive?",
        "Thanks, goodbye.",
    ]

    for utterance in test_utterances:
        start = time.monotonic()
        response = await pipeline.process_turn(utterance)
        elapsed = (time.monotonic() - start) * 1000
        latencies.append(elapsed)

    return {
        "call_id": call_id,
        "turns": len(test_utterances),
        "p50": statistics.median(latencies),
        "p90": sorted(latencies)[int(len(latencies) * 0.9)],
        "max": max(latencies),
    }

async def load_test(concurrent_calls: int, pipeline_factory):
    """Run N concurrent simulated calls."""
    tasks = [simulate_call(i, pipeline_factory) for i in range(concurrent_calls)]
    results = await asyncio.gather(*tasks)

    all_p50 = [r["p50"] for r in results]
    all_p90 = [r["p90"] for r in results]

    print(f"Concurrent calls: {concurrent_calls}")
    print(f"Median p50: {statistics.median(all_p50):.0f}ms")
    print(f"Median p90: {statistics.median(all_p90):.0f}ms")
    print(f"Worst p90: {max(all_p90):.0f}ms")
```

### Concurrent Call Scaling

Expected latency degradation under load:

| Concurrent Calls | p50 Increase | p90 Increase | Bottleneck |
|-----------------|-------------|-------------|------------|
| 1-5 | Baseline | Baseline | None |
| 5-20 | +10-20% | +15-30% | LLM rate limits |
| 20-50 | +20-40% | +30-60% | STT/TTS connections |
| 50-100 | +40-80% | +60-120% | CPU (VAD/audio processing) |
| 100+ | +80%+ | +120%+ | Everything — scale horizontally |

**Mitigation at scale:**
- **LLM**: Request rate limit increases from provider. Use caching.
- **STT/TTS**: Use connection pooling. Pre-warm connections per instance.
- **CPU**: Horizontal scaling. One pipeline per vCPU core.

---

## Latency Monitoring Dashboard

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Total turn latency (p90) | Pipeline instrumentation | > 800ms |
| STT latency (p90) | STT timestamps | > 150ms |
| LLM TTFB (p90) | LLM timestamps | > 350ms |
| TTS first audio (p90) | TTS timestamps | > 200ms |
| VAD false positives/hr | VAD event log | > 10/hr |
| WebSocket reconnections/hr | Connection log | > 5/hr |
| Call drop rate | Transport events | > 2% |

```python
# Export metrics to Prometheus/Datadog/CloudWatch
from dataclasses import dataclass

@dataclass
class LatencyMetrics:
    """Collect and export latency metrics per turn."""
    stt_latency_ms: float
    llm_ttfb_ms: float
    tts_latency_ms: float
    total_turn_ms: float
    call_id: str
    turn_number: int

    def to_tags(self) -> dict:
        return {
            "call_id": self.call_id,
            "turn": str(self.turn_number),
        }

    def emit(self, stats_client):
        """Emit to StatsD/Datadog."""
        tags = self.to_tags()
        stats_client.histogram("voice.stt_latency_ms", self.stt_latency_ms, tags=tags)
        stats_client.histogram("voice.llm_ttfb_ms", self.llm_ttfb_ms, tags=tags)
        stats_client.histogram("voice.tts_latency_ms", self.tts_latency_ms, tags=tags)
        stats_client.histogram("voice.total_turn_ms", self.total_turn_ms, tags=tags)
```

---

## Related References

- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Pipeline stages being optimized
- [pipecat-patterns.md](pipecat-patterns.md) — Pipecat-specific latency tuning
- [livekit-agents-patterns.md](livekit-agents-patterns.md) — LiveKit-specific latency tuning
- [voice-quality-metrics.md](voice-quality-metrics.md) — Quality metrics alongside latency
- [telephony-platform-selection.md](telephony-platform-selection.md) — Platform latency characteristics
