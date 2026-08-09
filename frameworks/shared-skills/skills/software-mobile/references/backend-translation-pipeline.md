# Backend Translation Pipeline (i18n for Generated Prose)

Mobile apps with localized UI hit a ceiling when the backend returns **generated English prose** (AI-generated summaries, recommendations, interpretations) that the client cannot localize reliably on-device. Choose a pattern at endpoint-design time, not after shipping English to non-English users.

## Pattern A — Generate-in-locale (preferred for on-demand LLM content)

The backend injects a locale instruction into the generation prompt; the LLM produces target-locale output directly. No second LLM call, no translation cache.

Best for:
- Per-user dynamic content (assistant responses, onboarding chat, interpretations)
- Content the user requests once and rarely re-reads
- Routes that already run a prompt through the LLM

Cost: zero extra per request (locale instruction is a small prefix to an already-happening call). Latency: zero extra.

## Pattern B — Translate-after-cache (post-pass at response boundary)

The backend computes or caches English once, then layers a translation cache on top keyed by `sha256(english_content) + locale + translation_policy`.

Best for:
- Deterministic compute endpoints (year-ahead forecasts, periodic returns, numerology)
- Static catalog content (meanings, bond types, sign keywords)
- Per-user scheduled content (daily digests, summaries, recommendations)

## Critical Design Rules for Pattern B

1. **Split the cache by translation policy or accept single-quality output.** Shared caches serve whatever quality the first requester got. If an endpoint returns different quality tiers, model classes, or safety policies, the cache key must include that policy dimension.
2. **Never cache strings with runtime placeholders** (user names, absolute times, personalized dates). Split the sentence into a template fragment + placeholder fragment; translate only the template; re-inject the variable.
3. **Compute caches stay English.** Translation happens at the response boundary, never inside the deterministic compute pipeline — keeps compute cache entries shareable across locales.
4. **Post-pass translation is non-fatal.** On LLM failure, return the original English; a partially-English response is preferable to a 5xx.
5. **Keep prompt execution config declarative and centralized.** Model choice, max tokens, temperature, and response format come from versioned prompt definitions, not hardcoded route logic.
6. **Locale detection priority.** Server-side: `?locale=` query param > `Accept-Language` header > stored user profile locale. Inverted priority (profile first) silently locks users out of their picker selection.

## Mobile Client Contract

- Inject `?locale=` query param AND `Accept-Language` header on every API request.
- Propagate locale-picker changes to the API client immediately, not lazily.
- Read locale from the API client at request-build time, not at client-construction time — mid-session locale switches otherwise leak stale state.
- Keep locale in the request builder or transport layer, read it at send time.
- Fixed mobile UI chrome (labels, controls, chart legends, button copy) belongs in the app's local l10n catalog. Do not use backend translation or on-device AI to localize static strings.
- For generated mobile catalogs, test both key parity and value parity. If every non-English locale receives the English default for a new key, the app is technically localized but user-visible localization is still broken.

## Structural vs Prose Distinction

Before writing a translator, inspect the response shape. If the backend returns pure structured data (positions, aspect types, sign keywords), the mobile client can localize it via enum helpers — no backend translation needed. Only generated prose (interpretations, narratives, summaries) needs Pattern B. This distinction routinely eliminates ~20–30% of planned translator work during an i18n audit.

## Economics and Latency Model

Before recommending one translation architecture over another, estimate:

- Cold-fill cost per translated response
- Cache-hit latency versus miss latency
- Cache fragmentation cost if different plans or model classes produce different output policies
- Pre-warm cost per locale and endpoint after each deploy or model-policy change
- Failure behavior when translation is unavailable and the fallback language must ship

Treat exact unit economics as volatile; verify current pricing and measure cold-fill latency separately from cache-hit latency.

## Test Gates

| Gate | What It Checks |
|------|----------------|
| l10n key parity test (iOS) | Programmatic scan of every `l10n.text()` call site vs every locale JSON catalog. Catches missing keys at test time. |
| l10n value parity test | New keys have non-empty, non-English values for every supported locale. Use before claiming "all keys translated." |
| Locale layout smoke | Long-string and non-Latin locales on the narrowest supported phone. Cards, containers, controls must not overlap. |
| Locale-switch smoke | Tap every main tab in a non-English locale; fail on English prose in response payloads for localized routes. |
| Cold-fill pre-warm | CI/post-deploy job pre-populates the translation cache for all supported locales × all covered endpoints. |
