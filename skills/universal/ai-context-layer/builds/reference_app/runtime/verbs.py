"""Runtime verbs — Phase 1 signatures + thin reference logic.

Phase 1 ships the type-correct signatures and the simplest honest implementation
that exercises every adapter Protocol. Phase 2 will replace the bodies with the
production logic (token-aware compression, parallel select, KV-cache layout
checks, sub-agent dispatch).

Each verb is documented with the anti-patterns it blocks and the failure mode
it mitigates. Removing a verb without replacement re-opens those failures.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ..adapters import (
    ArtifactLoader,
    EmbeddingClient,
    EpisodeLog,
    LLMClient,
    MemoryStore,
    OperationalToolkit,
    ReferenceResolver,
    RetrievalStore,
)
from ..contracts import (
    ArtifactRef,
    ContextAssemblyRequest,
    ContextBundle,
    ContextRef,
    EntityProfile,
    Guardrails,
    LearnedMemory,
    LoadedArtifact,
    MemoryType,
    RetrievalResult,
)


# -----------------------------------------------------------------------------
# write — persist outside the window
# -----------------------------------------------------------------------------

def write(
    *,
    fact: LearnedMemory,
    memory_store: MemoryStore,
    episode_log: EpisodeLog | None = None,
) -> str:
    """Persist a typed fact. Blocks A1 (chat-as-memory) by requiring extraction
    to have already happened — `fact` is typed, not raw.

    Runs ingest-time contradiction detection (A4). The caller is responsible
    for resolving conflicts; this verb surfaces them, not silences them.
    """
    if not fact.source_episode_id:
        raise ValueError("LearnedMemory.source_episode_id is required (A13)")
    if not fact.owner_scope:
        raise ValueError("LearnedMemory.owner_scope is required (A10)")
    if not 0.0 <= fact.confidence <= 1.0:
        raise ValueError("LearnedMemory.confidence must be in [0, 1] (A14)")

    conflicts = memory_store.find_contradictions(fact)
    if conflicts:
        # Phase 2: route to P4 invalidation queue based on category
        # (attribution / temporal / stale). For now, attach to the fact for
        # the caller to handle.
        fact.tags = [*fact.tags, f"conflicts:{len(conflicts)}"]

    return memory_store.remember(fact)


# -----------------------------------------------------------------------------
# select — pull just-in-time slices
# -----------------------------------------------------------------------------

def select(
    *,
    request: ContextAssemblyRequest,
    entity: EntityProfile,
    memory_store: MemoryStore,
    retrieval_store: RetrievalStore,
    toolkit: OperationalToolkit,
    memory_min_confidence: float = 0.4,
    memory_limit: int = 20,
    retrieval_top_k: int = 8,
) -> dict[str, Any]:
    """Just-in-time selection from each layer. Blocks A5 (prompt stuffing)
    by capping each source and applying confidence/relevance filters before
    assembly.

    Returns a dict with `live_facts`, `memory`, `evidence` keys ready for
    `format_for_model` and `order`.
    """
    live_facts = toolkit.fetch_live_facts(entity=entity, request=request)
    memory = memory_store.recall(
        entity_id=entity.id,
        owner_scope=request.owner_scope,
        min_confidence=memory_min_confidence,
        limit=memory_limit,
    )
    evidence = retrieval_store.retrieve(
        query=request.intent,
        owner_scope=request.owner_scope,
        top_k=retrieval_top_k,
    )
    return {
        "live_facts": live_facts,
        "memory": memory,
        "evidence": evidence,
        "context_refs": list(request.context_refs),
        "artifact_refs": list(request.artifact_refs),
    }


# -----------------------------------------------------------------------------
# resolve — expand runtime refs just in time
# -----------------------------------------------------------------------------

def resolve(
    *,
    selected: dict[str, Any],
    request: ContextAssemblyRequest,
    resolver: ReferenceResolver | None = None,
    artifact_loader: ArtifactLoader | None = None,
) -> dict[str, Any]:
    """Resolve pointer-first runtime refs into typed projections.

    This is the P12 helper step around the six-verb core: keep handles in the
    request, then expand only what the current surface needs. The output stays
    typed so `format_for_model` can project signal, not payload noise.
    """

    resolved: dict[str, Any] = {
        "live_facts": list(selected.get("live_facts", [])),
        "memory": list(selected.get("memory", [])),
        "evidence": list(selected.get("evidence", [])),
        "relationship_context": list(selected.get("relationship_context", [])),
        "context_refs": list(selected.get("context_refs", [])),
        "artifact_refs": list(selected.get("artifact_refs", [])),
        "loaded_artifacts": [],
    }

    if resolver and request.context_refs:
        additions = resolver.resolve(refs=request.context_refs, request=request)
        resolved["live_facts"].extend(additions.get("live_facts", []))
        resolved["memory"].extend(additions.get("memory", []))
        resolved["evidence"].extend(additions.get("evidence", []))
        resolved["relationship_context"].extend(additions.get("relationship_context", []))
        resolved["artifact_refs"].extend(additions.get("artifact_refs", []))

    deduped_artifact_refs = _dedupe_artifact_refs(resolved["artifact_refs"])
    artifact_budget = max(0, request.projection.modality_budgets.get("artifacts", request.projection.max_artifacts))
    deduped_artifact_refs = deduped_artifact_refs[: min(request.projection.max_artifacts, artifact_budget)]
    resolved["artifact_refs"] = deduped_artifact_refs

    if artifact_loader and deduped_artifact_refs:
        loaded_artifacts = artifact_loader.load(refs=deduped_artifact_refs, request=request)
        resolved["loaded_artifacts"] = loaded_artifacts[: len(deduped_artifact_refs)]

    return resolved


# -----------------------------------------------------------------------------
# format — typed projection over raw payloads
# -----------------------------------------------------------------------------

def format_for_model(
    *,
    selected: dict[str, Any],
    request: ContextAssemblyRequest,
) -> dict[str, Any]:
    """Project each layer into the model-facing shape. Blocks A18 (raw
    embeddings) and A24 (no tool-result compaction) by ensuring nothing
    raw reaches the prompt.

    Phase 1 returns minimally projected dicts; Phase 2 adds field-level
    allowlists and per-surface projection rules.
    """
    return {
        "live_facts": [
            {k: v for k, v in fact.items() if not k.startswith("_")}
            for fact in selected["live_facts"]
        ],
        "memory": [
            {
                "id": m.id,
                "type": m.memory_type.value,
                "value": m.value,
                "confidence": round(m.confidence, 2),
                "source_episode_id": m.source_episode_id,
                "inferred": m.inferred,
            }
            for m in selected["memory"]
        ],
        "evidence": [
            {
                "evidence_id": r.evidence_id,
                "snippet": r.snippet,
                "source_id": r.source_id,
                "score": round(r.score, 3),
            }
            for r in selected["evidence"]
        ],
        "loaded_artifacts": [
            _project_loaded_artifact(
                artifact,
                max_chars=request.projection.modality_budgets.get(
                    "artifact_chars",
                    request.projection.max_inline_artifact_chars,
                ),
            )
            for artifact in selected.get("loaded_artifacts", [])
        ],
        "relationship_context": list(selected.get("relationship_context", [])),
    }


# -----------------------------------------------------------------------------
# compress — fit the budget
# -----------------------------------------------------------------------------

def compress(
    *,
    formatted: dict[str, Any],
    max_tokens: int,
    llm: LLMClient,
    strategy: str = "progressive_disclosure",
) -> dict[str, Any]:
    """Bring `formatted` under `max_tokens`. Blocks A20 (context distraction)
    and mitigates context rot by capping the bundle before it reaches the
    model.

    Two strategies, both preserve IDs so `assemble()` can correlate compressed
    items back to the source memory/evidence rows:

    - `progressive_disclosure` (default): drop lowest-priority items first
      (evidence tail → memory tail → live_facts tail). Preserves the highest-
      ranked items in full. Best when items are independent and ranking is
      trustworthy.
    - `summarize`: ask the LLM to rewrite each evidence snippet and memory
      value to a tighter form *while preserving evidence_id and
      source_episode_id*. Items remain countable and citable; only their
      payload shrinks. Best when every item carries load-bearing information.
    """
    if _total_tokens(formatted, llm) <= max_tokens:
        return formatted
    if strategy == "summarize":
        return _summarize_to_fit(formatted, max_tokens, llm)
    return _truncate_to_fit(formatted, max_tokens, llm)


def _total_tokens(formatted: dict[str, Any], llm: LLMClient) -> int:
    return sum(llm.count_tokens(str(v)) for v in formatted.values())


def _truncate_to_fit(
    formatted: dict[str, Any], max_tokens: int, llm: LLMClient
) -> dict[str, Any]:
    out = {**formatted}
    for key in ("loaded_artifacts", "evidence", "memory", "live_facts", "relationship_context"):
        while out.get(key) and _total_tokens(out, llm) > max_tokens:
            out[key] = out[key][:-1]
    return out


def _summarize_to_fit(
    formatted: dict[str, Any], max_tokens: int, llm: LLMClient
) -> dict[str, Any]:
    """Rewrite snippets and values to a tighter form, preserving IDs.

    The LLM is told the budget for each section; it returns one summary per
    item. If the LLM cannot meet the budget, we fall back to truncation —
    summarization is a hint, not a guarantee.
    """
    out = {**formatted}
    # Cheap heuristic: each section gets a proportional share of the budget.
    sections = ("loaded_artifacts", "evidence", "memory", "live_facts")
    section_budgets = {s: max_tokens // (len(sections) + 1) for s in sections}

    for section, budget in section_budgets.items():
        items = out.get(section, [])
        if not items:
            continue
        if sum(llm.count_tokens(str(i)) for i in items) <= budget:
            continue
        per_item = max(64, budget // max(len(items), 1))
        out[section] = [_summarize_item(item, per_item, llm) for item in items]

    if _total_tokens(out, llm) > max_tokens:
        # LLM didn't hit the budget; fall back to truncation on the summaries.
        return _truncate_to_fit(out, max_tokens, llm)
    return out


def _summarize_item(item: dict[str, Any], per_item_budget: int, llm: LLMClient) -> dict[str, Any]:
    """Summarize the prose-y field of an item while preserving IDs.

    For evidence: shrink `snippet`. For memory: shrink `value` if it is
    large prose. Other fields pass through untouched. The model is shown
    the IDs and told not to invent or drop them.
    """
    text_field = "snippet" if "snippet" in item else None
    if text_field is None and isinstance(item.get("value"), str):
        text_field = "value"
    if text_field is None and isinstance(item.get("text_excerpt"), str):
        text_field = "text_excerpt"
    if text_field is None:
        return item

    original = item[text_field]
    if not isinstance(original, str) or llm.count_tokens(original) <= per_item_budget:
        return item

    id_field = next((k for k in ("evidence_id", "source_episode_id", "id") if k in item), None)
    id_value = item.get(id_field, "") if id_field else ""
    system = (
        "You compress context for a downstream LLM. Rewrite the input to fit "
        f"within ~{per_item_budget} tokens. Preserve every named identifier "
        "exactly. Do not invent facts. Output the rewritten text only."
    )
    instruction = f"Identifier: {id_field}={id_value}\n\nInput:\n{original}"
    rewritten = llm.complete(
        system=system,
        messages=[{"role": "user", "content": instruction}],
        max_tokens=per_item_budget,
    )
    return {**item, text_field: rewritten}


# -----------------------------------------------------------------------------
# order — KV-cache-friendly layout
# -----------------------------------------------------------------------------

def order(
    *,
    formatted: dict[str, Any],
    priority_order: list[str],
) -> list[tuple[str, Any]]:
    """Apply deterministic ordering. Blocks F3 (clash) inputs from producing
    nondeterministic prompts and keeps KV cache hits stable across turns.

    Returns an ordered list of (section_name, payload) tuples. Caller renders
    them into the prompt in this exact order, every turn."""
    section_map = {
        "live_facts": formatted.get("live_facts", []),
        "memory": formatted.get("memory", []),
        "domain_evidence": formatted.get("evidence", []),
        "loaded_artifacts": formatted.get("loaded_artifacts", []),
        "relationship_context": formatted.get("relationship_context", []),
        "guardrails": formatted.get("guardrails", {}),
    }
    return [(name, section_map[name]) for name in priority_order if name in section_map]


# -----------------------------------------------------------------------------
# isolate — sub-agent for long-horizon work (P11)
# -----------------------------------------------------------------------------

def isolate(
    *,
    sub_task_intent: str,
    parent_bundle: ContextBundle,
    llm: LLMClient,
    max_tokens: int = 4000,
    allowed_evidence_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Dispatch a bounded sub-task to its own context window and return only
    the validated summary.

    Blocks F2 (distraction) on long-horizon tasks and mitigates context rot
    by isolating the parent. Adds a summary-contract check that blocks F1
    (poisoning) at the sub-agent boundary: the sub-agent must declare which
    evidence it cited, and we reject any IDs not in the parent bundle.

    Returns:
        {
            "summary": str,                 # the sub-agent's compact answer
            "cited_evidence_ids": [str],    # validated subset of parent evidence
            "rejected_ids": [str],          # IDs the sub-agent claimed but were
                                            # not in the parent bundle (audit signal)
        }
    """
    parent_evidence_ids = {r.evidence_id for r in parent_bundle.domain_evidence}
    if allowed_evidence_ids is not None:
        parent_evidence_ids &= set(allowed_evidence_ids)

    sub_system = (
        "You are a focused sub-agent with a bounded context window. Complete "
        "the task using ONLY the parent context provided. Return a JSON "
        'object: {"summary": "<your compact answer>", "cited_evidence_ids": '
        '["evidence_id_1", ...]}. Cite only evidence_ids that appear in the '
        "parent context. Do not invent IDs."
    )
    sub_messages = [
        {
            "role": "user",
            "content": (
                f"Task: {sub_task_intent}\n"
                f"Parent bundle id: {parent_bundle.id}\n"
                f"Available evidence_ids: {sorted(parent_evidence_ids)}\n"
            ),
        },
    ]
    raw = llm.complete(system=sub_system, messages=sub_messages, max_tokens=max_tokens)

    parsed = _parse_subagent_response(raw)
    claimed = set(parsed.get("cited_evidence_ids", []))
    cited = sorted(claimed & parent_evidence_ids)
    rejected = sorted(claimed - parent_evidence_ids)
    return {
        "summary": parsed.get("summary", raw),
        "cited_evidence_ids": cited,
        "rejected_ids": rejected,
    }


