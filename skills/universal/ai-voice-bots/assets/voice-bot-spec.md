# Voice Bot Specification Template

Use this template to define a voice bot before implementation.

## Bot Identity

- **Name:** [bot name]
- **Voice:** [e.g., "Female, American English, warm professional tone"]
- **TTS provider/voice ID:** [e.g., "ElevenLabs / Rachel"]
- **Persona:** [brief personality — e.g., "Patient, clear, solution-oriented"]
- **Channel:** [phone / web / in-app]

## Call Flow

### Inbound / Outbound
- **Type:** [inbound / outbound / both]
- **Phone number(s):** [dedicated number(s)]
- **Operating hours:** [24/7 or specific hours with after-hours handling]

### IVR Structure
```
[greeting]
├── Press 1 or say "Orders" → [order_flow]
├── Press 2 or say "Billing" → [billing_flow]
├── Press 3 or say "Support" → [support_flow]
└── Press 0 or say "Agent" → [human_transfer]
```

### Conversation States
1. **[State name]:** [Entry condition] → [Key actions] → [Exit transitions]
2. **[State name]:** ...

## Voice Pipeline

| Component | Provider | Config |
|-----------|----------|--------|
| Transport | [Twilio / Daily / WebRTC] | [SIP trunk / Media Streams] |
| STT | [Deepgram Nova-3 / AssemblyAI Universal-2 / Azure] | [Language, model variant] |
| LLM | [Claude Sonnet / GPT-4o / Gemini] | [Model, temp, max tokens] |
| TTS | [ElevenLabs / Cartesia / Azure] | [Voice ID, speed, stability] |
| VAD | [Silero / WebRTC / energy-based] | [Threshold, silence duration] |

## Latency Budget

| Component | Target (ms) | Actual (ms) |
|-----------|-------------|-------------|
| VAD end-of-speech | 250 | [measure] |
| STT processing | 150 | [measure] |
| LLM TTFB | 200 | [measure] |
| TTS first chunk | 100 | [measure] |
| Network RTT | 30 | [measure] |
| **Total turn latency** | **< 700** | **[measure]** |

## Telephony Integration

- **Platform:** [Twilio / Telnyx / Vonage]
- **Number type:** [local / toll-free / short code]
- **Geographic coverage:** [countries/regions]
- **Concurrent call capacity:** [number]
- **Fallback:** [if bot fails, route to: queue / voicemail / callback]

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total turn latency (p90) | < 700ms | Pipeline instrumentation |
| Call completion rate | > [X]% | Calls reaching resolution/transfer |
| Containment rate | > [X]% | Resolved without human |
| MOS (estimated) | > 3.5 | Voice quality scoring |
| WER | < [X]% | Transcript accuracy sampling |
| Cost per call | < $[X] | Telephony + STT + LLM + TTS |

## Compliance

- [ ] Recording consent disclosure implemented
- [ ] PCI: recording paused during payment info collection
- [ ] TCPA: outbound calling hours enforced (if applicable)
- [ ] GDPR: voice data retention policy defined
- [ ] PII redaction configured for stored transcripts

## Pre-Launch Checklist

- [ ] Pipeline latency measured and within budget
- [ ] Barge-in tested and working
- [ ] Fallback to human tested end-to-end
- [ ] IVR DTMF paths tested
- [ ] Concurrent call load test passed
- [ ] Voice quality (MOS/WER) within targets
- [ ] Compliance requirements met for all target jurisdictions
- [ ] Monitoring and alerting configured
