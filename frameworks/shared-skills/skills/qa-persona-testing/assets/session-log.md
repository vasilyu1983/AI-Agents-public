# Persona Test Session Log

One log per persona per scenario run. The log is the raw evidence the report cites — capture it during the session, not reconstructed afterwards.

## Session Header

| Field | Value |
|---|---|
| Persona | {{name + segment}} |
| Scenario | {{# and title from persona profile}} |
| App / build under test | {{URL, version, commit}} |
| Environment | {{browser tool: Playwright MCP / Chrome DevTools MCP}} |
| Emulation applied | {{viewport + mobile/touch flags, networkConditions, cpuThrottlingRate, geolocation, colorScheme — record actual values, not "default"}} |
| Context isolation | {{isolated context name, or "reused from scenario N" for a returning-user test}} |
| Date / duration | {{YYYY-MM-DD, mm:ss}} |
| Model running the persona | {{model + version — sycophancy is model-dependent; runs on different models are not directly comparable}} |
| Outcome | completed / partial / abandoned (reason) |

## Step Trace (think-aloud)

Record every meaningful action. `Persona voice` is the in-character reaction; `Observation` is the out-of-character QA fact. Keep them separate — mixing them corrupts both.

| # | Screen / URL | Action | Persona voice (in character) | Observation (out of character) | Evidence |
|---|---|---|---|---|---|
| 1 | {{...}} | {{click/type/scroll/wait}} | "{{first-person reaction}}" | {{latency, console error, layout issue}} | {{screenshot ref / console line}} |
| 2 | | | | | |

## Friction Events

| # | Step ref | Type | Severity (0-4) | Description |
|---|---|---|---|---|
| F1 | {{step #}} | confusion / dead end / error / distrust / delay / accessibility | {{0-4}} | {{what happened, in one sentence}} |

Severity scale (Nielsen): 0 = not a problem, 1 = cosmetic, 2 = minor, 3 = major (delays/blocks with workaround), 4 = catastrophic (task-blocking or trust-breaking).

## Abandonment Point (if any)

- Step where the persona quit: {{#}}
- Persona's stated reason (in character): "{{...}}"
- What would have kept them going: {{smallest change}}

## Session Verdict (in persona voice)

> "{{2-4 sentences: would this persona return, pay, recommend? What one thing almost made them leave?}}"
