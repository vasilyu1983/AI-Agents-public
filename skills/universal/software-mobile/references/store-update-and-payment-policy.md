# Store Update and Payment Policy Decisions

Decision logic for two store-policy areas that change often: over-the-air (OTA) code updates and external-payment / anti-steering rules. This file holds the durable reasoning; the rules themselves live on Apple and Google pages that are revised without a version bump. Read the linked primary page before every release that touches either area, and quote it rather than this file.

## Contents

- [OTA and Code-Push Updates](#ota-and-code-push-updates)
- [External Payments and Anti-Steering](#external-payments-and-anti-steering)
- [Primary Pages to Check](#primary-pages-to-check)

## OTA and Code-Push Updates

### What the stores allow

The two stores use different clauses; a framework vendor's OTA feature does not establish store permission.

- **Apple.** [Guideline 2.5.2](https://developer.apple.com/app-store/review/guidelines/) restricts downloaded code that introduces or changes functionality. The [Developer Program License Agreement](https://developer.apple.com/support/terms/apple-developer-program-license-agreement/) separately permits interpreted code subject to purpose, OS-security and storefront restrictions. Apply both; the license exception is not a blanket App Review exemption.
- **Google.** [Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/16559646) restricts self-updates and downloaded executable files. It exempts code running in a VM/interpreter with indirect Android API access, while requiring runtime-loaded interpreted code to comply with Play policies.

Read the applicable revision before deciding. The store-build default below is a conservative delivery rule for new features; it does not assert that Google's interpreter clause bans every new interpreted feature.

### Decision

```text
Proposed change
  ├─ Touches native code, native modules, entitlements, permissions, or Info.plist/manifest?
  │     → Store build. OTA cannot ship it, and a JS bundle that expects the new native code will crash old binaries.
  ├─ Adds a feature or flow App Review has not seen, or changes what the app is for?
  │     → Default to a store build; evaluate the specific store clauses rather than treating both policies as identical.
  ├─ Bug fix, copy/content change, styling, or tuning inside an already-reviewed feature?
  │     → Candidate for OTA after policy and runtime-compatibility checks; being interpreted is insufficient by itself.
  └─ Unsure?
        → Ship through the store. Resolve the policy uncertainty before distributing the change.
```

Content that the app already fetches from a backend (articles, prices, remote config, feature-flag values for reviewed features) is not a code update. Use flags to turn reviewed features on or off, not to hide unreviewed features from review.

### Tooling options

- **Expo EAS Update** for Expo and React Native apps. Updates are scoped by runtime version and channel.
- **CodePush-style services** (self-hosted or third-party) for bare React Native. Check that the service is still maintained before adopting it.
- **Flutter.** Dart is compiled ahead of time in release builds. Code push needs a dedicated third-party toolchain; check its current store-compliance statement before adopting it.
- **Native Swift/Kotlin.** No code push. Use remote config and server-driven UI for reviewed features only.

### Operating rules

- **Pin compatibility.** Tie each update to the exact native runtime (EAS runtime version, or a binary version for CodePush-style tools). Never serve a bundle to a binary whose native layer it was not built against.
- **Stage the rollout.** Start with internal users, then a small percentage, and watch crash-free sessions and key-flow errors before widening.
- **Keep rollback one step away.** Know the command or dashboard action that republishes the previous bundle. Rehearse it before the first production OTA. Make sure the client falls back to the embedded bundle when a downloaded update crashes on launch.
- **Log what shipped.** Record the update ID, the runtime version, and who published it. Surface the update ID in crash reports so an incident can be traced to a bundle, not only a binary.
- **Do not use OTA to dodge a rejection.** If App Review rejected a behavior, an OTA that reintroduces it is the clearest violation case.

## External Payments and Anti-Steering

### What changes, and why this file has no numbers

Both stores now allow some form of external purchase links or alternative billing. What is allowed varies by storefront or country, needs an entitlement or program enrollment, and has changed repeatedly after court rulings and regulation. Fee levels, eligible regions, and deadlines are not written here on purpose. Read them from the primary pages at decision time.

Durable facts from the primary pages, worded as they appear there:

- **Apple.** Guideline 3.1.1 still requires in-app purchase to unlock digital features or content. Guideline 3.1.1(a) lets developers apply for entitlements to link to their own website for purchases. The guidelines say those entitlements "are not required for developers to include buttons, external links, or other calls to action in their United States storefront apps". Outside the United States storefront, calls to action toward other purchase methods are prohibited unless a region-specific entitlement (StoreKit External Purchase Link, Music Streaming Services, or the reader-app External Link Account Entitlement under 3.1.3(a)) applies.
- **Google.** The Payments policy requires Google Play's billing system for digital goods, with listed exceptions such as physical goods and services. It lets developers in eligible countries or regions offer an alternative billing system, or lead users outside the app through an external offers program, if they enroll in the applicable program.

### Decision

```text
Selling digital goods or services in-app?
  ├─ No (physical goods/services, or other listed exceptions) → store billing not required; confirm the exception still applies.
  └─ Yes
      ├─ 1. List target storefronts/countries by revenue share.
      ├─ 2. For each, look up on the primary page: is a link-out or alternative billing allowed,
      │      does it need an entitlement/enrollment, what disclosure sheet or UI is mandated,
      │      and what commission or fee still applies to external purchases.
      ├─ 3. Model net revenue: external conversion rate after the extra step, times price, minus
      │      any remaining store fee and payment-processor cost, against the in-app purchase baseline.
      │      Use your own funnel data, not a blog post's.
      ├─ 4. Decide per region: store billing only, store billing plus link-out, or alternative billing.
      │      Keep store billing available wherever a program requires it alongside the alternative.
      └─ 5. Gate it: one canonical entitlement registry for web and store purchases, a server-side
             storefront/country check (never a client-side locale guess), and a kill switch that
             reverts a region to store billing only if the rules change.
```

### Traps

- **Inferring a region from device locale.** Use the storefront or country that the store APIs report, because eligibility follows the account's storefront and not the language setting.
- **Treating a ruling as a policy.** A court order or press report is not the rule. The implementing entitlement terms or program page are. Wait for them.
- **Forgetting reporting duties.** Some programs require transaction reporting to the store even when the store does not process the payment. Read the program terms for reporting as well as fees.
- **One global paywall build.** A link-out that is legal in one storefront is a rejection in another. Branch server-side by storefront.

## Primary Pages to Check

- Apple App Review Guidelines (2.5.2, 3.1.1, 3.1.1(a), 3.1.3, 4.7): <https://developer.apple.com/app-store/review/guidelines/>
- Apple Developer Program License Agreement (section 3.3.1(B)): <https://developer.apple.com/support/terms/apple-developer-program-license-agreement/>
- Apple StoreKit External Purchase entitlements: <https://developer.apple.com/documentation/storekit/external_purchase>
- Google Play Device and Network Abuse policy: <https://support.google.com/googleplay/android-developer/answer/16559646>
- Google Play Payments policy: <https://support.google.com/googleplay/android-developer/answer/9858738>
- Google Play user choice and alternative billing programs by country: <https://support.google.com/googleplay/android-developer/answer/13821247>
- Google Play external offers program enrollment: <https://support.google.com/googleplay/android-developer/answer/14372887>
- Expo EAS Update documentation: <https://docs.expo.dev/eas-update/introduction/>
