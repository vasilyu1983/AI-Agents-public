# Bot Safety Checklist

Complete this checklist before launching a bot to production.

## Conversation Safety

- [ ] **Fallback hierarchy** — Every conversation state has a fallback that doesn't dead-end
- [ ] **Turn budget** — Max turns enforced, escalation triggered at budget
- [ ] **Escalation path** — Human handoff is reachable from every state
- [ ] **Out-of-scope handling** — Bot gracefully declines topics outside its scope
- [ ] **Loop detection** — Bot detects and breaks conversation loops (3+ repeated fallbacks)

## Content Safety

- [ ] **Topic boundaries** — Bot refuses to discuss topics outside its domain
- [ ] **No harmful content** — Bot cannot be tricked into generating harmful, offensive, or misleading content
- [ ] **No medical/legal/financial advice** — Unless specifically designed and reviewed for that domain
- [ ] **No other-user data** — Bot never leaks information from other users or accounts
- [ ] **Honest identity** — Bot tells users it is an AI at the latest at the first interaction (EU AI Act Art. 50(1), applies from 2 Aug 2026), not only "when asked", and never pretends to be human. The only exception is when being an AI is obvious to a reasonably well-informed user in context

## Prompt Security

- [ ] **Injection resistance** — Tested with prompt injection attacks (role override, instruction override, jailbreaks)
- [ ] **Tool-output poisoning** — Bot doesn't blindly trust data from external tools (malicious content in KB articles, API responses)
- [ ] **System prompt protection** — Bot doesn't reveal its system prompt when asked
- [ ] **Boundary enforcement** — User messages cannot modify the bot's persona or safety rules

## Data Safety

- [ ] **PII handling** — PII is handled according to privacy policy (collection, storage, retention)
- [ ] **Conversation logging** — Logs are stored securely with appropriate retention policies
- [ ] **Access control** — Bot only accesses data the authenticated user is authorized to see
- [ ] **No credential exposure** — API keys, tokens, and secrets are never exposed in responses

## Tool Safety

- [ ] **Tool boundaries** — Bot can only call defined tools, no arbitrary code execution
- [ ] **Side-effect confirmation** — Actions with side effects (create, update, delete) require confirmation
- [ ] **Rate limits** — Tool calls are rate-limited to prevent abuse
- [ ] **Error handling** — Tool failures are handled gracefully, never exposing raw errors

## Operational Safety

- [ ] **Kill switch** — Bot can be immediately disabled without code deployment
- [ ] **Fallback mode** — If the bot goes down, users are routed to human support or a static message
- [ ] **Cost cap** — Per-conversation and total spend limits are enforced
- [ ] **Monitoring** — Alerts configured for: high escalation rate, tool failures, cost spikes, conversation loops
- [ ] **Rollback plan** — Previous bot version can be restored within minutes

## Testing

- [ ] **Multi-turn eval suite** — Bot tested with representative conversations across all flows
- [ ] **Edge cases** — Empty inputs, very long inputs, special characters, multiple intents
- [ ] **Adversarial inputs** — Prompt injection, topic boundary testing, social engineering attempts
- [ ] **Regression baseline** — Current conversation quality scores recorded for future comparison
- [ ] **Load testing** — Bot tested at expected peak concurrent conversation volume
