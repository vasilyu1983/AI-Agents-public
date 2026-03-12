# Memory Systems — Best Practices

*Purpose: Provide operational patterns and rules for building, retrieving, validating, updating, and consolidating memory in AI agents.*

---

# 1. Memory Types

### Pattern: Four-Memory Model

| Type | Purpose | Lifetime |
|------|---------|----------|
| Session | Track current conversation | short-term |
| Long-Term | Persist user preferences / stable facts | long-term |
| Episodic | Capture past events with timestamps | medium-term |
| Task (Scratchpad) | Internal reasoning state | ephemeral |

---

# 2. Memory Retrieval Pattern

### Pattern: Retrieval-on-Demand

```
retrieve_memory(query)
→ filter_relevant()
→ summarize_if_needed()
→ inject_into_context()
```

**Checklist**

- [ ] Retrieve only when needed for task.  
- [ ] Apply relevance scoring.  
- [ ] Summarize entries > 200 tokens.  
- [ ] Remove duplicates.  
- [ ] Enforce recency window if domain requires.  

### Decision Tree

```
Is task dependent on prior context?
→ Yes → Retrieve memory
→ No → Continue without memory
```

---

# 3. Memory Write Pattern

### Pattern: Controlled Write

```
validate_candidate_memory()
request_confirmation_if_needed()
write_memory(entry)
```

**Checklist**

- [ ] Must be stable, verifiable, and non-sensitive.  
- [ ] Must have clear provenance (source, date).  
- [ ] Reduce to smallest factual unit.  
- [ ] Ask for user confirmation when ambiguous or personal.  

### Anti-Patterns

- AVOID: Storing temporary reasoning steps.  
- AVOID: Storing tool errors or noise.  
- AVOID: Storing unverified user claims.  
- AVOID: Storing private data without explicit consent.  

---

# 4. Memory Extraction Pattern

### Pattern: Key-Value Extraction

```
extract_key_facts(content)
clean_facts()
store_as_memory(facts)
```

**Checklist**

- [ ] Convert long explanations into atomic facts.  
- [ ] Remove redundant phrasing.  
- [ ] Use consistent field names.  
- [ ] Exclude emotional or subjective text.  

**Structure**

```
{
  "fact": "...",
  "source": "...",
  "timestamp": "YYYY-MM-DD"
}
```

---

# 5. Memory Consolidation Pattern

### Pattern: Merge & Summarize

```
group_similar_memories()
combine()
rewrite_as_summary()
store_summary()
archive_originals()
```

**Checklist**

- [ ] Combine memories about same domain/user preference.  
- [ ] Summaries ≤ 200 tokens.  
- [ ] Preserve traceability.  

**When to Consolidate**
>
- >5 related memories  
- Memory drift detected  
- Repeated queries from user  

---

# 6. Memory Scoring Pattern

### Pattern: Relevance Scoring

For each memory entry:

```
score = relevance_to_query + domain_match + recency_weight
```

**Checklist**

- [ ] Only score memories in matching domain.  
- [ ] Discard score < threshold (e.g., <0.3).  
- [ ] Prioritize recent memories when conflicts appear.  

**Quick Table**

| Factor | Weight |
|--------|--------|
| Relevance | 0.5 |
| Domain Match | 0.3 |
| Recency | 0.2 |

---

# 7. Memory Injection Pattern

### Pattern: Minimal Injection

```
<memories>
[summary_1]
[summary_2]
</memories>
```

**Checklist**

- [ ] Inject only relevant and summarized entries.  
- [ ] Keep total injection < 500 tokens.  
- [ ] Put memories before planning block.  

---

# 8. Memory Trigger Rules

### Retrieval Triggers

- Query references past events.  
- Query references personal preference.  
- Query requires continuity.  
- Query references incomplete prior task.  

### Write Triggers

- User makes an explicit preference statement.  
- User confirms a new stable fact.  
- Session summary contains durable information.  

### Consolidation Triggers

- Drift detected (conflicting memories).  
- High memory volume.  
- Similar items repeating across sessions.  

---

# 9. Session Management Patterns

### Pattern: Compact Session

```
keep(relevant_history)
summarize(past_turns)
store_short_summary()
```

**Checklist**

- [ ] Keep only relevant turns (≤ 10).  
- [ ] Use summaries to replace long transcripts.  
- [ ] Avoid injecting entire transcripts.  

---

# 10. Episodic Memory Pattern

### Pattern: Event Capture

```
event:
  description: "..."
  source: "..."
  timestamp: "..."
```

**Checklist**

- [ ] Used only for events with lasting relevance.  
- [ ] Timestamped.  
- [ ] Neutral language (no reasoning).  

---

# 11. Memory Validation Pattern

### Pattern: Validate Before Use

```
validate_source()
validate_recency()
validate_consistency()
```

**Checklist**

- [ ] Reject outdated memories.  
- [ ] Reject memories referencing deprecated schemas.  
- [ ] Reject contradictory entries (trigger consolidation).  

**Decision Tree**

```
Is memory contradictory?
→ Yes → consolidate or request clarification
→ No → continue
```

---

# 12. Memory Safety Rules

**Do Not Store**

- Sensitive PII  
- Financial/health data  
- Credentials  
- System IDs  
- Speculative information  
- Internal reasoning or chain-of-thought  

**Do Store (with confirmation)**

