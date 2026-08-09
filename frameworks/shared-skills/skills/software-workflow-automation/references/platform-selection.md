# Platform Selection

Use this file when the user needs to choose an automation layer.

## Decision Rule

| Primary need | Best fit |
|--------------|----------|
| Many SaaS integrations and operational glue | n8n |
| Visual AI and model-centric experimentation | Langflow |
| Self-hosted event monitoring and automation agents | Huginn |
| Durable retries, replay safety, and long-running workflow state | Temporal or Trigger.dev |
| Core product logic with strong testing needs | Custom code |

## Escalation Boundary

- Stay on a platform while speed of iteration matters most.
- Move to code when the workflow becomes business-critical, hard to review, or too complex to debug safely.

## Licensing Check

- n8n's self-hosted Community Edition ships under the fair-code Sustainable Use License: free for internal business use and modification, but restricted once the commercial value offered to a third party derives substantially from n8n itself (e.g., reselling hosted multi-tenant access, white-labeling it as a proprietary product). Flag this before recommending n8n as the backbone of a customer-facing or resold automation product; verify current license terms rather than assuming.
- Verify each platform's current license and hosting terms before a recommendation — fair-code, open-core, and fully open-source projects draw the commercial-use line in different places, and terms change over time.
