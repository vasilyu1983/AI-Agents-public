# Template – Quick Operational Prompt

*Purpose: Minimal template for fast, deterministic execution of a single task.*

## TASK
Describe the task in one sentence:
```

{{task_description}}

```

## INPUT
```

{{input_data}}

```

## RULES
- Follow the task exactly.
- Use ONLY the INPUT.
- No invented details.
- If required information is missing → state it.
- Keep reasoning hidden.
- Follow the OUTPUT FORMAT.

## OUTPUT FORMAT
Define the required output format:
```

{{output_format_spec}}

```

---

# COMPLETE EXAMPLE

### TASK
```

Rewrite the following text using short sentences.

```

### INPUT
```

The engine overheats during long-haul operations and occasionally triggers safety shutdowns.

```

### RULES
- Keep meaning.
- Short sentences.
- No added details.
- No visible reasoning.

### OUTPUT FORMAT
```

Short rewritten text.

```

### OUTPUT
```

The engine overheats during long-haul operations. It sometimes triggers safety shutdowns.

```
