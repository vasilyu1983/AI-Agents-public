# software-desktop — Learnings

## Patterns That Work

- [2026-07-11] Gate every desktop-framework decision on 'would a PWA satisfy this?' before the Electron/Tauri/native decision tree — saves signing/update pipeline entirely when it applies.
## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] Windows EV/OV code-signing keys require hardware HSM since June 2023; Azure Artifact Signing (formerly Trusted Signing) is Microsoft's cloud-native alternative. Squirrel.Windows is unmaintained — use NSIS + electron-updater.
## Open Questions

## Consolidated Principles

