---
name: software-workflow-automation
description: "Designs workflow automation with n8n, Langflow, Temporal, and Trigger.dev. Use when choosing automation platforms, durable runtimes, or custom code."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Workflow Automation

Use this skill to choose and design software workflow automation when the system needs triggers, integrations, routing, approvals, or AI-assisted steps across tools and services.

This skill covers:

- platform choice between n8n, Langflow, Huginn, Temporal, Trigger.dev, and custom code
- event-driven workflow design for internal tools and product operations
- side-effect control, retries, approvals, and observability
- AI-assisted workflow steps without turning every flow into a full agent system
- handoff rules for when visual automation should become code

## Quick Reference

| Need | Default path | Notes |
|------|--------------|-------|
| Broad integration workflow with many SaaS connectors | n8n | Strong default for business and product operations with many external systems. Fair-code Sustainable Use License — free for internal business use; check terms before reselling hosted access. |
| Visual AI or LLM pipeline prototyping | Langflow | Best fit when the workflow is model-centric and still evolving quickly. Open source, IBM-stewarded since the DataStax acquisition; the DataStax-hosted managed product was retired in early 2026 — self-host or re-check current managed options. |
| Self-hosted event watchers and automation agents | Huginn | Good fit for monitoring, alerts, and privacy-first self-hosted automations; upstream project has low recent activity — evaluate community forks before committing |
| Long-running, retried, or replay-sensitive business workflows | Temporal or Trigger.dev v4 | Use when durable execution, idempotency, and code review matter more than visual editing speed. Trigger.dev v3 was fully shut down 2026-07-01 — v4 is the only supported line. |
| Complex state, strong testing, or strict SLOs | Custom code | Move out of no-code/low-code once the workflow becomes core software |
| Tool protocol or reusable tool surface | `../agents-mcp/SKILL.md` | MCP is the integration contract layer, not the workflow designer itself |
| Platform state, version traps, and migration notes (verify before advising) | [references/platform-state.md](references/platform-state.md) | Temporal (Nexus GA), Trigger.dev v4, n8n 2.x, Inngest, Hatchet 1.0, LangGraph vs Langflow |
| Durable execution deep-dive: Temporal, Trigger.dev v4, n8n 2.x, LangGraph/Langflow | [references/durable-execution.md](references/durable-execution.md) | breaking changes and production traps |
| Replay DLQ messages from a JSON file | [scripts/replay_dlq.py](scripts/replay_dlq.py) | generic scaffold; adapt TARGET_COMMAND_TEMPLATE |

## Default Workflow

1. Define the trigger, inputs, outputs, and irreversible side effects.
2. Decide whether the workflow is mainly integration glue, model pipeline, durable business process, or core product logic.
3. Choose the simplest automation layer that can express the flow safely.
4. Add retries, dead-letter handling, idempotency boundaries, approval steps, and logging before rollout.
5. Set explicit handoff rules for when the workflow should move into code.

## ASCII Flow

```text
Workflow automation request
  -> Define trigger, inputs, outputs, owners, and side effects
  -> Classify glue, AI pipeline, durable process, or core product logic
  -> Choose visual tool, durable runtime, or custom code
  -> Add idempotency, retries, approvals, DLQ, and observability
  -> Define handoff point from automation to code
  -> Verify platform limits and run failure-path tests
```

## Platform Selection Rules

- Use **n8n** when connector breadth and operational workflows matter more than bespoke runtime behavior.
- Use **Langflow** when the main job is experimenting with AI chains, prompts, retrieval, or agent-shaped flows visually.
- Use **Huginn** when the need is self-hosted event monitoring, polling, alerts, and lightweight privacy-first automations. Note: verify upstream maintenance status before adopting; core repo activity has been low since 2023.
- Use **Temporal** or **Trigger.dev v4** when retries, long-running execution, replay safety, and code-reviewed workflow definitions are first-order concerns. (Trigger.dev v3 was fully shut down 2026-07-01 — v4 is the only supported line; new v3 deploys stopped working three months earlier, on 2026-04-01.)
- Use **custom code** when correctness, tests, version control, and maintainability matter more than visual editing speed.

## Platform Capability Matrix

| Platform | Best fit | Durable execution | Visual editor | Code review | Self-host |
|----------|----------|-------------------|--------------|-------------|-----------|
| n8n (2.x line; verify current minor — ships weekly) | SaaS integration glue, many connectors | No | Yes | Limited | Yes (Sustainable Use License — internal business use free) |
| Langflow | AI/LLM chain prototyping | No | Yes | Limited | Yes |
| Huginn | Self-hosted event monitoring, alerts | No | Yes | No | Only |
| Temporal | Long-running, retried business processes | Yes (replay-safe; Nexus cross-namespace calls GA on Python SDK) | No | Yes | Yes |
| Trigger.dev v4 | Code-first durable tasks, cloud or self-host | Yes | No | Yes | Yes |
| Custom code | Core product logic, strict SLOs, testable | Custom | No | Yes | Yes |

