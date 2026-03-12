# Offline-First Mobile Architecture

Patterns for building mobile apps that work without a network connection. Covers architecture models, local database strategies, sync patterns, conflict resolution, queue-based operations, network state detection, optimistic updates, background sync, and testing.

---

## Offline-First vs Offline-Capable

| Characteristic | Offline-First | Offline-Capable |
|---------------|---------------|-----------------|
| **Data source** | Local database is primary | Server is primary, local cache |
| **Default state** | App works without network | App degrades without network |
| **Sync direction** | Bidirectional (local <-> server) | Mostly server -> local |
| **Write path** | Writes to local, syncs later | Writes to server, caches locally |
| **Conflict handling** | Must resolve conflicts | Minimal conflicts (server wins) |
| **Complexity** | High | Medium |
| **Best for** | Field apps, travel, poor connectivity | E-commerce, social, content apps |

### Architecture Decision

```text
Choose offline-first when:
  ✓ Users regularly have no connectivity (field work, travel, rural)
  ✓ Data entry happens offline (forms, surveys, inspections)
  ✓ App must be fully functional without network
  ✓ Sync can be deferred for hours or days

Choose offline-capable when:
  ✓ Users are usually online but need graceful degradation
  ✓ Reads are more common than writes
  ✓ Stale data is acceptable for short periods
  ✓ Server is the authority for most operations
```

---

## Local Database Strategies

### Platform Comparison

| Database | Platform | Type | Reactive | Sync Support | Best For |
|----------|----------|------|----------|-------------|----------|
| **Core Data** | iOS | ORM/Object graph | Combine, async | CloudKit | iOS-only apps |
| **SwiftData** | iOS 17+ | ORM (Swift macros) | SwiftUI native | CloudKit | Modern SwiftUI apps |
| **Room** | Android | ORM over SQLite | Flow, LiveData | Custom | Android-only apps |
| **WatermelonDB** | React Native | Lazy-loading ORM | Observable | Custom sync | RN offline-first apps |
| **Realm** | All | Object database | Reactive | Atlas Device Sync | Cross-platform with sync |
| **SQLDelight** | KMP | Type-safe SQL | Flow | Custom | KMP shared data layer |
| **MMKV** | All | Key-value | No | No | Fast preferences, small data |
| **SQLite (raw)** | All | Relational | No | Custom | Full control, small footprint |

### iOS: Core Data / SwiftData

```swift
// SwiftData model with offline sync metadata
@Model
final class Task {
    var id: UUID
    var title: String
    var isCompleted: Bool
    var updatedAt: Date

    // Sync metadata
    var syncStatus: SyncStatus
    var localVersion: Int
    var serverVersion: Int?

    enum SyncStatus: String, Codable {
        case synced
        case pendingUpload
        case pendingDelete
        case conflict
    }

    init(title: String) {
        self.id = UUID()
        self.title = title
        self.isCompleted = false
        self.updatedAt = Date()
        self.syncStatus = .pendingUpload
        self.localVersion = 1
    }
}
```

### Android: Room

```kotlin
@Entity(tableName = "tasks")
data class TaskEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val title: String,
    val isCompleted: Boolean = false,
    val updatedAt: Long = System.currentTimeMillis(),

    // Sync metadata
    val syncStatus: SyncStatus = SyncStatus.PENDING_UPLOAD,
    val localVersion: Int = 1,
    val serverVersion: Int? = null,
)

enum class SyncStatus {
    SYNCED,
    PENDING_UPLOAD,
    PENDING_DELETE,
    CONFLICT,
}

@Dao
interface TaskDao {
    @Query("SELECT * FROM tasks WHERE syncStatus != 'PENDING_DELETE' ORDER BY updatedAt DESC")
    fun observeAll(): Flow<List<TaskEntity>>

    @Query("SELECT * FROM tasks WHERE syncStatus IN ('PENDING_UPLOAD', 'PENDING_DELETE')")
    suspend fun getPendingSync(): List<TaskEntity>

    @Upsert
    suspend fun upsert(task: TaskEntity)

    @Query("UPDATE tasks SET syncStatus = :status WHERE id = :id")
    suspend fun updateSyncStatus(id: String, status: SyncStatus)
}
```

### React Native: WatermelonDB

```typescript
// model/Task.ts
import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export default class Task extends Model {
  static table = 'tasks';

  @field('title') title!: string;
  @field('is_completed') isCompleted!: boolean;
  @field('sync_status') syncStatus!: string; // 'synced' | 'pending' | 'conflict'
  @field('local_version') localVersion!: number;
  @field('server_version') serverVersion!: number | null;
  @readonly @date('created_at') createdAt!: Date;
  @readonly @date('updated_at') updatedAt!: Date;
}
```

