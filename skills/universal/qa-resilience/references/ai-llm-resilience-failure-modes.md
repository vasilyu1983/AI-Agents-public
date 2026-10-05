# AI/LLM Resilience Failure Modes

AI-backed features introduce failure modes that classic resilience testing misses. Standard chaos experiments (latency injection, pod kill, dependency outage) do not cover these patterns. Use this checklist when a service calls an LLM or AI model provider.

## Table of Contents

- [Failure-Mode Checklist](#failure-mode-checklist)
- [Telemetry Contract for AI Features](#telemetry-contract-for-ai-features)
- [Integration with the Resilience Gate](#integration-with-the-resilience-gate)
- [Related Resources](#related-resources)

## Failure-Mode Checklist

Each entry states: the failure mode, how it manifests, and how to test or detect it.

---

### 1. Provider Rate Limits and Quota Exhaustion

**How it manifests:** The provider returns 429 or a quota-exceeded error. The service may retry aggressively, amplifying the problem. Quota may be shared across tenants or environments without visibility.

**How to test:**
- Inject 429 responses from a stub or proxy in front of the provider call.
- Verify the client honors `Retry-After` or applies exponential backoff — not a tight retry loop.
- Verify the degraded-mode path activates (cached response, fallback content, or graceful error) rather than surfacing a raw error to the user.
- Assert that retry budget is bounded and does not cascade into downstream timeouts.

---

### 2. Latency Tail Blow-Ups

**How it manifests:** Median latency is acceptable; p99 is 10–30× the median. LLM inference latency is non-deterministic and can spike unpredictably. Without a tight deadline the service hangs.

**How to test:**
- Inject 5s, 15s, and 30s latency on the provider stub and verify the deadline fires within the configured budget.
- Assert that long-tail calls do not cascade into connection-pool exhaustion upstream.
- Verify the user receives a bounded response (timeout error or fallback), not an indefinitely pending request.
- Check that p99 is tracked in telemetry separately from p50, and that an alert fires when it breaches the SLO target.

---

### 3. Partial and Streamed Response Failures

**How it manifests:** The provider starts streaming tokens but drops the connection midway. The client may treat a partial response as a success (no error code), or hang waiting for the stream to close. The resulting output is semantically incomplete but not technically an error.

**How to test:**
- Inject premature stream termination at varying offsets (25%, 50%, 75% of expected tokens).
- Verify the client detects incomplete responses — either via a stop-sequence check, token-count heuristic, or explicit stream-done signal.
- Assert that a partial response is treated as a degraded outcome (fallback, retry, or error) not silently returned to the caller.
- Verify timeout applies to time-to-first-token and total stream duration independently.

---

### 4. Schema and Format Drift

**How it manifests:** The model is prompted to return structured output (JSON, XML, code). The model returns a plausible but non-conformant response — extra fields, missing fields, wrong type, or prose explanation instead of JSON. This is not an HTTP error; parsers silently fail or throw runtime exceptions.

**How to test:**
- Fuzz the prompt to produce off-format outputs from the stub (wrap real output in explanatory prose, omit required fields, nest fields incorrectly).
- Verify the parser has explicit schema validation and returns a structured error, not a panic or nil-pointer.
- Assert that format-violation events are counted in telemetry (not swallowed).
- Check that retrying on format failure does not enter an infinite loop; cap format-retry attempts separately from network retries.

---

### 5. Prompt-Injection-Induced Degradation

**How it manifests:** User-controlled input that flows into a prompt causes the model to deviate from its intended behavior — ignoring instructions, leaking system-prompt content, or producing off-topic output. This does not produce an HTTP error; the system silently degrades to incorrect behavior.

**How to test:**
- Inject canonical prompt-injection payloads into user-controlled fields and verify the output stays within the expected schema and behavior envelope.
- Assert that injected content does not appear verbatim in responses (system-prompt leak detection).
- Verify that output validation (schema check, content filter, output classifier) fires and routes to a fallback when the response is out-of-distribution.
- This is a resilience concern, not only a security concern: the service must degrade gracefully, not silently return adversarial output.

---

### 6. Silent Quality Regression

**How it manifests:** No error is thrown, latency is normal, format is valid — but the model output is subtly wrong. This happens after model version changes, prompt changes, or temperature/sampling-param changes. Classic resilience tests do not catch it because there is no signal to intercept.

**How to test:**
- Maintain a golden-set of inputs with expected output envelopes (not exact strings). Run the set in CI after any model/prompt/config change.
- Assert that a quality-classification signal (human eval sample, LLM-as-judge, or output-classifier score) is tracked in telemetry.
- Define an SLO on quality score, not only on availability and latency.
- Gate model or prompt updates on a golden-set pass and a quality-score burn-rate check — treat it like a release gate on a behavioral contract.

---

## Telemetry Contract for AI Features

Track these signals in addition to the standard resilience signals:

- provider error rate by error type (429, 503, timeout, stream-abort)
- time-to-first-token p50 / p99
- total generation latency p50 / p99
- format-validation failure rate
- quality-score distribution (if measurable)
- fallback activation rate per failure mode above

## Integration with the Resilience Gate

Add AI failure modes to the deterministic fault-injection stage (SKILL.md Testing Ladder — Deterministic first):

1. Stub the provider.
2. Inject each failure mode above.
3. Assert the correct control activates (deadline, backoff, fallback, format-error, quality-gate).
4. Only promote to chaos-stage experiments after all deterministic injections pass.

Do not rely on live provider calls for fault-injection tests. A stub that can return 429, injected latency, partial streams, and malformed JSON covers all six modes deterministically.

## Related Resources

- [resilience-checklists.md](resilience-checklists.md) — Failure Testing section
- [graceful-degradation.md](graceful-degradation.md) — Fallback and degraded-mode patterns
- [timeout-policies.md](timeout-policies.md) — Deadline budgets including streaming timeouts
- [retry-patterns.md](retry-patterns.md) — Retry budget and backoff for provider calls
- [slo-as-code.md](slo-as-code.md) — Declaring quality SLOs alongside availability SLOs
