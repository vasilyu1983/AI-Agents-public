# software-ios-ai-engine — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] (corrected 2026-09-07) Current Foundation Models documentation exposes `contextSize`, `tokenCount(for:)`, and `LanguageModelError.contextSizeExceeded(_:)`. Verify availability and spelling in the target SDK; do not hardcode 4096 or carry the deprecated generation-error case forward.
- [2026-07-11] Newly announced Foundation Models surfaces (larger model tiers, third-party `LanguageModel` providers) need their own availability gates; keep the oldest-supported-OS model path as the shipping default and check Apple's current docs for hardware and OS requirements.
## Open Questions

## Consolidated Principles
