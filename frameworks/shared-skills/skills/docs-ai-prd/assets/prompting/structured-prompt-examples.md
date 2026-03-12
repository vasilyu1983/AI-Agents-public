```markdown
# Structured Prompt Examples Template

*Purpose: Operational template with copy-paste examples of high-quality, structured prompts for GenAI/agentic coding. Use these to ensure reproducible results, format control, and clear agent instructions for common coding and documentation tasks.*

---

## When to Use

- Need examples of well-formed prompts for your LLM or agentic coding tool (Claude, Copilot, Cursor, etc.)
- Onboard team members or standardize prompt patterns for repeated use
- Train agents or workflows to produce consistent outputs (specs, code, docs, tests, etc.)

---

## Structure

Each example includes:
- Task Type
- Context Block
- Instruction Block
- Output Format Block
- (Optional) Few-shot Example

---

# TEMPLATE STARTS HERE

---

### Example 1: Feature Generation (React Component)

**Prompt**
```

You are a senior frontend developer.
Context: Building a React dashboard for managing user tasks. Status (completed/pending) must be visible and accessible.
Instruction: Generate a `TaskStatusIndicator` component that displays a green check for completed and gray circle for pending, with ARIA labels for accessibility.
Output: Only the React component code, as a Markdown code block.

```

---

### Example 2: API Endpoint (Express.js)

**Prompt**
```

You are a backend engineer.
Context: Users need an endpoint to fetch all their active tasks for the dashboard.
Instruction: Generate an Express.js route handler for `GET /tasks/active` that queries tasks by userId and returns them as JSON. Include basic error handling.
Output: Only the route handler code in a Markdown code block.

```

---

### Example 3: Unit Test Generation (Python)

**Prompt**
```

You are a Python test engineer.
Context: The following function needs comprehensive unit tests:

```python
def multiply(a, b):
    return a * b
```

Instruction: Generate pytest unit tests covering positive, zero, negative, and invalid input.
Output: Only the pytest test functions, as a Markdown code block.

```

---

### Example 4: Documentation/README Block

**Prompt**
```

You are a technical writer.
Context: The following module provides utilities for manipulating dates:

- `add_days(date, n)`
- `days_between(date1, date2)`
Instruction: Write a concise README section describing the usage of these functions, with code samples.
Output: Only the documentation block, in Markdown format.

```

---

### Example 5: Planning/Task Breakdown

**Prompt**
```

You are a tech lead planning a new dashboard feature.
Context: Goal is to display real-time user notifications in the dashboard. Users need to see new alerts within 2 seconds.
Instruction: Break down the work into clear engineering tasks (backend, frontend, agent integration, QA), list dependencies and edge cases. Output as a Markdown checklist.
Output: Only the task checklist, no implementation.

```

---

### Example 6: Few-Shot Prompt (for Standardized Output)

**Prompt**
```

Example:
Input: Generate a function to reverse a string in Python.
Output:

```python
def reverse_string(s):
    return s[::-1]
```

Now do the same for:
Input: Generate a function to check if a string is a palindrome in Python.
Output:

```

---

## Quality Checklist

Before using or sharing:
- [ ] Context, instruction, and output format clearly separated
- [ ] Only one main task per example
- [ ] Examples copy-paste directly into agent/LLM and work
- [ ] Team or agent has validated output

```
