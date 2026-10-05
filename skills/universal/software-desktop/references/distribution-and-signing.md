# Distribution And Signing

Use this file when the request is about releasing desktop apps. Re-verify signing-service names, pricing, and eligibility at the primary sources below before quoting them — these details move faster than most of this skill.

## Minimum Release Checklist

- Sign builds for every target OS.
- Notarize macOS apps distributed outside the App Store.
- Verify auto-update signatures before shipping the updater.
- Test install, upgrade, rollback, and uninstall paths on each platform.
- Decide who owns the update server (or confirm you're using a hosted option) before first release — retrofitting update infrastructure after users are on an un-updatable build is expensive.

## Platform Notes

- **macOS**: notarization via `notarytool` (the only supported path — Apple stopped accepting `altool` notarization uploads in November 2023) and the hardened runtime matter. For Developer ID distribution, require notarization and staple the ticket for offline Gatekeeper checks; assessment can also depend on user/admin policy.
- **Windows**: since June 2023, CA/Browser Forum rules require EV *and* OV code-signing private keys to live in a hardware token or HSM — plain software certificates are no longer issuable, which breaks naive CI signing setups. Microsoft's cloud-native answer is **Azure Artifact Signing** (GA under that name; it launched in preview as "Trusted Signing") — it signs from CI with no physical token, is available for Public Trust certificates to organizations in a listed set of regions and to individual developers in fewer countries than organizations (look up Microsoft's current eligibility list); it requires a paid Azure subscription and issues no EV certificates, so SmartScreen reputation still builds per file hash. It is the default recommendation for new pipelines when eligible. A traditional CA-issued EV/OV cert with a hardware token/HSM remains the fallback when Artifact Signing's eligibility rules don't fit. Signed installers reduce SmartScreen friction; Smart App Control (introduced in Windows 11 22H2; starts in evaluation mode, and recent Windows updates allow enabling it without a clean install) blocks unsigned or low-reputation executables on machines where it is on.
- **Linux**: package format choice depends on the expected distribution channel and sandbox model (AppImage = portable + optional GPG signature, Flatpak/Snap = store-managed trust and confinement).

## Update-Server Operational Burden

Running your own update endpoint is not "just a URL" — it carries ongoing costs teams routinely underestimate:

- Custody of the signing key(s) used to sign update manifests (Minisign/Ed25519 for Tauri, code-signing cert for electron-updater payloads).
- TLS certificate renewal and endpoint uptime — a down update server doesn't just delay updates, it can hang app startup if the client blocks on a check.
- Staged/canary rollout and the ability to halt or roll back a bad release before it reaches 100% of users.
- Per-target endpoint correctness (`windows-x86_64`, `darwin-aarch64`, etc.) — serving the wrong binary to the wrong target silently corrupts installs.

Prefer hosted options (GitHub Releases for Electron via `electron-updater`, a static object-store endpoint for Tauri) until you specifically need staged rollout percentages or enterprise-only channels that hosted options don't support.

## Installers, Auto-Update, and App Stores

**Installer creation**:
- macOS: DMG (drag-to-Applications), PKG (scripted install). Use `create-dmg` or `electron-builder`.
- Windows: NSIS, Inno Setup, or MSI. `electron-builder` and Tauri bundler handle these.
- Linux: AppImage (portable), Flatpak (sandboxed), Snap (Ubuntu store), .deb/.rpm (distro-specific).

