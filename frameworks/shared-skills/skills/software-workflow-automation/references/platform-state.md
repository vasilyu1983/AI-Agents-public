# Workflow Automation Platform State

> Last verified: 2026-07-11. Re-verify platform release notes before making version-specific recommendations.

## Table of Contents

- [Temporal v1.x SDK Changes](#temporal-v1x-sdk-changes)
- [Trigger.dev v4 Cloud / Self-Hosted (v3 Fully Retired)](#triggerdev-v4-cloud--self-hosted-v3-fully-retired)
- [n8n 2.x Connector Breaking Changes](#n8n-2x-connector-breaking-changes)
- [Inngest](#inngest)
- [Hatchet](#hatchet)
- [LangGraph vs Langflow Post-LangChain Restructuring](#langgraph-vs-langflow-post-langchain-restructuring)
- [Cross-Platform Decision Table](#cross-platform-decision-table)
- [Anti-Patterns](#anti-patterns)

---

## Temporal v1.x SDK Changes

Temporal reached 1.0 for its TypeScript and Go SDKs during 2024. The Python and Java SDKs followed in 2025. As of April 2026, the `.NET` SDK is at RC status.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| TypeScript SDK determinism lint | `@temporalio/worker` v1.x ships a built-in non-determinism linter that throws `DeterminismViolationError` for patterns that were silently wrong in 0.x — `Math.random()`, `Date.now()`, and `setTimeout` called directly inside workflow functions. These may surface as new failures on upgrade from 0.x. |
| `proxyActivities` timeout required | In SDK v1.x, calling `proxyActivities` without an explicit `startToCloseTimeout` or `scheduleToCloseTimeout` throws at workflow instantiation time, not at activity invocation. Legacy 0.x code that omitted timeouts will fail immediately on upgrade. |
| Workflow versioning `patched` API | `workflow.patched()` is the supported versioning primitive. The older `workflow.getVersion()` pattern still works but is deprecated in 1.x TypeScript SDK. Mixing both in the same codebase causes replay errors during migration. |
| Search attribute type registration | Custom search attributes must be registered with the Temporal server before workflows write to them. SDK v1 does not validate attribute types at write time — type mismatches only surface during search query execution. |
| Worker versioning (opt-in beta) | Worker versioning (`useVersioning: true`) is an opt-in beta feature in v1.3+. It changes how the task queue routes workflows and is not compatible with the default queue routing. Do not enable it on an existing queue without a migration plan. |
| Nexus (cross-namespace calls) | Temporal Nexus is now GA for the Python SDK (Go and Java support Nexus Services too) and in public preview for TypeScript and .NET. It uses a different error model than regular activity calls. Code that catches `ApplicationFailure` from activities does not automatically catch Nexus errors. Verify current SDK-specific GA status before recommending Nexus for a production cross-namespace call on a non-Python/Go/Java stack. |
| Cloud namespace egress pricing | Temporal Cloud bills on action count, not execution time. Workflows with tight heartbeat loops or high-frequency timer checks can accumulate actions faster than expected. Audit heartbeat cadence before deploying to Temporal Cloud. |

---

## Trigger.dev v4 Cloud / Self-Hosted (v3 Fully Retired)

Trigger.dev v3 stopped accepting new deploys 2026-04-01 and was fully shut down 2026-07-01. v4 builds on the v3 execution model rather than rewriting it (unlike the v2→v3 rewrite), so most v3→v4 migrations complete in minutes — but several APIs changed shape and self-hosted infrastructure changed materially.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| v3 SDK import path deprecated | `@trigger.dev/sdk/v3` still resolves in v4 but is deprecated in favor of `@trigger.dev/sdk`. Update imports during migration; the old path is slated for removal. |
| Queues must be predefined | v4 no longer allows creating a queue inline at trigger time (`{ queue: { name, concurrencyLimit } }`). Define queues with `queue({ name, concurrencyLimit })` and reference them by name. Code carried over from v3 that creates queues on demand will fail. |
| Self-hosted v4 collapses provider/coordinator/`trigger-worker` into one supervisor | The v3 split of provider, coordinator, and `trigger-worker` containers no longer applies. v4's reference Docker Compose stack bundles Postgres, Redis, ElectricSQL, ClickHouse, a container registry, and MinIO behind a single supervisor process — the v3 compose file will not work for v4. |
| Migration can change static IPs | Cutting over from v3 to v4 can change Trigger.dev's outbound static IPs. Any IP allowlist (databases, third-party APIs) must be updated before or immediately after migration to avoid connectivity gaps. |
| Lifecycle hook signatures changed | `onSuccess`/`onFailure`/etc. moved from positional arguments to one destructurable object (`({ payload, ctx, task, output }) => {}`). Code ported directly from v3 hooks will fail to compile or silently receive `undefined`. |
| `wait.for` inside tasks | `wait.for` suspends the task and resumes it after a delay or event. Unlike `setTimeout`, it survives process restarts. v4 adds the Waitpoints primitive (a completable token) for cases where one wait gates multiple runs. Using `setTimeout` as a workaround for wait behavior will not survive a worker restart on either version. |

---

## n8n 2.x Connector Breaking Changes

n8n reached 1.0 in late 2023, shipped 1.x minors through early 2026, then reached 2.0 in 2026 (verify the exact date and current minor — n8n ships new minors most weeks). Self-hosted Community Edition runs under the fair-code **Sustainable Use License**: free for internal business use, restricted once the commercial value offered to a third party derives substantially from n8n itself (e.g., multi-tenant resale, white-labeling). Verify current license text before recommending a resale or managed-hosting model.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| Task runners on by default (2.0) | Code node executions run in isolated task-runner processes by default in 2.0. Custom Code node logic that assumed same-process access to the main runtime may behave differently after upgrade. |
| Code node environment access blocked (2.0) | `process.env` is no longer readable from Code nodes by default in 2.0. Explicitly allow required variables or pass values via node parameters. |
| SQLite pooled driver default (2.0) | The `sqlite-pooled` driver becomes the default (tunable via `DB_SQLITE_POOL_SIZE`), but the self-hosted docs still recommend Postgres for any production instance — SQLite remains on a deprecation path and new queue-mode features require Postgres. |
| Binary data mode default removed (2.0) | The in-memory default for `N8N_DEFAULT_BINARY_DATA_MODE` is removed. Set it explicitly to `filesystem` (regular mode) or `database` (queue mode). |
| `--tunnel` CLI flag removed (2.0) | Use ngrok, localtunnel, or Cloudflare Tunnel for local webhook development instead. |
| Migration Report tool | Run the built-in Migration Report before any 1.x → 2.0 upgrade to catch workflow- and instance-level issues ahead of time. |
| Legacy 1.x traps (only if not yet upgraded) | Google Sheets node parameter renames, HTTP Request pagination batch-size defaults, per-workflow webhook path namespacing, and `$json` vs `$item` expression semantics were all 1.x-era changes; confirm the target instance's major version before applying these fixes. |
| Credential encryption key migration | Upgrading across a major version boundary (0.x→1.x, and check whether 1.x→2.x carries the same requirement) requires explicit migration of the credential encryption key. Skipping this step can make stored credentials unreadable silently. Follow the official migration guide step-by-step for the specific version jump. |

---

## Inngest

Inngest is a durable function execution platform targeting TypeScript/JavaScript applications with a focus on low-configuration setup.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| `inngest/next` vs `serve` export | Inngest v3 unified the framework adapters under `serve()`. Older `inngest/next` import paths still resolve but are deprecated. Using the deprecated path loses TypeScript type inference for middleware. |
| Step function result types | `step.run()` return types are inferred from the function body in v3. Implicit `any` returns from async steps typed in v2 become `unknown` in v3. Callers that spread step results without a type assertion will fail to compile. |
| Event payload size limit | Inngest enforces a 512 KB event payload limit in cloud mode. Self-hosted deployments inherit this limit from the configured event store. Workflows that pass large blobs as event data must externalize the data and pass a reference. |
| `step.sleep` and `step.waitForEvent` billing | Each `step.sleep` and `step.waitForEvent` consumes a step credit on Inngest Cloud. Workflows with many wait steps accumulate credits faster than single-step workflows. Exact plan limits and prices are volatile (recent public pricing showed a free tier around 50k runs/month and a paid tier starting near $75/month with usage-based overages) — treat any specific number as a starting estimate and confirm current pricing before quoting it to a customer. |
| Branch and fan-out pattern | Inngest does not natively support spawning parallel child runs from within a step and awaiting all of them. Fan-out requires triggering child functions via events and using `step.waitForEvent` per child, which is verbose and credit-intensive. |

---

## Hatchet

Hatchet is an open-source durable workflow engine targeting TypeScript, Python, and Go, self-hostable on Postgres. Hatchet reached 1.0 on 2026-04-24 — the pre-1.0 API-flux caveat that applied through 2025 no longer holds; re-verify the current minor before assuming behavior described here still applies unchanged.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| Post-1.0 stability, but confirm the exact minor | Hatchet 1.0 (GA 2026-04-24) commits to a more stable API surface than the earlier v0.x line. Multi-year stability guarantees should still be weighed against Temporal's longer production track record for the most risk-averse workloads, but pre-1.0 API-flux concerns no longer apply outright. |
| Postgres dependency is required | Hatchet requires Postgres as its backing store for both the task runtime and observability. There is no SQLite or in-memory mode. Local development requires a running Postgres instance or Docker. |
| Worker registration on startup | Hatchet workers register their workflow definitions at startup. Adding a new step to an existing workflow definition without a version bump causes in-flight runs of the old version to attempt to execute the new step definition. Use explicit workflow versioning. |
| `step.spawn` maturity | Verify current stability of the child-workflow-spawning API against the installed version — APIs that were experimental pre-1.0 may have since stabilized; do not assume either way without checking the current docs. |
| Cloud offering exists but is invite-only | Hatchet Cloud (managed) exists alongside the open-source self-hosted option, but access has been invite-only; self-hosting remains the default path for most teams and still requires managing the engine and Postgres. Confirm current cloud availability and pricing before recommending it — treat any specific price as volatile. |

---

## LangGraph vs Langflow Post-LangChain Restructuring

LangChain, Inc. restructured its product portfolio in 2024-2025, separating the open-source `langchain` library, the LangGraph execution engine, LangSmith (observability), and Langflow (which was acquired separately). LangGraph and LangChain both reached 1.0 in 2026.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| LangChain library fragmentation | The `langchain` npm/PyPI package is now a thin wrapper. Core abstractions moved to `@langchain/core`. Application code that imports directly from `langchain` often re-exports from `@langchain/core`, but some utility classes changed module paths. Audit imports after upgrading. |
| LangGraph is not LangChain | LangGraph (`@langchain/langgraph`) is a separate graph-based execution runtime, not a high-level wrapper around LangChain chains. Tutorials that conflate LangGraph nodes with LangChain runnables produce correct-looking but brittle code. |
| LangGraph state persistence | LangGraph checkpointing requires an explicit `Checkpointer` (e.g., `MemorySaver`, `SqliteSaver`/`AsyncSqliteSaver`, `PostgresSaver`). Without a checkpointer, graph execution does not resume on failure — it restarts. Docs examples often use `MemorySaver` (in-process, non-durable) for brevity. Production use requires `PostgresSaver` or an equivalent durable backend. |
| Langflow ownership changed twice | Langflow was acquired by DataStax in 2024; IBM's acquisition of DataStax subsequently closed. The DataStax-hosted managed Langflow product was deprecated 2026-03-09 and shut down 2026-04-09 — it is no longer a valid recommendation. The open-source repo (`langflow-ai/langflow`) continues to be maintained, now under IBM. Verify whether IBM offers a new managed option before assuming self-host is the only path. |
| Langflow node compatibility | Langflow nodes that use older `langchain` abstractions do not always work with current `@langchain/core` equivalents. Langflow built-in nodes are updated at their own cadence — custom nodes written against older patterns may silently receive `None` outputs. |
| LangGraph Studio dependency | LangGraph Studio (desktop app for visualizing graph state) requires LangSmith API access. It is not usable fully offline and is not appropriate for air-gapped or strict data-residency environments. |
| `invoke` vs `stream` semantics | LangGraph graph `.invoke()` runs synchronously and blocks until completion. `.stream()` yields intermediate state (a content-block-centric streaming API shipped as part of the 1.x line). Workflows that need partial progress updates must use `.stream()` — `.invoke()` returns only the final state. Using `.invoke()` for long agent loops causes apparent hangs with no feedback. |

---

## Cross-Platform Decision Table

| Scenario | Recommended | Notes |
|----------|-------------|-------|
| Long-running retried business workflow, TypeScript | Temporal (TypeScript SDK v1.x) | Mature, determinism guarantees, cloud or self-hosted |
| Serverless background jobs with retries, TypeScript/Next.js | Trigger.dev v4 | v4 cloud for managed; v4 self-hosted uses a single supervisor process over Docker Compose or Kubernetes (v3 is fully retired — no fallback) |
| Event-driven serverless functions, low ops overhead | Inngest | Simple setup; watch step credit costs (confirm current pricing tiers — volatile) |
| SaaS integration glue, many connectors | n8n (2.x line) | Best connector breadth; pin node versions; fair-code Sustainable Use License for self-hosted Community Edition |
| Self-hosted durable workflows, Postgres already in stack | Hatchet (1.0+) | Open source; reached 1.0 in 2026 — re-verify current minor and stability posture before assuming pre-1.0 caveats still apply |
| Visual AI/LLM pipeline prototyping | Langflow (self-hosted) | DataStax-hosted managed offering is retired; open source continues under IBM; not for core product |
| Stateful agent execution with branching | LangGraph (1.x) + LangSmith | Graph model fits agent loops; use PostgresSaver in prod |

---

## Anti-Patterns

**Using Temporal for simple job queues.** Temporal is designed for long-running, stateful, retried workflows with determinism requirements. Running a simple "send email after signup" background job through Temporal adds operational overhead (worker, namespace, history service) without benefit. Use a simple job queue (BullMQ, Inngest) for fire-and-forget or short-retry tasks.

**Pinning Langflow for production AI pipelines.** Langflow is a visual prototyping tool. When a prompt chain stabilizes enough to require tests, versioning, and SLA monitoring, rewrite it in code using LangGraph or a direct LLM SDK call. Keeping production logic in Langflow nodes creates a review and testing dead zone.

**Relying on n8n connector retry semantics for non-idempotent actions.** n8n's built-in retry behavior does not distinguish idempotent from non-idempotent operations. An HTTP Request node retry on a billing or send-email action will double-bill or double-send. Model side-effect guards explicitly at the node level.

**Treating Trigger.dev major versions as interchangeable.** v2, v3, and v4 execution models are not drop-in compatible with each other. v3 is now fully retired (shut down 2026-07-01) — there is no fallback to run v3 workloads. Complete migration to v4 fully before decommissioning any prior version's infrastructure, and re-verify self-host topology since it changes materially between major versions.

**Using LangGraph `MemorySaver` in production.** `MemorySaver` is an in-process, non-durable checkpointer. Process restarts lose all in-flight graph state. Production deployments require `PostgresSaver` or an equivalent durable backend.

**Assuming Hatchet is still pre-1.0.** Hatchet reached 1.0 on 2026-04-24. Treat it as a viable option for teams that want a Postgres-backed, self-hostable durable engine, while still weighing it against Temporal's longer production track record and broader ecosystem for the most risk-averse workloads. Re-verify current stability posture before applying older pre-1.0 caveats.
