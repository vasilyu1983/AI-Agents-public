# Foundation Models Service Template

Use this shape to keep Foundation Models optional and typed.

```swift
import Foundation

enum LocalAIAvailability {
    case available
    case unavailable(reason: String)
    case notReady
}

struct AITrace: Sendable {
    var engine: String
    var availability: LocalAIAvailability
    var fallbackReason: String?
    var latencyMs: Int?
}

protocol AppAIService<Input, Output> {
    associatedtype Input: Sendable
    associatedtype Output: Sendable

    func run(_ input: Input) async throws -> (Output, AITrace)
}

@MainActor
final class AppLocalAIEngine<Input: Sendable, Output: Sendable> {
    private let foundationModels: any AppAIService<Input, Output>
    private let fallback: any AppAIService<Input, Output>

    init(
        foundationModels: any AppAIService<Input, Output>,
        fallback: any AppAIService<Input, Output>
    ) {
        self.foundationModels = foundationModels
        self.fallback = fallback
    }

    func run(_ input: Input) async throws -> (Output, AITrace) {
        // Real implementation gates on SystemLanguageModel.default.availability.
        // On unavailable/not-ready/validation failure, call fallback.
        try await fallback.run(input)
    }
}
```

Replace comments with current Foundation Models API calls in the app project. Keep the fallback path compiled and tested even when Foundation Models is enabled.
