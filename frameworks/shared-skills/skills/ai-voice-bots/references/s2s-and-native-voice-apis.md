# S2S and Native Voice APIs — July 2026

Reference for speech-to-speech (S2S) APIs and their use in production voice bot pipelines. Covers OpenAI Realtime API and Gemini Live as of July 2026, with selection criteria, session management patterns, and the S2S vs cascading decision.

**Fact-check requirement**: verify current model versions, pricing, language support, and API availability against official provider docs before recommending for production use.

## Table of Contents

- [What Is S2S?](#what-is-s2s)
- [OpenAI Realtime API](#openai-realtime-api)
- [Gemini Live](#gemini-live)
- [S2S vs Cascading: Selection Criteria](#s2s-vs-cascading-selection-criteria)
- [Session-State Loss on Model Switch](#session-state-loss-on-model-switch)
- [Integration with Pipecat](#integration-with-pipecat)
- [Integration with LiveKit Agents](#integration-with-livekit-agents)

---

## What Is S2S?

Speech-to-speech (S2S) eliminates the text layer in a voice pipeline. Instead of:

```
Audio → STT → text → LLM → text → TTS → Audio    (cascading, ~700ms)
```

S2S processes:

```
Audio → S2S model → Audio                          (native S2S, ~500ms)
```

The model receives raw audio and emits raw audio. The intermediate text representation exists inside the model but is not exposed or inspectable by default.

**Implication**: you cannot inject guardrails, compliance checks, PII detection, or structured-output parsing at the text layer. Everything that relies on reading or modifying the text between STT and TTS is unavailable unless you add a parallel transcript track.

---

## OpenAI Realtime API

**Status (Jul 2026)**: the Realtime API has exited beta and is fully GA. The model line has already iterated twice since the first GA cut — `gpt-realtime-2` (May 2026) was superseded by `gpt-realtime-2.1` / `gpt-realtime-2.1-mini` (Jul 2026), which cut measured p95 latency by roughly 25% and added reasoning + reliable tool calling to the mini tier (previously flagship-only). `gpt-4o-realtime-preview` / `gpt-4o-mini-realtime-preview` are fully retired. Access via WebSocket or the Realtime API endpoint. Supported in Pipecat and LiveKit Agents. **Expert judgment**: this model line has shipped a materially different generation roughly every 8-10 weeks through 2026 — treat any specific model name in a runbook as provisional and re-check OpenAI's model index before a launch, not just at initial build time.

### How it works

The Realtime API maintains a persistent WebSocket session. The client streams audio in; the model streams audio out. The session is stateful — it maintains conversation history within the session as an in-memory context managed by OpenAI's infrastructure.

Key session objects:
- **Session configuration**: voice selection (alloy, echo, shimmer, etc.), VAD settings, system prompt, temperature, tools.
- **Conversation items**: the model maintains a list of `conversation.item` objects representing the dialogue history.
- **Response lifecycle**: `response.create` → `response.audio.delta` (streaming audio chunks) → `response.audio.done`.

### Model support (Jul 2026)

The `gpt-4o-realtime-preview` / `gpt-4o-mini-realtime-preview` line is fully retired. Current generation as of this writing:

- `gpt-realtime-2.1` — flagship; reasoning S2S, large context, improved alphanumeric read-back (order numbers, confirmation codes), better noise/silence handling and interruption behavior. Supersedes `gpt-realtime-2`.
- `gpt-realtime-2.1-mini` — smaller tier; now has the reasoning + reliable tool-calling that only the flagship had before, at the same price as the earlier mini. Use this as the default for cost-sensitive high-volume voice agents rather than routing everything to the flagship.
- `gpt-realtime-translate` — live speech-to-speech translation: 70+ input languages to 13 output languages, keeps pace with the speaker, returns translated speech plus text transcripts.
- `gpt-realtime-whisper` — streaming STT with a controllable latency/quality tradeoff (lower delay setting = earlier partial text, higher delay = better transcript quality).

**Do not hardcode these names into production config as permanent facts** — verify current model IDs and pricing in OpenAI's model index before every material release; this line has changed generation at least three times in under three months.

### Latency

Typical first-audio-chunk latency: ~300–500ms (p50) on the current generation, with the `2.1` update specifically targeting p95 tail latency (~25% reduction over `gpt-realtime-2`) rather than median. Actual latency depends on: utterance length, VAD end-of-turn detection, server load, and client geographic proximity to the OpenAI data center. **Judgment**: if your pain point is bad p95/p99 (occasional multi-second stalls) rather than median latency, check which generation you're on before reaching for a cascaded fallback — recent Realtime generations have specifically targeted tail latency, and an upgrade may fix the complaint cheaper than an architecture change.

### Session management patterns

**Critical**: the Realtime API session is ephemeral. Session state is lost on:
- WebSocket disconnection.
- Model version switch.
- Session timeout (idle sessions are terminated by the API).
- API errors that close the connection.

**Pattern: external state persistence**

```python
# After each turn, persist conversation state to Redis
async def on_response_done(session_id: str, conversation_items: list):
    await redis.set(
        f"voice:session:{session_id}:items",
        json.dumps(conversation_items),
        ex=3600,  # 1-hour TTL
    )

# On reconnect or model switch, restore from Redis
async def restore_session(session_id: str, realtime_client):
    items = await redis.get(f"voice:session:{session_id}:items")
    if items:
        for item in json.loads(items):
            await realtime_client.conversation.item.create(item)
```

**Pattern: parallel transcript track**

For compliance, PII detection, or audit requirements, run a parallel Deepgram or Whisper STT stream alongside the S2S session. This gives you the text layer for guardrails and logging without abandoning S2S latency.

```
Audio in → Realtime API (S2S) → Audio out
         ↓
         Deepgram streaming STT → text → compliance filter → audit log
```

Cost: adds ~10–30ms latency to the compliance path (async, does not block audio output) and Deepgram per-minute costs.

### Tool use in S2S

The Realtime API supports function calling with the same tool-call flow as the standard API. The model emits a `response.function_call_arguments.done` event instead of audio when it decides to call a tool. Your server handles the function call and returns the result; the model then continues with audio output.

**Approval requirement**: irreversible or high-value tool calls (payments, account changes) must be gated with a human-confirmation turn — do not allow the model to execute them autonomously. The S2S latency advantage disappears if you add a blocking confirmation round-trip for every tool call; design tool use to minimize blocking gates.

### Known limitations (May 2026)

- Session context window: bounded (verify current limit in API docs). Long sessions require explicit context management or truncation.
- No native streaming output of the intermediate transcript (text must be requested separately via `response.text.done`).
- Voice selection is fixed for the session duration — cannot change mid-call without reconnecting.
- Not available in all OpenAI API regions — verify availability before EU/APAC deployments.

---

## Gemini Live

**Status (May 2026)**: available via the Google AI Studio and Vertex AI. Supports persistent bidirectional audio sessions.

### How it works

Gemini Live (also called Gemini Multimodal Live API in some docs) provides a WebSocket-based session for real-time audio and video interaction. The model receives audio (and optionally video) and streams audio responses.

Key differences from OpenAI Realtime:
- Gemini Live sessions are designed for longer, open-ended conversations — better session endurance.
- Native integration with Google Search for grounding (the model can call Search as a tool without you providing the tool definition).
- Multimodal: accepts video frames alongside audio for richer context.

### Latency

Comparable to OpenAI Realtime (~300–500ms first audio chunk, p50). Google's data center proximity advantage may matter for EU and APAC deployments.

### Session management patterns

Same persistence pattern as OpenAI Realtime applies — Gemini Live sessions are also ephemeral on disconnect. Persist conversation state to Redis using the same pattern.

**Session duration**: Gemini Live supports longer continuous sessions than OpenAI Realtime (verify current limits). For long IVR or support calls, this is a meaningful advantage.

### Known limitations (May 2026)

- Pipecat support for Gemini Live: check current release notes — Pipecat adds provider support iteratively; Gemini Live support may be experimental.
- Function calling in Gemini Live: available but the API and event format differ from the standard Gemini API. Verify against current Vertex AI docs.
- Text transcript access: available via separate API call; not automatically included in the audio stream.

---

## S2S vs Cascading: Selection Criteria

| Criterion | S2S | Cascading (STT→LLM→TTS) |
|-----------|-----|-------------------------|
| Latency (p50) | ~300–500ms | ~600–800ms |
| Text-layer compliance filtering | Not available without parallel track | Native |
| PII detection / redaction | Not available without parallel track | Native |
| Guardrail injection | Not available without parallel track | Native |
| Intermediate transcript logging | Requires parallel track | Native |
| Debugging / root cause analysis | Hard (audio-only trace) | Easy (text trace) |
| Tool use / function calling | Supported (event-based) | Supported (standard) |
| Multimodal (video + audio) | Gemini Live only | No |
| Provider session management | Ephemeral — requires external state | Managed by your code |
| Cost per minute | Typically higher than cascading | Typically lower |
| Compliance suitability (regulated industries) | Requires parallel track + audit | Strong |

**Rule of thumb**: S2S is a latency optimization, not an architecture simplification. In regulated contexts, the parallel transcript pattern often erases the simplicity benefit. Choose S2S when: you have measured that 700ms cascading latency is causing user complaints, and you are willing to add the parallel transcript infrastructure to preserve compliance.

---

## Session-State Loss on Model Switch

When switching between S2S model versions (e.g., an older Realtime generation → the current one), the existing WebSocket session cannot be migrated. All in-session state (conversation history, voice configuration, tool context) is lost.

**Resolution**:

1. Persist conversation state to Redis after every turn (see pattern above).
2. Define the model version at deploy time, not at session start — use a feature flag to control model version transitions.
3. Canary-test model version changes on a small traffic slice before full rollout.
4. Log the model version per session in your audit trail — model switches during production incidents are a common root cause of behavior regressions.

This trap is described in the Known Traps section of SKILL.md.

---

## Integration with Pipecat

Pipecat supports OpenAI Realtime via `OpenAIRealtimeLLMService` (the current class; the older `OpenAIRealtimeBetaLLMService` is deprecated and slated for removal — migrate off it). Check the installed Pipecat package version for the exact import path, since service module paths have moved between releases. The S2S model replaces the LLM node in the standard pipeline; STT and TTS processors are removed when using pure S2S.

For the parallel transcript pattern, add a second STT processor alongside the transport input and route its output to a separate compliance handler, not to the LLM.

See [`references/pipecat-patterns.md`](references/pipecat-patterns.md) for the S2S pipeline configuration.

---

## Integration with LiveKit Agents

LiveKit Agents supports OpenAI Realtime via the `openai.realtime` plugin (check current LiveKit Agents release notes for exact plugin name and version). The `VoicePipelineAgent` is replaced or complemented by the Realtime-aware agent class.

See [`references/livekit-agents-patterns.md`](references/livekit-agents-patterns.md) for the S2S agent configuration.
