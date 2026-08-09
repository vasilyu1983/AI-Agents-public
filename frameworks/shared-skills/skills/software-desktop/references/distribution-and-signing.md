# Distribution And Signing

Use this file when the request is about releasing desktop apps. Re-verify signing-service names, pricing, and eligibility at the primary sources below before quoting them — these details move faster than most of this skill.

## Minimum Release Checklist

- Sign builds for every target OS.
- Notarize macOS apps distributed outside the App Store.
- Verify auto-update signatures before shipping the updater.
- Test install, upgrade, rollback, and uninstall paths on each platform.
- Decide who owns the update server (or confirm you're using a hosted option) before first release — retrofitting update infrastructure after users are on an un-updatable build is expensive.

## Platform Notes

- **macOS**: notarization via `notarytool` (the only supported path — `altool` was removed by Apple in November 2023) and the hardened runtime matter. Gatekeeper blocks unnotarized apps outright; staple the ticket so offline Gatekeeper checks still pass.
- **Windows**: since June 2023, CA/Browser Forum rules require EV *and* OV code-signing private keys to live in a hardware token or HSM — plain software certificates are no longer issuable, which breaks naive CI signing setups. Microsoft's cloud-native answer is **Azure Artifact Signing** (GA under that name; it launched in preview as "Trusted Signing") — it signs from CI with no physical token, is available to eligible US/Canada/EU/UK businesses and verified individuals, and is the default recommendation for new pipelines. A traditional CA-issued EV/OV cert with a hardware token/HSM remains the fallback when Artifact Signing's eligibility rules don't fit. Signed installers avoid SmartScreen friction; Windows 11 24H2's Smart App Control blocks unsigned or low-reputation executables by default outside the Microsoft Store.
- **Linux**: package format choice depends on the expected distribution channel and sandbox model (AppImage = portable + optional GPG signature, Flatpak/Snap = store-managed trust and confinement).

## Update-Server Operational Burden

Running your own update endpoint is not "just a URL" — it carries ongoing costs teams routinely underestimate:

- Custody of the signing key(s) used to sign update manifests (Minisign/Ed25519 for Tauri, code-signing cert for electron-updater payloads).
- TLS certificate renewal and endpoint uptime — a down update server doesn't just delay updates, it can hang app startup if the client blocks on a check.
- Staged/canary rollout and the ability to halt or roll back a bad release before it reaches 100% of users.
- Per-target endpoint correctness (`windows-x86_64`, `darwin-aarch64`, etc.) — serving the wrong binary to the wrong target silently corrupts installs.

Prefer hosted options (GitHub Releases for Electron via `electron-updater`, a static object-store endpoint for Tauri) until you specifically need staged rollout percentages or enterprise-only channels that hosted options don't support.
