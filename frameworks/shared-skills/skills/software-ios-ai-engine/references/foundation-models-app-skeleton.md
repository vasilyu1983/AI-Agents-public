# Foundation Models App Skeleton

Use this reference when a native iOS app foundation should be AI-ready as of July 2026 without making cloud LLMs or Foundation Models mandatory for every device.

## Table of Contents

- [Default Architecture](#default-architecture)
- [Contracts](#contracts)
- [Foundation Models Gate](#foundation-models-gate)
- [App Intents and Tools](#app-intents-and-tools)
- [Fallbacks](#fallbacks)
- [Proof Gates](#proof-gates)

## Default Architecture

```text
AI/
  AIContracts.swift
  LocalAIEngine.swift
  FoundationModelsService.swift
  DeterministicAIEngine.swift
  LocalRetrievalIndex.swift
  AITrace.swift
```

`LocalAIEngine` is the stable app-facing interface. Foundation Models is one implementation, not the interface itself.

```swift
protocol LocalAIEngine {
    associatedtype Input
    associatedtype Output

    func run(_ input: Input) async throws -> Output
}
```

Use typed Swift output for every AI path. Raw model prose is an implementation detail and must not be parsed by views.

## Contracts

Common generic contracts:

- summarize local content
- extract structured fields
- classify or tag a record
- rewrite user-authored text
- answer from local evidence
- generate follow-up suggestions
- choose a next action from a bounded enum

Foundation Models paths should prefer `@Generable` structs for output when the model emits the type directly. Deterministic paths should emit the same type.

## Foundation Models Gate

Gate by runtime model availability, not by OS version or a guessed device list.

Required handling:

- available -> Foundation Models path may run
- unavailable -> deterministic local fallback
- model not ready/downloading -> deterministic fallback for this turn, retry later
- unsupported locale -> deterministic fallback or locale-specific non-AI path
- validation failure -> discard model output and fallback

Keep prompts short. Tool definitions, schemas, tool outputs, instructions, transcript, and expected response all consume context.

## App Intents and Tools

App Intents expose stable app actions and entities to Siri, Spotlight, widgets, controls, Shortcuts, and Apple Intelligence. Foundation Models tools expose app code/data to an on-device model session.

Do not conflate them:

| Surface | Purpose |
|---|---|
| App Intent | System-discoverable action or entity |
| Foundation Models Tool | Runtime callable function inside a model session |
| Local service | Deterministic app capability both surfaces may call |

Put real side effects in local services, then wrap them with App Intents or Foundation Models tools as needed.

## Fallbacks

Every Foundation Models feature needs a non-FM path:

| Feature | Fallback |
|---|---|
| summarization | extractive summary or title/metadata digest |
| classification | enum rules, Natural Language classifier, or keyword map |
| semantic search | lexical search or deterministic filters |
| answer composition | sentence bank or retrieval stitch |
| rewrite | conservative template or no-op with explanation |

## Proof Gates

1. Unit-test deterministic fallback without simulator.
2. Physical-device smoke for Foundation Models before claiming support.
3. Validate typed output, enum membership, word limits, locale, and forbidden fields.
4. Trace engine used, availability result, latency, fallback reason, and validation status.
5. Run at least one unsupported-device or model-unavailable test path.
