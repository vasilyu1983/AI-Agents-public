# Template – Deterministic JSON Extractor

*Purpose: Produce EXACT structured output from text using a fixed JSON schema.*

---

## 1. TASK
Describe the extraction task in one sentence:
```

{{task_description}}

```

---

## 2. INPUT
Provide the raw text to extract from:
```

{{input_text}}

```

---

## 3. RULES
Follow these rules exactly:

### Extraction Rules
- Extract ONLY the fields defined in the schema.
- Use ONLY information present in the INPUT.
- No invented, inferred, or transformed data.
- If a field is missing → return null.
- If multiple candidates exist → choose clearest or null.

### Formatting Rules
- Output MUST be valid JSON.
- No comments.
- No trailing commas.
- No text outside the JSON object.
- Field order must match the schema.

### Reasoning Rules
- Keep reasoning hidden.
- Return ONLY the JSON.

---

## 4. OUTPUT SCHEMA
Define the exact JSON schema to use:
```

{
  "field1": "string|null",
  "field2": "string|null",
  "field3": "integer|null",
  "list_field": ["string"]
}

```

Modify schema as needed.

---

## 5. OUTPUT FORMAT
Return ONLY the completed JSON object:
```

{{json_result}}

```

---

## 6. QUALITY CHECK (INTERNAL ONLY)
Before responding, verify:
- JSON is valid and parseable.
- All schema fields included.
- No extra fields.
- No missing quotes.
- Nulls correctly applied.
- No hallucinated content.
- No reasoning or prose.

(Do NOT output this checklist.)

---

# COMPLETE EXAMPLE

## 1. TASK
```

Extract customer complaint data.

```

## 2. INPUT
```

On March 2, Sarah Lopez reported that her charger overheats during use.

```

## 3. SCHEMA
```

{
  "name": "string|null",
  "date": "string|null",
  "issue": "string|null"
}

```

## 4. OUTPUT
```

{
  "name": "Sarah Lopez",
  "date": "March 2",
  "issue": "charger overheats"
}

```