## Handoff Decision Table

| Signal | Action |
|--------|--------|
| Flow has conditional branches affecting billing, access control, or user-visible state | Move to code |
| Team cannot run unit tests against the flow | Move to code |
| Flow has strict latency SLO (p99 < 500ms) | Move to code |
| Flow triggers more than 3 external side effects in sequence | Audit idempotency first; then evaluate code |
| Flow is still a prototype with evolving branches | Stay in visual tool |
| Flow is pure integration glue between stable SaaS APIs | Stay in visual tool |

## Governance Rules

- Treat external credentials and webhooks as production dependencies.
- Model every side effect explicitly: create, update, send, delete, notify, bill.
- For any retried workflow, define the idempotency-key scope and which side effects are replay-safe before enabling retries.
- Require approvals for destructive or user-visible actions.
- Keep observability and retry policy outside the happy path design.
- Do not keep mission-critical product logic trapped inside an opaque visual flow if the team cannot review or test it properly.
- Check licensing before treating a platform as free to operate: n8n's Community Edition ships under the fair-code Sustainable Use License — free for internal business use, but restricted if the commercial value offered to a third party derives substantially from n8n itself (e.g., reselling hosted multi-tenant access). Verify current terms at n8n's license docs before recommending a resale or managed-hosting model.

## Known Traps

- Building the first working flow directly against production systems without replay-safe staging data and side-effect guards.
- Assuming connector retries are safe when downstream actions are non-idempotent, rate-limited, or billable.
- Letting human approvals live in chat or email instead of modeling them as explicit workflow states with timeout behavior.
- Treating webhook payload shape, auth, and delivery semantics as stable when SaaS vendors change them over time.
- Splitting one business process across several visual tools and scripts with no canonical owner, trace, or failure boundary.
- Leaving secrets, scopes, and credential rotation implicit because the platform stores credentials for you.
- Using visual automation for long-running or retried workflows with no durable state, replay semantics, or idempotency boundaries.

## Common Anti-Patterns

- **Keeping core product logic in visual automation.** Visual flows cannot be unit-tested, type-checked, or reviewed like code. Once a workflow has branching logic that affects billing, access control, or user-visible state, move it to code before it accrues a testing debt that makes future changes dangerous.
- **Turning every branching workflow into an agent problem.** LLM-based routing is non-deterministic and expensive. A workflow with known branching conditions should use a rules engine, a decision table, or plain conditional code — not an agent. Reserve agents for genuinely open-ended tasks.
- **Polling and scraping for system state.** Polling creates brittle coupling to internal data shapes and wastes request quota. Use webhooks, CDC, or event streams when the source system supports them. Polling is acceptable only when no event contract exists.
- **Using workflow nodes as domain-model substitutes.** Duplicating business rules across visual flows makes them invisible to the codebase. When a flow contains the same conditional logic as application code, it will diverge silently.
- **Treating observability as dashboard screenshots.** Dashboards do not survive incidents. Every run must have a structured run ID, start/end timestamps, step-level status, and a dead-letter record for failures. Screenshots are not replay controls.
- **Treating retried steps as safe by default.** Retry does not imply idempotency. Each side-effect step must prove it is replay-safe or carry an idempotency key before retries are enabled. See [references/platform-state.md](references/platform-state.md) for platform-specific retry behavior.

## Verification Checklist

Before a workflow is production-ready:

- [ ] Trigger, inputs, outputs, and all side effects (create / update / send / delete / bill) listed explicitly
- [ ] Every side-effect step proven idempotent or carrying an idempotency key before retries enabled
- [ ] Dead-letter queue defined; failure destination is not silent discard
- [ ] Approval steps modeled as explicit workflow states with timeout and escalation, not chat/email
- [ ] Credentials stored in the platform's encrypted secret store; rotation interval documented
- [ ] Platform version confirmed current: n8n 2.x line (verify exact minor — weekly releases), Temporal latest stable, Trigger.dev v4 (v3 fully shut down 2026-07-01, no longer usable)
- [ ] Webhook payload shape, auth scheme, and delivery semantics verified against current vendor docs
- [ ] Inbound webhooks verify a signature (with timestamp tolerance against replay) before trusting payload, acknowledge with 2xx immediately, and process asynchronously so handler latency cannot trigger vendor-side duplicate delivery
- [ ] Every run has structured run ID, step-level status, and a dead-letter record for failures
- [ ] Handoff condition to code is documented: if the flow needs unit tests, type-checking, or SLOs, migrate it

## When To Use This Skill

Use this skill when the user asks:

- "Should I use n8n or code for this workflow?"
- "Do I need Temporal or Trigger.dev, or is n8n enough?"
- "How do I design an automation pipeline across these tools?"
- "When should a Langflow prototype become real application code?"
- "What should I use for self-hosted automation and monitoring?"
- "How do I govern retries, approvals, and failures in an automation workflow?"

## Scenarios

Recipes keyed to common workflow automation design moments. Each lists the shortest path using patterns above.