**Auto-update mechanisms**:
- Electron: `electron-updater` with GitHub Releases, S3, or custom server; target NSIS on Windows. Supports differential updates and signature verification.
- **Squirrel.Windows is a toolchain choice, not a dead end** — Electron's built-in `autoUpdater` still supports Squirrel.Windows (electron-winstaller / Forge maker) and MSIX, while electron-builder's `electron-updater` flow targets NSIS and does not support Squirrel. Pick one toolchain and stay on it; check the upstream Squirrel.Windows repo's recent activity before depending on upstream fixes.
- Tauri: built-in updater plugin (`tauri-plugin-updater`) with mandatory Minisign (Ed25519) signature verification and configurable per-target endpoints. For existing v1 installations, follow the [migration-compatible artifact setting](https://v2.tauri.app/plugin/updater/) and test an update using the installed public key; do not rotate keys without a transition that existing clients can verify.
- macOS native: Sparkle 2 (adds sandboxed-app support and a modern install pipeline) for non-Electron/non-Tauri apps, or `tauri-plugin-sparkle-updater` / WinSparkle equivalents.
- Delta updates reduce download size for frequent releases.
- **Operational burden of self-hosting an update server**: signature-key custody, TLS-cert renewal, staged/canary rollout, and the ability to halt a bad release are real ongoing costs — most teams underestimate this until a bad build needs to be pulled. GitHub Releases (Electron) or a static object-store endpoint (Tauri) removes most of that burden versus a bespoke update server; only build custom infrastructure when you need staged rollout percentages or enterprise-specific channels the hosted options don't support.

**App store distribution**:
- Mac App Store: requires the App Sandbox entitlement and Apple review. Some Electron/Tauri APIs (raw filesystem access outside sandbox containers, some IPC/child-process patterns) are restricted or need sandbox-safe rewrites. Trade-off: MAS buys discoverability, trusted-install psychology, and Apple-run payments, at the cost of review latency, commission and commercial terms to check at Apple's applicable program, and giving up your own update cadence/channel (App Store review turnaround, not your release pipeline, gates ship speed). Direct distribution (notarized DMG/PKG) keeps full control of updates and payments but forfeits Store discovery and requires you to run your own trust/update story end-to-end.
- **Microsoft Store MSIX route:** check [individual onboarding](https://learn.microsoft.com/en-us/windows/apps/publish/whats-new-individual-developer) for the free-registration flow and current eligibility; company accounts have separate terms. For an accepted MSIX Store submission, Microsoft signs the package without a publisher signing fee: [MSIX signing options](https://learn.microsoft.com/en-us/windows/msix/package/signing-package-overview). This does not sign independently distributed EXE/MSI files; retain Artifact Signing or a CA route for those. Store certification, packaging requirements, and update policy still apply.
- Snap Store: straightforward for Linux; auto-update built in, but Snap's confinement model can restrict filesystem/device access similarly to sandboxing.

## Notarization Log and Architecture Matrix

Use [Apple's custom workflow](https://developer.apple.com/documentation/security/customizing-the-notarization-workflow) to retain the submission ID and fetch the JSON log, including after an accepted submission:

```bash
xcrun notarytool log "$SUBMISSION_ID" \
  --keychain-profile "YOUR_NOTARIZATION_PROFILE" notarization-log.json
```

Triage each issue's path, architecture, and message against [Apple's common failures](https://developer.apple.com/documentation/security/resolving-common-notarization-issues): missing/invalid nested signatures, timestamp, hardened runtime, or `get-task-allow`. Repair, re-sign inside-out, and resubmit; staple only after acceptance. Keep credentials out of commands and logs shared for diagnosis.

A universal2 macOS release contains arm64 and x86_64 slices in every applicable native executable, helper, library, and sidecar; a single universal main binary is insufficient. Inspect actual executables with `lipo -archs`, merge before signing, and test arm64 natively plus x86_64 on Intel when Intel is supported (Rosetta on Apple silicon is additional coverage). An arm64-only release excludes Intel: declare that platform boundary. See [Apple's universal binary guide](https://developer.apple.com/documentation/apple-silicon/building-a-universal-macos-binary).

| Build choice | Release checks |
|---|---|
| universal2 | Both slices in nested native code; both architectures install, launch, update, and verify signature/ticket |
| separate macOS arm64/x86_64 | Correct artifact/update endpoint per architecture; test each supported target |
| Wails standalone app | Follow [Wails prerequisites](https://wails.io/docs/gettingstarted/installation/); Go binary plus frontend assets still relies on the target OS webview/dependencies, and needs platform signing/packaging |
| Avalonia self-contained app | Publish for a specific .NET RID with `--self-contained true`; bundled .NET does not bundle every OS native library. Verify [Avalonia deployment](https://docs.avaloniaui.net/docs/deployment/) and packaged dependencies per target; test trimming separately |
