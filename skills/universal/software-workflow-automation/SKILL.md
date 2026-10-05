---
name: software-workflow-automation
description: "Designs workflow automation with n8n, Zapier/Make, Temporal, Trigger.dev, Inngest. Use when choosing platforms, durable execution, or approval gates; not job queues or agents."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.5"
last_validated: 2026-09-26
---

# Workflow Automation

## Quick Reference

| Need | Default path | Notes |
|------|--------------|-------|
| Broad integration workflow with many SaaS connectors | n8n | Strong default for business and product operations with many external systems. Check the licence before reselling hosted access ([Licensing](references/platform-state.md#licensing)). |
| Visual AI or LLM pipeline prototyping | Langflow | Best fit when the workflow is model-centric and still evolving quickly. Open source; self-host it, or check which managed Langflow offerings exist before recommending a hosted one. |
| Self-hosted event watchers and automation agents | Huginn | Good fit for monitoring, alerts, and privacy-first self-hosted automations; check upstream release activity before committing |
| Long-running, retried, or replay-sensitive business workflows | Temporal or Trigger.dev | Use when durable execution, idempotency, and code review matter more than visual editing speed. |
| Complex state, strong testing, or strict SLOs | Custom code | Move out of no-code/low-code once the workflow becomes core software |
| Tool protocol or reusable tool surface | `../agents-mcp/SKILL.md` | MCP is the integration contract layer, not the workflow designer itself |
| Platform state, version traps, and migration notes (check vendor release notes before advising) | [references/platform-state.md](references/platform-state.md) | Temporal, Trigger.dev, n8n, Inngest, Hatchet, durable-execution selector, iPaaS buy-vs-build, licensing |
| Durable execution deep-dive: Temporal, Trigger.dev, n8n, Langflow | [references/durable-execution.md](references/durable-execution.md) | breaking changes and production traps |
| Replay DLQ messages from a JSON file | [scripts/replay_dlq.py](scripts/replay_dlq.py) | generic scaffold; adapt TARGET_COMMAND_TEMPLATE |

## Default Workflow

1. Define the trigger, inputs, outputs, and irreversible side effects.
2. Decide whether the workflow is mainly integration glue, model pipeline, durable business process, or core product logic.
3. Choose the simplest automation layer that can express the flow safely.
4. Add retries, dead-letter handling, idempotency boundaries, approval steps, and logging before rollout.
5. Set explicit handoff rules for when the workflow should move into code.

## Platform Capability Matrix

| Platform | Best fit | Durable execution | Visual editor | Code review | Self-host |
|----------|----------|-------------------|--------------|-------------|-----------|
| n8n | SaaS integration glue, many connectors | No | Yes | Limited | Yes (Sustainable Use License) |
| Langflow | AI/LLM chain prototyping | No | Yes | Limited | Yes |
| Huginn | Self-hosted event monitoring, alerts | No | Yes | No | Only |
| Temporal | Long-running, retried business processes | Yes (replay-safe) | No | Yes | Yes |
| Trigger.dev | Code-first durable tasks, cloud or self-host | Yes | No | Yes | Yes |
| Custom code | Core product logic, strict SLOs, testable | Custom | No | Yes | Yes |

## Handoff Decision Table

| Signal | Action |
|--------|--------|
| Flow has conditional branches affecting billing, access control, or user-visible state | Move to code |
| Team cannot run unit tests against the flow | Move to code |
| Flow cannot meet its measured latency SLO in the visual runtime | Move to code |
| Flow has several dependent external side effects | Audit idempotency first; then evaluate code |
| Flow is still a prototype with evolving branches | Stay in visual tool |
| Flow is pure integration glue between stable SaaS APIs | Stay in visual tool |

## Governance Rules

- Treat external credentials and webhooks as production dependencies.
- Model every side effect explicitly: create, update, send, delete, notify, bill.
- For any retried workflow, define the idempotency-key scope and which side effects are replay-safe before enabling retries.
- Default key scope: one key per item, taken from the upstream business ID (order, invoice, event ID), so a retry or a redelivered webhook sends the same key and two distinct items never share one. Never build the key from execution, run, attempt or time values, or from a batch-level accessor. When one item triggers several effects, scope the key by operation as well (`<business-id>:charge`, `<business-id>:email`).
- Require approvals for destructive or user-visible actions.
- Keep observability and retry policy outside the happy path design.
- Do not keep mission-critical product logic trapped inside an opaque visual flow if the team cannot review or test it properly.
- Check licensing before treating a platform as free to operate; see [Licensing](references/platform-state.md#licensing).

**When not to automate.** Leave a task manual (with a checklist) when it runs rarely, its inputs change shape each time, the failure cost of a wrong automated side effect exceeds the time saved, or no one will own the flow after launch. Automate the checklist first; automate the action once the steps have stayed stable for several runs.

**LLM steps in workflows.** Treat each model call as an untrusted step: validate structured output against a schema and route failures to a deterministic fallback or a human queue; cap tokens, cost, and retries per run; run evals before letting model output trigger side effects without approval; and version prompts and model IDs with the workflow version so in-flight runs stay reproducible. Keep deterministic routing in code, not in the model.

**Compensation contract.**

For each multi-step workflow, classify every completed side effect as reversible, compensatable, or irreversible. Define compensation order, retry behavior, and the terminal state when compensation also fails. Never claim transaction semantics across independent SaaS APIs; expose partial completion to operators with the run ID, completed steps, and safe next action.

## Known Traps

- Building the first working flow directly against production systems without replay-safe staging data and side-effect guards.
- Assuming connector retries are safe when downstream actions are non-idempotent, rate-limited, or billable.
- Letting human approvals live in chat or email instead of modeling them as explicit workflow states with timeout behavior.
- Treating webhook payload shape, auth, and delivery semantics as stable when SaaS vendors change them over time.
- Splitting one business process across several visual tools and scripts with no canonical owner, trace, or failure boundary.
- Leaving secrets, scopes, and credential rotation implicit because the platform stores credentials for you.
- Using visual automation for long-running or retried workflows with no durable state, replay semantics, or idempotency boundaries.

## Verification Checklist

Before a workflow is production-ready:

- [ ] Trigger, inputs, outputs, and all side effects (create / update / send / delete / bill) listed explicitly
- [ ] Every side-effect step proven idempotent or carrying an idempotency key before retries enabled
- [ ] For n8n app nodes with omitted `parameters.operation`, check the node type/version’s default in vendor documentation and review its side effects manually. The linter does not resolve app defaults; a clean report does not satisfy this gate
- [ ] Dead-letter queue defined; failure destination is not silent discard
- [ ] In n8n, each side-effect node's error output reaches durable storage, directly or through a transform node. Treat the workflow-level Error Workflow as an alerting backstop, not as the DLQ: it is built to notify, and how much of the failed item it carries has not been verified here. The linter below recognizes only a direct error-output connection to a DLQ node, so a transform in between is reported; confirm that chain by hand
- [ ] Approval steps modeled as explicit workflow states with timeout and escalation, not chat/email
- [ ] Credentials stored in the platform's encrypted secret store; rotation interval documented
- [ ] Platform versions pinned and checked against each vendor's release notes (n8n, Temporal SDKs, Trigger.dev) before relying on version-specific behavior; confirm the pinned major is still supported — a retired major can stop running workloads outright, not just stop getting fixes
- [ ] Webhook payload shape, auth scheme, and delivery semantics verified against current vendor docs
- [ ] Inbound webhooks verify a signature (with timestamp tolerance against replay) before trusting payload, acknowledge with 2xx after durably queuing the event, and process asynchronously so handler latency cannot trigger vendor-side duplicate delivery
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

1. Define the workflow function as a pure deterministic orchestrator with no I/O. In Go/Java avoid native random and wall-clock calls; the TypeScript workflow sandbox makes `Math.random` and `Date.now` deterministic, but I/O still belongs in activities.
2. Extract every side effect (HTTP call, DB write, email send) into a named `Activity`; activities own all I/O.
3. Set `ScheduleToCloseTimeout` on each activity to bound how long a retry loop may run for that step.
4. Use the SDK's durable timer (`workflow.Sleep` in Go, `sleep` in TypeScript) for delays inside the workflow; do not use OS sleep or tickers.
5. Add a `HeartbeatTimeout` on long-running activities so Temporal detects worker crashes and reschedules.
6. Test replay safety: run the workflow, kill the worker mid-flight, restart, and confirm idempotent completion.

### S2 — Trigger.dev cloud-vs-self-host decision

1. List the hard requirements: data residency, VPC egress, SOC2 audit log, custom runtime dependencies.
2. If none apply, choose Trigger.dev Cloud; it handles infra, scaling, and log retention out of the box.
3. If data residency or VPC egress is required, evaluate self-hosting on Docker Compose (single VM) or Kubernetes for larger fleets.
4. List the current self-host components from the vendor's self-host docs for the supported major, and cost each one (patching, scaling, backup); the component set changes between majors, and a retired major's stack cannot be provisioned as a fallback.
5. Factor in operational cost: self-host requires owned patching, scaling, and backup; weigh against cloud pricing from the vendor's current pricing page.
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
3. In a code-first runtime such as Trigger.dev: wait on the runtime's durable wait-for-external-completion primitive with an explicit timeout, and complete it from the approval UI or webhook. Do not use a duration sleep. Check the SDK docs for the current primitive, because it has changed across majors; [platform-state.md](references/platform-state.md#triggerdev-v4-cloud--self-hosted-v3-fully-retired) records the one known at its last check.
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
- [references/automation-governance.md](references/automation-governance.md) - retries, approvals, logging, and migration-to-code rules
- [references/platform-state.md](references/platform-state.md) - platform migration traps, selectors, and licensing
- [references/durable-execution.md](references/durable-execution.md) - durable-runtime patterns, migrations, and production traps
- [data/sources.json](data/sources.json) - workflow automation platform sources from the curated repo list

**Scripts**
- [scripts/check_workflow_idempotency.py](scripts/check_workflow_idempotency.py) - lint a workflow JSON for missing idempotency keys, retry policy, and DLQ gaps. Fixtures in [tests/fixtures/](tests/fixtures/), tests in [scripts/test_check_workflow_idempotency.py](scripts/test_check_workflow_idempotency.py).
  - Input: a generic `steps`/`tasks`/`nodes`/`activities`/`jobs` object, a bare step array (group steps with their own `steps` stay steps), or an array made only of workflows (each linted separately; issues carry `workflow`). Anything else exits 2, and so does input with no steps at all (`{"nodes": []}`, `[{"nodes": []}]`), so an empty export cannot pass a `--fail-on error` gate; one empty workflow inside a non-empty batch gets a `no-steps-found` warning.
  - Side effects: steps whose id, name or type has a word starting with a write keyword (`sendgrid`, `createOrder`; words split on non-alphanumerics and camelCase, with an exception list so words such as `postgres`, `posthog` and `postal` are not `post`), outbound POST/PUT/PATCH/DELETE (`method`, or `requestMethod` on the n8n HTTP Request node's typeVersion 1), and n8n app nodes whose `parameters.operation` contains a write verb (create, update, delete, upsert, insert, send, charge, post, capture, refund, add, remove, cancel, append, upload, reply, publish, push, incr/increment, decr/decrement, move, copy, share, invite, archive). Not linted: n8n trigger nodes (Webhook, Form, Manual, any `*Trigger`, whose `httpMethod` is inbound), Respond to Webhook, explicit reads (`select`, `get`, `getAll`, `find`, `aggregate`), and DLQ targets, meaning DLQ-named nodes reached only through an error output (a duplicate failure record is harmless; check the DLQ write's own durability by hand). Any other error-path node, such as a fallback charge, is linted like the normal path.
  - Database nodes (Postgres, MySQL, Microsoft SQL, MongoDB and similar) cannot carry a key. `upsert` and simple SQL conflict writes are static candidates, not proof: confirm a unique business key, stable input, and replay-safe triggers. SQL `SET` assignments accept only literals/binds or direct incoming values (`excluded.col`, a simple MERGE source alias, MySQL `VALUES(col)`). Increments, functions, complex expressions, comments and multiple statements get a warning rather than a clean result; complex safe SQL needs manual review. A query is read-only only when every statement is a SELECT or WITH … SELECT with no write keyword. Any other write, including a node with no `operation` (n8n omits default values from exports), gets the warning `non-idempotent-db-write`: use stable replacement values on a unique business key. App nodes relying on a default operation are not detected; resolve the default against the exported node type/version before accepting a clean report.
  - Keys: a generic key must be a non-empty string or a structured reference. Key headers are the listed key names, any header containing `idempotency` (e.g. `X-Idempotency-Key`), and `PayPal-Request-Id`; add other providers' key headers to `IDEMPOTENCY_HEADER_NAMES` in the script. In n8n exports a key must be a `={{ }}` expression reading the current item (`$json.id`, `$('Node').item.json.id`): a constant, `$execution`, `$workflow`, or a batch accessor (`.first()`, `.last()`, `.all()`, `$items(...)[n]`) alone is `static-idempotency-key` (use `.item` to follow the current item); item data mixed with `$execution`, `$runIndex`, `$now`, `$today`, `Date()`/`new Date()`, `Date.now()`, `DateTime.now/local/utc()`, `performance.now()`, `Math.random()`, `randomUUID()` or a batch accessor is `unstable-idempotency-key`. A passing key can still have the wrong business scope.
  - DLQ: generic steps declare a `dlq` field. In n8n exports only a connected `onError` error output whose direct target is a DLQ-named node counts; a `dlq` field on an n8n node does not, and disabled nodes, sticky notes and No-Op nodes never do. Either is static evidence, not proof of delivery.
  - Exit codes: 0 pass; 1 an issue at or above `--fail-on` (default `warning`, so any issue fails; `--fail-on error` reports warnings but passes them); 2 input error, including no steps to lint. `--strict` changes what is found (keyword steps need keys and DLQs, missing retries become errors); `--fail-on` only sets which severities fail, so `--strict --fail-on error` gates on strict-mode errors. `--format text` prints a readable report.
- [scripts/replay_dlq.py](scripts/replay_dlq.py) - dry-run dead-letter replay scaffold. `--execute` exits 2 until the echo template is configured; invalid messages, missing payloads, non-object filters and non-positive limits also exit 2. Offline regressions: [scripts/test_replay_dlq.py](scripts/test_replay_dlq.py).

**Related Skills**
- [../software-ai-integration/SKILL.md](../software-ai-integration/SKILL.md) - AI feature integration in products
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) - reusable tool and integration contracts
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) - platform operations, deployment, and runtime engineering
- [../software-backend/SKILL.md](../software-backend/SKILL.md) - code-first service implementation when automation becomes core application logic

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