def _parse_subagent_response(raw: str) -> dict[str, Any]:
    """Best-effort JSON extraction. Sub-agent contract is JSON, but real
    models occasionally wrap or echo. Be tolerant; fall back to {}."""
    import json
    import re

    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {}


# -----------------------------------------------------------------------------
# assemble — the one function most callers use
# -----------------------------------------------------------------------------

def assemble(
    *,
    request: ContextAssemblyRequest,
    entity: EntityProfile,
    memory_store: MemoryStore,
    retrieval_store: RetrievalStore,
    toolkit: OperationalToolkit,
    llm: LLMClient,
    resolver: ReferenceResolver | None = None,
    artifact_loader: ArtifactLoader | None = None,
) -> ContextBundle:
    """Compose the runtime verbs into one bundle. This is what the
    application calls per request.

    Order of operations (do not reorder casually — each step depends on the
    previous):
        select → resolve → format → compress → order → bundle
    """
    selected = select(
        request=request,
        entity=entity,
        memory_store=memory_store,
        retrieval_store=retrieval_store,
        toolkit=toolkit,
    )
    resolved = resolve(
        selected=selected,
        request=request,
        resolver=resolver,
        artifact_loader=artifact_loader,
    )
    formatted = format_for_model(selected=resolved, request=request)
    compressed = compress(
        formatted=formatted,
        max_tokens=request.projection.max_tokens,
        llm=llm,
        strategy=request.projection.compression_strategy,
    )
    ordered_sections = order(
        formatted=compressed,
        priority_order=request.projection.priority_order,
    )

    bundle = ContextBundle(
        surface=request.surface,
        actor=request.actor,
        owner_scope=request.owner_scope,
        live_facts=compressed.get("live_facts", []),
        memory=[m for m in resolved["memory"] if _included(m, compressed.get("memory", []))],
        domain_evidence=[
            r for r in resolved["evidence"] if _included_evidence(r, compressed.get("evidence", []))
        ],
        context_refs=list(request.context_refs),
        loaded_artifacts=[
            a
            for a in resolved.get("loaded_artifacts", [])
            if _included_artifact(a, compressed.get("loaded_artifacts", []))
        ],
        relationship_context=list(compressed.get("relationship_context", [])),
        guardrails=Guardrails(),
        projection=request.projection,
        assembled_at=datetime.now(UTC),
        token_count_estimate=sum(llm.count_tokens(str(v)) for _, v in ordered_sections),
    )
    return bundle


