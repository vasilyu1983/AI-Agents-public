# Template – Standard Operational Prompt

*Purpose: Production-grade template for tasks requiring structure, constraints, and validation.*

---

## 1. TASK
Describe the task in one clear sentence:
```

{{task_description}}

```

---

## 2. INSTRUCTIONS
Follow these instructions exactly:
- Perform the task described in **TASK**.
- Use ONLY the information provided in **INPUT**.
- Apply all **CONSTRAINTS**.
- If information is missing, state it directly.
- Keep reasoning hidden.
- Follow the **OUTPUT FORMAT** exactly.
- No invented details or assumptions.
- No commentary outside the output format.

---

## 3. INPUT
```

{{input_data}}

```

---

## 4. CONSTRAINTS
Add operational constraints:
- {{constraint_1}}
- {{constraint_2}}
- {{constraint_3}}

(If unused, remove the list.)

---

## 5. OUTPUT FORMAT
Describe the exact format Claude must output:
```

{{output_format_spec}}

```

---

## 6. QUALITY CHECK
Before returning the final output, internally verify:
- Output matches the specified format.
- All constraints satisfied.
- No missing required fields.
- No reasoning exposed.
- No invented or transformed data.
- If extraction: missing items → explicitly state or return null equivalent.

(Checks stay internal; do not output them.)

---

# COMPLETE EXAMPLE

## 1. TASK
```

Rewrite the paragraph with simpler language.

```

## 2. INSTRUCTIONS
- Keep meaning.
- Short sentences.
- No new facts.
- No removed facts.
- Hidden reasoning.
- Follow output format.

## 3. INPUT
```

The device intermittently fails during peak load, causing unpredictable shutdowns across several subsystems.

```

## 4. CONSTRAINTS
- Must not exceed 2 sentences.
- Must stay factual.
- Keep technical terms.

## 5. OUTPUT FORMAT
```

Simplified rewritten text.

```

## 6. OUTPUT
```

The device sometimes fails during peak load. This causes unexpected shutdowns in several subsystems.

```

