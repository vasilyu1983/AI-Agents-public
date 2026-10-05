# Query Rewriting Template

A template for LLM-assisted query rewriting to improve retrieval performance.

---

## Task

Rewrite the query to maximize retrieval relevance.  
Add synonyms and alternative phrasings **without changing intent**.

---

## Input

<USER_QUERY>

---

## Output

{
"rewritten_query": "<expanded_query>",
"keywords": ["<keyword1>", "<keyword2>"]
}

---

## Rules

- Do not add assumptions  
- Maintain original meaning  
- Keep stable, deterministic structure  
- Do not exceed 20 tokens unless necessary  

---

## Checklist

- [ ] No hallucinated facts  
- [ ] Meaning preserved  
- [ ] Improves recall@k on evaluation set  
