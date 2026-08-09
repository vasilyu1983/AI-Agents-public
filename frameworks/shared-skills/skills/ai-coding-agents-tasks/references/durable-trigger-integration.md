# Durable Trigger Integration

Use this reference when an agent invocation must be **durable**: the orchestrator survives process crashes, retries with exactly-once semantics, supports multi-step compensation, and replays history on restart.

Substrate choice in May 2026: Temporal, Inngest, Restate, Trigger.dev, AWS Step Functions. All four implement durable execution; pick by ecosystem, not features.

Pair this reference with [`webhook-and-queue-triggers.md`](webhook-and-queue-triggers.md): use queue triggers when fire-and-forget is fine, use durable triggers when correctness across failures matters.

## Table of Contents

- [When You Need Durable Execution](#when-you-need-durable-execution)
- [Substrate Comparison (May 2026)](#substrate-comparison-may-2026)
- [The Agent-as-Activity Pattern](#the-agent-as-activity-pattern)
- [Temporal Integration](#temporal-integration)
- [Inngest Integration](#inngest-integration)
- [Restate Integration](#restate-integration)
- [AWS Step Functions Integration](#aws-step-functions-integration)
- [Replay Semantics](#replay-semantics)
- [Compensation and Sagas](#compensation-and-sagas)
- [Long-Running Agents](#long-running-agents)
- [Signals and Human-in-the-Loop](#signals-and-human-in-the-loop)
- [Observability](#observability)
- [Operational Checklist](#operational-checklist)
- [Cross-References](#cross-references)

## When You Need Durable Execution

Use durable triggers when **any** of the following hold:

- The agent's work has side effects that must not happen twice (charges, sends, deletes).
- The work is multi-step and must finish all steps or none.
- A single agent run can exceed 15 minutes (Lambda cap) or even hours.
- You need to send a signal to a running agent (human approval, cancel, update parameters).
- The work spans services or providers and needs compensation on failure.
- You need to replay a past run for audit, debugging, or recovery.

Use plain queue triggers from [`webhook-and-queue-triggers.md`](webhook-and-queue-triggers.md) when:

- The work is idempotent and short (<5 minutes).
- A failed run is acceptable to retry from scratch.
- No human-in-the-loop signal is needed.

## Substrate Comparison (May 2026)

| Substrate | Type | Hosted Option | Best For | Caution |
|---|---|---|---|---|
| **Temporal** | Workflow engine, polyglot SDKs | Temporal Cloud | Complex multi-step agent orchestration, long-running workflows | Self-hosting non-trivial; learning curve |
| **Inngest** | Event-driven durable functions | Inngest Cloud + self-host | Event-driven agent pipelines, fan-out, debouncing | Less expressive than Temporal for branching workflows |
| **Restate** | Distributed RPC + durable state | Restate Cloud + self-host | Agent-as-service with durable state, low operational overhead | Newer ecosystem, smaller community |
| **Trigger.dev** | Background jobs, TypeScript-first | Trigger.dev Cloud + self-host | Node/TS agent backends, dev ergonomics | Less mature multi-region story |
| **AWS Step Functions** | State-machine orchestration | AWS-hosted only | AWS-native stacks, integration with Bedrock | Verbose JSON; not portable |
| **DBOS** | Postgres-native durable execution | Self-host | Python/TS teams already on Postgres | Newer; fewer enterprise references |

If you don't know which to pick: Temporal for backend-heavy stacks, Inngest for product/event-driven stacks, Trigger.dev for full-TS shops.

## The Agent-as-Activity Pattern

The single most important pattern: **the agent invocation is an activity, not a workflow**.

```text
Workflow (durable, replay-safe, deterministic)
   ├─ activity: load_context()
   ├─ activity: invoke_agent(prompt, context)      ← the LLM call lives here
   ├─ activity: validate_output(result)
   ├─ activity: apply_side_effects(result)
   └─ activity: notify(result)
```

Why:

- Workflows must be deterministic for replay. LLM outputs are non-deterministic — they cannot be replayed.
- Activities are recorded once; their output becomes part of workflow history. On replay, the recorded output is returned without re-invoking the LLM.
- This is the only safe way to retry workflow steps without re-paying for the LLM call.

Rule of thumb: anything non-deterministic, slow, or expensive lives in an activity. The workflow is just glue.

## Temporal Integration

```python
# activities.py
from temporalio import activity
from anthropic import Anthropic

@activity.defn
async def invoke_agent(prompt: str, context: dict) -> dict:
    client = Anthropic()
    response = await client.messages.create(
        model=CURRENT_MODEL_ID,  # resolve from config; see ../../claude-api/SKILL.md for current model ids
        max_tokens=4096,
        system=context["system"],
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "text": response.content[0].text,
        "tokens": response.usage.input_tokens + response.usage.output_tokens,
        "model": response.model,
    }

@activity.defn
async def apply_side_effects(result: dict) -> str:
    # Idempotent side-effect with external transaction ID
    txn_id = await db.execute(
        "INSERT ... ON CONFLICT (idempotency_key) DO NOTHING RETURNING id",
        result["idempotency_key"],
    )
    return txn_id
```

```python
# workflow.py
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(self, request: dict) -> dict:
        context = await workflow.execute_activity(
            load_context, request,
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        agent_result = await workflow.execute_activity(
            invoke_agent, args=[request["prompt"], context],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(maximum_attempts=2, non_retryable_error_types=["BadRequest"]),
        )

        validation = await workflow.execute_activity(
            validate_output, agent_result,
            start_to_close_timeout=timedelta(minutes=1),
        )

        if not validation["passed"]:
            # Wait for human approval
            await workflow.wait_condition(lambda: self.human_approved is not None)
            if not self.human_approved:
                return {"status": "rejected", "result": agent_result}

        txn_id = await workflow.execute_activity(
            apply_side_effects, agent_result,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )

        return {"status": "ok", "txn_id": txn_id, "result": agent_result}

    @workflow.signal
    def approve(self, decision: bool):
        self.human_approved = decision

    human_approved: bool | None = None
```

Notes:

- `invoke_agent` activity timeout is generous (10 min) but bounded.
- Non-retryable error types prevent retrying on 400 / bad prompt errors.
- Signals (`approve`) implement human-in-the-loop without polling.

## Inngest Integration

```typescript
// inngest/functions.ts
import { inngest } from "./client";
import Anthropic from "@anthropic-ai/sdk";

export const agentFunction = inngest.createFunction(
  { id: "agent-handler", concurrency: 50 },
  { event: "agent/triggered" },
  async ({ event, step }) => {
    const context = await step.run("load-context", async () =>
      loadContext(event.data.requestId)
    );

    const agentResult = await step.run("invoke-agent", async () => {
      const client = new Anthropic();
      const response = await client.messages.create({
        model: CURRENT_MODEL_ID, // resolve from config; see ../../claude-api/SKILL.md for current model ids
        max_tokens: 4096,
        system: context.system,
        messages: [{ role: "user", content: event.data.prompt }],
      });
      return {
        text: response.content[0].text,
        tokens: response.usage.input_tokens + response.usage.output_tokens,
      };
    });

    const validation = await step.run("validate", async () =>
      validateOutput(agentResult)
    );

    if (!validation.passed) {
      // Wait for human approval via inngest event
      const approval = await step.waitForEvent("approval", {
        event: "agent/approved",
        timeout: "24h",
        match: "data.requestId",
      });
      if (!approval || !approval.data.decision) {
        return { status: "rejected" };
      }
    }

    const txnId = await step.run("apply-side-effects", async () =>
      applySideEffects(agentResult)
    );

    return { status: "ok", txnId };
  }
);
```

Inngest's `step.run` gives the same memoization guarantee as Temporal activities: each step's output is recorded and replayed on retry.

## Restate Integration

Restate's model: durable RPC handlers with built-in state. The agent becomes a virtual object.

```typescript
import * as restate from "@restatedev/restate-sdk";
import Anthropic from "@anthropic-ai/sdk";

const agentService = restate.service({
  name: "agent",
  handlers: {
    handle: async (ctx: restate.Context, request: AgentRequest) => {
      const context = await ctx.run("load-context", () => loadContext(request.id));

      const result = await ctx.run("invoke-agent", async () => {
        const client = new Anthropic();
        const response = await client.messages.create({ /* ... */ });
        return { text: response.content[0].text };
      });

      const validation = await ctx.run("validate", () => validate(result));

      if (!validation.passed) {
        const decision = await ctx.awakeable<boolean>();
        // Approval flow notifies and resolves the awakeable
        if (!(await decision.promise)) return { status: "rejected" };
      }

      return ctx.run("side-effect", () => applySideEffects(result));
    },
  },
});
```

Restate trade-off: simpler model than Temporal, less mature observability tooling.

## AWS Step Functions Integration

For AWS-native stacks, especially when the agent calls Bedrock:

```json
{
  "Comment": "Agent workflow with approval gate",
  "StartAt": "LoadContext",
  "States": {
    "LoadContext": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:::function:load-context",
      "Next": "InvokeAgent"
    },
    "InvokeAgent": {
      "Type": "Task",
      "Resource": "arn:aws:states:::bedrock:invokeModel",
      "Parameters": {
        "ModelId": "{current-bedrock-model-id}",
        "Body.$": "$.payload"
      },
      "Retry": [{
        "ErrorEquals": ["ThrottlingException"],
        "IntervalSeconds": 2, "MaxAttempts": 5, "BackoffRate": 2.0
      }],
      "Next": "Validate"
    },
    "Validate": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:::function:validate",
      "Next": "CheckApproval"
    },
    "CheckApproval": {
      "Type": "Choice",
      "Choices": [{
        "Variable": "$.validation.passed",
        "BooleanEquals": false,
        "Next": "WaitForApproval"
      }],
      "Default": "ApplySideEffects"
    },
    "WaitForApproval": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "send-approval-request",
        "Payload": {"taskToken.$": "$$.Task.Token", "request.$": "$"}
      },
      "Next": "ApplySideEffects"
    },
    "ApplySideEffects": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:::function:apply-side-effects",
      "End": true
    }
  }
}
```

`waitForTaskToken` is the canonical AWS way to do human-in-the-loop without polling.

## Replay Semantics

When a workflow replays:

- Activity results are returned from history without re-execution.
- `workflow.sleep`, `workflow.wait_condition`, signal handlers replay deterministically.
- Any non-deterministic code in the workflow (random, time, network) **outside** an activity will break replay.

The contract: workflow code = orchestration only. Anything that touches the outside world is in an activity.

Test replay determinism by running the workflow twice from the same history. Temporal and Inngest have explicit replay tests; use them in CI.

## Compensation and Sagas

Multi-step agent work often needs rollback on failure: the agent created a draft, applied a partial state change, then a downstream step failed. The compensation pattern handles this.

```python
@workflow.defn
class AgentSagaWorkflow:
    @workflow.run
    async def run(self, req: dict) -> dict:
        compensations = []
        try:
            draft = await workflow.execute_activity(create_draft, req, start_to_close_timeout=timedelta(minutes=2))
            compensations.append(("delete_draft", draft["id"]))

            preview = await workflow.execute_activity(generate_preview, draft, start_to_close_timeout=timedelta(minutes=5))
            compensations.append(("delete_preview", preview["id"]))

            published = await workflow.execute_activity(publish, preview, start_to_close_timeout=timedelta(minutes=2))
            return {"status": "ok", "published_id": published["id"]}
        except Exception as e:
            for activity_name, target_id in reversed(compensations):
                await workflow.execute_activity(activity_name, target_id, start_to_close_timeout=timedelta(minutes=1))
            raise
```

The compensation list is built as forward progress happens. On failure, compensations run in reverse order. Each compensation must be idempotent.

## Long-Running Agents

An agent run that exceeds an hour needs additional patterns:

- **Heartbeating**: the activity sends periodic heartbeats. Workflow can detect a hung activity.
- **Continue-as-new**: when a workflow's history grows large (>10k events in Temporal), continue-as-new keeps it healthy.
- **External cancellation**: a signal handler that sets a cancellation flag the activity checks periodically.

```python
@activity.defn
async def long_running_agent(prompt: str) -> dict:
    iters = 0
    while iters < MAX_ITERS:
        activity.heartbeat({"iter": iters})
        if activity.is_cancelled():
            return {"status": "cancelled", "iter": iters}
        result = await call_llm_once(prompt)
        if acceptance_met(result):
            return result
        iters += 1
    return {"status": "exhausted"}
```

Long-running agent activities should be considered a Shape C use case — see [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md).

## Signals and Human-in-the-Loop

Signals are the durable way to communicate with a running workflow:

- Approval / rejection
- Parameter updates ("increase budget", "change target")
- External cancellation
- Sub-task completion notifications

```python
@workflow.defn
class ApprovalGatedAgent:
    @workflow.run
    async def run(self, req: dict) -> dict:
        result = await workflow.execute_activity(invoke_agent, req, start_to_close_timeout=timedelta(minutes=10))
        await workflow.execute_activity(notify_human, result, start_to_close_timeout=timedelta(minutes=1))
        try:
            await workflow.wait_condition(lambda: self.decision is not None, timeout=timedelta(hours=24))
        except TimeoutError:
            return {"status": "timeout", "result": result}
        return {"status": self.decision, "result": result}

    @workflow.signal
    def approve(self, decision: str):
        self.decision = decision

    decision: str | None = None
```

The 24h timeout matters: an approval workflow that waits forever is a leaked workflow.

## Observability

Per-workflow signals (all substrates expose these natively):

- workflow started / completed / failed / timed out
- activity started / completed / failed / retrying
- signal received
- workflow continue-as-new

Wire these into your standard telemetry. Most substrates have native exporters to OpenTelemetry.

Key dashboards:

- workflow success rate by type
- activity p50 / p99 latency
- retry rate per activity
- in-flight workflows by age (long-running detector)
- approval wait time distribution

## Operational Checklist

Before deploying a durable agent workflow:

- [ ] Agent invocation isolated to a single activity (deterministic replay)
- [ ] Activity timeout matches realistic worst-case agent runtime + buffer
- [ ] Non-retryable error types defined (bad input, auth failure)
- [ ] Idempotency at the side-effect activity level (db unique constraint or external txn ID)
- [ ] Compensations defined for any irreversible action that has a successor
- [ ] Signal handlers documented with expected payload shape
- [ ] Wait conditions have explicit timeouts
- [ ] Long-running activities heartbeat at < timeout / 3
- [ ] Continue-as-new path tested if history grows large
- [ ] Replay determinism tested in CI
- [ ] Workflow worker autoscaling configured
- [ ] Activity worker pool sized for concurrent LLM calls

## Cross-References

- [`webhook-and-queue-triggers.md`](webhook-and-queue-triggers.md) — simpler triggers when durability is not required
- [`task-types-and-lifecycle.md`](task-types-and-lifecycle.md) — task model background
- [`claude-code-routines.md`](claude-code-routines.md) — Anthropic-hosted routine specifics
- [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) — Shape C loops as durable workflows
- [`../../ai-agents/references/24-7-operating-model.md`](../../ai-agents/references/24-7-operating-model.md) — SLOs and oncall
- [`../../software-workflow-automation/references/durable-execution.md`](../../software-workflow-automation/references/durable-execution.md) — substrate deep-dive
- [`../../ai-agents/references/guardrails-implementation.md`](../../ai-agents/references/guardrails-implementation.md) — approval gates and policy
- [`../../ai-mlops/references/incident-response-playbooks.md`](../../ai-mlops/references/incident-response-playbooks.md) — incident response
