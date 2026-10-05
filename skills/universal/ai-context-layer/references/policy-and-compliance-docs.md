# Policy, Compliance & Operational Docs as Context

## Table of Contents

- [Why this is its own pattern](#why-this-is-its-own-pattern)
- [The PolicyChunk schema](#the-policychunk-schema)

Patterns specific to a corpus of policies, standards, procedures, runbooks,
regulator letters, and control-framework mappings used as context for AI
agents. Required reading for RA11. Composes with RA10 (when policies live in
git), RA4 (regulated overlay), and RA9 (when one substrate carries policy
chunks alongside operational documents).

This file owns the *what is different about this corpus*; the storage and
ingest mechanics are in `git-anchored-ingestion.md` (commit-anchored sources)
and the worked schema in `builds/cookbooks/git_repo_ingest.md`.

## Why this is its own pattern

A policy corpus is not the same as a doc corpus. The differences that drive
schema and retrieval choices:

1. **Authority is part of the answer.** A regulation outranks an internal
   guideline. A model that retrieves both at equal weight will quote the
   guideline against the regulation and produce a wrong answer with
   confident phrasing. Schema must encode `normative_weight`.
2. **Effective-time is not system-time.** A policy approved last week may
   become effective in three months. A regulator asking "what was your
   policy on date X" needs effective-time, not commit-time. Schema must
   carry `effective_from` / `effective_to` as separate axes from the RA10
   commit window.
3. **Citations are paragraph-precise.** "Per AML Policy v3.4" is unusable;
   "Per AML Policy v3.4 §4.2(a), effective 2026-02-01" is auditable.
   Anchors must survive re-ingestion and re-chunking; clause IDs are the
   canonical anchor, not heading slugs.
4. **Cross-references are first-class.** A policy implements a regulation
   and is operationalized by runbooks. The graph (P5) is more useful here
   than for any other corpus type.
5. **Sources are heterogeneous.** Git markdown, Confluence, SharePoint,
   regulator PDFs, exported Word, sometimes Notion. The chunk schema must
   absorb all of them without lossy normalization.
6. **Reviewer approval is non-negotiable.** A policy update going live with
   no editorial review is a regulatory finding waiting to happen. P7
   (knowledge compilation with mandatory review) is the table stakes.

## The PolicyChunk schema

Extends `LearnedMemory` / `knowledge_chunk`. Mongo and Postgres have
identical field shapes; pick the substrate per RA9/RA10 substrate decision.

```sql
CREATE TABLE policy_chunk (
  id                  uuid PRIMARY KEY,
  doc_id              text NOT NULL,                -- 'aml-policy', 'pci-dss-encryption-std'
  version             text NOT NULL,                -- 'v3.4', '2026-02-01', commit sha
  clause_id           text NOT NULL,                -- '§4.2.a', 'A.5.7', 'Art-18(3)'
  source_type         text NOT NULL,                -- regulation|policy|standard|procedure|runbook|guideline
  normative_weight    text NOT NULL,                -- same enum as source_type
  authority_owner     text NOT NULL,                -- 'legal', 'compliance', 'security', 'engineering'
  effective_from      date NOT NULL,
  effective_to        date,                         -- NULL = currently in force
  superseded_by       uuid REFERENCES policy_chunk(id),
  source_uri          text NOT NULL,                -- canonical URI: confluence://… , repo://… , file://…
  source_format       text NOT NULL,                -- 'markdown'|'docx'|'pdf'|'confluence'|'notion'
  content_hash        bytea NOT NULL,
  text                text NOT NULL,
  embedding           vector(1024),
  control_mappings    jsonb,                        -- [{"framework":"ISO27001","id":"A.5.7"}, …]
  next_review_at      date,
  reviewer_approved_at timestamptz,
  reviewer_id         text,
  owner_scope         jsonb NOT NULL,
  inserted_at         timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_policy_clause_version
  ON policy_chunk (doc_id, version, clause_id);

CREATE INDEX ix_policy_live
  ON policy_chunk (doc_id, clause_id)
  WHERE effective_to IS NULL;

CREATE INDEX ix_policy_review
  ON policy_chunk (next_review_at)
  WHERE next_review_at IS NOT NULL;

CREATE INDEX ix_policy_vec
  ON policy_chunk USING hnsw (embedding vector_cosine_ops);
```

`policy_registry` is a separate table: one row per `doc_id` carrying the
*current* version pointer, owner, next review date. Treat it as P1
(operational truth) — agents asking "what is the current version of Policy
X" hit this table, not the vector index. This blocks A28.

## Authority hierarchy (the table that earns its keep)

```
regulation     ← non-negotiable; conflict surfaces upward
   ▲ implemented_by
policy         ← internal binding; cites regulation
   ▲ implemented_by
standard       ← testable controls
   ▲ implemented_by
procedure      ← step-by-step, auditable
   ▲ operationalized_by
runbook        ← incident playbooks; cited but not normative
   ─────
guideline      ← informational; never cited as compliance evidence
```

Confidence rules:

- `regulation`: confidence 1.0, no decay. A regulation chunk is either
  current or superseded; no soft-decay.
- `policy`: confidence 0.95–1.0 when `reviewer_approved_at` is fresh; decays
  to 0.85 if past `next_review_at`.
- `standard` / `procedure`: confidence 0.9, decays to 0.7 if stale.
- `runbook`: confidence 0.8, decays faster — runbooks rot fastest.
- `guideline`: confidence 0.6, capped; cannot be cited as compliance
  evidence regardless of decay state.

A policy past `next_review_at` raises a "stale policy" flag in the bundle,
not a silent decay. Reviewers must see the staleness; agents must surface
it.

## The cross-reference graph

Build edges at ingest time. Substrate-agnostic edge shape:

```jsonl
{"src":{"type":"policy","id":"aml-policy","version":"v3.4"},"rel":"IMPLEMENTS","dst":{"type":"regulation","id":"MLR-2017","clause":"reg-28"}}
{"src":{"type":"standard","id":"encryption-std","version":"2026-01"},"rel":"IMPLEMENTS","dst":{"type":"policy","id":"infosec-policy","version":"v5.1"}}
{"src":{"type":"runbook","id":"rb-pay-014","version":"main@abc123"},"rel":"OPERATIONALIZES","dst":{"type":"procedure","id":"corp-onboarding","version":"v2.0"}}
{"src":{"type":"code","repo":"acme/payment-svc","path":"src/screening.cs","sha":"abc"},"rel":"ENFORCES","dst":{"type":"standard","id":"sanctions-screening-std","version":"v3"}}
{"src":{"type":"policy","id":"aml-policy","version":"v3.3"},"rel":"SUPERSEDED_BY","dst":{"type":"policy","id":"aml-policy","version":"v3.4"}}
{"src":{"type":"policy","id":"aml-policy","version":"v3.4"},"rel":"MAPS_TO","dst":{"type":"control","framework":"ISO27001","id":"A.5.7"}}
```

The `ENFORCES` edge is the bridge to RA10: code artifacts that implement
internal standards. This is what makes "is this code change compliant?"
answerable as a graph traversal: `(code change)` → `(standards it
ENFORCES)` → `(policies they IMPLEMENT)` → `(regulations cited)`.

Substrate options:

- **Neo4j + Graphiti** — bi-temporal graph (P4 semantics on edges),
  Cypher queries, mature visualization. Default when the graph drives the
  product.
- **Postgres `policy_edge` table** — simpler stack; recursive CTEs for
  traversal up to ~5 hops; works for ~10⁵ edges.
- **MongoDB `$graphLookup`** — works on the converged-stack RA9 substrate.
- **Apache AGE on Postgres** — Cypher-on-Postgres if you want graph
  ergonomics without a second cluster.
- **In-process JSON graph** — when the firm has <10⁴ nodes and <10⁵ edges,
  load into memory at process start; saves a database dependency.

## Polyglot ingest

Each source emits the same `PolicyChunk`. Keep adapters thin; the heavy
lifting is in the chunker.

| Source | Adapter pattern | Anchor | Notes |
|--------|-----------------|--------|-------|
| Git markdown | RA10 ingestion | heading slug or numbered clause | Default; commit-anchored. |
| Confluence | REST + page-version webhooks | heading + Confluence anchor | Track page-version-as-effective-date; archive page = `effective_to`. |
| SharePoint `.docx` | `python-docx` + heading walker | numbered heading | Track-changes preserved as superseded chunks. |
| Regulator PDF | `unstructured.io` + a layout-aware parser (Marker, Docling, LayoutLMv3-class) | clause number | Preserve numbered clauses, footnotes, schedules. |
| Regulator PDF (AWS path — standardized/high-volume) | AWS Textract (S3 event → Textract → JSON → clause-tree extractor) | clause number | Handles handwriting, forms, and tables; pair with Lambda for S3-triggered pipelines. Output structured JSON feeds the same clause-tree extractor as unstructured.io. Preferred for standardized, high-volume document types (e.g., a single recurring form at scale). |
| Regulator PDF (AWS path — mixed/variable docs) | **AWS Bedrock Data Automation (BDA)** — FM-based classify + extract pipeline; Textract is the OCR layer inside BDA's "Bedrock Pipeline" mode | clause number | AWS-recommended front door for mixed or variable document sets (multi-type corpora, unstructured layouts). BDA classifies document type, extracts fields using foundation models, then outputs structured JSON feeding the clause-tree extractor. Check current pricing. Use standalone Textract only for standardized high-volume docs where BDA overhead is unnecessary. |
| Notion | Notion API | block ID | Block IDs survive renames; richer than headings. |
| Email/letter | Manual upload + register row | letter-section ID | Regulator letters are first-class evidence. |

For each adapter, the rule is:

1. Extract structure (clause tree) before extracting text.
2. Promote frontmatter / page-properties to columns
   (`as_of`, `last_verified`, `owner`, `next_review_at`).
3. Normalize the anchor: prefer the *human-readable clause ID* the
   regulator or author would cite, not an internal slug.
4. Preserve the `source_uri` so reviewers can click through to the
   original.

## Compliance retrieval pattern (the assembly path)

```text
question
  → entity recognition
      (regulation IDs, policy names, control IDs, transaction IDs)
  → policy_registry lookup
      (resolve "AML Policy" → current doc_id+version, or as_of version)
  → graph traversal
      (follow IMPLEMENTS / OPERATIONALIZES / MAPS_TO edges
       to bound the relevant chunk set)
  → P8 retrieval over the bounded set
      (re-rank by normative_weight; regulation > policy > standard …)
  → ContextBundle:
      - citations[] : {doc_id, version, clause_id, effective_at,
                       normative_weight, source_uri}
      - conflicts[] : if multiple weights disagree
      - related_runbooks[]
      - related_code_artifacts[]   # RA10 join via ENFORCES edges
      - staleness_warnings[]       # any chunk past next_review_at
```

Two non-obvious moves:

- **Bound retrieval by graph traversal first.** Pure cosine search over the
  whole policy corpus returns "policies that talk like the question";
  graph-bounded retrieval returns "policies that *apply* to the question."
  Recall jumps; hallucinations drop.
- **Re-rank by authority, not just relevance.** A 0.92-similarity
  guideline must lose to a 0.78-similarity regulation. Retrieval
  re-ranker takes `normative_weight` as an input feature.

## Citation contract

Agents in production must surface citations verbatim. The contract:

```json
{
  "claim": "AML transaction monitoring threshold is £10,000 for retail customers",
  "citations": [
    {
      "doc_id": "aml-policy",
      "version": "v3.4",
      "clause_id": "§4.2.a",
      "effective_at": "2026-02-01",
      "normative_weight": "policy",
      "source_uri": "confluence://acme/aml/aml-policy?version=v3.4#§4.2.a"
    }
  ],
  "conflicts": [],
  "stale": false
}
```

If `citations` is empty, the agent must refuse the question, not guess. If
`conflicts` is non-empty, the agent surfaces the conflict and routes to a
human. If `stale: true`, the agent answers but flags staleness.

## Forget / supersession path

Two distinct flows:

- **Supersession** (normal lifecycle): new version approved → old version
  gets `effective_to` + `superseded_by`; both versions queryable by
  effective-time. This is A11 done right.
- **DSAR / regulator deletion**: rare for policies (policies are not
  personal data), but applies to ingested customer-specific letters or
  case files. Use the redact-and-tombstone path from RA10 / RA4 — text
  redacted, row preserved for audit, untouched tenants unaffected.

## Anti-patterns specifically blocked

- **A16** — never embed a regulator PDF as one chunk. Extract the clause
  tree first; one chunk per clause.
- **A4** — contradictions between authority levels (a guideline saying
  one thing, a regulation another) must surface at ingest, not when an
  agent quotes them in conflict.
- **A13** — every chunk row carries `(doc_id, version, clause_id,
  effective_at)`. Without all four, write is rejected.
- **A14** — confidence is bounded by authority. A guideline never
  out-confidences a regulation regardless of how often it is reinforced.
- **A23** — a regulator quoting "you must…" inside an ingested clause is
  *content*, not an instruction the model should obey. Tag policy text as
  data on bundle assembly.
- **A28** — the answer to "what is the current version of Policy X" comes
  from `policy_registry` (P1), not from the vector index.

## Operational SLOs

The dashboard a CISO / Head of Compliance actually wants:

- **Coverage:** % of mandatory controls (ISO 27001, PCI-DSS, NIST 800-53,
  PSD2 RTS) with a mapped policy + standard + runbook chain. Gaps red.
- **Freshness:** count of policies past `next_review_at`. Trend line.
- **Citation precision:** % of agent answers in production with at least
  one paragraph-precise citation. Target ≥ 99%.
- **Refusal rate:** % of compliance-flavored questions where the agent
  refused due to no citation. Healthy floor (some questions truly have no
  answer in policy); a sudden drop suggests the agent started guessing.
- **Conflict queue depth:** unresolved contradictions older than N days.
- **Source-format coverage:** which sources are ingested vs lagging
  (Confluence ingested, SharePoint Word docs not yet, etc.).

## See also

- `reference-architectures.md` → RA11 — the recipe this reference deepens.
- `git-anchored-ingestion.md` — when policies live in git.
- `markdown-chunking-patterns.md` — chunking interface for any structured
  source.
- `knowledge-compilation-and-wiki-pattern.md` — P7 deep dive; the
  editorial workflow this corpus needs.
- `inspection-and-review-surfaces.md` — review UI patterns.
- `tenant-isolation-patterns.md` — keeping one tenant's policies invisible
  to another.
- `graph-and-relationship-layer.md` — the cross-reference graph mechanics.
- Partner skills: `dev-context-multi-repo` for git-source catalog and
  freshness tooling; `ai-rag` for retrieval depth and reranker design.
