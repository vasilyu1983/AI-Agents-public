# Android Release and Compliance

Treat these as release gates, not cleanup tasks.

## Required checks

- **Target SDK compliance**: New apps and updates must meet Play's current target-API floor by its annual deadline (an extension is usually available on request); existing apps that stop updating must still meet a lower floor. The floor typically trails the newest platform release by one version — normal cadence, not a sign the requirement is stale. Verify the exact current requirement and date at [developer.android.com/google/play/requirements/target-sdk](https://developer.android.com/google/play/requirements/target-sdk) before submission; Google has moved this deadline before and a cached page can lag the live policy.
- **16KB page size support**: Apps targeting API 35+ must support 16KB memory page sizes on 64-bit devices on Google Play, and Play is phasing in a block on releasing updates that don't — check the page below for the enforcement date. Affects any app that ships native (`.so`) libraries. The OS runs an app in 16KB backcompat mode (with a first-launch user warning) if its ELF `LOAD` segments are 4KB-aligned instead of 16KB-aligned; NDK libraries must be recompiled/relinked with 16KB alignment. Test on a 16KB-page-size emulator image, not just a standard 4KB image. Verify current enforcement status at [developer.android.com/guide/practices/page-sizes](https://developer.android.com/guide/practices/page-sizes).
- **Edge-to-edge enforcement**: Mandatory since `targetSdk` 35 — Android 15+ devices force edge-to-edge rendering once the app targets API 35+; content can render under the status/navigation bars if insets are not handled. The `windowOptOutEdgeToEdgeEnforcement` manifest opt-out is temporary and was disabled starting with Android 16 — do not rely on it as a long-term fix. Handle insets with `WindowInsets`/`Scaffold` padding, not the opt-out flag.
- **Data safety declarations**: Complete the data safety form in Play Console. Declare all data types collected, shared, and their purposes. Must match actual app behavior — Play reviews can reject or suspend for discrepancies.
- **ProGuard/R8 rules + mapping upload**: Release builds must have R8 minification enabled. Upload the `mapping.txt` file to Play Console for each release to enable crash deobfuscation. Test the release build locally before uploading — R8 can strip classes Compose or reflection depends on.
- **Play Integrity**: Integrate the Play Integrity API for anti-abuse verification if the app handles payments, auth tokens, or sensitive user data. Server-side verification of integrity verdicts.
- **App signing (Play App Signing)**: Enroll in Play App Signing. Google manages the app signing key; you retain the upload key. Required for new apps; strongly recommended for existing apps. Reduces risk of key loss.
- **Deobfuscation symbols**: Upload native debug symbols (`.so` files with debug info) alongside the AAB for NDK crash deobfuscation.
- **Permissions**: Declare only permissions the app actually uses. Remove unused permissions from `AndroidManifest.xml`. Runtime permissions must be requested with clear rationale. `ACCESS_FINE_LOCATION`, `CAMERA`, `RECORD_AUDIO` require prominent disclosure.
- **Content rating (IARC)**: Complete the content rating questionnaire in Play Console. Apps without a rating are restricted from certain regions and age groups.
- **Accessibility**: Test with TalkBack enabled. Touch targets must be at least 48dp. Use `contentDescription` on all non-decorative images and icons. Verify color contrast ratios. Test screen reader navigation order.

## Target SDK timeline

Read [Play's target-SDK requirements](https://developer.android.com/google/play/requirements/target-sdk) for the app/update floor, existing-app discoverability floor, extension eligibility and form-factor exceptions before each submission. Do not infer one floor from another or from platform release cadence.

## Target API 37 migration checklist

Use [target-specific changes](https://developer.android.com/about/versions/17/behavior-changes-17) together with [all-app changes](https://developer.android.com/about/versions/17/behavior-changes-all). Select checks by the APIs the app and its SDKs use:

- LAN: request `ACCESS_LOCAL_NETWORK` or adopt a system-mediated picker; test denial.
- Networking: test certificate transparency (enabled by default at target 37), and ECH where both the client library and server support it.
- Large screens: the target-36 opt-out for orientation/resizability/aspect-ratio restrictions ends at target 37; test resizing and saved state.
- Runtime/SDKs: remove reflection on private MessageQueue internals and attempts to mutate `static final` fields; dynamically loaded native libraries must be read-only.
- Widgets: test RemoteViews bitmap/icon memory limits from the source; oversized parcels crash rather than degrade gracefully.
- SMS: use SMS Retriever or User Consent for OTP; ordinary SMS reads/broadcasts can be delayed for non-exempt apps.
- Audio: exercise background playback/focus/volume with the required foreground service and while-in-use capability, or the alarm exemption.

Record device OS, target SDK, affected SDK version and actual evidence for each applicable row; a source review alone does not prove migration success.

## Build and submission posture

- Submit AAB (Android App Bundle), not APK. Play Console requires AAB for new apps. AABs enable dynamic delivery and smaller downloads.
- Re-check Play Console policy requirements close to the release cut.
- Do not rely on old policy dates.
- Keep signing config, package names, and version codes reviewable and explicit.
- Increment `versionCode` for every upload. `versionName` is user-facing; `versionCode` is Play-Console-facing.

## Extensions and SDK risk

- **Wear OS, Android Auto, Android TV**: Each is a separate compatibility surface with its own guidelines, required features, and review criteria. Do not assume a phone app runs correctly on extended surfaces.
- **Third-party SDKs**: Do not assume a third-party SDK is Compose-compatible, R8-safe, or supports the target API level without checking its current docs or issue tracker.
- **SDK console declarations**: If using listed SDKs (advertising, analytics), verify they have completed their own data safety declarations as required by Google.

## Play Store policy highlights

- **Families Policy**: Apps targeting children must comply with Designed for Families requirements (no behavioral advertising, COPPA/GDPR-K compliance, appropriate content rating).
- **Subscriptions**: Must offer easy cancellation. Auto-renewal terms must be clear. Grace periods and account hold should be handled gracefully.
- **User data**: Privacy policy URL required. Data handling must match data safety declarations. Data deletion request mechanism required for apps that collect user data.
- **Ads**: Ad SDKs for children-targeted apps must use Google-certified ad networks only. Deceptive ads (fullscreen interstitials on accidental tap) are policy violations.
- **Store listing**: Screenshots and descriptions must accurately represent current app functionality. Keyword stuffing and misleading metadata are policy violations.

## Release evidence

Require:

- release build (AAB) proof
- emulator proof for core flows on target API level
- real-device proof where hardware or permissions matter
- ProGuard/R8 mapping uploaded to Play Console
- documented unresolved issues, if any

## Avoid

- discovering data safety or permissions issues at the final upload step
- rolling new third-party SDKs into a rewrite without a compatibility check
- treating "works on emulator" as complete release proof
- forgetting to increment `versionCode` before upload
