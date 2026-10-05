---
name: software-desktop
description: "Builds and reviews desktop apps. Use when choosing a stack, signing or notarizing releases, adding auto-update, or reviewing Electron/Tauri security."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Desktop Application Development

Build cross-platform and native desktop apps with correct architecture, security defaults, and distribution pipelines.

## Quick Reference

| Need | Recommended Tool / Framework |
|---|---|
| Cross-platform (JS/TS) | Electron — mature ecosystem, large community, Chromium-based |
| Cross-platform (Go + Web) | Wails — Go backend with an OS webview; verify target dependencies and selected major's release status at [Wails](https://wails.io/docs/introduction/) |
| Cross-platform (.NET desktop) | Avalonia — Windows/macOS/Linux XAML UI; self-contained deployment bundles .NET, but target native libraries still matter |
| Cross-platform (Rust + Web) | Tauri — smaller bundles, stronger security model, OS webview, also targets iOS/Android from the same codebase (stable since Tauri 2.0, Oct 2024) |
| Cross-platform (Dart) | Flutter Desktop — shared mobile/desktop codebase; strongest on macOS, Windows/Linux slightly behind on package maturity |
| Cross-platform (.NET) | .NET MAUI — Windows (WinUI 3 host) + macOS (Mac Catalyst) only; no first-party native Linux desktop target (check the .NET MAUI supported-platforms docs, including any third-party Linux backends, before promising Linux) |
| Cross-platform (Kotlin) | Compose Multiplatform — shared Android/desktop UI |
| Native macOS | SwiftUI (default for new apps) + AppKit interop for advanced window/menu chrome |
| Native Windows | WPF for established Windows-only line-of-business apps; WinUI 3 when Windows App SDK integration fits the product |
| Native Linux | GTK (GNOME), Qt (KDE) |
| Auto-update | Pick by toolchain: electron-builder → NSIS target + `electron-updater`; Electron Forge → built-in `autoUpdater` (Squirrel.Windows via electron-winstaller, or MSIX); Tauri's built-in updater; Sparkle 2 (macOS) |
| Code signing | Apple notarization via `notarytool`; Windows Authenticode via Azure Artifact Signing (formerly "Trusted Signing") or a traditional EV/OV cert; Linux (distro-specific) |
| Installers | electron-builder, Tauri bundler, create-dmg, Inno Setup, NSIS, AppImage/Flatpak/Snap |
| Tauri capability/plugin migration | [references/tauri-2-migration.md](references/tauri-2-migration.md) — load for migration and WebView2 deployment |
| Verify Developer ID .app signature and ticket | [scripts/check_signing.sh](scripts/check_signing.sh) — macOS only; non-macOS and unsupported artifacts fail |
| Validate signing configuration before CI | [scripts/check_signing_readiness.py](scripts/check_signing_readiness.py) — static schema checks; `--strict` requires referenced files locally, without inspecting key material |

## When to Use This Skill

- Choosing a framework for a new desktop application
- Building Electron or Tauri apps with correct security and IPC patterns
- Implementing desktop-specific features: file system access, system tray, native menus, protocol handlers, drag-and-drop
- Setting up code signing, notarization, and installer pipelines
- Adding auto-update mechanisms to desktop apps
- Reviewing desktop application architecture or security posture
- Migrating from Electron to Tauri (or evaluating the tradeoff)

## When NOT to Use This Skill

- **Web-only frontends (SPA, SSR, static sites)** → [software-frontend](../software-frontend/SKILL.md)
- **Mobile apps (iOS, Android, React Native)** → [software-mobile](../software-mobile/SKILL.md)
- **CLI tools and developer utilities** → [software-devtools](../software-devtools/SKILL.md)
- **System architecture and service decomposition** → [software-architecture-design](../software-architecture-design/SKILL.md)
- **Security audits and threat modeling** → [software-security-appsec](../software-security-appsec/SKILL.md)

## Workflow

1. Confirm the platform scope, native integration needs, distribution targets, and team constraints.
2. Route web-only, mobile, CLI, or system-design work to the adjacent skill when desktop is not the core problem.
3. Choose the framework and packaging approach from the decision tree.
4. Apply the relevant architecture, distribution, update, and security guidance for that stack.
5. Verify current signing, notarization, and platform-policy details through the navigation sources before final advice.

## Before Reaching for a Framework: Does This Need to Be Desktop At All?

A meaningful fraction of "we need a desktop app" requests are better served by a PWA — no code signing, no update server, no per-OS QA matrix. Push back and confirm desktop is the right call before opening the decision tree below:

