---
name: ai-voice-bots
description: "Builds production voice bots and IVR with Python STT/TTS pipelines. Use when designing telephony, streaming audio, latency budgets, or voice quality monitoring."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# AI Voice Bots

Use this skill to build, ship, and tune voice bots — phone IVR, real-time speech agents, and voice-first customer interactions — using pure Python frameworks.

This skill owns the voice-specific pipeline: STT, TTS, telephony platforms, latency engineering, and voice quality. For conversation design, persona, and escalation patterns, use [`../ai-bot-builder/SKILL.md`](../ai-bot-builder/SKILL.md).

Default to a streaming STT→LLM→TTS pipeline when text inspection, redaction, or deterministic call state is required. Choose Pipecat for custom transports and LiveKit Agents for LiveKit room or SIP integration. Test speech-to-speech (S2S) against the same target calls when latency or multimodal behavior may justify a different pipeline; see [references/s2s-and-native-voice-apis.md](references/s2s-and-native-voice-apis.md).

## When to Use This Skill

- Building a voice bot for phone, IVR, or real-time speech
- Choosing a telephony platform (Twilio, Vapi, Bland.ai, Retell, Telnyx, Vonage)
- Choosing a voice pipeline framework (Pipecat, LiveKit Agents, Vocode)
- Engineering latency budgets for voice (TTFB, total turn latency)
- Selecting and configuring STT/TTS providers (Deepgram, ElevenLabs, Cartesia, Azure)
- Monitoring voice quality (MOS, WER, call completion rate)
- Designing IVR flows with DTMF and voice hybrid
- Building outbound dialing campaigns

## When NOT to Use This Skill

| Need | Route to |
|------|----------|
| Bot conversation design, persona, escalation | [`../ai-bot-builder/SKILL.md`](../ai-bot-builder/SKILL.md) |
| Text-only bot architecture | [`../ai-bot-builder/SKILL.md`](../ai-bot-builder/SKILL.md) |
| General agent architecture | [`../ai-agents/SKILL.md`](../ai-agents/SKILL.md) |
| WebSocket/SSE infrastructure (non-voice) | [`../software-realtime/SKILL.md`](../software-realtime/SKILL.md) |
| Voice/multimodal reference material | [`../ai-agents/references/voice-multimodal-agents.md`](../ai-agents/references/voice-multimodal-agents.md) |

## Quick Reference

| Need | Default | Notes |
|------|---------|-------|
| Choose telephony platform | `references/telephony-platform-selection.md` | Twilio, Vapi, Bland.ai, Retell, Telnyx, Vonage |
| Design voice pipeline | `references/voice-pipeline-architecture.md` | STT→LLM→TTS streaming, codec selection |
| Build with Pipecat | `references/pipecat-patterns.md` | Processors, transports, production deployment |
| Build with LiveKit Agents | `references/livekit-agents-patterns.md` | AgentSession, rooms, plugins |
| Optimize latency | `references/latency-engineering.md` | Component budgets, edge deployment, caching |
| Monitor voice quality | `references/voice-quality-metrics.md` | MOS, WER, dashboards, alerting |
| Design IVR flows | `references/ivr-design.md` | DTMF, menu trees, hybrid voice+keypad |
| Voice compliance | `references/voice-safety-compliance.md` | Recording consent, PCI, TCPA, GDPR |
| Deploy voice bot to 24/7 production | [references/production-deployment.md](references/production-deployment.md) | Concurrent-call capacity, SIP/PSTN HA, autoscaling, drain, recording compliance, cost model |
| Pick a hosting platform (LiveKit Cloud + Fly.io, Pipecat Cloud, etc.) | [`../software-paas-hosting/references/agent-hosting-matrix.md`](../software-paas-hosting/references/agent-hosting-matrix.md) | Voice stacks BV1–BV3 + what does NOT host voice |

## Default Workflow

1. **Define call flow** — inbound vs outbound, IVR menu tree, conversation states.
2. **Choose telephony platform** — by volume, region, compliance, and API quality.
3. **Choose voice pipeline framework** — Pipecat (default) or LiveKit Agents.
4. **Set latency budgets** — measure each stage on target call conditions and set a product-specific percentile target.
5. **Select STT/TTS providers** — by language support, latency, quality, and cost.
6. **Integrate conversation logic** — use `ai-bot-builder` patterns for the LLM "brain."
7. **Add voice-specific guardrails** — AI identity disclosure where required, recording consent as a separate step, PII in speech, and barge-in safety; use [voice-safety-compliance.md](references/voice-safety-compliance.md).
8. **Instrument voice quality metrics** — MOS, WER, call completion, latency percentiles.
9. **Load test and tune** — verify latency under concurrent call load.

## Voice Pipeline Architecture