def _included(memory: LearnedMemory, projected: list[dict[str, Any]]) -> bool:
    return any(p.get("id") == memory.id for p in projected)


def _included_evidence(result: RetrievalResult, projected: list[dict[str, Any]]) -> bool:
    return any(p.get("evidence_id") == result.evidence_id for p in projected)


def _included_artifact(artifact: LoadedArtifact, projected: list[dict[str, Any]]) -> bool:
    return any(p.get("artifact_id") == artifact.artifact_id for p in projected)


def _dedupe_artifact_refs(refs: list[ArtifactRef]) -> list[ArtifactRef]:
    seen: dict[str, ArtifactRef] = {}
    for ref in refs:
        seen.setdefault(ref.artifact_id, ref)
    return list(seen.values())


def _project_loaded_artifact(artifact: LoadedArtifact, *, max_chars: int) -> dict[str, Any]:
    text_excerpt = artifact.text_content[:max_chars]
    if len(artifact.text_content) > max_chars:
        text_excerpt += "..."
    return {
        "artifact_id": artifact.artifact_id,
        "artifact_type": artifact.artifact_type,
        "mime_type": artifact.mime_type,
        "source_ref_id": artifact.source_ref_id,
        "evidence_id": artifact.evidence_id,
        "text_excerpt": text_excerpt,
        "metadata": {
            k: v
            for k, v in artifact.metadata.items()
            if k not in {"raw_payload", "bytes", "base64"}
        },
    }
