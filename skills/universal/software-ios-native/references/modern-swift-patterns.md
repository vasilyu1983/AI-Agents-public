# Modern Swift Patterns

Modern Swift idioms and Foundation API usage for iOS 17+ / Swift 6.2. Covers language features, Foundation modernization, and coding style.

Primary docs:

- https://docs.swift.org/swift-book/documentation/the-swift-programming-language/
- https://developer.apple.com/documentation/foundation

## Table of Contents

- [Foundation Modernization](#foundation-modernization)
- [String and Text](#string-and-text)
- [Date and Time](#date-and-time)
- [Numbers and Formatting](#numbers-and-formatting)
- [Collections](#collections)
- [Control Flow](#control-flow)
- [Type Design](#type-design)
- [Error Handling](#error-handling)
- [Import Hygiene](#import-hygiene)

## Foundation Modernization

| Old | Modern | Notes |
|---|---|---|
| `FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!` | `URL.documentsDirectory` | Static property, no force unwrap |
| `url.appendingPathComponent("file.txt")` | `url.appending(path: "file.txt")` | Simpler API |
| `NSTemporaryDirectory()` | `URL.temporaryDirectory` | Static property |
| `Bundle.main.url(forResource:withExtension:)` | `Bundle.main.url(forResource:withExtension:)` | Unchanged, but prefer `URL.documentsDirectory` pattern for app data |
| `JSONSerialization` | `JSONDecoder` / `JSONEncoder` | Type-safe Codable |
| `NSAttributedString` for simple formatting | `AttributedString` | Swift-native, works with SwiftUI `Text` |

## String and Text

| Old | Modern | Notes |
|---|---|---|
| `str.contains(searchText)` (for user input) | `str.localizedStandardContains(searchText)` | Case-insensitive, diacritic-insensitive, locale-aware |
| Manual first/last name parsing | `PersonNameComponents` | Locale-aware name formatting |
| `String(format: "%.2f", value)` | `value.formatted(.number.precision(.fractionLength(2)))` | Locale-aware formatting |
| C-style number formatting | Swift format styles | Type-safe, localizable |
| Manual string interpolation for plural | Automatic grammar agreement API | Localizable strings adapt to count |

```swift
// User-facing search: always use localizedStandardContains
let filtered = items.filter { $0.name.localizedStandardContains(searchText) }

// Name formatting
var name = PersonNameComponents()
name.givenName = "John"
name.familyName = "Doe"
let formatted = name.formatted(.name(style: .long))  // Locale-aware
```

## Date and Time

| Old | Modern | Notes |
|---|---|---|
| `Date()` | `Date.now` | Clearer intent |
| `ISO8601DateFormatter().date(from: str)` | `try Date(str, strategy: .iso8601)` | Throwing, no optional to unwrap |
| `DateFormatter` with `"yyyy-MM-dd"` | `Date.FormatStyle` or `.formatted(date:time:)` | Locale-safe |
| `"yyyy"` for display years | `"y"` | Four-digit year is already the default |
| `Calendar.current.dateComponents([.year], from: date).year!` | `date.formatted(.dateTime.year())` | For display |

```swift
// Parse ISO 8601
let date = try Date("2026-04-12T10:30:00Z", strategy: .iso8601)

// Format for display
let display = date.formatted(date: .abbreviated, time: .shortened)

// Relative dates
let relative = date.formatted(.relative(presentation: .named))
```

## Numbers and Formatting

```swift
// Currency
let price = 29.99
Text(price, format: .currency(code: "USD"))

// Percentage
let ratio = 0.85
Text(ratio, format: .percent)

// Measurement
let distance = Measurement(value: 5.2, unit: UnitLength.kilometers)
Text(distance, format: .measurement(width: .abbreviated))
```

## Collections

| Old | Modern | Notes |
|---|---|---|
| `array.filter { condition }.count` | `array.count(where: { condition })` | Single pass, no intermediate array |
| Repeated sort comparisons | `Comparable` conformance on type | Define `<` once, use `.sorted()` everywhere |
| `Dictionary(uniqueKeysWithValues:)` for grouping | `Dictionary(grouping:by:)` | Built-in grouping |

```swift
// Count without intermediate array
let activeCount = users.count(where: { $0.isActive })

// Comparable conformance for repeated sorting
struct Transaction: Comparable {
    let date: Date
    let amount: Double

    static func < (lhs: Transaction, rhs: Transaction) -> Bool {
        lhs.date < rhs.date
    }
}
// Now: transactions.sorted() works everywhere
```

## Control Flow

### Optional binding shorthand

```swift
// Old
if let value = value { use(value) }

// Modern (Swift 5.7+)
if let value { use(value) }
```

### if/switch as expressions

```swift
// Old
let label: String
if isActive {
    label = "Active"
} else {
    label = "Inactive"
}

// Modern (Swift 5.9+)
let label = if isActive { "Active" } else { "Inactive" }

let icon = switch tier {
    case .free: "star"
    case .pro: "star.fill"
    case .enterprise: "crown"
}
```

### Implicit return

Omit `return` for single-expression functions and computed properties:

```swift
var isValid: Bool { !name.isEmpty && email.contains("@") }

func greeting(for name: String) -> String { "Hello, \(name)" }
```

### Static member lookup

```swift
// Old
let style = ShapeStyle.red

// Modern — inferred context
.foregroundStyle(.red)
.clipShape(.rect(cornerRadius: 12))
```

## Type Design

### Prefer Double over CGFloat

In Swift, `Double` and `CGFloat` are interchangeable. Prefer `Double` for new code — `CGFloat` is a legacy alias.

### Prefer enums for namespacing

```swift
// Namespace constants without instantiation
enum Layout {
    static let padding: CGFloat = 16
    static let cornerRadius: CGFloat = 12
}
```

### Avoid force unwraps

Force unwraps crash at runtime. Prefer:

- `guard let` / `if let` for optionals
- `try #require()` in tests
- `preconditionFailure()` when a nil value indicates a programmer error (with an explanatory message)

## Error Handling

### Make impossible states unrepresentable

Use exhaustive enums with associated values instead of optional fields or stringly-typed states:

```swift
// WRONG — impossible states are representable
struct Payment {
    var status: String  // "pending", "completed", "failed" — what else?
    var error: String?  // Non-nil when status is "failed"... maybe?
    var receiptURL: URL?  // Non-nil when "completed"... hopefully?
}

// CORRECT — impossible states are unrepresentable
enum PaymentStatus {
    case pending
    case completed(receiptURL: URL)
    case failed(reason: PaymentError, recovery: String)
}
```

### Error design with recovery paths

Provide actionable recovery suggestions in domain errors:

```swift
enum SyncError: LocalizedError {
    case networkUnavailable
    case conflict(local: Date, remote: Date)
    case quotaExceeded(current: Int, limit: Int)

    var errorDescription: String? {
        switch self {
        case .networkUnavailable: "Unable to sync — no network connection"
        case .conflict: "Your local changes conflict with the server"
        case .quotaExceeded(let cur, let lim): "Storage full (\(cur)/\(lim) items)"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .networkUnavailable: "Check your connection and try again"
        case .conflict: "Choose which version to keep"
        case .quotaExceeded: "Delete old items or upgrade your plan"
        }
    }
}
```

### Flag silently swallowed errors

```swift
// DANGEROUS — error silently discarded
try? riskyOperation()

// BETTER — at minimum, log the error
do {
    try riskyOperation()
} catch {
    logger.warning("Operation failed: \(error)")
}
```

When reviewing code, flag every `try?` that discards an error without logging or handling it. Silent failure is the most common source of "it just doesn't work" bugs.

### Typed throws (Swift 6.0+)

```swift
func fetch() throws(NetworkError) -> Data {
    // Can only throw NetworkError
}
```

## Import Hygiene

| Rule | Notes |
|---|---|
| `import SwiftUI` includes Foundation and UIKit/AppKit symbols | No extra `import UIKit` or `import AppKit` needed |
| `import Combine` is needed for `ObservableObject` | Even with `import SwiftUI`, Combine types need explicit import |
| Prefer `import SwiftUI` over `import UIKit` in SwiftUI files | UIKit import is only needed for UIKit-specific types |
| `@testable import` only in test targets | Never in production code |
