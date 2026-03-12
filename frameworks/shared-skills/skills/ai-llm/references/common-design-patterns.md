# Common Design Patterns

Copy-paste ready examples of fundamental LLM design patterns for prompting, retrieval, and agentic workflows.

---

## Chain-of-Thought (CoT) Prompting

**Purpose:** Improve reasoning by forcing the model to show its work step-by-step.

**When to use:**
- Math and logical reasoning problems
- Complex multi-step tasks
- When intermediate steps aid understanding
- Debugging model reasoning

**Pattern:**

```text
Q: What's 17 times 24?
A: Let's think step by step. 17 x 20 = 340. 17 x 4 = 68. 340 + 68 = 408. The answer is 408.
```

**Implementation:**

```python
system_prompt = """
You are a helpful assistant. When solving problems:
1. Break down the problem into steps
2. Show your work for each step
3. Provide the final answer clearly
"""

user_prompt = """
Q: What's 17 times 24?
A: Let's think step by step.
"""
```

**Best practices:**
- Use "Let's think step by step" or similar trigger phrase
- Validate intermediate steps make sense
- Can combine with few-shot examples
- Consider extracting just the final answer for user display

**Variants:**
- **Zero-shot CoT:** Just add "Let's think step by step"
- **Few-shot CoT:** Provide examples with reasoning chains
- **Self-consistency CoT:** Sample multiple reasoning paths, majority vote on answer

---

## ReAct (Reason + Act) Pattern

**Purpose:** Combine reasoning with action execution for agentic workflows.

**When to use:**
- Tasks requiring external tool use
- Multi-step workflows with dependencies
- When observations inform next actions
- Agent-based systems

**Pattern:**

```text
User: Summarize this article and email it to Alice.

Agent:
[Thought] I need to read and summarize the article, then send an email.
[Action] Read article from URL
[Observation] Article is about climate change impacts on agriculture.

[Thought] Now I'll compose a summary.
[Action] Compose summary
[Observation] Summary created: "The article discusses..."

[Thought] Now I can send the email.
[Action] Send email to Alice with summary
[Observation] Email sent successfully.

[Answer] I've read the article about climate change and agriculture, created a summary, and sent it to Alice via email.
```

**Implementation:**

```python
system_prompt = """
You are an agent that can use tools to complete tasks.
For each step, provide:
- Thought: Your reasoning about what to do next
- Action: The tool/action to execute
- Observation: The result of the action

Continue until you have enough information to answer, then provide [Answer].
"""

# Agent loop
while not done:
    response = llm.generate(history + context)

    if "[Thought]" in response:
        thought = extract_thought(response)
        log_thought(thought)

    if "[Action]" in response:
        action = extract_action(response)
        result = execute_tool(action)
        history.append({"observation": result})

    if "[Answer]" in response:
        final_answer = extract_answer(response)
        done = True
```

**Best practices:**
- Clear tool descriptions in system prompt
- Parse structured action format reliably
- Set max iteration limits to prevent loops
- Log full trajectory for debugging
- Validate action parameters before execution

**Variants:**
- **ReWOO:** Reason Without Observation (plan all steps upfront)
- **Reflexion:** Add self-reflection and error correction
- **Plan-and-Execute:** Separate planning and execution phases

---

## RAG Pipeline (Minimal)

**Purpose:** Ground LLM responses in retrieved knowledge to reduce hallucination.

**When to use:**
- Answering questions from documents
- Current/dynamic knowledge required
- Factual accuracy critical
- Private/proprietary knowledge bases

**Pattern:**

```text
1. Split raw docs (chunking, overlap=50 tokens)
2. Embed chunks (e.g., BGE-large, ada-002)
3. Store in vector DB (e.g., Pinecone, Qdrant)
4. At query: embed question, retrieve top-k, construct context window
5. Generate answer, citing sources (if possible)
6. Evaluate: precision, recall, faithfulness, latency
```

**Implementation:**

```python
# Indexing phase
def build_index(documents):
    chunks = []
    for doc in documents:
        # Chunk with overlap
        doc_chunks = chunk_text(
            doc.content,
            chunk_size=400,
            overlap=50
        )
        chunks.extend(doc_chunks)

    # Embed and store
    embeddings = embedding_model.embed(chunks)
    vector_db.upsert(
        ids=[c.id for c in chunks],
        vectors=embeddings,
        metadata=[c.metadata for c in chunks]
    )

# Query phase
def rag_query(question):
    # Embed question
    query_embedding = embedding_model.embed(question)

    # Retrieve top-k
    results = vector_db.search(
        query_embedding,
        top_k=5,
        include_metadata=True
    )

    # Construct context
    context = "\n\n".join([
        f"[Source {i+1}] {r.text}"
        for i, r in enumerate(results)
    ])

    # Generate answer with citation
    prompt = f"""
    Answer the question based on the context below.
    Cite sources using [Source N] format.

    Context:
    {context}

    Question: {question}

    Answer:
    """

    answer = llm.generate(prompt)

    return {
        "answer": answer,
        "sources": [r.metadata for r in results]
    }
```

**Best practices:**
- Chunk size: 200-400 tokens (optimal for most cases)
- Overlap: 10-20% of chunk size
- Retrieve: 5-10 chunks typical (tune based on context window)
- Add reranking step for better relevance
- Track source citations for verification
- Monitor retrieval recall (>85% recommended)

