# iOS Release and Compliance

Treat these as release gates, not cleanup tasks.

> This file covers the **technical** release gates (privacy manifests, entitlements, CI parity). For the **App Store Review Guidelines** themselves — the content/business/design/legal rules a reviewer applies, including the 4.3(b) saturated-category gate, 4.2 minimum-functionality, 5.1.1(v) account deletion, and AI-generated-content rules — see [../../software-ios-design/references/app-review-guidelines-map.md](../../software-ios-design/references/app-review-guidelines-map.md).

## Required checks

- privacy manifest coverage for the app and listed SDKs
- required-reason API declarations where applicable
- third-party SDK compliance against Apple's current requirements
- entitlement review for push, background execution, associated domains, keychain sharing, app groups, and extension surfaces
- accessibility smoke check on current devices
- deep link and push behavior verified on the intended targets

## Build and submission posture

- Re-check Apple submission guidance close to the release cut.
- Do not rely on old policy dates.
- Keep signing, bundle identifiers, and entitlement changes reviewable and explicit.

## Release signing and distribution

- Automatic signing is supported; use manual signing only when the team's workflow requires it. Xcode can re-sign and repackage an archive during distribution, so a development-signed archive alone does not prove the final export is invalid.
- Inspect the exported App Store/TestFlight app and its matching provisioning profile: release exports must not enable debugging; push-enabled apps require `aps-environment = production`. An app without the push capability need not have that entitlement. See [Apple distribution guidance](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases).
- Inspect the exact newest `.xcarchive`; don't use a generic `find ... .app` that can hit an older one.
- In Organizer choose the TestFlight/App Store distribution method (or Custom → App Store Connect); `Release Testing` exports for registered devices. Confirm the available labels in the installed Xcode.
- Validation can fail on generated `Info.plist` (e.g., missing `UISupportedInterfaceOrientations~ipad`); review generated plist, not just UI.
- Encryption prompt: Apple/system crypto only → `None of the algorithms mentioned above`. Suppress with `ITSAppUsesNonExemptEncryption = NO` in plist.

## CI-parity rules for a fresh-clone build

Apple's CI (Xcode Cloud and most fresh-clone pipelines) does a clean `git clone` into a fresh workspace and runs `xcodebuild` directly against the committed `.xcodeproj`. Anything that depends on local-machine state breaks silently. Treat these as design rules, not optional hygiene:

- **Generated resources referenced from the pbxproj must be in the repo.** If `project.yml` declares `INFOPLIST_FILE: <path>/Info.generated.plist` (or any generated JSON, manifest, or locale export), either commit the file (`git add -f` if the containing folder is ignored) or regenerate it inside `ci_scripts/ci_post_clone.sh`. Fresh-clone CI does not run your local `generate-*.sh` scripts by default.
- **Gitignored folders with tracked files are a landmine.** When a folder is listed in `.gitignore` but some files inside it were added to the index before the ignore rule, new files added to the same folder silently never reach the remote. The pbxproj then references files that exist locally but not on CI. Fix: either unignore the folder, or force-track each required file with `git add -f` and set a pre-commit check that warns on new unforced files in that folder.
- **Xcode Cloud supports three hooks:** `ci_post_clone.sh`, `ci_pre_xcodebuild.sh`, and `ci_post_xcodebuild.sh` inside `ci_scripts` next to the project/workspace. Choose the hook for the phase that needs the output, make it executable with a shebang, and fail nonzero on missing required configuration. Hooks run from `ci_scripts`, so resolve repository paths explicitly; do not assume hook-created files persist between phases. Check [Apple custom-build-script guidance](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts) when choosing output locations. Never generate production settings with localhost fallbacks.
- **`TARGETED_DEVICE_FAMILY` is baked into the binary.** Changing it in `project.yml` (for example from `"1,2"` iPhone+iPad to `"1"` iPhone-only) does not retroactively update App Store Connect's device-family expectations — you must upload a new Archive built after the change. Until that new build is attached to the version, ASC will keep demanding iPad screenshots.

Fast local repro for a fresh-clone CI failure:

```bash
git clone --depth 1 <origin> /tmp/fresh && cd /tmp/fresh
# run whatever your CI does, in order:
bash ci_scripts/ci_post_clone.sh
xcodebuild -scheme <Scheme> -configuration Release archive \
  -archivePath /tmp/fresh.xcarchive
```

If this fails, CI will fail. Fix it here, not by squinting at Xcode Cloud logs.

## Extensions and SDK risk

- Treat app extensions as a separate compatibility surface.
- Do not assume a third-party SDK is extension-safe, simulator-safe, or beta-Xcode-safe without checking its current upstream docs or issue tracker.

## Release evidence

Require:

- archive or distribution build proof
- simulator proof for core flows
- real-device proof where hardware or permissions matter
- documented unresolved issues, if any

## Avoid

- discovering privacy or entitlement issues at the final archive step
- rolling new third-party SDKs into a rewrite without a compatibility check
- treating “works on simulator” as complete release proof
