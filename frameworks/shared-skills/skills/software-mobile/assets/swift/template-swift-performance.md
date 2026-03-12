# iOS App Template (Performance-Optimized)

Complete production-ready iOS application template focused on high-performance patterns, memory optimization, lazy loading, efficient rendering, and scalability for large datasets.

---

## Tech Stack

- **Language**: Swift 6.1+
- **UI Framework**: SwiftUI (optimized, Observation-first)
- **Architecture**: MVVM with Performance Focus
- **Concurrency**: Swift Concurrency (@MainActor optimization)
- **Persistence**: Core Data with NSFetchedResultsController (SwiftData optional)
- **Networking**: URLSession with request pooling
- **Caching**: NSCache + Disk Cache
- **Image Loading**: SDWebImage / Kingfisher
- **Profiling**: Instruments, Memory Graph Debugger
- **Monitoring**: MetricKit
- **Testing**: Swift Testing (preferred) + XCTest (UI/legacy)

---

## Project Structure

```
YourApp/
├── YourApp/
│   ├── App/
│   │   ├── YourAppApp.swift
│   │   └── PerformanceMonitor.swift
│   ├── Models/
│   │   ├── User.swift
│   │   └── Post.swift
│   ├── ViewModels/
│   │   ├── FeedViewModel.swift
│   │   └── ImageCacheViewModel.swift
│   ├── Views/
│   │   ├── Optimized/
│   │   │   ├── LazyLoadingListView.swift
│   │   │   ├── VirtualizedGridView.swift
│   │   │   └── CachedImageView.swift
│   │   └── Feed/
│   │       └── FeedView.swift
│   ├── Services/
│   │   ├── CacheService.swift
│   │   ├── ImageCache.swift
│   │   └── RequestPool.swift
│   ├── Utilities/
│   │   ├── MemoryMonitor.swift
│   │   ├── PerformanceMetrics.swift
│   │   └── LazyLoader.swift
│   └── Resources/
└── YourAppTests/
    └── PerformanceTests/
```

---

## 1. Performance Monitoring

**YourApp/App/PerformanceMonitor.swift**

```swift
import Foundation
import MetricKit

@MainActor
class PerformanceMonitor: NSObject, ObservableObject, MXMetricManagerSubscriber {
    static let shared = PerformanceMonitor()

    @Published var cpuUsage: Double = 0
    @Published var memoryUsage: UInt64 = 0
    @Published var frameRate: Double = 60

    private override init() {
        super.init()
        MXMetricManager.shared.add(self)
        startMonitoring()
    }

    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            // CPU Metrics
            if let cpuMetrics = payload.cpuMetrics {
                let cumulativeCPU = cpuMetrics.cumulativeCPUTime.value(for: .seconds)
                print("CPU Time: \(cumulativeCPU)s")
            }

            // Memory Metrics
            if let memoryMetrics = payload.memoryMetrics {
                let peakMemory = memoryMetrics.peakMemoryUsage.value(for: .megabytes)
                print("Peak Memory: \(peakMemory)MB")
            }

            // Hang Time
            if let hangMetrics = payload.applicationResponsivenessMetrics {
                print("Hang Time: \(hangMetrics.histogrammedApplicationHangTime)")
            }
        }
    }

    private func startMonitoring() {
        Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.updateMetrics()
            }
        }
    }

    private func updateMetrics() {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4

        let result: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }

        if result == KERN_SUCCESS {
            memoryUsage = info.resident_size
        }
    }
}
```

**YourApp/Utilities/MemoryMonitor.swift**

```swift
import Foundation

class MemoryMonitor {
    static let shared = MemoryMonitor()

    private init() {
        // Register for memory warnings
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleMemoryWarning),
            name: UIApplication.didReceiveMemoryWarningNotification,
            object: nil
        )
    }

    @objc private func handleMemoryWarning() {
        print("Memory warning received")

        // Clear caches
        URLCache.shared.removeAllCachedResponses()
        ImageCache.shared.clearMemoryCache()

        // Force garbage collection
        autoreleasepool {
            // Heavy objects released here
        }
    }

    func currentMemoryUsage() -> UInt64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4

        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }

        return kerr == KERN_SUCCESS ? info.resident_size : 0
    }
}
```

---

## 2. Optimized Image Caching

**YourApp/Services/ImageCache.swift**

