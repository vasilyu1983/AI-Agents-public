# Grounding Checklists for RAG Systems

Tools and patterns for ensuring model outputs remain tied to retrieved evidence, preventing hallucinations and ensuring context compression.

---

## 1. Context Compression & Budgeting

**Use when context window is tight.**

### Compression Strategies

1. **Merge adjacent chunks** - Combine semantically related chunks
2. **Deduplicate repeated sentences** - Remove redundant information
3. **Summarize long chunks (LLM distillation)** - Use smaller model to compress
4. **Prioritize by relevance score** - Include highest-scoring chunks first
5. **Structure context as sections** - Group by topic/source

### Token Budget Management

- Calculate token budget: `model_context_window - prompt_tokens - max_output_tokens`
- Reserve 20-30% buffer for formatting overhead
- Track actual usage vs budget
- **Example:** Claude 200k context → reserve ~150k for retrieved content

### Context Optimization Checklist

- [ ] Fits within model's token budget
- [ ] Includes top-ranked chunks
- [ ] Avoids filler / irrelevant content
- [ ] Document titles preserved
- [ ] Compression tested on eval set (no quality degradation)

---

## 2. Grounding Enforcement Pattern

### Prompt Constraints

Use ONLY the provided context.
If the answer is not found in the context, respond:
"Not found in the documents."

### Required

- No external facts
- No speculation
- All claims must cite chunks

### Reinforcement Techniques

- Add **negative examples** in prompt (show what NOT to do)
- Add citations requirement (force explicit references)
- Apply reranker with **answerability scoring**
- Use constrained decoding or structured outputs

### Grounding Enforcement Checklist

- [ ] Instructions explicitly forbid outside knowledge
- [ ] Tested on "not answerable" cases
- [ ] Model declines when context insufficient
- [ ] No hallucinated facts in outputs

---

## 3. Citation Pattern

### Format

Answer: <text>
Sources:

[1] <chunk_metadata>
[2] <chunk_metadata>

### Checklist

- [ ] All claims traceable to source chunk  
- [ ] Chunk IDs stable  
- [ ] No fabricated citations  

---

## 4. Context Quality Checklist

- [ ] Top-ranked chunks relevant  
- [ ] No noisy or empty chunks  
- [ ] Context fits within token budget  
- [ ] Ordered by relevance  
- [ ] Headings/titles preserved  

---

## 5. Hallucination Suppression Rules

Add negative constraints:

- "Do not guess."
- "If unsure, say: 'I don't know.'"
- "Do not infer facts not explicitly provided."

---

## 6. Answerability Validation Pattern

Use before generation:

1. Add classifier or shallow LLM to test if context is answerable  
2. If unanswerable → return safe response  
3. If answerable → generate output  

---

## 7. Grounding Final Checklist

- [ ] Output references retrieved evidence
- [ ] No ungrounded claims
- [ ] Declines appropriately when context insufficient
- [ ] Citations are accurate and traceable
- [ ] Context fits within token budget
- [ ] Tested on edge cases (unanswerable questions)

---

## Related Resources

- [Advanced RAG Patterns](advanced-rag-patterns.md) - Context compression strategies
- [Pipeline Architecture](pipeline-architecture.md) - Where grounding fits in the pipeline
- [Retrieval Patterns](retrieval-patterns.md) - Improving context relevance
- [../assets/context/template-grounding.md](../assets/context/template-grounding.md) - Implementation template
