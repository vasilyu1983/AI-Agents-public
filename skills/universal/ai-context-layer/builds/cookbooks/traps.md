# Cookbook: Traps Appendix

Concrete recipes for failure modes seen in production context layers. Each entry: what it looks like, why it happens, what to do.
Pair with `references/anti-patterns-catalog.md` (storage axis) and
`references/context-hygiene.md` (runtime axis).

## T1. Anthropic streaming truncation at long context

**Symptom.** Streamed responses cut off mid-sentence at high token
counts. The completion is shorter than `max_tokens` and the stop reason
is `end_turn` despite obvious incomplete output.

**Cause.** At very long input contexts (≳200K tokens), output budgets
silently shrink to keep latency bounded. The provider does not error;
it returns whatever it had.

**Fix.**
- Check `response.stop_reason` on every call, not just on errors.
- For long-context interactive surfaces, cap input at 70% of the model's
  max context to leave room for sane output.
- If you genuinely need long inputs and long outputs, dispatch to a
  sub-agent (`isolate`) instead — small input, full output budget.

## T2. JSON-mode parser drift across providers

**Symptom.** Your tool-using agent works on Anthropic, breaks on
OpenAI on the same prompt because the JSON has trailing commas, code
fences, or extra commentary.

**Cause.** "JSON mode" / "structured output" semantics differ across
providers. Anthropic typically wraps JSON in prose unless you use a
tool definition; OpenAI's structured output mode is strict; older
APIs return whatever the model felt like.

**Fix.**
- The `isolate` verb in the kit ships a `_parse_subagent_response`
  helper that handles "JSON wrapped in prose" and "raw JSON" — copy
  the pattern for your own tool replies.
- For genuine reliability, define tools properly via the provider's
  tool API; do not rely on prompt-only "respond with JSON" instructions.
- Validate every parsed JSON against a schema (Pydantic, JSONSchema)
  and raise on failure rather than coercing — silent coercion masks
  the drift and surfaces as wrong-data bugs later.

## T3. Embedding-model migration

**Symptom.** Switching from text-embedding-3-small to a newer or
different model. Naive switch breaks recall: existing embeddings are in
the old space, queries are in the new space.

**Recipe.**

Use the model-versioned embedding table pattern in
`ai-vector-brain/assets/sql/001_schema.sql` instead of adding a second vector
column to a context-layer table.

Migration shape:

1. Add new embedding rows with the new `model_id`.
2. Dual-write during the migration window.
3. Backfill in batches; old retrieval keeps working from old `model_id` rows.
4. Once 100% backfilled and validated, switch retrieval to the new `model_id`.
5. Delete old model rows only after rollback is no longer needed.

Validation in step 4 means: pick 50 representative queries, run them
against v1 and v2, compare top-5 overlap. Cut over only if overlap is
≥80% or the v2 results are clearly better on your eval suite (Phase 4).

**Don't:**
- Drop v1 before v2 is fully backfilled. You'll have a window of empty
  results.
- Mix v1 and v2 in the same query — vector ops between different
  embedding models are meaningless.
- Re-embed in the foreground. It is always batchable.

## T4. MCP indirect-prompt-injection regression

**Symptom.** A new MCP server is added; unrelated agent behaviors
regress (oscillating tool choice, unexpected refusals).

**Cause.** MCP tool descriptions enter the model's context. A malicious
or just careless tool description can override your system prompt
("ignore previous instructions and..."). This is the canonical F3
clash + A23 indirect-prompt-injection failure.

**Fix.** See `references/security-threat-model.md` for the full T1–T7
threat model. Three controls that catch most cases:

1. **Vet tool descriptions on registration.** Strip imperative phrases
   addressing the model. Anything starting with "Always", "Ignore",
   "From now on" is a smell.
2. **Per-surface tool allowlists.** A new MCP server should not be
   universally available; opt surfaces into it explicitly.
3. **Token-origin tagging.** Tool outputs and MCP descriptions are
   not trusted instruction sources. Format-tag them in your prompt
   so the model knows to treat them as data, not commands.

## T5. Mode-collapse detection at scale

**Symptom.** Across thousands of users, the agent's responses
qualitatively converge. Phase 4's mode-collapse suite catches the
acute case but is too small to catch slow drift in production.