- No deep OS integration required (no system tray persistence, no global shortcuts, no raw filesystem/serial/USB access, no offline-first local database as the primary store) → a PWA (installable, `manifest.json` + service worker) likely covers it with a fraction of the packaging and signing burden.
- Users are already inside a Chromium-family browser and don't need to run at machine startup or survive without the browser installed → PWA.
- The ask genuinely needs OS-level integration (file associations, native menus/tray, background services, hardware access, MSI/enterprise deployment, App Store distribution) → proceed to a native or hybrid desktop framework below.
- When in doubt, prototype the PWA first — it is cheap to abandon and expensive to have skipped.

## Decision Tree

```text
Desktop framework selection (after confirming a PWA won't do):

START
├─ Need full native platform integration and max performance?
│  ├─ macOS only → SwiftUI (+ AppKit for custom chrome)
│  ├─ Windows only → WPF for an existing WPF codebase or WinUI 3 for Windows App SDK integration
│  └─ Linux only → GTK or Qt
├─ Have a web app and want desktop distribution?
│  ├─ Team knows Node.js, needs mature plugins / deepest native integration → Electron
│  ├─ Bundle size, memory, and a stronger default security posture matter, team can absorb some Rust → Tauri
│  ├─ Go backend team → Wails (OS webview; verify release status and native dependencies)
│  └─ Also need iOS/Android from the same codebase → Tauri (mobile targets stable since 2.0; feature parity with desktop plugins still catching up)
├─ Already have a Flutter mobile app?
│  └─ Flutter Desktop (shared codebase; strongest on macOS, fewer production-grade Windows/Linux packages)
├─ Already have a Compose Android app?
│  └─ Compose Multiplatform Desktop
├─ .NET team needing desktop?
│  ├─ Windows + macOS only, want one XAML codebase across mobile too → .NET MAUI (no native Linux target yet)
│  ├─ Windows/macOS/Linux desktop with XAML → Avalonia (self-contained publish per target RID)
│  └─ Windows-only → WPF or WinUI 3
├─ Bundle size and memory footprint critical?
│  └─ Tauri or Wails (OS webview); benchmark the actual release artifacts and full process tree
└─ Security-sensitive app?
   └─ Tauri (no Node.js in renderer, capability-scoped IPC, an explicitly configured CSP) — or Electron with `contextIsolation`/`sandbox` enforced as non-negotiables if the team can't take on Rust
```

### Electron vs Tauri: the gates that actually decide it

