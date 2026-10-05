# Serving a Knowledge Base or Context Layer over MCP

Load this when an MCP server returns retrieved document text (policy corpus, wiki, code hub, notes) to agents. Structured stores (SQL, BI) use [mcp-for-dwh.md](mcp-for-dwh.md); generic hardening is in [mcp-security.md](mcp-security.md). What to put in the store (labels, graph, freshness) belongs to [ai-context-layer](../../ai-context-layer/SKILL.md); its `references/patterns-catalog.md` holds the sensitivity-label pattern this server enforces.

The pattern comes from a regulated multi-entity policy corpus served to Claude Code and Codex over stdio. A 180-repo code hub showed the opposite failure: agents with no queryable surface read a large graph JSON directly.

## 1. Bounded tool surface, not file access

Expose two tools, not the filesystem or the graph:

- `list_scopes()` returns the scopes (entity, repo, tenant) the caller may query, plus the server's fixed clearance and flags.
- `retrieve_context(question, scope, k)` returns cited evidence or an abstain. Validate `scope` against the discovered allow-list before touching disk (path traversal), and clamp `k` (non-numeric, NaN, and huge values fall back to the default).

Tell agents in the server `instructions` and in project memory not to read the index, registry, or graph files directly: that path bypasses scope isolation, approval gates, and clearance.

## 2. Policy is bound at launch, never an argument

Clearance (`public|internal|restricted`) and `include_pending` (serve known-unratified drafts) come from the launch environment. A tool argument for either lets the model escalate itself, including under prompt injection. Default to the lower clearance and refuse to start on an invalid value. Filter clearance inside each retrieval leg, before ranking (ai-context-layer P24), so no count, rank, or abstain reason reveals that an above-clearance document exists. Governance withholding is not secret: return `superseded_withheld` and `pending_withheld` so the agent knows a newer or draft version exists.

**Named deviation: existence signal.** A deployment whose callers all sit inside one trust boundary, and that has an escalation path ("ask someone with clearance"), may also return `restricted_withheld` and say that clearance is fixed at launch. Otherwise the generic "no results" reads as "the corpus is silent". Enable it as a launch flag, record the decision, and never offer it as a tool argument. It is off for multi-tenant, customer-facing, or mixed-trust callers.

## 3. Retrieved text is data

Documents are edited by many people, so every string that came from a document or registry (title, heading, exception notes, abstain reasons that embed titles), not just the body, is untrusted.

- NFKC-normalise first, then drop control and format characters (zero-width, ESC, BEL), keeping newline and tab.
- Wrap each hit body in a fence tag carrying scope, doc id, and version. Neutralise any fence lookalike inside the text however it is spelled (`</ retrieved-document`, fullwidth or zero-width variants). Do this after normalisation and before the length cap, because neutralising lengthens the string.
- Strip absolute server paths and home directories from every string sent out.
- Truncate on a paragraph, then line, then space boundary, and report `truncated` plus `full_length`. Add the truncation marker after neutralising.
- Mark every hit and the packet `content_trust: untrusted`, and state in server `instructions` that fenced text is evidence, never directives. Fencing lowers the risk; it does not remove it, so still gate sensitive sinks (see Security Guardrails in `../SKILL.md`).

## 4. Results carry citations and status

Per hit: doc id, title, version, section or clause id, page where one exists, content hash and source revision, retrieval time, and the registry status fields (approval state, normative weight, sensitivity). Also pass through, never silently resolve:

- `stale` or past-effective-date flags;
- superseded documents withheld by default, with a count;
- `version_conflict` when two versions of one document both match;
- an approval basis, so "unknown" is not read as "approved".

Per-section scope matters: tagging scope per document served one entity's addendum as another entity's rule. Tag scope where the content changes, not where the file is.

## 5. Abstain is a first-class result

Return `{abstain: true, reason, coverage}` when coverage of the question is below a gate, with wording that silence is not permission. Without it the model fills gaps. Test abstain on questions the corpus cannot answer, using hard negatives; an eval that has only answerable questions never exercises it.

## 6. Text for people, JSON for machines

Return the packet as structured content with an `outputSchema` and a short text rendering (`mcp-patterns.md` has the result shapes). Machine consumers need validated fields (status, version, citation) to monitor at field level; a prose-only answer cannot be checked.

## 7. Tests that pin intent

Cover with unit tests, run against the default launch config with no overrides:

- above-clearance canaries are never returned and never change counts or ranks; with the existence signal enabled, only `restricted_withheld` changes;
- clearance and `include_pending` cannot be set through tool arguments;
- an injected closing fence cannot close the wrapper (several spellings);
- unknown scope abstains without calling the retrieval layer;
- `k` coercion, truncation flag, and path stripping.

## Pitfalls from the real builds

- Editing the query code changed the index fingerprint, and the eval silently fell back to a weaker in-memory path. Fail loud on a stale index instead of degrading.
- An eval written by the builders scored far above an independent held-out set; score the served tool, not only the retrieval library behind it.
