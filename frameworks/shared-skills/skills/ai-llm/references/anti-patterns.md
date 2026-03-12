# Anti-Patterns

Common LLM engineering mistakes and how to prevent them. Learn from production failures.

---

## Data Leakage

**Problem:** Test set data or user content included in training set, inflating performance metrics.

**Symptoms:**
- Suspiciously high evaluation scores
- Poor performance in production vs test
- Model memorizing specific examples
- Evaluation metrics don't match user experience

**Prevention:**

```python
# Hash-based deduplication
def deduplicate_splits(train_data, test_data):
    """Ensure zero overlap between train and test"""
    train_hashes = {hash_example(ex) for ex in train_data}
    test_hashes = {hash_example(ex) for ex in test_data}

    # Check for overlap
    overlap = train_hashes & test_hashes
    if overlap:
        raise ValueError(f"Found {len(overlap)} overlapping examples")

    return train_data, test_data

# Time-based split for temporal data
def temporal_split(data, test_start_date):
    """Ensure test data is strictly after training data"""
    train = [ex for ex in data if ex.date < test_start_date]
    test = [ex for ex in data if ex.date >= test_start_date]
    return train, test

# Monitor for leakage events
def monitor_leakage():
    """Continuous monitoring for data leakage"""
    alerts = []

    # Check: Test examples appearing in training logs
    if test_examples_in_training_logs():
        alerts.append("Test data in training logs")

    # Check: User data in training pipeline
    if user_data_in_training():
        alerts.append("User data leaked into training")

    # Check: Eval metrics too good to be true
    if eval_metrics_suspicious():
        alerts.append("Suspicious evaluation scores")

    return alerts
```

**Detection:**
- Compare train/test set overlap with checksums
- Monitor evaluation vs production metrics divergence
- Audit training data provenance
- Regular data lineage reviews

**Best practices:**
- Isolate splits before any processing
- Use content hashing for deduplication
- Version all datasets with timestamps
- Automated leakage detection in CI/CD

---

## Prompt Dilution

**Problem:** Too many instructions/examples, exceeding context window, causing model to ignore key task.

**Symptoms:**
- Model ignoring critical instructions
- Inconsistent behavior across requests
- Following some instructions but not others
- Performance degrading with prompt complexity

**Prevention:**

```python
# Test prompt lengths
def validate_prompt_length(prompt, max_tokens=4000):
    """Ensure prompt fits in context window with room for response"""
    token_count = count_tokens(prompt)

    if token_count > max_tokens:
        raise ValueError(
            f"Prompt too long: {token_count} tokens (max: {max_tokens})"
        )

    # Check: Instructions are clear and prioritized
    if not has_clear_priority(prompt):
        warnings.warn("Prompt lacks clear instruction priority")

    return token_count

# Trim low-value context
def optimize_prompt(prompt, max_tokens=4000):
    """Remove low-value content to fit budget"""
    sections = parse_prompt_sections(prompt)

    # Priority order
    priorities = [
        "core_task",         # Always keep
        "constraints",       # Keep if space
        "examples",          # Trim to 2-3
        "background_context" # Remove if needed
    ]

    optimized = []
    token_budget = max_tokens

    for priority in priorities:
        section = sections.get(priority)
        if section:
            section_tokens = count_tokens(section)

            if section_tokens <= token_budget:
                optimized.append(section)
                token_budget -= section_tokens
            elif priority == "examples":
                # Keep fewer examples
                trimmed = trim_examples(section, token_budget)
                optimized.append(trimmed)
                break

    return "\n\n".join(optimized)

# Scoring metrics for prompt quality
def score_prompt_quality(prompt):
    """Evaluate prompt effectiveness"""
    scores = {
        "clarity": measure_instruction_clarity(prompt),
        "conciseness": measure_conciseness(prompt),
        "completeness": measure_completeness(prompt),
        "token_efficiency": measure_token_efficiency(prompt)
    }

    # Fail if any dimension below threshold
    if any(score < 0.7 for score in scores.values()):
        warnings.warn(f"Low prompt quality: {scores}")

    return scores
```

