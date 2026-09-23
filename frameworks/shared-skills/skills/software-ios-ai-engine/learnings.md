# software-ios-ai-engine — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11, corrected 2026-09-07] Current Foundation Models documentation exposes `contextSize`, `tokenCount(for:)`, and `LanguageModelError.contextSizeExceeded(_:)`. Verify availability and spelling in the target SDK; do not hardcode 4096 or carry the deprecated generation-error case forward.
- [2026-07-11] WWDC26 previewed 3rd-gen Foundation Models (20B sparse tier, 12GB+ devices, 3rd-party LanguageModel protocol) for iOS 27 beta only — not shipped; keep iOS 26 ~3B model as the shipping default.
## Open Questions

## Consolidated Principles
