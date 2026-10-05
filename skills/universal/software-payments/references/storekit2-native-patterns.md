# Native StoreKit 2 Integration Patterns

## Table of Contents

- [1. StoreKit 2 vs RevenueCat Decision](#1-storekit-2-vs-revenuecat-decision)
- [2. Architecture Pattern](#2-architecture-pattern)
- [3. Critical: Transaction.finish() Timing](#3-critical-transactionfinish-timing)
- [4. VerifiedTransaction Pattern](#4-verifiedtransaction-pattern)
- [5. Backend JWS Verification](#5-backend-jws-verification)
- [6. App Store Server Notifications v2](#6-app-store-server-notifications-v2)
- [7. Dual Billing Guard (Stripe + Apple)](#7-dual-billing-guard-stripe--apple)
- [8. Apple Small Business Program](#8-apple-small-business-program)
- [9. Pricing for App Store](#9-pricing-for-app-store)
- [10. StoreKit Testing](#10-storekit-testing)
- [11. External Purchase Links (Guideline 3.1.1(a))](#11-external-purchase-links-guideline-311a)

Production patterns for integrating StoreKit 2 directly (without RevenueCat) in iOS apps that have an existing backend for entitlement management.

---

## 1. StoreKit 2 vs RevenueCat Decision

**Use native StoreKit 2 when:**

- Small product catalog (fewer than 10 products)
- Existing backend entitlement system that already tracks subscriptions
- Want zero third-party dependencies in the purchase flow
- iOS-only app (no Android counterpart)

**Use RevenueCat when:**

- Cross-platform (iOS + Android) and need unified subscription state
- No backend — RevenueCat acts as the entitlement server
- Large product catalog with frequent experimentation
- Need an analytics dashboard for subscription metrics without building one
- Team is unfamiliar with StoreKit APIs and App Store Server Notifications

---

## 2. Architecture Pattern

Four components:

| Component | Role |
|-----------|------|
| `StoreKitManager` | `@Observable @MainActor` class. Loads products, runs purchase flow, listens to `Transaction.updates` for renewals and external transactions. |
| `TransactionSyncService` | Swift `actor`. Sends JWS to backend, retries unfinished transactions on launch. Isolated from UI thread. |
| `ProductCatalog` | Static product ID constants. Single place to update when products change in App Store Connect. |
| Backend | Source of truth for entitlements. Receives JWS, verifies, upserts subscription records, exposes entitlement status to client. |

Flow: `StoreKitManager` handles the user-facing purchase → hands the verified transaction and JWS to `TransactionSyncService` → sync service calls backend → on backend success, calls `transaction.finish()`.

The backend remains the single source of truth for entitlement state. StoreKit provides immediate local feedback (optimistic UI) while the sync completes.

---

## 3. Critical: Transaction.finish() Timing

**NEVER call `Transaction.finish()` before the backend confirms the sync.**

If you finish before the backend records the transaction, Apple considers it delivered but your backend never received it. The user paid and got nothing. There is no way to recover the transaction after it is finished.

### Correct sequence

1. `product.purchase()` returns `Product.PurchaseResult`
2. Extract `VerificationResult<Transaction>` from the `.success` case
3. Capture `verification.jwsRepresentation` (the signed JWS string for server verification)
4. Unwrap and verify the `Transaction` from the `VerificationResult`
5. Send JWS to backend verify endpoint
6. Backend verifies signature, upserts subscription/purchase record
7. Backend returns success
8. **THEN** call `transaction.finish()`

### On failure

Leave the transaction unfinished. `Transaction.unfinished` persists across app launches. On next launch, `TransactionSyncService` iterates unfinished transactions and retries the backend sync. Only finish after confirmed success.

---

## 4. VerifiedTransaction Pattern

`VerificationResult<Transaction>` has `.jwsRepresentation` (a `String` containing the signed JWS for server verification). The unwrapped `Transaction` does **NOT** have this property. You must capture both before unwrapping.

```swift
struct VerifiedTransaction {
    let transaction: Transaction
    let jwsRepresentation: String
}
```

Extract from purchase result:

```swift
case .success(let verification):
    let transaction = try checkVerification(verification)
    return VerifiedTransaction(
        transaction: transaction,
        jwsRepresentation: verification.jwsRepresentation
    )
```

The `checkVerification` helper unwraps the `VerificationResult` and throws on `.unverified`:

```swift
private func checkVerification<T>(_ result: VerificationResult<T>) throws -> T {
    switch result {
    case .verified(let value):
        return value
    case .unverified(_, let error):
        throw error
    }
}
```

This pattern prevents the common mistake of trying to access `.jwsRepresentation` on `Transaction` (which does not exist) and ensures you always have the JWS available for backend sync.

---

## 5. Backend JWS Verification

Two approaches depending on existing stack:

### Option A: `@apple/app-store-server-library` (npm)

Higher-level library from Apple. Handles:

- Certificate chain validation from the x5c header
- JWS signature verification
- Subscription Status API calls
- Signed notification decoding

Best when starting fresh or when you want subscription status polling as a fallback.

### Option B: `jose` library

Decode the JWS, extract the x5c certificate chain from the header, verify the signature. Lighter dependency, works well if `jose` is already in the stack.

### Key validations (both approaches)

- `bundleId` matches your app's bundle identifier
- `environment` matches expected environment (`Sandbox` vs `Production`)
- Transaction is not revoked
- `productId` matches a known product
- For subscriptions: check `expiresDate` and `revocationDate`

---

## 6. App Store Server Notifications v2

Register a webhook URL in App Store Connect under App Information. Apple sends signed notifications (JWS) for subscription lifecycle events.

### Events to handle

| Notification | Action |
|-------------|--------|
| `DID_RENEW` | Update period start/end dates, set status active |
| `DID_CHANGE_RENEWAL_STATUS` | Toggle `cancel_at_period_end` flag |
| `DID_FAIL_TO_RENEW` | Set status to `past_due`, record `payment_failed_at` |
| `GRACE_PERIOD_EXPIRED` | Downgrade to free tier |
| `EXPIRED` | Downgrade to free tier |
| `REFUND` | Revoke access, record refund |
| `REVOKE` | Revoke access (Family Sharing revocation) |
| `DID_CHANGE_RENEWAL_INFO` | Handle plan switches (e.g., monthly to annual) |
| `SUBSCRIBED` | New subscription or resubscription |
| `OFFER_REDEEMED` | Promotional or offer code applied |

### Reliability notes

- Apple retries failed webhooks with exponential backoff
- Always return HTTP 200, even if you cannot process immediately (queue internally)
- Notifications are signed JWS — verify before trusting
- Use the `signedDate` field for ordering, not arrival time
- Implement idempotency using `notificationUUID`

---

## 7. Dual Billing Guard (Stripe + Apple)

When web uses Stripe and iOS uses StoreKit, users can accidentally (or intentionally) subscribe through both channels.

### Prevention

Add a `billing_platform` column to the subscriptions table:

```
billing_platform: 'stripe' | 'apple'
```

Before processing an Apple purchase:

1. Check if user has an active Stripe subscription
2. If yes, block the purchase with a message: "You're already subscribed via web. Manage your subscription at [web URL]."
3. If no active Stripe subscription, proceed with Apple purchase

Before processing a Stripe checkout:

1. Check if user has an active Apple subscription
2. If yes, show: "You're already subscribed via the iOS app. Manage in Settings > Subscriptions."

### Additional safeguards

- Include `billing_platform` in the entitlement response so the client knows where to direct management actions
- On the backend, never allow two active subscriptions for the same user — the second attempt should fail gracefully
- Consider a grace period check: if an Apple subscription is in `cancel_at_period_end` state (canceled but not expired), allow Stripe subscription to start only after expiry

---

## 8. Apple Small Business Program

Apple offers a reduced commission tier for developers under an annual proceeds threshold. The rate, the threshold and the enrollment rules are Apple's to change, so read the [Small Business Program page](https://developer.apple.com/app-store/small-business-program/) before you model revenue. These rules are structural and change less often:

- Enrollment is an explicit application, not automatic. Check whether it must be renewed.
- All associated developer accounts count together toward the threshold.
- Crossing the threshold mid-year moves the remaining transactions to the standard rate.
- Auto-renewable subscriptions can already get a reduced rate after the subscriber's first paid year, regardless of enrollment. Confirm this in the current terms before counting on it twice.

### Impact on pricing

Model net revenue per price point at both the reduced and the standard rate, using the rates from the current terms. Break-even and CAC payback should hold at the standard rate, because growth past the threshold removes the discount.

---

## 9. Pricing for App Store

### Display prices

- Always use `product.displayPrice` from StoreKit — never hardcode prices
- Apple handles currency conversion per storefront automatically
- `displayPrice` returns a formatted string with the correct currency symbol for the user's locale

### Price point structure

- App Store prices come from a fixed grid of price points per storefront, not arbitrary amounts. Pick from the price-point list in App Store Connect for each storefront you ship to.
- The grid's spacing and the per-storefront equivalents differ with currency and tax. Do not hardcode the increments; read them from App Store Connect.

### Pricing strategy

- For competitive pricing, calculate net revenue after Apple's cut, not just the sticker price
- Set the annual-plan discount against the monthly price deliberately and test it. Don't copy a "standard" percentage; category and trial design move the right number.
- Use introductory offers (free trial, pay-up-front, pay-as-you-go) to reduce acquisition friction
- Promotional offers (codes) for win-back campaigns

---

## 10. StoreKit Testing

### Xcode StoreKit Configuration

- Create a `.storekit` configuration file (JSON format) in the Xcode project
- Define products, subscriptions, and subscription groups
- Enable in scheme: Edit Scheme > Run > Options > StoreKit Configuration
- Purchases work in Simulator without a sandbox account

### Transaction Manager

- Access via Debug > StoreKit > Manage Transactions in Xcode
- Simulate refunds, subscription renewals, billing issues, and offer redemptions
- Delete transactions to reset state during development

### Sandbox testing

- Use sandbox Apple IDs on physical devices (create in App Store Connect > Users and Access > Sandbox)
- Sandbox renewals are accelerated:

| Real duration | Sandbox duration |
|--------------|-----------------|
| 1 week | 3 minutes |
| 1 month | 5 minutes |
| 2 months | 10 minutes |
| 3 months | 15 minutes |
| 6 months | 30 minutes |
| 1 year | 1 hour |

- Subscriptions auto-renew up to 6 times in sandbox, then expire
- Sandbox environment connects to Apple's sandbox servers — separate from production

### Testing checklist

- [ ] New purchase flow completes and backend receives JWS
- [ ] Transaction.finish() only called after backend confirmation
- [ ] Unfinished transactions retry on next app launch
- [ ] Subscription renewal updates entitlement correctly
- [ ] Expired subscription downgrades access
- [ ] Restore purchases works (Transaction.currentEntitlements)
- [ ] Dual billing guard prevents double-subscription
- [ ] App Store Server Notifications received and processed correctly

---

## 11. External Purchase Links (Guideline 3.1.1(a))

Whether an iOS app may point users to a web checkout for digital goods depends on the **storefront**, not on where the developer is based. The App Store Review Guidelines give the US storefront its own rule: under 3.1.1(a), the link-out entitlements "are not required for developers to include buttons, external links, or other calls to action in their United States storefront apps". Guideline 3.1.3 carries the same United States exception. In other storefronts, apps may not include buttons, external links, or other calls to action that lead to non-IAP purchasing, unless they hold a regional StoreKit External Purchase Link Entitlement (or a Music Streaming Services Entitlement), use it only where it is valid, and follow its terms. Reader apps (3.1.3(a)) have a separate External Link Account Entitlement for account creation and management.

### Decision logic

1. **Resolve the storefront at runtime** with StoreKit's `Storefront.current` and branch the UI on it. Do not rely on device locale, IP, or the user's billing country.
2. **US storefront:** you may show a button or link to your own web checkout alongside IAP. Keep IAP available if the app already sells the same items through it, and keep the dual-billing guard (section 7) because users can now subscribe on both rails.
3. **A storefront with an entitlement program you hold:** use only the entitlement's approved link format, disclosure sheet, and reporting obligations. Anything outside the entitlement terms is a rejection risk.
4. **Any other storefront:** do not show purchase links, buttons, or calls to action for non-IAP purchasing inside the app or its metadata. Communication outside the app, such as email to existing customers, is allowed under 3.1.3.
5. **Web checkout target:** the link must go to a website the developer owns or maintains responsibility for. Pass an account-linking token so the web purchase provisions the same entitlement record (the `billing_platform` record from section 7), and grant access from the verified web-payment webhook, not from the redirect.

### Lookup before shipping

Wording, eligible storefronts, entitlement terms, and any commission or reporting duty on linked purchases all change, sometimes because of litigation or regulation. Before designing or approving a link-out, check the current text of the [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) (3.1.1(a), 3.1.3) and Apple's [StoreKit external purchase documentation](https://developer.apple.com/documentation/storekit/external_purchase). Do not hardcode fee rates or effective dates in code or docs. Route legal-exposure questions to counsel.
