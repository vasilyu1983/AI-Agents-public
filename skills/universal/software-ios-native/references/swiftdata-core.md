# SwiftData Core Reference

Essential rules for writing correct SwiftData code. Covers modeling, predicates, CloudKit constraints, indexing, and class inheritance.

Primary docs:

- https://developer.apple.com/documentation/swiftdata
- https://developer.apple.com/videos/play/wwdc2023/10187/
- https://developer.apple.com/videos/play/wwdc2024/10137/

## Table of Contents

- [Core Rules](#core-rules)
- [Relationships](#relationships)
- [Predicates](#predicates)
- [Migrations](#migrations)
- [CloudKit Constraints](#cloudkit-constraints)
- [Indexing (iOS 18+)](#indexing-ios-18)
- [Class Inheritance (iOS 26+)](#class-inheritance-ios-26)
- [Common Anti-Patterns](#common-anti-patterns)

## Core Rules

### Autosaving

Autosaving is unpredictable — prefer explicit `modelContext.save()` at known-good points. Do not check `hasChanges` before saving; the save call is cheap and the check is unreliable.

### Actor Isolation

`ModelContext` and model instances must never cross actor boundaries. Send `PersistentIdentifier` values instead and re-fetch on the destination actor:

```swift
// WRONG — sending model across actors
let user = try modelContext.fetch(...)
await backgroundActor.process(user)  // Crash or data corruption

// CORRECT — send the identifier
let userId = user.persistentModelID
await backgroundActor.process(userId)

// On the destination actor
func process(_ id: PersistentIdentifier) {
    let user = modelContext.model(for: id) as? User
}
```

Persistent identifiers are temporary before the first `save()` — they start with "t" and are not stable for cross-context use until persisted.

### @Query

`@Query` only works inside SwiftUI views. For programmatic fetching, use `ModelContext.fetch(_:)` with `FetchDescriptor`.

Use `fetchCount()` when you only need a count — it is more efficient but does not live-update like `@Query`.

For performance, use `propertiesToFetch` and `relationshipKeyPathsForPrefetching` on `FetchDescriptor` to limit what's loaded.

### Property Constraints

- Cannot use `description` as a property name (conflicts with `CustomStringConvertible`)
- Property observers (`willSet`, `didSet`) are silently ignored on `@Model` classes
- `@Transient` properties must have a default value — prefer computed properties for derived data
- `@Attribute(.externalStorage)` is a suggestion, not a guarantee — only works with `Data` type
- Enum properties must conform to `Codable` — associated values are supported

### Uniqueness

Use `#Unique` to define unique constraints. A single model can have one `#Unique` declaration, but it can contain multiple key path arrays for separate constraints:

```swift
@Model
class User {
    var email: String
    var username: String

    #Unique<User>([\.email], [\.username])
}
```

## Relationships

- Define `@Relationship` on one side only to avoid circular reference issues
- Always define explicit inverse relationships — SwiftData frequently infers them incorrectly
- Nearly always set an explicit delete rule — the default `.nullify` can orphan data or crash when the graph expects the related object

```swift
@Model
class Author {
    var name: String
    @Relationship(deleteRule: .cascade, inverse: \Book.author)
    var books: [Book] = []
}

@Model
class Book {
    var title: String
    var author: Author?
}
```

## Predicates

### Supported Operations

```swift
// String matching (case-insensitive, locale-aware)
#Predicate<User> { $0.name.localizedStandardContains(searchText) }

// Prefix matching
#Predicate<User> { $0.name.starts(with: prefix) }

// Boolean negation — use ! not == false
#Predicate<Item> { !$0.items.isEmpty }  // CORRECT
// #Predicate<Item> { $0.items.isEmpty == false }  // CRASHES at runtime
```

### Unsupported in Predicates (compile but crash or produce wrong results)

| Operation | Status | Alternative |
|---|---|---|
| `hasSuffix()` | Unsupported | Fetch and filter in memory |
| `lowercased()` / `uppercased()` | Unsupported | Use `localizedStandardContains` |
| `map`, `reduce`, `compactMap` | Unsupported | Fetch and transform in memory |
| `count(where:)` | Unsupported | Fetch and count in memory |
| `first` / `last` on collections | Unsupported | Fetch the collection and access in memory |
| Custom operators | Unsupported | Express as standard comparisons |
| Computed properties | Unsupported | Use stored properties only |
| `@Transient` properties | Unsupported | Use stored properties in predicates |
| Custom `Codable` struct properties | Unsupported | Flatten to scalar stored properties |
| Regex | Unsupported | Use `localizedStandardContains` or fetch+filter |

### Dangerous Predicates

These compile without error but crash at runtime:

```swift
// CRASHES — isEmpty == false
#Predicate<Folder> { $0.items.isEmpty == false }

// SAFE — use negation operator
#Predicate<Folder> { !$0.items.isEmpty }
```

## Migrations

Nearly always define a migration schema. Without one, any model change risks silent data loss or a crash on launch.

```swift
enum MySchemaV1: VersionedSchema {
    static let versionIdentifier = Schema.Version(1, 0, 0)
    static let models: [any PersistentModel.Type] = [User.self]

    @Model class User {
        var name: String
    }
}

enum MySchemaV2: VersionedSchema {
    static let versionIdentifier = Schema.Version(2, 0, 0)
    static let models: [any PersistentModel.Type] = [User.self]

    @Model class User {
        var name: String
        var email: String = ""  // New property with default
    }
}

enum MyMigrationPlan: SchemaMigrationPlan {
    static let schemas: [any VersionedSchema.Type] = [MySchemaV1.self, MySchemaV2.self]
    static let stages: [MigrationStage] = [
        .lightweight(fromVersion: MySchemaV1.self, toVersion: MySchemaV2.self)
    ]
}
```

## CloudKit Constraints

When using SwiftData with CloudKit (`NSPersistentCloudKitContainer` or CloudKit-enabled container):

| Rule | Reason |
|---|---|
| No `@Attribute(.unique)` or `#Unique` | CloudKit does not support unique constraints |
| All properties must have defaults or be optional | CloudKit may sync partial records |
| All relationships must be optional | Related records may arrive out of order |
| Code must handle eventual consistency | Records sync asynchronously across devices |

Indexes and subclasses are supported on correct OS versions.

### iOS 26 CloudKit sync regression (known trap, 2026)

After the iOS 26 update, SwiftData automatic CloudKit sync regressed for some apps: sync stops and the CloudKit Console shows `BAD_REQUEST` errors on push. WWDC25 added only model inheritance to SwiftData — it did **not** expand sync (still no public/shared scope, no dynamic predicates), so the iOS 26 story is "stability + inheritance," and this sync break is the main field hazard. Workarounds, in order:

1. **Migrate before syncing.** If the `ModelContainer` fails to load with CloudKit enabled, build it once with `cloudKitDatabase: .none` so the local store completes migration, then rebuild with CloudKit enabled. A container that never migrated cleanly cannot sync.
2. **Force schema match.** When sync produces partial data or unsynced relationships, the cloud schema is behind the local model. Call `initializeCloudKitSchema` (debug builds, signed into iCloud) to push the local model into the CloudKit container, then promote the schema in the CloudKit Console.
3. **macOS only:** explicitly add `CloudKit.framework` under *Frameworks, Libraries, and Embedded Content*. The CloudKit service can fail to initialize without it, and SwiftData reports it as a generic sync failure.
4. **Re-provision the container** as a last resort: toggle *Automatically manage signing*, add a fresh CloudKit container, re-promote the schema.

Do not assume a sync failure is your model code first — on iOS 26 specifically, suspect the environment regression and the migration-before-sync ordering. See [icloud-cloudkit-app-skeleton.md](icloud-cloudkit-app-skeleton.md) for the broader no-server decision tree.

## Indexing (iOS 18+)

Add indexes to speed up common queries. Small write performance cost.

```swift
@Model
class Transaction {
    var date: Date
    var amount: Double
    var category: String

    // Single-property indexes
    #Index<Transaction>([\.date])

    // Compound index for common query patterns
    #Index<Transaction>([\.category, \.date])
}
```

## Class Inheritance (iOS 26+)

SwiftData supports model subclassing on iOS 26+.

```swift
@Model
class Vehicle {
    var make: String
    var year: Int
}

@available(iOS 26, *)  // Required even if iOS 26 is minimum deployment target
@Model
class ElectricVehicle: Vehicle {
    var batteryCapacity: Double
}
```

Rules:

- Both parent and child classes need `@Model` macro
- Child classes must have `@available(iOS 26, *)` — even when iOS 26 is the minimum deployment target
- List both parent and children in the schema when creating the container
- `@Query` for a base class returns all subclass instances too
- Use `is` in `#Predicate` to filter for specific subclasses
- Typecast results with `as` for child-specific properties
- Relationships can reference parent or any subclass type

## Traps and Edge Cases

### @Query with SortDescriptor on optional property can crash

`SortDescriptor(\.optionalProperty)` in `@Query` may crash at runtime even though it compiles. Test sort descriptors against real data including nil values before shipping.

### Array of @Model types implicitly creates a relationship

Any `@Model` type referenced as a property of another `@Model` is automatically treated as a relationship — not a plain stored property. `[ModelType]` becomes a to-many relationship with cascade/nullify implications. If you want a plain stored array, use a `Codable` value type instead.

### modelContext.delete() does not immediately remove from @Query

After `modelContext.delete(item)`, the item may still appear in `@Query` results until the next `save()` or UI update cycle. Save explicitly if you need immediate removal from the UI.

### Development-time schema mismatch silently wipes data

Before your first release, if the model schema changes and no migration is defined, SwiftData recreates the store empty — all test data is silently lost. This is expected behavior during development but surprises developers who have been building up test data.

### AsyncStream.finish() must be called on ALL exit paths

If the producer throws, returns early, or is deallocated without calling `continuation.finish()`, the `for await` consumer hangs forever. Wire `onTermination` as a safety net, and audit every error/return path in the producer.

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Accessing models across actor boundaries | Crash or data corruption | Send `PersistentIdentifier`, re-fetch on destination |
| `@Relationship` on both sides | Circular reference issues | Define on one side only with explicit inverse |
| Missing migration schema | Silent data loss on model changes | Always define `VersionedSchema` and `SchemaMigrationPlan` |
| Default `.nullify` delete rule | Orphaned data or crashes | Set explicit delete rule (`.cascade`, `.deny`, or intentional `.nullify`) |
| `@AppStorage` for SwiftData-managed values | Two sources of truth | Use SwiftData for persistent model state |
| Computed properties in predicates | Runtime crash | Use stored properties only |
| `isEmpty == false` in predicates | Runtime crash | Use `!isEmpty` |
| Using `@Query` outside SwiftUI views | Does not compile | Use `ModelContext.fetch()` with `FetchDescriptor` |
| Trusting temporary persistent IDs | ID changes after first save | Save before sharing IDs across contexts |
