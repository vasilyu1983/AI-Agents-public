#!/usr/bin/env python3
"""
risk_tier_classifier.py — stdlib-only risk tier classifier for AI feature specs.

Reads a feature spec (JSON or plain text) and emits a Tier 0 / 1 / 2
classification with reasoning. Based on data sensitivity, action reversibility,
and autonomy level.

Tier model (from references/data-boundaries-and-risk-tiers.md):
    Tier 0 — Low risk: public or non-personal data, read-only or display actions,
              no financial/health/legal domain. External API default acceptable.
    Tier 1 — Medium risk: user PI involved but not sensitive categories; bounded
              tool use with reversible actions; explicit control flow; human can
              review before commit.
    Tier 2 — High risk: sensitive PI categories (health, financial, legal,
              biometric); irreversible or high-value actions; agentic with broad
              tool access; regulatory scope; EU AI Act Annex III use cases
              (biometric ID, critical infrastructure, education/exam scoring,
              employment/recruitment/worker management, essential
              private/public services incl. credit and benefits eligibility,
              law enforcement, migration/asylum/border control,
              administration of justice/democratic processes).

EU AI Act signals reported separately from the tier:
    Art 5 prohibited practice — a BLOCK, not a tier. A hit means "do not build
              or deploy until legal review confirms the practice is outside
              Art 5"; the result is Tier 2 with `prohibited: true`.
    Later-applying Art 5 amendment — before its application date, flag Tier 2
              with `pending_prohibition_signals` and `needs_review: true`;
              after that date, report it as a possible prohibited practice.
    Art 50 transparency — an obligation, not a tier: interaction disclosure
              (chatbots, voice assistants), machine-readable marking of
              synthetic content, deepfake and emotion-recognition disclosure.
    Look up the applicable dates in the canonical owner,
    ../../startup-compliance-enterprise-readiness/references/regulatory-overlays.md.

Matching: keywords match whole words (after folding "_", "-", "/" and "."
into spaces) plus a fixed set of inflections — plural, past tense, -ing,
-er, -ion, -ies — so "applicants" matches "applicant" but "philosophy"
does not match "phi" and "three" does not match "hr". Ambiguous words that
belong to more than one domain (a bare "applicant" or "candidate" is used for
loans, jobs, and model selection alike) are listed only in unambiguous
phrases ("job applicant", "job candidate").

Fail-closed policy: this classifier is a triage aid, not a compliance
determination. Unknown, ambiguous, or weak-signal input never defaults to
Tier 0 — it defaults to Tier 1 with `needs_review: true` and a non-zero exit
code, forcing a human to make the Tier 0 call explicitly. An explicit Tier 0
result only occurs when a recognized Tier-0 signal actually matched (public
content, anonymized data, display/summarize action).

Usage:
    python3 scripts/risk_tier_classifier.py --input feature-spec.json
    python3 scripts/risk_tier_classifier.py --text "Feature: summarize emails"
    python3 scripts/risk_tier_classifier.py --input spec.json --output tier.json

Input JSON format (all fields optional, richer input = more accurate classification):
    {
      "feature_name": "...",
      "description": "...",
      "data_types": ["user_email", "order_history", ...],
      "actions": ["read", "send_email", "charge_payment", ...],
      "autonomy_level": "request_response | tool_workflow | agent",
      "domain": "support | finance | health | legal | hr | general | ...",
      "user_consent_obtained": true,
      "human_in_loop": false
    }

Exit codes:
    0 — classification complete, an explicit signal was matched
    1 — input error
    2 — unclassified input or later-applying Art 5 signal (needs_review=true);
        treat as a gate failure requiring human review
    3 — possible EU AI Act Art 5 prohibited practice matched (prohibited=true);
        blocked until legal review; treat as a gate failure
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Signal definitions
# ---------------------------------------------------------------------------

# Each signal is: (label, match_terms, tier_contribution)
# tier_contribution: 0 = Tier 0 signal, 1 = Tier 1 signal, 2 = Tier 2 signal

DATA_TYPE_SIGNALS = [
    # Tier 2 — sensitive categories
    ("health / medical data", ["health", "healthcare", "medical", "patient", "diagnosis", "prescription", "ehr", "phi", "hipaa"], 2),
    ("financial / payment data", ["financial", "payment", "card", "bank", "credit", "debit", "billing", "transaction", "pci"], 2),
    ("legal / compliance data", ["legal", "compliance", "contract", "lawsuit", "regulatory", "kyc", "aml"], 2),
    ("biometric data", ["biometric", "face", "fingerprint", "voice_print", "retina"], 2),
    ("government ID", ["passport", "ssn", "national_id", "drivers_license", "tax_id"], 2),
    ("HR / employee data", ["salary", "performance_review", "hr", "employee_record", "payroll"], 2),
    # Tier 1 — personal but not sensitive category
    ("user email", ["email", "user_email"], 1),
    ("user name / contact", ["name", "address", "phone", "contact"], 1),
    ("user behavior / preferences", ["behavior", "preference", "history", "usage_data", "analytics"], 1),
    ("authentication credentials", ["password", "token", "api_key", "credential", "secret"], 1),
    # Tier 0 — public or non-personal
    ("public content", ["public", "published", "open_data", "documentation", "product_catalog"], 0),
    ("anonymized / aggregate", ["anonymized", "aggregate", "aggregate_metrics", "pseudonymized"], 0),
]

# EU AI Act Annex III high-risk use-case categories. These always contribute
# Tier 2 regardless of which data/action terms also matched — Annex III
# status is about the use case, not just the data class. See
# references/data-boundaries-and-risk-tiers.md and the canonical EU AI Act
# statement in ../../startup-compliance-enterprise-readiness/references/regulatory-overlays.md.
ANNEX_III_SIGNALS = [
    ("biometric identification/categorization", ["biometric_id", "facial_recognition", "biometric_categorization", "emotion_recognition"], 2),
    ("critical infrastructure", ["critical_infrastructure", "water_supply", "power_grid", "gas_supply", "traffic_management"], 2),
    ("education / exam scoring", ["exam_scoring", "admissions", "student_assessment", "proctoring", "vocational_training_access"], 2),
    ("employment / recruitment / worker management", [
        "recruit", "recruitment", "hire", "hiring", "job_applicant", "job_candidate", "job_application",
        "candidate_screening", "screen_candidate", "resume", "cv", "screen_cv", "screen_resume",
        "worker_management", "promotion_decision",
        "termination_decision", "task_allocation_monitoring",
    ], 2),
    ("essential services eligibility — credit/benefits/insurance", [
        "loan", "credit_scoring", "creditworthiness", "mortgage", "credit_eligibility",
        "public_benefits", "welfare_eligibility", "insurance_underwriting", "insurance_pricing",
    ], 2),
    ("law enforcement", ["law_enforcement", "predictive_policing", "crime_risk", "evidence_reliability_assessment"], 2),
    ("migration / asylum / border control", ["migration", "asylum", "border_control", "visa_application"], 2),
    ("justice / democratic processes", ["judicial_decision", "sentencing", "legal_research_for_ruling", "election_influence"], 2),
]

# Ambiguous terms that count only when a context term also matches:
# (label, terms, context_terms, tier). "Credit applicants" is a credit case,
# not a recruitment case; "candidate" is also used for candidate models.
ANNEX_III_CONTEXT_SIGNALS = [
    ("employment / recruitment / worker management", ["applicant", "candidate"],
     ["job", "role", "position", "vacancy", "interview", "employer", "employment", "hr", "talent", "staffing"], 2),
]

# EU AI Act Art 5 prohibited practices currently applicable. A hit is a
# BLOCK, not a tier: stop and get legal review. Format: (label, terms, context_terms);
# an empty context list means the terms alone are enough.
ART5_PROHIBITED_SIGNALS = [
    ("subliminal / manipulative or deceptive techniques causing harm",
     ["subliminal", "manipulative_technique", "deceptive_technique", "behavioural_manipulation",
      "behavioral_manipulation"], []),
    ("exploiting vulnerabilities of age, disability, or social/economic situation",
     ["exploit_vulnerability", "exploit_vulnerabilities", "target_vulnerable"], []),
    ("social scoring", ["social_scoring", "social_score", "social_credit_score"], []),
    ("crime prediction based solely on profiling",
     ["solely_on_profiling", "profiling_based_crime_prediction"], []),
    ("untargeted scraping of facial images for recognition databases",
     ["untargeted_scraping", "scrape_facial_images", "facial_image_scraping", "face_scraping"], []),
    ("emotion recognition in the workplace or education",
     ["emotion_recognition", "emotion_detection", "emotion_inference"],
     ["workplace", "employee", "worker", "staff", "school", "student", "classroom", "education"]),
    ("biometric categorisation inferring sensitive attributes",
     ["biometric_categorization", "biometric_categorisation", "infer_race", "infer_religion",
      "infer_sexual_orientation", "infer_political_opinion"],
     ["race", "ethnicity", "religion", "religious", "political", "sexual_orientation", "trade_union",
      "infer_race", "infer_religion", "infer_sexual_orientation", "infer_political_opinion"]),
    ("real-time remote biometric identification in public spaces",
     ["real_time_biometric_identification", "real_time_facial_recognition", "live_facial_recognition"],
     ["public", "public_space", "street", "crowd"]),
]

# Regulation (EU) 2026/1744 added these Art 5 practices, applicable from
# 2 December 2026. Before that date they need legal review but must not be
# described as an already-applicable Art 5 prohibition. Recheck the official
# enforcement timeline when using this triage aid.
NEW_ART5_EFFECTIVE_DATE = date(2026, 12, 2)
NEW_ART5_SIGNALS = (
    "non-consensual intimate material or child sexual abuse material",
    ["non_consensual_intimate", "intimate_deepfake", "nudify", "undress_app", "csam",
     "child_sexual_abuse_material"],
)

# EU AI Act Art 50 transparency duties. An obligation to plan for, not a tier.
# Format: (label, terms).
ART50_TRANSPARENCY_SIGNALS = [
    ("Art 50(1) interaction disclosure — tell people they are dealing with an AI system, "
     "at the latest at first interaction, unless it is obvious",
     ["chatbot", "chat_bot", "chat_assistant", "virtual_assistant", "voice_assistant", "voice_bot",
      "voicebot", "conversational_agent", "conversational_ai", "ai_assistant", "ai_companion"]),
    ("Art 50(2) machine-readable marking of synthetic audio, image, video, or text output",
     ["generate_image", "image_generation", "text_to_image", "generate_video", "video_generation",
      "text_to_video", "generate_audio", "audio_generation", "speech_synthesis", "text_to_speech",
      "voice_clone", "voice_cloning", "synthetic_media", "synthetic_content", "ai_generated_content",
      "generated_image", "generated_video"]),
    ("Art 50(3) inform people exposed to emotion recognition or biometric categorisation",
     ["emotion_recognition", "emotion_detection", "biometric_categorization", "biometric_categorisation"]),
    ("Art 50(4) disclose deepfakes and AI-generated text published on matters of public interest",
     ["deepfake", "face_swap", "ai_generated_news", "ai_written_news", "synthetic_news"]),
]

ACTION_SIGNALS = [
    # Tier 2 — irreversible or high-value
    ("financial transaction", ["charge", "payment", "transfer", "withdraw", "withdrawal", "refund", "invoice", "debit"], 2),
    ("account deletion", ["delete_account", "delete_user", "remove_account", "purge"], 2),
    ("legal action / filing", ["file_legal", "submit_filing", "sign_contract", "legal_action"], 2),
    ("bulk data export", ["export_all", "bulk_export", "data_download", "dump"], 2),
    ("privilege escalation", ["grant_admin", "elevate_permissions", "change_role"], 2),
    ("automated eligibility / approval decision", ["auto_approve", "auto_reject", "auto_deny", "eligibility_decision", "approve_application", "deny_application"], 2),
    # Tier 1 — reversible tool use
    ("send email / message", ["send_email", "send_message", "notify", "alert"], 1),
    ("create / update record", ["create", "update", "edit", "modify", "upsert"], 1),
    ("read user data", ["read", "fetch", "retrieve", "query", "lookup"], 1),
    ("schedule / book", ["schedule", "book", "reserve", "calendar"], 1),
    # Tier 0 — display / summarize only
    ("display / render", ["display", "render", "show", "present", "format"], 0),
    ("summarize / classify", ["summarize", "classify", "extract", "analyze", "parse"], 0),
    ("search / lookup public", ["search", "lookup", "index"], 0),
]

DOMAIN_SIGNALS = [
    ("finance domain", ["finance", "fintech", "banking", "insurance", "investment", "trading", "lending", "credit"], 2),
    ("health domain", ["health", "healthcare", "medical", "clinical", "pharma", "pharmacy", "pharmaceutical"], 2),
    ("legal domain", ["legal", "law", "compliance", "regulatory", "gdpr", "hipaa"], 2),
    ("HR domain", ["hr", "human_resources", "recruiting", "payroll", "recruitment"], 2),
    ("support / general domain", ["support", "customer_service", "help", "general"], 0),
    ("ecommerce / retail", ["ecommerce", "retail", "shop", "order", "catalog"], 1),
]

AUTONOMY_SIGNALS = {
    "request_response": 0,
    "llm_feature": 0,
    "tool_workflow": 1,
    "agent": 2,
    "agentic": 2,
    "multi_step": 1,
}

# Fail-closed default: unknown/ambiguous input never lands on Tier 0. It
# defaults to this tier and is flagged needs_review so a human makes the
# Tier 0 call explicitly (see module docstring "Fail-closed policy").
DEFAULT_UNCLASSIFIED_TIER = 1


# ---------------------------------------------------------------------------
# Keyword matching
# ---------------------------------------------------------------------------

_SEPARATORS = re.compile(r"[\s_\-/.,;:()\[\]{}\"'!?]+")
_VOWELS = set("aeiou")


def normalize(text: str) -> str:
    """Lowercase and fold separators so "screen_cv", "screen-cv" and "screen cv" match alike."""
    return " " + _SEPARATORS.sub(" ", text.lower()).strip() + " "


def _inflections(word: str) -> list[str]:
    """Deliberate inflections of the LAST word of a term.

    Covers plural, past tense, -ing, agent noun, and -ion forms, with the usual
    English spelling changes (drop final "e", "y" -> "ies"/"ied", doubled final
    consonant). It does not match arbitrary prefixes or suffixes, so "phi" never
    matches "philosophy" and "hr" never matches "three".
    """
    forms = {word, word + "s", word + "es", word + "ed", word + "ing", word + "er", word + "ers",
             word + "ion", word + "ions"}
    if word.endswith("e"):
        stem = word[:-1]
        forms |= {word + "d", word + "r", word + "rs", stem + "ing", stem + "ion", stem + "ions",
                  stem + "al", stem + "als"}
    if word.endswith("y") and len(word) > 2 and word[-2] not in _VOWELS:
        stem = word[:-1]
        forms |= {stem + "ies", stem + "ied", stem + "ication", stem + "ications"}
    if len(word) >= 3 and word[-1] not in _VOWELS and word[-1] not in "wxy" and word[-2] in _VOWELS:
        forms |= {word + word[-1] + "ed", word + word[-1] + "ing", word + word[-1] + "er"}
    return sorted(forms, key=len, reverse=True)


_PATTERN_CACHE: dict[str, re.Pattern] = {}


def _term_pattern(term: str) -> re.Pattern:
    pattern = _PATTERN_CACHE.get(term)
    if pattern is None:
        words = normalize(term).split()
        head = " ".join(re.escape(w) for w in words[:-1])
        tail = "|".join(re.escape(f) for f in _inflections(words[-1]))
        body = (head + " " if head else "") + "(?:" + tail + ")"
        pattern = re.compile(r" " + body + r" ")
        _PATTERN_CACHE[term] = pattern
    return pattern


def matches_any(normalized_text: str, terms: list[str]) -> bool:
    """True when any term occurs as a whole word or phrase (with inflections)."""
    return any(_term_pattern(term).search(normalized_text) for term in terms)


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class ClassificationResult:
    def __init__(self):
        self.tier: int = 0
        self.reasons: list[str] = []
        self.data_signals: list[str] = []
        self.action_signals: list[str] = []
        self.domain_signals: list[str] = []
        self.annex_iii_signals: list[str] = []
        self.autonomy_signal: Optional[str] = None
        self.mitigations_found: list[str] = []
        self.needs_review: bool = False
        self.prohibited_signals: list[str] = []
        self.pending_prohibition_signals: list[str] = []
        self.transparency_signals: list[str] = []

    @property
    def prohibited(self) -> bool:
        return bool(self.prohibited_signals)

    @property
    def tier_label(self) -> str:
        return {0: "Tier 0 — Low risk", 1: "Tier 1 — Medium risk", 2: "Tier 2 — High risk"}[self.tier]

    @property
    def minimum_controls(self) -> list[str]:
        if self.prohibited:
            return [
                "BLOCKED: do not build, pilot, or deploy until legal review confirms the use case "
                "is outside the EU AI Act Art 5 prohibited practices (or outside EU scope).",
                "Record the legal decision, the reviewer, and the scope boundary before any work resumes.",
            ]
        if self.pending_prohibition_signals:
            return [
                "REVIEW: check the Art 5 amendment's application date and other applicable law before rollout.",
                "Record legal ownership and a decision before proceeding.",
            ]
        if self.tier == 0:
            return [
                "External API acceptable (verify no PI in requests).",
                "Standard telemetry: cost, latency, refusal rate.",
                "Eval suite before production.",
            ]
        elif self.tier == 1:
            return [
                "External API only after verifying the applicable DPA, training use, and retention terms.",
                "Sensitive fields minimized before model submission.",
                "Output filtering for PII before user-visible response.",
                "Eval suite + staged rollout before broad launch.",
                "Audit log: actor, feature, data class, timestamp.",
            ]
        else:
            return [
                "Narrow provider allowlist and isolation matched to the data and action risk.",
                "PI minimization and redaction before model submission — non-negotiable.",
                "Human-in-the-loop approval for irreversible or high-value actions.",
                "Explicit rollback plan for every action type.",
                "Full audit trail with retention policy.",
                "Offline evals + canary rollout before any production traffic.",
                "Incident playbook and escalation path defined before launch.",
            ]


def extract_text(spec: dict) -> str:
    """Flatten spec dict to a searchable string."""
    parts = []
    for v in spec.values():
        if isinstance(v, str):
            parts.append(v.lower())
        elif isinstance(v, list):
            parts.extend(str(i).lower() for i in v)
    return " ".join(parts)


def classify(spec: dict, *, as_of: Optional[date] = None) -> ClassificationResult:
    result = ClassificationResult()
    text = normalize(extract_text(spec))
    max_tier = 0

    # --- Data type signals ---
    for label, terms, contrib in DATA_TYPE_SIGNALS:
        if matches_any(text, terms):
            result.data_signals.append(f"{label} (Tier {contrib})")
            if contrib > max_tier:
                max_tier = contrib

    # --- Action signals ---
    for label, terms, contrib in ACTION_SIGNALS:
        if matches_any(text, terms):
            result.action_signals.append(f"{label} (Tier {contrib})")
            if contrib > max_tier:
                max_tier = contrib

    # --- Domain signals ---
    domain = normalize(str(spec.get("domain", ""))) if spec.get("domain") else ""
    for label, terms, contrib in DOMAIN_SIGNALS:
        if matches_any(domain or text, terms):
            result.domain_signals.append(f"{label} (Tier {contrib})")
            if contrib > max_tier:
                max_tier = contrib

    # --- EU AI Act Annex III use-case signals (always Tier 2) ---
    for label, terms, contrib in ANNEX_III_SIGNALS:
        if matches_any(text, terms):
            result.annex_iii_signals.append(f"{label} (Tier {contrib})")
            if contrib > max_tier:
                max_tier = contrib
    for label, terms, context, contrib in ANNEX_III_CONTEXT_SIGNALS:
        entry = f"{label} (Tier {contrib})"
        if entry not in result.annex_iii_signals and matches_any(text, terms) and matches_any(text, context):
            result.annex_iii_signals.append(entry)
            if contrib > max_tier:
                max_tier = contrib

    # --- Autonomy level ---
    autonomy = str(spec.get("autonomy_level", "")).lower().replace("-", "_").replace(" ", "_")
    if autonomy in AUTONOMY_SIGNALS:
        contrib = AUTONOMY_SIGNALS[autonomy]
        result.autonomy_signal = f"{autonomy} (Tier {contrib})"
        if contrib > max_tier:
            max_tier = contrib
    elif matches_any(text, ["agent", "agentic"]):
        contrib = 2
        result.autonomy_signal = "agent detected in text (Tier 2)"
        if contrib > max_tier:
            max_tier = contrib

    # --- EU AI Act Art 5 prohibited practices (block, reported as Tier 2) ---
    for label, terms, context in ART5_PROHIBITED_SIGNALS:
        if matches_any(text, terms) and (not context or matches_any(text, context)):
            result.prohibited_signals.append(label)
    if matches_any(text, NEW_ART5_SIGNALS[1]):
        if (as_of or date.today()) >= NEW_ART5_EFFECTIVE_DATE:
            result.prohibited_signals.append(NEW_ART5_SIGNALS[0])
        else:
            result.pending_prohibition_signals.append(NEW_ART5_SIGNALS[0])
            result.needs_review = True
    if result.prohibited_signals or result.pending_prohibition_signals:
        max_tier = 2

    result.tier = max_tier

    # --- Build reasons ---
    if result.data_signals:
        result.reasons.append(f"Data types: {', '.join(result.data_signals)}")
    if result.action_signals:
        result.reasons.append(f"Actions: {', '.join(result.action_signals)}")
    if result.domain_signals:
        result.reasons.append(f"Domain: {', '.join(result.domain_signals)}")
    if result.annex_iii_signals:
        result.reasons.append(f"EU AI Act Annex III use case: {', '.join(result.annex_iii_signals)}")
    if result.autonomy_signal:
        result.reasons.append(f"Autonomy: {result.autonomy_signal}")
    if result.prohibited_signals:
        result.reasons.append(
            f"EU AI Act Art 5 possible prohibited practice (BLOCK): {', '.join(result.prohibited_signals)}")
    if result.pending_prohibition_signals:
        result.reasons.append(
            f"EU AI Act Art 5 amendment pending legal review: {', '.join(result.pending_prohibition_signals)}")

    # --- Mitigations ---
    if spec.get("human_in_loop") is True:
        result.mitigations_found.append("human_in_loop: true — reduces action risk by one tier in some cases")
    if spec.get("user_consent_obtained") is True:
        result.mitigations_found.append("user_consent_obtained: true — required for Tier 1+ but does not lower tier")

    # --- Fail-closed default ---
    # No recognized signal matched at all: this is not evidence of low risk,
    # it is an unclassified input. Never default to Tier 0 here. Escalate to
    # DEFAULT_UNCLASSIFIED_TIER and flag for mandatory human review.
    if not result.reasons:
        result.needs_review = True
        result.tier = max(result.tier, DEFAULT_UNCLASSIFIED_TIER)
        result.reasons.append(
            f"No recognized signals matched — fail-closed default to "
            f"Tier {DEFAULT_UNCLASSIFIED_TIER} (needs_review=true). This is NOT a Tier 0 "
            f"classification; a human must review this spec and either add enough detail "
            f"to classify it or explicitly confirm Tier 0."
        )

    # --- EU AI Act Art 50 transparency duties (obligation, not a tier) ---
    # Collected after the fail-closed check on purpose: a transparency duty says
    # nothing about data or action risk, so it never clears needs_review.
    for label, terms in ART50_TRANSPARENCY_SIGNALS:
        if matches_any(text, terms):
            result.transparency_signals.append(label)

    return result


# ---------------------------------------------------------------------------
# Text spec parsing
# ---------------------------------------------------------------------------

def parse_text_spec(text: str) -> dict:
    """Convert plain text description to a minimal spec dict."""
    return {
        "description": text,
        "feature_name": text[:60],
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_result(result: ClassificationResult, feature_name: str) -> None:
    print(f"\n=== Risk Tier Classification ===")
    print(f"Feature:    {feature_name}")
    print(f"Tier:       {result.tier_label}")
    if result.prohibited:
        print("BLOCKED: possible EU AI Act Art 5 prohibited practice — legal review before any work.")
    if result.needs_review:
        print("NEEDS REVIEW: unclassified input or pending legal applicability; do not treat as cleared.")
    print()
    print("Signals detected:")
    for r in result.reasons:
        print(f"  - {r}")
    if result.transparency_signals:
        print()
        print("EU AI Act Art 50 transparency duties (apply at any tier):")
        for t in result.transparency_signals:
            print(f"  ! {t}")
    if result.mitigations_found:
        print()
        print("Mitigations noted:")
        for m in result.mitigations_found:
            print(f"  + {m}")
    print()
    print("Minimum controls for this tier:")
    for c in result.minimum_controls:
        print(f"  • {c}")


def to_dict(result: ClassificationResult, feature_name: str) -> dict:
    return {
        "feature_name": feature_name,
        "tier": result.tier,
        "tier_label": result.tier_label,
        "reasons": result.reasons,
        "data_signals": result.data_signals,
        "action_signals": result.action_signals,
        "domain_signals": result.domain_signals,
        "annex_iii_signals": result.annex_iii_signals,
        "autonomy_signal": result.autonomy_signal,
        "mitigations_found": result.mitigations_found,
        "minimum_controls": result.minimum_controls,
        "needs_review": result.needs_review,
        "prohibited": result.prohibited,
        "prohibited_signals": result.prohibited_signals,
        "pending_prohibition_signals": result.pending_prohibition_signals,
        "transparency_signals": result.transparency_signals,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Classify AI feature spec into risk Tier 0/1/2.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", "-i", metavar="FILE",
                       help="Path to a JSON feature spec file.")
    group.add_argument("--text", "-t", metavar="TEXT",
                       help="Plain text description of the feature (quoted string).")
    p.add_argument("--output", "-o", metavar="FILE",
                   help="Optional path to write JSON classification result.")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        with path.open(encoding="utf-8") as fh:
            try:
                spec = json.load(fh)
            except json.JSONDecodeError as exc:
                print(f"ERROR: malformed JSON: {exc}", file=sys.stderr)
                sys.exit(1)
        feature_name = spec.get("feature_name", path.stem)
    else:
        spec = parse_text_spec(args.text)
        feature_name = spec["feature_name"]

    result = classify(spec)
    print_result(result, feature_name)

    if args.output:
        out_path = Path(args.output)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(to_dict(result, feature_name), fh, indent=2, ensure_ascii=False)
        print(f"\nResult written to: {out_path}")

    # Fail closed: an unclassified/ambiguous spec is a CI-visible signal, not
    # a silent Tier 0 pass. Exit 2 so callers can gate on it. A possible Art 5
    # prohibited practice is a block and takes precedence: exit 3.
    if result.prohibited:
        sys.exit(3)
    sys.exit(2 if result.needs_review else 0)


if __name__ == "__main__":
    main()
