# Scaffold: Entitlement Store + Paywall Gate

Copy-paste StoreKit 2 monetization core. App-class-agnostic: a notes app, an AI wrapper, and a utility-IAP app all use the *same* entitlement store — only the products and the gated features differ. Fill the `// TODO` markers.

Pairs with [cloudflare-worker-backend.md](cloudflare-worker-backend.md) (server webhook that confirms the entitlement) and the decision logic in [../../references/starter-stacks-and-monetization.md](../../references/starter-stacks-and-monetization.md). For the full entitlement-registry rationale see `../../../software-payments/references/storekit2-native-patterns.md`.

## When to Use

- Any app selling subscriptions or non-consumables through StoreKit 2.
- Start here even before you add RevenueCat — RevenueCat sits on StoreKit 2, so this store is the seam you'd swap behind later.

## What it gives you

- One `@Observable @MainActor` entitlement store = the single source of truth for "is this user pro?".
- A `Transaction.updates` listener so server-driven changes (upgrade, downgrade, cancel, refund) reach the UI.
- A reusable `PaywallGate` view modifier: wrap any premium feature, get a paywall when locked.

## EntitlementStore.swift

```swift
import StoreKit
import SwiftUI

/// Single source of truth for entitlements. Gate ALL paid UI from this store —
/// never from a second independent check (client + server timing diverges).
@Observable
@MainActor
final class EntitlementStore {
    enum LoadState { case idle, loading, loaded, failed(String) }

    private(set) var state: LoadState = .idle
    private(set) var products: [Product] = []
    private(set) var isPro: Bool = false                 // derived entitlement

    // TODO: your product IDs (must match App Store Connect exactly).
    private let productIDs: Set<String> = ["com.example.app.pro.monthly",
                                           "com.example.app.pro.annual"]
    // TODO: your subscription group ID (from ASC) for status queries.
    private let subscriptionGroupID = "TODO_GROUP_ID"

    private var updatesTask: Task<Void, Never>?

    func start() {
        // Begin listening BEFORE loading products so no transaction is missed.
        updatesTask = Task { [weak self] in
            for await result in Transaction.updates {
                await self?.handle(result)
            }
        }
        Task { await load() }
    }

    func load() async {
        state = .loading
        do {
            products = try await Product.products(for: productIDs)
            // TRAP: empty array with no error usually means the account-level
            // Paid Apps Agreement is not Active, or products are Missing Metadata
            // in ASC — check those FIRST, not your code. See SKILL.md StoreKit rows.
            await refreshEntitlement()
            state = .loaded
        } catch {
            state = .failed(error.localizedDescription)
        }
    }

    func purchase(_ product: Product) async throws {
        let result = try await product.purchase()
        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)
            // TODO: if you run a server, confirm the entitlement there BEFORE
            // finishing, so a dropped network call can't strand a paid user.
            await refreshEntitlement()
            await transaction.finish()
        case .userCancelled, .pending:
            break
        @unknown default:
            break
        }
    }

    func restore() async {
        try? await AppStore.sync()
        await refreshEntitlement()
    }

    /// Authoritative entitlement read. Do NOT trust `SubscriptionStatus.all` —
    /// it caches and goes stale after upgrade/downgrade (Xcode 26 StoreKit bug).
    private func refreshEntitlement() async {
        var entitled = false
        for await result in Transaction.currentEntitlements {
            if let transaction = try? checkVerified(result),
               productIDs.contains(transaction.productID) {
                entitled = true
            }
        }
        isPro = entitled
    }

    private func handle(_ result: VerificationResult<Transaction>) async {
        guard let transaction = try? checkVerified(result) else { return }
        await refreshEntitlement()
        await transaction.finish()
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .verified(let safe): return safe
        case .unverified: throw StoreError.failedVerification
        }
    }

    enum StoreError: Error { case failedVerification }
}
```

## PaywallGate.swift

```swift
import SwiftUI

/// Wrap any premium feature: `.paywallGate(isPro: store.isPro) { showPaywall = true }`
/// Locked content stays visible-but-inert so the user sees value before paying
/// (App Review 3.1.1 + higher conversion than a hard wall on first launch).
struct PaywallGate: ViewModifier {
    let isPro: Bool
    let onLocked: () -> Void

    func body(content: Content) -> some View {
        content
            .allowsHitTesting(isPro)
            .overlay {
                if !isPro {
                    Color.clear
                        .contentShape(Rectangle())
                        .onTapGesture(perform: onLocked)
                }
            }
    }
}

extension View {
    func paywallGate(isPro: Bool, onLocked: @escaping () -> Void) -> some View {
        modifier(PaywallGate(isPro: isPro, onLocked: onLocked))
    }
}
```

## Wiring

```swift
@main
struct MyApp: App {
    @State private var entitlements = EntitlementStore()
    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(entitlements)
                .task { entitlements.start() }   // start listener + load once
        }
    }
}
```

## Fill-in checklist

- [ ] Replace `productIDs` and `subscriptionGroupID` with your ASC values.
- [ ] Decide hard-wall vs free-trial paywall (hard walls convert ~10.7% vs ~2.1% — but only after a value preview; never on first launch).
- [ ] If you have a server, confirm entitlement server-side in `purchase(...)` before `finish()`.
- [ ] Test upgrade, downgrade, restore, cancellation in the StoreKit sandbox before TestFlight.
- [ ] Add RevenueCat only when cross-platform entitlements or paywall A/B testing justify the 1% + extra SDK surface.
