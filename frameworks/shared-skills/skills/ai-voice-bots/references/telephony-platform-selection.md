# Telephony Platform Selection

**Purpose**: Choose the right telephony platform for voice bot deployment by use case, budget, geography, and compliance needs.

No theory. Decision matrices and migration guidance only.

---
## Table of Contents

- [Platform Overview](#platform-overview)
- [Twilio Programmable Voice](#twilio-programmable-voice)
- [Vapi](#vapi)
- [Bland.ai](#blandai)
- [Retell](#retell)
- [Telnyx](#telnyx)
- [Vonage (Vonage Communications APIs)](#vonage-vonage-communications-apis)
- [Decision Matrix by Use Case](#decision-matrix-by-use-case)
- [Pricing Comparison (May 2026)](#pricing-comparison-may-2026)
- [Per-Minute Rates (US Inbound)](#per-minute-rates-us-inbound)
- [Monthly Cost Estimate: 10K Minutes](#monthly-cost-estimate-10k-minutes)
- [Feature Comparison Matrix](#feature-comparison-matrix)
- [Geographic Coverage](#geographic-coverage)
- [Compliance and Regulatory](#compliance-and-regulatory)
- [Integration Depth](#integration-depth)
- [Migration Considerations](#migration-considerations)
- [Common Migration Paths](#common-migration-paths)
- [Migration Checklist](#migration-checklist)
- [Quick Decision Guide](#quick-decision-guide)
- [Related References](#related-references)

---

## Platform Overview

### Twilio Programmable Voice

**Best for**: Full control over the voice pipeline with custom STT/TTS/LLM integration.

| Attribute | Detail |
|-----------|--------|
| **Core feature** | Media Streams (raw audio via WebSocket), TwiML for IVR, SIP trunking |
| **Pipeline control** | Full — you own STT, LLM, TTS selection and orchestration |
| **Pricing** | ~$0.013/min inbound US, ~$0.014/min outbound US + phone number fees |
| **Global PSTN** | 100+ countries, local/toll-free/mobile numbers |
| **SIP trunking** | Elastic SIP Trunking for BYO carrier integration |
| **Recording** | Built-in call recording with dual-channel support |
| **Compliance** | HIPAA eligible, PCI DSS Level 1, SOC 2 Type II, GDPR |
| **Strengths** | Massive ecosystem, battle-tested at scale, Media Streams for custom audio |
| **Weaknesses** | No built-in AI pipeline — you wire STT/LLM/TTS yourself, complex pricing |

**When to use Twilio:**
- You need full pipeline control (custom STT/TTS/LLM choices)
- Global PSTN coverage matters
- SIP trunking into existing PBX/contact center
- Enterprise compliance requirements (HIPAA, PCI)
- You have engineering capacity to build and maintain the pipeline

### Vapi

**Best for**: Fastest time-to-market with managed voice AI pipeline.

| Attribute | Detail |
|-----------|--------|
| **Core feature** | Managed STT→LLM→TTS orchestration, built-in voice pipeline |
| **Pipeline control** | Medium — choose STT/TTS/LLM providers via config, platform manages orchestration |
| **Pricing** | $0.05/min orchestration fee + provider costs. Realistic total: $0.13-0.31/min depending on STT/LLM/TTS providers chosen |
| **Telephony** | Built-in phone numbers (US/EU), SIP trunk support |
| **Recording** | Built-in with transcription |
| **Compliance** | SOC 2 Type II, HIPAA eligible |
| **Strengths** | Fast prototyping, one API for everything, handles latency optimization |
| **Weaknesses** | Less control over pipeline internals, vendor lock-in on orchestration layer |

**When to use Vapi:**
- Rapid prototyping or MVP (days, not weeks)
- Small team without voice pipeline expertise
- All-inclusive pricing simplifies budgeting
- You want managed latency optimization out of the box

### Bland.ai

**Best for**: Outbound calling campaigns with simple conversational agents.

| Attribute | Detail |
|-----------|--------|
| **Core feature** | Outbound batch dialing, simple conversational AI agents |
| **Pipeline control** | Low — platform manages the full pipeline, you configure via API |
| **Pricing** | ~$0.09/min connected (outbound), reduced rates for volume |
| **Telephony** | US-focused, outbound-optimized, limited inbound |
| **Recording** | Built-in with transcription |
| **Compliance** | TCPA-aware features (calling hours, DNC integration) |
| **Strengths** | Purpose-built for outbound, batch campaign management, simple API |
| **Weaknesses** | Limited inbound support, US-centric, less pipeline customization |

**When to use Bland.ai:**
- Outbound sales/appointment campaigns
- Batch dialing with retry logic
- Simple conversational flows (not complex IVR)
- US-focused operations

### Retell

**Best for**: Enterprise voice agents with low latency and custom LLM integration.

| Attribute | Detail |
|-----------|--------|
| **Core feature** | Enterprise voice agent platform, custom LLM integration, ~600ms response latency |
| **Pipeline control** | Medium-high — custom LLM endpoints, configurable STT/TTS |
| **Pricing** | ~$0.07-0.12/min depending on plan + platform fee |
| **Telephony** | US/EU/APAC numbers, SIP trunk support |
| **Recording** | Built-in with analytics |
| **Compliance** | SOC 2 Type II, HIPAA eligible, enterprise security |
| **Strengths** | Low latency focus, enterprise features, custom LLM hosting support |
| **Weaknesses** | Higher cost, enterprise-oriented pricing, smaller ecosystem than Twilio |

**When to use Retell:**
- Enterprise voice agents with SLA requirements
- Need custom LLM integration (self-hosted models)
- Multi-region deployment (US/EU/APAC)
- Advanced analytics and call intelligence

### Telnyx

**Best for**: Cost-efficient SIP/PSTN with programmable voice.

| Attribute | Detail |
|-----------|--------|
| **Core feature** | SIP trunking, programmable voice, global PSTN |
| **Pipeline control** | Full — similar to Twilio, you own the pipeline |
| **Pricing** | ~$0.007/min inbound US, ~$0.01/min outbound US (lower than Twilio) |
| **Global PSTN** | 80+ countries, private IP network |
| **SIP trunking** | Full SIP trunking with BYO carrier |
| **Recording** | Built-in call recording |
| **Compliance** | SOC 2 Type II, HIPAA eligible, GDPR |
| **Strengths** | 40-50% lower cost than Twilio, private IP network (quality), media streaming |
| **Weaknesses** | Smaller ecosystem, fewer tutorials/examples, media streaming API less mature |

**When to use Telnyx:**
- Cost is the primary driver and you need PSTN
- High call volume makes per-minute savings significant
- You have pipeline engineering capacity (similar to Twilio)
- Private network quality matters (Telnyx owns its IP backbone)

### Vonage (Vonage Communications APIs)

**Best for**: Enterprise omnichannel with existing contact center integration.

| Attribute | Detail |
|-----------|--------|
| **Core feature** | SIP trunking, contact center integration, omnichannel (voice + SMS + video) |
| **Pipeline control** | Full — programmable voice with WebSocket audio streaming |
| **Pricing** | ~$0.014/min inbound US, enterprise volume discounts |
| **Global PSTN** | Global coverage, enterprise-grade |
| **SIP trunking** | Full SIP trunking, contact center connectors |
| **Recording** | Built-in with compliance features |
| **Compliance** | SOC 2 Type II, HIPAA, PCI DSS, GDPR |
| **Strengths** | Enterprise-grade, contact center integration, omnichannel |
| **Weaknesses** | Enterprise sales process, less developer-friendly than Twilio, complex pricing |

**When to use Vonage:**
- Existing Vonage/contact center infrastructure
- Enterprise omnichannel needs (voice + SMS + video in one platform)
- Contact center AI augmentation

---

## Decision Matrix by Use Case

| Use Case | First Choice | Second Choice | Avoid |
|----------|-------------|---------------|-------|
| **Custom pipeline, full control** | Twilio | Telnyx | Bland.ai |
| **Rapid MVP/prototype** | Vapi | Retell | Twilio (overkill) |
| **Outbound campaigns** | Bland.ai | Vapi | Vonage |
| **Enterprise inbound** | Retell | Twilio | Bland.ai |
| **High volume, cost-sensitive** | Telnyx | Twilio | Vapi |
| **Global coverage (50+ countries)** | Twilio | Telnyx | Bland.ai |
| **Contact center integration** | Vonage | Twilio | Bland.ai |
| **HIPAA compliance** | Twilio | Retell | Bland.ai |
| **Multi-party calls** | Twilio | Vonage | Bland.ai |

---

## Pricing Comparison (May 2026)

> **Verification required:** Telephony pricing, number availability, managed-platform S2S support, and compliance attestations change often. Treat this table as a planning baseline; verify against current vendor docs or contract terms before recommending or budgeting.

### Per-Minute Rates (US Inbound)

| Platform | Per-Minute Rate | Phone Number/mo | Notes |
|----------|----------------|-----------------|-------|
| Twilio | ~$0.013 | $1.15 (local) | STT/TTS billed separately |
| Vapi | $0.05 orch + provider costs | Included | $0.05 is orchestration only; realistic total $0.13-0.31/min |
| Bland.ai | ~$0.09 | Included (outbound) | Outbound-focused pricing |
| Retell | ~$0.07-0.12 | Included | Plan-dependent |
| Telnyx | ~$0.007 | $1.00 (local) | STT/TTS billed separately |
| Vonage | ~$0.014 | $1.00 (local) | Enterprise discounts available |

### Monthly Cost Estimate: 10K Minutes

| Platform | Telephony Only | With STT/TTS | Total Estimate |
|----------|---------------|-------------|----------------|
| Twilio | $130 | +$200-400 STT/TTS | $330-530 |
| Vapi | $500 orch | +$800-2600 providers | $1,300-3,100 |
| Bland.ai | $900 | Included | $900 |
| Retell | $700-1,200 | Included | $700-1,200 |
| Telnyx | $70 | +$200-400 STT/TTS | $270-470 |
| Vonage | $140 | +$200-400 STT/TTS | $340-540 |

> **Note**: "With STT/TTS" assumes Deepgram Nova-3 ($0.0077/min) + ElevenLabs Turbo v2.5 ($0.024/min). Actual cost depends on provider selection and negotiated rates. Recheck these provider prices before quoting them.

---

## Feature Comparison Matrix

### Geographic Coverage

| Platform | Countries | Local Numbers | Toll-Free | Mobile Numbers | SIP Trunking |
|----------|-----------|---------------|-----------|----------------|-------------|
| Twilio | 100+ | Yes | Yes | Yes | Yes |
| Vapi | US/EU | Limited | Limited | No | Yes |
| Bland.ai | US primary | US only | No | No | No |
| Retell | US/EU/APAC | Yes | Yes | Limited | Yes |
| Telnyx | 80+ | Yes | Yes | Yes | Yes |
| Vonage | Global | Yes | Yes | Yes | Yes |

### Compliance and Regulatory

| Platform | SOC 2 | HIPAA | PCI DSS | GDPR | TCPA Tools |
|----------|-------|-------|---------|------|------------|
| Twilio | Type II | Eligible | Level 1 | Yes | Yes |
| Vapi | Type II | Eligible | No | Yes | Limited |
| Bland.ai | Pending | No | No | No | Yes (calling hours) |
| Retell | Type II | Eligible | No | Yes | Limited |
| Telnyx | Type II | Eligible | No | Yes | Yes |
| Vonage | Type II | Yes | Level 1 | Yes | Yes |

### Integration Depth

| Platform | Raw Audio Stream | Custom STT/TTS | Custom LLM | WebSocket | SIP | REST API |
|----------|-----------------|----------------|------------|-----------|-----|----------|
| Twilio | Media Streams | Full control | Full control | Yes | Yes | Yes |
| Vapi | Limited | Provider selection | Provider selection | Yes | Yes | Yes |
| Bland.ai | No | Platform-managed | Platform-managed | No | No | Yes |
| Retell | Yes | Configurable | Custom endpoint | Yes | Yes | Yes |
| Telnyx | Media streaming | Full control | Full control | Yes | Yes | Yes |
| Vonage | WebSocket audio | Full control | Full control | Yes | Yes | Yes |

---

## Migration Considerations

### Common Migration Paths

| From | To | Effort | Key Challenges |
|------|-----|--------|----------------|
| Vapi → Twilio | High | Build entire STT/TTS/LLM pipeline from scratch |
| Twilio → Telnyx | Medium | API differences, phone number porting (2-4 weeks) |
| Bland.ai → Twilio | High | Rebuild pipeline + inbound support |
| Twilio → Vapi | Low-Medium | Simplify pipeline, map TwiML flows to Vapi config |
| Vonage → Twilio | Medium | API migration, number porting |

### Migration Checklist

1. **Phone number porting** — Initiate LOA (Letter of Authorization) early. Porting takes 2-4 weeks in the US, longer internationally.
2. **Audio pipeline** — If moving from managed (Vapi/Retell) to custom (Twilio/Telnyx), budget 2-4 weeks for pipeline development.
3. **Compliance** — Verify target platform meets same compliance requirements (HIPAA, PCI).
4. **Testing** — Run parallel on both platforms for 1-2 weeks before cutover.
5. **Monitoring** — Replicate dashboards and alerting on the new platform.
6. **Failover** — Keep the old platform active for 30 days post-migration as rollback insurance.

---

## Quick Decision Guide

```
Need full pipeline control?
├── Yes → Budget matters most?
│   ├── Yes → Telnyx
│   └── No → Twilio
└── No → Speed to market?
    ├── Yes → Vapi
    └── No → Outbound campaigns?
        ├── Yes → Bland.ai
        └── No → Enterprise with SLA?
            ├── Yes → Retell
            └── No → Existing contact center?
                ├── Yes → Vonage
                └── No → Vapi
```

---

## Related References

- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Pipeline design that sits on top of the telephony platform
- [pipecat-patterns.md](pipecat-patterns.md) — Pipecat framework (pairs with Twilio/Telnyx/Vonage)
- [livekit-agents-patterns.md](livekit-agents-patterns.md) — LiveKit Agents (alternative transport layer)
- [latency-engineering.md](latency-engineering.md) — Latency optimization across the full pipeline
- [voice-safety-compliance.md](voice-safety-compliance.md) — Compliance requirements per platform
