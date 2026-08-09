# Platform Guides

## Table of Contents

- [Contents](#contents)
- [Platform Selection Heuristics](#platform-selection-heuristics)
- [Support Suites](#support-suites)
- [Docs Portals](#docs-portals)
- [Internal Knowledge Tools](#internal-knowledge-tools)
- [In-App Guidance Layer](#in-app-guidance-layer)
- [Evaluation Checklist](#evaluation-checklist)
- [Migration Notes](#migration-notes)

Current platform-fit guidance for help centers, support suites, and AI-native docs.

## Contents

- Platform selection heuristics
- Support suites
- Docs portals
- Internal knowledge tools
- In-app guidance layer
- Evaluation checklist
- Migration notes

## Platform Selection Heuristics

Choose the platform family before choosing a vendor.

| Primary Need | Platform Family | Typical Winners |
|--------------|-----------------|-----------------|
| Public support content plus ticketing, chat, SLAs, and agent handoff | Support suite | Zendesk, Intercom, Freshdesk |
| Public product or API docs with structured navigation and strong AI-doc features | Docs portal | ReadMe, Mintlify, GitBook |
| Internal-only knowledge for support and operations teams | Internal knowledge base | Guru, Confluence, Notion |
| Product onboarding and contextual prompts in-app | In-app guidance layer | Intercom, Pendo, Appcues, custom |
| High-volume support automation with tool execution | Support AI layer | Zendesk AI, Intercom Fin, custom |

### Default Rules

- Pick a support suite when ticketing, routing, agent workspace, and compliance requirements drive the choice.
- Pick a docs portal when the hardest problem is publishing structured, versioned, searchable documentation.
- Keep internal knowledge separate when permissions, draft workflows, or sensitive runbooks differ from public docs.
- Do not let pricing be the first filter. Integration fit, ownership model, and AI behavior matter more.
- Verify current packaging and AI entitlements before recommending any vendor.

## Support Suites

### Zendesk

Best fit:
- Mature support operations
- Multi-team routing and SLA management
- Enterprise controls, auditability, and help-center governance

Strengths:
- Full support suite with mature workflows
- Strong handoff and agent-operating model
- Official guidance for optimizing help-center content for AI agents

Watch-outs:
- Heavier admin surface than simpler tools
- Packaging and add-ons change; verify before advising
- AI value depends on content quality and operational setup, not just enablement

Use when:
- The user needs a serious support operation, not just a docs site
- Compliance, approvals, or escalation rigor are important

### Intercom

Best fit:
- SaaS and product-led support
- Messenger-first support and in-app help
- Teams that want support AI and product guidance in one surface

Strengths:
- Strong in-app support and messenger integration
- Fin procedures and simulation workflows are useful for operating support AI safely
- Good fit when support and onboarding are tightly connected

Watch-outs:
- Packaging, traffic controls, and AI billing are volatile
- Help center structure is lighter-weight than enterprise support suites
- Still needs strong procedures and source hygiene to avoid weak automation

Use when:
- The user wants help center plus in-app assistance plus conversational support

### Freshdesk

Best fit:
- Teams that need standard support-suite capability without a heavy enterprise footprint

Strengths:
- Solid baseline support workflows
- Suitable for conventional help-center plus ticketing use cases

Watch-outs:
- Verify current AI packaging and enterprise features before positioning it as an AI leader
- Less useful as a docs-first recommendation than dedicated docs portals

Use when:
- Budget and operational simplicity matter more than best-in-class docs UX

## Docs Portals

### ReadMe

Best fit:
- API products and developer-facing documentation
- Teams that want docs, API reference, and AI features in one surface

Strengths:
- Mature docs and API reference experience
- Strong current coverage for MCP servers and `llms.txt`
- Good fit when documentation itself must be AI-consumable

Watch-outs:
- Not a replacement for a full customer-support suite
- Requires disciplined content modeling to get the most from AI surfaces

### Mintlify

Best fit:
- Fast-moving product and API docs teams
- Teams explicitly optimizing docs for humans and AI systems

Strengths:
- Clear AI-facing features such as `llms.txt` and MCP support
- Strong fit for docs-as-product workflows

Watch-outs:
- Not a full support operation platform
- Evaluate governance, versioning, and non-technical editing needs against the team model

### GitBook

Best fit:
- Teams that want collaborative docs with strong web publishing and growing AI-native capabilities

Strengths:
- Strong authoring workflow for mixed technical and non-technical teams
- Public emphasis on AI-native docs, MCP, and skill.md-style assistant context

Watch-outs:
- Legacy GitBook docs-as-code assumptions do not always match current product behavior
- Verify the exact publishing and sync model the team needs

## Internal Knowledge Tools

### Guru and Confluence

Use when:
- Support and ops teams need restricted, reviewed, internal knowledge
- The public help center should not expose runbooks, exception handling, or internal policies

### Notion

Use when:
- The team needs lightweight internal documentation or a temporary public docs surface

Do not default to Notion when:
- Search analytics, structured IA, versioning, support-AI operations, or long-term public docs quality matter

## In-App Guidance Layer

Use an in-app guidance layer when the user’s main problem is adoption or workflow assistance rather than searchable documentation.

Good fits:
- onboarding checklists
- contextual nudges
- feature discovery
- error-state rescue flows

Common stack:
- support suite or docs portal for durable content
- in-app guidance layer for contextual delivery
- support AI for conversational retrieval and escalation

## Evaluation Checklist

For any vendor comparison, answer these before making a recommendation:

1. What is the primary surface: support suite, docs portal, internal KB, or in-app guidance?
2. Who owns content: support, docs, product marketing, developer relations, or a mixed team?
3. Does the product need versioning, role-aware delivery, or multilingual content?
4. Is support AI informational only, or can it execute approved tasks?
5. What systems must integrate: CRM, billing, status, order management, analytics?
6. What level of auditability, approvals, and permissions is required?
7. Which metrics matter most: search success, containment, ticket reduction, onboarding completion, or dev-doc adoption?

## Migration Notes

When migrating platforms:
- separate content cleanup from platform migration when possible
- preserve canonical URLs and redirects
- validate search, analytics, and AI source indexing after launch
- re-test support AI behavior after migration because retrieval behavior often changes

Use [content-migration-guide.md](content-migration-guide.md) for the detailed migration checklist.
