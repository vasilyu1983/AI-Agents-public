# Context Engineering — Structured Context Management

**Purpose**: Context engineering matters more than model selection. Even weaker LLMs perform well with proper context structure.

---

## Core Principle

**Key Insight**: Structured context management has more impact on agent performance than model selection.

**Evidence**: Proper context structure allows even weaker LLMs to perform comparably to stronger models on complex tasks.

---

## Progressive Disclosure

**What**: Load context on-demand rather than upfront

**Pattern**:
```text
1. Route by domain (classify intent)
2. Retrieve relevant context (lazy load)
3. Inject only what's needed (filter by relevance)
4. Expand context if needed (iterative refinement)
```

**Benefits**:
- Reduces token costs
- Improves latency
- Minimizes irrelevant information
- Scales better with large knowledge bases

**Implementation**:
```yaml
# Bad: Load all context upfront
context = load_all_knowledge()

# Good: Load on-demand
domain = classify_query(query)
context = retrieve_by_domain(domain, query)
```

---

## Session Management

**What**: Treat sessions as conversation containers with proper lifecycle management

**Best Practices**:

1. **Framework differences**: Honor session handling differences across frameworks (LangChain, LangGraph, CrewAI)
2. **Shared sessions**: Share session handles safely across agents with scoped replay
3. **Session boundaries**: Clear session start/end; no context leakage between sessions
4. **Session state**: Persist critical state; allow recovery on failures
5. **Session cleanup**: Expire inactive sessions; enforce retention policies

**Session Lifecycle**:
```yaml
session:
  id: "sess-abc-123"
  started_at: "2024-01-01T00:00:00Z"
  state:
    conversation_history: []
    task_context: {}
    user_preferences: {}
  ttl: 3600  # seconds
```

---

## Memory Provenance

**What**: Track lineage (source, timestamp, approvals) for all stored data

**Requirements**:

- **Source attribution**: Where did this information come from?
- **Timestamp**: When was this information acquired?
- **Approvals**: Who/what validated this information?
- **Verifiability**: Can this information be verified?

**Store Only Verifiable Data**:
```json
{
  "fact": "User prefers dark mode",
  "source": "user_settings_api",
  "timestamp": "2024-01-01T12:00:00Z",
  "verified_by": "user_confirmation",
  "confidence": 1.0
}
```

**Never Store**:
- Unverified assumptions
- Hallucinated information
- PII without explicit consent
- Sensitive data without encryption

---

## Generation Triggers

**What**: When to generate/consolidate memory records

**Triggers**:

1. **Phase boundaries**: Task start/end, session end, workflow completion
2. **Confidence drops**: Agent uncertainty increases, contradictions detected
3. **New entities**: New people, organizations, or concepts identified
4. **Explicit user requests**: User asks to remember something
5. **State changes**: Important context updates (preferences, goals, constraints)

**Pattern**:
```yaml
# After phase boundary
if task_completed:
  consolidate_task_memory()
  update_long_term_memory()

# After confidence drop
if confidence < threshold:
  retrieve_additional_context()
  rewrite_query()

# After new entity
if new_entity_detected:
  extract_entity_metadata()
  store_with_provenance()
```

---

## Background vs Blocking Operations

**What**: When to run memory operations async vs sync

**Background (Async)**:
- Heavy writes (consolidation, summarization)
- Low-priority updates (analytics, logging)
- Bulk operations (cleanup, archival)
- Non-critical metadata (usage stats)

**Blocking (Sync)**:
- Critical state updates (task progress, user preferences)
- Safety checks (PII detection, policy validation)
- Handoff context (agent-to-agent transfer)
- Real-time validation (input/output checks)

**Pattern**:
```python
# Background write
async def consolidate_session():
    await background_task(generate_summary, session_data)

# Blocking write
def update_task_state(state):
    validate_state(state)
    write_task_state(state)  # Must complete before continuing
```

---

## Retrieval Timing

**What**: When to retrieve/re-retrieve context