---

## Sync Strategies

### Strategy Comparison

| Strategy | Direction | Latency | Complexity | Best For |
|----------|-----------|---------|------------|----------|
| **Push-based** | Client -> Server | Low (on change) | Medium | Write-heavy apps |
| **Pull-based** | Server -> Client | Higher (polling) | Low | Read-heavy apps |
| **Real-time** | Bidirectional | Lowest | High | Collaborative apps |
| **Batch** | Bidirectional | Highest (scheduled) | Medium | Periodic sync (e.g., daily) |
| **Delta sync** | Bidirectional | Medium | High | Large datasets |

### Delta Sync Pattern

```typescript
// Delta sync: only transfer changes since last sync
interface SyncRequest {
  lastSyncTimestamp: string; // ISO 8601
  clientChanges: ChangeSet[];
}

interface ChangeSet {
  table: string;
  created: Record<string, unknown>[];
  updated: Record<string, unknown>[];
  deleted: string[]; // IDs
}

interface SyncResponse {
  serverChanges: ChangeSet[];
  currentTimestamp: string;
  conflicts: ConflictItem[];
}

// Client-side sync coordinator
async function performSync(): Promise<SyncResult> {
  const lastSync = await getLastSyncTimestamp();
  const localChanges = await getLocalChangesSince(lastSync);

  const response = await api.sync({
    lastSyncTimestamp: lastSync,
    clientChanges: localChanges,
  });

  // Apply server changes to local DB
  await applyServerChanges(response.serverChanges);

  // Handle conflicts
  if (response.conflicts.length > 0) {
    await resolveConflicts(response.conflicts);
  }

  // Update sync timestamp
  await setLastSyncTimestamp(response.currentTimestamp);

  // Mark local changes as synced
  await markAsSynced(localChanges);

  return { success: true, conflictsResolved: response.conflicts.length };
}
```

---

## Conflict Resolution

### Strategies

| Strategy | How It Works | Data Loss Risk | Best For |
|----------|-------------|---------------|----------|
| **Last-write-wins (LWW)** | Most recent timestamp wins | Medium | Simple apps, non-critical data |
| **Client-wins** | Local change always wins | Low for user | Single-user apps |
| **Server-wins** | Server change always wins | Low for system | Server-authoritative data |
| **Field-level merge** | Merge non-conflicting fields | Low | Forms, profiles |
| **Manual resolution** | Present both versions to user | None | Critical data, collaborative |
| **CRDT** | Conflict-free replicated data types | None | Real-time collaborative |

### Field-Level Merge Implementation

```typescript
// Merge non-conflicting field changes
function mergeTask(
  base: Task,       // Last synced version
  local: Task,      // Local changes
  server: Task,     // Server changes
): { merged: Task; hasConflict: boolean } {
  const merged = { ...base };
  let hasConflict = false;

  for (const field of ['title', 'isCompleted', 'dueDate', 'assignee'] as const) {
    const localChanged = local[field] !== base[field];
    const serverChanged = server[field] !== base[field];

    if (localChanged && serverChanged && local[field] !== server[field]) {
      // Both changed the same field to different values — conflict
      hasConflict = true;
      merged[field] = server[field]; // Default: server wins on conflict
    } else if (localChanged) {
      merged[field] = local[field];
    } else if (serverChanged) {
      merged[field] = server[field];
    }
  }

  return { merged, hasConflict };
}
```

### Manual Resolution UI Pattern

```text
Conflict resolution screen:
┌─────────────────────────────────────────┐
│ Conflict Detected                       │
│                                         │
│ Field: Title                            │
│ ┌─────────────┐  ┌──────────────────┐  │
│ │ Your version│  │ Server version   │  │
│ │ "Buy milk"  │  │ "Buy groceries"  │  │
│ └─────────────┘  └──────────────────┘  │
│                                         │
│ [Keep Mine] [Keep Theirs] [Edit Merge]  │
└─────────────────────────────────────────┘
```

---

## Queue-Based Operation Patterns

### Command Queue (Outbox Pattern)

