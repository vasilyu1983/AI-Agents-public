# Voice Quality Metrics

**Purpose**: Monitor and measure voice bot quality in production — MOS, WER, call completion, latency percentiles, dashboards, alerting, and A/B testing.

No theory. Measurement methods, thresholds, and implementation only.

---
## Table of Contents

- [MOS (Mean Opinion Score)](#mos-mean-opinion-score)
- [What MOS Measures](#what-mos-measures)
- [Programmatic MOS Estimation](#programmatic-mos-estimation)
- [MOS Thresholds](#mos-thresholds)
- [WER (Word Error Rate)](#wer-word-error-rate)
- [WER Calculation](#wer-calculation)
- [Automated WER Sampling](#automated-wer-sampling)
- [WER Thresholds by Use Case](#wer-thresholds-by-use-case)
- [Call Completion Metrics](#call-completion-metrics)
- [Core Call Metrics](#core-call-metrics)
- [Call Outcome Classification](#call-outcome-classification)
- [User Hang-Up Timing Analysis](#user-hang-up-timing-analysis)
- [Latency Percentile Tracking](#latency-percentile-tracking)
- [Per-Component Latency](#per-component-latency)
- [Total Turn Latency](#total-turn-latency)
- [User Satisfaction Proxies](#user-satisfaction-proxies)
- [Monitoring Dashboard Design](#monitoring-dashboard-design)
- [Dashboard Panels](#dashboard-panels)
- [Alerting Thresholds](#alerting-thresholds)
- [Quality Degradation Detection](#quality-degradation-detection)
- [Anomaly Detection Pattern](#anomaly-detection-pattern)
- [A/B Testing Voice Quality](#ab-testing-voice-quality)
- [What to A/B Test](#what-to-ab-test)
- [A/B Test Framework](#ab-test-framework)
- [Statistical Significance](#statistical-significance)
- [Related References](#related-references)

---

## MOS (Mean Opinion Score)

### What MOS Measures

MOS is the standard metric for perceived audio quality. It rates audio on a 1-5 scale based on how a human listener would judge it.

| Score | Quality | Meaning |
|-------|---------|---------|
| 5.0 | Excellent | Imperceptible degradation |
| 4.0 | Good | Perceptible but not annoying |
| 3.5 | Fair | Slightly annoying — minimum for voice bots |
| 3.0 | Poor | Annoying — users will complain |
| 2.0 | Bad | Very annoying — users will hang up |
| 1.0 | Terrible | Not usable |

**Target**: MOS >= 3.8 for production voice bots. >= 4.0 for premium/enterprise.

### Programmatic MOS Estimation

You cannot get true MOS without human listeners. These algorithms estimate it from audio signals:

| Algorithm | Type | Accuracy | Speed | License |
|-----------|------|----------|-------|---------|
| **PESQ** (ITU-T P.862) | Full-reference | High | Slow | Proprietary (free implementations exist) |
| **POLQA** (ITU-T P.863) | Full-reference | Highest | Slow | Commercial license |
| **ViSQOL** | Full-reference | High | Medium | Open source (Google) |
| **DNSMOS** | No-reference | Medium | Fast | Open source (Microsoft) |
| **Warp-Q** | No-reference | Medium | Fast | Open source |

> **Full-reference** algorithms compare degraded audio against the original (reference) signal. Useful for testing TTS output against source text.
>
> **No-reference** algorithms estimate quality from the degraded signal alone. Useful for monitoring live calls where you don't have a reference.

```python
"""Estimate MOS using DNSMOS (no-reference, works on live audio)."""
import numpy as np
import onnxruntime as ort

class DNSMOSEstimator:
    """Microsoft DNSMOS P.835 — estimates MOS from audio without reference."""

    def __init__(self, model_path: str = "dnsmos_p835.onnx"):
        self.session = ort.InferenceSession(model_path)

    def estimate(self, audio: np.ndarray, sample_rate: int = 16000) -> dict:
        """
        Estimate MOS scores from audio array.

        Returns:
            {"overall": float, "signal": float, "background": float}
        """
        # Normalize to float32
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0

        # Run inference
        input_name = self.session.get_inputs()[0].name
        result = self.session.run(None, {input_name: audio.reshape(1, -1)})

        return {
            "overall": float(result[0][0]),     # Overall MOS (1-5)
            "signal": float(result[1][0]),       # Signal quality
            "background": float(result[2][0]),   # Background noise
        }
```

### MOS Thresholds

| Scenario | Minimum MOS | Action if Below |
|----------|------------|-----------------|
| Production voice bot | 3.8 | Investigate TTS/codec/network |
| Enterprise SLA | 4.0 | Alert on-call |
| Development/staging | 3.5 | Acceptable for testing |
| Post-degradation event | 3.0 | Incident — route to human agent |

---

## WER (Word Error Rate)

### WER Calculation

WER measures STT accuracy: what percentage of words in the reference transcript were incorrectly recognized.

```
WER = (Substitutions + Insertions + Deletions) / Total Words in Reference
```

```python
import jiwer

def calculate_wer(reference: str, hypothesis: str) -> dict:
    """Calculate WER between reference and STT hypothesis."""
    transform = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.RemovePunctuation(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(),
    ])

    measures = jiwer.compute_measures(
        reference,
        hypothesis,
        truth_transform=transform,
        hypothesis_transform=transform,
    )

    return {
        "wer": measures["wer"],                      # 0.0 - 1.0
        "substitutions": measures["substitutions"],
        "insertions": measures["insertions"],
        "deletions": measures["deletions"],
        "total_words": len(reference.split()),
    }

# Example
result = calculate_wer(
    reference="I'd like to check my order status please",
    hypothesis="I'd like to check my order status please",
)
# result["wer"] == 0.0 (perfect)
```

### Automated WER Sampling

You cannot measure WER on every call (no reference transcript). Instead, sample periodically:

```python
import random

class WERSampler:
    """Sample calls for WER measurement against reference transcripts."""

    def __init__(self, sample_rate: float = 0.05):
        self.sample_rate = sample_rate  # 5% of calls
        self.test_phrases = [
            "I'd like to check my order status",
            "Can you transfer me to billing",
            "My account number is one two three four five six",
            "I want to cancel my subscription",
        ]

    def should_sample(self) -> bool:
        return random.random() < self.sample_rate

    async def run_wer_test(self, stt_client) -> float:
        """Play test phrases through STT and measure WER."""
        wer_scores = []
        for phrase in self.test_phrases:
            # Synthesize phrase → play through STT → compare
            hypothesis = await stt_client.transcribe(phrase)
            result = calculate_wer(phrase, hypothesis)
            wer_scores.append(result["wer"])
        return sum(wer_scores) / len(wer_scores)
```

### WER Thresholds by Use Case

| Use Case | Maximum WER | Notes |
|----------|------------|-------|
| General conversation | 15% | Acceptable for open-ended dialogue |
| Order numbers / IDs | 5% | Critical accuracy — consider DTMF fallback |
| Names / addresses | 10% | Spell-back confirmation recommended |
| Medical terms | 5% | Specialized vocabulary boosting required |
| Financial amounts | 3% | Require confirmation step |

---

## Call Completion Metrics

### Core Call Metrics

| Metric | Definition | Target | Measurement |
|--------|-----------|--------|-------------|
| **Call completion rate** | % of calls reaching natural end | > 85% | Call state machine → "ended" state |
| **Call drop rate** | % of calls lost to technical failure | < 2% | Transport disconnect without "goodbye" |
| **Average call duration** | Mean seconds per call | Use-case dependent | Transport timestamps |
| **Transfer rate** | % of calls transferred to human | < 25% (AI handling goal) | Transfer action triggers |
| **First-call resolution** | % of issues resolved without callback | > 70% | Post-call survey or repeat call analysis |
| **Repeat call rate (7d)** | % of callers calling back within 7 days | < 20% | Caller ID matching |

### Call Outcome Classification

```python
from enum import Enum

class CallOutcome(Enum):
    RESOLVED = "resolved"               # User issue handled successfully
    TRANSFERRED = "transferred"         # Transferred to human agent
    ABANDONED_EARLY = "abandoned_early" # User hung up in first 15 seconds
    ABANDONED_MID = "abandoned_mid"     # User hung up during conversation
    DROPPED = "dropped"                 # Technical failure (connection lost)
    TIMEOUT = "timeout"                 # Call exceeded max duration
    COMPLETED_NO_ISSUE = "no_issue"     # Informational call, no issue to resolve

def classify_call_outcome(
    call_duration_s: float,
    transfer_occurred: bool,
    user_said_goodbye: bool,
    connection_error: bool,
    resolution_confirmed: bool,
) -> CallOutcome:
    if connection_error:
        return CallOutcome.DROPPED
    if transfer_occurred:
        return CallOutcome.TRANSFERRED
    if call_duration_s < 15 and not user_said_goodbye:
        return CallOutcome.ABANDONED_EARLY
    if not user_said_goodbye and call_duration_s < 300:
        return CallOutcome.ABANDONED_MID
    if resolution_confirmed:
        return CallOutcome.RESOLVED
    return CallOutcome.COMPLETED_NO_ISSUE
```

### User Hang-Up Timing Analysis

Where users abandon reveals quality problems:

| Hang-Up Window | Likely Cause | Fix |
|---------------|-------------|-----|
| 0-5 seconds | No greeting / silence | Check TTS startup, greeting audio |
| 5-15 seconds | Bad initial interaction | Improve greeting, reduce first-response latency |
| 15-30 seconds | Irrelevant response / confusion | Improve intent detection, system prompt |
| 30-60 seconds | Stuck in loop / repetitive | Add loop detection, escalation triggers |
| 60+ seconds | Long wait / unresolved issue | Improve resolution rate, offer transfer earlier |

---

## Latency Percentile Tracking

### Per-Component Latency

Track these as histograms (not averages — averages hide tail latency):

| Metric | p50 Target | p90 Target | p99 Target |
|--------|-----------|-----------|-----------|
| STT latency | 50ms | 100ms | 200ms |
| LLM TTFB | 100ms | 200ms | 400ms |
| TTS first audio | 80ms | 150ms | 300ms |
| Total turn | 500ms | 700ms | 1200ms |

### Total Turn Latency

```python
import time
from collections import deque
import statistics

class LatencyTracker:
    """Track latency percentiles over a rolling window."""

    def __init__(self, window_size: int = 1000):
        self.window: deque[float] = deque(maxlen=window_size)

    def record(self, latency_ms: float):
        self.window.append(latency_ms)

    def percentile(self, p: float) -> float | None:
        if not self.window:
            return None
        sorted_vals = sorted(self.window)
        idx = int(len(sorted_vals) * p / 100)
        return sorted_vals[min(idx, len(sorted_vals) - 1)]

    def summary(self) -> dict:
        return {
            "p50": self.percentile(50),
            "p90": self.percentile(90),
            "p99": self.percentile(99),
            "count": len(self.window),
        }
```

---

## User Satisfaction Proxies

When you cannot ask users directly, these proxy metrics correlate with satisfaction:

| Proxy Metric | High Satisfaction Signal | Low Satisfaction Signal |
|-------------|------------------------|----------------------|
| **Call duration** | Matches expected range for use case | Too short (abandoned) or too long (struggling) |
| **Turn count** | Resolves in 3-6 turns | > 10 turns (stuck in loop) |
| **Repeat calls (7d)** | < 10% same caller | > 30% same caller |
| **Transfer rate** | < 15% | > 40% |
| **Barge-in rate** | < 20% of turns | > 50% (user frustrated, interrupting) |
| **DTMF fallback rate** | < 10% | > 30% (voice not working, falling back to keypad) |
| **Silence duration (user)** | < 3s average | > 5s (confused, waiting) |
| **"Repeat" requests** | < 5% of turns | > 15% ("Can you say that again?") |

---

## Monitoring Dashboard Design

### Dashboard Panels

**Panel 1: Real-Time Health**
- Active calls (gauge)
- Call starts/min (counter, 1-min window)
- Error rate (% of calls with errors)
- Current p90 total turn latency (gauge)

**Panel 2: Latency Breakdown**
- Total turn latency (p50/p90/p99 time series)
- STT latency (p50/p90 time series)
- LLM TTFB (p50/p90 time series)
- TTS first audio (p50/p90 time series)

**Panel 3: Quality**
- MOS estimate (rolling average, time series)
- WER sample results (scatter plot, last 24h)
- Call completion rate (%, time series)
- Transfer rate (%, time series)

**Panel 4: Call Outcomes**
- Outcome distribution (pie chart: resolved, transferred, abandoned, dropped)
- Abandon timing histogram
- Average call duration (time series)
- Repeat call rate (%, 7-day rolling)

### Alerting Thresholds

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Latency spike | p90 total turn > 1000ms for 5 min | Warning | Investigate LLM/STT/TTS provider |
| Latency critical | p90 total turn > 1500ms for 5 min | Critical | Failover to faster model/provider |
| Drop rate spike | Call drop rate > 5% for 10 min | Critical | Check transport/WebSocket health |
| WER degradation | WER > 20% on sampled calls | Warning | Check STT provider status |
| MOS drop | MOS estimate < 3.5 for 15 min | Warning | Check TTS/codec/network |
| Abandon spike | Early abandon > 30% for 10 min | Critical | Check greeting/TTS startup |
| Error rate | Pipeline errors > 5% for 5 min | Critical | Check all provider connections |

---

## Quality Degradation Detection

### Anomaly Detection Pattern

```python
from collections import deque
import statistics

class QualityAnomalyDetector:
    """Detect quality degradation using rolling z-score."""

    def __init__(self, window_size: int = 100, z_threshold: float = 2.5):
        self.window: deque[float] = deque(maxlen=window_size)
        self.z_threshold = z_threshold

    def check(self, value: float) -> dict:
        """Check if a new metric value is anomalous."""
        if len(self.window) < 20:
            self.window.append(value)
            return {"anomaly": False, "z_score": 0.0}

        mean = statistics.mean(self.window)
        stdev = statistics.stdev(self.window)

        if stdev == 0:
            z_score = 0.0
        else:
            z_score = (value - mean) / stdev

        self.window.append(value)

        return {
            "anomaly": abs(z_score) > self.z_threshold,
            "z_score": z_score,
            "direction": "high" if z_score > 0 else "low",
            "mean": mean,
            "stdev": stdev,
        }

# Usage
latency_detector = QualityAnomalyDetector(window_size=200, z_threshold=2.5)
wer_detector = QualityAnomalyDetector(window_size=50, z_threshold=2.0)

# On each turn
result = latency_detector.check(turn_latency_ms)
if result["anomaly"]:
    alert(f"Latency anomaly: {turn_latency_ms:.0f}ms (z={result['z_score']:.1f})")
```

---

## A/B Testing Voice Quality

### What to A/B Test

| Test | Variable | Metric | Sample Size |
|------|----------|--------|-------------|
| STT provider swap | Deepgram vs Azure | WER, latency | 500 calls per variant |
| TTS voice change | Voice A vs Voice B | Call duration, completion rate, MOS | 1000 calls per variant |
| TTS provider swap | ElevenLabs vs Cartesia | Latency, MOS, completion rate | 500 calls per variant |
| VAD sensitivity | threshold=0.4 vs 0.6 | Barge-in rate, false trigger rate | 500 calls per variant |
| LLM model | Sonnet vs Haiku | Resolution rate, turn count, latency | 1000 calls per variant |
| System prompt | Prompt A vs Prompt B | Resolution rate, transfer rate | 1000 calls per variant |

### A/B Test Framework

```python
import hashlib
import random

class VoiceABTest:
    """Assign calls to A/B test variants and track metrics."""

    def __init__(self, test_name: str, variants: list[str], weights: list[float] | None = None):
        self.test_name = test_name
        self.variants = variants
        self.weights = weights or [1.0 / len(variants)] * len(variants)

    def assign(self, call_id: str) -> str:
        """Deterministic assignment based on call_id."""
        hash_val = int(hashlib.md5(f"{self.test_name}:{call_id}".encode()).hexdigest(), 16)
        bucket = (hash_val % 1000) / 1000.0

        cumulative = 0.0
        for variant, weight in zip(self.variants, self.weights):
            cumulative += weight
            if bucket < cumulative:
                return variant
        return self.variants[-1]

# Usage
tts_test = VoiceABTest("tts_provider", ["elevenlabs", "cartesia"], [0.5, 0.5])
variant = tts_test.assign(call_id="call-12345")
# Use variant to select TTS provider for this call
```

### Statistical Significance

- Minimum sample: **500 calls per variant** for latency metrics, **1000 calls per variant** for conversion/completion metrics.
- Run duration: **At least 7 days** to capture day-of-week patterns.
- Significance level: **p < 0.05** with Welch's t-test for continuous metrics, chi-squared for proportions.
- Watch for: time-of-day effects, caller population differences, seasonal volume changes.

---

## End-to-End Voice Agent Evaluation: EVA-Bench

Component metrics (MOS, WER) measure parts; they miss whole-conversation failure. **EVA-Bench** (ServiceNow, arXiv 2605.13841, May 2026) is the first open framework that evaluates a voice agent end-to-end by running two AIs talking over a live WebSocket — no human listeners, no text replays. It scores two axes:

- **EVA-A (Accuracy):** task completion (deterministic) + faithfulness (LLM-as-judge) + speech fidelity (audio-LM-as-judge)
- **EVA-X (Experience):** conciseness + conversation progression + turn-taking timing

Headline finding (preprint, ~20 systems incl. S2S and cascading): no system exceeded 0.5 on **both** EVA-A and EVA-X at pass@1 — a measurable accuracy-vs-experience tradeoff that WER/MOS alone cannot surface.

**When to use:** when choosing between S2S and cascading architecture, or comparing TTS/LLM providers on experience quality, and call-completion rate + MOS are not discriminating. Evidence grade C (preprint; English/airline-domain dataset, framework itself is general). Resources: GitHub `ServiceNow/eva`, HF `ServiceNow-AI/eva` (built on Pipecat).

---

## Related References

- [latency-engineering.md](latency-engineering.md) — Latency optimization (one of the metrics tracked here)
- [voice-pipeline-architecture.md](voice-pipeline-architecture.md) — Pipeline stages being measured
- [voice-safety-compliance.md](voice-safety-compliance.md) — Compliance for call recording used in quality monitoring
- [ivr-design.md](ivr-design.md) — IVR analytics (menu path, abandonment)
