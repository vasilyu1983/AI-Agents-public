# ReAct (Reason + Act) Prompt Template

*Purpose: Scaffold LLM prompts that interleave reasoning and tool/API use—enabling complex workflows, tool-based retrieval, and multi-step planning in agentic and RAG systems.*

---

## When to Use

Use this template when:

- The LLM must reason through steps and take actions (API/tool calls, searches, etc)
- The workflow requires alternating between thought, action, observation, and next steps
- Use cases include multi-hop QA, research, web search, code exec, or agentic plans

---

## Structure

This template has 5 main sections:

1. **Explicit Instructions** – clarify the Reason+Act workflow
2. **User Question/Task** – prompt input
3. **ReAct Loop Format** – repeatable [Thought] → [Action] → [Observation] sequence
4. **Final Answer** – LLM delivers answer only after reasoning and tool steps are done
5. **Error/Fallback Handling** – guide model to replan or escalate if actions fail

---

# TEMPLATE STARTS HERE

**Prompt Scaffold:**

```
You are an AI assistant that can think step by step and use tools or APIs to solve tasks.
Follow this format:

Question: {user_question}

Thought: [Describe what you want to do next.]
Action: [If needed, specify the tool, API, or search and inputs.]
Observation: [Result/output from tool or previous action.]

(Repeat Thought/Action/Observation as needed...)

When you have enough information, finish with:

Final Answer: [Your answer to the original question.]
```

---

# COMPLETE EXAMPLES

**Web Search ReAct**

```
Question: Who is the CEO of OpenAI?

Thought: I need to look up the latest information.
Action: [Search "OpenAI CEO"]
Observation: The search result says Sam Altman is the CEO of OpenAI.

Thought: I have found the answer.
Final Answer: The CEO of OpenAI is Sam Altman.
```

**RAG + Tool Example**

```
Question: What is the warranty policy for product X?

Thought: I need to search the company knowledge base.
Action: [RAG_Search "product X warranty policy"]
Observation: The retrieved chunk says "Product X has a 2-year limited warranty."

Thought: The answer is now clear.
Final Answer: Product X has a 2-year limited warranty.
```

**Multi-Step/Agentic Example**

```
Question: What’s the weather in Paris and send it to my email?

Thought: First, I need to look up the current weather in Paris.
Action: [WeatherAPI "Paris"]
Observation: It's 22°C, partly cloudy.

Thought: Now, I need to send this info via email.
Action: [SendEmail to="user@example.com" body="Weather in Paris is 22°C, partly cloudy."]
Observation: Email sent.

Final Answer: I checked the weather in Paris (22°C, partly cloudy) and emailed it to you.
```

**Error Handling/Fallback**

```
Observation: The API failed to return results.

Thought: The tool failed, so I will try an alternate approach or inform the user.
Action: [Alternative_Tool or escalate]
Observation: Alternate tool also failed.

Final Answer: I was unable to retrieve the information due to a system error.
```

---

## Quality Checklist

Before finalizing:

- [ ] Explicit “Thought/Action/Observation” loop present in the prompt
- [ ] Instructions clarify how and when to use tools/APIs
- [ ] Prompt tested for both successful and failed tool calls
- [ ] Output always ends with “Final Answer” for clarity
- [ ] Handles action failures with fallback/escalation logic

---

*For stepwise reasoning, see [template-cot.md]. For more agentic orchestration, see [agentic-workflows/]. For prompt anti-patterns, see [references/prompt-engineering-patterns.md].*
