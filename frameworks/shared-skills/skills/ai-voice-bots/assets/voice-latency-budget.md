# Voice Latency Budget Worksheet

Use this worksheet to set and track latency budgets for each voice pipeline component.

## Target: Total Turn Latency < 700ms

"Turn latency" = time from user stops speaking to bot audio starts playing.

## Component Budgets

| # | Component | Budget (ms) | Measured p50 | Measured p90 | Measured p99 | Status |
|---|-----------|-------------|-------------|-------------|-------------|--------|
| 1 | VAD (end-of-speech detection) | 200-300 | | | | |
| 2 | STT (speech → text) | 100-200 | | | | |
| 3 | LLM (text → response TTFB) | 100-300 | | | | |
| 4 | TTS (text → first audio chunk) | 50-150 | | | | |
| 5 | Network (round-trip) | 20-50 | | | | |
| **Total** | | **< 700** | | | | |

## Optimization Levers by Component

### VAD (Voice Activity Detection)
- [ ] Silence threshold: [X]ms (lower = faster but more false positives)
- [ ] Using Silero VAD / WebRTC VAD / energy-based
- [ ] End-of-utterance confidence threshold: [X]

### STT (Speech-to-Text)
- [ ] Streaming mode enabled (not batch)
- [ ] Provider: [Deepgram Nova-3 / AssemblyAI Universal-2 / Azure]
- [ ] Language model optimized for domain
- [ ] Interim results enabled for early LLM processing

### LLM (Language Model)
- [ ] Model: [name] (TTFB measured: [X]ms)
- [ ] Streaming enabled
- [ ] System prompt optimized for length
- [ ] Prefix caching enabled (if available)
- [ ] Response length capped for voice (shorter = better)

### TTS (Text-to-Speech)
- [ ] Streaming synthesis enabled
- [ ] Provider: [ElevenLabs Turbo / Cartesia Sonic / Azure Neural]
- [ ] Voice optimized for latency (not all voices are equal)
- [ ] Chunk size: [X] characters (smaller = faster first audio)

### Network
- [ ] Edge deployment (closest region to users)
- [ ] Connection pre-warming (persistent WebSocket to providers)
- [ ] Audio codec: [Opus / PCM / G.711] (Opus for web, G.711 for telephony)

## Load Test Results

| Concurrent calls | p50 (ms) | p90 (ms) | p99 (ms) | Error rate |
|------------------|----------|----------|----------|------------|
| 1 | | | | |
| 10 | | | | |
| 50 | | | | |
| 100 | | | | |
| [target peak] | | | | |

## Notes

- Measure under realistic conditions (real phone calls, not localhost)
- Measure each component independently AND total pipeline
- Run measurements at expected peak load, not just idle
- Re-measure after any provider, model, or infrastructure change