**Recipe.** Sample-based detection.

1. Sample 0.1–1% of assembled bundle/response pairs per surface.
2. For each sample, compute Jaccard distance against (a) other
   sampled responses on the same surface, (b) the previous week's
   samples.
3. Track two metrics:
   - **mean cross-prompt distance** (today vs today) — should stay
     above your `MODE_COLLAPSE_FLOOR`.
   - **week-over-week drift** — sudden drops are the early warning
     signal even if absolute numbers are still above the floor.
4. Alert on either dropping below the floor or week-over-week drop
   >20%.

## T6. Backfill pipeline flooding the contradiction queue

**Symptom.** Backfill (T0 of memory layer adoption) generates
thousands of `find_contradictions` hits. Reviewers cannot keep up;
the contradiction queue grows monotonically.

**Cause.** Backfill extracts inferred memories from old chats. Many
will conflict with each other because the user's preferences changed
over time. Treating each as a present-tense contradiction misclassifies
*temporal supersession* as *attribution conflict*.

**Fix.**
- Sort backfill rows by their source episode timestamp ascending.
- For each conflict the contradiction detector returns, if the older
  row's `created_at` is before the new row's, treat it as temporal
  supersession (auto `forget` with reason="temporal_backfill") and
  skip the review queue.
- Only attribution conflicts (same time window, different value) reach
  the queue.

## T7. Re-embedding the entire corpus on every nightly job

**Symptom.** Embedding cost is the largest line item in your AI bill.

**Cause.** Nightly job re-embeds every chunk regardless of whether
the source changed.

**Fix.** Use `KnowledgeSource.content_hash` as the change-detection
signal. Re-embed only when the hash changes; for chunk-level edits,
re-embed only the changed chunks. The reference schema supports this
out of the box; the trap is in your sync job's logic.

## T8. Sub-agent fabricating evidence_ids

**Symptom.** Audit shows users get responses citing evidence IDs
that do not exist in any source.

**Cause.** Sub-agents under pressure to "answer something" hallucinate
plausible-looking evidence IDs.

**Fix.** Built into Phase 2's `isolate(...)` — it returns
`rejected_ids` for any cited ID not in the parent bundle. Two
follow-ups:

- Alert on any non-empty `rejected_ids` (T0 — that's the F1 detector).
- For repeat offenders (a sub-task that consistently fabricates), tighten
  the `allowed_evidence_ids` allowlist passed to `isolate(...)` rather
  than relying on the validator alone.

## T9. Provider model deprecation

**Symptom.** Your `model="claude-..."` returns 410 Gone or silently
falls back to a different model. Eval suite results shift overnight.

**Fix.**
- Pin model IDs in config, not in code. One config change should swap
  every site.
- Run the eval suite on the new model *before* the old one is
  deprecated, not after.
- Treat model deprecation as a release event with a rollback plan.
  It is not a routine upgrade.

## T10. Memory layer becoming a data subject's "right to be forgotten" liability

**Symptom.** GDPR / CCPA / similar request asks for full deletion of
a user's data. Your memory layer is non-destructive (good) but now
you cannot honor the request.

**Fix.** Build the tombstone pipeline before you need it.

```python
def hard_delete_for_dsar(scope, entity_id):
    """For data-subject deletion requests only. Bypasses non-destructive
    semantics — use audit logs to record the legal basis."""
    audit.record(action="dsar_delete", scope=scope, entity_id=entity_id, ticket=...)
    memory.execute("DELETE FROM learned_memory WHERE entity_id = %s "
                   "AND owner_scope = %s::jsonb", (entity_id, json.dumps(scope)))
    episodes.execute("DELETE FROM episode_log WHERE owner_scope = %s::jsonb "
                     "AND episode->>'entity_id' = %s", (json.dumps(scope), entity_id))
    # Re-embed affected sources because chunks may quote the user.
```

This is the only sanctioned `DELETE` path against either table. Audit
every call. Test the path in staging quarterly.

## How to add to this list

When something bites you in production:

1. Add an entry here with **Symptom / Cause / Fix**.
2. If applicable, add a regression case to `evals/suites/<suite>/dataset.jsonl`.
3. If structural, add an anti-pattern to `references/anti-patterns-catalog.md`.

The list earns its keep when the same trap doesn't bite the same team
twice.
