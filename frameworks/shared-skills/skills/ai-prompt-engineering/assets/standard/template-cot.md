# Template – Hidden Reasoning (CoT) Prompt

*Purpose: Perform multi-step reasoning internally and return only the final answer in the required format.*

---

## 1. TASK
Describe the task in one clear sentence:
```

{{task_description}}

```

---

## 2. INSTRUCTIONS
Follow these instructions exactly:
- Perform all reasoning internally.
- Do NOT reveal chain-of-thought.
- Return only the final answer in the required format.
- Use ONLY the information in **INPUT**.
- If information is missing → state explicitly.
- No invented details.
- No filler language.
- Follow the **OUTPUT FORMAT** exactly.

---

## 3. INPUT
```

{{input_data}}

```

---

## 4. OUTPUT FORMAT
Define the expected output clearly:
```

{{output_format_spec}}

```

Rules:
- Format must be deterministic.
- No explanation, justification, or visible steps.

---

## 5. QUALITY CHECK (INTERNAL ONLY)
Before returning the output, verify internally:
- Reasoning is hidden.
- Output matches the declared format exactly.
- No hallucinated facts.
- No extra content.
- If the task is classification: class ∈ closed set.
- If the task requires calculation: compute internally; output only result.

(Do NOT output these checks.)

---

# COMPLETE EXAMPLE

## 1. TASK
```

Classify the issue described in the text.

```

## 2. INSTRUCTIONS
- Hidden reasoning.
- Use closed-set classes: "overheating", "mechanical_failure", "unknown".
- Use only INPUT.

## 3. INPUT
```

The engine repeatedly shuts down after long-duration missions.

```

## 4. OUTPUT FORMAT
```

{"class": "overheating|mechanical_failure|unknown"}

```

## 5. OUTPUT
```

{"class": "overheating"}

```
