# Workflow Automation Platform State

> Version-sensitive content. Check each platform's release notes and pricing pages before making version-specific recommendations.

## Table of Contents

- [Temporal v1.x SDK Changes](#temporal-v1x-sdk-changes)
- [Trigger.dev v4 Cloud / Self-Hosted (v3 Fully Retired)](#triggerdev-v4-cloud--self-hosted-v3-fully-retired)
- [n8n 2.x Connector Breaking Changes](#n8n-2x-connector-breaking-changes)
- [Inngest](#inngest)
- [Hatchet](#hatchet)
- [Langflow and LangGraph](#langflow-and-langgraph)
- [Cross-Platform Decision Table](#cross-platform-decision-table)
- [Durable-Execution Selector](#durable-execution-selector)
- [iPaaS Buy-vs-Build](#ipaas-buy-vs-build)
- [Licensing](#licensing)
- [Anti-Patterns](#anti-patterns)

---

## Temporal v1.x SDK Changes

Read the installed Server and SDK versions, then check their compatibility and release notes before pinning or upgrading.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| TypeScript workflow sandbox | The TS workflow sandbox *replaces* `Math.random()`, `Date.now()` / `new Date()` (time of the last Workflow Task completion) and `setTimeout` with deterministic versions, so they are safe to call inside workflow code. The real determinism traps are Node built-ins and non-deterministic imports pulled into workflow code, and any I/O outside activities. |
| `proxyActivities` timeout required | In SDK v1.x, calling `proxyActivities` without an explicit `startToCloseTimeout` or `scheduleToCloseTimeout` throws at workflow instantiation time, not at activity invocation. Legacy 0.x code that omitted timeouts will fail immediately on upgrade. |
| Workflow versioning `patched` API | In the TypeScript SDK the patching primitives are `patched()` and `deprecatePatch()`. `getVersion()` is the Go/Java-style API and does not appear in the TS docs (verify before porting Go/Java examples). |
| Search attribute type registration | Custom search attributes must be registered with the Temporal server before workflows write to them. Check each attribute’s declared type before writing or filtering; do not rely on a later search to catch invalid values. |
| Worker Versioning | Worker Versioning (Worker Deployments) supports PINNED and AUTO_UPGRADE workflow behaviours; verify Server/SDK requirements and feature status in the [versioning guide](https://docs.temporal.io/worker-versioning). It changes task routing, so adopt it on an existing queue with a migration plan. Pair it with replay tests of recorded histories in CI (`Worker.runReplayHistories` in TS). |
| Nexus (cross-namespace calls) | Check Nexus Operations support and release status for the chosen Server/SDK before adoption. It uses a different error model than regular activity calls. Code that catches `ApplicationFailure` from activities does not automatically catch Nexus errors. |
| Cloud namespace egress pricing | Read [Temporal Cloud pricing](https://temporal.io/pricing) for billable actions, storage and other units; model the workflow’s timer/heartbeat traffic before deployment. |

---

## Trigger.dev v4 Cloud / Self-Hosted (v3 Fully Retired)

Trigger.dev v3 is retired (no new deploys, no running workloads). v4 builds on the v3 execution model rather than rewriting it (unlike the v2→v3 rewrite), but APIs and self-hosted infrastructure changed materially. Check the [migration guide](https://trigger.dev/docs/migrating-from-v3) and [self-host docs](https://trigger.dev/docs/self-hosting/overview) for supported releases before planning cutover.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| v3 SDK import path deprecated | `@trigger.dev/sdk/v3` still resolves in v4 but is deprecated in favor of `@trigger.dev/sdk`. Update imports during migration; the old path is slated for removal. |
| Queues must be predefined | v4 no longer allows creating a queue inline at trigger time (`{ queue: { name, concurrencyLimit } }`). Define queues with `queue({ name, concurrencyLimit })` and reference them by name. Code carried over from v3 that creates queues on demand will fail. |
| Self-hosted v4 collapses provider/coordinator/`trigger-worker` into one supervisor | The v3 split of provider, coordinator, and `trigger-worker` containers no longer applies. Resolve the supported release’s Docker Compose dependencies from the self-host guide rather than reusing a v3 compose file. |
| Migration can change static IPs | Cutting over from v3 to v4 can change Trigger.dev's outbound static IPs. Any IP allowlist (databases, third-party APIs) must be updated before or immediately after migration to avoid connectivity gaps. |
| Lifecycle hook signatures changed | `onSuccess`/`onFailure`/etc. moved from positional arguments to one destructurable object (`({ payload, ctx, task, output }) => {}`). Code ported directly from v3 hooks will fail to compile or silently receive `undefined`. |
| `wait.for` is duration-only | In v4, `wait.for()` / `wait.until()` wait for a duration or date. External events and approvals use Waitpoint tokens: `wait.createToken({ timeout, idempotencyKey })` then `wait.forToken(token.id)`, completed by `wait.completeToken` or an HTTP POST to the token URL. Set the token timeout explicitly against the approval window; read the installed SDK’s token docs for defaults. Using `setTimeout` as a workaround will not survive a worker restart. |

---

## n8n 2.x Connector Breaking Changes

Read [n8n release notes](https://docs.n8n.io/release-notes/) for the supported major and stable release channel; pin an exact supported version. Licence: see [Licensing](#licensing).

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| Task runners on by default (2.0) | Code node executions run in isolated task-runner processes by default in 2.0. Custom Code node logic that assumed same-process access to the main runtime may behave differently after upgrade. |
| Code node environment access blocked (2.0) | `process.env` is no longer readable from Code nodes by default in 2.0. Explicitly allow required variables or pass values via node parameters. |
| Database support (2.0) | MySQL/MariaDB storage was removed. SQLite is still supported (the legacy driver was removed; the pooled driver, tunable via `DB_SQLITE_POOL_SIZE`, is the only one), but Postgres remains the recommended production store. |
| Binary data mode default removed (2.0) | The in-memory default for `N8N_DEFAULT_BINARY_DATA_MODE` is removed. Set it explicitly to `filesystem` (regular mode) or `database` (queue mode). |
| `--tunnel` CLI flag removed (2.0) | Use ngrok, localtunnel, or Cloudflare Tunnel for local webhook development instead. |
| Migration Report tool | Run the built-in Migration Report before any 1.x → 2.0 upgrade to catch workflow- and instance-level issues ahead of time. |
| Legacy 1.x traps (only if not yet upgraded) | Google Sheets node parameter renames, HTTP Request pagination batch-size defaults, per-workflow webhook path namespacing, and `$json` vs `$item` expression semantics were all 1.x-era changes; confirm the target instance's major version before applying these fixes. |
| Credential encryption key | Keep `N8N_ENCRYPTION_KEY` identical across upgrades and hosts; losing it makes stored credentials unreadable. Whether a given major upgrade needs extra key-migration steps is unverified here — follow the official upgrade guide for the specific version jump. |
| Other 2.0 removals | ExecuteCommand and LocalFileTrigger nodes disabled by default, Start node removed, Activate replaced by Publish/Unpublish, Pyodide-based Python Code node removed — check the full list at docs.n8n.io/changelog/v20-breaking-changes before upgrading. |
| Community nodes | Unverified community nodes on internet-facing instances are a supply-chain risk; pin versions and review changelogs. |

---

## Inngest

Inngest is a durable function execution platform for TypeScript/JavaScript (plus other SDKs) with low-configuration setup. Check the installed JS SDK against its migration guide before porting code across major releases.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| Payload size by plan | Event payload limits differ by plan (the free tier is smallest), and step return data and total step data per run are also capped — check the current limits page. Externalize large blobs and pass a reference. |
| Billing units | Read [Inngest pricing](https://www.inngest.com/pricing) for execution accounting and which step types count; price the run/step shape and retention before quoting. |
| Parallel fan-out | Parallel steps are native: `await Promise.all([step.run(...), step.run(...)])`. Per-function step limits apply — check the current limits page. Use event-triggered child functions only when children need their own retries, concurrency keys or lifecycles. |
| v3 → v4 migration | v4 is a major release; do not copy v3-era adapter or type-inference advice without checking the v4 migration notes. |

---

## Hatchet

Hatchet is an open-source durable workflow engine for TypeScript, Python, and Go, self-hostable on Postgres. The engine/SDK generation and release tag are distinct: check the installed versions and support status, rather than inferring a 1.0 GA from a “v1 engine” label.

**Version-pinned gotchas *(verify current release before advising)***

| Trap | Detail |
|------|--------|
| v1 engine vs v0 tags | “v1” names an engine/SDK generation, not necessarily a 1.0 release tag. Check the installed engine and SDK versions against the current docs rather than assuming semver stability promises. |
| Postgres dependency is required | Hatchet requires Postgres as its backing store for both the task runtime and observability. There is no SQLite or in-memory mode. Local development requires a running Postgres instance or Docker. |
| Worker registration on startup | Hatchet workers register their workflow definitions at startup. Adding a new step to an existing workflow definition without a version bump causes in-flight runs of the old version to attempt to execute the new step definition. Use explicit workflow versioning. |
| `step.spawn` maturity | Verify current stability of the child-workflow-spawning API against the installed version; do not assume either way without checking the current docs. |
| Cloud offering access | Confirm [Hatchet Cloud](https://hatchet.run/) availability, access requirements and pricing before recommending managed hosting. |

---

## Langflow and LangGraph

LangGraph internals (checkpointers vs stores, `invoke` vs `stream`, interrupt/resume, library fragmentation) belong to the agents skill: see [../../ai-agents/references/framework-landscape.md](../../ai-agents/references/framework-landscape.md). This skill keeps only the handoff rule: prototype model-centric flows visually in Langflow; move to code (LangGraph with a durable checkpointer such as `PostgresSaver`, never the in-process `MemorySaver`, or a plain SDK call) once the flow needs tests, versioning, or SLOs.

| Trap | Detail |
|------|--------|
| Langflow managed hosting | Check the [deployment guide](https://docs.langflow.org/deployment-overview) for managed offerings and support status before recommending a host. |
| Langflow node compatibility | Langflow nodes that use older `langchain` abstractions do not always work with current `@langchain/core` equivalents; custom nodes written against older patterns may silently receive `None` outputs. |

---

## Cross-Platform Decision Table

| Scenario | Recommended | Notes |
|----------|-------------|-------|
| Long-running retried business workflow, TypeScript | Temporal (TypeScript SDK v1.x) | Mature, determinism guarantees, cloud or self-hosted |
| Serverless background jobs with retries, TypeScript/Next.js | Trigger.dev | Check the supported cloud/self-host major and component topology; never fall back to a retired major |
| Event-driven serverless functions, low ops overhead | Inngest | Check billing accounting against the expected run/step shape |
| SaaS integration glue, many connectors | n8n | Best connector breadth; pin node versions; fair-code Sustainable Use License for self-hosted Community Edition |
| Self-hosted durable workflows, Postgres already in stack | Hatchet | Verify installed engine/SDK versions and support status |
| Visual AI/LLM pipeline prototyping | Langflow (self-hosted) | Check managed offering status; require reviewed/tested flow exports for core product logic |
| Stateful agent execution with branching | LangGraph — see `ai-agents` | Use a durable checkpointer in prod |

---

## Durable-Execution Selector

Ask one discriminating question per row; verify status and pricing at the source before recommending.

| Shape | Options | Discriminating question |
|-------|---------|-------------------------|
| Library inside your app, state in your own Postgres | DBOS (MIT-licensed Transact libraries for Python, TypeScript, Go, Java and more) | Do you want durability without running a separate orchestration server? |
| Library + managed runtime on your host | Vercel Workflows (`'use workflow'` / `'use step'` directives on the open-source Workflow SDK) | Are you already on Vercel, and do its billing units, region model and release status fit? Check Vercel's current docs |
| Managed serverless durable functions | Inngest, Trigger.dev v4, Cloudflare Workflows | Compare each vendor’s current billing units, step/instance caps, maximum sleep duration and payload limits against the workflow’s shape; use the pricing links in data/sources.json |
| Server-based engine you run or buy | Temporal, Restate (lightweight runtime; Cloud, BYOC or self-host; Business Source License 1.1 that forbids offering it as a public platform service), Hatchet | Do you need multi-language SDKs, long histories, and replay tooling, and who operates the server? |

Plain fire-and-forget or short-retry jobs do not need any of these — use a job queue (see `software-backend`).

## iPaaS Buy-vs-Build

| Tool | Billing unit / hosting | Fit |
|------|------------------------|-----|
| Zapier | Tasks, counted per successful action step; triggers and built-in utility steps are generally not billed — check which steps count today. Cloud only | Non-engineers wiring SaaS apps; cost scales with action volume |
| Make | Credits per module action (some AI features cost more). Cloud only | Visual scenarios with heavier branching than Zapier; compare credits per expected run before choosing |
| Pipedream | Credits based on compute time and memory per workflow segment | Developer-friendly code steps with managed auth to many APIs |
| n8n | Self-host (Sustainable Use License) or n8n Cloud; see [Licensing](#licensing) | Connector breadth with self-hosting and code nodes |
| Activepieces | Core MIT (Expat); enterprise (`ee`) directories under a commercial licence | Permissively licensed self-hosted alternative to Zapier-style flows |
| Windmill | Open-source build AGPLv3 (clients and OpenFlow spec Apache-2.0); enterprise features proprietary | Script-first internal tools and workflows (Python/TS/Go/SQL) that engineers own |

Prices change often; compare on the billing unit against your expected action volume, then check the vendor pricing page.

## Licensing

n8n's self-hosted edition uses the fair-code **Sustainable Use License**: use and modify only for your own internal business purposes or non-commercial/personal use, and redistribute only free of charge for non-commercial purposes. That rules out reselling hosted multi-tenant access or white-labeling n8n as your product without a commercial agreement; `.ee.` files are under the n8n Enterprise License. Explainer: docs.n8n.io/n8n-community-license; licence text: github.com/n8n-io/n8n/blob/master/LICENSE.md. Fair-code, open-core, AGPL, BSL and MIT projects draw the commercial-use line in different places — verify each platform's current licence before recommending it as the backbone of a resold or customer-facing product.

---

## Anti-Patterns

**Using Temporal for simple job queues.** Temporal is designed for long-running, stateful, retried workflows with determinism requirements. Running a simple "send email after signup" background job through Temporal adds operational overhead (worker, namespace, history service) without benefit. Use a job queue such as BullMQ for fire-and-forget or short-retry tasks; Inngest belongs to the durable-function options above.

**Pinning Langflow for production AI pipelines.** Langflow is a visual prototyping tool. When a prompt chain stabilizes enough to require tests, versioning, and SLA monitoring, rewrite it in code using LangGraph or a direct LLM SDK call. Keeping production logic in Langflow nodes creates a review and testing dead zone.

**Relying on n8n connector retry semantics for non-idempotent actions.** n8n's built-in retry behavior does not distinguish idempotent from non-idempotent operations. An HTTP Request node retry on a billing or send-email action will double-bill or double-send. Model side-effect guards explicitly at the node level.

**Treating Trigger.dev major versions as interchangeable.** v2, v3, and v4 execution models are not drop-in compatible with each other. v3 is now retired — there is no fallback to run v3 workloads. Complete migration to v4 fully before decommissioning any prior version's infrastructure, and re-verify self-host topology since it changes materially between major versions.

**Reading Hatchet's "v1" as a 1.0 release.** The v1 engine is the default, but check its actual release tag. Weigh it as a viable Postgres-backed, self-hostable engine against Temporal's longer production track record for the most risk-averse workloads.
