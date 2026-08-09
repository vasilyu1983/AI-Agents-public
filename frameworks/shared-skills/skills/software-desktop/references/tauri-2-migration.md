# Tauri 2 Migration and Production Guide

Production traps, capability system changes, and platform notes for Tauri 2.x (verify current at tauri.app/releases).

## Table of Contents

- [Tauri 2 Capability System](#tauri-2-capability-system)
- [Plugin API Breaks from Tauri 1](#plugin-api-breaks-from-tauri-1)
- [WebView2 Versioning on Windows](#webview2-versioning-on-windows)
- [EU Accessibility Act for Desktop Apps](#eu-accessibility-act-for-desktop-apps)
- [Tauri 2 Production Traps](#tauri-2-production-traps)

---

## Tauri 2 Capability System

Tauri 2.0 (stable October 2024) replaces the v1 allowlist with a **capability-based permission model**. This is the most significant architectural change for migrating apps.

### How capabilities work

Each window or web view is granted a named capability. Capabilities list the specific plugin permissions the window is allowed to invoke.

**File structure:**

```
src-tauri/
  capabilities/
    main-window.json   ← per-window capability file
  tauri.conf.json
```

**Example capability file (`src-tauri/capabilities/main-window.json`):**

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-window",
  "description": "Permissions for the main application window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:allow-read-text-file",
    "fs:allow-write-text-file",
    "dialog:allow-open",
    "dialog:allow-save",
    "shell:allow-open"
  ]
}
```

**Granular scoping (filesystem example):**

```json
{
  "identifier": "main-window",
  "windows": ["main"],
  "permissions": [
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [{ "path": "$APPDATA/**" }]
    }
  ]
}
```

Path variables: `$APPDATA`, `$APPCONFIGDIR`, `$RESOURCE`, `$TEMP`, `$HOME` (restricted on mobile).

### Migrating from v1 allowlist

v1 `tauri.conf.json` allowlist:

```json
{
  "tauri": {
    "allowlist": {
      "fs": { "readFile": true, "writeFile": true, "scope": ["$APPDATA/**"] },
      "dialog": { "open": true }
    }
  }
}
```

v2 equivalent: create `src-tauri/capabilities/main-window.json` with the permissions above, then remove the `allowlist` key from `tauri.conf.json`.

Use the official migration CLI: `npx @tauri-apps/cli migrate` (handles most mechanical changes).

---

## Plugin API Breaks from Tauri 1

### Plugin packages renamed

| v1 package | v2 package |
|------------|------------|
| `@tauri-apps/api/tauri` (invoke) | `@tauri-apps/api/core` |
| `@tauri-apps/api/fs` | `@tauri-apps/plugin-fs` |
| `@tauri-apps/api/dialog` | `@tauri-apps/plugin-dialog` |
| `@tauri-apps/api/shell` | `@tauri-apps/plugin-shell` |
| `@tauri-apps/api/notification` | `@tauri-apps/plugin-notification` |
| `@tauri-apps/api/http` | `@tauri-apps/plugin-http` |
| `@tauri-apps/api/os` | `@tauri-apps/plugin-os` |

### invoke() change

```ts
// v1
import { invoke } from '@tauri-apps/api/tauri';

// v2
import { invoke } from '@tauri-apps/api/core';
```

### Event API change

```ts
// v2: listen returns a Promise<UnlistenFn>
import { listen } from '@tauri-apps/api/event';
const unlisten = await listen('my-event', (event) => { ... });
// call unlisten() to clean up
```

### Rust command signatures

v2 commands require explicit `State` extraction; the global `AppHandle` pattern changed:

```rust
// v2
#[tauri::command]
async fn my_command(app: tauri::AppHandle, state: tauri::State<'_, MyState>) -> Result<String, String> {
    Ok("hello".into())
}
```

---

## WebView2 Versioning on Windows

Tauri 2 on Windows uses the system WebView2 Runtime (Chromium-based, provided by Microsoft).

**Key points:**

- WebView2 is **auto-updated** by Windows Update on Windows 10/11 — you do not control the version in production, and Windows 11 ships it by default (Windows 10 needs the bootstrapper below).
- Minimum required at Tauri 2.0's stable release: WebView2 Runtime 109+ (maps to Chromium 109). Treat this as a historical floor, not a current minimum — Tauri's own minimum has likely risen since; verify against the current Tauri docs before relying on it.
- Current stable evergreen runtime: verify at [Microsoft Edge WebView2 release notes](https://learn.microsoft.com/en-us/microsoft-edge/webview2/release-notes/) — because it auto-updates independently of your app, this number changes on Microsoft's schedule, not yours.

**Bootstrapping strategy in installer:**

```nsis
; In NSIS / WiX — detect and install WebView2 if missing
; Recommended: use MicrosoftEdgeWebview2Setup.exe /silent /install
; Tauri's tauri-bundler adds this automatically when using the MSI/NSIS bundler
```

**Fixed version (offline/enterprise):**

Use the `Evergreen Standalone Installer` or the `Fixed Version` runtime. Fixed Version is ~150 MB — embed only when the target environment has no internet access.

**Minimum OS support:** WebView2 is supported on Windows 7, 8.1, 10, 11. Windows 7/8.1 support ends with WebView2 runtime 109; newer runtimes require Windows 10+.

**Testing across versions:** Use GitHub Actions `windows-2019` (WebView2 runtime ~100) vs `windows-2022` (current runtime) to surface version-specific bugs.

---

## EU Accessibility Act for Desktop Apps

The European Accessibility Act (EAA, Directive 2019/882) entered force **28 June 2025**. It applies to software distributed as a product to EU consumers, including desktop applications.

**Covered desktop categories under Annex I:**

- E-commerce software (checkout flows, product browsers)
- Banking and financial service applications
- E-book readers
- Computers and operating systems (when offered to consumers)

**Technical standard:** EN 301 549 v3.2.1, which references WCAG 2.1 AA for web content embedded in applications (WebView-based apps like Tauri/Electron are web content by this standard).

**Tauri-specific implications:**

1. All WebView-rendered content must meet WCAG 2.1 AA (WCAG 2.2 AA is recommended for new builds)
2. Native OS window controls (title bar, system dialogs) are inherently accessible — do not replace with custom WebView chrome
3. Custom drag regions (`data-tauri-drag-region`) that also contain interactive elements must preserve keyboard access
4. `tauri-plugin-window-state` saved positions must not cause windows to open off-screen (violates 2.4.11)

**Microenterprise exemption:** < 10 employees AND ≤ €2 M annual turnover — exempt from service obligations; products still covered.

**Timeline:** Products placed on the EU market after 28 June 2025 must comply at launch. Existing products have until 28 June 2030.

---

## Tauri 2 Production Traps

- **`tauri migrate` does not handle custom plugins:** First-party plugins are migrated; any custom Rust plugin using v1 `tauri::plugin::Builder` must be manually updated to v2's `tauri::plugin::TauriPlugin` with `Permissions` derive.
- **macOS Hardened Runtime + WebView:** Tauri 2 enables Hardened Runtime by default for notarization. The `com.apple.security.cs.allow-jit` entitlement is required if your WebView executes JavaScript from dynamic sources — missing it causes a silent JIT fallback with 10–100× slower JS.
- **Windows arm64:** Native Windows arm64 (aarch64) support landed incrementally across Tauri 2.x minor releases (verify the exact version at [tauri.app/release](https://v2.tauri.app/release/) — treat any specific version/date pin as provisional). Only the NSIS installer target supports arm64; the NSIS *installer stub itself* still runs via x86 emulation even though your app binary is native arm64. You also need the "C++ ARM64 build tools" component in Visual Studio and the `aarch64-pc-windows-msvc` Rust target.
- **CSP and IPC:** Tauri 2 IPC uses a custom `ipc://localhost` scheme. Content Security Policy rules that block `connect-src ipc:` break all `invoke()` calls — a silent failure with no console error.
- **Updater v2:** `tauri-plugin-updater` v2 signs update manifests using the **Minisign** format (still Ed25519 signatures under the hood, just a different key/signature serialization and CLI than v1's `tauri-bundler`-generated keys). v1 and v2 key files are not interchangeable — generate a fresh keypair with `tauri signer generate` and update your signing pipeline before switching, regardless of the fact both ultimately use Ed25519.
