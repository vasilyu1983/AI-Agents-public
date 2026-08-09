# Framework Selection

Use this file when the request is deciding which desktop stack to adopt. Verify version-specific claims at [tauri.app/releases](https://tauri.app/release/), [electronjs.org](https://releases.electronjs.org/), and [learn.microsoft.com/dotnet/maui](https://learn.microsoft.com/en-us/dotnet/maui/supported-platforms) before quoting them as current.

## Zero-th Question: Is Desktop the Right Answer?

Before this table, confirm the app actually needs OS-level integration (filesystem/hardware access, background services, native menus/tray, offline-first local storage, enterprise MSI/App Store deployment). If the requirement is "installable, works offline-ish, no deep OS hooks," a PWA is usually cheaper to build, ship, and update than any option below — it has no code-signing, notarization, or update-server surface at all.

## Defaults

| Scenario | Default |
|---|---|
| Web team, many existing web components, need deepest native integration or largest plugin ecosystem | Electron |
| Need smaller bundles, lower memory, stronger default security posture, team can absorb some Rust | Tauri |
| Already shipping Flutter mobile, want to reuse that codebase on desktop | Flutter Desktop (strongest on macOS; expect fewer production-grade Windows/Linux packages) |
| .NET team wanting one XAML codebase across mobile + desktop, Windows/macOS only | .NET MAUI (no native Linux target as of mid-2026; an Avalonia-powered Linux/browser backend is in preview) |
| Need Tauri/Electron-class web UI *and* iOS/Android from one codebase | Tauri 2.x (mobile targets stable since Oct 2024, though plugin parity with desktop is still catching up) |
| Deep platform integration and native UX, single-OS target | Native framework for the target OS (SwiftUI/AppKit, WPF/WinUI 3, GTK/Qt) |

## Decision Signals

- Choose Electron when Chromium compatibility, the largest plugin/tooling ecosystem, and web hiring leverage outweigh package size and memory footprint.
- Choose Tauri when smaller installers (commonly single-digit-to-low-double-digit MB vs 100MB+ for Electron), lower idle memory (~30-40MB vs ~200-300MB), Rust sidecar logic (bundling a separate native binary as a child process via the shell plugin), and a stronger default security model (capability-scoped IPC, no Node.js in the frontend) are acceptable tradeoffs. On Linux specifically, verify your minimum supported distro ships a compatible WebKitGTK (`4.1`, not the sunsetting `4.0`) before committing.
- Choose Flutter Desktop or .NET MAUI when you already own that ecosystem and want more shared UI than webview shells provide — but confirm platform coverage first: MAUI has no Linux desktop target, and Flutter Desktop's Windows/Linux package ecosystem lags macOS.
- Migrating from Electron to Tauri later is a near-rewrite (different process model, different IPC, no Node.js APIs available) — treat the initial choice as expensive to reverse, not as a "start simple, migrate later" decision.
