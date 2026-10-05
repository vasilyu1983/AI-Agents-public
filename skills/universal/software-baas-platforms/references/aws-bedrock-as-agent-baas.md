# AgentCore in a Managed-Backend Decision

AgentCore supplies agent runtime and managed agent services; it does not replace the application's database, object storage, or end-user identity system.

## When to compare it

- Prefer an app BaaS when the main need is application data, auth, storage, and client sync.
- Evaluate AgentCore when an AWS-hosted agent needs managed execution, conversation memory, delegated credentials, MCP tool exposure, or agent observability.
- Compose the two when application state stays in the BaaS and the agent service has a separately justified runtime boundary.

## Responsibility split

| Need | Owner |
|------|-------|
| Application records and files | Chosen database/object store; AgentCore is not the system of record |
| End-user sign-in and tenant membership | Application identity provider and authorization model |
| Agent execution | AgentCore Runtime, with selected framework/model |
| Conversation/long-term memory | AgentCore Memory; define retention and deletion scope |
| Tool exposure and access | Gateway plus Identity/Policy as required; user authorization remains explicit |
| Traces and evaluation | AgentCore services plus application-owned acceptance criteria |

Check the [official service overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) for the selected service. Resolve runtime mode, protocol, region, quotas, and consumption pricing before judging fit; do not reuse another BaaS's function timeout as an AgentCore comparison.

## Exit and composition

Keep application-owned user/tenant IDs across the boundary. Authenticate agent calls and map identity explicitly; sharing an ID is not authorization. Test whether memory, credentials, tool definitions, and traces can be exported or reconstructed before adoption. Runtime framework portability alone does not establish service portability.

Use [software-paas-hosting's AgentCore reference](../../software-paas-hosting/references/aws-bedrock-agentcore.md) for runtime/deployment depth. Use [migration-exit-strategies.md](migration-exit-strategies.md) for application-backend exit proof. Measure setup effort on the proposed workload; no time-to-first-agent estimate is supplied here.