```typescript
// Operations are queued locally and replayed when online
interface QueuedOperation {
  id: string;
  type: 'create' | 'update' | 'delete';
  table: string;
  payload: Record<string, unknown>;
  createdAt: string;
  retryCount: number;
  maxRetries: number;
  status: 'pending' | 'processing' | 'failed' | 'completed';
}

class OperationQueue {
  private db: LocalDatabase;

  async enqueue(operation: Omit<QueuedOperation, 'id' | 'createdAt' | 'retryCount' | 'status'>): Promise<void> {
    await this.db.operations.insert({
      ...operation,
      id: generateUUID(),
      createdAt: new Date().toISOString(),
      retryCount: 0,
      status: 'pending',
    });
  }

  async processQueue(): Promise<void> {
    const pending = await this.db.operations
      .query()
      .where('status', 'pending')
      .orderBy('createdAt', 'asc')
      .fetch();

    for (const op of pending) {
      try {
        await this.db.operations.update(op.id, { status: 'processing' });
        await this.executeOperation(op);
        await this.db.operations.update(op.id, { status: 'completed' });
      } catch (error) {
        const newRetryCount = op.retryCount + 1;
        if (newRetryCount >= op.maxRetries) {
          await this.db.operations.update(op.id, { status: 'failed', retryCount: newRetryCount });
        } else {
          await this.db.operations.update(op.id, { status: 'pending', retryCount: newRetryCount });
        }
      }
    }
  }

  private async executeOperation(op: QueuedOperation): Promise<void> {
    switch (op.type) {
      case 'create':
        await api.post(`/${op.table}`, op.payload);
        break;
      case 'update':
        await api.put(`/${op.table}/${op.payload.id}`, op.payload);
        break;
      case 'delete':
        await api.delete(`/${op.table}/${op.payload.id}`);
        break;
    }
  }
}
```

---

## Network State Detection

### Platform-Specific Detection

```swift
// iOS: NWPathMonitor
import Network

class NetworkMonitor: ObservableObject {
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")

    @Published var isConnected = true
    @Published var connectionType: ConnectionType = .unknown

    enum ConnectionType {
        case wifi, cellular, wired, unknown
    }

    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
                self?.connectionType = self?.getConnectionType(path) ?? .unknown
            }
        }
        monitor.start(queue: queue)
    }

    private func getConnectionType(_ path: NWPath) -> ConnectionType {
        if path.usesInterfaceType(.wifi) { return .wifi }
        if path.usesInterfaceType(.cellular) { return .cellular }
        if path.usesInterfaceType(.wiredEthernet) { return .wired }
        return .unknown
    }
}
```

```kotlin
// Android: ConnectivityManager
class NetworkMonitor(context: Context) {
    private val connectivityManager =
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    val isConnected: StateFlow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(true) }
            override fun onLost(network: Network) { trySend(false) }
        }

        connectivityManager.registerDefaultNetworkCallback(callback)
        trySend(connectivityManager.activeNetwork != null)

        awaitClose { connectivityManager.unregisterNetworkCallback(callback) }
    }.stateIn(CoroutineScope(Dispatchers.Default), SharingStarted.Eagerly, true)
}
```

### Graceful Degradation Pattern

```typescript
// Show connectivity status and degrade features
function useOfflineAwareAction<T>(
  onlineAction: () => Promise<T>,
  offlineAction: () => Promise<T>,
) {
  const { isConnected } = useNetworkState();

  return useCallback(async () => {
    if (isConnected) {
      try {
        return await onlineAction();
      } catch (error) {
        if (isNetworkError(error)) {
          return await offlineAction();
        }
        throw error;
      }
    }
    return await offlineAction();
  }, [isConnected, onlineAction, offlineAction]);
}
```

---

## Optimistic Updates with Rollback

```typescript
// Pattern: Update UI immediately, sync in background, rollback on failure
async function toggleTaskComplete(taskId: string): Promise<void> {
  const task = await db.tasks.find(taskId);
  const previousState = { ...task };

  // 1. Optimistic update — UI updates immediately
  await db.tasks.update(taskId, {
    isCompleted: !task.isCompleted,
    updatedAt: new Date().toISOString(),
    syncStatus: 'pending',
  });

  // 2. Attempt server sync
  try {
    await api.updateTask(taskId, { isCompleted: !task.isCompleted });
    await db.tasks.update(taskId, { syncStatus: 'synced' });
  } catch (error) {
    if (isNetworkError(error)) {
      // Queue for later sync — keep optimistic update
      await operationQueue.enqueue({
        type: 'update',
        table: 'tasks',
        payload: { id: taskId, isCompleted: !task.isCompleted },
        maxRetries: 5,
      });
    } else {
      // Server rejected the change — rollback
      await db.tasks.update(taskId, previousState);
      showError('Failed to update task');
    }
  }
}
```

---

## Background Sync

### iOS: BGTaskScheduler