```swift
import UIKit
import Combine

actor ImageCache {
    static let shared = ImageCache()

    private let memoryCache = NSCache<NSString, UIImage>()
    private let fileManager = FileManager.default
    private let cacheDirectory: URL

    private init() {
        // Configure memory cache
        memoryCache.totalCostLimit = 100 * 1024 * 1024 // 100 MB
        memoryCache.countLimit = 100

        // Disk cache directory
        let paths = fileManager.urls(for: .cachesDirectory, in: .userDomainMask)
        cacheDirectory = paths[0].appendingPathComponent("ImageCache")

        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)

        // Clear old cache on init
        Task {
            await clearOldCacheFiles()
        }
    }

    // MARK: - Memory Cache

    func getImageFromMemory(forKey key: String) -> UIImage? {
        memoryCache.object(forKey: key as NSString)
    }

    func setImageInMemory(_ image: UIImage, forKey key: String) {
        let cost = image.size.width * image.size.height * 4 // Rough size estimate
        memoryCache.setObject(image, forKey: key as NSString, cost: Int(cost))
    }

    func clearMemoryCache() {
        memoryCache.removeAllObjects()
    }

    // MARK: - Disk Cache

    func getImageFromDisk(forKey key: String) async -> UIImage? {
        let fileURL = cacheDirectory.appendingPathComponent(key.md5)

        guard fileManager.fileExists(atPath: fileURL.path),
              let data = try? Data(contentsOf: fileURL),
              let image = UIImage(data: data) else {
            return nil
        }

        // Store in memory for faster access
        setImageInMemory(image, forKey: key)
        return image
    }

    func setImageOnDisk(_ image: UIImage, forKey key: String) async {
        guard let data = image.jpegData(compressionQuality: 0.8) else { return }

        let fileURL = cacheDirectory.appendingPathComponent(key.md5)

        try? data.write(to: fileURL)
    }

    // MARK: - Combined Get

    func getImage(forKey key: String) async -> UIImage? {
        // 1. Check memory cache (fast)
        if let memoryImage = getImageFromMemory(forKey: key) {
            return memoryImage
        }

        // 2. Check disk cache (slower)
        if let diskImage = await getImageFromDisk(forKey: key) {
            return diskImage
        }

        return nil
    }

    func setImage(_ image: UIImage, forKey key: String) async {
        setImageInMemory(image, forKey: key)
        await setImageOnDisk(image, forKey: key)
    }

    // MARK: - Cleanup

    private func clearOldCacheFiles() async {
        let maxAge: TimeInterval = 7 * 24 * 60 * 60 // 7 days

        guard let files = try? fileManager.contentsOfDirectory(
            at: cacheDirectory,
            includingPropertiesForKeys: [.contentModificationDateKey],
            options: .skipsHiddenFiles
        ) else { return }

        for file in files {
            guard let attributes = try? fileManager.attributesOfItem(atPath: file.path),
                  let modificationDate = attributes[.modificationDate] as? Date else {
                continue
            }

            if Date().timeIntervalSince(modificationDate) > maxAge {
                try? fileManager.removeItem(at: file)
            }
        }
    }
}

extension String {
    var md5: String {
        // Simple hash for filename (use CryptoKit in production)
        return String(self.hashValue)
    }
}
```

**YourApp/Views/Optimized/CachedImageView.swift**

```swift
import SwiftUI

struct CachedImageView: View {
    let url: URL
    let placeholder: Image?

    @State private var image: UIImage?
    @State private var isLoading = false

    init(url: URL, placeholder: Image? = Image(systemName: "photo")) {
        self.url = url
        self.placeholder = placeholder
    }

    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
            } else if isLoading {
                placeholder?
                    .resizable()
                    .overlay(ProgressView())
            } else {
                placeholder?
                    .resizable()
            }
        }
        .task {
            await loadImage()
        }
    }

    @MainActor
    private func loadImage() async {
        isLoading = true

        // Check cache first
        if let cachedImage = await ImageCache.shared.getImage(forKey: url.absoluteString) {
            image = cachedImage
            isLoading = false
            return
        }

        // Download image
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            if let downloadedImage = UIImage(data: data) {
                // Cache it
                await ImageCache.shared.setImage(downloadedImage, forKey: url.absoluteString)
                image = downloadedImage
            }
        } catch {
            print("Failed to load image: \(error)")
        }

        isLoading = false
    }
}
```

---

## 3. Lazy Loading List with Pagination

**YourApp/Views/Optimized/LazyLoadingListView.swift**

```swift
import SwiftUI

struct LazyLoadingListView: View {
    @StateObject private var viewModel = FeedViewModel()

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(viewModel.posts.indices, id: \.self) { index in
                    PostRowView(post: viewModel.posts[index])
                        .onAppear {
                            // Trigger pagination when near end
                            if index == viewModel.posts.count - 5 {
                                Task {
                                    await viewModel.loadMoreIfNeeded()
                                }
                            }
                        }
                }

                if viewModel.isLoadingMore {
                    ProgressView()
                        .padding()
                }
            }
            .padding()
        }
        .task {
            await viewModel.initialLoad()
        }
    }
}

struct PostRowView: View {
    let post: Post

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                CachedImageView(url: post.author.avatarURL ?? URL(string: "https://via.placeholder.com/50")!)
                    .frame(width: 40, height: 40)
                    .clipShape(Circle())

                Text(post.author.name)
                    .font(.headline)

                Spacer()

                Text(post.createdAt, style: .relative)
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            Text(post.title)
                .font(.subheadline)
                .fontWeight(.semibold)

            Text(post.content)
                .font(.body)
                .lineLimit(3)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
    }
}
```

