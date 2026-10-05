---
name: queueing-theory-applied
description: "Queueing theory applied to voice bots and IVR: latency budget partitioning, jitter buffer sizing, Erlang-C call capacity, barge-in pre-emption, and TTS start delay. Theory lives in foundations-queueing-theory."
type: reference
---

# Queueing Theory Applied to Voice Bots

> **Gate before invoking:** check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first.

This file maps queueing decisions onto the voice pipeline (VAD → STT → LLM → TTS → codec) and IVR capacity. It does not restate the theory. Formulas and derivations live in the foundation:

| Model | Owner |
|-------|-------|
| Little's Law | [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) |
| M/M/c, Erlang-C | [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md) |
| M/G/1, Pollaczek-Khinchine | [04-mg1-pollaczek-khinchine.md](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) |
| Priority queues, residual service | [05-priority-queues.md](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md) |
| Jackson networks (serial stages) | [06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) |
| Kingman (G/G/1) | [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) |
| Bufferbloat | [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md) |
| Erlang-B (loss) | [10-loss-systems-erlang-b.md](../../foundations-queueing-theory/assets/templates/queueing-theory/10-loss-systems-erlang-b.md) |
| Fork-join | [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md) |
| Allen-Cunneen G/G/c, square-root staffing, overload, retries | [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md) |

**No portable utilization target.** Derive c and ρ from the SLO and the measured variability (square-root staffing, Allen-Cunneen). Do not apply a fixed "ρ ≤ 0.70" rule.

Thresholds below marked *illustrative* have no source. Replace them with your own measurements.

## Table of Contents

