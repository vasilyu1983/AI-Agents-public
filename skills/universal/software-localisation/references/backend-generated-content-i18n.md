# Backend-Generated Content and Client Catalog Contract

This skill owns strings, plurals, catalogs, and the translation pipeline for every client, web or native. Use this reference when a backend returns generated prose (AI summaries, recommendations, narratives) to localized clients, or when a native app's catalogs must stay in step with the pipeline. Platform APIs (String Catalogs, `strings.xml`, per-app language settings) stay in the platform skills; see the Native Mobile Boundary in [SKILL.md](../SKILL.md).

## Table of Contents

- [Choose a pattern at endpoint-design time](#choose-a-pattern-at-endpoint-design-time)
- [Pattern A: generate in the target locale](#pattern-a-generate-in-the-target-locale)
- [Pattern B: translate after cache](#pattern-b-translate-after-cache)
- [Design rules for Pattern B](#design-rules-for-pattern-b)
- [Structural data versus prose](#structural-data-versus-prose)
- [Client contract](#client-contract)
- [Catalog integrity for native apps](#catalog-integrity-for-native-apps)
- [Economics and latency](#economics-and-latency)
- [Test gates](#test-gates)

## Choose a pattern at endpoint-design time

Localized clients hit a ceiling when the backend returns generated English prose the client cannot localize reliably on-device. Decide the pattern when the endpoint is designed, not after English has shipped to non-English users.

## Pattern A: generate in the target locale

The backend adds a locale instruction to the generation prompt and the model writes the target-locale output directly. No second model call and no translation cache.

Best for:

- per-user dynamic content (assistant replies, onboarding chat, interpretations)
- content requested once and rarely re-read
- routes that already run a prompt through a model

The locale instruction is a small prefix to a call that already happens, so extra cost and latency are near zero. Validate output in the target locale (length, script, forbidden terms); do not assume the model complied.

## Pattern B: translate after cache

The backend computes or caches the source language once, then layers a translation cache keyed by `sha256(source_content) + locale + translation_policy`.

Best for:

- deterministic compute endpoints (periodic plans, reports, scored assessments)
- static catalog content (glossary entries, category descriptions, keywords)
- scheduled per-user content (digests, summaries, recommendations)

## Design rules for Pattern B

1. **Split the cache by translation policy or accept single-quality output.** A shared cache serves whatever quality the first requester got. If an endpoint returns different quality tiers, model classes, or safety policies, the cache key must include that dimension.
2. **Never cache strings that carry runtime values** (user names, absolute times, personalized dates). Each unique interpolation multiplies the key space. Split into a template fragment plus a placeholder fragment, translate only the bounded template, and re-inject the value after translation. Follow the ICU-AST gate in [translation-workflows.md](translation-workflows.md#ai-powered-translation) so placeholders survive.
3. **Compute caches stay in the source language.** Translation happens at the response boundary, never inside the deterministic compute pipeline, so compute entries stay shareable across locales.
4. **Post-pass translation is non-fatal.** On translation failure return the source-language text; a partially translated response beats a 5xx. Record the fallback so it is visible in monitoring.
5. **Keep prompt execution config declarative and centralized.** Model choice, token limits, temperature, and response format come from versioned prompt definitions, not route code.
6. **Server-side locale priority:** explicit `?locale=` query parameter, then `Accept-Language`, then stored profile locale. Putting the profile first silently locks users out of the locale they just picked. This is the server half of the resolution rule in [locale-handling.md](locale-handling.md).

## Structural data versus prose

Inspect the response shape before writing a translator. If the backend returns structured values (enums, category types, keywords, units), the client localizes them through its own catalog or enum helpers and no backend translation is needed. Only generated prose needs Pattern A or B. Drawing this line during an i18n audit often removes a large share of planned translator work.

## Client contract

- Send the locale as `?locale=` and as an `Accept-Language` header on every API request.
- Propagate locale-picker changes to the API client immediately, not lazily.
- Read the locale at request-build or send time, not at client construction, so mid-session switches do not leak stale state or stale cached variants.
- Fixed UI chrome (labels, controls, chart legends, button copy) belongs in the app's local catalog. Do not localize static strings through backend translation or on-device AI.
- When one screen mixes static strings and backend prose, verify both paths are localized; half-localized screens read as bugs.

## Catalog integrity for native apps

- Test **key parity** (every catalog lookup call site has a key in every locale) and **value parity** (new keys have non-empty, non-source-language values in every locale). If every non-source locale receives the source default for a new key, the app is technically localized but visibly broken.
- Fallback strings mask missing keys in the default language; switch language to confirm.
- For generated catalogs, fix the upstream source of truth and regenerate. Editing only the generated copy is a stopgap the next generation overwrites. A crash or raw key from a missing catalog entry means the shipped catalog lacks the key; patch upstream, regenerate, and test.
- Edit large locale JSON files programmatically (load, modify, dump, verify the write); editor tools can silently fail on very large files.

## Economics and latency

Before recommending one architecture over another, estimate:

- cold-fill cost per translated response
- cache-hit latency versus miss latency
- cache fragmentation if plans or model classes produce different output policies
- pre-warm cost per locale and endpoint after each deploy or model-policy change
- behavior when translation is unavailable and the fallback language must ship

Treat unit economics as volatile: look up current pricing and measure cold-fill latency separately from cache-hit latency.

## Test gates

| Gate | What it checks |
|---|---|
| Key parity | Programmatic scan of every catalog lookup call site against every locale catalog; catches missing keys at test time |
| Value parity | New keys have non-empty, non-source-language values for every supported locale; run before claiming "all keys translated" |
| Locale layout smoke | One long-string locale and one non-Latin locale on the narrowest supported device; cards, containers, and controls must not overlap |
| Locale-switch smoke | Visit every main destination in a non-source locale; fail on source-language prose in payloads for localized routes |
| Cold-fill pre-warm | A CI or post-deploy job fills the translation cache for all supported locales and all covered endpoints |
