# Provider-Native Prompt Ops

> Operational reference for current provider-native prompt tooling. Use this when the user asks for the latest prompt management, structured output, evaluation, or reasoning controls for a specific model family.

**Freshness anchor:** March 2026. Re-verify provider docs before recommending exact product names, flags, or limits.

---

## Quick Reference

| Provider | Use First | Use When | Notes |
|---|---|---|---|
| OpenAI | Prompting guide, Structured Outputs, Evals, Graders, Prompt optimizer, Prompt caching | API-based prompt delivery, schema-first outputs, eval-gated prompt changes | Prefer native prompt ops before custom wrappers |
| Anthropic | Prompting tools, Prompt generator, Prompt improver, Templates and variables, Eval tool, Adaptive/interleaved thinking | Claude-centered prompt authoring, prompt iteration, tool-heavy workflows | Avoid redundant "think step-by-step" when native thinking is enabled |
| Google Gemini | Prompting strategies, Structured output | Gemini prompt design, multimodal extraction, provider-specific parameter tuning | Start from current Google defaults, then tune after evals |

---

## OpenAI

Primary docs:

- Prompting guide: `https://developers.openai.com/api/docs/guides/prompting`
- Structured Outputs: `https://developers.openai.com/api/docs/guides/structured-outputs`
- Evals: `https://developers.openai.com/api/docs/guides/evals`
- Graders: `https://developers.openai.com/api/docs/guides/graders`
- Evaluation getting started: `https://developers.openai.com/api/docs/guides/evaluation-getting-started`
- Prompt optimizer: `https://developers.openai.com/api/docs/guides/prompt-optimizer`
- Prompt caching: `https://developers.openai.com/api/docs/guides/prompt-caching`

Operational guidance:

- Use Structured Outputs plus local schema validation for extractor and tool-response prompts.
- Use Evals + Graders before and after prompt changes; treat prompt updates like code changes.
- Use the Prompt optimizer when a prompt is underperforming but the task definition is stable.
- Use prompt caching for stable prompt prefixes or large repeated instructions.
- Prefer provider-native prompt/version management when available over ad hoc inline prompt duplication.

---

## Anthropic

Primary docs:

- Prompt engineering overview: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview`
- Prompting tools: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-tools`
- Claude prompting best practices: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`
- Eval tool: `https://platform.claude.com/docs/en/test-and-evaluate/eval-tool`
- Define success and build evals: `https://platform.claude.com/docs/en/test-and-evaluate/define-success-and-build-evals`
- Extended thinking: `https://platform.claude.com/docs/en/build-with-claude/extended-thinking`
- Adaptive thinking: `https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking`

Operational guidance:

- Use Anthropic's prompting tools page as the entrypoint for generator, improver, and template/variable workflows, then lock changes with evals.
- Use templates and variables for reusable prompt families instead of copy-pasting near-duplicates.
- Use the eval tool before shipping prompt changes that affect behavior, refusals, or tool use.
- If adaptive or interleaved thinking is enabled, keep prompt instructions high-level and avoid repetitive reasoning directives.
- For tool-heavy workflows, separate operational plans from private reasoning and validate each tool result before the next step.

---

## Google Gemini

Primary docs:

- Prompting strategies: `https://ai.google.dev/gemini-api/docs/prompting-strategies`
- Structured output: `https://ai.google.dev/gemini-api/docs/structured-output`

Operational guidance:

- Start with Google's current defaults before tuning temperature or reasoning controls.
- Use structured output for schema-first extraction and response-contract enforcement.
- For multimodal prompting, separate extraction prompts from interpretation prompts and evaluate them independently.
- Re-test provider-specific parameter changes; do not port OpenAI or Anthropic defaults directly into Gemini prompts.

---

## Shared Rules

- Prefer provider-native prompt management and eval tooling before introducing a custom prompt orchestration layer.
- Keep local schema validation, golden sets, and rollback criteria even when a provider offers native tooling.
- Treat current product names, flags, and model availability as volatile. Verify them before final recommendations.
