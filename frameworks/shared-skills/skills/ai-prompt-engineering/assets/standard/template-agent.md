# Template – Agent / Tool-Use Prompt

*Purpose: Deterministic agent workflow for planning, deciding on tool use, and producing final answers.*

---

## 1. TASK
Describe the task in one sentence:
```

{{task_description}}

```

---

## 2. AVAILABLE TOOLS
List only the tools relevant to this task (or leave empty if none are used):
```

{{tool_spec_block}}

```

Example format (adjust as needed):
```

Tools:

- search_tool(query: string)
- database_lookup(id: string)

```

---

## 3. INSTRUCTIONS
Follow these instructions exactly:
- Perform planning **before** any action.
- Use **only one tool call per turn**.
- If a tool is required → create a plan → call the tool via the **Action** block.
- If a tool is NOT required → create a plan → return the answer with **Action = null**.
- Keep reasoning hidden.
- Use ONLY the data provided in tool results or INPUT.
- No invented details.
- No commentary outside the required output structure.

---

## 4. INPUT
```

{{input_data}}

```

---

## 5. OUTPUT FORMAT
Produce output in this exact structure:
```

Plan:

- step 1
- step 2
- step 3

Action:
{ "tool": "tool_name", "input": { ... } } | null

Answer:
"final answer string or null"

```

Rules:
- **If Action ≠ null → Answer must be null.**  
- **If Action = null → Answer must contain the final response.**  
- Plan steps must be short, imperative verbs only (e.g., "lookup", "extract", "compare").  
- No visible reasoning.

---

## 6. QUALITY CHECK (INTERNAL ONLY)
Before responding, internally verify:
- Plan logically leads to the action or answer.
- Only one tool call is used.
- Action object matches the declared tool signatures.
- Answer appears only when no tool is called.
- No reasoning leaked.
- No hallucinated fields.

(Do NOT output these checks.)

---

# COMPLETE EXAMPLE

## 1. TASK
```

Find the price of the product ID provided by the user.

```

## 2. AVAILABLE TOOLS
```

Tools:

- get_product_data(id: string)

```

## 3. INPUT
```

product_id: "A-19"

```

## 4. OUTPUT FORMAT (required)
```

Plan:

- step 1
- step 2
- step 3

Action:
{ "tool": "tool_name", "input": { ... } } | null

Answer:
"final answer string or null"

```

## 5. OUTPUT
```

Plan:

- verify product ID exists
- call get_product_data with provided ID
- inspect returned fields

Action:
{
  "tool": "get_product_data",
  "input": { "id": "A-19" }
}

Answer:
null

```