- Stable preferences  
- Non-sensitive profile info  
- Reusable task context  

---

# 13. Memory Anti-Patterns (Master List)

- AVOID: Writing memory without confirmation.  
- AVOID: Storing hallucinated or unverified information.  
- AVOID: Injecting large memory blocks directly.  
- AVOID: Using memory for internal reasoning steps.  
- AVOID: Allowing drift without consolidation.  
- AVOID: Storing user prompts verbatim.  

---

## 14. Advanced Memory Architectures (2025)

Recent research introduces sophisticated memory patterns for production agents.

## A-MEM: Agentic Memory (Zettelkasten-Inspired)

A dynamic memory organization system that creates interconnected knowledge networks:

```
┌─────────────────────────────────────────────────────────────┐
│                    A-MEM ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│  │ Memory  │◄──►│ Memory  │◄──►│ Memory  │                │
│  │ Note A  │    │ Note B  │    │ Note C  │                │
│  └────┬────┘    └────┬────┘    └────┬────┘                │
│       │              │              │                       │
│       └──────────────┼──────────────┘                       │
│                      ▼                                      │
│              ┌──────────────┐                               │
│              │ Dynamic Index │                              │
│              │ (Auto-updated)│                              │
│              └──────────────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles**:

1. **Atomic Notes**: Each memory is a self-contained unit
2. **Bidirectional Links**: Memories connect to related memories
3. **Dynamic Indexing**: Index updates as new memories form
4. **Emergent Structure**: Knowledge networks form organically

**Implementation Pattern**:

```python
class AgenticMemory:
    def add_memory(self, content: str, context: dict):
        # Create atomic memory note
        note = MemoryNote(
            id=generate_id(),
            content=content,
            metadata=context,
            links=[]
        )

        # Find related memories
        related = self.find_related(content)

        # Create bidirectional links
        for related_note in related:
            note.links.append(related_note.id)
            related_note.links.append(note.id)

        # Update dynamic index
        self.index.update(note)

        return note

    def retrieve(self, query: str, depth: int = 2):
        # Get directly matching memories
        direct = self.index.search(query)

        # Follow links to depth
        expanded = self.expand_links(direct, depth)

        return self.rank_and_filter(expanded)
```

## Mem0: Production Long-Term Memory

A scalable memory architecture addressing the fundamental limitation that LLMs "reset" outside their context window:

**Core Operations**:

```yaml
memory_operations:
  ADD:
    trigger: "New information worth remembering"
    action: "Create new memory entry with metadata"

  UPDATE:
    trigger: "Existing memory needs refinement"
    action: "Modify memory while preserving provenance"

  DELETE:
    trigger: "Memory is outdated or contradicted"
    action: "Remove with audit trail"

  NOOP:
    trigger: "Information already captured or irrelevant"
    action: "Skip storage, continue processing"
```

**Memory Manager Pattern**:

```python
class MemoryManager:
    def process_turn(self, dialogue_turn: str) -> str:
        # Decide operation via RL-fine-tuned model
        operation = self.decide_operation(dialogue_turn)

        if operation == "ADD":
            self.memory_bank.add(
                extract_facts(dialogue_turn),
                timestamp=now(),
                source="dialogue"
            )
        elif operation == "UPDATE":
            existing = self.find_related(dialogue_turn)
            self.memory_bank.update(existing, dialogue_turn)
        elif operation == "DELETE":
            outdated = self.find_contradicted(dialogue_turn)
            self.memory_bank.delete(outdated)

        return operation
```

## Agentic Context Engineering (ACE)

Treats contexts as **evolving playbooks** that accumulate and refine strategies:

```
┌─────────────────────────────────────────────────────────────┐
│                 ACE PIPELINE                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GENERATION        REFLECTION         CURATION             │
│  ┌─────────┐      ┌─────────┐       ┌─────────┐           │
│  │ Create  │ ──►  │ Evaluate│  ──►  │ Organize│           │
│  │ Strategy│      │ Success │       │ & Prune │           │
│  └─────────┘      └─────────┘       └─────────┘           │
│       ▲                                   │                 │
│       └───────────────────────────────────┘                 │
│              (Iterative Refinement)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Performance**: +10.6% on agent tasks, +8.6% on finance tasks vs baselines

**Key Innovation**: Avoids "context collapse" where iterative rewriting erodes important details

## Event-Centric Conversational Memory

Represents conversation history as short, event-like propositions:

```json
{
  "event": "user_preference_stated",
  "participants": ["user"],
  "temporal_cue": "2025-11-25T10:30:00Z",
  "proposition": "User prefers dark mode in all applications",
  "local_context": "Mentioned while customizing dashboard settings"
}
```

**Advantages over Turn-Based Memory**:

- More compact representation
- Better long-term coherence
- Survives context window limits
- Easier relevance filtering

---

## 15. Quick Reference Tables

### Memory Types Table

| Type | Example | Storage |
|------|---------|---------|
| Session | recent conversation | volatile |
| Long-Term | “user prefers metric units” | persistent |
| Episodic | “task failed at 2024-07-01” | timestamped |
| Task | plan steps | ephemeral |

### Write Criteria Table

| Condition | Required? |
|-----------|-----------|
| Stable | Yes |
| Verifiable | Yes |
| Non-sensitive | Yes |
| User confirmation | Yes for personal data |

---

# End of File
