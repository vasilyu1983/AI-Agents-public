# Eval Framework Selection and Integration

## Table of Contents

- [How to choose](#how-to-choose)
- [Framework map](#framework-map)
- [Integration snippets](#integration-snippets)
- [Do not make one framework the whole strategy](#do-not-make-one-framework-the-whole-strategy)

> Versions and APIs below drift fast. Verify the current API against official
> docs before copying a call into production. Snippets show the *shape*, not a
> guaranteed-current signature. The OpenTelemetry GenAI semantic conventions
> (`gen_ai.*` spans/metrics/events) moved out of the core `semantic-conventions`
> repo into a dedicated `semantic-conventions-genai` repo in 2026 — if you are
> wiring OTel-native tracing (Langfuse, Arize Phoenix, or a custom collector),
> point at the current dedicated repo/spec rather than a bookmarked link into
> the old location.

## How to choose

Match the framework to the **grader type and where it runs**, not to popularity:

- Deterministic metrics + custom logic in CI -> a thin custom harness (often best)
- Benchmarking open models on standard tasks -> lighteval / lm-eval-harness
- Agentic / tool-use scored tasks -> inspect-ai
- RAG faithfulness / context metrics -> Ragas
- App-level CI assertions over prompts -> promptfoo or DeepEval
- Hosted eval logging + dataset/experiment tracking -> Braintrust / LangSmith
- Self-hostable online eval sampling with OTel -> Langfuse or Arize Phoenix
- Team already on Weights & Biases -> W&B Weave
- Already on AWS / Bedrock -> Amazon Bedrock Model Evaluation (managed model comparison + RAG eval)

## Framework map

| Framework | Best for | Grader style | Notes |
|-----------|----------|--------------|-------|
| **inspect-ai** (UK AISI) | Agentic + tool-use tasks, structured scoring | Solver/scorer, supports model graders | Strong for behavior grading; provider-backed or local. |
| **lighteval** (HF) | Standard benchmarks on Hub models | Log-likelihood + generative | One-file-one-task since 0.13; multi-backend (vllm/accelerate). |
| **lm-eval-harness** (EleutherAI) | Reproducible academic benchmarks | Mostly log-likelihood | Contamination-aware; the benchmark lingua franca. |
| **Ragas** | RAG faithfulness/context metrics + synthetic testsets | LLM-judge metrics | Pair with deterministic retrieval metrics; verify metric defs per version. |
| **DeepEval** | CI-oriented app assertions (G-Eval) | LLM-judge + assertions | pytest-style; good for regression gating in app repos. DeepEval v4.0.0 released May 8, 2026 — verify API against current docs before using pre-v4 snippets. |
| **promptfoo** | Prompt/app matrix testing in CI | Assertions + model graders | Config-driven; fast for prompt A/B in CI. Acquired by OpenAI March 9, 2026; remains open source; roadmap now OpenAI-aligned — factor into vendor-neutrality assessment for multi-provider eval stacks (verified: https://www.promptfoo.dev/blog/promptfoo-joining-openai/). |
| **Braintrust** | Hosted experiment/dataset tracking | Custom + model graders | Logging/iteration platform, not a metric source by itself. |
| **LangSmith** | Tracing + dataset eval in LangChain stacks | Custom + model graders | Useful for online traces; not a substitute for offline design. |
| **Langfuse** | Online eval sampling + LLM observability; self-hostable | OTel-native tracing + custom scoring | Open-source; self-hostable; strong for online production sampling; verify current SDK before use. |
| **Arize Phoenix** | RAG eval + enterprise production monitoring | OTel-native tracing + model graders | Vendor-agnostic; works alongside any LLM stack; useful for retrieval attribution in production. |
| **W&B Weave** | ML-team experiment tracking + production tracing | Custom + model graders | Native to Weights & Biases; best when team already uses W&B for training runs. |
| **Amazon Bedrock Model Evaluation** | Managed model-comparison + RAG eval (Knowledge Bases) on Bedrock | LLM-as-judge + human + automatic metrics | Native for Bedrock-stack users; supports side-by-side model comparison and RAG Knowledge Base eval jobs; verify current job types, eligible models, and metric support in AWS docs before use. |

## Integration snippets

**inspect-ai** (agentic task with a model grader — shape only):

```python
from inspect_ai import Task, eval
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import generate

task = Task(
    dataset=my_jsonl_dataset,          # samples with input + target
    solver=generate(),                 # or a tool-using agent solver
    scorer=model_graded_qa(model="<different-judge-model>"),  # not the model under test
)
eval(task, model="<model-under-test>")
```

**Ragas faithfulness** (RAG answer grounding — shape only):

```python
from ragas import evaluate
from ragas.metrics import faithfulness, context_precision

# dataset: question, answer, contexts (retrieved), ground_truth (optional)
result = evaluate(dataset, metrics=[faithfulness, context_precision])
# inspect per-row scores, never just the aggregate
```

**DeepEval / promptfoo** run as CI assertions: define cases, define
metric/assertion + threshold, fail the build on regression. Keep the threshold
in version control and derive it per `threshold-derivation.md`.

**lighteval / lm-eval-harness**: invoked as CLIs over a served or local model;
see the `huggingface-skills:` plugin (external) for
the runnable `uv` scripts and backend selection.

## Do not make one framework the whole strategy

- Keep **deterministic metrics and versioned gold cases outside** any single
  vendor tool, so you can swap frameworks without losing your eval history.
- Use frameworks for the **judge plumbing and reporting**, not as the source of
  truth for what "good" means — that lives in your rubric and gold set.
- A framework's default metric is a starting point, not your spec. Read what its
  faithfulness/relevance metric actually computes before gating on it.
