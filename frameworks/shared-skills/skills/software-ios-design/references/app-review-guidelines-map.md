# App Store Review Guidelines — Pass/Fail Map

## Table of Contents

- [How to use this map](#how-to-use-this-map)
- [1. Safety](#1-safety)
- [2. Performance](#2-performance)
- [3. Business](#3-business)
- [4. Design](#4-design)
- [5. Legal](#5-legal)
- [App Review for AI-generated content](#app-review-for-ai-generated-content)
- [Pre-submit gate](#pre-submit-gate)

Canonical: [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/). Re-read the live page before a submission — Apple edits it without versioning. This file maps the five sections to concrete checks an agent can run against a build and its metadata. Deep "why it fails" rationale lives in [ios-shipping-antipatterns.md](ios-shipping-antipatterns.md); submission mechanics live in [../../software-mobile/references/app-store-connect-checklist.md](../../software-mobile/references/app-store-connect-checklist.md).

Treat every row as a release gate. A failed row is a likely rejection, not a polish item.

## How to use this map

1. Before proposing or building an app, run the [Section 4.3 / 4.2 viability check](#43--42-the-do-not-build-this-way-gate) first. It can kill a concept before any code.
2. During build, satisfy the Safety / Performance / Business / Legal rows that apply.
3. Before Submit, walk the [pre-submit gate](#pre-submit-gate) and the antipatterns checklist.

## 1. Safety

| Guideline | Check | Fail signal |
|---|---|---|
| 1.1 Objectionable content | No defamatory, discriminatory, or gratuitously violent content | Reviewer finds offensive content with no purpose |
| 1.2 User-Generated Content | If users post content visible to other users: a content filter, an in-app **report** mechanism, an in-app **block** mechanism, a published contact, and action on reports within **24h** all exist. You are also responsible for **removing** content that violates the guideline, your ToS, or your community standards once notified — repeated/egregious failure is grounds for removal from the app *and* the Developer Program | UGC surface with no report/block/moderation path — automatic rejection, and the #1 trap for social/community features; leaving flagged violating content live after Apple asks you to remove it |
| 1.4 Physical harm | Medical/health claims are accurate and not dangerous; no encouragement of harm | Unsubstantiated health advice presented as fact |
| 1.5 Developer information | Support URL resolves and offers a real contact route | Dead or placeholder support URL |

## 2. Performance

| Guideline | Check | Fail signal |
|---|---|---|
| 2.1 App Completeness | No crashes on launch in the reviewer's region/locale; no placeholder/lorem/TODO content; working demo account in Review Notes if login is required | Crash on a fresh install, broken demo creds, visible placeholder copy |
| 2.3.1 Hidden features | No undocumented, hidden, or toggled-on-later functionality | Feature flags that reveal behavior not shown to review |
| 2.3.2/2.3.3 Accurate metadata | Screenshots show the actual app in use; subscription terms appear in the description; previews demonstrate real in-app content | Marketing-only screenshots, content not achievable in-app |
| 2.3.7 Keywords | No competitor names, no trademarked terms, no category names | Competitor name in the keyword field — rejection |
| 2.5.2 No executable code download | The app does not download code that changes its features/UI after review. **Loading model weights / prompt configs / content data is fine; downloading executable logic that alters app behavior is not** | Remote config that ships new screens or capabilities review never saw |
| 2.5.4 Background modes | Every declared background mode (location, audio, fetch) maps to a real, demonstrable feature | `location` background mode with only a one-time lookup feature |

## 3. Business

| Guideline | Check | Fail signal |
|---|---|---|
| 3.1.1 In-App Purchase | Digital goods/services unlocked inside the app use StoreKit IAP, not an external payment sheet | Stripe/web checkout for in-app digital content (outside the narrow reader/external-link entitlements) |
| 3.1.1(a) / 3.1.3 External link & reader exceptions | If using the External Link Account entitlement or a "reader" exception, the entitlement is granted and the flow matches Apple's rules exactly | Linking out to buy digital goods without the entitlement |
| 3.1.2 Subscriptions | Auto-renew terms, price, period, and a functioning restore-purchases path are present; terms also in the binary and the description | Missing restore button, terms only in App Store metadata |
| 3.1.1 Value before paywall | The user can see what the app does before the purchase screen (also a 4.2 concern) | App opens directly onto a paywall |

## 4. Design

| Guideline | Check | Fail signal |
|---|---|---|
| 4.1 Copycats | UI/name/icon are not a knockoff of another app | Reskinned clone of a popular app |
| 4.2 Minimum Functionality | The app does something useful and native; it is **not** a repackaged website, a thin wrapper, or a single static screen | "It's basically our website in a WebView" |
| 4.2.6 Template/generated apps | Apps built from a commercialized template or app-generation service are rejected unless submitted **by the content provider directly** under their own account | Agency/template-farm submissions for many similar clients |
| 4.3(a) Spam — duplicate Bundle IDs | You are not shipping multiple Bundle IDs of the same app (e.g. one map app per city). Location/team/university variants belong in **one** app with the variation behind in-app purchase | A family of apps differing only in theme/content/region — unnecessary apps that degrade discovery |
| 4.3(b) Indistinguishable / saturated category | App is not "indistinguishable from what's already widely available." Apple names **dating, flashlight, sound effects, wallpaper, simple timers, and fortune telling** as established categories that need a *meaningfully different or improved* experience; **drinking games, Kama Sutra, fart, and burp** apps are treated as low-value. See the dedicated gate below | A me-too entry in a named category with no differentiation — and existing apps in these categories can be removed if not updated/improved or if they fail to attract customers |
| 4.5.3 Apple Services anti-spam | Push Notifications, **Live Activities**, Game Center, and other Apple services are **not** used to spam, phish, or send unsolicited messages. A Live Activity shows live, user-relevant session state — not promos, re-engagement nags, or marketing pushed into the Lock Screen / Dynamic Island | A Live Activity (or push) used to advertise, re-engage, or message users content they did not ask for — grounds for removal |
| 4.8 Login services | If any third-party/social login is offered, an **equivalent privacy-preserving** login is also offered (limits data to name+email, lets users keep email private, no tracking). Sign in with Apple is the simplest qualifying option | Google/Facebook/email login with no privacy-preserving equivalent |

> **4.8 nuance:** Apple no longer mandates Sign in with Apple *specifically* — it requires an equivalent privacy option when third-party login exists. SiwA is the lowest-effort way to comply, which is why [ios-shipping-antipatterns.md](ios-shipping-antipatterns.md) frames it as "implement SiwA." Either is correct; do not ship third-party login with no privacy-preserving equivalent.

### 4.3 / 4.2 — the "do not build this way" gate

This gate runs **before** design or code. 4.3(b) is the rule that rejects whole concepts, and it names categories explicitly. Apple's current text (re-verified 2026-07-11 — re-read live, Apple edits without versioning):

> "Don't submit apps that are indistinguishable from what's already widely available. ... Certain kinds of apps, such as dating, flashlight, sound effects, wallpaper, simple timers, and **fortune telling**, are well established on the App Store and we will not accept new submissions unless they offer a meaningfully different or improved experience. We may remove these apps from the App Store going forward if they are not updated, improved, or do not attract customers. Other kinds of apps, such as drinking games, Kama Sutra, fart, and burp apps, are mediocre, low-quality, or low-effort and do not add value to the App Store."

**Saturated categories Apple is openly hostile to** (4.3(b)): fortune telling / horoscopes / **astrology / tarot / numerology / palmistry / dream-reading and other divination**, flashlight, sound effects, fart/soundboard, drinking games, Kama Sutra, generic dating, simple wallpaper, simple timers, and QR/utility one-screen apps. Membership in this list is not an automatic ban — but it flips the burden of proof onto the app to demonstrate a *meaningfully different or improved, unique, high-quality, app-like* experience. Note the added teeth: Apple now says it **may remove existing apps** in these categories that are not updated/improved or that fail to attract customers — being live is not a grandfather clause.

**Do NOT propose, and do not let a user ship, an app whose pitch reduces to:**

- "A horoscope/astrology/tarot/numerology reading app" with generic readings and a Day-1 paywall → rejected under 4.3(b) + 3.1.1.
- One concept replicated as N themed apps (Leo app, Virgo app, …) → 4.3(a).
- A reskinned template from an app-generation service → 4.2.6.
- A WebView around an existing astrology website → 4.2.

**Do this instead — the unique/high-quality bar that clears 4.3(b):**

- Ship genuinely **interactive, personalized, native** functionality (e.g. real ephemeris-accurate chart computation, on-device interpretation, journaling/tracking with history, notifications tied to the user's own data) — not a static text generator.
- Give substantial **free value before any paywall** (clears 3.1.1 and the "this app does nothing but ask for money" rejection).
- Make it demonstrably **more than a content feed**: local state, user inputs, and features that justify being an app rather than a webpage (clears 4.2).
- Differentiate from the category clones in a way a reviewer can see in 30 seconds of use.
- If advising on a divination/cosmic concept, **say this explicitly up front**: "This category is named in Guideline 4.3(b); to pass review the app must clear a unique/high-quality bar — here is what that requires." Do not present a generic reading-generator as review-ready.

## 5. Legal

| Guideline | Check | Fail signal |
|---|---|---|
| 5.1.1 Data collection & storage | Permission usage strings name the specific feature; permissions requested **at point of need**; privacy policy URL resolves; App Privacy labels match real collection | Vague usage strings, cold permission prompts, label mismatch (also 5.1.1(v) below) |
| 5.1.1(v) Account deletion | If the app supports account creation, it offers **in-app account deletion** (not just "email us") | Account creation with no in-app delete path — a current, heavily enforced rejection |
| 5.1.2 Data use & sharing | No undisclosed third-party data sharing; ATT prompt present if tracking; SDKs' data behavior reflected in the label | New SDK adds tracking the label does not declare |
| 5.2 Intellectual property | No use of others' content/trademarks without rights; no "Apple/iPhone/iOS" implying endorsement | Trademarked names in app name or screenshots |
| 5.6 Developer Code of Conduct | No review manipulation, no misleading the reviewer, no rating-prompt abuse | Soliciting fake reviews; gating content on a 5-star rating |

## App Review for AI-generated content

If the app generates user-facing text/images with a model (local or cloud), additionally:

- **1.2 applies even to model output.** A surface that can produce content shown to the user needs a safety filter and, where users can share generated content, a report path. Safety/refusal copy must be content that was actually reviewed — not free-form model output.
- **Divination/cosmic AI features sit inside 4.3(b).** "AI horoscope/tarot reader" does not escape the saturated-category bar by being AI — it raises it. The unique/high-quality requirement above still governs. See [../../software-ios-ai-engine/SKILL.md](../../software-ios-ai-engine/SKILL.md) for the engine-side framing.
- **2.5.2:** shipping/updating model weights, prompts, sentence-bank fragments, or retrieval data is allowed; downloading code that changes app behavior is not.

## Pre-submit gate

- [ ] 4.3(b)/4.2 viability confirmed: app is unique, high-quality, app-like — not a saturated-category clone, template, or web wrapper
- [ ] No crash on a fresh install in the reviewer's likely locale (test a non-US locale)
- [ ] Value visible before any paywall; subscription terms in description + binary; restore-purchases works
- [ ] In-app account deletion present if accounts exist (5.1.1(v))
- [ ] Permission strings name the feature; prompts fire at point of need; App Privacy labels match reality
- [ ] If third-party login exists, a privacy-preserving equivalent (e.g. Sign in with Apple) is offered (4.8)
- [ ] UGC surfaces have filter + report + block + 24h moderation (1.2), and a path to remove violating content once notified
- [ ] If kids/teens are plausible users, the experience is age-appropriate and the age rating + parental-control posture match what the app actually does (Intro kid/teen safety)
- [ ] Live Activities / push are used only for live, user-relevant state — never spam, marketing, or re-engagement nags (4.5.3)
- [ ] No competitor/trademark terms in keywords; screenshots show real in-app content
- [ ] Working demo account in Review Notes; no placeholder content in the binary
- [ ] Full antipattern pass: [ios-shipping-antipatterns.md](ios-shipping-antipatterns.md)