```
Phone/WebRTC → Transport → STT → LLM → TTS → Transport → Phone/WebRTC
                  │          │      │      │         │
                  │          │      │      │         └── Audio codec encoding
                  │          │      │      └── Text-to-speech streaming
                  │          │      └── Conversation logic (ai-bot-builder)
                  │          └── Speech-to-text streaming
                  └── WebSocket / WebRTC / SIP
```

**Pipeline budget:** Measure each component and the end-to-end first-audio time before setting numerical targets. Streaming stages overlap, so summing component durations does not necessarily equal perceived turn latency.

| Component | Measure |
|-----------|---------|
| VAD or turn detector | End-of-speech to end-of-turn decision |
| STT | Audio to stable transcript, including partials |
| LLM | Request to first usable output token |
| TTS | Text availability to first playable audio |
| Transport | Caller network and SIP/WebRTC delivery |

Full depth → [references/voice-pipeline-architecture.md](references/voice-pipeline-architecture.md)

## Telephony Platform Selection

Default to the telephony provider already approved for the target geography and call type. Compare its current number/SIP availability, recording controls, transfer behavior, concurrent-call limits, and pricing against the [official provider documentation](references/telephony-platform-selection.md) before changing platforms.

Full comparison → [references/telephony-platform-selection.md](references/telephony-platform-selection.md)

## Framework Selection

| Framework | Best for | Transport | S2S support | Ecosystem |
|-----------|----------|-----------|-------------|-----------|
| **Pipecat** (default) | Custom voice pipelines, multi-transport | WebSocket, Twilio, Daily, WebRTC | Yes (OpenAI Realtime, Gemini Live) | Deepgram, ElevenLabs, Cartesia, Anthropic, OpenAI |
| **LiveKit Agents** | Room-based voice, recording, multi-party | LiveKit (WebRTC) | Yes (OpenAI Realtime) | LiveKit Cloud, STT/TTS plugins |
| **Vocode** | Simple voice bots, telephony focus | Twilio, Vonage, WebSocket | No | Deepgram, Azure, ElevenLabs |

Default: **Pipecat** — strongest Python ecosystem, composable pipeline processors, multi-transport support, and broadest S2S provider coverage.

Use **LiveKit Agents** when: multi-participant calls, built-in recording, or already using LiveKit infrastructure.

### S2S vs cascading

If an inline text gate must block unsafe output before the caller hears it, use the cascading pipeline. If that gate is not required and a same-call-set test shows S2S improves the chosen latency or experience metric, use S2S. A parallel transcript can help audit after the fact but cannot block already-spoken audio. Check the current model, regional availability and price in the provider docs before selection.

Full S2S reference → [references/s2s-and-native-voice-apis.md](references/s2s-and-native-voice-apis.md)

## Production Defaults

- **Framework:** Pipecat with streaming pipeline
- **STT/TTS:** Select from the providers supported by the installed framework. Compare language/accent accuracy, first-audio latency, interruption recovery and current provider terms on target calls; see [voice-pipeline-architecture.md](references/voice-pipeline-architecture.md).
- **LLM:** Choose by measured task success, tool reliability, latency and cost for the call flow.
- **Transport:** Use the approved SIP/PSTN or WebRTC integration for the target region and codec.
- **Latency target:** Set p50/p95 and interruption targets from the product's call tests; do not import a vendor benchmark as the SLO.
- **Quality monitoring:** MOS tracking, WER sampling, call completion rate
- **Compliance:** Recording consent per jurisdiction, PII redaction from transcripts

## Expert Judgment: Latency Budget and Barge-In

**Decompose the budget before optimizing.** Attribute delay to VAD, STT, LLM first token, TTS first audio, and network. The bottleneck can be turn detection or a cold TTS connection even when the LLM is fast. Full instrumentation → [latency-engineering.md](references/latency-engineering.md); queueing effects → [queueing-theory-applied.md](references/queueing-theory-applied.md).

**Barge-in is a cancellation path.** A user talking over the bot must stop the in-flight audio and pending generation promptly. Measure time to actual audio stop, false interruptions and recovery separately from end-of-turn latency. See [queueing-theory-applied.md](references/queueing-theory-applied.md) (P3, A3).

Recompare S2S and cascading when changing models or providers. Use the same target-region calls to measure first audio, task success, tool safety and transcript needs; see [s2s-and-native-voice-apis.md](references/s2s-and-native-voice-apis.md).

## Real-Call Launch Gate

Test the target languages, accents, codecs, handset networks, background noise, silence, barge-in, DTMF, transfer, provider timeout, and reconnect paths with real or replayed call audio. Report end-of-turn and first-audio latency percentiles, interruption success, task completion, false transfer, hang-up, and consent-capture rates by scenario. Launch only when every blocking scenario has a deterministic fallback and the concurrent-call test meets the same bounds. A provider connection or synthetic clean-audio demo is not launch evidence.

