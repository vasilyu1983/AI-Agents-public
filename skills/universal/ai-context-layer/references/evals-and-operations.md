# Evals And Operations

## Evaluate Separate Planes

1. **Context quality**
- freshness
- ACL correctness
- missing fields
- stale or conflicting memory

2. **Retrieval quality**
- recall
- ranking quality
- citation support

3. **Answer or action quality**
- correctness
- usefulness
- execution success
- downstream lift

## Operational Metrics

- context bundle size
- retrieval hit rate
- citation coverage
- stale-context incidents
- tenant leakage incidents
- correction rate
- recommendation execution rate
- recommendation success rate

## Context Observability

Metrics are only useful if you can instrument and trace them. Use OpenTelemetry GenAI semantic conventions as the baseline:

- **Context assembly spans**: wrap each context assembly call in a trace span. Record attributes: `surface`, `actor_id`, `owner_scope`, `bundle_size_tokens`, `retrieval_count`, `memory_count`, `compression_applied`.
- **Source-level spans**: create child spans for each context source fetch (tool call, retrieval query, memory lookup, graph traversal). Record latency, result count, and cache hit/miss.
- **Distributed tracing**: when context assembly calls multiple services, propagate trace context so you can trace end-to-end from user request through assembly to final response.
- **Alerting**: set alerts on stale-context incidents (freshness > threshold), tenant-leakage events (owner_scope mismatch in response), and budget overruns (bundle_size > cap). These are P0 failures.
- **Dashboard basics**: track p50/p95 assembly latency, retrieval hit rate, citation coverage, and correction rate over time. Break down by surface.

Treat observability as a requirement, not a nice-to-have. Context assembly failures are silent — the model produces plausible but wrong answers. Instrumentation is the only way to catch them.

## Contradiction Detection Categories

A drift or consistency pass over `LearnedMemory` should classify conflicts into three concrete categories rather than treating "memory conflicts" as one bucket. Each category has a different resolution path and a different signal about what went wrong upstream.

- **Attribution conflicts** — wrong entity credited with a fact. Example: "Soren finished the auth migration" when the operational record shows Maya was assigned. Resolution: re-read the source episode; the wrong-entity extraction is almost always upstream.
- **Temporal errors** — wrong dates, tenures, durations. Example: "Kai has been here 2 years" when HR records show 3 years. Resolution: fix the `valid_from` on the underlying edge and re-derive any dependent facts.
- **Stale information** — facts superseded by more recent entries that were never invalidated. Example: "The sprint ends Friday" when the current sprint ends Thursday. Resolution: the older fact should have had its `valid_to` closed by the newer episode — the bug is in the extraction pipeline's supersession logic, not the fact itself.

Treat the category as a first-class label on the contradiction report, not as a free-text field. Dashboards can then show "this week: 12 attribution, 3 temporal, 47 stale" — each with a different owner for the fix.

<!-- Source: MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), pattern M5, cross-routed 2026-04-15 -->

## State-Maintenance Eval

Retrieval evals check that the right text comes back. They do not check that the memory stays correct while the world changes. Build a state-maintenance set across several domains (incidents, accounts, policies). Give each case a dated event history, a question, and an expected answer with its evidence ID. Score each category separately; one aggregate number hides which maintenance job is broken.

Running example (labelled, not real data): incident `INC-42`. Its owner changes from Alice to Bob at 09:10. Afterwards an index refresh at 09:11 still says Alice, the change event is redelivered, a summary says "Alice is handling it", a 09:00 snapshot is backfilled late, a chat topic still names Alice, the postmortem doc names Carol (a different object), and a task inside the incident is owned by Dan.

| Category | Case shape (history -> question) | Expected | Failure it catches |
|---|---|---|---|
| Update | owner Alice -> Bob at 09:10; "who owns INC-42?" | Bob, citing the 09:10 event | sibling rows instead of supersession (A3, F5) |
| Rename | service `pay-api` renamed `payments`; "who owns payments?" | same owner, same entity ID | entity keyed by display name; duplicate entity |
| Relationship change | INC-42 re-linked from service A to service B; "which incidents touch B?" | includes INC-42, excludes it for A after the change | edge not invalidated (A7) |
| Deletion / tombstone | source doc retracted; ask a question only it answered | abstain, or the successor answer | A40 non-cascading tombstone in an index, graph, or summary |
| Supersession | policy v2 supersedes v1 from a date; "current limit?" | v2 value, v2 section cited | v1 still live; `superseded_by` self-pointer |
| Point-in-time (as-of) | "who owned INC-42 at 09:05?" | Alice (`valid_from <= t < valid_to`) | only current state stored; as-of not computable |
| Duplicate event | the 09:10 change is delivered twice | one transition, one history row | non-idempotent reducer (A39) |
| Out-of-order backfill | the 09:00 snapshot (owner Alice) arrives after 09:10 | current owner stays Bob; 09:00 history is filled in | arrival-order apply (A39) |
| Stale secondary source | chat topic or cached summary still says Alice | Bob; the secondary is ignored or flagged | last-writer-wins across sources (A38) |
| Role confusion | incident owner Bob; task owner Dan; "who owns INC-42?" | Bob, not Dan | two kinds of owner collapsed into one attribute |
| Scope leakage | postmortem names Carol as doc owner, or entity B's addendum sets a different limit | answer stays on the asked object and scope | object or section scope not enforced (A43, P23) |

Case-writing rules:

- Every case has a hard negative that is lexically closer to the question than the right answer (the stale index row, the other owner). A case without a tempting wrong answer measures nothing.
- Score on an independent held-out set written by people who did not build the system. In one in-house KB, the builders' own set reported a much higher answer rate than the independent set.
- Record which retrieval and state path answered each case; a pass on a fallback path is not a pass (A41).
- An executable specification of the duplicate, out-of-order, stale-secondary, and as-of invariants ships in `builds/evals/suites/state_maintenance` (no credentials). Its reducer lives in the test, so it pins the rules, not your code: point the same cases at your write path before calling it a regression.

Evaluate per stage as well as end to end. Use the acceptance checks in [memory-responsibilities-audit](memory-responsibilities-audit.md): admission recall, extraction validity, rebuild idempotency, the maintenance categories above, retrieval with held-out and hard-negative sets, as-of and citation support after retrieval, and field validation at materialisation. Re-run the per-stage and state-maintenance sets on every model, prompt, or extraction-schema update, and compare against the last accepted run; the method (sampling, judge calibration, CIs) belongs to [ai-evals](../../ai-evals/SKILL.md).

## Failure Modes To Guard

- stale operational state in prompts
- overbroad memory replay
- wrong-tenant context
- graph edges with unknown provenance
- retrieval with no evidence contract
- action learning corrupting source-of-truth facts
- unclassified contradictions (see categories above) — piling them into one "memory conflict" bucket prevents the upstream fix
- state questions scored only by retrieval evals (no state-maintenance set)
