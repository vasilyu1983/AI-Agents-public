# Context-Layer Detailed Navigation and Operations

This reference contains detail moved out of the skill root. Load it after the root router selects the relevant workflow; do not preload it for unrelated work.

## Contents

- [Navigation](#navigation)
- [Fact-checking](#fact-checking)
- [Learnings loop](#learnings-loop)

## Navigation

### References

**Pattern selection and sweep (start here):**

- [references/memory-scenario-playbooks.md](memory-scenario-playbooks.md) — load first when the scenario is known: selector table plus one playbook per scenario (personal assistant, support/CRM, coding agent, multi-agent, regulated KB, multi-repo hub, incident/ops, procedural agent, voice, analytics hand-off, on-device) with R1–R7 defaults, upgrade trigger, acceptance tests, and links to P/A IDs
- [references/memory-responsibilities-audit.md](memory-responsibilities-audit.md) — load when building or auditing a KB or memory system end to end: workload-first step, then admission → encoding → persistence → maintenance → retrieval → post-retrieval → materialisation, each with default, deviation, acceptance checks, and covering P/A IDs
- [references/patterns-catalog.md](patterns-catalog.md) — P1–P25 named patterns (P14 sleep-time consolidation, P15 procedural memory / skill library, P16 multi-agent shared memory with isolation barriers, P17 schema-grounded write path, P18 ACE playbook loop, P19 harness engineering, P20 anchored iterative summarization, P21 evidence-linked observation, P22 current state linked to evidence, P23 section-level scope, P24 sensitivity filter before retrieval, P25 schema-first typed memory; P4 holds the canonical bitemporal vocabulary)
- [references/anti-patterns-catalog.md](anti-patterns-catalog.md) — A1–A49 with detection signals (A31 sleep-time pollution, A32 uncoordinated multi-agent writes, A33 GraphRAG misapplied to single-hop, A34 voice-tier memory miss, A35 context collapse, A36 victory-declaration bias, A37 eager compaction, A38 stale secondary override, A39 arrival-order events, A40 non-cascading tombstone, A41 silent retrieval fallback, A42 evidence-free edges, A43 addendum leak)
- [references/filesystem-as-memory.md](filesystem-as-memory.md) — Filesystem-as-memory thesis, transcript-style anti-pattern, when specialized memory still wins (Pokémon longitudinal case)
- [references/reference-architectures.md](reference-architectures.md) — RA1–RA13 composed recipes (incl. RA9 converged datastore, RA10 multi-repo KB, RA11 policy/compliance/ops-doc KB, RA12 multi-agent shared memory, RA13 voice-tier real-time memory)
- [references/architectures-by-organization.md](architectures-by-organization.md) — orthogonal deployment lens: 5 org tiers (solo → large enterprise) × 5 substrates (files → graph+vector) with ASCII + Mermaid diagrams, pros/cons, graduation triggers, and back-mapping to RA1–RA13
- [references/substrate-combinations.md](substrate-combinations.md) — answers "RAG or files? memory or vector?" with C1–C5 (combinations that produce real value) + X1–X5 (combinations that look clever but cost more than they return) + seam-contract checklist + cross-skill ownership map (`ai-context-layer` ↔ `ai-rag` ↔ `ai-vector-brain` ↔ `agents-memory` ↔ `software-database-design`)
- [references/context-hygiene.md](context-hygiene.md) — F1–F5 runtime failure modes, runtime verbs, context mutation economics, compaction verification
- [references/security-threat-model.md](security-threat-model.md) — T1–T7 threats + defenses
- [references/vendor-landscape.md](vendor-landscape.md) — decision matrix across frameworks, storage substrates, and managed services, plus an engine table by representation × output and native responsibilities. Living doc; see `as_of` header for last full review.
- [references/knowledge-compilation-and-wiki-pattern.md](knowledge-compilation-and-wiki-pattern.md) — P7 deep dive
- [references/operational-brain-pattern.md](operational-brain-pattern.md) — living markdown brain + structured identity/events/facts/graph projection pattern inspired by `garrytan/gbrain`
- [references/company-brain-assembly.md](company-brain-assembly.md) — org-scale composition recipe: 6 phases (collectors → DWH+vault → wiki ingestion → optional risk packs → MCP surface → agent), seam anti-patterns, phase-to-phase gates
- [references/multi-source-wiki-ingestion.md](multi-source-wiki-ingestion.md) — 6-stage ingestion pipeline (source → extractor → resolver → reconciler → page writer → run log) with supersede + provenance discipline
- [references/inspection-and-review-surfaces.md](inspection-and-review-surfaces.md) — review UI layer
- [references/just-in-time-context-loading.md](just-in-time-context-loading.md) — P12 runtime ref loading
- [references/managed-memory-boundaries.md](managed-memory-boundaries.md) — P13 hosted-memory boundaries
- [references/multimodal-context-assembly.md](multimodal-context-assembly.md) — typed multimodal assembly
- [references/git-anchored-ingestion.md](git-anchored-ingestion.md) — RA10 ingest rules: commit-as-time, diff-emit, content-hash idempotency, tombstone-on-delete
- [references/markdown-chunking-patterns.md](markdown-chunking-patterns.md) — heading-aware, code-block-atomic chunking with stable anchors
- [references/policy-and-compliance-docs.md](policy-and-compliance-docs.md) — RA11 deep dive: authority hierarchy, effective-time, polyglot ingest (Confluence/SharePoint/PDFs), cross-reference graph, citation contract
- [references/composition-with-related-skills.md](composition-with-related-skills.md) — how this skill composes with `dev-context-multi-repo`, `dev-context-engineering`, `dev-context-code-graph`, and `ai-rag` for the requirements-hub-shaped case
- [references/agent-memory-benchmarks.md](agent-memory-benchmarks.md) — external benchmarks (LongMemEval, LoCoMo, MemBench, GraphRAG-Bench, MemTier) with starter SLOs and what each gets wrong
- [references/conversational-surfaces-cross-platform.md](conversational-surfaces-cross-platform.md) — natural-conversation composition across iOS, Android, web browser, messaging bots (Telegram/Discord/WhatsApp/Slack), voice, and backend, with and without on-device models (Apple FM / Gemini Nano / Chrome `window.ai`); three generic domain scenarios at each platform
- [references/retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md) — entry-point decision rubric for RAG vs CAG/long-context vs fine-tune; RA-CB-1 composed context brain
- [references/cache-augmented-generation.md](cache-augmented-generation.md) — CAG pattern: preload corpus, KV-cache lifecycle (prime/reuse/invalidate), P-CAG-1…5 + 6 anti-patterns
- [references/long-context-first-architecture.md](long-context-first-architecture.md) — whole-corpus prompting at 1M+ tokens, lost-in-middle handling, prompt-cache economics, P-LC-1…5 + 6 anti-patterns
- [references/fine-tune-for-behavior-not-facts.md](fine-tune-for-behavior-not-facts.md) — "fine-tune for form not facts" rule, schema/persona/refusal training, P-FT-1…6 + 7 anti-patterns

**Layer deep dives:**

- [references/architecture-patterns.md](architecture-patterns.md)
- [references/entity-and-memory-models.md](entity-and-memory-models.md)
- [references/retrieval-and-grounding.md](retrieval-and-grounding.md)
- [references/graph-and-relationship-layer.md](graph-and-relationship-layer.md)
- [references/context-assembly.md](context-assembly.md)
- [references/mcp-context-delivery.md](mcp-context-delivery.md)
- [references/semantic-caching.md](semantic-caching.md)
- [references/tenant-isolation-patterns.md](tenant-isolation-patterns.md)
- [references/evals-and-operations.md](evals-and-operations.md)
- [references/example-assessments.md](example-assessments.md) — Patterns A–F
- [references/information-theory-applied.md](information-theory-applied.md) — Load only for defined distribution/compression questions: measured budget tradeoffs, heuristic relevance/diversity, drift and cache contracts; cosine and tokens are not MI.

### Agent Definitions

- [agents/openai.yaml](../agents/openai.yaml) — OpenAI-platform agent definition (display name, short description, default prompt) mirroring this skill for the OpenAI Agents / Responses runtime.
### Scripts

- [scripts/score_context_layer.py](../scripts/score_context_layer.py) — scorecard scorer (JSONL input)
- [scripts/check_sources.py](../scripts/check_sources.py) — sources.json validator

### Data Sources

- [data/sources.json](../data/sources.json)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Re-check provider capabilities, managed memory features, and hosted retrieval claims before user-facing recommendations.
- Prefer official platform docs, specs, and primary project docs over blog summaries.
- If browsing is unavailable, avoid strong ranking claims and state the uncertainty clearly.

## Learnings Loop

Consult relevant entries in `learnings.consolidated.md` when prior context-layer decisions or known pitfalls matter; inspect raw `learnings.md` history only when a repeated failure, provenance question, or unresolved decision needs it. Otherwise skip both files.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
