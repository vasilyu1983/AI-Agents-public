# Local AI Task Patterns

## Table of Contents

- [Decision Matrix](#decision-matrix)
- [Patterns](#patterns)
- [Anti-Patterns](#anti-patterns)
- [Known Traps](#known-traps)
- [Scenarios](#scenarios)
- [Verification](#verification)

Use this reference when the local iOS AI work is **not primarily a chat answer**. These patterns cover local classification, extraction, summarization, tagging, rewrite helpers, semantic search, and tool-backed actions. Default to the smallest local engine that can satisfy the product contract; Apple Foundation Models are powerful, but not the default for every local AI task.

## Decision Matrix

| Task | Prefer | Use Foundation Models when | Avoid FM when |
|---|---|---|---|
| Intent routing | Regex / rules, then NaturalLanguage embeddings | Labels are fuzzy and examples are enough to define a small enum | High precision safety routing is required |
| Entity extraction | Deterministic parser, `NLTagger`, typed `@Generable` | Fields are natural-language, variable, and low-risk | Missing/extra fields create irreversible side effects |
| Summarization | Foundation Models for short local text; chunked pipeline for long text | Source fits the context window and hallucination is tolerable behind validation | Source exceeds token budget or needs legal/medical fidelity |
| Tagging/categorization | Rules, embeddings, or FM enum output | Categories need semantic nuance but are bounded | Tags drive billing, compliance, or access control |
| Rewrite/proofread | Foundation Models or system Writing Tools surface | User-authored text is the source of truth and output is editable | Product needs exact approved copy |
| Local semantic search | NaturalLanguage/Core ML embeddings + local index | FM is used only to generate query expansions or a final short explanation | Retrieval is sparse and model would invent missing facts |
| Tool-backed action | App code executes the action; model only proposes typed intent | Tool choice is optional and read-only until user confirms | Model output would directly mutate state or spend money |
| Custom domain model | Core ML | You own model weights and task is narrow/stable | A general language task can be solved by FM + typed output |

## Patterns

### P1 · Task-before-model selection

Name the local task before choosing the engine: `route`, `extract`, `summarize`, `tag`, `rewrite`, `search`, `compose`, or `proposeAction`. If the team cannot name the task, it is not ready for model work. Most production bugs start with "add AI here" instead of "extract these 5 fields into this struct."

### P2 · Typed contract at the boundary

Every local AI path returns a Swift type the caller can validate:

```swift
@Generable
struct ExpenseFields: Codable, Sendable {
    let merchant: String?
    let amount: Decimal?
    let currencyCode: String?
    let purchasedAt: Date?
    let category: ExpenseCategory
}
```

The UI never parses prose. If the task is classification, return an enum. If it is extraction, return a struct with nullable fields and confidence. If it is summarization, return `{ summary, sourceRefs, omittedSections }`.

### P3 · Deterministic-first safety routes

Safety, access control, spending, destructive actions, and crisis boundaries use deterministic routing first. FM can enrich the explanation after the boundary is decided, but it does not own the boundary.

### P4 · Two-pass extraction

For messy user input or OCR:

1. Normalize locally: trim, de-duplicate, detect locale/script, fix obvious OCR whitespace.
2. Extract with the smallest engine: parser/rules first, FM `@Generable` only for fields rules cannot handle.
3. Validate fields independently: date range, currency, enum membership, source span, confidence.

If validation fails, ask a user-visible clarification or leave a field blank; do not ask the model to "try harder" until it fabricates a value.

### P5 · Summarize by chunks, then merge

For content near or above the on-device context window, split first. Summarize chunks in separate sessions, merge summaries in a new session, and preserve source refs. Do not keep appending messages to one long `LanguageModelSession` until `.exceededContextWindowSize`.

### P6 · Bounded classification taxonomy

Foundation Models are strongest when selecting from a small fixed taxonomy. Keep labels mutually exclusive, human-readable, and stable. If you have more than 12-15 classes, add a hierarchy: coarse class first, subtype second.

### P7 · Embeddings before generation for search

For local semantic search, retrieve first using NaturalLanguage/Core ML embeddings or a small bundled embedding model. Use FM after retrieval only to explain, summarize, or re-rank a small candidate set. A language model is not a database.

### P8 · Rewrite helpers preserve user agency

For proofread/rewrite features, keep the original text visible and let the user accept, reject, or edit the suggestion. Do not auto-replace long user-authored content after a model call. Store the diff, not just the final text, if the user may need undo.

### P9 · Tool calls are proposals until confirmed

When a local model proposes an action (`createTask`, `scheduleReminder`, `sendMessage`, `purchase`, `delete`), app code validates the typed proposal and asks for confirmation before side effects. The model can propose; the app decides.

### P10 · Capability probe per feature, not per app

Check availability at the feature boundary. A device may support one local path and not another because of language, asset readiness, OS point release, or feature flag. Cache the result briefly, but allow it to refresh when the user re-enters the surface.

### P11 · Locale as an input, not decoration

Pass locale/script into classification, extraction, summarization, and validation. A classifier trained or prompted in English can silently mislabel Russian, Arabic, Japanese, or mixed-language text. For non-English locales, verify both the output language and the typed fields.

### P12 · Local telemetry without sensitive payloads

Emit task-level telemetry: `task`, `engine`, `availability`, `latencyMs`, `validationResult`, `fallbackReason`, `locale`, `inputSizeBand`. Do not log raw user text, OCR text, health notes, journal entries, or extracted secrets.

## Anti-Patterns

### A1 · FM for every local AI task

Using Foundation Models for simple yes/no routing, literal keyword detection, or fixed enum mapping adds latency, token pressure, and nondeterminism. Rules and `NaturalLanguage` are often better.

### A2 · Raw prose as API

The model returns "Looks like this is a grocery receipt from Tesco for £18.24" and downstream code regexes it. This fails across locales, wording changes, and retries. Return typed fields.

### A3 · Single giant assistant session

One long session handles routing, retrieval, extraction, summarization, answer prose, and action planning. This leaks context across tasks, blows the context window, and makes validation impossible. Split tasks into small sessions or deterministic stages.

### A4 · Model-owned permissions

"The model decided it was safe to send." This is never acceptable. Permissions, payments, deletion, posting, sharing, and messaging are app-owned policy decisions.

### A5 · Summaries without source refs

A local summary that cannot point back to source spans is hard to debug and easy to overtrust. Even if you do not render citations, store source refs in trace/eval artifacts.

### A6 · Tag drift as product personalization

The model invents new categories over time ("urgent-ish", "wellbeing admin") and the product treats that as personalization. If tags drive filters, notifications, or analytics, they must come from a bounded taxonomy.

### A7 · Unsupported locale hidden by fallback English

The device cannot produce reliable output in the user's language, so the app emits English anyway. This looks like a localization bug and breaks trust. Fall back to deterministic localized copy or cloud opt-in.

### A8 · Core ML model bundled without lifecycle

A custom model ships in the app bundle, but there is no model version, benchmark, migration path, or rollback. Treat Core ML assets like code: version, test, profile, and release-gate them.

### A9 · Local-only privacy claim with cloud fallback

Marketing says "runs entirely on device," but error paths silently call cloud. If cloud exists, label it as cloud opt-in or document the policy clearly.

### A10 · Simulator-only proof

The local AI path "works" in simulator but fails on a physical device because assets, Apple Intelligence settings, memory pressure, language availability, or Neural Engine behavior differ. Simulator proof is not release proof.

## Known Traps

### T1 · Context-window math ignores schemas and tools

Apple counts prompts, instructions, `@Generable` schemas, tool definitions, tool inputs/outputs, and responses in the session context. A short OCR prompt plus a large schema can still overflow. Budget the full request.

### T2 · `maximumResponseTokens` clips structured output

Strict caps can produce malformed prose or incomplete structured fields. Use smaller schemas, shorter prompts, fewer tools, and chunking before using a hard cap.

### T3 · Optional fields become invented fields

If every extraction field is optional, the model may fill blanks with plausible guesses. Include "unknown is acceptable" guidance and validate every field against source spans where possible.

### T4 · Dates and currencies parse differently by locale

`03/04/26`, `1.234,56`, and currency symbols are locale-sensitive. Use locale-aware parsers after extraction; do not trust the model's normalized value without checking.

### T5 · Classification confidence is not calibrated

Small on-device models may sound certain even when wrong. Treat confidence as a product heuristic unless calibrated against a labeled eval set. Use abstain/clarify states.

### T6 · Rewrite helpers remove legally meaningful text

Proofread/rewrite can delete qualifiers, dates, negations, dosage, amounts, or legal terms. For sensitive documents, show diffs and preserve original meaning checks.

### T7 · Local embeddings and FM disagree

Retrieval says chunk A is top; FM says chunk B seems more relevant. Do not let the generator override retrieval without traceable re-ranking. Store both scores and final choice.

### T8 · Asset readiness changes after install

Foundation Models or language assets may be unavailable, downloading, disabled, or unsupported on first launch. The first-run path must not be the only tested path.

### T9 · Background execution budget kills local AI

Long summarization or indexing jobs can be interrupted in background. Use resumable chunks, persist progress, and avoid assuming a long model session survives app lifecycle events.

### T10 · Thermal and battery pressure change UX

Local inference can become slower under thermal pressure or low battery. Put a latency ceiling on user-facing calls and fall back to deterministic local output or a queued job.

### T11 · Personal data leaks through telemetry

"Local" does not protect the user if traces upload raw prompts, extracted fields, source text, or summaries. Log bands and validation codes, not payloads.

### T12 · Core ML model size breaks app distribution

Bundled models increase app size and can affect download/install behavior. Consider lazy asset download, model compression, or server-side preparation for heavy models.

### T13 · NaturalLanguage language support assumed universal

Tokenization, tagging, and embeddings vary by language and OS version. Check support for the active language and keep rule-based fallbacks for unsupported locales.

### T14 · Tool-backed action loops hide side effects

A model calls a tool that reads app state, then another tool that writes app state, then the UI shows only the final answer. Keep read tools and write actions separate; require app-owned confirmation before writes.

### T15 · Eval set covers only happy-path English

Local AI fails in short, misspelled, multilingual, emoji-heavy, OCR-noisy, and adversarial inputs. Eval corpora need these cases before release.

## Scenarios

### S1 · Local intent router for an ASK screen

1. Start with regex/rules for high-confidence intents and safety boundaries.
2. Add NaturalLanguage or embedding nearest-neighbor only for ambiguous mid-confidence inputs.
3. Use FM enum classification only for long-tail phrasing, with a strict enum output.
4. Trace `route`, `confidenceBand`, `engine`, and `fallbackReason`.

### S2 · Extract fields from a receipt, note, or onboarding text

1. Normalize OCR/user text and detect locale.
2. Extract obvious fields deterministically.
3. Use FM `@Generable` for messy fields only.
4. Validate against source spans and locale-aware parsers.
5. Leave uncertain fields blank and ask a clarification instead of inventing.

### S3 · Summarize a long journal or document locally

1. Split source into chunks below the token budget.
2. Summarize each chunk in a separate session with `{ summary, sourceRange, omissions }`.
3. Merge chunk summaries in a final session.
4. Store source refs and run a factual-consistency spot check before rendering.

### S4 · Local tag suggestions for user content

1. Define a bounded taxonomy and "none/other" state.
2. Use embeddings/rules for common tags.
3. Use FM enum output for ambiguous content.
4. Require user confirmation before tags affect notifications, filters, or automations.

### S5 · Rewrite helper for user-authored text

1. Keep original text visible.
2. Ask for a specific operation: proofread, shorten, soften, formalize, translate, or summarize.
3. Render a diff or replacement preview.
4. Let the user accept/edit/reject; preserve undo.

### S6 · Local semantic search over app knowledge

1. Build a local index from versioned chunks.
2. Retrieve top-k with embeddings or lexical+embedding hybrid.
3. Use FM only to summarize the top 1-3 chunks or explain why they match.
4. If top-k score is low, ask a clarification or offer cloud search; do not hallucinate an answer.

### S7 · Tool-backed action proposal

1. Classify the requested action into a typed proposal.
2. Run read-only tools to fill missing context.
3. Validate permissions and side effects in app code.
4. Present a confirmation sheet for write/send/spend/delete actions.
5. Execute with deterministic app code, then summarize the result.

### S8 · Pre-iOS-26 or Apple-Intelligence-disabled users

1. Do not hide the feature behind a broken local model path.
2. Use deterministic local rules, NaturalLanguage, Core ML models, or sentence banks where possible.
3. Offer cloud opt-in only if product policy allows.
4. Telemetry should distinguish "local deterministic" from "Foundation Models unavailable."

### S9 · Custom Core ML model for a narrow task

1. Use Core ML when the task is stable, narrow, and model-owned by your team.
2. Version the model asset and benchmark it against target devices.
3. Profile memory, latency, power, and app size.
4. Keep a rules/cloud fallback for model load failure or unsupported hardware.

### S10 · Point-release regression in local AI behavior

1. Re-run the pinned eval set on the new iOS/Xcode version and at least one physical target device.
2. Compare validation failures by task: routing, extraction, summary consistency, rewrite meaning preservation.
3. If only FM regressed, disable FM path by remote config and keep deterministic fallback.
4. Add the repro to the eval corpus before re-enabling.

## Verification

- The local task is named and has a typed output contract.
- The chosen engine is the smallest reliable one for the task.
- Foundation Models availability is checked at the feature boundary.
- Prompt, schema, tools, and expected output fit the session context window.
- Every FM output is validated before reaching UI or app state.
- Sensitive actions require app-owned confirmation.
- Locales, scripts, dates, numbers, and currencies have explicit tests.
- Physical-device proof exists for the target OS/device band.
- Telemetry records engine, validation result, fallback reason, latency, and locale without raw sensitive payloads.
- Cloud fallback is explicit when privacy or quota copy promises local execution.