**Detection:**
- Monitor prompt token lengths
- Test with varying prompt complexity
- A/B test simplified vs complex prompts
- Track instruction-following metrics

**Best practices:**
- Single clear task per prompt
- Prioritize most important instructions
- Use structured format (XML tags, JSON)
- Test at max expected prompt length
- Remove redundant or conflicting instructions

---

## RAG Context Overload

**Problem:** Too many irrelevant chunks in context, degrading LLM accuracy.

**Symptoms:**
- Model ignoring relevant retrieved information
- Hallucinating despite having correct context
- Low groundedness scores
- Citing wrong sources

**Prevention:**

```python
# Tighten retrieval
def retrieve_with_threshold(query, min_score=0.7):
    """Only retrieve highly relevant chunks"""
    results = vector_db.search(query, top_k=20)

    # Filter by relevance score
    filtered = [r for r in results if r.score >= min_score]

    if len(filtered) == 0:
        # Fallback: lower threshold or return None
        filtered = results[:3]  # Top 3 as backup

    return filtered[:5]  # Max 5 chunks

# Apply rerankers
def retrieve_with_reranking(query, initial_k=20, final_k=5):
    """Two-stage retrieval with reranking"""
    # Stage 1: Fast vector search
    candidates = vector_db.search(query, top_k=initial_k)

    # Stage 2: Cross-encoder reranking
    reranked = reranker.rank(
        query=query,
        documents=[c.text for c in candidates]
    )

    # Take top-k after reranking
    return reranked[:final_k]

# Compress or filter context
def compress_context(chunks, max_tokens=2000):
    """Compress retrieved chunks to fit budget"""
    if sum(count_tokens(c) for c in chunks) <= max_tokens:
        return chunks

    # Strategy 1: Summarize each chunk
    compressed = [
        summarize_chunk(c, max_tokens=200)
        for c in chunks
    ]

    # Strategy 2: Extract key sentences
    compressed = [
        extract_key_sentences(c, max_sentences=3)
        for c in chunks
    ]

    # Strategy 3: Deduplicate information
    compressed = deduplicate_chunks(chunks)

    return compressed

# Monitor context quality
def monitor_rag_quality():
    """Track RAG performance metrics"""
    metrics = {
        "retrieval_recall": measure_recall(),      # >85%
        "groundedness": measure_groundedness(),    # >95%
        "hallucination_rate": measure_hallucination(), # <3%
        "citation_accuracy": measure_citations()  # >90%
    }

    for metric, value in metrics.items():
        if value < thresholds[metric]:
            alert(f"{metric} below threshold: {value}")

    return metrics
```

**Detection:**
- Monitor groundedness metrics
- Track hallucination rates
- Measure citation accuracy
- A/B test different retrieval strategies

**Best practices:**
- Retrieve fewer, higher-quality chunks (5-10 optimal)
- Use reranking for better relevance
- Set minimum relevance score threshold
- Compress context if needed (summarization, key sentence extraction)
- Monitor retrieval quality continuously

---

## Agentic Runaway

**Problem:** Agents stuck in loop, redundant tool calls, or unsafe escalation.

**Symptoms:**
- Agent exceeding step limits
- Repeated identical tool calls
- Oscillating between states
- High costs from redundant API calls
- Unsafe actions without proper validation

**Prevention:**