**Retrieve Before**:
- High-impact actions (irreversible operations)
- First interaction (session start)
- Domain switches (route change)
- User requests (explicit questions)

**Re-retrieve After**:
- State changes (user updates preferences)
- Time windows (enforce recency constraints)
- Failed actions (context might be stale)
- Contradictions detected (verify current state)

**Enforce Recency Windows**:
```yaml
retrieval_policy:
  max_age: 3600  # seconds
  revalidate_on:
    - state_change
    - time_window_expired
    - contradiction_detected
```

---

## Multimodal Context

**What**: Handling images, audio, video alongside text

**Normalization**:
```yaml
multimodal_asset:
  id: "asset-123"
  type: "image"
  modalities:
    - visual: {url: "...", format: "png"}
    - text: {caption: "...", alt_text: "..."}
    - embedding: {vector: [...], model: "clip"}
  metadata:
    source: "user_upload"
    timestamp: "2024-01-01T12:00:00Z"
    tags: ["diagram", "architecture"]
```

**Storage Strategy**:
- **Text + embeddings**: Always store both
- **Metadata normalization**: Consistent schema across modalities
- **Modality tags**: Label each modality clearly
- **Cross-modal search**: Enable search across modalities

---

## Fresh Contexts

**What**: Spawning new agents with clean state

**When to Use**:
- Task isolation (prevent context bleed)
- Parallel execution (independent subtasks)
- Testing/evaluation (reproducible conditions)
- Security boundaries (different trust levels)

**Pattern**:
```python
# Spawn new agent with fresh context
def spawn_agent(task):
    agent = Agent()
    agent.load_context(
        domain=task.domain,
        constraints=task.constraints,
        memory=load_validated_memory(task.context_id)
    )
    return agent
```

**Hydration from Validated Memory**:
```yaml
context_hydration:
  session_id: "sess-abc-123"
  validated_facts:
    - fact_id: "fact-001"
      source: "user_settings"
      verified: true
  constraints:
    - policy: "no_pii"
    - policy: "sandbox_mode"
```

---

## Context Size Management

**Strategies**:

1. **Summarization**: Compress long context (> 2000 tokens)
2. **Sliding windows**: Keep recent context, archive old
3. **Hierarchical context**: High-level summary + detail on-demand
4. **Relevance filtering**: Only inject relevant chunks
5. **Dynamic truncation**: Truncate low-priority context first

**Pattern**:
```python
def manage_context(context, max_tokens=8000):
    if len(context) > max_tokens:
        # Prioritize critical context
        critical = extract_critical_context(context)
        remaining = max_tokens - len(critical)

        # Summarize non-critical
        non_critical = context - critical
        summarized = summarize(non_critical, max_tokens=remaining)

        return critical + summarized
    return context
```

---

## Context Validation

**What**: Verify context quality before injection

**Validation Checks**:

- **Relevance**: Does this context relate to the task?
- **Recency**: Is this context up-to-date?
- **Completeness**: Is critical information missing?
- **Contradictions**: Does context contain conflicts?
- **Safety**: Does context contain PII/sensitive data?

**Pattern**:
```python
def validate_context(context):
    checks = [
        validate_relevance(context),
        validate_recency(context),
        validate_completeness(context),
        check_contradictions(context),
        check_pii(context)
    ]
    return all(checks)
```

---

## Related Resources

**Memory Architecture**: [`memory-systems.md`](memory-systems.md)
**RAG Patterns**: [`rag-patterns.md`](rag-patterns.md)
**Tool Design**: [`tool-design-specs.md`](tool-design-specs.md)
**Agent Operations**: [`agent-operations-best-practices.md`](agent-operations-best-practices.md)

---

## Usage Notes

- **Context > Model**: Invest in context engineering before upgrading models
- **Measure impact**: Track performance improvements from context changes
- **Iterate quickly**: Test context patterns with fast feedback loops
- **Document provenance**: Always track where context came from
