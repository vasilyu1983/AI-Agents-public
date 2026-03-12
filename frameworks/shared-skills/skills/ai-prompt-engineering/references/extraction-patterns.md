# Extraction Patterns

*Purpose: Deterministic structures and checklists for extracting fields, entities, spans, tables, and classifications without hallucination.*

## Contents
- Extraction contract
- Deterministic JSON extractor
- Span extraction pattern
- Classification extraction
- Table extraction pattern
- Multi-field + multi-span extraction
- Number extraction pattern
- Date extraction pattern
- Entity presence detection
- List extraction pattern
- Nested extraction pattern
- Normalization rules (optional)
- Handling missing or conflicting data
- Error patterns
- Anti-patterns
- Quick reference table

---

# 1. Extraction Contract

Extraction requires:
- A **fixed schema**
- Null defaults
- No invented data
- No transformations unless explicitly allowed
- Exact, reproducible output shape

Checklist:
- [ ] Schema declared before input  
- [ ] Null rules explicit  
- [ ] All fields accounted for  
- [ ] No added keys  
- [ ] No reasoning in output  

---

# 2. Deterministic JSON Extractor

## 2.1 Structure
```

Extract ONLY the fields in this schema.
If missing → null.
If multiple options → choose clearest or null.
No invented or inferred data.

Schema:
{
  "field1": "string|null",
  "field2": "integer|null",
  "list_field": ["string"]
}

Text:
{{input}}

```

Checklist:
- [ ] JSON only  
- [ ] Missing → null  
- [ ] No data normalization unless allowed  
- [ ] Output parses cleanly  
- [ ] Keys in the same order  

---

# 3. Span Extraction Pattern

## 3.1 Structure
```

Extract the exact text span(s) that answer the query.

Return:
{
  "spans": [
      {"chunk": "chunk-id", "text": "exact span"}
  ],
  "missing": "string|null"
}

```

Rules:
- Preserve original casing + punctuation  
- Do not modify text  
- Do not split spans unless specified  
- Only include spans present verbatim  

Checklist:
- [ ] Spans are exact quotes  
- [ ] IDs match retrieval source  
- [ ] No inferred phrases  

---

# 4. Classification Extraction

## 4.1 Structure
```

Return:
{
  "class": "A|B|C|unknown",
  "evidence": "short clause from input or null"
}

```

Rules:
- Closed set of classes  
- No “best guess”  
- If unclear → `"unknown"`  
- Evidence must appear directly in input  

Checklist:
- [ ] Class from closed set  
- [ ] Evidence verifiable  
- [ ] No synthesis  

---

# 5. Table Extraction Pattern

## 5.1 Structure
```

Return a Markdown table with these columns:
| colA | colB | colC |

Extract rows ONLY if information is explicitly present.
Missing cells → "N/A"

```

Rules:
- Column order fixed  
- Header row required  
- No extra columns  
- No fabricated rows  

Checklist:
- [ ] Row count matches evidence  
- [ ] Each cell justified by input  
- [ ] “N/A” instead of blank  

---

# 6. Multi-Field + Multi-Span Extraction

## 6.1 Structure
```

{
  "entities": [
    {
      "name": "string|null",
      "quote": "exact span|null",
      "type": "string|null"
    }
  ]
}

```

Rules:
- Each entity must map cleanly to the text  
- If partial info appears → null the rest  
- Never combine separate items into one entity  

---

# 7. Number Extraction Pattern

## 7.1 Structure
```

{
  "value": "raw_number_string|null"
}

```

Rules:
- Preserve original format  
- Do not normalize (e.g., “1,000” → keep comma)  
- If textual (“one hundred”), return raw span unless told to convert  

Checklist:
- [ ] Exact fidelity  
- [ ] No rounding  
- [ ] No conversion unless rule provided  

---

# 8. Date Extraction Pattern

## 8.1 Structure
```

{
  "date": "raw_input_value|null"
}

```

Rules:
- Keep original formatting unless schema specifies ISO  
- If multiple dates appear → return clearest or null  

Checklist:
- [ ] No guessing format  
- [ ] No future/past interpretation  
- [ ] No timezone assumptions  

---

# 9. Entity Presence Detection

## 9.1 Structure
```

{
  "present": true|false,
  "evidence": "exact quote or null"
}

```

Rules:
- Do not assume existence  
- Set false if ambiguous  
- Evidence must match verbatim  

---

# 10. List Extraction Pattern

## 10.1 Structure
```

{
  "items": ["string", ...]
}

```

Rules:
- Items must appear directly in the input  
- No inferred grouping  
- Order should match input appearance  

Checklist:
- [ ] No duplicates unless input repeats them  
- [ ] No sorting unless required  
- [ ] No summarization  

---

# 11. Nested Extraction Pattern

Use only when schema requires nested groups.

## 11.1 Structure
```

{
  "groups": [
    {
      "title": "string|null",
      "entries": ["string"]
    }
  ]
}

```

Rules:
- No merging across groups  
- If input does not imply hierarchy → flat structure or null group  

---

# 12. Normalization Rules (Optional)

Include **only if explicitly required**.

Allowed transformations:
- Lowercasing  
- Whitespace trimming  
- ISO date conversion  
- Float conversion  

Checklist:
- [ ] Transformations explicitly stated  
- [ ] No transformation of unspecified fields  

---

# 13. Handling Missing or Conflicting Data

## 13.1 Missing
```

"value": null

```

## 13.2 Conflicting
```

"value": null,
"conflict": true

```

Rules:
- Never choose a side in conflict  
- Mark explicitly when inconsistencies exist  

---

# 14. Error Patterns

## 14.1 Invalid Input
```

{"error": "invalid_input"}

```

## 14.2 Non-parseable JSON
Regenerate once. If still invalid:
```

{"error": "generation_failed"}

```

Checklist:
- [ ] No stack traces  
- [ ] No prose explanations  

---

# 15. Anti-Patterns

Avoid:
- Inferring names, dates, or numbers  
- Transforming text without rules  
- Blending multiple values into one  
- Adding fields not in schema  
- Partial prose + partial JSON  
- Guessing missing details  
- Reasoning in output  

---

# 16. Quick Reference Table

| Task | Pattern | Template |
|------|---------|----------|
| JSON extraction | Deterministic extractor | template-json-extractor.md |
| Multi-span | Span extractor | template-standard.md |
| Classification | Closed-set | template-standard.md |
| Table extraction | Table pattern | template-standard.md |
| Multi-entity | Nested extraction | template-standard.md |