```python
# Max step limits
class Agent:
    def __init__(self, max_steps=10):
        self.max_steps = max_steps
        self.step_count = 0
        self.action_history = []

    def run(self, task):
        while self.step_count < self.max_steps:
            # Detect loops
            if self.is_looping():
                return self.handle_loop()

            action = self.plan_next_action(task)

            # Validate action
            if not self.is_action_safe(action):
                return self.escalate_unsafe_action(action)

            result = self.execute_action(action)
            self.step_count += 1
            self.action_history.append(action)

            if self.is_task_complete():
                return self.finalize()

        return self.handle_max_steps_exceeded()

    def is_looping(self):
        """Detect if agent is stuck in a loop"""
        if len(self.action_history) < 3:
            return False

        # Check: Same action repeated
        last_3 = self.action_history[-3:]
        if len(set(last_3)) == 1:
            return True

        # Check: Oscillating between two actions
        if len(set(last_3)) == 2 and last_3[0] == last_3[2]:
            return True

        return False

    def handle_loop(self):
        """Recovery from detected loop"""
        # Option 1: Try different approach
        alternative_plan = self.generate_alternative_plan()
        if alternative_plan:
            return self.execute_plan(alternative_plan)

        # Option 2: Escalate to human
        return self.escalate("Agent stuck in loop")

# Tool rate limits
class RateLimitedTool:
    def __init__(self, tool, max_calls_per_minute=10):
        self.tool = tool
        self.max_calls = max_calls_per_minute
        self.call_history = []

    def execute(self, params):
        """Execute with rate limiting"""
        # Check rate limit
        recent_calls = self.count_recent_calls(window=60)
        if recent_calls >= self.max_calls:
            raise RateLimitError(
                f"Tool {self.tool.name} rate limit exceeded"
            )

        result = self.tool.execute(params)
        self.call_history.append(time.time())
        return result

# Explicit fallback/abort paths
class SafeAgent:
    def __init__(self, fallback_strategy="escalate"):
        self.fallback_strategy = fallback_strategy

    def execute_with_fallback(self, action):
        """Execute action with fallback handling"""
        try:
            result = self.execute_action(action)

            # Validate result
            if not self.is_result_valid(result):
                return self.fallback()

            return result

        except ToolError as e:
            return self.fallback(error=e)

    def fallback(self, error=None):
        """Fallback strategy for failures"""
        if self.fallback_strategy == "escalate":
            return self.escalate_to_human(error)

        elif self.fallback_strategy == "retry_alternative":
            return self.try_alternative_approach()

        elif self.fallback_strategy == "graceful_degradation":
            return self.provide_best_effort_response()

        else:
            raise ValueError(f"Unknown fallback: {self.fallback_strategy}")
```

**Detection:**
- Monitor step count distribution
- Track repeated tool calls
- Detect oscillating patterns
- Alert on excessive retries

**Best practices:**
- Set max step limits (5-20 depending on task complexity)
- Implement loop detection
- Tool rate limiting per agent
- Explicit fallback strategies
- Human escalation for failures
- Audit trail for debugging

---

## Over-Engineering

**Problem:** Building complex systems when simple solutions would work.

**Symptoms:**
- High maintenance burden
- Difficult to debug
- Slow iteration speed
- Engineers don't understand the system

**Prevention:**

**Start simple:**
```python
# DON'T: Build multi-agent system for simple task
class ComplexSystem:
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.specialist1 = SpecialistAgent("domain1")
        self.specialist2 = SpecialistAgent("domain2")
        self.validator = ValidatorAgent()
        self.router = RouterAgent()

# DO: Single prompt for simple task
def simple_solution(query):
    prompt = f"""Answer the question concisely: {query}"""
    return llm.generate(prompt)
```

**Progressive complexity:**
1. Start with single prompt
2. Add RAG if knowledge needed
3. Add tools if actions needed
4. Add agents if orchestration needed

**Complexity checklist:**
- [ ] Can this be solved with a better prompt?
- [ ] Can this be solved with RAG?
- [ ] Can this be solved with a single agent?
- [ ] Do I really need multiple agents?

---

## Ignoring Evaluation

**Problem:** Deploying without measuring quality, leading to production failures.

**Symptoms:**
- Users reporting poor quality
- No baseline for improvement
- Can't measure impact of changes
- Regressions going unnoticed

**Prevention:**

```python
# Automated regression tests
def test_regression():
    """Run on every prompt/model change"""
    golden_set = load_golden_test_set()

    results = []
    for example in golden_set:
        prediction = llm.generate(example.input)
        score = evaluate(prediction, example.expected)
        results.append(score)

    avg_score = sum(results) / len(results)

    # Block deployment if regression
    if avg_score < QUALITY_THRESHOLD:
        raise RegressionError(f"Quality below threshold: {avg_score}")

# Multi-metric evaluation
def evaluate_llm_system(test_set):
    """Comprehensive evaluation suite"""
    metrics = {
        "accuracy": measure_accuracy(test_set),
        "hallucination_rate": measure_hallucination(test_set),
        "groundedness": measure_groundedness(test_set),
        "latency_p95": measure_latency(test_set),
        "cost_per_request": measure_cost(test_set),
        "user_satisfaction": measure_satisfaction(test_set)
    }

    # All metrics must pass
    failed = [
        m for m, v in metrics.items()
        if v < thresholds[m]
    ]

    if failed:
        raise EvaluationError(f"Failed metrics: {failed}")

    return metrics
```

