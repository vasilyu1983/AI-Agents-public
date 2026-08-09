# Context Packing Template

A deterministic method for assembling the final context block fed into the LLM.

---

## 1. Strategy

context_window: <max_tokens>
max_chunks: 5
ordering: "relevance"
dedupe: true
preserve_section_titles: true

---

## 2. Context Assembly Steps

1. Sort retrieved chunks by score  
2. Remove duplicates  
3. Add section titles  
4. Concatenate with separators  
5. Stop when reaching token budget  

---

## 3. Template Format

<START_CONTEXT>
[1] <section_title>
<chunk_text>
[2] <section_title>
<chunk_text>
...
<END_CONTEXT>

---

## 4. Checklist

- [ ] Fits within model token limit  
- [ ] Ordered by relevance  
- [ ] Section titles preserved  
- [ ] Clean concatenation (no markup noise)  
