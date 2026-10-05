# Observability-Driven Testing

OpenTelemetry setup, instrumentation, SLO design and alerting are owned by [qa-observability](../../qa-observability/SKILL.md). This file keeps only the testing-strategy delta: asserting on traces, turning production traces into tests, and using traces to diagnose flakes.

## Contents

- [When to Use](#when-to-use)
- [Trace-Based Assertions](#trace-based-assertions)
- [Production Trace to Test Case](#production-trace-to-test-case)
- [Flaky-Test Diagnosis with Traces](#flaky-test-diagnosis-with-traces)
- [Gate Rules](#gate-rules)

## When to Use

- A distributed flow can pass every per-service test yet fail end to end (missing downstream call, wrong ordering, silent retry).
- An incident should become a regression test with the same span shape.
- A flaky test needs evidence of where the timing or dependency difference is.

## Trace-Based Assertions

Assert on the spans a request produces, not only on its HTTP response. The pattern is tool-agnostic: trigger a request with a known trace context, fetch the trace from the backend, then assert on span presence, attributes, status and duration.

```yaml
# Illustrative trace-test definition (Tracetest syntax; adapt to your tool)
specs:
  - selector: span[name="POST /orders"]
    assertions:
      - attr:http.response.status_code = 201
      - attr:tracetest.span.duration < 2000ms
  - selector: span[name="payment.process"]      # downstream call must happen
    assertions:
      - attr:payment.status = "success"
  - selector: span[name="db.orders.insert"]     # exactly one write, no retry storm
    assertions:
      - attr:db.operation = "INSERT"
```

Tracetest is one option; check its current maintenance and integration status before adopting it, because third-party integrations around it have changed. Any backend with a trace-query API can support the same pattern in a plain test.

What trace assertions add over response assertions:

- Missing or duplicated downstream calls (the response can be 201 while the payment span is absent).
- Retries hidden inside a client library.
- Per-hop latency budgets instead of a single end-to-end number.

## Production Trace to Test Case

```text
1. CAPTURE   export traces for the failing or critical journey
2. FILTER    keep traces that represent the journey, not noise
3. SANITIZE  remove PII; replace IDs with fixture IDs
4. CONVERT   request becomes the trigger; span tree becomes the assertions
5. VALIDATE  confirm the new test fails on the pre-fix build and passes after
```

Step 5 is the gate: a regression test that does not fail on the pre-fix build proves nothing.

## Flaky-Test Diagnosis with Traces

1. Propagate a trace ID from the test into the system under test, and print the trace link on failure.
2. Collect traces from a passing and a failing run of the same test on the same commit.
3. Diff the span names (missing or extra spans), then the per-span durations (timing), then error-status spans.
4. Classify the flake: order-dependent, async/timing, shared resource, or environment. A difference inside the system under test is a product or test defect; a difference only in infrastructure spans points at the environment.

## Gate Rules

- Critical journeys must emit the spans their trace tests assert on; a missing required span fails the deploy gate, it is not skipped.
- Retain traces for failed CI runs long enough to triage (at least the flake-triage SLA).
- Link every production-derived test to the incident or trace that produced it.

## Related References

- [operational-playbook.md](operational-playbook.md) — CI gates and merge-queue policy
- [production-testing-and-shift-right.md](production-testing-and-shift-right.md) — synthetic monitoring and production replay
- [qa-observability](../../qa-observability/SKILL.md) — OpenTelemetry, SLOs, alerting
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
