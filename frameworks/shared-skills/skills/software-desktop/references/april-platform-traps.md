# Platform Traps For Desktop Applications

Verified platform-specific traps, breaking changes, and compliance requirements. Cross-reference with `distribution-and-signing.md` and `framework-selection.md` for broader context. This file was last substantively verified against primary sources in **July 2026** — OS-version-specific sections (macOS Sequoia/15, Windows 11 24H2) describe the entitlement/permission changes introduced at those releases; re-check current release notes for anything shipped after them (e.g. macOS 26 "Tahoe" or later Windows 11 feature updates) before treating version-pinned claims as current.

## Table of Contents

1. [Tauri 2 Migration Breaking Changes](#tauri-2-migration-breaking-changes)
2. [Electron Security Defaults](#electron-security-defaults)
3. [WebView2 Versioning on Windows](#webview2-versioning-on-windows)
4. [WebKitGTK Fragmentation on Linux](#webkitgtk-fragmentation-on-linux)
5. [macOS 15 Sequoia Entitlement Changes](#macos-15-sequoia-entitlement-changes)
6. [Windows 11 24H2 Permission Shifts](#windows-11-24h2-permission-shifts)
7. [EU Accessibility Act Enforcement](#eu-accessibility-act-enforcement)
8. [Code Signing Pipeline Changes](#code-signing-pipeline-changes)
9. [Auto-Update Mechanisms](#auto-update-mechanisms)

---

## Tauri 2 Migration Breaking Changes

Tauri 2 shipped in October 2024 and is now the stable baseline. If you are on Tauri 1.x, every item below is a breaking change.

### Capability System Rewrite (allowlist to capabilities)

Tauri 1 used a flat `tauri.conf.json` allowlist to permit IPC surface:

```json
// Tauri 1 — allowlist pattern (removed in Tauri 2)
"tauri": {
  "allowlist": {
    "all": false,
    "fs": { "readFile": true, "scope": ["$APP/*"] },
    "dialog": { "open": true }
  }
}
```

Tauri 2 replaces the allowlist entirely with a capability system. Each capability file lives in `src-tauri/capabilities/` and is a JSON file that grants specific permissions to specific windows or remote origins:

```json
// src-tauri/capabilities/main-window.json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-window",
  "description": "Capabilities for the main application window",
  "windows": ["main"],
  "permissions": [
    "fs:read-files",
    "dialog:open"
  ]
}
```

Anti-patterns:
- Granting `shell:execute` or `fs:write-all` without scope restrictions — Tauri 2 allows fine-grained scope. Use it.
- Copying `allow-all` capability files from examples into production builds — this defeats the security model.
- Forgetting to declare capabilities for remote URLs if your app loads any remote content — the permission is window-scoped and origin-aware.

Migration path from Tauri 1 to Tauri 2:
1. Run `npx @tauri-apps/cli migrate` (or `cargo tauri migrate`). It generates capability files from your existing allowlist.
2. Review each generated capability file — the migrator is conservative but may over-grant.
3. Replace any `"all": true` in legacy allowlist entries with the minimum capability set.
4. Test on all target platforms; WebView2 (Windows) sometimes handles CSP headers differently from WebKit.

### Plugin API Changes

Tauri 2 moves all first-party plugins out of the core crate into separate, versioned packages under `@tauri-apps/plugin-*`. Every plugin import path changed:

| Tauri 1 import | Tauri 2 package |
|---|---|
| `tauri::api::dialog` | `@tauri-apps/plugin-dialog` |
| `tauri::api::fs` | `@tauri-apps/plugin-fs` |
| `tauri::api::shell` | `@tauri-apps/plugin-shell` |
| `tauri::api::notification` | `@tauri-apps/plugin-notification` |
| `tauri::api::http` | `@tauri-apps/plugin-http` |
| `tauri::api::global_shortcut` | `@tauri-apps/plugin-global-shortcut` |
| `tauri::api::clipboard` | `@tauri-apps/plugin-clipboard-manager` |
| `tauri::updater` | `@tauri-apps/plugin-updater` |

On the Rust side, plugin registration moved to the builder pattern:

```rust
// Tauri 2 plugin registration
tauri::Builder::default()
    .plugin(tauri_plugin_fs::init())
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_shell::init())
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
```

Anti-patterns:
- Importing from `tauri::api::*` paths in Tauri 2 — they no longer exist.
- Using `tauri-plugin-*` crates from crates.io at `0.x` versions alongside a `tauri` `2.x` dependency — version incompatibilities cause silent build failures.

### IPC and Command Invocation Changes

The frontend `invoke` API signature changed. In Tauri 2, argument serialization is stricter:

```typescript
// Tauri 2 — invoke with typed arguments
import { invoke } from '@tauri-apps/api/core';

const result = await invoke<string>('read_file', { path: '/tmp/test.txt' });
```

The key change: the second argument is always the full payload object. The command must declare matching Rust struct field names (snake_case is serialized as camelCase automatically by serde).

---

## Electron Security Defaults

These are mandatory settings. None are optional in a production app.

### Required BrowserWindow Configuration

```javascript
const win = new BrowserWindow({
  webPreferences: {
    contextIsolation: true,      // REQUIRED — renderer cannot access Node.js globals
    nodeIntegration: false,      // REQUIRED — no Node.js in renderer
    sandbox: true,               // STRONGLY RECOMMENDED — OS-level sandbox for renderer
    webSecurity: true,           // never set to false in production
    preload: path.join(__dirname, 'preload.js'),
    additionalArguments: [],     // never pass secrets or tokens here
  }
});
```

Why each setting matters:
- `contextIsolation: true` — prevents renderer-world scripts from accessing the preload world or Node.js APIs. The default changed to `true` in Electron 12; explicit declaration is still required because legacy configs may override it.
- `nodeIntegration: false` — if this is `true`, any JavaScript running in the renderer (including content injected via XSS) has full access to Node.js APIs including `child_process.exec`.
- `sandbox: true` — applies the OS-level Chromium sandbox to the renderer process.
- `webSecurity: true` — disabling this allows cross-origin requests from the renderer and removes CORS enforcement. This is a common quick-fix for local dev that must never reach production.

### Content Security Policy

Set a restrictive CSP via `session.setPermissionRequestHandler` and `webContents` headers:

```javascript
session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      'Content-Security-Policy': [
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
      ]
    }
  });
});
```

Anti-patterns:
- `script-src 'unsafe-eval'` — allows `eval()` and `Function()` constructor, which are common XSS payloads.
- `script-src *` — allows loading scripts from any origin.
- Omitting CSP entirely — any remote content loaded via `loadURL` is in scope.

### Navigation Restrictions

```javascript
win.webContents.on('will-navigate', (event, url) => {
  if (!url.startsWith('https://your-trusted-origin.com') && url !== 'about:blank') {
    event.preventDefault();
  }
});

win.webContents.setWindowOpenHandler(({ url }) => {
  shell.openExternal(url); // open in browser, not new Electron window
  return { action: 'deny' };
});
```

---

## WebView2 Versioning on Windows

Tauri on Windows uses the Microsoft WebView2 runtime, which ships separately from the OS on Windows 10 and is bundled with Windows 11.

### Key Versioning Facts

- WebView2 Evergreen runtime: auto-updates silently via Windows Update. Most consumer machines have it.
- WebView2 Fixed Version: opt-in mode where you bundle a specific WebView2 version with your app. Larger installer size (~150 MB) but no surprise regressions from runtime updates.
- The installer generated by `cargo tauri bundle` on Windows includes a bootstrapper that installs WebView2 if missing.

Anti-patterns:
- Shipping without a WebView2 bootstrapper — enterprise Windows 10 machines often have WebView2 blocked by group policy.
- Using WebView2 Fixed Version without a documented update process — you inherit the security patching responsibility for the bundled runtime.
- Relying on CSS features available in Chrome but not in the current evergreen WebView2 — always test on Windows with a WebView2 runtime version that matches your minimum floor.

### WebView2 and CSS/API Gaps

WebView2 tracks Chromium but is not identical to the Chrome release on the same date:
- `dialog` element: fully supported in WebView2 since approximately Chromium 99.
- CSS `color-scheme`: supported but may render differently in high-contrast mode on Windows 11.
- `navigator.userAgent`: contains `Edg/` suffix — guard your user-agent detection code.

---

## WebKitGTK Fragmentation on Linux

Tauri (and any other WebView-based Linux app) depends on system WebKitGTK, and the Linux ecosystem is mid-transition between two incompatible API generations:

- `webkit2gtk-4.0` (uses `libsoup2`) — the version Tauri 1.x targets.
- `webkit2gtk-4.1` (uses `libsoup3`) — the version Tauri 2.x requires.

**Distro timeline (verify current status before relying on this):**
- Ubuntu 24.04 LTS and Fedora 40 dropped the `4.0` **development** package (the runtime library may still be present for existing apps, but you cannot build against it).
- Ubuntu 22.04 LTS ships both `4.0` and `4.1` in parallel through its support window (into 2027), so it is a safe build target for either Tauri major.
- Older LTS images (e.g. Ubuntu 20.04) may lack `4.1` entirely, blocking Tauri 2.x builds without a backport or container-based build environment.
- Upstream WebKitGTK plans to sunset `4.0` entirely; treat any date given for this as provisional and re-check the distro's package repository directly.

Anti-patterns:
- Assuming "it built on my machine" transfers to your CI runner or your users' distro — pin your CI image to the oldest distro you claim to support and build there, not just on the latest LTS.
- Shipping a single generic Linux binary and assuming WebKitGTK is present system-wide — bundle dependency detection or document the required package explicitly in your install instructions.
- Treating Windows (WebView2, evergreen, low fragmentation risk since Microsoft ships and updates it centrally) and Linux (WebKitGTK, distro-packaged, real fragmentation risk) as symmetrical risks — they are not; budget more Linux QA time for any Tauri app that supports Linux.

---

## macOS 15 Sequoia Entitlement Changes

### Hardened Runtime Requirements

macOS 15 (Sequoia, shipped September 2024) tightens the hardened runtime requirements for notarized apps:

- `com.apple.security.cs.allow-jit` — required for apps that use JIT compilation (includes some Electron versions that use V8's JIT). Apple Notarization Service rejects unsigned JIT usage.
- `com.apple.security.cs.disable-library-validation` — required if your app loads third-party dylibs or plugins not signed by your team.
- `com.apple.security.files.user-selected.read-write` — required for file system access granted via open/save panels on macOS 15. Tauri apps using `tauri-plugin-fs` without this entitlement will silently fail on protected paths.

### Network Access Entitlement

macOS 15 introduces stricter enforcement of the `com.apple.security.network.client` entitlement for sandboxed apps:
- Outbound network connections require `com.apple.security.network.client: true` in `entitlements.plist`.
- Inbound connections require `com.apple.security.network.server: true`.

### Local Network Access Dialog

macOS 14 introduced a local network access permission prompt. macOS 15 enforces it more strictly.

Anti-patterns:
- Suppressing the local network dialog by connecting via `localhost` numeric address instead of `.local` — Apple has closed this workaround in macOS 15.
- Omitting `NSLocalNetworkUsageDescription` from `Info.plist` — the OS will block the connection.

---

## Windows 11 24H2 Permission Shifts

Windows 11 24H2 (released October 2024) introduced several permission model changes relevant to desktop apps.

### Location Access

The location API now requires an explicit manifest declaration for MSIX packages:

```xml
<Capabilities>
  <DeviceCapability Name="location"/>
</Capabilities>
```

For non-MSIX EXE distributions, the Windows 11 24H2 geolocation permission dialog appears on first use and the user can revoke it per-app from Settings.

### Camera and Microphone

24H2 unified the camera/microphone permission surface across Win32 and UWP apps. Electron apps accessing `getUserMedia` will now surface the same system-level permission dialog that UWP apps show.

Anti-patterns:
- Requesting camera/microphone access at app startup rather than at the moment of use — a startup request with no visible reason raises rejection rates.
- Not testing `getUserMedia` on a clean 24H2 installation — permission state from older Windows versions does not carry over after an in-place upgrade.

### Smart App Control

Windows 11 24H2 default installs have Smart App Control (SAC) enabled. SAC blocks unsigned or low-reputation executables. Authenticode code signing is now effectively mandatory for any app distributed outside the Microsoft Store on 24H2.

---

## EU Accessibility Act Enforcement

The European Accessibility Act (EAA) Directive 2019/882 entered enforcement for new products in EU member states on **28 June 2025**. Desktop B2C apps distributed in the EU are in scope.

### Who Is in Scope

- B2C desktop applications sold or made available in the EU.
- Apps that are part of a service covered by the EAA (e-commerce, banking, transport, e-books, communications services).
- Existing products have until 28 June 2030 for conformance, but new products sold after 28 June 2025 must conform immediately.

### Technical Requirements

The EAA mandates conformance with EN 301 549, which references WCAG 2.1 Level AA for software user interfaces.

Key criteria for desktop apps:
- **Keyboard accessibility** — all functionality operable without a mouse. Focus order must be logical and visible.
- **Screen reader support** — on macOS, VoiceOver; on Windows, NVDA and JAWS. Use native accessibility APIs or ARIA where applicable.
- **Colour contrast** — minimum 4.5:1 for normal text, 3:1 for large text (WCAG 2.1 AA 1.4.3).
- **Resize and reflow** — UI must not clip or lose functionality when text is scaled to 200% or the window is resized.
- **Alternative text** — decorative images suppressed from assistive technology; informative images have text alternatives.
- **Error identification** — form validation errors identified in text, not only by colour.
- **Timeout warnings** — users warned before sessions expire and given the option to extend.

### Framework-Specific Guidance

Electron:
- Chromium's accessibility tree surfaces automatically to OS accessibility APIs. Do not disable it.
- Use semantic HTML (`<button>`, `<nav>`, `<main>`) in your renderer — these map to correct ARIA roles.
- Test with NVDA (Windows) and VoiceOver (macOS).

Tauri:
- The webview inherits OS accessibility APIs from the platform webview (WebKit / WebView2). The same HTML semantics apply.
- Run `axe-core` or `playwright-axe` in your test suite.

Native macOS (SwiftUI):
- SwiftUI controls are accessible by default. Custom views must implement `AccessibilityRepresentation` or use `.accessibilityLabel`, `.accessibilityHint`, `.accessibilityValue`.

Native Windows (WinUI 3):
- WinUI 3 controls expose UIA (UI Automation) properties. Custom controls must implement `AutomationPeer`.

Anti-patterns:
- Relying solely on WCAG audits of your web counterpart — desktop apps have additional EN 301 549 criteria for platform software.
- Treating accessibility as a final-stage polish task — retroactive fixes to layout and interaction patterns are expensive.
- Ignoring keyboard focus on modal dialogs — focus must be trapped inside modal dialogs and returned to the trigger element on close.

---

## Code Signing Pipeline Changes

### macOS: Notarytool (Xcode 26)

`altool` was deprecated in November 2023 and removed. Notarytool is the only supported notarization method as of Xcode 15+.

Current notarization pipeline:

```bash
# Step 1: Sign the app bundle
codesign --force --deep --options runtime \
  --entitlements entitlements.plist \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  YourApp.app

# Step 2: Create zip for submission
ditto -c -k --keepParent YourApp.app YourApp.zip

# Step 3: Submit for notarization
xcrun notarytool submit YourApp.zip \
  --keychain-profile "YOUR_NOTARIZATION_PROFILE" \
  --wait

# Step 4: Staple the ticket
xcrun stapler staple YourApp.app
```

Store credentials in CI via:

```bash
xcrun notarytool store-credentials "YOUR_NOTARIZATION_PROFILE" \
  --apple-id "$APPLE_ID" \
  --team-id "$APPLE_TEAM_ID" \
  --password "$APPLE_APP_SPECIFIC_PASSWORD"
```

Anti-patterns:
- Passing `--apple-id` and `--password` directly in CI logs — use `--keychain-profile` or masked environment variables.
- Skipping `--options runtime` on the `codesign` command — notarization will reject apps not signed with the hardened runtime.
- Not stapling the ticket — stapling embeds the notarization proof so the app passes Gatekeeper checks offline.

### Windows: Hardware-Protected Keys and Azure Artifact Signing

- Since June 1, 2023, CA/Browser Forum baseline requirements mandate that **both EV and OV** code-signing private keys be generated and held in a hardware crypto module (FIPS 140-2 Level 2 / Common Criteria EAL 4+ or better) — a secure USB token, an on-prem HSM, or a cloud HSM the CA has verified. Software-only `.pfx` signing certificates are no longer issuable for new orders.
- Microsoft's own answer to this is **Azure Artifact Signing** (the current, generally-available name; it launched in preview as "Trusted Signing"). It runs the HSM on Microsoft's side, so CI can sign without a physical token attached to a build agent. It is GA for eligible US/Canada/EU/UK businesses and, more recently, verified individual developers — check current eligibility before assuming it fits your org.
- For apps that ship kernel-mode drivers (VPN clients, hardware interface tools): Microsoft still requires an Extended Validation (EV) code-signing certificate, and new kernel-mode drivers must be submitted to and signed by Microsoft via the Hardware Dev Center portal — Azure Artifact Signing does not (as of this writing) cover kernel-mode driver submission; verify current status before assuming otherwise.
- OV-equivalent signing (now via Artifact Signing or a hardware-token EV/OV cert) is sufficient for user-mode code, including standard desktop apps and installers.

### Linux: AppImage Signing Patterns

AppImage does not have a centralized store with mandatory signing, but signature verification is supported:

```bash
# Sign an AppImage with GPG
gpg --detach-sign --armor YourApp-x86_64.AppImage
# Creates YourApp-x86_64.AppImage.asc

# Embed the signature using appimagetool with --sign flag
SIGN=1 SIGN_KEY=YOUR_KEY_ID appimagetool AppDir YourApp-x86_64.AppImage
```

Users verify with:
```bash
gpg --verify YourApp-x86_64.AppImage.asc YourApp-x86_64.AppImage
```

For Flatpak (Flathub) and Snap (Snapcraft Store), signing is handled by the store infrastructure.

---

## Auto-Update Mechanisms

### Squirrel (Electron on Windows) — deprecated, avoid for new projects

Squirrel.Windows was the traditional auto-update mechanism for Electron apps on Windows:
- Installs to user profile (`%LOCALAPPDATA%`) — no admin elevation required.
- Uses delta packages (NuGet format) to minimize download size.

**Current status: the upstream Squirrel.Windows project is unmaintained** (issues and PRs are no longer reviewed or merged), and `electron-updater`'s simplified auto-update flow does not support it on Windows — only the NSIS target gets that simplified path. Treat Squirrel as legacy: existing Squirrel-based apps keep working, but do not start a new project on it, and plan a migration to NSIS for anything still on it.

Anti-patterns:
- Adopting Squirrel for a new Electron app in 2026 — use `electron-builder`'s NSIS target with `electron-updater` instead.
- Using Squirrel without `--squirrel-install`, `--squirrel-updated`, and `--squirrel-uninstall` event handlers — these events fire during install/update/uninstall; the app must handle them and exit cleanly, or the install silently fails.
- Shipping the first version without testing the update path — Squirrel delta packages require the old version to still be present.

### electron-updater (electron-builder)

`electron-updater` is the more actively maintained option and supports GitHub Releases, S3, and generic HTTP.

```javascript
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall();
});
```

Anti-patterns:
- Not verifying update signatures — `electron-updater` supports signature validation. Skipping it allows MITM attacks to deliver arbitrary code.
- Calling `quitAndInstall()` without user confirmation for non-background apps.

### Tauri Updater Plugin

Tauri 2 ships `tauri-plugin-updater` as a separate plugin. The Tauri updater requires a `pubkey` and verifies the update signature before applying it — enforced at compile time.

```json
// tauri.conf.json
{
  "plugins": {
    "updater": {
      "endpoints": ["https://your-update-server.com/{{target}}/{{arch}}/{{current_version}}"],
      "pubkey": "your-public-key-here"
    }
  }
}
```

Anti-patterns:
- Using a test keypair in production — generate a fresh keypair (`tauri signer generate`) for each production environment.
- Pointing the update endpoint at a non-HTTPS URL — Tauri enforces HTTPS for update endpoints.
- Forgetting to configure update endpoints per-target (`windows-x86_64`, `darwin-aarch64`, etc.) — serving the wrong binary silently corrupts installs.