- [Patterns](#patterns): P1 budget partitioning · P2 jitter buffer · P3 barge-in pre-emption · P4 IVR capacity · P5 TTS start delay · P6 variable utterance length · P7 codec queue
- [Anti-Patterns](#anti-patterns): A1 blocking on full LLM response · A2 no jitter buffer · A3 fixed barge-in timeout · A4 ignoring per-stage CV²
- [Recipes](#recipes): R1 latency budget · R2 IVR sizing · R3 bursty load test
- [Sources](#sources)

---

## Patterns

### P1 — End-to-End Latency Budget Partitioning

**Decision:** how to split a turn-latency SLO across VAD, STT, LLM first token, TTS first chunk, and codec.

- Serial stages add in the **mean**: W_e2e = Σ W_i. Percentiles do not add. The sum of per-stage p90s usually overstates the end-to-end p90 for independent stages. Measure the end-to-end percentile directly.
- Parallel branches (for example echo cancellation next to VAD) contribute their max, not their sum. H_K for the max is exact only for iid exponential times with no waiting; otherwise simulate (see [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md)).
- Per call, each stage sees one turn at a time, so per-channel ρ is tiny and queueing wait is negligible (see R1). Queueing matters at **shared pools**: the LLM provider concurrency limit, a GPU TTS server, the SIP channel pool. Model those as M/M/c or G/G/c.
- The bottleneck is the shared pool with the highest ρ. After you scale it, re-solve: the next-highest-ρ pool becomes the bottleneck.
- Measure CV²_s per stage from the service-time sample (variance / mean²). Do not infer it from p99/p50.

### P2 — Jitter Buffer Sizing for Streaming STT

**Decision:** how deep the audio ingest buffer should be.

Heuristic (*illustrative*, not a queueing result): `N_buf = ceil(J / T_pkt) + 1`, where J is the jitter you want to absorb (for example p95 inter-arrival deviation) and T_pkt is the packet interval. The buffer adds N_buf × T_pkt of latency before STT. Subtract it from the STT budget.

| Link | J | T_pkt | N_buf | Added latency |
|------|---|-------|-------|---------------|
| Wireline, 20 ms G.711 | 18 ms | 20 ms | 2 | 40 ms |
| Mobile, high jitter | 60 ms | 20 ms | 4 | 80 ms (over half of a 150 ms STT budget) |

Rules:
- Never use N_buf = 0. One late packet then stalls the decoder or drops audio.
- Never use "safe large values". A deep buffer is bufferbloat in front of every later stage ([08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md)).
- Cap N_buf and apply packet loss concealment to packets that miss the deadline.
- Measure J per carrier and network type. Do not reuse one number.

### P3 — Barge-In and Pre-emption Priority Queues

**Decision:** how fast the bot stops talking when the user talks over it.

Two classes: class 1 = barge-in signal from VAD; class 2 = queued TTS audio chunks. Under **non-preemptive** priority, the barge-in waits for the in-flight chunk to finish. Mean residual = E[S] × (1 + CV²_s)/2; worst case = the longest chunk ([05-priority-queues.md](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md)).

Example: chunks of 100–300 ms, E[S] = 150 ms, CV²_s = 0.8 → mean residual 135 ms, worst case 300 ms. With 50 ms VAD detection, worst case ≈ 350 ms.

Rules:
- Make it pre-emptive where you can: flush the TTS buffer and cancel the LLM stream on barge-in instead of waiting for the chunk to end. Shorter chunks cut the non-preemptive worst case.
- Do not use a fixed barge-in timeout (see A3).
- Track barge-in success rate (bot audio stops within the target) as its own SLO. The 350 ms target and ≥ 95% rate are *illustrative*.
- For speech-to-speech APIs, pre-emption depends on the provider's server-side interrupt. Measure its latency.

### P4 — IVR Concurrent-Call Capacity via Erlang-C

**Decision:** how many concurrent call slots (SIP channels, bot workers) keep queue wait inside the SLO.

Model the IVR as M/M/c ([03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)). Offered load a = λ × E[S].

Example: λ = 0.5 calls/s, E[S] = 240 s → a = 120 Erlangs. SLO: mean wait ≤ 3 s.

| c | ρ | C(c, a) | Wq | P(wait > 3 s) |
|---|---|---------|----|---------------|
| 133 | 0.902 | 0.170 | 3.15 s | 14.5% |
| **134** | 0.896 | 0.144 | **2.48 s** | 12.1% |
| 140 | 0.857 | 0.048 | 0.58 s | 3.7% |
| 160 | 0.750 | 0.0003 | 0.002 s | 0.02% |

- Minimum c for Wq ≤ 3 s is **134** (square-root staffing: c ≈ a + β√a with β ≈ 1.28).
- If the SLO is "95% wait < 3 s" instead of a mean, you need c = 139. State which SLO you are sizing for.
- Erlang-C is a Poisson/exponential **baseline**, not a bound. For bursty arrivals or variable call length, use Allen-Cunneen: with CV²_a = 1 and CV²_s = 2, c = 135. For campaign spikes, simulate.
- Size the overflow threshold from the wait budget: queue limit ≈ c·μ × wait budget. At c = 134: 134/240 × 3 ≈ 1.7, so cap the queue at about 2 calls and overflow the rest to humans.
- Model a bot → human handoff as a separate pool with its own E[S] and c.
- Use Erlang-B ([10-loss-systems-erlang-b.md](../../foundations-queueing-theory/assets/templates/queueing-theory/10-loss-systems-erlang-b.md)) when the IVR rejects calls (busy signal) instead of queuing them.

### P5 — TTS Streaming Start Delay

**Decision:** how long before the first audio chunk, given the LLM token rate.

This is a fill time, not a queue: if TTS waits for N_min tokens, the first chunk starts after N_min / λ_tok.

| N_min | λ_tok | Start delay |
|-------|-------|-------------|
| 8 tokens | 80 tok/s | 100 ms |
| 8 tokens | 30 tok/s | 267 ms (2.7× longer, same model) |

Check each TTS provider's current docs for its N_min. Rules:
- Cut N_min (smaller first fragment) or raise λ_tok (faster model, lower provider load). Prompting for a short opener also helps.
- Track `tts_first_chunk_latency_ms` apart from `turn_latency_ms`. They diverge under LLM load.
- If the LLM fans out to parallel tool calls before speaking, the wait is a max over branches. Model it with [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md); do not apply a fixed correction factor.

### P6 — Turn-Taking Under Variable User Speech Length

**Decision:** how much a batch STT worker queues when utterance length varies a lot.

Use P-K ([04-mg1-pollaczek-khinchine.md](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md)). Example: E[S] = 4 s, CV²_s = 6, λ = 0.2/s → ρ = 0.8.

```
Wq = 0.8 × 4 × (1 + 6) / (2 × 0.2) = 56 s
M/M/1 at the same ρ: 16 s. CV²_s = 6 inflates the wait 3.5×.
```

Rules:
- Measure CV²_s from production VAD logs before sizing. It depends on the domain (yes/no menus are short and uniform; open-ended support is long-tailed). Any specific CV² range is *illustrative*.
- Streaming STT processes audio while the user speaks. That removes most of this queue.
- Better end-of-utterance detection shortens E[S] by trimming trailing silence.

### P7 — Telephony Codec Encode/Decode Queue Depth

**Decision:** how deep the codec queue may grow.

Codec service is near-deterministic. Queue depth comes from upstream bursts, not service variability. Latency added = frames queued × frame time. For 20 ms frames: 2 frames = 40 ms; 20 frames (a large default in some RTP stacks) = 400 ms, which eats most of a turn budget.

Rules:
- Cap the codec queue at a few frames (*illustrative*: 2–3) and conceal loss instead of buffering late frames.
- Alert when depth stays above the cap. It signals upstream network trouble.

---

## Anti-Patterns

### A1 — Blocking the Audio Path on Full LLM Response

**Symptom:** silence for the whole LLM completion, then the full reply at once.
**Cause:** the LLM → TTS handoff is a synchronous gate. The TTS start delay equals the full completion time instead of N_min / λ_tok (P5).
**Fix:** stream LLM output. Start TTS at the first sentence boundary.
**Detection:** `llm_response_complete_ms` and `tts_first_chunk_ms` are almost equal.

### A2 — No Jitter Buffer (Zero-Depth Audio Queue)

**Symptom:** transcript gaps and missed words on mobile or VoIP callers.
**Cause:** N_buf = 0. Each late packet is dropped or stalls the decoder.
**Fix:** size N_buf per P2 from measured jitter per carrier. Add loss concealment.
**Detection:** rising STT "audio gap" or "discontinuity" errors. Pick the alert threshold from your own baseline.

### A3 — Fixed Barge-In Timeout Ignoring Per-Stage Variance

**Symptom:** a fixed silence timeout (for example 500 ms) cuts users off on fast paths and fires before the first LLM token on slow paths.
**Cause:** a fixed timeout ignores that stage latencies vary. LLM first-token time in particular has high CV²_s under load.
**Fix:** set the timeout from measured per-stage latency distributions for each deployment and region. One heuristic (*illustrative*): `P95(vad) + P95(stt) + P75(llm_first_token)`. Calibrate the VAD stop-silence setting per deployment, not from a global default.
**Detection:** track both false positives (user finished, bot still silent) and false negatives (user still talking, bot starts).

### A4 — Ignoring Per-Stage CV² in the Latency Budget

**Symptom:** the load test passes with constant synthetic prompts; production p99 is much worse at the same volume.
**Cause:** synthetic prompts have low service-time variance. The budget used the M/M/1 or Erlang-C baseline with no variability term.
**Fix:** compute CV²_s per stage from production service-time samples. At shared pools, scale the baseline wait by (CV²_a + CV²_s)/2 (Kingman for one server, Allen-Cunneen for c servers). For tail percentiles, simulate or replay traces; do not multiply the mean by a fixed tail factor.
**Detection:** compare the measured wait at each shared pool with the variability-adjusted prediction. Compute CV² from the samples, not from p99/p50.

---

## Recipes

### R1 — Setting a 350 ms Voice Latency Budget with Per-Stage Caps

**Goal:** 350 ms p90 from end of user speech to first TTS audio byte.

1. **Remove fixed overhead.** Transport ≈ 40 ms (2 × 20 ms WebSocket, *illustrative*) → 310 ms for stages.
2. **Collect per-stage service times** (*illustrative* values):

   | Stage | E[S] | CV²_s |
   |-------|------|-------|
   | VAD end of speech | 50 ms | 0.4 |
   | STT final transcript | 80 ms | 0.6 |
   | LLM first token | 120 ms | 2.2 |
   | TTS first chunk | 40 ms | 0.5 |

3. **Check per-channel queueing.** At λ = 0.3 turns/s per channel, ρ is 0.012–0.036 and the Kingman wait is under 8 ms per stage. Mean W_e2e ≈ 300 ms + 40 ms = 340 ms. Queueing is not the problem per channel; service-time tails are.
4. **Budget with measured percentiles.** Set per-stage p90 alerts from production histograms. LLM first token, with the highest CV²_s, is the most likely to breach. Mitigate its variance first (warm pools, caching common intents, a lower-variance endpoint).
5. **Check the shared pools.** Size the LLM concurrency pool and any TTS server pool with P4 / Allen-Cunneen at peak concurrent calls. That is where queueing wait appears.
6. **Verify end to end.** Measure the e2e p90 directly. Do not sum per-stage p90s.

### R2 — Sizing IVR Concurrent-Call Capacity with Erlang-C

**Goal:** 95% of calls wait < 5 s to enter the IVR.

1. **Inputs:** peak λ = 120 calls/h = 0.0333/s; E[S] = 180 s → a = 6.0 Erlangs. Stability needs c > 6.
2. **Erlang-C baseline:**

   | c | ρ | C(c, a) | Wq | P(wait > 5 s) |
   |---|---|---------|----|---------------|
   | 8 | 0.750 | 0.357 | 32.1 s | 33.8% |
   | 9 | 0.667 | 0.196 | 11.8 s | 18.0% |
   | 10 | 0.600 | 0.101 | 4.6 s | 9.1% (fails) |
   | **11** | 0.545 | 0.049 | 1.8 s | **4.3% (passes)** |
   | 12 | 0.500 | 0.022 | 0.7 s | 1.9% |

   P(wait > t) = C(c, a) × exp(−(cμ − λ)t).
3. **Adjust for bursty arrivals.** If CV²_a = 2 and CV²_s = 1, Allen-Cunneen scales mean wait by 1.5: 2.7 s at c = 11, 1.0 s at c = 12. Allen-Cunneen gives means, not the tail. Simulate with the measured arrival process to choose between 11 and 12.
4. **Overflow.** Queue limit ≈ c·μ × wait budget = 11/180 × 5 ≈ 0.3 calls. At this size a queue barely forms; overflow any call that has waited past 5 s.
5. **Handoff pool.** If 20% escalate: λ_h = 0.0067/s, E[S_h] = 600 s → a_h = 4.0. For mean human wait < 30 s, c = 7 (Wq = 27 s; c = 6 gives 85 s).

### R3 — Reproducing Latency Under Bursty Arrivals in a Load Test

**Goal:** make the load test reproduce production waits at shared pools.

1. **Measure the arrival process.** From CDRs or pipeline logs compute CV²_a = Var(inter-arrival) / mean². Organic inbound tends to be near Poisson; campaign-driven traffic is burstier; metered webhooks can be smoother. Treat any specific range as *illustrative*.
2. **Predict the wait.** Single pool of one server: Kingman ([07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md)). c servers: Allen-Cunneen.
3. **Generate matching arrivals.** Gamma inter-arrivals with shape k = 1/CV²_a and scale θ = mean × CV²_a:
   ```python
   import numpy as np
   k = 1 / cv2_a
   theta = (1.0 / lambda_calls) * cv2_a
   iat = np.random.gamma(k, theta)
   ```
   Most load tools default to Poisson (CV²_a = 1).
4. **Validate.** Compare measured wait at each shared pool with the prediction. If measured wait is far below it, the generator is not bursty enough.
5. **Size from the SLO.** If the e2e percentile misses the SLO, find the pool whose variability term dominates (R1 step 5). Derive c from the SLO; do not aim for a fixed ρ.
6. **Audio-path stress.** Replay real caller audio bursts to all bots at once. Confirm the jitter buffer (P2) and codec queue (P7) stay within caps.

---

## Sources

- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- Gettys, J. & Nichols, K. (2011). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11).
- [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md) — definitions, formulas, and worked examples for every model used here.
