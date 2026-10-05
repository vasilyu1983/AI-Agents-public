# Core Data Persistence

Use this reference when the iOS task is Core Data-heavy: stack setup, context ownership, threading, migrations, batch operations, or `NSPersistentCloudKitContainer`.

## Default Model

- Prefer a single `NSPersistentContainer` or `NSPersistentCloudKitContainer` owned by an app-level service on the main actor.
- Treat `viewContext` as UI-facing state only. Configure `automaticallyMergesChangesFromParent = true` when background saves are expected to feed SwiftUI lists.
- Create dedicated background contexts for imports, sync, backfills, and batch writes. Do not run heavy work on `viewContext`.

## Context And Isolation Rules

- Never pass `NSManagedObject` instances across contexts, actors, or task boundaries.
- Pass `NSManagedObjectID` instead, then re-fetch on the destination context or actor.
- If strict concurrency starts surfacing main-actor isolation errors around fetched objects, assume the fix is object-ID handoff first.
- Keep Core Data access behind explicit ownership boundaries. UI stores should ask a persistence service for work instead of reaching into arbitrary contexts.

## Save And Merge Discipline

- Save child or background contexts intentionally and in bounded units of work.
- After background saves, rely on merge notifications or `automaticallyMergesChangesFromParent` instead of manually patching SwiftUI state from stale objects.
- When using merge policies, document which side wins. Silent overwrite behavior becomes data-loss behavior later.

## Batch Operations

- Use `NSBatchDeleteRequest` or batch updates only for large maintenance work, not routine UI mutations.
- Request object IDs from batch deletes when the UI must stay coherent, then merge those changes back into live contexts.
- Assume batch operations bypass normal object graph bookkeeping. Validate side effects on fetched results, derived counts, and relationship caches.

## Persistent History Tracking

- Use persistent history tracking when multiple writers exist: app plus extensions, background importers, or CloudKit mirroring.
- Persist the last processed history token and replay transactions in order.
- Treat history processing as infrastructure, not ad hoc cleanup logic inside view models.

## Migration Ladder

1. Try lightweight migration first for additive or rename-safe changes.
2. Use staged or custom migration when relationships, transforms, uniqueness, or model splits make lightweight migration unreliable.
3. Rehearse migrations against realistic stores before shipping schema changes.

- Never treat migration success on an empty simulator database as evidence for production data safety.

## CloudKit Constraints

- `NSPersistentCloudKitContainer` is the right default only when the product genuinely needs Apple-account sync semantics.
- Production CloudKit schemas are effectively immutable in the ways that matter to shipping apps. Treat model mistakes as expensive.
- Validate delete rules, optionality, uniqueness expectations, and record-volume assumptions before enabling production mirroring.
- If CloudKit-backed Core Data changes are planned late in a release, slow down and re-check schema impact first.

## Performance And Testing

- Measure fetch scope, faulting, prefetching, and sort/index choices before blaming SwiftUI.
- Keep fetches narrow and paginated where possible; wide eager loads create fake "UI performance" issues that are really persistence issues.
- Unit-test repository or persistence-service behavior separately from SwiftUI.
- For migration, batch operations, or CloudKit sync paths, prefer integration-style tests with seeded stores over view-level tests.
