# Networking and Data Loading

Durable patterns for the networking layer, list pagination, image caching, and field performance metrics. Moved from the retired software-mobile Swift templates, with their bugs fixed. Token storage is owned by [software-security-appsec](../../software-security-appsec/assets/mobile/template-mobile-security.md). Whether the client should be an `actor` or a `@MainActor final class` is covered in [swiftui-observation-concurrency.md](swiftui-observation-concurrency.md#actor--mainactor-final-class-refactoring-guidance).

## Contents

- [API Client Shape](#api-client-shape)
- [In-Flight Request Coalescing](#in-flight-request-coalescing)
- [Pagination](#pagination)
- [Image Cache](#image-cache)
- [Field Performance Metrics](#field-performance-metrics)

## API Client Shape

- Use one injected client type. Do not use `static let shared` singletons that views reach for directly, because tests cannot replace them. Inject the client as a protocol or closure so previews and tests can stub it.
- Map the status code before you decode. `2xx` means decode, `401` means one refresh then retry, and everything else becomes a typed error that carries the server's error body when it decodes.
- Configure `JSONDecoder` and `JSONEncoder` (date strategy, key strategy) once, in the client. Do not configure them per call.
- Read the auth token from a token provider at request-build time. Do not cache it in a stored property, or a refresh leaves stale headers in flight.
- Let `CancellationError` and `URLError(.cancelled)` pass through untouched. Never show them to the user as failures.

```swift
enum APIError: Error {
    case unauthorized
    case server(status: Int, message: String?)
    case invalidResponse
}

struct Endpoint<Response: Decodable> {
    var path: String
    var method = "GET"
    var body: (any Encodable)?
}

final class APIClient {
    private let baseURL: URL
    private let session: URLSession
    private let tokens: TokenProvider          // Keychain-backed; see software-security-appsec
    private let decoder: JSONDecoder = {
        let d = JSONDecoder(); d.dateDecodingStrategy = .iso8601; return d
    }()

    init(baseURL: URL, session: URLSession = .shared, tokens: TokenProvider) {
        self.baseURL = baseURL; self.session = session; self.tokens = tokens
    }

    func send<R>(_ endpoint: Endpoint<R>) async throws -> R {
        var request = URLRequest(url: baseURL.appending(path: endpoint.path))
        request.httpMethod = endpoint.method
        if let body = endpoint.body {
            request.httpBody = try JSONEncoder().encode(body)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        if let token = try await tokens.currentToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        switch http.statusCode {
        case 200..<300: return try decoder.decode(R.self, from: data)
        case 401:       throw APIError.unauthorized   // caller or a wrapper refreshes once, then retries
        default:        throw APIError.server(status: http.statusCode,
                                              message: String(data: data, encoding: .utf8))
        }
    }
}
```

When several requests get a `401` at the same time, refresh the token once. Store the refresh `Task` and have every caller await it, as in the next section. Do not start one refresh per failed request.

## In-Flight Request Coalescing

When two callers ask for the same resource, they should share one network call. Store the `Task` in the dictionary before the first `await`. An actor is reentrant, so if you check the dictionary, await, and only then insert, a second caller can slip in and start a duplicate request.

```swift
actor RequestCoalescer<Key: Hashable & Sendable, Value: Sendable> {
    private var inFlight: [Key: Task<Value, Error>] = [:]

    func value(for key: Key, load: @escaping @Sendable () async throws -> Value) async throws -> Value {
        if let existing = inFlight[key] { return try await existing.value }
        let task = Task { try await load() }
        inFlight[key] = task                 // inserted before any suspension point
        defer { inFlight[key] = nil }
        return try await task.value
    }
}
```

To cap concurrency, bound a task group. See [swift-concurrency-patterns.md](swift-concurrency-patterns.md#limiting-concurrency). Do not hand-roll a queue of continuations. The retired template did, and a slot it freed early could let the queue exceed the limit.

## Pagination

- Trigger the next page from the appearing item's **id** (last item, or a few before it). Do not compare list indices. Index-based triggers misfire after inserts and deletes.
- Guard with `isLoading` and `hasMore`. Set `hasMore = false` when the server says so (cursor is `nil`). Do not infer it from "the page came back short".
- Prefer cursor pagination over page numbers for feeds that change while the user scrolls.
- A pull-to-refresh cancels the in-flight page task and resets the cursor. If it does not, a late page response appends stale items.

```swift
@MainActor @Observable
final class FeedModel {
    private(set) var items: [Post] = []
    private(set) var isLoading = false
    private var cursor: String?
    private var hasMore = true
    private var pageTask: Task<Void, Never>?
    private let api: APIClient
    init(api: APIClient) { self.api = api }

    func onAppear(of item: Post) {
        guard item.id == items.last?.id else { return }
        loadNextPage()
    }

    func refresh() {
        pageTask?.cancel(); items = []; cursor = nil; hasMore = true
        isLoading = false                      // the cancelled task will not reset it (see defer)
        loadNextPage()
    }

    func loadNextPage() {
        guard !isLoading, hasMore else { return }
        isLoading = true
        pageTask = Task {
            defer { if !Task.isCancelled { isLoading = false } }
            guard let page = try? await api.send(Endpoint<Page<Post>>(path: "posts?cursor=\(cursor ?? "")")),
                  !Task.isCancelled else { return }
            items.append(contentsOf: page.items)
            cursor = page.nextCursor
            hasMore = page.nextCursor != nil
        }
    }
}
```

## Image Cache

- Check first whether `URLCache` with correct server cache headers already covers the need. Build a custom cache only for decoded-image reuse or offline availability.
- Use two tiers. The memory tier is an `NSCache` with a `totalCostLimit`, costed by decoded bytes. The disk tier goes under the Caches directory, which the OS may purge.
- **Key the disk file by a stable digest of the URL** (for example, SHA-256 via CryptoKit). Never use `String.hashValue`. Swift randomizes hash seeds per process, so a `hashValue` key misses every entry after relaunch. The retired template had this bug.
- Downsample to the display size (ImageIO thumbnail APIs) before you cache the decoded image. A full-resolution decode in a list is the usual memory spike.
- Empty the memory tier on a memory warning. Evict disk entries by age or total size in a background task. Never evict them on the main actor at launch.
- Coalesce concurrent loads of the same URL with the pattern above.

## Field Performance Metrics

- **Locally:** use Instruments (Time Profiler, Allocations, Leaks, Hangs) and `os_signpost` / `OSSignposter` intervals around the operations you care about. Record from the command line with `xcrun xctrace record --template 'Time Profiler' --device <name-or-UDID> --launch <bundle-id> --output profile.trace`. For CI use, see [qa-testing-ios](../../qa-testing-ios/SKILL.md).
- **In the field:** subscribe to `MXMetricManager` (MetricKit) once at launch and forward payloads to your telemetry backend. Payloads are aggregated and arrive with a delay, not in real time. Use them for launch time, hang rate, memory peaks and diagnostics across real devices.
- Do not ship a repeating timer that polls `task_info` or pushes CPU/memory numbers into `@Published` state. That costs energy and view invalidations, and it measures only the one device.