**YourApp/ViewModels/FeedViewModel.swift**

```swift
import Foundation

@MainActor
class FeedViewModel: ObservableObject {
    @Published var posts: [Post] = []
    @Published var isLoadingMore = false

    private var currentPage = 0
    private let pageSize = 20
    private var canLoadMore = true

    func initialLoad() async {
        posts = []
        currentPage = 0
        canLoadMore = true
        await loadMoreIfNeeded()
    }

    func loadMoreIfNeeded() async {
        guard !isLoadingMore && canLoadMore else { return }

        isLoadingMore = true

        do {
            // Simulate API call with pagination
            let newPosts = try await fetchPosts(page: currentPage, pageSize: pageSize)

            if newPosts.count < pageSize {
                canLoadMore = false
            }

            posts.append(contentsOf: newPosts)
            currentPage += 1
        } catch {
            print("Failed to load posts: \(error)")
        }

        isLoadingMore = false
    }

    private func fetchPosts(page: Int, pageSize: Int) async throws -> [Post] {
        // Implement actual API call
        // For demo, simulate delay
        try await Task.sleep(nanoseconds: 500_000_000) // 0.5s

        return (0..<pageSize).map { index in
            Post(
                id: "\(page * pageSize + index)",
                title: "Post \(page * pageSize + index)",
                content: "Lorem ipsum dolor sit amet...",
                author: User(
                    id: "\(index)",
                    email: "user\(index)@example.com",
                    name: "User \(index)",
                    avatarURL: nil,
                    createdAt: Date()
                ),
                isStarred: false,
                createdAt: Date()
            )
        }
    }
}
```

---

## 4. Virtualized Grid View

**YourApp/Views/Optimized/VirtualizedGridView.swift**

```swift
import SwiftUI

struct VirtualizedGridView: View {
    let items: [String]
    let columns: Int

    @State private var visibleRange: Range<Int> = 0..<20

    private let itemHeight: CGFloat = 200

    var body: some View {
        GeometryReader { geometry in
            let columnWidth = (geometry.size.width - CGFloat(columns - 1) * 8) / CGFloat(columns)

            ScrollView {
                LazyVGrid(
                    columns: Array(repeating: GridItem(.fixed(columnWidth), spacing: 8), count: columns),
                    spacing: 8
                ) {
                    ForEach(visibleRange, id: \.self) { index in
                        if index < items.count {
                            GridItemView(item: items[index])
                                .frame(height: itemHeight)
                                .onAppear {
                                    updateVisibleRange(for: index)
                                }
                        }
                    }
                }
                .padding(8)
            }
        }
    }

    private func updateVisibleRange(for index: Int) {
        let buffer = 10

        let newStart = max(0, index - buffer)
        let newEnd = min(items.count, index + buffer + columns * 5)

        if newStart != visibleRange.lowerBound || newEnd != visibleRange.upperBound {
            visibleRange = newStart..<newEnd
        }
    }
}

struct GridItemView: View {
    let item: String

    var body: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(Color.blue.opacity(0.3))
            .overlay(
                Text(item)
                    .font(.headline)
            )
    }
}
```

---

## 5. @MainActor Optimization

**YourApp/ViewModels/OptimizedViewModel.swift**

```swift
import Foundation

@MainActor
class OptimizedViewModel: ObservableObject {
    @Published var data: [Item] = []
    @Published var isLoading = false

    // Heavy computation offloaded to background
    func processData() async {
        isLoading = true

        // Perform heavy work off main thread
        let processed = await Task.detached(priority: .userInitiated) {
            // Expensive computation here
            return self.performExpensiveCalculation()
        }.value

        // Update UI on main thread
        data = processed
        isLoading = false
    }

    nonisolated private func performExpensiveCalculation() -> [Item] {
        // CPU-intensive work that doesn't touch @Published properties
        var result: [Item] = []

        for i in 0..<10000 {
            result.append(Item(id: "\(i)", value: i * 2))
        }

        return result
    }
}

struct Item: Identifiable {
    let id: String
    let value: Int
}
```

---

## 6. Request Pooling & Throttling

**YourApp/Services/RequestPool.swift**