- **Team skills**: Electron if the team is JS/TS-only with no Rust appetite; Tauri if the team can own a Rust backend (or keep it thin and mostly use plugins).
- **Binary size / memory**: Electron bundles Chromium and Node; Tauri relies on the OS webview. Installer and idle-RAM figures are unverified here: measure signed release builds with the same UI, OS, architecture, and all child processes, including bundled or downloaded runtimes.
- **Webview fragmentation risk**: Windows is low-risk — WebView2 is evergreen and bundled with Windows 11 (bootstrap it for Windows 10). Linux is real risk for Tauri — it depends on WebKitGTK, and distro packaging of `webkit2gtk-4.0` vs `4.1` (soup2 vs soup3) differs. [WebKitGTK 2.52 removed libsoup2 support in March 2026](https://webkitgtk.org/2026/03/18/webkitgtk-2.52-highlights.html); check package availability on the minimum supported distro. Pin and test against your minimum supported distro before committing to Tauri on Linux.
- **Plugin/ecosystem maturity**: Electron's plugin and tooling ecosystem is larger and older; Tauri's is smaller but growing quickly, especially since mobile landed.
- **Migration cost**: Electron → Tauri is closer to a rewrite than a refactor (different process model, different IPC, no Node.js APIs) — get this choice right up front rather than planning to switch later.

## Electron Architecture

Electron apps run two process types: the **main process** (Node.js, one per app) and **renderer processes** (Chromium, one per window).

**Process model and IPC**:
- Main process owns lifecycle, native APIs, menus, tray, and file system access.
- Renderer processes display UI and must never have direct Node.js access.
- Preload scripts bridge main and renderer via `contextBridge.exposeInMainWorld`.
- All cross-process communication flows through typed IPC channels (`ipcMain.handle` / `ipcRenderer.invoke`).

**Security model (mandatory)**:
- `contextIsolation: true` — always. No exceptions.
- `nodeIntegration: false` — always. Preload scripts are the only bridge.
- `webSecurity: true` — never disable in production.
- `sandbox: true` — renderer default since Electron 20; keep it explicit because enabling Node integration disables it.
- Check the [Electron support schedule](https://www.electronjs.org/docs/latest/tutorial/electron-timelines) when selecting a release: stay on a supported stable line and budget recurring upgrades. Package-time fuses and ASAR integrity: load [Electron hardening](references/platform-traps.md#electron-security-defaults).
- Validate and sanitize all IPC inputs in the main process.
- Restrict `webContents.loadURL` to known origins; never load arbitrary remote content.

**Key anti-patterns**:
- `nodeIntegration: true` in BrowserWindow options — exposes full Node.js to renderer.
- Disabling `webSecurity` to work around CORS — opens the app to remote code execution.
- Loading remote URLs in the main renderer without origin restrictions.
- Passing unsanitized user input through IPC to Node.js APIs.

## Tauri Architecture

Tauri apps pair a **Rust backend** with a **webview frontend** (the OS-native webview, not bundled Chromium).

**Core design**:
- Rust backend defines commands (`#[tauri::command]`) exposed to the frontend via an IPC bridge.
- Frontend can be any web framework (React, Svelte, Vue, vanilla) — Tauri is frontend-agnostic.
- IPC is capability-scoped (Tauri 2's permission system, not the old v1 allowlist): only explicitly granted commands and scopes are available per window/origin. See [references/tauri-2-migration.md](references/tauri-2-migration.md).
- Plugin system for file system, shell, dialog, notification, clipboard, and custom extensions.
- Since Tauri 2.0 (stable Oct 2024), the same codebase also targets iOS and Android — evaluate this before reaching for React Native/Flutter if the team already owns a Tauri desktop app and mobile parity is "good enough," not full native.
- **Sidecar pattern**: bundle a separate native binary (a Python service, a compiled CLI, a heavier compute engine) alongside the app and invoke it as a child process from the Rust backend (`tauri-plugin-shell`'s sidecar API) — useful when logic can't or shouldn't be ported to Rust/JS.

Security advantages over Electron (no Node.js in the frontend, an explicitly configured CSP, capability-scoped IPC, smaller attack surface) and tradeoffs (cross-platform webview differences, Linux WebKitGTK fragmentation, smaller plugin ecosystem, Rust required, mobile plugin parity still catching up): [references/framework-selection.md](references/framework-selection.md#tauri-security-advantages-and-tradeoffs).

## Desktop-Specific Concerns

Use framework dialogs for file access (never raw `fs` in the renderer), follow each platform's tray/menu-bar and shortcut conventions, register protocol handlers and file associations deliberately, and treat local storage as the source of truth with sync-and-merge rather than fetch. Details for file system, tray and menus, native integrations, and offline-first: [references/desktop-integration.md](references/desktop-integration.md).

## Distribution and Updates

**Update recovery gate.**

An updater is production-ready only when the previous signed build can be restored after download failure, signature rejection, crash-on-launch, or incompatible local-data migration. Test interrupted download, offline launch, downgrade protection, and rollback on each supported OS. Keep application-data migrations backward compatible for at least the rollback window, or explicitly block auto-update until recovery is possible.

Sign for every target OS: macOS Developer ID plus `notarytool` notarization (`altool` is removed), Windows Authenticode via Azure Artifact Signing or a hardware-token/HSM EV/OV certificate, and the Linux channel's own trust model. Pick one auto-update toolchain per framework (Tauri updater with Minisign keys, `electron-updater` on NSIS, or Electron's built-in `autoUpdater` with Squirrel.Windows/MSIX, Sparkle 2 on macOS) and prefer hosted update endpoints over a bespoke server. Signing detail, update-server burden, installers, auto-update mechanisms, and app-store trade-offs: [references/distribution-and-signing.md](references/distribution-and-signing.md).

## Known Traps

- Developing only on one operating system and discovering packaging, permissions, or rendering failures after release.
- Treating auto-update as a later enhancement when desktop users will quickly diverge onto stale and insecure builds.
- Treating OS webviews as interchangeable: WebKit (macOS/Linux) and WebView2 (Windows) differ in CSS support, font rendering, and media codec availability — test on all three platforms before shipping.
- Shipping protocol handlers, file associations, or deep links without validating hostile input, duplicate launches, and auth callback flow.
- Depending on filesystem paths, tray behavior, or window chrome that only match one platform's conventions.
- Leaving crash reporting, update rollback, and corrupted local-state recovery undefined until after the first production incident.

## Common Anti-Patterns

- **Choosing from generic size/RAM figures** — compare equivalent release builds including webview dependencies and all child processes; unverified benchmarks cannot justify a stack choice.
- **Storing secrets in the renderer process** — use the main/backend process with OS keychain integration (keytar, keyring).
- **Missing auto-update** — desktop apps without auto-update become permanently stale. Implement from day one.
- **Ignoring platform conventions** — macOS expects menus in the menu bar, Cmd+Q to quit, and native title bars. Windows expects different keyboard shortcuts and window chrome. Test on each target platform.
- **Not testing on all target platforms** — webview rendering and native API behavior differ. CI should build and test on macOS, Windows, and Linux.
- **Bundling development dependencies in production** — audit `package.json` dependencies vs devDependencies. Use `electron-builder`'s pruning or Tauri's Rust release profile.
- **Ignoring process crashes** — handle main process crashes gracefully. Implement crash reporting (Sentry, Crashpad).

## Scenarios

1. **New cross-platform app** — Confirm platform targets, team language constraints, and bundle size requirements. Route to the framework decision tree; apply Tauri 2 capability config or Electron security defaults as appropriate.
2. **Tauri 1 to Tauri 2 migration** — Audit the existing `tauri.conf.json` allowlist, run `cargo tauri migrate`, review generated capability files, update all plugin imports from `tauri::api::*` to `@tauri-apps/plugin-*`, and update frontend `invoke` calls to `@tauri-apps/api/core`.
3. **Code signing and notarization pipeline setup** — Confirm platform targets; apply notarytool for macOS (altool was removed), Azure Artifact Signing or an HSM/hardware-token-backed EV/OV cert for Windows (CA/Browser Forum has required hardware-protected private keys for both EV and OV code-signing since June 2023 — software-only cert files are no longer issuable), and GPG for AppImage on Linux. Check `references/platform-traps.md` for current platform requirements.
4. **EU Accessibility Act compliance check** — Scope is a question for qualified counsel; route technical mapping to `software-accessibility` and audit evidence to `qa-testing-accessibility` (see the pointer below).
5. **Auto-update implementation** — Choose the updater for the framework (Tauri updater plugin with a Minisign keypair, electron-updater targeting NSIS with signature verification for electron-builder, or Electron's built-in `autoUpdater` with Squirrel.Windows/MSIX for Forge). Implement from day one; retrofitting auto-update is expensive.
6. **"Do we even need a desktop app?" gate** — Before any of the above, check whether a PWA satisfies the actual requirement (see "Before Reaching for a Framework" above). Saves a packaging/signing/update pipeline entirely when it does.

## EU Accessibility Act

Whether the EAA applies is a question for qualified counsel; technical conformance mapping is in [software-accessibility](../software-accessibility/SKILL.md), legal landscape and audit evidence in [qa-testing-accessibility](../qa-testing-accessibility/SKILL.md), and desktop-specific checks in [platform-traps](references/platform-traps.md#desktop-accessibility-and-the-eu-accessibility-act).

## Navigation

### References
- [references/framework-selection.md](references/framework-selection.md) — Electron vs Tauri vs Flutter Desktop vs .NET MAUI selection guidance; Tauri security advantages and tradeoffs
- [references/desktop-integration.md](references/desktop-integration.md) — file system, tray and menus, native integrations, offline-first
- [references/distribution-and-signing.md](references/distribution-and-signing.md) — packaging, code signing, notarization, installers, auto-update mechanisms, app-store distribution, and update rollout guidance
- [references/platform-traps.md](references/platform-traps.md) — Electron security defaults, WebView2 versioning, macOS / Windows permission changes, desktop accessibility, code signing, and auto-update traps
- [Skill Sources](data/sources.json): curated primary sources for desktop development.

### Related Skills

- [software-frontend](../software-frontend/SKILL.md) — Web frontend frameworks and SPA patterns
- [software-mobile](../software-mobile/SKILL.md) — Mobile app development (iOS, Android, cross-platform)
- [software-backend](../software-backend/SKILL.md) — Backend service patterns (relevant for Electron main process / Tauri Rust backend)
- [software-security-appsec](../software-security-appsec/SKILL.md) — Application security, threat modeling
- [ops-devops-platform](../ops-devops-platform/SKILL.md) — CI/CD pipelines for build and distribution
- [software-architecture-design](../software-architecture-design/SKILL.md) — System-level architecture decisions

## Release Lookups

Before choosing a release, read its support/compatibility notes through [data/sources.json](data/sources.json).
For a signing or update pipeline, verify the chosen channel's eligibility, package requirements, and updater API at the linked distribution sources.
Record the checked release and target OS/architecture in the recommendation; use measured artifacts for footprint claims.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
