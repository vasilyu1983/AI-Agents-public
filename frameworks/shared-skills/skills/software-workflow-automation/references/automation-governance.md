# Automation Governance

Use this file when the workflow has real operational or user-facing consequences.

## Minimum Controls

- retry policy
- timeout policy
- dead-letter or failure queue
- idempotency strategy
- replay-safe side-effect boundary
- approval step for destructive actions
- logs and execution history

## Migration-To-Code Rule

Move a platform workflow into code when:

- it carries core revenue or product logic
- debugging requires reading hidden node internals
- retries or long-running execution need durable state and explicit replay semantics
- versioning and review are inadequate
- test coverage is weaker than the business risk allows

## Credential and Secret Governance
- Store credentials only in the platform's secrets manager or external vault (e.g. AWS Secrets Manager, HashiCorp Vault).
- Rotate credentials on a schedule; automate rotation for credentials used by scheduled workflows.
- Scope OAuth tokens to minimum required permissions; reject broad-scope tokens without documented justification.
- Audit credential usage: log which workflows access which credentials; alert on first-use from a new workflow.

## Observability Minimum
- Every workflow execution must emit: run ID, trigger source, step-level start/end timestamps, step-level exit status.
- Failures must write a structured dead-letter record with: run ID, failed step ID, error type, payload hash, attempt count.
- Do not treat a visual flow's execution log UI as the observability layer — export structured logs to a queryable store.

## Webhook Reliability Pattern
- Delivery is at-least-once from essentially every provider, never exactly-once. Idempotency at the consumer is load-bearing, not optional — key on the provider's stable event ID (e.g. an `event.id`, `X-*-Webhook-Id`, or `webhook-id` header), not on payload content or arrival order.
- Verify the signature (HMAC or provider-specific scheme) before trusting any payload, and reject deliveries whose embedded timestamp is outside a tight tolerance window (commonly a few minutes) to block replay of captured requests.
- Acknowledge fast: return 2xx as soon as the payload is durably queued, then process asynchronously. If the handler's business logic finishes but the HTTP response arrives after the provider's timeout, the provider will retry and the logic can run twice — slow synchronous processing is a self-inflicted duplicate-delivery bug.
- Retry windows and attempt counts are provider-specific and change over time (illustratively, some retry over multiple days, others retry a fixed number of times over a few hours) — do not hardcode a specific vendor's retry schedule into workflow logic; read it from that vendor's current docs and design the DLQ to catch whatever exhausts.
- Use exponential backoff with jitter for any outbound retries you control, with an explicit maximum attempt count and a defined stop condition — unbounded retries against a downstream that is failing create a retry storm.

## Idempotency Design Notes
- Scope the idempotency key to the smallest unit that must not repeat (e.g., subscription-period + customer ID for a billing charge), not to the workflow run ID — a run ID changes on every retry attempt and cannot dedupe across attempts.
- Idempotency keys must be checked at the point of the external side effect (the payment gateway call, the send-email call), not only at the workflow's entry point — a workflow can be idempotent end-to-end yet still double-fire one internal step if that step's own guard is missing.

## Approval Workflow Requirements
- Every human approval gate must have an explicit timeout state with a defined escalation action (not silent expiry).
- Approval state must be durable (Temporal signal, Trigger.dev wait.for, persisted DB record) — not a chat message or email thread.
- Store the approver identity and timestamp in the workflow state for audit.