```swift
import BackgroundTasks

class BackgroundSyncManager {
    static let syncTaskIdentifier = "com.myapp.sync"

    static func register() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: syncTaskIdentifier,
            using: nil
        ) { task in
            handleSync(task: task as! BGAppRefreshTask)
        }
    }

    static func scheduleSync() {
        let request = BGAppRefreshTaskRequest(identifier: syncTaskIdentifier)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15 min
        try? BGTaskScheduler.shared.submit(request)
    }

    private static func handleSync(task: BGAppRefreshTask) {
        let syncTask = Task {
            do {
                try await SyncService.shared.performFullSync()
                task.setTaskCompleted(success: true)
            } catch {
                task.setTaskCompleted(success: false)
            }
        }

        task.expirationHandler = { syncTask.cancel() }
        scheduleSync() // Reschedule for next sync
    }
}
```

### Android: WorkManager

```kotlin
class SyncWorker(
    context: Context,
    params: WorkerParameters,
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            SyncService.getInstance().performFullSync()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }

    companion object {
        fun schedule(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val request = PeriodicWorkRequestBuilder<SyncWorker>(
                15, TimeUnit.MINUTES,
            )
                .setConstraints(constraints)
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .build()

            WorkManager.getInstance(context)
                .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, request)
        }
    }
}
```

---

## Data Migration for Local Databases

### Room Migration

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE tasks ADD COLUMN sync_status TEXT NOT NULL DEFAULT 'synced'")
        db.execSQL("ALTER TABLE tasks ADD COLUMN local_version INTEGER NOT NULL DEFAULT 1")
    }
}

val database = Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .addMigrations(MIGRATION_1_2)
    .build()
```

### Core Data Lightweight Migration

```swift
let container = NSPersistentContainer(name: "MyApp")
let description = container.persistentStoreDescriptions.first!
description.setOption(true as NSNumber, forKey: NSMigratePersistentStoresAutomaticallyOption)
description.setOption(true as NSNumber, forKey: NSInferMappingModelAutomaticallyOption)
```

---

## Testing Offline Scenarios

### Network Condition Simulation

```typescript
// Playwright: simulate offline
test('works offline', async ({ page, context }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');

  // Go offline
  await context.setOffline(true);

  // Perform action
  await page.click('[data-testid="add-task"]');
  await page.fill('[data-testid="task-title"]', 'Offline task');
  await page.click('[data-testid="save-task"]');

  // Verify task appears in local list
  await expect(page.locator('[data-testid="task-list"]'))
    .toContainText('Offline task');

  // Verify sync indicator
  await expect(page.locator('[data-testid="sync-status"]'))
    .toContainText('Pending');

  // Go back online
  await context.setOffline(false);

  // Verify sync completes
  await expect(page.locator('[data-testid="sync-status"]'))
    .toContainText('Synced');
});
```

### Unit Testing Sync Logic

```typescript
describe('SyncService', () => {
  it('queues operations when offline', async () => {
    const queue = new OperationQueue(mockDb);
    const syncService = new SyncService(mockApi, mockDb, queue);

    mockApi.updateTask.mockRejectedValue(new NetworkError());

    await syncService.updateTask('task-1', { title: 'Updated' });

    const pending = await queue.getPending();
    expect(pending).toHaveLength(1);
    expect(pending[0].type).toBe('update');
  });

  it('resolves conflicts with field-level merge', async () => {
    const result = mergeTask(
      { title: 'Original', isCompleted: false, dueDate: '2026-01-01' },
      { title: 'Local edit', isCompleted: false, dueDate: '2026-01-01' },
      { title: 'Original', isCompleted: true, dueDate: '2026-01-01' },
    );

    expect(result.merged.title).toBe('Local edit');
    expect(result.merged.isCompleted).toBe(true);
    expect(result.hasConflict).toBe(false);
  });
});
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No sync metadata on entities | Cannot track what needs syncing | Add syncStatus, localVersion, updatedAt |
| Last-write-wins for all data | Silent data loss | Use field-level merge for important data |
| Unbounded operation queue | Memory and storage growth | Set max queue size, expire old operations |
| No migration strategy | App crashes on schema change | Plan migrations from day one |
| Syncing on every change | Battery drain, server load | Batch changes, sync on schedule or connectivity change |
| No conflict UI | Users never know data was overwritten | Show conflict indicators, provide resolution UI |

---

## Cross-References

- [cross-platform-comparison.md](cross-platform-comparison.md) — Database options per platform
- [mobile-testing-patterns.md](mobile-testing-patterns.md) — Testing offline scenarios
- [ios-best-practices.md](ios-best-practices.md) — Core Data, SwiftData patterns
- [android-best-practices.md](android-best-practices.md) — Room, DataStore patterns
- [operational-playbook.md](operational-playbook.md) — Background task scheduling
