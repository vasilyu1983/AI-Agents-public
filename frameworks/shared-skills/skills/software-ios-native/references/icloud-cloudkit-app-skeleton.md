# iCloud and CloudKit App Skeleton

Use this reference when an iOS app needs a database in iCloud without Supabase, Vercel, Firebase, or a custom backend.

## Table of Contents

- [Default Choice](#default-choice)
- [Database Scopes](#database-scopes)
- [Schema Rules](#schema-rules)
- [Implementation Shape](#implementation-shape)
- [No-Server Boundaries](#no-server-boundaries)
- [Testing](#testing)

## Default Choice

Start with SwiftData + CloudKit private database for user-owned data that should sync across the user's devices.

Move to Core Data + `NSPersistentCloudKitContainer` when:

- migrations are already complex
- batch imports or history processing matter
- extensions or multiple writers touch the same store
- you need mature Core Data tooling or an existing Core Data model
- CloudKit sharing is a first-class requirement

Use direct CloudKit when:

- the app needs public records
- the app needs shared records between different iCloud users
- the schema is not a good fit for SwiftData/Core Data mirroring
- you need explicit `CKRecord`, `CKShare`, zone, or subscription control

## Database Scopes

| Scope | Use For | Notes |
|---|---|---|
| Private database | Per-user app data | Requires iCloud account for user-specific writes; best fit for most skeleton apps |
| Shared database | Records another user shared with this user | Use explicit sharing flows; not the same as public data |
| Public database | App-wide content all users can read | Writes still require identity; moderation/admin workflows usually need a backend |

CloudKit is app-container scoped. Do not use it as a global SQL database with service-role writes.

## Schema Rules

For SwiftData or Core Data mirrored to CloudKit:

- Avoid unique constraints in CloudKit-backed models.
- Give properties defaults or make them optional where CloudKit may sync partial records.
- Make relationships optional and handle out-of-order arrival.
- Avoid deny delete rules in SwiftData CloudKit sync paths.
- Treat production schema promotion as a one-way gate; later changes are additive in practice.
- Keep schema versioning and migration plans in the skeleton from day one.

## Implementation Shape

```swift
import SwiftData

enum AppPersistenceMode {
    case localOnly
    case iCloudPrivate(containerIdentifier: String)
}

@MainActor
struct SwiftDataStack {
    let container: ModelContainer

    init(mode: AppPersistenceMode) throws {
        let schema = Schema([
            // App model types here.
        ])

        let configuration: ModelConfiguration
        switch mode {
        case .localOnly:
            configuration = ModelConfiguration(schema: schema, cloudKitDatabase: .none)
        case .iCloudPrivate(let id):
            configuration = ModelConfiguration(schema: schema, cloudKitDatabase: .private(id))
        }

        container = try ModelContainer(for: schema, configurations: [configuration])
    }
}
```

Keep the real skeleton more explicit than this sample:

- model list in one place
- CloudKit container identifier in build configuration
- local-only test configuration
- seeded preview/test data
- sync/account status exposed separately from the data store

## No-Server Boundaries

CloudKit-only is a strong default for private Apple-native apps, but it is the wrong default when the app needs:

- cron jobs or scheduled server work
- service-role/admin writes
- web admin dashboards
- public moderation queues
- complex tenant permissions
- analytics pipelines over all users' private data
- cross-platform web clients with the same data contract
- heavy full-text/vector search over a shared corpus

When any of those become product requirements, route to `software-baas-platforms`, `software-backend`, or `ai-vector-brain` depending on the missing capability.

## Testing

Minimum gates:

1. Local-only configuration test with seeded data.
2. CloudKit-compatible schema lint: optional relationships, no unique constraints, defaults on new fields.
3. Simulator persistence smoke.
4. Real-device iCloud sync smoke on two devices signed into the same account when sync is release-critical.
5. Production schema promotion checklist before App Store release.
6. Migration rehearsal against a non-empty store.
7. Offline edit, relaunch, and later sync test.
8. iOS 26 sync-regression check: verify two-device sync on iOS 26 specifically, and confirm the container loads after a clean install. See [swiftdata-core.md → iOS 26 CloudKit sync regression](swiftdata-core.md#ios-26-cloudkit-sync-regression-known-trap-2026) for the migrate-before-sync ordering and `initializeCloudKitSchema` recovery.
