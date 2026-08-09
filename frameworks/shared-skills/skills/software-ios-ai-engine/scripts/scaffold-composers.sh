#!/usr/bin/env bash
set -euo pipefail

# scaffold-composers.sh
#
# Drops a minimal Swift file layout into an iOS app for the three-tier grounded
# answer architecture described in ../SKILL.md. Idempotent: skips files that
# already exist. Produces the shared contract + protocol + empty composer stubs
# so the team can implement each Tier 1 option independently behind one API.
#
# Usage:
#   ./scripts/scaffold-composers.sh <target-swift-source-root>
#
# Example:
#   ./scripts/scaffold-composers.sh App/Features/Ask/Composers
#
# After running, wire the chain in your DI container and the screen's store.
# Do not commit these stubs without implementing them — empty composers fall
# through to the safety copy.

TARGET_DIR="${1:-}"
if [[ -z "${TARGET_DIR}" ]]; then
  echo "usage: $0 <target-swift-source-root>" >&2
  exit 2
fi

mkdir -p "${TARGET_DIR}"

write_if_absent() {
  local path="$1"
  local content="$2"
  if [[ -e "${path}" ]]; then
    echo "skip (exists): ${path}"
    return 0
  fi
  printf '%s\n' "${content}" > "${path}"
  echo "wrote: ${path}"
}

# --- Shared contract ----------------------------------------------------------
write_if_absent "${TARGET_DIR}/GroundedAnswer.swift" 'import Foundation

/// The single shape every composer emits. UI renders from this type; it must
/// not branch on `composerUsed` — use telemetry for that.
struct GroundedAnswer: Codable, Equatable, Sendable {
    let answer: String
    let grounding: String
    let followUp: String?
    let archetype: Archetype
    let composerUsed: ComposerID
    let confidence: Confidence
    let anchorsNamed: [AnchorRef]

    enum Confidence: String, Codable, Sendable { case high, medium, low }
}

enum Archetype: String, Codable, Sendable {
    case reflect, interpret, guide, clarify, checkIn = "check_in"
}

enum ComposerID: String, Codable, Sendable {
    case foundationModels = "foundation_models"
    case sentenceBank = "sentence_bank"
    case retrievalStitch = "retrieval_stitch"
    case safetyFallback = "safety_fallback"
}

struct AnchorRef: Codable, Equatable, Sendable {
    let kind: Kind
    let detail: String
    enum Kind: String, Codable, Sendable {
        case sunSign, moonSign, risingSign, transit, progressedMoon
        case personalDay, personalYear, lifePath
        case hdType, hdAuthority, hdProfile, hdDefinition
        case knowledgeChunk
    }
}
'

# --- Composer protocol --------------------------------------------------------
write_if_absent "${TARGET_DIR}/GroundedAnswerComposer.swift" 'import Foundation

/// Chain-of-responsibility composer. Returning nil means "decline this turn,
/// pass to the next composer in the chain" — NOT "emit a reject card."
/// Throws are for bugs; declines are normal.
protocol GroundedAnswerComposer: Sendable {
    var id: ComposerID { get }

    func compose(
        bundle: EvidenceBundle,
        tier0: Tier0Output,
        regenerate: Bool
    ) async throws -> GroundedAnswer?
}
'

# --- Composer chain -----------------------------------------------------------
write_if_absent "${TARGET_DIR}/ComposerChain.swift" 'import Foundation
import OSLog

actor ComposerChain {
    private let composers: [any GroundedAnswerComposer]
    private let validator: AnchorValidator
    private let safetyFallback: SafetyFallbackComposer
    private let log = Logger(subsystem: "local-ai-engine", category: "chain")

    init(
        composers: [any GroundedAnswerComposer],
        validator: AnchorValidator,
        safetyFallback: SafetyFallbackComposer
    ) {
        self.composers = composers
        self.validator = validator
        self.safetyFallback = safetyFallback
    }

    func compose(
        bundle: EvidenceBundle,
        tier0: Tier0Output,
        regenerate: Bool
    ) async -> GroundedAnswer {
        if tier0.safetyBoundary == .crisisRedirect {
            return safetyFallback.crisisResponse(locale: tier0.locale)
        }

        for composer in composers {
            do {
                guard let candidate = try await composer.compose(
                    bundle: bundle,
                    tier0: tier0,
                    regenerate: regenerate
                ) else { continue }

                switch validator.validate(candidate, bundle: bundle) {
                case .ok:
                    return candidate
                case .failed(let reason):
                    log.warning("composer=\(composer.id.rawValue, privacy: .public) failed: \(String(describing: reason), privacy: .public)")
                    continue
                }
            } catch {
                log.error("composer=\(composer.id.rawValue, privacy: .public) threw: \(String(describing: error), privacy: .public)")
                continue
            }
        }

        log.error("composer chain exhausted — emitting safety-net answer")
        return safetyFallback.genericSupportive(locale: tier0.locale)
    }
}
'

# --- Stubs --------------------------------------------------------------------
write_if_absent "${TARGET_DIR}/FoundationModelsComposer.swift" 'import Foundation
// TODO: import FoundationModels when iOS 26+ deployment target is set.

