# Routing And Control Planes

Guide for request placement once serving is no longer a single-host problem.

The runtime generates tokens. The control plane decides where a request should go and how reusable state is preserved.

## When You Need This Layer

Add an explicit router or control plane when any of these become true:

- more than one replica matters to the SLO
- prompt prefixes are reused and locality affects cost
- many LoRAs or tenants share a base model
- multimodal traffic mixes encoder-heavy and decode-heavy requests
- some replicas are colocated while others are split by phase

## Current Options

| Option | Best For | Strength |
|---|---|---|
| **vLLM Router / Production Stack** | vLLM-centric clusters | request placement, sticky routing, practical production patterns |
| **llm-d** | Kubernetes fleets with cache-aware routing | explicit routing, KV locality, multi-tier cache patterns |
| **SGLang Model Gateway / DP Router** | SGLang-centric text or multimodal fleets | tight integration with SGLang server modes |
| **Dynamo** | Multi-cloud and on-premise data-center serving (AWS EKS, GKE, NVIDIA hardware) | control plane plus phase-aware orchestration; open-source Apache 2.0 |

## What To Route On

- model family and context size
- modality
- schema or structured-output requirement
- active LoRA adapter
- prompt prefix or cache reuse potential
- current queue depth and concurrency headroom
- phase affinity for split topologies

## Placement Rules

Start simple:

1. route by model and modality
2. add sticky prefix routing when reuse is high
3. add adapter locality when LoRAs are involved
4. add phase-aware routing only when disaggregation exists

## Operational Checklist

- [ ] router decisions are observable per request
- [ ] overload and shed reasons are logged
- [ ] sticky placement can be bypassed during failures
- [ ] cold adapter loads are visible
- [ ] cache hit or reuse metrics feed placement decisions
- [ ] rollback to simpler routing is possible

## What To Avoid

- Avoid pure round-robin once locality matters.
- Avoid mixing routing logic into every app service.
- Avoid phase-aware routing before you can observe per-phase queues.
- Avoid adding a control plane without defining what state it is preserving.

## Primary Sources

- vLLM Production Stack: https://docs.vllm.ai/projects/production-stack/
- vLLM Semantic Router Iris: https://blog.vllm.ai/2026/01/05/vllm-sr-iris.html
- llm-d: https://github.com/llm-d/llm-d
- SGLang Model Gateway: https://docs.sglang.io/advanced_features/sgl_model_gateway.html
- SGLang DP Router: https://docs.sglang.io/advanced_features/dp_dpa_smg_guide.html
- Dynamo (open-source, Apache 2.0, multi-cloud): https://github.com/ai-dynamo/dynamo (verified 2026-05-17)
