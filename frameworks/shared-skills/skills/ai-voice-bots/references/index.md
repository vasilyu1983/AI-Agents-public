# AI Voice Bots — Reference Index

Use this index to navigate to the right reference for your task.

## Platform and Framework Selection

| Reference | Use when |
|-----------|----------|
| [telephony-platform-selection.md](telephony-platform-selection.md) | Choosing between Twilio, Vapi, Bland.ai, Retell, Telnyx, Vonage |
| [pipecat-patterns.md](pipecat-patterns.md) | Building with Pipecat (default framework) |
| [livekit-agents-patterns.md](livekit-agents-patterns.md) | Building with LiveKit Agents |

## Pipeline Engineering

| Reference | Use when |
|-----------|----------|
| [voice-pipeline-architecture.md](voice-pipeline-architecture.md) | Designing STT→LLM→TTS streaming pipeline, codec selection |
| [latency-engineering.md](latency-engineering.md) | Optimizing component latency, edge deployment, caching |
| [s2s-and-native-voice-apis.md](s2s-and-native-voice-apis.md) | Choosing speech-to-speech vs cascading, OpenAI Realtime, Gemini Live |
| [queueing-theory-applied.md](queueing-theory-applied.md) | Capacity planning, jitter buffers, p95/p99 latency, barge-in priority |

## Quality and Operations

| Reference | Use when |
|-----------|----------|
| [voice-quality-metrics.md](voice-quality-metrics.md) | Monitoring MOS, WER, call completion, alerting |
| [ivr-design.md](ivr-design.md) | Designing IVR flows, DTMF, hybrid voice+keypad |
| [voice-safety-compliance.md](voice-safety-compliance.md) | Recording consent, PCI, TCPA, GDPR voice data |
| [production-deployment.md](production-deployment.md) | Deploying a voice agent for 24/7 production: concurrent-call capacity, LiveKit Cloud vs self-host, SIP/PSTN HA, autoscaling on active-calls, graceful drain, recording compliance, cost model |

## Cross-Skill Navigation

| Need | Skill |
|------|-------|
| Conversation design, persona, escalation | `ai-bot-builder` |
| Agent architecture decisions | [`../ai-agents/SKILL.md`](../ai-agents/SKILL.md) |
| Voice/multimodal agent reference | [`../ai-agents/references/voice-multimodal-agents.md`](../ai-agents/references/voice-multimodal-agents.md) |
| WebSocket/SSE infrastructure | [`../software-realtime/SKILL.md`](../software-realtime/SKILL.md) |
| Agent eval harnesses | [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md) |
