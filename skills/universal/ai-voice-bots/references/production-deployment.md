# Voice Bot Production Deployment

Use this reference for deploying **voice agents** (Pipecat, LiveKit Agents, native realtime APIs) to 24/7 production. Voice deployment differs from text bot deployment in latency budget, codec/SIP handling, concurrent-call capacity planning, and recording compliance.

Pair with [`voice-pipeline-architecture.md`](voice-pipeline-architecture.md) for the pipeline shape, [`latency-engineering.md`](latency-engineering.md) for the SLO budget, and [`telephony-platform-selection.md`](telephony-platform-selection.md) for SIP/PSTN vendor choice.

## Table of Contents

- [The Voice Production Stack](#the-voice-production-stack)
- [Concurrent-Call Capacity Planning](#concurrent-call-capacity-planning)
- [Hosting: LiveKit Cloud vs Self-Host vs Native APIs](#hosting-livekit-cloud-vs-self-host-vs-native-apis)
- [SIP / PSTN High Availability](#sip--pstn-high-availability)
- [Health Checks for Stateful Calls](#health-checks-for-stateful-calls)
- [Autoscaling on Concurrent Calls](#autoscaling-on-concurrent-calls)
- [Graceful Drain for Active Calls](#graceful-drain-for-active-calls)
- [Codec, Bandwidth, and Region](#codec-bandwidth-and-region)
- [Recording and Compliance](#recording-and-compliance)
- [Cost Model](#cost-model)
- [Observability and Quality Metrics](#observability-and-quality-metrics)
- [Pre-Production Checklist](#pre-production-checklist)
- [Common Failure Modes](#common-failure-modes)
- [Cross-References](#cross-references)

## The Voice Production Stack

```text
┌─────────────────────────────────────────────────────────────┐
│  PSTN / Carrier                                              │
│  (Twilio, Telnyx, Bandwidth, Vonage)                         │
└─────────────┬───────────────────────────────────────────────┘
              │ SIP trunk (primary + failover)
              ▼
┌─────────────────────────────────────────────────────────────┐
│  SIP Gateway / SBC                                           │
│  (Twilio Elastic SIP, FreeSWITCH, pjsua, LiveKit SIP)        │
└─────────────┬───────────────────────────────────────────────┘
              │ WebRTC / SIP
              ▼
┌─────────────────────────────────────────────────────────────┐
│  Media Server (sticky to call)                               │
│  - LiveKit Cloud, or                                         │
│  - LiveKit OSS self-host, or                                 │
│  - Pipecat Cloud, or                                         │
│  - mediasoup / Daily.co                                      │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  Agent Worker (per call)                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │  VAD     │→│  STT     │→│  LLM     │→│  TTS     │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│                       │            │                          │
│             Tool calls↓     Skills, RAG, MCP                  │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  Shared services: state (Redis), recording store (S3),       │
│  observability (Langfuse), compliance log, billing meter     │
└─────────────────────────────────────────────────────────────┘
```

Every layer is HA-critical. A single point of failure in SIP, media, or agent worker drops live customer calls.

## Concurrent-Call Capacity Planning

Voice bots scale on **concurrent calls**, not requests per second. One call holds resources for its entire duration (typical 2–8 minutes).

```
concurrent_calls = arrival_rate_per_minute × average_call_duration_minutes
```

Worked example: 60 calls/minute arriving, average 5 minutes per call = 300 concurrent calls.

Resource per concurrent call (May 2026 baseline):

| Resource | Per call | Notes |
|---|---|---|
| CPU | 0.25–0.5 vCPU | Audio resampling, VAD, codec work |
| Memory | 200–400 MB | STT buffer, conversation state |
| Network | 100 kbps bidirectional | Opus 32 kbps × 2 + RTCP overhead |
| Provider tokens/min | 1k–3k | LLM + STT + TTS combined |
| TTS chars/min | 1k–3k | Premium voice cost varies wildly |
| Recording storage | ~2 MB/min | Opus-compressed |

Plan for **2x peak** concurrent calls capacity. Voice traffic is bursty (event spikes, ad campaigns, business hours).

## Hosting: LiveKit Cloud vs Self-Host vs Native APIs

| Option | Time-to-prod | Cost at scale | Operational burden | Best for |
|---|---|---|---|---|
| **LiveKit Cloud** | Days | High at >500 concurrent | Low | Most teams; production-ready in May 2026 |
| **LiveKit OSS self-host** | Weeks | Low | High (SIP, scaling, TURN) | Cost-sensitive at >1000 concurrent |
| **Pipecat Cloud** | Days | Medium | Low | Pipecat-native teams, lower call volume |
| **OpenAI Realtime API** | Hours | Very high per minute | None | Prototypes, low-volume, ChatGPT-style demos |
| **Gemini Live** | Hours | Very high per minute | None | Google-ecosystem prototypes, long sessions |
| **Pure self-host (mediasoup + custom)** | Months | Lowest | Very high | Specific cost/regulation needs only |

**Note**: as of Jul 2026, Anthropic does not offer a builder-facing S2S realtime voice API comparable to OpenAI Realtime or Gemini Live — its shipped voice capability (Claude Code voice dictation, multilingual STT + ElevenLabs-subcontracted TTS) is a product feature, not an API you compose a voice bot pipeline on top of. For an "LLM brain" in a cascaded pipeline, Claude models are consumed as the text LLM stage, not as an S2S transport. Re-verify before assuming this has changed.

Decision rule:

- Under 100 concurrent calls and you control the carrier: LiveKit Cloud.
- 100–1000 concurrent with predictable load: LiveKit Cloud, evaluate self-host at year 2.
- Over 1000 concurrent or cost-sensitive: LiveKit OSS self-host on Kubernetes.
- Prototyping or low-volume internal: OpenAI Realtime API or Pipecat Cloud.

Avoid moving substrates mid-product. The migration cost is measured in months.

## SIP / PSTN High Availability

Single-carrier deployments fail. Plan for at minimum two carriers in active-active or active-passive.

```text
DID number → SIP routing layer ┬→ Carrier A (primary)
                                └→ Carrier B (failover, low DTMF latency)
```

Carrier strategies:

| Strategy | Setup | Failover time |
|---|---|---|
| **Carrier-managed failover** | Primary + secondary at carrier level | Carrier-dependent, often 30s+ |
| **DNS-based** | SRV records with weights | 30–120s (DNS TTL bound) |
| **SBC-level routing** | FreeSWITCH/Kamailio routes per call | <1s |
| **App-level retry** | On call setup failure, retry alternate carrier | Per-call, 1–5s |

SBC-level routing is the production baseline. App-level retry catches calls SBC missed.

Recording numbers in two carriers and provisioning failover is regulatory-relevant for KYC voice flows — work with [`telephony-platform-selection.md`](telephony-platform-selection.md) before signing carrier contracts.

## Health Checks for Stateful Calls

A Kubernetes-style HTTP liveness probe is insufficient for a media worker. The worker must report:

- WebRTC PeerConnection state
- Active call count
- Last successful STT and TTS provider call timestamp
- Last successful LLM call timestamp

```python
@app.get("/healthz")
def healthz():
    now = time.time()
    last_stt = state.last_stt_success_ts
    last_tts = state.last_tts_success_ts
    last_llm = state.last_llm_success_ts

    if state.active_calls > 0:
        if (now - last_stt) > 60 or (now - last_tts) > 60 or (now - last_llm) > 30:
            return JSONResponse({"status": "unhealthy"}, status_code=503)
    return {"status": "ok", "active_calls": state.active_calls}

@app.get("/readyz")
def readyz():
    if state.draining or state.active_calls > MAX_CALLS_PER_WORKER:
        return JSONResponse({"status": "not_ready"}, status_code=503)
    return {"status": "ready"}
```

Liveness probe is permissive (only fails after sustained issue); readiness probe controls traffic admission.

## Autoscaling on Concurrent Calls

Standard HPA on CPU is wrong for voice — a call uses constant CPU regardless of LLM activity. Autoscale on `active_calls_per_pod`.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 4
  maxReplicas: 50
  metrics:
  - type: Pods
    pods:
      metric:
        name: voice_agent_active_calls
      target:
        type: AverageValue
        averageValue: "20"  # 20 calls per pod target
```

Two warnings:

1. Scale-up must be aggressive. Voice traffic spikes don't wait — a 30-second autoscale delay drops 30 seconds of inbound calls.
2. Scale-down must be conservative. Draining requires waiting for active calls to end (typical 5–8 minutes). Set `scaleDown.stabilizationWindowSeconds: 600`.

Pre-warm pods before known traffic spikes (campaign launches, business hours start).

## Graceful Drain for Active Calls

A voice worker shutting down with active calls is worse than a text bot: the user hears silence or a hangup.

```python
class VoiceWorkerDrain:
    def __init__(self):
        self.draining = False

    async def shutdown(self):
        self.draining = True  # /readyz starts returning 503
        # Wait for active calls to end or hit max drain time
        deadline = time.time() + 600  # 10 minutes
        while self.active_calls > 0 and time.time() < deadline:
            await asyncio.sleep(2)
        if self.active_calls > 0:
            # Last resort: tell callers to call back
            for call in list(self.active_calls):
                await call.say("I need to transfer this call. Please call back in a moment.")
                await call.hangup()
```

Kubernetes setup:

```yaml
lifecycle:
  preStop:
    exec:
      command: ["python", "-m", "voice.drain"]
terminationGracePeriodSeconds: 700
```

Worse alternative if drain isn't possible: warm transfer to a human queue.

## Codec, Bandwidth, and Region

Codec choice impacts latency, cost, and quality.

| Codec | Bitrate | Latency add | Use |
|---|---|---|---|
| **Opus 32 kbps mono** | 32 kbps | 20–60 ms | Default for WebRTC |
| **PCMU / PCMA (G.711)** | 64 kbps | ~0 ms | PSTN baseline, mandatory on SIP |
| **Opus 16 kbps mono** | 16 kbps | 20–60 ms | Constrained mobile networks |

Region rules:

- Place media servers in the **caller's** region, not the LLM provider's.
- Acceptable round-trip media latency: <30 ms caller↔media, <150 ms media↔LLM provider.
- If your callers are global, use a multi-region media deployment with global IP anycast.

Bandwidth budgeting:

```
egress_per_call = (codec_bitrate × 2 directions × call_duration) × (1 + overhead)
overhead ≈ 0.3 (RTCP, signaling, headers)
```

For 32 kbps Opus, 5-minute call: ~25 MB egress. At 1k concurrent peak: ~25 GB/hour per region.

## Recording and Compliance

Recording rules in May 2026:

| Jurisdiction | Requirement |
|---|---|
| UK (FCA-regulated firms) | Mandatory recording for advice/transactions; 5y retention |
| EU GDPR | Lawful basis + clear consent disclosure |
| US (federal + most states) | One-party consent; 12 states need two-party |
| California | Two-party consent |
| EEA (FCA-equivalent) | MiFID II 5y retention for investment calls |

Implementation pattern:

```python
async def on_call_start(call):
    await call.announce("This call may be recorded for quality and compliance purposes.")
    if call.user_region in TWO_PARTY_CONSENT_REGIONS:
        consent = await call.ask_yes_no("Do you consent to recording?")
        if not consent:
            call.recording_enabled = False
            await call.announce("Understood — this call will not be recorded.")
            return
    call.recording_enabled = True
    await start_recording(call, storage_bucket="s3://compliance-recordings/...")
```

Storage:

- Encrypted at rest (AES-256, KMS-managed keys)
- Encrypted in transit (TLS to S3/GCS)
- Retention policy enforced (S3 Lifecycle, GCS Object Lifecycle)
- Access logged (CloudTrail, audit_log table)
- WORM-compliant for financial calls (Object Lock with retention)

If your bot is FCA-regulated, apply the relevant project-specific EMI patterns outside this portable voice-bot skill.

## Cost Model

Cost per call (5 minutes, May 2026 indicative):

| Component | Cost | Notes |
|---|---|---|
| STT | $0.04–$0.10 | Deepgram, Whisper, Anthropic native |
| LLM | $0.10–$0.40 | Current-generation flagship/mid tier (Claude Opus/Sonnet, GPT-5.x family, Gemini) — verify current pricing |
| TTS | $0.05–$0.30 | ElevenLabs / Cartesia / OpenAI |
| Telephony (inbound DID) | $0.02–$0.05 | |
| Media server (LiveKit Cloud) | $0.05–$0.10 | |
| Recording storage (5y, 25 MB) | $0.005 | S3 IA |
| **Total per 5-min call** | **$0.27–$0.96** | |

For 10k calls/day: ~$80–$290/day, $30k–$105k/year. Self-hosting + commodity STT can drop this 40–60%.

Always meter actual usage; never trust pre-launch estimates.

## Observability and Quality Metrics

| Metric | SLO target | Source |
|---|---|---|
| **Time to first audio** | <800 ms | Media server timestamps |
| **Turn latency (caller stops → bot starts)** | p50 <600 ms, p99 <1500 ms | Pipeline traces |
| **STT word error rate** | <5% on representative set | Eval samples |
| **TTS naturalness MOS** | >4.0 | Synthetic + spot checks |
| **Call completion rate** | >95% | Call dispositions |
| **Escalation rate** | <15% baseline | Tag on call end |
| **Recording success rate** | >99.5% | Storage write events |
| **Concurrent call ceiling** | Headroom >30% | Autoscaler metric |

Wire to Langfuse / Phoenix / OpenLLMetry plus a media-specific dashboard (LiveKit Cloud dashboards or Grafana).

## Pre-Production Checklist

- [ ] Two carriers configured with verified failover
- [ ] Recording consent disclosure tested in all target jurisdictions
- [ ] Recording storage encrypted, retained per regulation
- [ ] Media servers deployed in caller regions
- [ ] HPA configured on `active_calls_per_pod`
- [ ] Drain handler tested with simulated traffic
- [ ] Health and readiness probes verified
- [ ] Provider keys in secrets manager with rotation policy
- [ ] Provider fallback chain configured (STT and TTS)
- [ ] Eval suite covers golden calls and adversarial inputs
- [ ] Latency dashboard split by region
- [ ] Cost meter wired per call
- [ ] On-call runbook covers carrier outage, provider outage, mass call drop
- [ ] Kill-switch for new inbound calls (overload defense)
- [ ] Compliance log audited

## Common Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Single-carrier outage** | All inbound calls fail | Dual-carrier with SBC routing |
| **Slow autoscale** | Spike traffic dropped | Pre-warm + aggressive scale-up |
| **Drain dropping calls** | Hangups on deploy | Drain handler + long terminationGracePeriod |
| **STT provider outage** | Bot stops hearing user | Provider fallback chain |
| **TTS provider outage** | Bot stops speaking | Provider fallback + pre-rendered fallback audio |
| **LLM latency spike** | Long awkward silences | Filler phrases ("let me check…") + per-turn timeout |
| **Codec mismatch** | Robotic voice quality | Negotiate Opus or fall back to G.711 cleanly |
| **Recording gap** | Compliance violation | Recording success probe + alert on miss |
| **Region routing wrong** | High audio latency for callers | Geo-aware media server selection |
| **Concurrent call ceiling hit** | 503s on new calls | HPA tuned + busy-message graceful failure |

## Cross-References

- [`voice-pipeline-architecture.md`](voice-pipeline-architecture.md) — pipeline shape
- [`latency-engineering.md`](latency-engineering.md) — latency budget
- [`telephony-platform-selection.md`](telephony-platform-selection.md) — carrier choice
- [`s2s-and-native-voice-apis.md`](s2s-and-native-voice-apis.md) — native realtime API patterns
- [`livekit-agents-patterns.md`](livekit-agents-patterns.md) — LiveKit-specific patterns
- [`pipecat-patterns.md`](pipecat-patterns.md) — Pipecat-specific patterns
- [`voice-quality-metrics.md`](voice-quality-metrics.md) — quality measurement
- [`voice-safety-compliance.md`](voice-safety-compliance.md) — safety and recording compliance
- [`../../ai-bot-builder/references/stateful-rollout-and-blue-green.md`](../../ai-bot-builder/references/stateful-rollout-and-blue-green.md) — rollout strategy
- [`../../ai-agents/references/24-7-operating-model.md`](../../ai-agents/references/24-7-operating-model.md) — SLOs and oncall
- [`../../foundations-queueing-theory/SKILL.md`](../../foundations-queueing-theory/SKILL.md) — capacity modeling