**Best practices:**
- Create golden test set (100+ examples)
- Run automated tests on every change
- Track multiple metrics (not just accuracy)
- Set quality thresholds and gates
- Regular human evaluation

---

## Hard-Coded Prompts

**Problem:** Prompts embedded in code instead of versioned and tested separately.

**Symptoms:**
- Difficult to iterate on prompts
- No version history
- Can't A/B test easily
- Code changes required for prompt updates

**Prevention:**

```python
# DON'T: Hard-code prompts
def generate_response(query):
    prompt = "You are a helpful assistant. Answer: " + query
    return llm.generate(prompt)

# DO: Version and test prompts separately
class PromptManager:
    def __init__(self, version="v1"):
        self.prompts = self.load_prompts(version)

    def load_prompts(self, version):
        """Load prompts from versioned files"""
        return yaml.safe_load(
            open(f"prompts/{version}/prompts.yaml")
        )

    def get_prompt(self, name, **kwargs):
        """Get prompt template with variables"""
        template = self.prompts[name]
        return template.format(**kwargs)

# Usage
prompt_manager = PromptManager(version="v2")
prompt = prompt_manager.get_prompt("qa_assistant", query=query)
response = llm.generate(prompt)
```

**Best practices:**
- Store prompts in separate files (YAML, JSON)
- Version control prompts
- CI/CD for prompt testing
- A/B testing framework
- Prompt template system with variables

---

## Missing Observability

**Problem:** No logging/tracing, making debugging impossible.

**Symptoms:**
- Can't debug production issues
- No visibility into failures
- Can't measure performance
- User complaints with no context

**Prevention:**

```python
# Comprehensive logging
import structlog

logger = structlog.get_logger()

def llm_call_with_logging(prompt, trace_id):
    """LLM call with full observability"""
    start_time = time.time()

    logger.info(
        "llm_call_start",
        trace_id=trace_id,
        prompt_tokens=count_tokens(prompt),
        model=model_name
    )

    try:
        response = llm.generate(prompt)

        logger.info(
            "llm_call_success",
            trace_id=trace_id,
            latency_ms=(time.time() - start_time) * 1000,
            response_tokens=count_tokens(response),
            cost=calculate_cost(prompt, response)
        )

        return response

    except Exception as e:
        logger.error(
            "llm_call_failed",
            trace_id=trace_id,
            error=str(e),
            latency_ms=(time.time() - start_time) * 1000
        )
        raise

# Distributed tracing
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("rag_query")
def rag_query(query, trace_id):
    """RAG with distributed tracing"""
    span = trace.get_current_span()
    span.set_attribute("query", query)
    span.set_attribute("trace_id", trace_id)

    # Retrieval span
    with tracer.start_as_current_span("retrieval"):
        chunks = retrieve(query)
        span.set_attribute("chunks_retrieved", len(chunks))

    # Generation span
    with tracer.start_as_current_span("generation"):
        response = generate(query, chunks)
        span.set_attribute("response_length", len(response))

    return response
```

**Best practices:**
- Log all LLM calls with full context
- Distributed tracing with trace IDs
- Structured logging (JSON)
- Metrics dashboard (latency, cost, quality)
- Error tracking and alerting

---

## Related Resources

- **[Common Design Patterns](common-design-patterns.md)** - Correct implementation patterns
- **[Production Checklists](production-checklists.md)** - Pre-deployment validation
- **[LLMOps Best Practices](llmops-best-practices.md)** - Operational standards
- **[Evaluation Patterns](eval-patterns.md)** - Quality measurement and testing

---
