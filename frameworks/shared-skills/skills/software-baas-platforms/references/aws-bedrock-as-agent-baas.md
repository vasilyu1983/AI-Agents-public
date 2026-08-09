# AWS Bedrock AgentCore as a BaaS-for-Agents

AWS is not a traditional Backend-as-a-Service like Supabase or Convex. But **Amazon Bedrock AgentCore** is BaaS-shaped specifically for AI agents — managed runtime, managed memory, managed identity, managed tool exposure. For teams choosing where to host an agent workload, AgentCore deserves the same comparison as Supabase + a custom agent layer.

This reference frames AgentCore as a peer in the BaaS-for-agents decision, not a replacement for general-purpose BaaS.

AWS ships AgentCore features fast; treat session-length limits, region availability, S3 Vectors scale limits, and quota defaults below as directionally correct rather than fixed — verify current numbers against the AgentCore release notes and docs before quoting them in a decision.

---

## Table of Contents

- [Why "BaaS for agents" is the right framing](#why-baas-for-agents-is-the-right-framing)
- [What AgentCore replaces vs what it doesn't](#what-agentcore-replaces-vs-what-it-doesnt)
- [Side-by-side with Supabase / Convex / Firebase for agent use cases](#side-by-side-with-supabase--convex--firebase-for-agent-use-cases)
- [When AWS wins](#when-aws-wins)
- [When Supabase / Convex / Firebase wins](#when-supabase--convex--firebase-wins)
- [Lock-in trade-offs](#lock-in-trade-offs)
- [Composition: AgentCore + traditional BaaS](#composition-agentcore--traditional-baas)
- [Related](#related)

---

## Why "BaaS for agents" is the right framing

Traditional BaaS (Supabase, Convex, Firebase, Appwrite) provides:

- Database
- Auth
- Realtime
- Storage
- Functions / serverless compute

AgentCore provides the equivalent **for agent workloads**:

| BaaS primitive | AgentCore equivalent |
|---|---|
| Database | (paired with) DynamoDB / Aurora / S3 |
| Auth | AgentCore Identity (per-agent IAM + workforce/customer identity) |
| Realtime | AgentCore Runtime (microVM session, streaming) |
| Storage | (paired with) S3 / S3 Vectors |
| Functions | AgentCore Runtime (8h sessions, framework-agnostic) |
| — | AgentCore Memory (managed conversation + facts) |
| — | AgentCore Gateway (MCP tool exposure) |
| — | AgentCore Evaluations + Policy (quality gates) |
| — | AgentCore Observability (agent-shaped traces) |

The bottom four rows are **net-new** primitives that traditional BaaS doesn't provide. That's why AgentCore is a distinct category, not "AWS playing catch-up."

---

## What AgentCore replaces vs what it doesn't

| You still need | Pair with |
|---|---|
| Application DB (relational, document) | DynamoDB, Aurora, Supabase Postgres, MongoDB |
| Object storage | S3 |
| Vector store | S3 Vectors (cheapest on AWS), Aurora pgvector, OpenSearch, Pinecone |
| Frontend hosting | Amplify, CloudFront, Vercel, Netlify |
| End-user auth (consumer) | Cognito, Auth0, Clerk, Supabase Auth |
| RAG corpus + retrieval | Bedrock Knowledge Bases, or self-hosted |

AgentCore replaces:

- Your custom agent-runtime container
- Your custom conversation-memory layer
- Your custom MCP-server-per-API wrapper
- Your custom per-agent IAM model
- Your custom agent-quality eval pipeline (partially — eval set still yours)
- Your custom agent observability dashboard

For a small team, that's weeks of platform work.

---

## Side-by-side with Supabase / Convex / Firebase for agent use cases

| Need | Supabase | Convex | Firebase | AgentCore (AWS) |
|---|---|---|---|---|
| Database for app data | Yes Postgres | Yes Convex DB | Yes Firestore | Pair with DynamoDB / Aurora |
| Auth | Yes | Yes | Yes | Yes Identity |
| Realtime | Yes | Yes | Yes | Yes Runtime streaming |
| Long agent sessions (> 15 min) | Caution Edge Functions cap | Caution Action timeout | Caution Functions cap | Yes **8h sessions** |
| Managed conversation memory | No Build yourself | No Build yourself | No Build yourself | Yes Memory |
| MCP tool exposure | No Build yourself | No Build yourself | No Build yourself | Yes Gateway |
| Per-agent IAM | No Build yourself | No Build yourself | No Build yourself | Yes Identity |
| Agent-shaped traces | No External (Langfuse) | No External | No External | Yes Observability |
| Eval gates + policy | No External | No External | No External | Yes Evaluations + Policy |
| Vector store | Yes pgvector | Via embeddings | Via extensions | Yes S3 Vectors / pgvector / OpenSearch |
| Managed RAG | No Build yourself | No Build yourself | No Build yourself | Yes Bedrock KB |
| Cross-cloud portability | Yes Self-hostable | Caution Convex-only | No Google-only | No AWS-only |
| Time-to-first-agent | Days (DIY agent layer) | Days (DIY agent layer) | Days (DIY agent layer) | **Hours** |

The honest reading: **Supabase / Convex / Firebase + your agent layer** roughly equals **AgentCore on AWS**, with the difference being how much agent platform you build vs adopt.

---

## When AWS wins

1. **You are already on AWS.** Same billing, same IAM, same VPC. Significant integration savings.
2. **Compliance demands AWS regions / data residency.** Common in finance, healthcare, public sector.
3. **You need 8-hour agent sessions.** Other BaaS function timeouts can't host this; you'd need Modal/Fly/Fargate alongside.
4. **You want managed memory + identity + tools + evals + policy from one vendor.** Building these on Supabase or Convex is real platform work.
5. **You will expose tools to non-AWS agents via MCP** (Gateway). Multi-agent ecosystem play.
6. **Cost optimization at scale** with S3 Vectors becomes meaningful (~90% cheaper than pgvector or Pinecone at multi-million-vector scale).

---

## When Supabase / Convex / Firebase wins

1. **You are not on AWS.** Don't add a cloud to host an agent.
2. **You're optimizing for developer experience.** Supabase / Convex DX is generally faster for app + agent prototype than AWS console.
3. **Multi-cloud portability matters.** AWS lock-in (especially Strands framework + AgentCore Memory) is real.
4. **You need a unified app DB + agent backend.** Supabase Postgres + Edge Functions + pgvector is a single coherent stack; AgentCore needs to pair with DynamoDB/Aurora.
5. **Short agent calls only** (< 15 min). All three BaaS handle this; AgentCore's session model is overkill.
6. **Team cannot or will not learn 9 AWS services.** Even with documentation, AgentCore is a learning investment.

---

## Lock-in trade-offs

| Layer | Lock-in level on AgentCore |
|---|---|
| Bedrock model | Medium — Bedrock hosts many providers (Anthropic, Meta, Mistral, etc.) but Bedrock API ≠ direct provider APIs |
| Runtime | Medium — microVM hosting, but if you bring your own framework (LangGraph), code is portable |
| Memory | High — proprietary fact-extraction prompts; export gives raw conversations, not extracted memories |
| Gateway | Low — MCP protocol is portable; tool definitions can move |
| Identity | High — IAM-shaped, doesn't move |
| Observability | High — CloudWatch + AgentCore-specific trace format |
| Evaluations | Medium — eval definitions partly portable, runner is AWS |
| Policy | Medium — natural-language policy text is portable; enforcement is AWS |
| S3 Vectors | High — proprietary storage format; migration = re-embed |

The portable layer is roughly: **your agent code + framework + tool definitions**. Everything else is AWS-shaped.

For multi-cloud teams: keep agent code in a framework that runs anywhere (LangGraph), keep tool definitions in MCP, keep source documents in S3 with the option to re-ingest elsewhere. Then you can leave AWS if you must — at the cost of rebuilding memory, identity, observability, evals, policy.

---

## Composition: AgentCore + traditional BaaS

These are not mutually exclusive. Common composition pattern:

```text
Frontend (Vercel / Netlify)
  ↓
App API (Supabase / Convex for app data, auth, realtime)
  ↓ (agent calls)
AgentCore Runtime + Memory + Gateway (on AWS)
  ↓
Bedrock model + Bedrock KB / S3 Vectors
```

Use when:
- The app itself is a non-AWS SaaS (Supabase/Convex/Firebase chosen for DX)
- The agent layer needs the AgentCore service set (long sessions, managed memory, MCP gateway)
- Cross-cloud is acceptable (latency + auth complexity manageable)

The boundary is clean: app state in BaaS, agent state in AgentCore Memory, both reference the same user IDs via JWT or signed tokens.

---

## Related

- [`platform-comparison.md`](platform-comparison.md) — BaaS comparison (Supabase / Convex / Firebase / Appwrite / PocketBase)
- [`migration-exit-strategies.md`](migration-exit-strategies.md) — BaaS migration patterns (apply to AgentCore exit too)
- [`security-and-ownership-models.md`](security-and-ownership-models.md) — Security/ownership across BaaS choices
- [`../../software-paas-hosting/references/aws-bedrock-agentcore.md`](../../software-paas-hosting/references/aws-bedrock-agentcore.md) — Deep dive on AgentCore services
- [`../../ai-rag/references/aws-bedrock-knowledge-bases.md`](../../ai-rag/references/aws-bedrock-knowledge-bases.md) — Managed RAG companion
- [`../../ai-vector-brain/references/s3-vectors-backend.md`](../../ai-vector-brain/references/s3-vectors-backend.md) — Cheap vector backend on AWS
- [`../../ai-context-layer/references/managed-memory-boundaries.md`](../../ai-context-layer/references/managed-memory-boundaries.md) — P13 managed-memory discipline (AgentCore Memory case study)