## Known Traps

- proving latency with synthetic lab prompts instead of real barge-in, interruption, packet-loss, and handset-network conditions
- treating telephony acceptance as conversation success when the real failure is post-answer latency, bad turn segmentation, or TTS overlap
- mixing recording, transcript retention, PCI redaction, and consent rules across regions without one explicit policy owner
- optimizing only average latency while ignoring p95 or p99 tails that make production calls feel broken
- shipping one STT or TTS provider path with no fallback, rollback, or degraded-mode behavior for provider incidents
- **S2S session-state loss on model switch**: switching between S2S model versions mid-session (any provider — OpenAI Realtime, Gemini Live) drops all ephemeral session state — voice, tone configuration, conversation history, and tool state are not carried over. Resolution: persist conversation state to an external store (Redis or Postgres) after every turn; reload from the store when resuming or switching models. Do not rely on the S2S session as a state store for anything you cannot afford to lose. See `references/s2s-and-native-voice-apis.md` for the full session management pattern.

## Common Anti-Patterns

- **Batch-style voice pipelines** — waiting for full utterances or full synthesis destroys turn-taking and makes the bot feel laggy
- **LLM-first architecture with no deterministic call state** — IVR routing, transfers, and compliance prompts need explicit state machines, not only prompt logic
- **One-metric quality reporting** — MOS alone or WER alone hides interruption quality, completion failures, and escalation pain
- **Treating outbound voice like chat automation** — dialing, consent, voicemail handling, and retry policy need channel-specific controls
- **Using text-bot guardrails unchanged for speech** — voice bots need barge-in, silence, DTMF, and speaking-over-user protections

## Navigation

**References**
- [references/index.md](references/index.md) — Reference navigation map
- [references/s2s-and-native-voice-apis.md](references/s2s-and-native-voice-apis.md) — S2S vs cascading, OpenAI Realtime API, Gemini Live, session management (Jul 2026)
- [references/telephony-platform-selection.md](references/telephony-platform-selection.md) — Platform comparison
- [references/voice-pipeline-architecture.md](references/voice-pipeline-architecture.md) — Pipeline design
- [references/pipecat-patterns.md](references/pipecat-patterns.md) — Pipecat deep dive
- [references/livekit-agents-patterns.md](references/livekit-agents-patterns.md) — LiveKit Agents deep dive
- [references/latency-engineering.md](references/latency-engineering.md) — Latency optimization
- [references/voice-quality-metrics.md](references/voice-quality-metrics.md) — Quality monitoring
- [references/ivr-design.md](references/ivr-design.md) — IVR flow design
- [references/voice-safety-compliance.md](references/voice-safety-compliance.md) — Voice compliance
- [references/queueing-theory-applied.md](references/queueing-theory-applied.md) — Queueing theory applied to voice: latency budget partitioning, jitter buffer sizing, Erlang-C IVR capacity, barge-in priority, TTS streaming targets

**Assets**
- [assets/voice-bot-spec.md](assets/voice-bot-spec.md) — Voice bot specification template
- [assets/voice-latency-budget.md](assets/voice-latency-budget.md) — Latency budget worksheet
- [assets/voice-quality-checklist.md](assets/voice-quality-checklist.md) — Pre-launch quality gate
- [assets/voice-eval-scenarios.md](assets/voice-eval-scenarios.md) — End-to-end voice-agent eval scenario template

**Scripts**
- `python3 scripts/voice_latency_audit.py --input pipeline_logs.jsonl` — Pipeline latency breakdown
- `python3 scripts/call_quality_scorer.py --input calls.jsonl` — Call quality scoring

**Data**
- [data/sources.json](data/sources.json) — Curated voice-specific sources

## Related Skills

- [../ai-bot-builder/SKILL.md](../ai-bot-builder/SKILL.md) — Conversation design, persona, escalation, LangGraph
- [../ai-context-layer/references/conversational-surfaces-cross-platform.md](../ai-context-layer/references/conversational-surfaces-cross-platform.md) — Cross-platform composition recipe; voice section specifies the RA13 hot/cold memory tier split required for sub-300 ms turn latency
- [../ai-agents/SKILL.md](../ai-agents/SKILL.md) — Agent architecture decisions
- [../ai-agents/references/voice-multimodal-agents.md](../ai-agents/references/voice-multimodal-agents.md) — Voice/multimodal agent reference
- [../software-realtime/SKILL.md](../software-realtime/SKILL.md) — WebSocket/SSE infrastructure
- [../qa-agent-testing/SKILL.md](../qa-agent-testing/SKILL.md) — Agent eval harnesses
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md) — Pipeline telemetry

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
