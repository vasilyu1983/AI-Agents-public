---
name: queueing-theory-applied
description: "Applied queueing-theory patterns, anti-patterns, and recipes for voice bots and IVR: latency budget partitioning, jitter buffer sizing, Erlang-C call-center math, barge-in prioritization, and TTS streaming targets."
type: reference
---

# Queueing Theory Applied to Voice Bots

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Applied patterns, anti-patterns, and recipes that translate queueing-theory primitives into voice-bot and IVR engineering decisions. Use this reference when partitioning a latency budget, sizing audio chunk queues, provisioning IVR concurrent-call capacity, or diagnosing tail latency in a cascading STT→LLM→TTS pipeline.

See [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md) for canonical primitive definitions, formulas, and worked examples (Little's Law, M/M/c, M/G/1/P-K, Erlang-C, Kingman, fork-join).

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 — End-to-End Latency Budget Partitioning (Jackson Network)](#p1--end-to-end-latency-budget-partitioning-jackson-network)
  - [P2 — Jitter Buffer Sizing for Streaming STT](#p2--jitter-buffer-sizing-for-streaming-stt)
  - [P3 — Barge-In and Pre-emption Priority Queues](#p3--barge-in-and-pre-emption-priority-queues)
  - [P4 — IVR Concurrent-Call Capacity via Erlang-C](#p4--ivr-concurrent-call-capacity-via-erlang-c)
  - [P5 — TTS Streaming Start-Token Target Time](#p5--tts-streaming-start-token-target-time)
  - [P6 — Turn-Taking Under Variable User Speech Length](#p6--turn-taking-under-variable-user-speech-length)
  - [P7 — Telephony Codec Encode/Decode Queue Depth](#p7--telephony-codec-encodedecode-queue-depth)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Blocking the Audio Path on Full LLM Response](#a1--blocking-the-audio-path-on-full-llm-response)
  - [A2 — No Jitter Buffer (Zero-Depth Audio Queue)](#a2--no-jitter-buffer-zero-depth-audio-queue)
  - [A3 — Fixed Barge-In Timeout Ignoring Per-Stage Variance](#a3--fixed-barge-in-timeout-ignoring-per-stage-variance)
  - [A4 — Ignoring Per-Stage CV² in the Latency Budget](#a4--ignoring-per-stage-cv-in-the-latency-budget)
- [Recipes](#recipes)
  - [R1 — Setting a 350 ms End-to-End Voice Latency Budget with Per-Stage Caps](#r1--setting-a-350-ms-end-to-end-voice-latency-budget-with-per-stage-caps)
  - [R2 — Sizing IVR Concurrent-Call Capacity with Erlang-C](#r2--sizing-ivr-concurrent-call-capacity-with-erlang-c)
  - [R3 — Reproducing Latency Under Bursty Arrivals in a Load Test](#r3--reproducing-latency-under-bursty-arrivals-in-a-load-test)
- [Composition](#composition)
- [Sources](#sources)

_Last verified: 2026-05-03._

---

## Patterns

### P1 — End-to-End Latency Budget Partitioning (Jackson Network)

**Problem**: how do you allocate the per-stage latency budget so that STT, LLM, TTS, and audio encoding stay inside the total turn-latency SLO (e.g. 700 ms p90)?

**Mechanism**: model the cascading pipeline as a Jackson network — each stage is an independent M/M/c (or M/G/1) queue. The end-to-end wait W_e2e = Σ W_i (serial stages). The bottleneck is the stage with the highest ρᵢ, and scaling the wrong stage does not reduce W_e2e.

**Pipeline map**:

```
Caller audio → [VAD] → [STT stream] → [LLM first-token] → [TTS first-chunk] → [Codec encode] → Caller audio
    λ calls/s    stage 1   stage 2         stage 3              stage 4             stage 5
```

**Example** — outbound sales bot at λ = 80 concurrent calls, each turn arriving at μ_vad = 5 turns/s:

| Stage | E[S] | CV²_s | ρ at μ | Wq (Kingman) | W = Wq + E[S] | Budget |
|-------|------|-------|--------|-------------|---------------|--------|
| VAD | 250 ms | 0.3 | 0.45 | 37 ms | 287 ms | 300 ms |
| STT (Deepgram streaming) | 120 ms | 0.5 | 0.22 | 7 ms | 127 ms | 150 ms |
| LLM first-token (Haiku) | 150 ms | 1.8 | 0.27 | 29 ms | 179 ms | 200 ms |
| TTS first-chunk (Cartesia) | 40 ms | 0.6 | 0.07 | 1 ms | 41 ms | 60 ms |
| Codec encode (G.711) | 5 ms | 0.1 | 0.01 | 0 ms | 5 ms | 10 ms |

Serial total W_e2e = 639 ms, inside a 700 ms p90 SLO. LLM first-token has the highest Kingman Wq because CV²_s = 1.8 (cold-start inference spikes). Reducing CV²_s at LLM (model warm-pool, pre-fetch) has more impact than reducing μ at any other stage.

**Design rules**:
- Solve flow balance before assigning budgets. W_e2e = Σ W_i only for serial, uncorrelated stages; parallel branches (echo cancellation + VAD) contribute max, not sum.
- After scaling any stage, re-solve: Jackson's theorem guarantees that scaling one stage moves the bottleneck to the next highest-ρ stage.
- Target ρ ≤ 0.70 at every stage — the Erlang-C wait curve is nonlinear; ρ = 0.80 inflates Wq by 2–3× relative to ρ = 0.70.
- Use measured p99/p50 ratios per stage as a quick CV²_s proxy: if p99/p50 > 4, CV²_s likely exceeds 2 and Kingman correction is mandatory.

**When to use**: initial pipeline budget allocation; diagnosing which stage is blowing the SLO in production.

---

### P2 — Jitter Buffer Sizing for Streaming STT

**Problem**: network jitter causes audio packet bursts that overflow the STT input ring buffer (dropped audio, transcript gaps) or force excessive buffering that adds latency.

**Mechanism**: the audio chunk queue is a finite D/D/1 or G/D/1 system. Packet inter-arrival jitter σ_j (standard deviation of arrival times) determines the buffer depth needed to absorb bursts without loss. Required buffer depth in packets:

```
N_buf ≥ ceil( σ_j / T_pkt ) + 1   (jitter-headroom rule)
```

where T_pkt = packet interval (e.g. 20 ms for G.711 at 50 pkt/s). The implied latency of the jitter buffer is N_buf × T_pkt. This is queuing latency added before STT — it must be subtracted from the STT stage budget.

**Example** — Twilio WebSocket stream to Deepgram:

A Twilio media stream sends 20 ms G.711 muLaw packets. Measured network jitter σ_j ≈ 18 ms (95th pct). Required buffer:

```
N_buf = ceil(18/20) + 1 = 2 packets → 40 ms buffering
```

At σ_j = 60 ms (mobile LTE variability): N_buf = ceil(60/20) + 1 = 4 packets → 80 ms — this fully consumes the 150 ms STT budget if left uncontrolled.

Correct design: set N_buf = 3 packets (60 ms) as a hard maximum. Implement Packet Loss Concealment (PLC) for packets arriving after the buffer deadline. STT providers (Deepgram, Azure) handle PLC natively — do not over-buffer to avoid PLC.

**Design rules**:
- Never set N_buf = 0 (synchronous passthrough). A single late packet stalls the STT decoder.
- Never set N_buf to "safe large values." Bufferbloat in the audio path adds queuing latency in front of every subsequent stage.
- Measure σ_j per telephony carrier and per network condition. Mobile 4G/5G has σ_j 3–5× higher than wireline VoIP.
- Alert when observed N_buf utilization exceeds 80% — this is a leading indicator of packet loss events.

**When to use**: sizing audio ingestion buffers in Pipecat, LiveKit Agents, or any raw WebSocket audio path.

---

### P3 — Barge-In and Pre-emption Priority Queues

**Problem**: a user speaks over the bot (barge-in). The in-flight TTS chunk and pending LLM response must be pre-empted immediately. Without priority queuing, the bot finishes its utterance before processing the user's interruption, creating a hostile interaction.

**Mechanism**: model two classes in a non-preemptive priority queue:
- **Class 1 (high)**: barge-in signal from VAD — must drain ahead of all Class 2 work
- **Class 2 (low)**: pending TTS audio chunks from the current bot turn

When VAD detects user speech onset (barge-in event), the Class 1 barge-in token is inserted at the head of the pipeline queue. Under non-preemptive priority, it waits at most one E[S_2] residual service period (the in-flight TTS chunk). Barge-in latency = E[S_2]/2 (mean residual) + propagation.

**Example** — Pipecat pipeline barge-in:

TTS chunks are 100–300 ms of audio (E[S_2] = 150 ms, CV²_s = 0.8). Without priority: the bot completes the current utterance before VAD signal is processed. With non-preemptive priority at the TTS processor, the maximum additional barge-in delay is one TTS chunk ≈ 300 ms. Barge-in feels immediate at < 350 ms total (VAD 50 ms + residual TTS chunk 300 ms).

**Design rules**:
- Implement barge-in by flushing the TTS generator buffer and canceling the LLM stream in Pipecat's `EndFrame` / `CancelFrame` flow — this is the software-level priority pre-emption.
- Do not set a fixed barge-in timeout. Fixed timeouts under-react when TTS chunks are long and over-react when latency is short (see A3).
- Monitor barge-in success rate: the fraction of VAD barge-in events where bot audio actually stops within 350 ms. Target ≥ 95%.
- For S2S (speech-to-speech) pipelines, pre-emption is handled by the server-VAD interrupt signal — verify the provider's interrupt latency SLA matches the budget.

**When to use**: any voice bot with barge-in capability; IVR flows where users can interrupt prompts.

---

### P4 — IVR Concurrent-Call Capacity via Erlang-C

**Problem**: how many concurrent call-handling slots (SIP channels, bot worker processes) are needed to keep the call-queue wait time below an SLO (e.g. "95% of calls answered within 3 seconds")?

**Mechanism**: model the IVR as an M/M/c queue. Each call is a customer; each bot worker is a server. Offered load a = λ × E[S_call]. Erlang-C gives C(c, a) = probability a new call must queue, and mean wait Wq = C(c, a) / (c × μ − λ). Size c until Wq ≤ SLO_wait.

**Example** — inbound customer support IVR:

Peak λ = 30 calls/min = 0.5 calls/s. Mean call duration E[S] = 4 min = 240 s (μ = 1/240 calls/s). Offered load a = 0.5 × 240 = 120 Erlangs.

```
c_min = ceil(a) + 1 = 122 workers (ρ = 0.984 — too close to 1)
```

At c = 140: ρ = 120/(140 × 1) = 0.857. Apply Erlang-C:

```
C(140, 120) ≈ 0.62
Wq = 0.62 / (140/240 − 0.5) = 0.62 / (0.583 − 0.5) = 0.62 / 0.083 ≈ 7.5 s
```

7.5 s violates a 3 s SLO. At c = 160: ρ = 0.75, C(160, 120) ≈ 0.11, Wq ≈ 1.1 s. This meets the SLO.

For cloud telephony platforms (Twilio, Telnyx), c maps to the concurrent media stream limit (purchased channel count). Set c = 165 (safety margin of one server beyond the Erlang-C minimum) and configure an overflow routing to human agents at queue depth = C(160, 120) × λ.

**Design rules**:
- Erlang-C assumes Poisson arrivals. Real call spikes (marketing campaigns, incidents) are bursty — treat the Erlang-C result as a lower bound; add 20–30% capacity headroom.
- For agent-handoff queues (bot → human agent), model the handoff stage separately with its own Erlang-C. The bot stage and human stage have different E[S] and c.
- At ρ > 0.85, Wq grows superlinearly. Adding one worker buys disproportionate wait-time reduction. Always compute the marginal SLO improvement of the last server.
- Erlang-B (loss model) applies when the IVR drops calls rather than queuing them (e.g. busy-signal behavior). Use Erlang-B to compute blocking probability B(c, a) and set channel count accordingly.

**When to use**: IVR capacity planning, concurrent bot-worker pool sizing, SIP channel purchase decisions.

---

### P5 — TTS Streaming Start-Token Target Time

**Problem**: TTS providers begin streaming audio only after accumulating a minimum text buffer (typically one sentence or N tokens). If the LLM produces a long preamble before the first sentence boundary, the TTS first-chunk delay blows the latency budget.

**Mechanism**: model TTS token accumulation as an M/D/1 queue where tokens arrive from the LLM at rate λ_tok (tokens/s) and the TTS "service event" fires when N_min tokens accumulate. The wait time until the first audio chunk:

```
W_tts_start ≈ N_min / λ_tok
```

For Cartesia Sonic-3 (N_min ≈ 8 tokens minimum sentence fragment) at λ_tok = 80 tokens/s:

```
W_tts_start ≈ 8 / 80 = 0.10 s = 100 ms
```

At λ_tok = 30 tokens/s (heavy LLM load): W_tts_start = 267 ms — 2.5× higher, with no change to the model.

**Design rules**:
- Target W_tts_start ≤ 150 ms. Achieve this by: (a) selecting fast LLM token generation (Haiku > Sonnet for TTFT at given load), (b) pre-seeding TTS with the first sentence fragment via prompt engineering ("begin with a short opener"), or (c) reducing N_min by choosing a TTS provider with lower sentence-boundary requirement (Cartesia at 8 tokens vs ElevenLabs at 15–20 tokens).
- The LLM→TTS boundary is a fork-join interaction if the LLM produces multiple clauses in parallel (tool-call fan-out scenarios). Apply the harmonic-number correction from fork-join primitives.
- Monitor `tts_first_chunk_latency_ms` as a production metric distinct from `turn_latency_ms`. The two can diverge under LLM load.

**When to use**: TTS provider selection, LLM response prompt engineering for latency, streaming pipeline instrumentation.

---

### P6 — Turn-Taking Under Variable User Speech Length

**Problem**: users speak for variable durations (CV²_speech >> 1: "yes" at 0.5 s vs. long complaint at 30 s). A pipeline tuned for short utterances accumulates a growing STT processing queue during long utterances, causing post-utterance latency spikes.

**Mechanism**: apply M/G/1 Pollaczek-Khinchine. Speech duration is the service time S with CV²_s measured from utterance histograms. At ρ = λ × E[S_speech]:

```
Wq_pk = ρ × E[S] × (1 + CV²_s) / (2 × (1 − ρ))
```

For a support bot: E[S_speech] = 4 s (mean utterance), CV²_s = 6.0 (highly variable — users answer questions with 1–30 s utterances), λ = 0.2 utterances/s per channel, ρ = 0.2 × 4 = 0.8.

```
Wq_pk = 0.8 × 4 × (1 + 6.0) / (2 × 0.2) = 0.8 × 4 × 3.5 = 11.2 s
```

11.2 s wait in the STT processing queue at ρ = 0.80. Under M/M/1 (CV²_s = 1), Wq would be 16 s — but P-K shows the actual variance of 6.0 inflates wait further.

**Design rules**:
- Measure utterance CV²_s from production VAD logs before capacity planning. The distribution is highly domain-dependent (yes/no IVR: CV²_s ≈ 0.5; open-ended intent: CV²_s ≈ 4–8).
- For high-CV²_s domains, use streaming STT (Deepgram streaming) rather than batch STT — streaming begins processing mid-utterance, reducing effective E[S] and ρ.
- Apply end-of-utterance detection (EOU) heuristics beyond fixed silence timeout. Adaptive EOU (e.g., neural EOU in Deepgram Nova-3) reduces E[S_speech] by cutting off trailing silence — the single highest-leverage intervention for high-CV²_s variance.

**When to use**: VAD/STT pipeline sizing for support or open-ended conversation bots.

---

### P7 — Telephony Codec Encode/Decode Queue Depth

**Problem**: the codec encode/decode stage (G.711 muLaw, Opus, G.729) is fast but the queue feeding it can accumulate during network congestion, adding silent latency.

**Mechanism**: codec queues are near-deterministic (CV²_s ≈ 0). Model as D/D/1. The only queue depth that matters is the one caused by upstream jitter (burst arrival from the audio path) rather than service variability. Apply the bufferbloat rule: queue depth in time units = buffer_size × T_frame. Never exceed 2–3 frames of buffering.

**Example** — G.711 at 8 kHz, 20 ms frames:
- 2-frame buffer = 40 ms latency contribution.
- If set to 20 frames (common "safe" default in some RTP stacks): 400 ms latency — consumes the entire downstream budget.

**Design rules**:
- Set codec encode queue depth = 2–3 frames maximum. Emit RTP packet loss (PLC) rather than buffering late frames.
- Monitor codec queue depth as a component metric. Depth > 3 frames indicates upstream network degradation — alert and optionally switch codec (Opus LBRC adaptive bitrate handles packet loss better than G.711).
- For Opus: use the VBR + constrained-bitrate mode to reduce encode latency variance (CV²_s drops from 0.3 to ~0.05).

**When to use**: WebRTC audio path tuning, Twilio or Telnyx media stream configuration.

---

## Anti-Patterns

### A1 — Blocking the Audio Path on Full LLM Response

**Symptom**: the pipeline waits for the LLM to finish the entire completion before sending the first token to TTS. The bot produces no audio for 800 ms–3 s after the user stops speaking, then speaks the full response all at once.

**Root cause**: the LLM stage is modeled as a batch job rather than a streaming queue. The full LLM response (E[S_llm] = 1.5 s at average completion length) is added as a single blocking service event. The TTS stage has zero queue depth — it receives nothing until LLM completes.

**Queueing diagnosis**: the LLM→TTS handoff is modeled as a synchronous gate rather than a streaming producer-consumer queue. Removing the gate converts the stage from M/D/1 (batch) to M/G/1/streaming, reducing W_tts_start from E[S_llm] to N_min/λ_tok.

**Fix**: use LLM streaming output (Anthropic streaming, OpenAI streaming). Buffer to the first sentence boundary (≤ N_min tokens), then start TTS immediately. The remaining LLM tokens arrive in parallel while the first TTS chunk plays.

**Detection**: measure `llm_response_complete_ms` vs `tts_first_chunk_ms`. If they are ≤ 50 ms apart, the pipeline is blocking on full LLM response.

---

### A2 — No Jitter Buffer (Zero-Depth Audio Queue)

**Symptom**: with σ_j > 10 ms network jitter, the STT provider reports frequent transcript gaps, missed words, or "audio discontinuity" errors. Transcript quality degrades on mobile or VoIP callers.

**Root cause**: the audio chunk queue has depth 0 — packets are passed to STT immediately on arrival. A late packet is either dropped (causing audio gap) or stalls the STT decoder until it arrives (adding stochastic latency).

**Queueing diagnosis**: N_buf = 0 violates the minimum buffering required for jitter absorption (N_buf ≥ ceil(σ_j / T_pkt) + 1). This is the audio equivalent of setting a server connection pool to size 0 — each arrival either blocks or drops.

**Fix**: add N_buf = ceil(measured_σ_j_p95 / T_pkt) + 1 frames of jitter buffer. Instrument σ_j per carrier/network type. Implement PLC for packets exceeding the buffer deadline.

**Detection**: STT provider "audio gap" or "discontinuity" error rate > 1% is the leading indicator.

---

### A3 — Fixed Barge-In Timeout Ignoring Per-Stage Variance

**Symptom**: the bot uses a fixed 500 ms barge-in silence timeout. On fast STT+LLM paths (E[S_vad] = 150 ms), the bot cuts off the user mid-word. On slow paths (LLM cold start), the timeout fires before the LLM has generated a first token, causing empty responses.

**Root cause**: a fixed timeout is equivalent to a deterministic service time D with CV²_s = 0. The real pipeline has high CV²_s (LLM first-token latency: CV²_s ≈ 2–4 due to model load variability). M/G/1 P-K shows that high CV²_s inflates the tail of processing time — the fixed timeout either fires too early (before LLM first-token) or too late (holding the user in silence).

**Fix**: set barge-in timeout dynamically from observed latency percentiles:

```
timeout_barge_in = P95(vad_latency) + P95(stt_latency) + P75(llm_first_token)
```

Re-compute per deployment (provider latency varies by region and load). For Pipecat: use `VADAnalyzerProcessor` with `min_speech_duration` calibrated per deployment, not a global default.

**Detection**: measure barge-in false-positive rate (user finished, bot still suppressing output) and false-negative rate (user still speaking, bot started generating).

---

### A4 — Ignoring Per-Stage CV² in the Latency Budget

**Symptom**: the voice pipeline passes SLO in a load test using constant synthetic prompts. In production with real users, p99 is 2–4× above the test result, even at the same call volume.

**Root cause**: synthetic load tests use deterministic or low-variance prompts — CV²_llm ≈ 0.3 in testing vs. CV²_llm ≈ 2.5 in production (user prompts vary widely in complexity and length). The Jackson-network budget was computed without a Kingman variability factor (VF = (CV²_a + CV²_s)/2). At VF = 3, the actual Wq at ρ = 0.70 is 3× the M/M/1 prediction.

**Fix**: measure CV²_s per stage from production logs (LLM first-token time histogram, STT latency histogram, TTS chunk latency histogram). Apply Kingman correction to each stage:

```
Wq_real_i ≈ Wq_erlang_i × VF_i
W_e2e_p99 ≈ Σ (Wq_real_i + E[S_i]) × tail_factor (1.5–2.0)
```

Budget to the Kingman-corrected W_e2e, not the M/M/1 baseline.

**Detection**: compare `latency_p50` to `latency_p99` per stage in production. If p99/p50 > 3 at any stage, CV²_s is high and Kingman correction is mandatory.

---

## Recipes

### R1 — Setting a 350 ms End-to-End Voice Latency Budget with Per-Stage Caps

**Goal**: achieve 350 ms p90 total turn latency (VAD end-of-speech to first TTS audio byte) on a Pipecat + Deepgram Nova-3 + Claude Haiku + Cartesia Sonic-3 pipeline.

**Steps**:

1. **Establish the end-to-end budget**: SLO_e2e = 350 ms p90. Subtract fixed transport overhead (WebSocket round-trip ≈ 20 ms per direction × 2 = 40 ms). Budget available for pipeline stages: 310 ms.

2. **Map serial stages and collect inputs**:

   | Stage | E[S] (p50) | CV²_s | Source |
   |-------|-----------|-------|--------|
   | VAD end-of-speech (Silero) | 50 ms | 0.4 | Pipecat latency logs |
   | STT final transcript (Deepgram Nova-3 streaming) | 80 ms | 0.6 | Deepgram streaming TTFB |
   | LLM first-token (Haiku on Bedrock) | 120 ms | 2.2 | Anthropic streaming TTFT histogram |
   | TTS first-chunk (Cartesia Sonic-3) | 40 ms | 0.5 | Cartesia TTFA benchmark |

3. **Apply Kingman correction per stage** (assume λ_turn = 0.3 turns/s per channel, ρ per stage computed from μ = 1/E[S]):

   | Stage | ρ | VF = (1 + CV²_s)/2 | Wq_kingman | W = Wq + E[S] | Budget cap |
   |-------|---|--------------------|-----------|---------------|------------|
   | VAD | 0.015 | 0.70 | 0.5 ms | 51 ms | 65 ms |
   | STT | 0.024 | 0.80 | 1.5 ms | 82 ms | 100 ms |
   | LLM first-token | 0.036 | 1.60 | 10 ms | 130 ms | 160 ms |
   | TTS first-chunk | 0.012 | 0.75 | 0.3 ms | 40 ms | 55 ms |

   Serial total W_e2e (mean) = 303 ms + 40 ms transport = 343 ms. Within the 350 ms p90 budget.

4. **Set hard per-stage alerting thresholds**:
   - VAD: alert at > 65 ms p90
   - STT: alert at > 100 ms p90
   - LLM first-token: alert at > 160 ms p90 (most likely to breach under heavy model load)
   - TTS: alert at > 55 ms p90

5. **Validate with Kingman tail factor**: p90 ≈ mean × 1.3 at CV²_s = 1. With CV²_s = 2.2 at LLM: p90/p50 ≈ 2.0. LLM stage p90 ≈ 130 ms × 2.0 = 260 ms. This blows the 160 ms cap. Mitigation: add LLM response caching for common intents; pre-warm model replicas; switch to Haiku on Vertex (lower TTFT variance).

6. **Re-verify after mitigation**: with LLM CV²_s reduced from 2.2 to 1.2 (warm pool), LLM p90 ≈ 130 × 1.5 = 195 ms. Pipeline p90 ≈ 51 + 82 + 195 + 40 + 40 = 408 ms. Still over budget. Scale LLM concurrency (c = 2 Haiku replicas per Pipecat worker pool): ρ drops to 0.018, Wq → 0 ms. Total p90 ≈ 368 ms — within 5% of the 350 ms SLO.

**Strongest outcome**: step 5 reveals that LLM first-token variance (CV²_s), not mean latency, is the driver of p90 breaches. Reducing CV²_s via warm-pool pre-warming is more effective than switching to a faster (but more variable) model.

---

### R2 — Sizing IVR Concurrent-Call Capacity with Erlang-C

**Goal**: determine the number of Twilio concurrent media stream slots and bot worker processes needed to keep 95% of calls waiting less than 5 seconds to enter IVR.

**Steps**:

1. **Measure inputs from telephony platform logs**:
   - Peak λ = 120 calls/hour = 0.033 calls/s
   - Mean call handling time E[S_call] = 180 s (3 minutes: IVR menu + bot conversation)
   - Offered load: a = λ × E[S_call] = 0.033 × 180 = 6.0 Erlangs

2. **Compute minimum stable capacity**:
   ```
   c_min = ceil(a) + 1 = 8 workers (ρ = 6.0/8 = 0.75)
   ```

3. **Solve Erlang-C at candidate capacity sizes**:

   | c workers | ρ | C(c, a) | Wq (s) | P(wait > 5s) |
   |-----------|---|---------|--------|--------------|
   | 8 | 0.750 | 0.51 | 36.7 s | ~95% (fails) |
   | 10 | 0.600 | 0.16 | 4.8 s | ~25% (near) |
   | 12 | 0.500 | 0.04 | 0.9 s | ~3% (passes) |

   At c = 10: Wq = 4.8 s — close to the 5 s SLO but C(10, 6) = 0.16 means 16% of calls wait. P(wait > 5 s) = C(c, a) × exp(−(c × μ − λ) × 5) ≈ 0.16 × exp(−(10/180 − 0.033) × 5) ≈ 0.16 × 0.87 ≈ 14%. Fails the 5% target.

   At c = 12: ρ = 0.50, Wq ≈ 0.9 s, P(wait > 5 s) ≈ 0.04 × exp(−10 × 5/180) ≈ 0.04 × 0.76 ≈ 3%. Passes.

4. **Apply Kingman correction for real call arrival bursts**: call center arrivals are bursty (marketing emails, news events) — CV²_a ≈ 2.0. Erlang-C assumes Poisson (CV²_a = 1). Kingman inflates Wq by VF = (2.0 + 1.0)/2 = 1.5 at the queue stage. Corrected Wq at c = 12: 0.9 × 1.5 = 1.35 s. Still well inside 5 s SLO.

5. **Set capacity and overflow**:
   - Purchase 14 Twilio concurrent media stream slots (c = 12 + 2 safety margin).
   - Configure overflow routing at queue depth = C(12, 6) × λ = 0.04 × 0.033 = 0.001 calls/s (effectively never) — overflow is a safety net for sudden traffic spikes, not a normal operating mode.
   - Deploy 12 bot worker processes on autoscaling group; set min = 12, max = 18 (1.5× peak).

6. **Agent-handoff queue sizing**: bot escalates 20% of calls to human agents. Human agent pool: λ_human = 0.006 calls/s, E[S_human] = 600 s (10 min). a_human = 3.6 Erlangs. Run Erlang-C separately for the human agent pool (c_agents = 5 for ρ = 0.72 and Wq < 30 s for human queue SLO).

**Strongest outcome**: step 3 shows that the "obvious" choice of c = 10 (just above the offered load of 6) fails the SLO because Erlang-C Wq is nonlinear near ρ = 0.60. The jump from c = 10 to c = 12 reduces Wq by 5× (4.8 s → 0.9 s) at only a 20% capacity increase — the last two servers buy the most SLO margin.

---

### R3 — Reproducing Latency Under Bursty Arrivals in a Load Test

**Goal**: reproduce production p99 latency in a load test by correctly modeling bursty call arrivals (CV²_a >> 1) rather than Poisson arrivals.

**Steps**:

1. **Measure production arrival process**: collect inter-arrival times from telephony CDR or Pipecat pipeline logs. Compute CV²_a = Var(T_arrival) / E[T_arrival]². Typical values:
   - Organic inbound IVR: CV²_a ≈ 1.0–1.5 (near-Poisson)
   - Post-campaign outbound: CV²_a ≈ 3–8 (highly bursty batches)
   - Webhook-triggered voice agents: CV²_a ≈ 0.3–0.7 (sub-Poisson, metered)

2. **Translate Kingman prediction to load test target**: from Kingman:
   ```
   Wq_target = (ρ / (1 − ρ)) × ((CV²_a + CV²_s) / 2) × E[S]
   ```
   Use measured CV²_a and CV²_s from step 1 and P1. This is the latency the load test must reproduce.

3. **Generate bursty arrival load**: use a Paced Poisson Arrivals (PPA) or Gamma-distributed inter-arrival time generator:
   - Gamma inter-arrival: shape k = 1/CV²_a, scale θ = E[T] × CV²_a
   - In Python (locust or custom harness):
     ```python
     import numpy as np
     cv2_a = 3.0
     mean_iat = 1.0 / lambda_calls  # seconds
     k = 1 / cv2_a
     theta = mean_iat * cv2_a
     iat = np.random.gamma(k, theta)
     ```
   - Poisson arrivals (standard `locust` default) correspond to CV²_a = 1. For CV²_a = 3, replace with Gamma above.

4. **Verify load test reproduces Kingman Wq**: run the load test at target ρ. Measure p50 and p99 per stage. Check:
   ```
   p50_stage ≈ E[S] + Wq_kingman  (within 20%)
   p99_stage / p50_stage ≈ 2–4 (consistent with CV²_s)
   ```
   If p99/p50 < 1.5, the load test is under-bursty — increase CV²_a in the arrival generator.

5. **Run the capacity headroom validation**: at target ρ = 0.70 with correct CV²_a and CV²_s, verify W_e2e_p99 ≤ SLO_e2e. If not, return to R1 (latency budget partitioning) and identify which stage's VF needs reduction.

6. **Add a barge-in and VAD stress scenario**: replay 200 ms of real caller audio (burst of 10 packets) to every bot simultaneously. Observe STT queue depth and LLM TTFT distribution. Confirm jitter buffer N_buf holds without overflow (P2).

**Strongest outcome**: step 3 (Gamma inter-arrival generator) produces p99 latency 2–3× higher than Poisson-based locust at the same ρ. This reproduces the production failure mode that M/M/1 Poisson load tests miss, making the load test a reliable pre-production gate.

---

## Composition

| Starting point | Natural next step |
|---------------|-------------------|
| P1 (Jackson budget partitioning) | Apply P6 (Kingman VF correction per stage) before finalizing caps; run R1 for the full worked sizing |
| P2 (jitter buffer sizing) | Verify the buffer latency contribution does not violate the STT budget from P1 |
| P3 (barge-in priority) | Monitor Class 2 (TTS) starvation if barge-in rate exceeds ρ₁ = 0.70 of the pipeline capacity |
| P4 (Erlang-C IVR sizing) | Apply Kingman CV²_a correction (P6 logic) for burst arrivals; separate human agent pool with its own Erlang-C instance |
| P5 (TTS start-token target) | Feed W_tts_start into P1 as the TTS stage's E[S] input |
| P6 (variable utterance length) | Use M/G/1 P-K result as the STT stage W_i in P1; use measured CV²_s for load test arrival generator in R3 |
| R1 (latency budget) | Feeds into R3 as the per-stage Wq_target values that the load test must reproduce |
| R2 (IVR capacity) | Depends on P4 for Erlang-C computation; use R3 to validate that the sized capacity holds under bursty arrivals |
| R3 (bursty load test) | Depends on R1 for the Kingman Wq target; uses P2 jitter scenario for audio-path stress |

**Anti-patterns as guards**: run A2 (jitter buffer check) before deploying on any new telephony carrier. Run A4 (CV² check) before publishing any capacity plan. Run A1 check (streaming vs. blocking LLM handoff) before any pipeline architecture review.

---

## Sources

- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- ITU-T E.501 (2005). "Estimation of traffic offered in the network." — Telephony arrival process modeling.
- ITU-T E.502 (1997). "Traffic intensity measurement principles." — Erlang measurement methodology.
- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11). — Jitter buffer sizing and bufferbloat in audio paths.
- [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md) — canonical primitive definitions, formulas, and worked examples for all models referenced here.
