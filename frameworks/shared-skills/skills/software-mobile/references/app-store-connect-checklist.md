# App Store Connect — Full Preparation Checklist

## Table of Contents

- [Phase 1: Prerequisites (Before Touching App Store Connect)](#phase-1-prerequisites-before-touching-app-store-connect)
- [Phase 2: App Store Connect — App Record](#phase-2-app-store-connect--app-record)
- [Phase 3: Version Metadata](#phase-3-version-metadata)
- [Phase 4: In-App Purchases & Subscriptions](#phase-4-in-app-purchases--subscriptions)
- [Phase 5: Agreements & Finance](#phase-5-agreements--finance)
- [Phase 6: Build Upload](#phase-6-build-upload)
- [Phase 7: TestFlight](#phase-7-testflight)
- [Phase 8: App Review Preparation](#phase-8-app-review-preparation)
- [Phase 9: Submit](#phase-9-submit)
- [Phase 10: Post-Submission](#phase-10-post-submission)
- [Localization Strategy](#localization-strategy)
- [Automation](#automation)

Use this checklist when preparing an iOS app for App Store submission. It covers every field and setting in App Store Connect, ordered by the typical workflow.

Pair with [mobile-release-checklist.md](../../software-clean-code-standard/assets/checklists/mobile-release-checklist.md) for code-level and testing gates.

---

## Phase 1: Prerequisites (Before Touching App Store Connect)

- [ ] Apple Developer account active and enrolled ($99/year)
- [ ] App ID created in Apple Developer portal with required capabilities (Sign in with Apple, Push Notifications, etc.)
- [ ] Bundle ID matches Xcode project and App Store Connect record
- [ ] Xcode signing configured (Automatic or Manual) and provisioning profiles valid
- [ ] At least one 1024×1024 App Icon in the Xcode asset catalog (`AppIcon.appiconset/`)
- [ ] Privacy Policy page published at a public URL
- [ ] Support page or contact URL published at a public URL

## Phase 2: App Store Connect — App Record

### General > App Information

- [ ] **App Name** (30 chars max) — unique on the App Store
- [ ] **Subtitle** (30 chars max) — concise value prop, not repeating the name
- [ ] **Primary Category** — choose the closest match (e.g., Lifestyle, Entertainment, Health & Fitness)
- [ ] **Secondary Category** (optional but recommended)
- [ ] **Privacy Policy URL** — must be publicly accessible
- [ ] **Content Rights** — confirm you own or license all content

### Trust & Safety > App Privacy

- [ ] **Privacy Policy URL** set (may auto-fill from App Information)
- [ ] **Data Types** declared — click Edit and add every data type your app collects:

Common data types for mobile apps:

| Data Type | Category | Typical Purpose |
|-----------|----------|----------------|
| Email Address | Contact Info | Account creation, auth |
| User ID | Identifiers | App functionality |
| Product Interaction | Usage Data | Analytics |
| Purchase History | Purchases | Subscription management |
| Crash Data | Diagnostics | Stability monitoring |
| Performance Data | Diagnostics | Performance monitoring |
| Coarse Location | Location | Only if using device GPS |

For each type, specify:
- Whether it's linked to user identity
- Whether it's used for tracking (Apple's definition: sharing with third parties for advertising)
- Purpose categories (App Functionality, Analytics, etc.)

- [ ] Click **Publish** after completing data types

### Trust & Safety > Age Rating

Complete the multi-step questionnaire:

| Step | Typical Answer for Non-Game Apps |
|------|----------------------------------|
| Step 1: Features | All NO (no parental controls, no UGC, no messaging, no ads, no unrestricted web) |
| Step 2: Mature Themes | All NONE (no profanity, horror, substances) |
| Step 3: Medical | NONE + NO health topics (unless app provides health/wellness advice) |
| Step 4: Sexuality | All NONE |
| Step 5: Violence | All NONE |
| Step 6: Gambling | All NONE + NO gambling + NO loot boxes |
| Step 7: Confirmation | Keep "Not Applicable", save |

Expected result for most non-game utility/lifestyle apps: **4+**

## Phase 3: Version Metadata

### Version Page (per-version, per-locale)

For each locale you support:

- [ ] **Screenshots** — minimum 3 per required device class. Verify against Apple's current spec at [App Store Connect Help → Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications) before a submission:

| Device Class | Dimensions (portrait) | Required? | Notes |
|-------------|----------------------|-----------|-------|
| iPhone 6.9" (Air / 17 Pro Max / 16 Pro Max / 16 Plus / 15 Pro Max / 15 Plus / 14 Pro Max) | **1260 × 2736** | **Yes (primary)** | Apple's current consolidated class covering all modern Pro Max and Plus devices. Scales down to every smaller iPhone. |
| iPhone 6.5" (11 Pro Max / XS Max / XR / 14 Plus / 13 Pro Max / 12 Pro Max) | **1284 × 2778** | Required if 6.9" not provided | Historic fallback. Current consolidated size; not the older 1242 × 2688. |
| iPhone 6.3" (17 Pro / 17 / 16 Pro / 16 / 15 Pro / 15 / 14 Pro) | 1179 × 2556 | Optional | Listing only — the subscription review screenshot validator rejects this size even though listings accept it. |
| iPhone 6.1" (17e / 16e / 14 / 13 Pro / 13 / 13 mini / 12 Pro / 12 / 12 mini / 11 Pro / XS / X) | 1170 × 2532 | Optional | Listing only. |
| iPhone 5.5" (8 Plus / 7 Plus) | 1242 × 2208 | Only if supporting older devices | Different aspect ratio (0.5625 vs 0.46 for modern iPhones) — a proportional resize from a modern capture does not work, you need a dedicated 5.5" capture. |
| iPad Pro 12.9" (6th gen) | 2048 × 2732 | Only if supporting iPad | |

> **Modern iPhone consolidation note:** Apple periodically consolidates device classes. The 1290 × 2796 "6.7"" size that was primary for a few releases has been folded into the 6.9" class at 1260 × 2736. Always re-fetch the spec page before a submission — a size that was Required a year ago may now be Optional.

Screenshot best practices:
- First 3 screenshots appear on the app installation sheet — make them count
- Use marketing text overlays and device frames for professional appearance
- Show the most compelling screens: hero/dashboard, key features, unique differentiators
- Include a paywall screenshot (required if subscriptions are present)
- Consider localized screenshots for top markets

- [ ] **App Previews** (optional) — up to 3 video previews per device class (15-30 seconds)
- [ ] **Promotional Text** (170 chars max) — can be changed without a new review
- [ ] **Description** (4000 chars max) — structure:
  1. Hook (first 3 visible lines) — what makes your app different
  2. Key features — bullet list
  3. Social proof / accuracy / trust signals
  4. Free tier / pricing transparency
  5. Subscription terms (required if app has subscriptions): pricing, auto-renewal, cancellation, management URL
  6. Privacy Policy and Terms links at bottom
- [ ] **Keywords** (100 chars max, comma-separated, no spaces after commas) — do NOT repeat words from app name or subtitle (Apple indexes those automatically)
- [ ] **What's New** (4000 chars max) — release notes for this version
- [ ] **Support URL** — links to support/contact page
- [ ] **Marketing URL** (optional) — links to marketing website
- [ ] **Version** — typically matches `CFBundleShortVersionString`
- [ ] **Copyright** — e.g., "2026 Your Name"

### Keyword Strategy

- Apple indexes app name + subtitle words automatically — don't waste keyword chars repeating them
- Use singular forms (Apple matches plurals automatically)
- No spaces after commas to maximize character count
- Prioritize: direct search terms > feature terms > intent terms
- Review App Store Connect Analytics after launch to iterate

## Phase 4: In-App Purchases & Subscriptions

### Monetization > Subscriptions

If your app uses auto-renewable subscriptions:

- [ ] **Subscription group** created with a clear name
- [ ] **Products** created with correct Product IDs, pricing, and duration
- [ ] **Subscription Prices** — click the blue `+`, pick a tier (e.g. `USD 6.99` for monthly, `USD 59.99` for yearly), select *All Countries and Regions*, set a start date. Apple auto-converts USD tiers to every local currency. **Must be set** or the product stays in `Missing Metadata`.
- [ ] **Localizations** — display name and description for at least one locale. See *Subscription localization character limits* below.
- [ ] **Review screenshot** uploaded for each product. See *Subscription review screenshot preparation* below.
- [ ] **Review notes** explaining what the subscription unlocks and where the user reaches the paywall
- [ ] Clear **"Missing Metadata"** status on all products — verify by the product's Status pill at the top of the page, which flips to `Prepare for Submission` or `Ready to Submit` once every required field is present
- [ ] **App Store Server Notifications** URL configured (v2 recommended):
  - Production URL
  - Sandbox URL

### Subscription localization character limits

Verified against the live ASC *Edit Localization* dialog's remaining-characters counter. The counter is the source of truth — older Apple documentation still cites a 45-255 range for the description which does not match what the UI enforces.

| Field | Max |
|---|---|
| Subscription Display Name | **35 characters** |
| Subscription Description | **55 characters** |

For CJK scripts (Japanese, Korean, Chinese Simplified), Apple counts code points, not visual width — a 20-code-point Chinese sentence is 20 chars against the 55 max, not 40. For RTL scripts (Arabic, Hebrew), technical Latin proper nouns such as API or SDK names should usually stay Latin; transliterating can obscure the standard being referenced.

Recommended file structure for version-controlled subscription copy:

```
fastlane/metadata/<locale>/subscription.txt
```

One file per locale, INI-style sections named after the ASC product IDs. Example:

```text
# Subscription localization — de (draft, needs native speaker review)
# Character limits: name ≤ 35 chars, description ≤ 55 chars

[PremiumMonthly]
name: Premium Monatlich
description: Erweiterte Funktionen und tägliche Einblicke.

[PremiumAnnual]
name: Premium Jährlich
description: Erweiterte Funktionen und tägliche Einblicke.
```

Fastlane's `deliver` action does not automatically upload subscription localizations — a custom script or the App Store Connect API `POST /v1/subscriptionLocalizations` endpoint is the only path. Because nothing reads these files automatically today, a single `subscription.txt` per locale is cleaner than 4 separate `name.txt` / `description.txt` files nested in per-product subdirectories (a translator editing one language wants every piece of subscription copy for their locale in one file, not four).

### Subscription review screenshot preparation

The *Review Information → Screenshot* field is the subscription-metadata gate that trips up the most submissions. Apple's validator rejects uploads with a catch-all error — **"The dimensions of one or more screenshots are wrong"** — that fires for *any* file it cannot process, not just dimension mismatches. Real causes in order of likelihood:

| Problem | Symptom | Fix |
|---|---|---|
| **Wrong pixel dimensions** | Upload rejected even with a sRGB/8-bit file | Target a *Required* size: `1260 × 2736` (6.9") or `1284 × 2778` (6.5"). **Optional sizes like 1179 × 2556 are rejected by the subscription review validator** even though they are accepted for app listing screenshots — this is an undocumented difference between the two flows. |
| **Display P3 color profile** | Upload rejected at correct dimensions | iPhone screenshots from iPhone 15 Pro and later are captured in Display P3 wide gamut. ASC wants sRGB. A profile-strip produces washed-out colors; you need an actual profile-to-profile conversion. |
| **16-bit depth / HDR** | Same rejection | iPhone HDR screenshots are 16 bits/sample. Downsample to 8-bit. |
| **Alpha channel (RGBA)** | Same rejection | ASC wants RGB only. Flatten. |
| **144 DPI metadata flag** | Same rejection | iPhone screenshots carry a 144 DPI (3x) flag. Set to 72 DPI. |
| **EXIF / XMP metadata present** | Occasional rejection | Strip on re-save. |
| **`.heic` format** | File greyed out in file picker, cannot select | ASC only accepts PNG / JPG / JPEG. Convert to PNG. |

**The one-command fix** — use Python Pillow (preinstalled on most dev Macs via Xcode or Homebrew). Do **not** use `sips --matchTo`; that only updates the profile flag without converting colors, producing washed-out output.

```bash
python3 <<'PY'
from PIL import Image, ImageCms
import io

src = "/Users/you/Downloads/Screenshot.heic"      # or .png from any modern iPhone
dst = "/Users/you/Downloads/review-screenshot.png"

img = Image.open(src)
print(f"source: mode={img.mode} size={img.size}")

# Convert Display P3 → sRGB if the source embeds a color profile
if "icc_profile" in img.info:
    src_profile = ImageCms.ImageCmsProfile(io.BytesIO(img.info["icc_profile"]))
    srgb_profile = ImageCms.createProfile("sRGB")
    img = ImageCms.profileToProfile(img, src_profile, srgb_profile, outputMode="RGB")

# Drop alpha if still present
if img.mode != "RGB":
    img = img.convert("RGB")

# Resize to 6.5" Required fallback (1284 × 2778). Apple scales down from this
# for every smaller device class, so a single 6.5" asset covers everything.
img = img.resize((1284, 2778), Image.LANCZOS)

# Save as 8-bit PNG, 72 DPI, strip extra metadata
img.save(dst, format="PNG", optimize=True, dpi=(72, 72))

out = Image.open(dst)
print(f"saved: mode={out.mode} size={out.size}")
PY
```

Verify with `sips -g all <path>`:

```
samplesPerPixel: 3        ← RGB, no alpha
bitsPerSample:   8        ← not 16
space:           RGB
profile:         sRGB built-in   ← not Display P3
dpiWidth:        72.000    ← not 144
pixelWidth:      1284
pixelHeight:     2778
```

Every line must match or Apple's validator rejects the upload.

**Chicken-and-egg warning:** you cannot capture a real paywall screenshot showing actual GBP/USD prices until the subscription is at least `Ready to Submit`, because the paywall cannot load products until the review screenshot is uploaded. The standard industry workaround is to use a feature-lock card (any screen showing a locked premium feature with an Upgrade CTA) or the 1024 × 1024 app icon as the review screenshot on first submission, then swap it for a real paywall capture on a later metadata update once products are loading.

### Sandbox tester setup

The Sandbox tester must be signed in **at the OS level**, not inside the app. App-level auth is completely separate from StoreKit sandbox access.

1. ASC → **Users and Access → Sandbox → Test Accounts → `+`**
   - Email: any unique string that is not already an Apple ID. **The address does not need to receive mail** — Apple does not verify it during creation. Use a `+` alias on your own domain like `you+sandbox-monthly@yourdomain.com` to sidestep collisions with your real Apple ID.
   - Password: 8+ chars, 1 upper, 1 lower, 1 digit.
   - Region: match the currency tier the tester should see (UK → GBP, US → USD, etc.)
2. On the iPhone:
   - iOS 17+: **Settings → Developer → Sandbox Apple Account → Sign In**
   - iOS 18+: **Settings → App Store → scroll to bottom → Sandbox Account**
   - If the *Developer* menu does not appear, plug the phone into Xcode and run any dev build once — that enables the menu.
3. Sign in with the sandbox tester credentials. This slot is independent from your normal Apple ID sign-in.

### Sandbox propagation delay

After a subscription flips from `Missing Metadata` to `Ready to Submit`, Apple's sandbox catalog takes **15-30 minutes** to propagate. Retrying the paywall immediately after flipping the status will still show "Plans unavailable". Wait, force-quit the app, reopen, tap **Retry**.

### TestFlight is NOT strictly required for sandbox product loading

Apple's billing documentation strongly recommends TestFlight, but a direct `Xcode → Run` build on a physical device *does* load real products from Apple's sandbox catalog as long as:

1. The Sandbox tester is signed in at the OS level (see above)
2. The products are in `Ready to Submit` state in ASC
3. The Paid Apps Agreement is `Active` under *Business → Agreements, Tax, and Banking*
4. The Xcode scheme's *Run → Options → StoreKit Configuration* dropdown is set to **None** (not a local `.storekit` file — that would use local products instead of the real catalog)

This is useful for fast iteration during the first submission, when waiting for a TestFlight build to process is a 20-40 minute bottleneck. Once products are verified loading, switch to TestFlight for the actual gate record.

### Monetization > Pricing and Availability

- [ ] **Base country** set (e.g., United States)
- [ ] Review Apple's auto-generated pricing across storefronts
- [ ] Territory availability configured (usually all territories unless restricted)

## Phase 5: Agreements & Finance

In **Business > Agreements, Tax, and Banking** (direct URL: [https://appstoreconnect.apple.com/business](https://appstoreconnect.apple.com/business)):

- [ ] **Paid Apps Agreement** accepted and showing Status: **Active** (green). Required before any paid app or IAP can be sold.
- [ ] **Tax information** completed for all relevant territories — see *W-8BEN UK Residents Field Guide* below for UK sole traders
- [ ] **Banking information** completed and showing Status: **Active** (not `Processing`) — see *Banking Processing Delay* below
- [ ] **Small Business Program** applied for (optional — reduces Apple's commission from 30% to 15% while eligible)

### The account-level gate is the #1 invisible StoreKit blocker

**Critical cross-reference for Phase 4 (Subscriptions):** if your app has subscriptions in `Ready to Submit` state but StoreKit's `Product.products(for:)` returns an empty array on device (paywall shows "Plans unavailable" or equivalent), **the blocker is almost certainly on this page, not on the subscription products themselves**. Check here *first*, before any subscription-level or device-level diagnosis.

Apple's StoreKit backend refuses to return any IAP products via `Product.products(for:)` when the account-level **Paid Apps Agreement** is in any state other than `Active`. There is no specific Apple error code for this — the API silently returns an empty array, which every iOS client surfaces as "no products available". Every retry returns the same empty array until the agreement flips to Active.

This is undocumented in Apple's public developer guides and is the single most common "everything looks right but nothing works" cause of StoreKit product loading failures. Developers routinely spend hours debugging their code, their subscription configuration, their Sandbox tester, and their device state before realizing the blocker is an account-level legal gate that has nothing to do with any of those.

### Decision table for Paid Apps Agreement status

| Status | Meaning | Next action |
|---|---|---|
| **Active** (green) | Apple is ready to serve IAP from your account | Account-level gate is clear; debug elsewhere (per-product config, Sandbox tester, device state) |
| **Pending User Info** | Apple is waiting on one or more Tax Forms or Banking fields | Scroll down to *Tax Forms* and *Bank Accounts* sections on the same page; complete whatever shows `Missing Tax Info`, `Processing`, or any non-Active status |
| **Waiting for Your Contact** | A specific person on your team needs to accept | Track down the account holder; if it is you, accept the pending terms |
| **Not Started** | Agreement has never been signed | Click into the agreement and complete end-to-end (tax forms, banking, terms acceptance) |
| **Expired** | Apple updated the agreement and the old one lapsed | Re-accept the current version |
| **Action Required** | Apple flagged something for manual attention | Read the inline message and follow the prompts |

If the entire Agreements section is missing from your App Store Connect account, your account is enrolled in the **free Apple Developer** program rather than the paid **Apple Developer Program** ($99/year). Paid program enrollment is a prerequisite for any IAP and can be verified at [developer.apple.com/account](https://developer.apple.com/account). IAP submission is impossible without enrollment.

### Banking Processing Delay (24 hours, undocumented)

When you add or update a bank account on the Agreements page, Apple runs a banking verification batch that takes up to **24 hours** for non-US accounts (typically less for US, longer for some APAC regions). During the window:

- A yellow banner appears at the top of the Agreements page: *"Your banking updates are processing, you should see the changes in 24 hours. You won't be able to make any additional updates until then."*
- Bank Accounts row shows Status: **Processing**
- Paid Apps Agreement row shows Status: **Pending User Info** regardless of tax form status
- **StoreKit returns empty products on device** regardless of per-subscription state
- Additional banking and tax edits are locked during the window

Apple partners with an external financial services provider for international payouts, and that provider runs a daily verification batch during London business hours. A UK account updated in the evening typically clears the following afternoon UK time.

**Critical for release planning:** never schedule a TestFlight gate run, a launch, or a billing-dependent test for a time that assumes banking will clear in less than 24 hours. Plan for the long pole. This is the most common source of "we expected to ship tonight and now we can't" surprises in first-time Apple Developer account activation.

### W-8BEN UK Residents Field Guide

> **Disclaimer:** This is general-case guidance for UK individuals (sole traders) earning App Store royalties. Unusual circumstances (dual residency, corporate structure, multiple income streams) warrant an accountant consultation. Apple's tax processor is automated and does not verify your answers against your actual tax status.

W-8BEN is the US tax form non-US individuals use to certify foreign status and claim tax treaty benefits on US-source income. UK residents file it so Apple withholds **0% of royalty payments** under Article 12(1) of the US-UK Income Tax Treaty, instead of the default **30% US withholding**. This is a large, real-money financial difference over the lifetime of a shipping app.

**Line-by-line for UK sole traders:**

| Line | Field | Value |
|---|---|---|
| 1 | Name of Individual Beneficial Owner | Legal name exactly as on passport; must match Apple ID |
| 2 | Country of Citizenship | `United Kingdom` (not `UK`, `England`, `Britain`) |
| 3 | Permanent Residence Address | UK residential address |
| 4 | Mailing Address | Leave blank unless different from Line 3 |
| 5 | U.S. Taxpayer Identification Number | **Leave blank.** UK residents do not need a US TIN. Do not click the "SS-4" link — that is for US employers only. |
| 6a | Foreign Tax Identifying Number | UK UTR (10 digits from HMRC) OR National Insurance Number (`AB 12 34 56 C` format) OR blank |
| 6b | FTIN Not Legally Required | **Unchecked.** UK issues tax IDs. |
| 7 | Reference Number(s) | Blank (entity use only) |
| 8 | Date of Birth | **MM-DD-YYYY** format — US format, not UK DD/MM/YYYY. This is the #1 rejection reason for European filers. |

**Part II — Claim of Tax Treaty Benefits:**

| Line | Field | Value |
|---|---|---|
| 9 | Treaty country checkbox | Checked, country `United Kingdom` |
| 10 | Article and paragraph | `12` and `1` (or `Article 12(1)`) |
| 10 | Rate of withholding | `0` |
| 10 | Specify type of income | `Royalties` |

Line 10 free-text explanation (paste verbatim):

```
The beneficial owner is a resident of the United Kingdom and the royalties
are beneficially owned by the resident. The beneficial owner does not have
a permanent establishment in the United States to which the royalties are
attributable. The beneficial owner meets all conditions of Article 12(1)
of the United States-United Kingdom Income Tax Treaty for the 0% rate of
withholding on royalties.
```

**Part III — Certification:**

- Check "Under penalties of perjury..." (mandatory)
- Check "I have the capacity to sign" (signing for yourself)
- Signature: type your name exactly as it appears on Line 1 (including any Apple-side misspellings — fix Line 1 first if needed)
- Date: today in MM-DD-YYYY format

**Why Line 10 matters financially:** Apple pays developers as *royalties* (payments for IP, not commission or sales revenue), and Article 12(1) of the 2001 US-UK Income Tax Treaty exempts royalties from US withholding for UK residents. If Line 10 is left blank or filled in incorrectly, Apple withholds 30% of every royalty payment and you must claim it back from the IRS via a 1040-NR filing — a year-long process. On `$10k/month` of US App Store royalties, that is `$3k/month` of cash flow stuck with the IRS. Get Line 10 right.

**Pre-submit sanity check:**

- [ ] Line 8 date is MM-DD-YYYY (not DD-MM-YYYY) — #1 rejection cause
- [ ] Line 9 says `United Kingdom` exactly
- [ ] Line 10 says Article `12`, paragraph `1`, `0`%, `Royalties`
- [ ] Line 10 explanation paragraph is pasted
- [ ] Part III perjury box is checked
- [ ] Part III capacity box is checked
- [ ] Signature matches Line 1 exactly
- [ ] Date of signature is today in MM-DD-YYYY

**Realistic post-submit timeline:**

1. Apple's automated tax processor reviews — instant to 30 minutes
2. Tax Forms row flips from `Missing Tax Info` to `Active`
3. If banking is already Active, Paid Apps Agreement flips to `Active` within minutes
4. If banking is still `Processing`, Paid Apps Agreement stays at `Pending User Info` until banking completes (up to 24 hours)
5. Once Paid Apps is Active, wait 15-30 minutes for StoreKit sandbox catalog propagation
6. Force-quit the app on device, relaunch, tap Retry on the paywall — products should load

Total typical timeline from a fresh W-8BEN submission: **20-30 hours**, dominated by the banking processing window.

### US residents — W-9 form

US residents (individuals or single-member LLCs taxed as disregarded entities) file **W-9** instead of W-8BEN. The form is much shorter: legal name, business name if any, tax classification checkbox, address, SSN or EIN, signature, date. No treaty claim — US residents pay US tax on all income, which is handled on your personal 1040 or entity return rather than at withholding time.

### Other entity types

- **Non-US entities** (companies, partnerships, LLCs) file **W-8BEN-E** instead of W-8BEN. Significantly more complex: Chapter 3 status, Chapter 4 (FATCA) status, GIIN if applicable, limitation on benefits article. Consult an accountant.
- **US non-profit organizations** file **W-9** with the exempt payee code.
- **Income effectively connected to US trade or business** (rare for app developers — usually only if you maintain a US office): **W-8ECI**.

For most individual developers outside the US, W-8BEN with Article 12(1) (royalties) is the correct form and the most common filing.

## Phase 6: Build Upload

- [ ] Archive the app in Xcode (Product > Archive) or via CI (Xcode Cloud's `Archive - iOS` action)
- [ ] Upload to App Store Connect via Xcode Organizer or `xcodebuild` + Transporter
- [ ] Wait for build processing (5-30 minutes typically)
- [ ] App icon appears automatically in App Store Connect (extracted from build)
- [ ] Select the build on the version page

### Build action ≠ Archive action

A green `Build` action does not imply a green `Archive`. Only `Archive` produces the signed `.ipa` that App Store Connect accepts, and signing/provisioning failures surface at Archive time even when Build passes. If CI shows Build green + Archive red, do not ship — treat Archive as the submission gate.

### Xcode Cloud specifics

Xcode Cloud is Apple's CI for building, archiving, and uploading to App Store Connect. It behaves differently from a local developer checkout in ways that cause hard-to-diagnose failures:

| Fact about Xcode Cloud | Implication |
|---|---|
| Clones only the current repo into `/Volumes/workspace/repository` | No sibling repos. Local scripts that `cd ../<sibling>/…` will fail on CI. |
| Runs `xcodebuild` directly against the committed `.xcodeproj` | Never runs your local `generate-xcodeproj.sh`, `generate-infoplist.sh`, or locale-export scripts. Anything generated at local-build time must be either committed to git (`git add -f` if the folder is ignored) or regenerated in a `ci_scripts/*.sh` hook. |
| Has no `.env.local` or sibling env files | Environment values must come from App Store Connect → Xcode Cloud → product → Settings → Environment Variables (mark API keys as **Secret**). Generators must have fallbacks for when a var is unset. |
| Runs `ci_scripts/ci_post_clone.sh` automatically after clone, before dependency resolution | The file must live at that exact path, be executable, and exit 0. Its log appears under the **Post-Clone** step in the Xcode Cloud build log. This is the only officially-supported hook for synthesising generated files on CI. |
| Requires a Team selected on the workflow for signing | Without a Team, automatic signing fails even when Build passes — Archive needs a provisioning profile. |

### `xcodebuild` exit code 65 — always expand the nested step

`xcodebuild` summarises archive failures with a single line: `Command … failed with a nonzero exit code` or `exit code 65`. The summary never names the real cause. On Xcode Cloud, **always expand the nested build step** in the log UI — the actual error is in the inner output. Common real causes:

| Inner error | Root cause | Fix |
|---|---|---|
| `No profiles for '<bundle-id>' were found` | App ID missing a capability declared in `.entitlements` | In Apple Developer → Identifiers, enable Sign in with Apple, Associated Domains, Push Notifications, etc. to match the `.entitlements` file |
| `Signing for "<target>" requires a development team` | No Team selected on the Xcode Cloud workflow | Workflow → Environment → set Team |
| `The file '<Info.generated.plist>' couldn't be opened` | `ci_post_clone.sh` did not run or failed before generating the plist | Verify path, `chmod +x`, exit 0; check the Post-Clone step log |
| `The file 'manifest.json' couldn't be opened because there is no such file` | File is in a gitignored folder and was never committed, so Xcode Cloud's fresh clone doesn't have it | Either `git add -f` the specific file, or regenerate it in `ci_post_clone.sh` |
| `TARGETED_DEVICE_FAMILY` mismatch between build and App Store listing | Changed device family in project config, but the uploaded archive was built before the change | Device family is baked into the binary — produce a new Archive after the change; App Store Connect will not retroactively update |

## Phase 7: TestFlight

- [ ] Build appears in TestFlight after processing
- [ ] Add internal testers (up to 100, instant access)
- [ ] Add external testers if needed (requires brief Beta App Review)
- [ ] Test end-to-end: auth, core features, push, purchases (Sandbox)
- [ ] Address any issues found
- [ ] Verify push notifications work on TestFlight builds (production APNs environment)

### Pre-upload entitlement verification

Before uploading the archive, inspect the signed `.app` and confirm the entitlements match what the App ID has enabled:

```bash
codesign -d --entitlements - /path/to/<App>.app
```

Every `com.apple.developer.*` key in the output must correspond to an enabled capability on the App ID. A capability in `.entitlements` that is NOT enabled on the App ID causes an Archive failure; a capability enabled on the App ID but NOT declared in `.entitlements` is harmless but indicates drift. Run this check locally before every first-submission upload.

### Per-device APNs environment verification

TestFlight builds register with APNs **production**; local `Xcode → Run` builds register with APNs **sandbox**. If your backend records the `environment` string per device, verify the row for a given device flips between `sandbox` (local run) and `production` (TestFlight install) correctly. A mismatch — for example, a device token recorded with `environment = production` while the device is running a local dev build — silently drops every push because the backend sends to the wrong APNs gateway. Verify before TestFlight push-validation, not after.

## Phase 8: App Review Preparation

### App Review Information

- [ ] **Contact Information** — first name, last name, phone, email for reviewer contact
- [ ] **Demo Account** (if login required) — provide working test credentials
- [ ] **Notes** — explain anything non-obvious to the reviewer (e.g., "Subscriptions use Sandbox for testing")

### Common Rejection Reasons to Check

This checklist covers App Store Connect submission *mechanics*. For the full **App Store Review Guidelines** mapped to pass/fail checks across all five sections, see [../../software-ios-design/references/app-review-guidelines-map.md](../../software-ios-design/references/app-review-guidelines-map.md) and [../../software-ios-design/references/ios-shipping-antipatterns.md](../../software-ios-design/references/ios-shipping-antipatterns.md).

Metadata / submission triggers:

- Missing or inaccessible Privacy Policy URL
- App Privacy labels don't match actual data collection
- Subscription terms not in the description
- Screenshots show content not achievable in the app
- App crashes during review
- Login required but no demo account provided
- "Sign in with Apple" not offered when third-party sign-in is present
- Placeholder content or incomplete features

Concept-level triggers (these reject the *app idea*, not just the metadata — verify **before** building):

- **4.3(b) saturated category** — astrology/horoscope/tarot/numerology/fortune-telling, flashlight, soundboard, and similar are rejected unless they provide a "unique, high-quality experience." Adding AI does not exempt them. See the guidelines map's "do not build this way" gate.
- **4.2 Minimum Functionality** — web wrappers, single-screen utilities, and content feeds that should be a website.
- **4.2.6 Template/generated apps** — apps from a commercialized template or app-generation service must be submitted by the content provider directly.
- **5.1.1(v) Account deletion** — account-bearing apps must offer in-app account deletion, not just an email request. Heavily enforced.
- **1.2 User-Generated Content** — UGC surfaces need filter + report + block + 24h moderation.

## Phase 9: Submit

- [ ] All metadata complete (no yellow warnings)
- [ ] Build selected
- [ ] Review information filled
- [ ] Click **Add for Review** then **Submit to App Review**
- [ ] Expected review time: 24-48 hours (can vary)

## Phase 10: Post-Submission

- [ ] Monitor review status in App Store Connect
- [ ] Respond promptly to any reviewer questions via Resolution Center
- [ ] If rejected, read the specific guideline cited and fix the exact issue
- [ ] Once approved, choose release timing: immediate, manual, or scheduled date

## Localization Strategy

If your app supports multiple languages:

1. Use the locale dropdown in App Store Connect to add each language
2. For each locale, provide: subtitle, description, keywords, promotional text, what's new
3. Screenshots can be shared across locales or localized (localized converts better in non-English markets)
4. Store all metadata in version control (e.g., `fastlane/metadata/<locale>/`) for review and iteration
5. Fastlane locale codes: `en-US`, `es-MX`, `fr`, `de`, `ru`, `zh-Hans`, `pt-BR`, `tr`, `it`, `ar`, `vi`, `hi`, `ja`, `ko`

## Automation

### Fastlane Metadata Directory

```
fastlane/metadata/<locale>/
  name.txt              # App Name (30 chars)
  subtitle.txt          # Subtitle (30 chars)
  description.txt       # Description (4000 chars)
  keywords.txt          # Keywords (100 chars)
  promotional_text.txt  # Promotional Text (170 chars)
  release_notes.txt     # What's New (4000 chars)
  support_url.txt       # Support URL
  privacy_url.txt       # Privacy Policy URL
  marketing_url.txt     # Marketing URL
```

### Fastlane Screenshot Automation

```ruby
# Snapfile
devices([
  "iPhone 16 Pro Max",    # 6.7"
  "iPhone 11 Pro Max",    # 6.5"
])
languages(["en-US", "es-MX", "fr", "de", "ru", "zh-Hans", "pt-BR", "tr", "it", "ar", "vi", "hi", "ja", "ko"])
scheme("YourAppScheme")
output_directory("./fastlane/screenshots")
```

Run `fastlane snapshot` to capture, `fastlane frameit` for device frames, `fastlane deliver` to upload.
