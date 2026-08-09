# Eval Platform Selection

Use this reference when choosing an evaluation platform or assembling a toolchain for agent evaluation. It covers the dominant ecosystem, when to choose or skip each tool, and a decision tree for common setups.

Do not treat install snippets as canonical version pins — verify current versions against official docs before use.

## Contents

- [Platform Comparison](#platform-comparison)
- [Per-Platform Details](#per-platform-details)
- [Decision Tree](#decision-tree)
- [Combining Platforms](#combining-platforms)
- [Selection Rule](#selection-rule)

---

## Platform Comparison

| Platform | Model | Best Fit | Skip When |
|---|---|---|---|
| **DeepEval** | Open source (MIT) | pytest-style unit evaluations, 14+ built-in metrics (faithfulness, hallucination, RAG, agent goal, tool use, etc.), CI integration, assertion-style test authoring | You need hosted evaluation management, fine-grained trace replay, or a GUI-first workflow |
| **Inspect AI** | Open source (MIT), UK AISI | Scenario-driven agent evaluations, sandboxed agent execution, composable tasks and solvers, safety and capability evaluations | You need a lightweight CI gate or a RAG-specific metric suite |
| **Braintrust** | Commercial (hosted) | Managed evaluation platform, experiment tracking, human-in-the-loop review, scoring UI, SDK for Python/TS | You need fully on-premise or self-hosted infra, or budget is constrained |
| **Ragas** | Open source (Apache 2.0) | RAG pipeline metrics (answer relevancy, faithfulness, context precision/recall), multi-turn RAG, LLM-as-judge for retrieval quality | Your agent is not retrieval-augmented; use DeepEval or Inspect AI instead |
| **Promptfoo** | Open source (MIT) | Config-driven regression suites, red-team attack packs, refusal testing, side-by-side model comparisons, CI-friendly YAML | You need deep trace visibility or RAG-specific metrics |
| **OpenAI Evals** | Open source (MIT) | Model-graded evaluations, OpenAI model benchmarking, pre-built evaluation templates, large community of existing evals | You are not using OpenAI models, or need tool-trace and workflow-level coverage. **Note:** The hosted OpenAI Platform Evals UI is being shut down (read-only Oct 31 2026, full shutdown Nov 30 2026). The open-source `openai/evals` package and Evals API continue. |
| **Langfuse** | Open source + cloud (MIT core) | Production tracing, session replay, cost tracking, online evaluation triggers, LLM-as-judge on live traffic | You only need offline pre-deployment testing with no production traffic |

---

## Per-Platform Details

### DeepEval

**When to choose:** Your team writes Python tests and wants evaluation coverage that lives next to unit tests in CI. Strong for agents with tool calls, multi-turn conversations, RAG retrieval, and output grading across 14+ metric types. **v4.0 (2026)** adds agent-native evaluation with Task Completion, Tool Correctness, Step Efficiency, and Plan Quality metrics via `@observe` tracing; supports iterative patch-eval-retry workflows.

**When to skip:** You need a hosted dashboard, trace-first debugging, or non-Python stack.

**Install + minimal example:**

```bash
pip install deepeval
```

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, ToolCorrectnessMetric

def test_agent_answer():
    test_case = LLMTestCase(
        input="What is the capital of France?",
        actual_output="Paris",
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])
```

**Docs:** https://deepeval.com/docs/metrics-introduction

---

### Inspect AI (UK AISI)

**When to choose:** You are evaluating a coding agent, autonomous task agent, or safety-critical system. Inspect provides sandboxed Docker/subprocess execution, composable task and solver primitives, and scenario-driven evaluation design. It is the reference framework for capability and safety evaluations in the UK AISI tradition.

**When to skip:** You need a quick CI gate from YAML config, or your evaluation is purely RAG metric-based.

**Install + minimal example:**

```bash
pip install inspect-ai
```

```python
from inspect_ai import task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate

@task
def capitals():
    # returns a Task object for the inspect runner
    from inspect_ai import Task
    return Task(
        dataset=[Sample(input="Capital of France?", target="Paris")],
        solver=generate(),
        scorer=match(),
    )
```

Run with: `inspect run capitals.py`

**Docs:** https://inspect.aisi.org.uk/

---

### Braintrust

**When to choose:** Your team wants a managed experiment-tracking platform with a scoring UI, human-review queues, and SDK support in Python and TypeScript. Good for organizations that need evaluation lineage and team-level visibility without running their own infra.

**When to skip:** You need fully self-hosted deployment, have strict data-residency requirements, or the project is early-stage with no budget for managed tooling.

**Install + minimal example:**

```bash
pip install braintrust
```

```python
import braintrust

experiment = braintrust.init(project="my-agent", api_key="...")
experiment.log(
    input="What is 2+2?",
    output="4",
    expected="4",
    scores={"exact_match": 1.0},
)
```

**Docs:** https://www.braintrust.dev/docs

---

### Ragas

**When to choose:** Your system is retrieval-augmented (RAG pipeline). Ragas provides purpose-built metrics — answer relevancy, faithfulness, context precision, context recall — graded via LLM-as-judge against the retrieved context.

**When to skip:** Your agent does not retrieve documents. Applying Ragas metrics to non-RAG agents produces misleading results.

**Install + minimal example:**

```bash
pip install ragas
```

```python
from ragas import evaluate as ragas_evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

data = Dataset.from_dict({
    "question": ["What is RAG?"],
    "answer": ["Retrieval-Augmented Generation combines retrieval with generation."],
    "contexts": [["RAG is a technique that retrieves documents before generating text."]],
    "ground_truth": ["RAG retrieves documents and uses them during generation."],
})

result = ragas_evaluate(data, metrics=[faithfulness, answer_relevancy])
```

**Docs:** https://docs.ragas.io/

---

### Promptfoo

**When to choose:** Your team iterates quickly on prompts and wants diffable YAML evaluation configs checked into source control. Strong for red-team packs, refusal suites, and side-by-side model comparisons in CI.

**When to skip:** You need deep trace-level debugging or RAG-specific metrics.

**Install + minimal example:**

```bash
npm install -g promptfoo
```

```yaml
# promptfooconfig.yaml
prompts:
  - "Answer this question: {{question}}"
providers:
  - openai:gpt-5.4
tests:
  - vars:
      question: "What is the capital of France?"
    assert:
      - type: contains
        value: Paris
```

```bash
promptfoo eval
```

**Docs:** https://www.promptfoo.dev/docs/

---

### OpenAI Evals

**Platform deprecation notice:** The hosted OpenAI Platform Evals UI (at platform.openai.com) is being shut down — read-only on October 31, 2026, full shutdown November 30, 2026. The open-source `openai/evals` Python package and the Evals API remain available.

**When to choose:** You use OpenAI models and want model-graded evaluations, a large library of pre-built evaluation templates, or you are contributing to a shared benchmark. Use the open-source package or API directly rather than the Platform UI.

**When to skip:** You are not using OpenAI models, or you need tool-trace coverage and workflow-level grading beyond what model-graded evaluations provide. If you relied on the Platform Evals UI, migrate to Promptfoo (OpenAI-recommended migration path), DeepEval, or Braintrust.

**Install + minimal example:**

```bash
pip install evals
```

```bash
oaieval gpt-5.4 hellaswag
```

**Docs:** https://github.com/openai/evals

---

### Langfuse

**When to choose:** You need production observability — tracing LLM calls, tracking costs, replaying sessions, and triggering online evaluations on live traffic. Langfuse pairs well with an offline evaluation framework (DeepEval, Ragas) to provide end-to-end coverage from development through production. **2026 additions:** native OpenTelemetry ingestion (supports LangGraph, Pydantic AI, smolagents, CrewAI, Strands Agents), code evaluators writeable directly in the Langfuse UI (JSON schema validation, exact match, required tool argument checks, custom Python), and MCP server for agent-native interaction.

**When to skip:** You only need offline pre-deployment testing with no live traffic. Langfuse alone is not an offline evaluation framework.

**Install + minimal example:**

```bash
pip install langfuse
```

```python
from langfuse import Langfuse

lf = Langfuse()
trace = lf.trace(name="agent-run")
span = trace.span(name="llm-call", input={"prompt": "Hello"}, output={"text": "Hi"})
span.end()
```

**Docs:** https://langfuse.com/docs

---

## Decision Tree

```text
What is your primary evaluation need?
  ├─ RAG pipeline metrics (faithfulness, context recall, relevancy)?
  │   └─ Ragas
  │
  ├─ Coding agent or sandboxed autonomous agent (safety/capability)?
  │   └─ Inspect AI
  │
  ├─ CI gate from YAML config, red-team packs, refusal suites?
  │   └─ Promptfoo
  │
  ├─ Production trace visibility + online evaluations on live traffic?
  │   └─ Langfuse (pair with DeepEval for offline metrics)
  │
  ├─ pytest-style unit evaluations in Python CI with 14+ built-in metrics?
  │   └─ DeepEval
  │
  ├─ Managed platform with experiment tracking, scoring UI, human review?
  │   └─ Braintrust
  │
  └─ Standardizing on OpenAI models, need model-graded evals or benchmarks?
      └─ OpenAI Evals (open-source package/API; Platform UI deprecated Nov 2026)
```

---

## Combining Platforms

These tools are not mutually exclusive. Common pairings:

- **Offline + online:** DeepEval (CI) + Langfuse (production tracing)
- **RAG full stack:** Ragas (retrieval metrics) + Langfuse (tracing)
- **Safety-critical agents:** Inspect AI (sandboxed evaluation) + Promptfoo (red-team pack)
- **Managed with metrics:** Braintrust (tracking) + DeepEval (metric library)

---

## Selection Rule

Start with the failure mode you need to observe, not the tool:

1. Regressions in retrieval quality → Ragas first.
2. Regressions in agent behavior and safety → Inspect AI first.
3. Regressions in prompt outputs caught in CI → Promptfoo first.
4. Regressions visible only in production → Langfuse first.
5. pytest-style metric assertions needed → DeepEval.
6. Managed experiment tracking needed → Braintrust.

Do not let the tool define the rubric. Define the rubric, then pick the tool.

**Platform lifecycle note (June 2026):** The OpenAI Platform Evals UI shuts down November 2026. If currently using it, migrate to Promptfoo (recommended by OpenAI), DeepEval, or Braintrust.
