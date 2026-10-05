# software-desktop — Learnings

## Patterns That Work

- [2026-07-11] Gate every desktop-framework decision on 'would a PWA satisfy this?' before the Electron/Tauri/native decision tree — saves signing/update pipeline entirely when it applies.
## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] Windows EV/OV code-signing keys require hardware HSM since June 2023; Azure Artifact Signing (formerly Trusted Signing) is Microsoft's cloud-native alternative. Squirrel.Windows is unmaintained — use NSIS + electron-updater. **[Corrected 2026-09-23]** Squirrel vs NSIS is a toolchain split (Forge + built-in `autoUpdater` with Squirrel/MSIX vs electron-builder + NSIS + `electron-updater`); Electron docs still support Squirrel; upstream maintenance status unverified. Artifact Signing eligibility is 12 regions for orgs, US/CA only for individuals, no EV.
## Open Questions

## Consolidated Principles

