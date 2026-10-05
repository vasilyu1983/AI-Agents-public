# Local Retrieval Tool Template

Use this shape for local semantic search and Foundation Models tool calls.

```swift
import Foundation

struct RetrievalQuery: Sendable {
    var text: String
    var localeIdentifier: String
    var limit: Int
    var scope: String
}

struct RetrievalResult: Identifiable, Sendable {
    var id: String
    var title: String?
    var content: String
    var sourceURI: String
    var contentHash: String
    var corpusVersion: String
    var score: Double
}

protocol LocalRetrievalIndex: Sendable {
    func search(_ query: RetrievalQuery) async throws -> [RetrievalResult]
}

struct LocalRetrievalTool {
    let index: any LocalRetrievalIndex

    func call(query: String, localeIdentifier: String, scope: String) async throws -> [RetrievalResult] {
        try await index.search(
            RetrievalQuery(
                text: query,
                localeIdentifier: localeIdentifier,
                limit: 5,
                scope: scope
            )
        )
    }
}
```

For Foundation Models, expose compact results. Do not pass a whole local corpus into the prompt.