**Variants:**
- **Hybrid RAG:** Combine semantic (vector) + keyword (BM25) search
- **Contextual RAG:** Add context to chunks before embedding (Anthropic 2024)
- **Agentic RAG:** Iterative retrieval with query rewriting and filtering

---

## Agentic Planning Loop

**Purpose:** Multi-step problem solving with perception, planning, and action.

**When to use:**
- Complex tasks requiring multiple tools
- Dynamic environments requiring adaptation
- Long-horizon planning tasks
- Autonomous agent behavior

**Pattern:**

```text
Perceive → Plan (with tools and memory) → Act (API/tool call) → Observe → Learn/Update state
```

**Implementation:**

```python
class Agent:
    def __init__(self, llm, tools, memory):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.state = {}

    def run(self, task, max_steps=10):
        for step in range(max_steps):
            # Perceive current state
            perception = self.perceive()

            # Plan next action
            plan = self.plan(task, perception)

            # Execute action
            result = self.act(plan)

            # Observe outcome
            observation = self.observe(result)

            # Update state and memory
            self.learn(observation)

            # Check if task complete
            if self.is_task_complete(task):
                return self.generate_response()

        return "Task not completed within step limit"

    def perceive(self):
        """Gather current state and context"""
        return {
            "memory": self.memory.retrieve_relevant(self.state),
            "state": self.state,
            "available_tools": [t.name for t in self.tools]
        }

    def plan(self, task, perception):
        """Generate plan for next action"""
        prompt = f"""
        Task: {task}
        Current State: {perception['state']}
        Available Tools: {perception['available_tools']}
        Recent Memory: {perception['memory']}

        What should I do next? Provide:
        1. Reasoning for next step
        2. Tool to use (or 'respond' if done)
        3. Tool parameters
        """
        return self.llm.generate(prompt)

    def act(self, plan):
        """Execute planned action"""
        if plan.tool == "respond":
            return plan.response

        tool = self.get_tool(plan.tool)
        return tool.execute(plan.parameters)

    def observe(self, result):
        """Process action result"""
        return {
            "success": result.success,
            "data": result.data,
            "errors": result.errors
        }

    def learn(self, observation):
        """Update state and memory"""
        self.state.update(observation.get("data", {}))
        self.memory.store(observation)
```

**Best practices:**
- Set max step limits to prevent infinite loops
- Clear termination criteria
- Tool timeout and error handling
- State persistence for recovery
- Logging for debugging and evaluation

**Key considerations:**
- **Step limits:** 5-20 steps typical (depends on task complexity)
- **Memory management:** Store only relevant information
- **Error recovery:** Retry failed actions with different approach
- **Safety:** Approval gates for high-risk actions
- **Observability:** Full trajectory logging for debugging

---

## Advanced Patterns

### Self-Reflection Pattern

**Purpose:** Agent critiques its own output and iteratively improves.

```python
def self_reflection_loop(task, max_iterations=3):
    response = initial_attempt(task)

    for i in range(max_iterations):
        critique = llm.generate(f"""
        Task: {task}
        Response: {response}

        Critique this response:
        - What's correct?
        - What's missing?
        - What could be improved?
        """)

        if critique.is_satisfactory():
            break

        response = llm.generate(f"""
        Task: {task}
        Previous attempt: {response}
        Critique: {critique}

        Provide an improved response addressing the critique.
        """)

    return response
```

### Multi-Agent Collaboration

**Purpose:** Specialized agents collaborate on complex tasks.

```python
def multi_agent_collaboration(task):
    # Researcher gathers information
    research = researcher_agent.run(
        f"Research background for: {task}"
    )

    # Planner creates strategy
    plan = planner_agent.run(
        f"Create plan for: {task}\nResearch: {research}"
    )

    # Executor implements solution
    result = executor_agent.run(
        f"Execute: {plan}\nContext: {research}"
    )

    # Critic evaluates quality
    critique = critic_agent.run(
        f"Evaluate: {result}"
    )

    return {
        "result": result,
        "research": research,
        "plan": plan,
        "evaluation": critique
    }
```

### Retrieval-Augmented Generation with Reranking

**Purpose:** Improved RAG with two-stage retrieval.

```python
def rag_with_reranking(query, top_k=5, rerank_k=20):
    # Stage 1: Fast retrieval (vector search)
    candidates = vector_db.search(
        embed(query),
        top_k=rerank_k  # Get more candidates
    )

    # Stage 2: Rerank with cross-encoder
    reranked = reranker.rank(
        query=query,
        documents=[c.text for c in candidates]
    )

    # Take top-k after reranking
    top_results = reranked[:top_k]

    # Generate with reranked context
    context = "\n\n".join([r.text for r in top_results])
    answer = llm.generate(f"""
    Context: {context}
    Question: {query}
    Answer:
    """)

    return answer
```

---

## Related Resources

- **[Prompt Engineering Patterns](prompt-engineering-patterns.md)** - Detailed prompt design techniques
- **[Agentic Patterns](agentic-patterns.md)** - Advanced agent architectures
- **[RAG Best Practices](rag-best-practices.md)** - Deep dive on retrieval-augmented generation
- **[Anti-Patterns](anti-patterns.md)** - Common mistakes to avoid

---
