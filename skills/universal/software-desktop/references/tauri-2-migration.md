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

Commands can receive `AppHandle` and managed state through injected arguments; this is not by itself a v2 migration break:

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

- WebView2 is **auto-updated** through Microsoft Edge Update on Windows 10/11 — you do not control the version in production, and Windows 11 ships it by default (Windows 10 needs the bootstrapper below).
- Minimum required at Tauri 2.0's stable release: WebView2 Runtime 109+ (maps to Chromium 109). Treat this as a historical floor, not a current minimum — Tauri's own minimum has likely risen since; verify against the current Tauri docs before relying on it.
- Current stable evergreen runtime: verify at [Microsoft Edge WebView2 release notes](https://learn.microsoft.com/en-us/microsoft-edge/webview2/release-notes/) — because it auto-updates independently of your app, this number changes on Microsoft's schedule, not yours.

**Bootstrapping strategy in installer:**

```nsis
; In NSIS / WiX — detect and install WebView2 if missing
; Recommended: use MicrosoftEdgeWebview2Setup.exe /silent /install
; Tauri's tauri-bundler adds this automatically when using the MSI/NSIS bundler
```

**Fixed version (offline/enterprise):**

Use the `Evergreen Standalone Installer` or the `Fixed Version` runtime. Measure the selected Fixed Version payload. The Evergreen Standalone Installer installs an updatable runtime; Fixed Version bundles a runtime whose security updates you own.

**Minimum OS support:** WebView2 is supported on Windows 7, 8.1, 10, 11. Windows 7/8.1 support ends with WebView2 runtime 109; newer runtimes require Windows 10+.

**Testing across versions:** The GitHub Actions `windows-2019` image was retired on 2025-06-30; use a currently supported Windows runner image, and pin an older WebView2 **Fixed Version** runtime in a test job when you need to reproduce version-specific bugs.

---

## EU Accessibility Act for Desktop Apps

Legal scope and conformance mapping: see [software-desktop platform traps](platform-traps.md#desktop-accessibility-and-the-eu-accessibility-act). Tauri-specific checks: custom drag regions must preserve keyboard access; saved window positions must remain reachable after monitor changes; custom window chrome needs accessibility tests.

---

## Tauri 2 Production Traps

- **Migration is partial:** the [official guide](https://v2.tauri.app/start/migrate/from-tauri-1/) explicitly says the migration command does not replace reading the guide; review custom plugins and generated permissions manually.
- **macOS Hardened Runtime + WebView:** Tauri 2 enables Hardened Runtime by default for notarization. Do not add `com.apple.security.cs.allow-jit` by reflex: WKWebView runs page JavaScript in Apple's separate WebContent processes, not in the host app. Add the exception only if profiling a notarized build with and without it shows the host needs it.
- **Windows arm64:** Native Windows arm64 (aarch64) support landed incrementally across Tauri 2.x minor releases (verify the exact version at [tauri.app/release](https://v2.tauri.app/release/) — treat any specific version/date pin as provisional). Only the NSIS installer target supports arm64; the NSIS *installer stub itself* still runs via x86 emulation even though your app binary is native arm64. You also need the "C++ ARM64 build tools" component in Visual Studio and the `aarch64-pc-windows-msvc` Rust target.
- **CSP and IPC:** Tauri 2 IPC uses a custom `ipc://localhost` scheme. Keep `ipc:` and `http://ipc.localhost` in `connect-src` if you write a custom CSP; test `invoke()` under your production CSP rather than assuming how it degrades when the custom-protocol IPC is blocked.
- **Updater migration:** use the official updater guide's `createUpdaterArtifacts: "v1Compatible"` for artifacts consumed by v1 clients. Signature verification cannot be disabled; retain the installed public key or design an authenticated key transition, and test the old-client update path before release.
