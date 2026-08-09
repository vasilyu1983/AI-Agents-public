# Inference Cost Optimization Patterns

Cost guidance that avoids hard-coded March 2026 price tables. Provider pricing and discounts change too often to bake into a long-lived skill.

Use current provider pricing pages before making dollar-denominated recommendations.

## Cost Levers In Order

1. remove wasted tokens
2. improve cache reuse
3. route simpler work to cheaper models
4. batch non-interactive workloads
5. right-size hardware or replica count
6. revisit precision only after quality is measured

## Measurement Baseline

Track these first:

- cost per request
- cost per output token
- cache hit rate
- average prompt length
- average output length
- retry rate
- overload rate
- schema-valid rate if structured outputs are required

## Managed API Levers

Use features exposed by the provider rather than generic prompt trimming alone:

- prompt or context caching
- batch APIs for offline work
- model routing by task class
- image or multimodal resizing before upload
- rate-limit aware retry logic

Verify current pricing and limits before quoting savings percentages.

## Self-Hosted Levers

- route requests to replicas with reusable prefixes or loaded adapters
- cap context windows to the workload distribution
- tune batching by real prompt length buckets
- avoid over-scaling decode replicas when encoder or prefill is the bottleneck
- use cheaper hardware only when the runtime support and SLO still hold

## Break-Even Questions

Before moving to a new model or topology, calculate:

- current requests per day and token mix
- expected cache hit rate after the change
- latency impact of the cheaper option
- quality regression tolerance
- ops cost of a more complex self-hosted stack

## Decision Rules

| Situation | First Move |
|---|---|
| system prompt is large and reused | add provider or prefix caching |
| many simple requests hit an expensive model | route by task class or complexity |
| offline processing dominates spend | use batch APIs or batch jobs |
| multimodal costs are rising | resize or compress inputs before inference |
| self-hosted cost is high | inspect routing, batching, and idle replicas before changing hardware |

## Guardrails

- Do not quote provider prices from memory.
- Do not claim a fixed savings percentage without a current pricing source.
- Keep quality and schema-valid metrics next to cost metrics.
- Treat retries as a direct cost multiplier and cap them aggressively.

## Current Docs To Check

- OpenAI pricing and batch docs
- Anthropic pricing and prompt caching docs
- Google Gemini pricing and context caching docs
- AWS Bedrock pricing and inference docs
