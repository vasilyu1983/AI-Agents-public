# Agentic Reflection Workflow Template

*Purpose: Scaffold for agents that improve their reasoning, correctness, and robustness by reflecting, self-evaluating, and revising plans after each major step—field-tested in RAG, coding agents, complex QA, and self-correcting assistants.*

---

## When to Use

Use this template when:

- Building agents that should check, critique, or improve their own output before responding
- Tasks require high reliability (e.g., coding, complex reasoning, multi-step plans)
- Reducing hallucination, error propagation, or failed tool/API calls is critical
- You want agents to “think about their thinking” and adjust plans dynamically

---

## Structure

This template has 5 sections:

1. **Explicit Instructions** – direct the agent to always reflect and self-evaluate after actions
2. **Perception/Planning** – model plans and acts as in standard agent workflow
3. **Reflection Step** – after each action or output, agent must pause and review results
4. **Revision/Correction** – agent proposes improvements, corrections, or re-plans if errors/uncertainty detected
5. **Final Output** – after one or more reflection cycles, agent delivers answer or outcome

---

# TEMPLATE STARTS HERE

**Prompt Scaffold:**

```
You are an AI agent that must always reflect on your actions before finishing a task.
For each task:
- Plan and describe your next step.
- Take action (tool/API call, reasoning step, etc.).
- After each action, reflect: Did this action succeed? Is the result correct and sufficient? What could be improved?
- If any error or uncertainty, revise your plan or retry, then reflect again.
- When you are confident the answer is correct and complete, finish with:

Final Answer: [Your best, reviewed answer.]
```

---

# COMPLETE EXAMPLE

**QA with Reflection**

```
Question: What is the capital of Australia?

Plan: I'll recall what I know or search trusted sources.
Action: Recall: I think it's Sydney.
Reflection: Wait—let me double-check. Is this correct?
Action: [Search "capital of Australia"]
Observation: The search result says the capital is Canberra.
Reflection: My first answer was incorrect. I'll update my answer.

Final Answer: The capital of Australia is Canberra.
```

**Coding Agent with Reflection**

```
Task: Write a Python function that computes Fibonacci numbers.

Plan: I'll write the function using recursion.
Action:
```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```

Reflection: Is this efficient? For large n, this will be slow.
Revision: I'll use memoization to improve performance.

```python
def fib(n, memo={}):
    if n in memo: return memo[n]
    if n <= 1: return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
```

Reflection: This is now efficient and correct.

Final Answer: [Returns improved function with memoization.]

```

**Tool/API Use with Reflection**
```

Task: Get the weather for Paris.

Plan: Use WeatherAPI.
Action: [WeatherAPI "Paris"]
Observation: API error, failed to fetch.
Reflection: My action failed. I'll try an alternative API.
Action: [BackupWeatherAPI "Paris"]
Observation: Success! 20°C, sunny.
Reflection: Now I have the correct result.

Final Answer: The weather in Paris is 20°C and sunny.

```

---

## Quality Checklist

Before finalizing:
- [ ] Explicit reflection step after every major action/tool call in prompt
- [ ] Instructions require agent to revise/replan if error or uncertainty detected
- [ ] Prompt tested for both error correction and normal paths
- [ ] Output always ends with confident, reviewed Final Answer
- [ ] At least one end-to-end example for each target use case

---

*For multi-agent collaboration, see [template-multi-agent.md]. For agentic workflow patterns and checklists, see [references/agentic-patterns.md].*

