# Platform Traps For Desktop Applications

Load for platform-specific release/security failures. Use `tauri-2-migration.md` for migration, `distribution-and-signing.md` for release decisions, and check the target OS release notes at the permission or compatibility decision.

## Table of Contents

1. [Tauri 2 Migration Breaking Changes](#tauri-2-migration-breaking-changes)
2. [Electron Security Defaults](#electron-security-defaults)
3. [WebView2 Versioning on Windows](#webview2-versioning-on-windows)
4. [WebKitGTK Fragmentation on Linux](#webkitgtk-fragmentation-on-linux)
5. [macOS Entitlements and Local Network Privacy](#macos-entitlements-and-local-network-privacy)
6. [Windows Permissions](#windows-permissions-api-and-package-identity-matter)
7. [Desktop Accessibility and the EU Accessibility Act](#desktop-accessibility-and-the-eu-accessibility-act)
8. [Code Signing Pipeline Changes](#code-signing-pipeline-changes)
9. [Auto-Update Mechanisms](#auto-update-mechanisms)

---

## Tauri 2 Migration Breaking Changes

For a Tauri 1→2 migration or capability/plugin API question, load [tauri-2-migration.md](tauri-2-migration.md). Keep migration examples there.

---

## Electron Security Defaults

These are mandatory settings. None are optional in a production app.

### Required BrowserWindow Configuration

```javascript
const win = new BrowserWindow({
  webPreferences: {
    contextIsolation: true,      // REQUIRED — renderer cannot access Node.js globals
    nodeIntegration: false,      // REQUIRED — no Node.js in renderer
    sandbox: true,               // renderer default since Electron 20; keep enabled
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

### Release Support and Package Hardening

At release planning, read [Electron's support policy and schedule](https://www.electronjs.org/docs/latest/tutorial/electron-timelines): verify the supported stable lines, minor/patch requirements, and major cadence rather than assuming an old line still receives fixes. Reserve upgrade work alongside app releases.

Before code signing, configure [Electron fuses](https://www.electronjs.org/docs/latest/tutorial/fuses): disable `RunAsNode`, `EnableNodeOptionsEnvironmentVariable`, and `EnableNodeCliInspectArguments` unless the product needs them. Regression-test features that depend on these paths, particularly `child_process.fork`.
For supported macOS/Windows builds using ASAR, enable `EnableEmbeddedAsarIntegrityValidation` together with `OnlyLoadAppFromAsar`, and ensure packaging embeds the integrity header hash. Verify [ASAR platform and packager support](https://www.electronjs.org/docs/latest/tutorial/asar-integrity); unsupported targets need a documented alternative. ASAR alone is packaging, not integrity protection.

### Content Security Policy

Set a restrictive CSP through response headers (permission handlers separately govern API access):

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
  if (new URL(url).origin !== 'https://app.example.com' && url !== 'about:blank') {
    event.preventDefault();
  }
});

win.webContents.setWindowOpenHandler(({ url }) => {
  const parsed = new URL(url);
  if (parsed.protocol === 'https:' && parsed.hostname === 'docs.example.com') {
    shell.openExternal(url); // allow only intended external destinations
  }
  return { action: 'deny' };
});
```

---

## WebView2 Versioning on Windows

Tauri on Windows uses the Microsoft WebView2 runtime, which ships separately from the OS on Windows 10 and is bundled with Windows 11.

### Key Versioning Facts

- WebView2 Evergreen runtime: updates through Microsoft Edge Update; enterprise policy can restrict updates. Check the target deployment policy.
- WebView2 Fixed Version: opt-in mode where you bundle a specific WebView2 version with your app. Larger installer size (measure the selected runtime) but no surprise regressions from runtime updates.
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

Tauri 1 targets the libsoup2 `webkit2gtk-4.0` API; Tauri 2 requires libsoup3 `webkit2gtk-4.1`. [WebKitGTK 2.52 removed libsoup2 in March 2026](https://webkitgtk.org/2026/03/18/webkitgtk-2.52-highlights.html).

Before promising Linux support, check the chosen distro's repositories for the required runtime and development packages. Build on the minimum supported distro and test there; a newer developer machine does not prove compatibility. Fixed Windows WebView2 runtimes also need a security-update owner.

---

## macOS Entitlements and Local Network Privacy

Two different mechanisms get conflated here — keep them apart.

### Hardened Runtime Exceptions (notarized, direct-distribution apps)

Notarization requires the hardened runtime (`--options runtime`). Hardened-runtime exceptions are opt-in entitlements; add only the ones you need:

- `com.apple.security.cs.allow-jit` — for code that JITs in-process (Electron/V8 main and renderer processes).
- `com.apple.security.cs.disable-library-validation` — only if you load third-party dylibs or plugins not signed by your team.

### App Sandbox Entitlements (Mac App Store only)

`com.apple.security.files.user-selected.read-write`, `com.apple.security.network.client` and `com.apple.security.network.server` are long-standing App Sandbox entitlements, not macOS 15 changes. They matter only when the app is sandboxed (required for the Mac App Store); a notarized, non-sandboxed Developer ID app does not need them.

### Local Network Privacy

Local network privacy arrived on macOS in **macOS 15** (Apple TN3179). Apps that talk to devices on the local network (Bonjour, `.local`, LAN IPs) trigger a user prompt.

Anti-patterns:
- Omitting `NSLocalNetworkUsageDescription` from `Info.plist` — the prompt has no explanation and users decline it; declare the Bonjour service types you browse in `NSBonjourServices`.
- Assuming a workaround (e.g. connecting by IP instead of `.local`) avoids the prompt — Apple documents no such exemption; test on a clean macOS 15+ machine.

---

## Windows Permissions: API and Package Identity Matter

**Location:** the packaged `location` capability is not a new universal 24H2 requirement. Check the specific API and packaging model. [Microsoft's Wi-Fi/location changes](https://learn.microsoft.com/en-us/windows/win32/nativewifi/wi-fi-access-location-changes) describe precise-location consent for affected Wi-Fi calls, including a per-app prompt in eligible user processes and denial results to handle.

**Camera/microphone:** do not promise that 24H2 gives every Win32/Electron app a UWP-style system dialog. [Microsoft's camera guidance](https://support.microsoft.com/en-us/windows/privacy/manage-app-permissions-for-a-camera-in-windows) distinguishes Store-app controls from the shared desktop-app access toggle. An Electron permission handler is an additional app-level decision. Test the target build, denied access, device availability, and packaged versus unpackaged installation; upgrade permission-state loss is unverified and must not be assumed.

### Smart App Control

Smart App Control (SAC) was introduced in Windows 11 22H2 (not 24H2). It starts in evaluation mode, and recent Windows updates allow enabling it without a clean install. Where it is on, SAC blocks unsigned or low-reputation executables, so Authenticode signing is effectively mandatory for apps distributed outside the Microsoft Store.

---

## Desktop Accessibility and the EU Accessibility Act

Whether the EAA applies to a desktop product is a question for qualified counsel; the technical conformance mapping is owned by `software-accessibility` and the legal landscape and audit evidence by `qa-testing-accessibility`. This section keeps only desktop-specific guidance.

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

### macOS: Notarytool

Apple stopped accepting `altool` notarization uploads in November 2023. Use `notarytool` or the Notary API; the `altool` binary also serves other workflows, so do not equate this boundary with removal of the tool.

Current notarization pipeline:

```bash
# Step 1: Sign the app bundle
# Sign nested code inside-out (helpers, frameworks, sidecars first), then the app.
# Apple: do not pass --deep when signing. electron-builder / the Tauri bundler do this for you.
codesign --force --options runtime --timestamp \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  YourApp.app/Contents/Frameworks/Helper.app   # repeat per nested item
codesign --force --options runtime --timestamp \
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
- Microsoft's own answer to this is **Azure Artifact Signing** (the current, generally-available name; it launched in preview as "Trusted Signing"). It runs the HSM on Microsoft's side, so CI can sign without a physical token attached to a build agent. Public Trust certificates are available to organizations in a listed set of regions, and to individual developers in fewer countries — look up Microsoft's current eligibility list. It needs a paid Azure subscription, issues no EV certificates, and SmartScreen reputation still builds per file hash.
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

### Squirrel.Windows (Electron Forge / electron-winstaller)

Squirrel.Windows is the Windows backend of Electron's built-in `autoUpdater` (alongside MSIX, which Electron detects automatically):
- Installs to user profile (`%LOCALAPPDATA%`) — no admin elevation required.
- Uses delta packages (NuGet format) to minimize download size.

**Status: a toolchain choice, not deprecated.** Electron's `autoUpdater` docs still support Squirrel.Windows (built with electron-winstaller or Forge's Squirrel maker) and MSIX. electron-builder's `electron-updater` does not support Squirrel — it targets NSIS. So the decision is Forge + built-in `autoUpdater` (Squirrel/MSIX) versus electron-builder + NSIS + `electron-updater`. Check the upstream Squirrel.Windows repo's recent activity before depending on upstream fixes.

Anti-patterns:
- Mixing toolchains — e.g. expecting `electron-updater` to update a Squirrel-installed app; migrating between Squirrel and NSIS needs an explicit migration release.
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
