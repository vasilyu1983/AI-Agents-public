# AI Integration

## Table of Contents

- [Contents](#contents)
- [Operating Model](#operating-model)
- [Source Design](#source-design)
- [Retrieval and Answer Policy](#retrieval-and-answer-policy)
- [Tool Permissions](#tool-permissions)
- [Escalation and Handoff](#escalation-and-handoff)
- [Evaluation and QA](#evaluation-and-qa)
- [Platform Notes](#platform-notes)

Retrieval-first support AI patterns for help centers and documentation hubs.

## Contents

- Operating model
- Source design
- Retrieval and answer policy
- Tool permissions
- Escalation and handoff
- Evaluation and QA
- Platform notes

## Operating Model

Do not start with a model choice. Start with a support operating model.

### Decision Ladder

1. Informational AI
   - Answers from approved knowledge only.
2. Guided AI
   - Asks clarifying questions and routes users to the right workflow.
3. Diagnostic AI
   - Uses product context or logs to narrow likely causes.
4. Agentic AI
   - Executes approved tasks through tools with guardrails and audit trails.

Recommendation:
- Start with informational or guided AI unless the user explicitly needs task execution.
- Add tool execution only when permissions, rollback paths, and QA are clear.

## Source Design

### Approved Source Types

| Source | Use For | Notes |
|--------|---------|-------|
| Public help-center articles | End-user support | Highest priority for customer-facing answers |
| Developer docs and API reference | Technical answers | Keep separate from end-user guidance when the audience differs |
| Internal runbooks | Agent assist only | Usually not appropriate for direct end-user answers |
| Resolved tickets | Gap discovery and draft inputs | Do not expose raw tickets directly without curation |
| Release notes and changelogs | Product changes | Important for freshness and renamed features |
| Status and incident data | Live issue handling | Must be explicitly scoped and time-aware |

### Source Rules

- Prefer one canonical source per fact domain.
- Separate public content from internal-only policies.
- Store version, locale, audience, and last-updated metadata with each source.
- Remove duplicated or conflicting pages before scaling retrieval.

## Retrieval and Answer Policy

### Retrieval Pipeline

```
user question
  -> classify intent, audience, and risk
  -> retrieve from approved sources
  -> rerank for exactness and freshness
  -> answer with citations
  -> clarify or escalate if evidence is weak
```

### Practical Defaults

- Use hybrid retrieval, not semantic-only retrieval.
- Preserve headings and section boundaries when chunking.
- Keep exact error strings searchable.
- Add freshness and product-version metadata to every chunk.
- Require citations for factual or procedural answers.

### Answer Policy

The assistant should:
- answer only from retrieved evidence
- cite the exact page or section used
- say when the evidence is insufficient
- ask a clarifying question when multiple workflows are plausible
- avoid implied certainty when the source is stale or incomplete

The assistant should not:
- infer plan limits, pricing, or policy from weak context
- merge public and internal guidance unless the audience is explicit
- execute tasks just because a tool exists

## Tool Permissions

### Permission Matrix

| Task Type | Example | Default |
|-----------|---------|---------|
| Informational | Explain billing limits | Allowed from approved content |
| Navigational | Link to the invoice page | Allowed |
| Diagnostic | Check status page or logs | Allowed only with scoped read access |
| Transactional | Cancel subscription or issue refund | Denied unless explicitly approved |
| Escalation | Create ticket or hand off | Allowed when trigger conditions are met |

### Tooling Rules

- Define which tools exist, who may use them, and under what conditions.
- Log every transactional tool call with actor, reason, and outcome.
- Provide a rollback or compensating action for destructive tasks.
- Require additional confirmation for money movement, account access, or irreversible changes.

### MCP Notes

MCP is useful when the user wants a standard way to expose tools or documentation to assistants.

Use MCP when:
- multiple assistant clients need the same tools or docs access
- the team wants explicit tool schemas and authorization boundaries
- documentation itself should be discoverable as machine-usable resources

Do not present MCP as mandatory for every support AI deployment.

## Escalation and Handoff

Escalate when:
- retrieved evidence is weak or contradictory
- the task is high-risk or policy-sensitive
- the user explicitly asks for a person
- the same conversation loops without progress
- required tools are unavailable or denied

### Handoff Payload

Every escalation should include:
- user intent
- what sources were checked
- what the assistant already tried
- relevant IDs, timestamps, or environment details
- why escalation happened

## Grounding Quality Judgment

Citation rate is a weak proxy for grounding quality — an assistant can cite a real source and still be wrong. A support-content lead reviewing transcripts checks for these specific failure shapes, which a "has a citation" check will not catch:

- **Superficial citation.** The cited page is topically related but does not actually contain the claim in the answer — the model paraphrased plausibly from a nearby chunk rather than stating what the source says. Spot-check by reading the cited section, not just confirming a link exists.
- **Chunking that separates a rule from its caveat.** A limit, a rate, or a policy is stated in one paragraph and its exception ("...unless you are on the Enterprise plan" or "...this changed in v4.2") sits in the next paragraph. If the chunk boundary falls between them, the assistant answers with the rule and cites the source honestly, while still being wrong for a meaningful share of users.
- **Right answer, wrong version or plan.** Retrieval returns the highest-relevance chunk regardless of whether it matches the asking user's product version, plan tier, or locale. This is invisible in aggregate citation-rate metrics and only shows up when you segment evaluation by version/plan/locale.
- **Confident synthesis across sources.** The assistant blends two retrieved chunks into a claim that neither source makes on its own — each citation is individually accurate, but the combined claim is invented. This is harder to catch than an unsupported claim because every link in the answer is real.
- **Stale-but-fresh-looking sources.** A page was reviewed and re-approved on schedule (passes freshness checks) but the underlying screenshot, workflow, or limit it describes changed in a release that did not trigger a content update. Citation and freshness metadata both look healthy while the retrieved fact is wrong.

None of these are caught by citation rate, unresolved-intent rate, or automated retrieval-quality scores alone. Build a recurring human-review sample (weekly, 20-30 transcripts, weighted toward high-risk intents) that reads the cited source against the claim, not just whether a source was attached.

## Evaluation and QA

### Evaluation Layers

1. Retrieval quality
   - Did the right sources appear?
2. Answer quality
   - Was the response correct, cited, and complete enough?
3. Policy adherence
   - Did the assistant escalate or refuse when required?
4. Task execution quality
   - Did tool calls succeed and produce the intended outcome?

### Pre-Launch QA

- Build a scenario set for top intents, edge cases, and policy-sensitive cases.
- Test stale-content scenarios and renamed-feature scenarios.
- Simulate low-confidence retrieval and verify escalation behavior.
- Review handoff summaries with the support team.

### Live Monitoring

Track:
- citation rate
- unresolved-intent rate
- escalation-after-loop rate
- tool-call success rate
- reopen-after-AI rate
- stale-source hit rate

## Platform Notes

### Zendesk

- Use Zendesk when the user needs a support-suite operating model first.
- Current guidance emphasizes AI agents plus help-center content optimization, not just a legacy bot toggle.

### Intercom

- Current Intercom guidance puts more emphasis on procedures, simulation, and operational tuning for Fin.
- Strong fit when help center, in-app guidance, and conversational support need to work together.

### Custom Build

Build custom only when:
- the user needs proprietary data access or workflows
- vendor platforms do not fit security or product requirements
- the team can own evaluation, prompt policy, tool governance, and observability
