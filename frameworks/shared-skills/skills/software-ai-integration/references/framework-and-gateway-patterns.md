# Framework And Gateway Patterns

Use this file when the user needs help choosing the integration layer around models.

## Product SDK Layer

- Use Vercel AI SDK or direct provider SDKs when the feature is mostly:
  - streaming chat
  - structured extraction
  - inline suggestions
  - generation inside an existing product surface
- This should be the default for most product teams.

## Copilot UI Layer

- Use CopilotKit when the product explicitly needs an embedded copilot experience in a React application.
- It is most useful when the UI shell matters as much as the model call itself.

## Agent Workflow Layer

- Use LangGraph or CrewAI when the system is genuinely multi-step, stateful, or multi-agent.
- Do not default to these frameworks for simple chat, autocomplete, or one-shot generation flows.
- If orchestration is the main challenge, also consult `ai-agents`.
- If the chosen framework is LangGraph and the user needs implementation detail, route to `ai-bot-builder`.

## Gateway Layer

- Use Portkey or a thin internal gateway when you need:
  - provider routing
  - logging across many features
  - shared policy controls
  - cross-team model governance
- A gateway is an ops and control-plane choice, not a substitute for good product UX.
