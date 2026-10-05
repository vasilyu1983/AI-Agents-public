# iOS CloudKit Persistence Stack Template

Use this template when the app wants iCloud-backed data without Supabase, Vercel, or Firebase.

## Decision Record

```text
Primary store:
  [ ] SwiftData + CloudKit private database
  [ ] Core Data + NSPersistentCloudKitContainer
  [ ] Direct CloudKit
  [ ] Local-only first, CloudKit later

CloudKit container:
  identifier:
  development schema initialized:
  production schema promoted:

Data scope:
  [ ] private user data
  [ ] shared records
  [ ] public catalog
```

## SwiftData Stack Shape

```swift
import SwiftData

@MainActor
struct AppModelContainerFactory {
    static func make(containerIdentifier: String?, inMemory: Bool = false) throws -> ModelContainer {
        let schema = Schema([
            // Add @Model types here.
        ])

        let cloudKitDatabase: ModelConfiguration.CloudKitDatabase
        if let containerIdentifier {
            cloudKitDatabase = .private(containerIdentifier)
        } else {
            cloudKitDatabase = .none
        }

        let config = ModelConfiguration(
            schema: schema,
            isStoredInMemoryOnly: inMemory,
            cloudKitDatabase: cloudKitDatabase
        )

        return try ModelContainer(for: schema, configurations: [config])
    }
}
```

## Schema Checklist

- [ ] no `@Attribute(.unique)` or `#Unique` in CloudKit-backed models
- [ ] new properties have defaults or are optional
- [ ] relationships are optional where CloudKit sync can receive records out of order
- [ ] delete rules are safe under eventual consistency
- [ ] migration plan exists before release
- [ ] production schema promotion is explicitly tracked

## Sync UX

Expose sync/account state separately from the data model:

- iCloud available
- iCloud account missing/restricted
- model not synced yet
- last successful import/export timestamp if observable
- local-only mode
- conflict or migration error state
