# Android Release and Compliance

Treat these as release gates, not cleanup tasks.

## Required checks

- **Target SDK compliance**: As of 2026-07-11, new apps and updates must target API 36 (Android 16) by 2026-08-31, with an extension option to 2026-11-01; existing apps without updates face distribution restrictions if their target falls two major versions behind. Android 17 (API 37) shipped stable 2026-06-16, so the target-API floor is one version behind the latest platform release — this is normal cadence, not a sign the requirement is stale. Verify the exact current requirement and date at [developer.android.com/google/play/requirements/target-sdk](https://developer.android.com/google/play/requirements/target-sdk) before submission; Google has moved this deadline before and a cached page can lag the live policy.
- **16KB page size support**: Mandatory for app updates from 2026-05-01 (extension to 2026-05-31), affecting any app that ships native (`.so`) libraries. The OS runs an app in 16KB backcompat mode if its ELF `LOAD` segments are 4KB-aligned instead of 16KB-aligned; NDK libraries must be recompiled/relinked with 16KB alignment. Test on a 16KB-page-size emulator image, not just a standard 4KB image. Verify current enforcement status at [developer.android.com/guide/practices/page-sizes](https://developer.android.com/guide/practices/page-sizes).
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

Google enforces target SDK requirements on a rolling basis:

- New apps and updates: must target the latest required API level — API 36 (Android 16) as of 2026-08-31, extension to 2026-11-01 (verify: this is Google's rolling policy and the exact level/date changes roughly yearly).
- Existing apps (no updates): may face distribution restrictions if targeting an API level more than roughly one platform version behind the current requirement.
- Wear OS, Android Automotive OS, and Android TV historically get a one-level-lower floor — verify the current exception at submission time rather than assuming last year's rule still holds.

Verify the current timeline at [developer.android.com/google/play/requirements/target-sdk](https://developer.android.com/google/play/requirements/target-sdk) before each release cycle — treat any hardcoded date here, including this one, as due for re-verification once it is more than a few months old.

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
