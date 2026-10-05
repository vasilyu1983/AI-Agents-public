# Grounding Template

Ensures that generation stays strictly tied to retrieved context.

---

## System

You must use *only* the evidence provided in the context block.  
If the answer is not contained in the context, output:  
**"Not found in the documents."**

---

## Input

Context:
<CONTEXT_BLOCK>

Query:
<USER_QUERY>

---

## Output Requirements

- No external facts  
- No speculation  
- Use citations referencing chunk index  
- Format:

{
"answer": "<text>",
"sources": ["<chunk-id-1>", "<chunk-id-2>"]
}

---

## Checklist

- [ ] All claims traceable  
- [ ] Refusal used when answer not in context  
- [ ] JSON-safe output  
