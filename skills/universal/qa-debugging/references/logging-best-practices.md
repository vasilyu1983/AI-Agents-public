# Logging While Debugging

Structured-logging setup, SDKs, aggregation, retention, and cost belong to `qa-observability`:
`../../qa-observability/references/log-aggregation-patterns.md` and
`../../qa-observability/references/opentelemetry-best-practices.md`. This file covers only what
to add while chasing a bug.

## Add a Log Line Only to Answer a Question

- Before adding logging, write the question it answers ("is `user` null before or after the
  cache lookup?"). Logging "more" without a target question burns a second session without new
  evidence.
- Log at the **boundary where the invariant should hold** (input parse, cache return, before the
  external call), not downstream where the symptom appears.
- Include the values that distinguish the hypotheses (IDs, sizes, versions, branch taken,
  retry count, elapsed time), as structured fields, plus the correlation or trace ID.
- If the system has no correlation ID, thread a temporary one through the path under
  investigation rather than correlating by timestamp and endpoint.
- In production, scope added logging to the affected tenant or endpoint and give it an expiry
  (`production-debugging-patterns.md`).

## Redact Even in Throwaway Debug Logs

A debugging session under pressure is when a raw payload gets logged "just this once." Never log
credentials, tokens, session cookies, private keys, full card numbers, government IDs, health
data, or full request/response bodies. Redact by field allowlist (log only named fields), not by
blocklist; a blocklist misses the next new sensitive field. Treat log content as untrusted input
when an LLM summarizes it: logs can carry prompt-injection text from user-controlled fields.
