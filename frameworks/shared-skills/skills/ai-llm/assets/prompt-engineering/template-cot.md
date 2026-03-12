# Chain-of-Thought (CoT) Prompt Template

*Purpose: Instantly scaffold prompts for LLMs that require multi-step reasoning, math, or explanations; maximizes answer faithfulness and transparency.*

---

## When to Use

Use this template when:

- The task requires logic, math, planning, or multi-step reasoning
- You want to make the model’s thinking explicit (“show your work”)
- Reducing hallucinations and increasing faithfulness is important
- Tasks include problem-solving, code explanation, root cause analysis, or planning

---

## Structure

This template has 3 main sections:

1. **Explicit Reasoning Cue** – tell the model to “think step by step” or similar
2. **User Question/Task** – the prompt input
3. **CoT Answer Format** – request intermediate steps, then final answer

---

# TEMPLATE STARTS HERE

**Prompt Scaffold:**

```
Q: {user_question}

A: Let's think step by step.
[Model writes out all steps, explains logic, makes calculations or deductions.]
The answer is: [final answer or result].
```

**Add explicit cues:**  

- "Explain your reasoning."
- "List each step."
- "Show all calculations before the answer."

---

# COMPLETE EXAMPLE

**Math Reasoning**

```
Q: If a train leaves at 8:00am and travels 120 miles at 40 mph, what time does it arrive?

A: Let's think step by step.
- The train speed is 40 mph.
- To go 120 miles at 40 mph: 120 / 40 = 3 hours.
- The train leaves at 8:00am, so it arrives at 8:00am + 3 hours = 11:00am.
The answer is: 11:00am.
```

**Root Cause Analysis**

```
Q: The website is down. What are the likely causes and how would you check?

A: Let's think step by step.
- First, check if the server is responding to pings.
- If not, check network connectivity and firewall rules.
- If server responds, check web server process status.
- Check for recent deploys or config changes.
The answer is: Start with server/network checks, then web server process, then configs.
```

**Code Explanation**

```
Q: What does this Python code do? [code snippet]

A: Let's think step by step.
- The code defines a function called foo(x).
- It loops from 1 to x, adding each number to a sum.
- Returns the final sum.
The answer is: It calculates the sum of all numbers from 1 to x.
```

---

## Quality Checklist

Before finalizing:

- [ ] "Let's think step by step" or explicit reasoning cue included
- [ ] Prompt requires stepwise output, not just direct answer
- [ ] At least one test case per core use (math, logic, code, planning)
- [ ] Model output includes intermediate reasoning, not just result
- [ ] Final answer always clearly marked (e.g., “The answer is:”)

---

*For tool use/agent patterns, see [template-react.md]. For structure and validation, see [references/prompt-engineering-patterns.md].*