```swift
import Foundation

actor RequestPool {
    static let shared = RequestPool()

    private var activeRequests: [URL: Task<Data, Error>] = [:]
    private let maxConcurrentRequests = 5
    private var requestQueue: [(URL, CheckedContinuation<Data, Error>)] = []
    private var activeCount = 0

    func fetch(from url: URL) async throws -> Data {
        // Deduplicate: If same URL is already being fetched, wait for it
        if let existingTask = activeRequests[url] {
            return try await existingTask.value
        }

        // Create new task
        let task = Task<Data, Error> {
            try await performFetch(from: url)
        }

        activeRequests[url] = task

        defer {
            activeRequests[url] = nil
        }

        return try await task.value
    }

    private func performFetch(from url: URL) async throws -> Data {
        // Throttle concurrent requests
        if activeCount >= maxConcurrentRequests {
            return try await withCheckedThrowingContinuation { continuation in
                requestQueue.append((url, continuation))
            }
        }

        activeCount += 1

        defer {
            activeCount -= 1
            processQueue()
        }

        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }

    private func processQueue() {
        guard !requestQueue.isEmpty, activeCount < maxConcurrentRequests else { return }

        let (url, continuation) = requestQueue.removeFirst()

        Task {
            do {
                let (data, _) = try await URLSession.shared.data(from: url)
                continuation.resume(returning: data)
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }
}
```

---

## 7. Performance Testing

**Swift Testing (preferred)**
```swift
import Testing
@testable import YourApp

@Suite struct PerformanceSuite {
    @Test(arguments: [10_000, 50_000])
    func feedPaginationPerformance(count: Int) async throws {
        let service = MockFeedService(totalItems: count)
        let viewModel = FeedViewModel(feedService: service)
        let metrics = await PerformanceMetrics.measure {
            await viewModel.loadNextPage()
        }
        #expect(metrics.duration < 0.2)
    }
}
```

**YourAppTests/PerformanceTests/PerformanceTests.swift**

```swift
import XCTest
@testable import YourApp

final class PerformanceTests: XCTestCase {
    func testImageCachePerformance() {
        measure {
            let cache = NSCache<NSString, UIImage>()

            for i in 0..<1000 {
                let image = UIImage(systemName: "star")!
                cache.setObject(image, forKey: "image_\(i)" as NSString)
            }

            for i in 0..<1000 {
                _ = cache.object(forKey: "image_\(i)" as NSString)
            }
        }
    }

    func testLargeListRenderingPerformance() {
        measure {
            let items = (0..<10000).map { Item(id: "\($0)", value: $0) }

            // Simulate processing
            let filtered = items.filter { $0.value % 2 == 0 }
            XCTAssertFalse(filtered.isEmpty)
        }
    }

    func testConcurrentNetworkRequests() async {
        let options = XCTMeasureOptions()
        options.iterationCount = 5

        measure(options: options) {
            let expectation = XCTestExpectation(description: "Concurrent requests")

            Task {
                await withTaskGroup(of: Void.self) { group in
                    for _ in 0..<50 {
                        group.addTask {
                            _ = try? await RequestPool.shared.fetch(
                                from: URL(string: "https://jsonplaceholder.typicode.com/posts/1")!
                            )
                        }
                    }
                }

                expectation.fulfill()
            }

            wait(for: [expectation], timeout: 10.0)
        }
    }
}
```

---

## 8. Instruments Profiling

**Common Instruments Templates:**

1. **Time Profiler**
   - Identify CPU hotspots
   - Optimize expensive functions

2. **Allocations**
   - Track memory allocations
   - Find memory leaks

3. **Leaks**
   - Detect retain cycles
   - Identify leaked objects

4. **Core Animation**
   - Measure frame rate
   - Identify rendering issues

**Command Line Profiling:**

```bash
# Record instruments trace
xcrun xctrace record \
  --template 'Time Profiler' \
  --device 'iPhone 16' \
  --launch 'com.yourcompany.YourApp' \
  --output profile.trace

# View trace
open profile.trace
```

---

## 9. Performance Best Practices

1. **Lazy Loading**
   - Use LazyVStack/LazyHStack
   - Load images on demand
   - Implement pagination

2. **Caching**
   - Cache network responses
   - Cache computed values
   - Use NSCache for memory management

3. **@MainActor Usage**
   - Mark ViewModels with @MainActor
   - Offload heavy work to background
   - Use nonisolated for pure functions

4. **Image Optimization**
   - Resize images to display size
   - Use appropriate compression
   - Implement disk + memory cache

5. **List Performance**
   - Use identifiable items
   - Avoid expensive computations in body
   - Implement virtualization for large lists

6. **Network Optimization**
   - Pool concurrent requests
   - Implement request deduplication
   - Use HTTP/2 multiplexing

---

This template provides comprehensive performance optimization patterns for building fast, scalable iOS applications that handle large datasets and complex UIs efficiently.