### S1 — Temporal long-running workflow with deterministic activities

1. Define the workflow function as a pure deterministic orchestrator; no I/O, no random, no `time.Now()` inside.
2. Extract every side effect (HTTP call, DB write, email send) into a named `Activity`; activities own all I/O.
3. Set `ScheduleToCloseTimeout` on each activity to bound how long a retry loop may run for that step.
4. Use `workflow.Sleep` for scheduled delays inside the workflow; do not use OS sleep or tickers.
5. Add a `HeartbeatTimeout` on long-running activities so Temporal detects worker crashes and reschedules.
6. Test replay safety: run the workflow, kill the worker mid-flight, restart, and confirm idempotent completion.

### S2 — Trigger.dev v4 cloud-vs-self-host decision

1. List the hard requirements: data residency, VPC egress, SOC2 audit log, custom runtime dependencies.
2. If none apply, choose Trigger.dev Cloud (v4); it handles infra, scaling, and log retention out of the box.
3. If data residency or VPC egress is required, evaluate self-hosted v4 on Docker Compose (single VM) or Kubernetes for larger fleets.
4. Check the current v4 self-host docs before committing: the stack combines Postgres, Redis, ElectricSQL, ClickHouse, and MinIO (or your own object storage), with the provider and coordinator merged into one supervisor process — this replaced the separate `trigger-worker` container from v3. v3 self-host infrastructure is fully retired (v3 shut down 2026-07-01) and cannot be provisioned as a fallback.
5. Factor in operational cost: self-host requires owned patching, scaling, and backup; weigh against cloud pricing (verify current tiers — pricing changes independent of this skill).
6. Document the decision rationale in `docs/workflow/trigger-deployment-decision.md` for future team members, including any static-IP allowlist updates needed for outbound calls (Trigger.dev's infrastructure IPs can change on major-version migrations).

### S3 — n8n connector breaking-change recovery

1. Identify the broken credential or node version from the n8n execution log; pin the exact failed step.
2. Check the n8n changelog and the connector's upstream SaaS API changelog for the relevant version window.
3. If an API endpoint changed, update the HTTP Request node or credential with the new endpoint and auth scheme.
4. If a built-in node was removed or renamed, replace it with the HTTP Request node and replicate the behavior.
5. Run the fixed workflow against a staging environment or sandbox credentials before re-enabling production.
6. Add a periodic review reminder to the workflow description noting the connector version and last verified date.

### S4 — Approval-as-state durable gate

1. Model the approval as an explicit workflow state, not a chat message or email thread.
2. In Temporal: pause via `workflow.GetSignalChannel("approve")` or use a `Condition`; resume on signal receipt.
3. In Trigger.dev v4: use `wait.for({ event: "approval.granted" })` with an explicit `timeout`, or the v4 Waitpoints primitive (a token-based wait that a webhook or backend call completes) when multiple runs share one approval gate. Import from `@trigger.dev/sdk`, not the deprecated `@trigger.dev/sdk/v3` path.
4. On timeout, transition to a `pending_escalation` state and notify the escalation owner; do not silently expire.
5. Store the approval request ID and approver identity in the workflow state for audit purposes.
6. Test rejection and timeout paths explicitly; happy-path-only testing leaves silent failure modes in production.

### S5 — Visual-tool to code migration trigger

1. Identify the migration signal: the flow now has tests, conditional branches, local dev ergonomics needs, or strict SLOs.
2. Export or document the existing visual flow completely before touching any code.
3. Rewrite the flow as typed code (Temporal workflow, Trigger.dev task, or plain async service) with an identical I/O contract.
4. Run both the old visual flow and the new code side-by-side against the same trigger in staging; compare outputs.
5. Disable the visual flow only after the code version passes a full end-to-end verification cycle.
6. Archive the visual flow definition in version control as a migration artifact; do not delete it immediately.

## Navigation

**References**
- [references/platform-selection.md](references/platform-selection.md) - n8n vs Langflow vs Huginn vs custom-code decision rules
- [references/automation-governance.md](references/automation-governance.md) - retries, approvals, logging, and migration-to-code rules
- [references/platform-state.md](references/platform-state.md) - version-pinned platform state and migration traps
- [data/sources.json](data/sources.json) - workflow automation platform sources from the curated repo list

**Scripts**
- [scripts/check_workflow_idempotency.py](scripts/check_workflow_idempotency.py) - lint a workflow JSON for missing idempotency keys, retry policy, and DLQ gaps

**Related Skills**
- [../software-ai-integration/SKILL.md](../software-ai-integration/SKILL.md) - AI feature integration in products
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) - reusable tool and integration contracts
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) - platform operations, deployment, and runtime engineering
- [../software-backend/SKILL.md](../software-backend/SKILL.md) - code-first service implementation when automation becomes core application logic

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Start from `data/sources.json` for platform references.
- Verify current connector availability, deployment modes, and operational constraints before making platform-specific recommendations.
- If web access is unavailable, mark time-sensitive platform claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