/// Stub. Implement per references/option-a-foundation-models.md.
/// - Gate at DI time on `SystemLanguageModel.default.availability`.
/// - Use `@Generable` for structured decoding.
/// - Run AnchorValidator at the chain level, not here.
struct FoundationModelsComposer: GroundedAnswerComposer {
    let id: ComposerID = .foundationModels

    func compose(
        bundle: EvidenceBundle,
        tier0: Tier0Output,
        regenerate: Bool
    ) async throws -> GroundedAnswer? {
        // Return nil to fall through until implemented.
        return nil
    }
}
'

write_if_absent "${TARGET_DIR}/SentenceBankComposer.swift" 'import Foundation

/// Stub. Implement per references/option-b-sentence-bank.md.
/// - Load fragments from structured data (JSON/YAML), not inline strings.
/// - Enforce per-user, per-fragment cooldowns.
/// - Localized fragments only; do not machine-translate at runtime.
struct SentenceBankComposer: GroundedAnswerComposer {
    let id: ComposerID = .sentenceBank

    func compose(
        bundle: EvidenceBundle,
        tier0: Tier0Output,
        regenerate: Bool
    ) async throws -> GroundedAnswer? {
        // Return nil to fall through until implemented.
        return nil
    }
}
'

write_if_absent "${TARGET_DIR}/RetrievalStitchComposer.swift" 'import Foundation

/// Stub. Implement per references/option-c-retrieval-stitch.md.
/// - Use top-2 chunks max; weighting by (cosine, archetype affinity, anchor coverage).
/// - Prefer B over C for emotional-intent bundles.
/// - Dedupe overlapping phrases across chunks.
struct RetrievalStitchComposer: GroundedAnswerComposer {
    let id: ComposerID = .retrievalStitch

    func compose(
        bundle: EvidenceBundle,
        tier0: Tier0Output,
        regenerate: Bool
    ) async throws -> GroundedAnswer? {
        // Return nil to fall through until implemented.
        return nil
    }
}
'

write_if_absent "${TARGET_DIR}/SafetyFallbackComposer.swift" 'import Foundation

/// Static safety copy. Never composed, always localized.
struct SafetyFallbackComposer: Sendable {
    func crisisResponse(locale: String) -> GroundedAnswer {
        GroundedAnswer(
            answer: "", // TODO: fill from localized safety bundle.
            grounding: "",
            followUp: nil,
            archetype: .reflect,
            composerUsed: .safetyFallback,
            confidence: .high,
            anchorsNamed: []
        )
    }

    func genericSupportive(locale: String) -> GroundedAnswer {
        GroundedAnswer(
            answer: "", // TODO: fill from localized fallback bundle.
            grounding: "",
            followUp: nil,
            archetype: .reflect,
            composerUsed: .safetyFallback,
            confidence: .low,
            anchorsNamed: []
        )
    }
}
'

write_if_absent "${TARGET_DIR}/AnchorValidator.swift" 'import Foundation

/// Runs once inside the chain. Rejects candidates that mention anchors
/// (signs, planets, houses, HD attributes) not present in the bundle, or
/// that violate word-count / anchor-count rules.
struct AnchorValidator: Sendable {
    enum ValidationResult: Equatable {
        case ok
        case failed(reason: FailureReason)
    }

    enum FailureReason: Equatable {
        case wordCountOutOfBounds(Int)
        case tooFewAnchors(Int)
        case inventedAnchors([String])
        case forbiddenPhrase(String)
        case missingGrounding
    }

    func validate(_ answer: GroundedAnswer, bundle: EvidenceBundle) -> ValidationResult {
        // TODO: implement per SKILL.md non-negotiables.
        return .ok
    }
}
'

# --- Types referenced by composers (forward declarations) ---------------------
write_if_absent "${TARGET_DIR}/EvidenceBundle.swift" 'import Foundation

/// Output of Tier 0 bundle assembly. Typed, not stringly-encoded.
/// Keep optional sections truly optional — composers must handle missing data
/// without fabricating.
struct EvidenceBundle: Sendable {
    // TODO: fill in fields per references/intent-router-patterns.md.
}

struct Tier0Output: Sendable {
    let archetype: Archetype
    let safetyBoundary: SafetyBoundary
    let emotionalIntent: Bool
    let locale: String

    enum SafetyBoundary: String, Codable, Sendable {
        case none
        case supportiveNonClinical = "supportive_non_clinical"
        case crisisRedirect = "crisis_redirect"
    }
}
'

echo ""
echo "Done. Next steps:"
echo "  1. Implement FoundationModelsComposer per references/option-a-foundation-models.md"
echo "  2. Implement SentenceBankComposer per references/option-b-sentence-bank.md (universal fallback — ship first)"
echo "  3. Implement RetrievalStitchComposer per references/option-c-retrieval-stitch.md"
echo "  4. Wire ComposerChain in your DI container at DI time (not per-turn)."
echo "  5. Add per-answer telemetry per references/swiftui-composer-integration.md"
