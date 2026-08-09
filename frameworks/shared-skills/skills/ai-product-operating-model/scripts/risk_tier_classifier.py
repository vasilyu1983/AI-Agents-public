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
              tool access; regulatory scope.

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
    0 — classification complete
    1 — input error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Signal definitions
# ---------------------------------------------------------------------------

# Each signal is: (label, match_terms, tier_contribution)
# tier_contribution: 0 = Tier 0 signal, 1 = Tier 1 signal, 2 = Tier 2 signal

DATA_TYPE_SIGNALS = [
    # Tier 2 — sensitive categories
    ("health / medical data", ["health", "medical", "diagnosis", "prescription", "ehr", "phi", "hipaa"], 2),
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

ACTION_SIGNALS = [
    # Tier 2 — irreversible or high-value
    ("financial transaction", ["charge", "payment", "transfer", "withdraw", "refund", "invoice", "debit"], 2),
    ("account deletion", ["delete_account", "delete_user", "remove_account", "purge"], 2),
    ("legal action / filing", ["file_legal", "submit_filing", "sign_contract", "legal_action"], 2),
    ("bulk data export", ["export_all", "bulk_export", "data_download", "dump"], 2),
    ("privilege escalation", ["grant_admin", "elevate_permissions", "change_role"], 2),
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
    ("finance domain", ["finance", "fintech", "banking", "insurance", "investment", "trading"], 2),
    ("health domain", ["health", "healthcare", "medical", "clinical", "pharma"], 2),
    ("legal domain", ["legal", "law", "compliance", "regulatory", "gdpr", "hipaa"], 2),
    ("HR domain", ["hr", "human_resources", "recruiting", "payroll"], 2),
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
        self.autonomy_signal: Optional[str] = None
        self.mitigations_found: list[str] = []

    @property
    def tier_label(self) -> str:
        return {0: "Tier 0 — Low risk", 1: "Tier 1 — Medium risk", 2: "Tier 2 — High risk"}[self.tier]

    @property
    def minimum_controls(self) -> list[str]:
        if self.tier == 0:
            return [
                "External API acceptable (verify no PI in requests).",
                "Standard telemetry: cost, latency, refusal rate.",
                "Eval suite before production.",
            ]
        elif self.tier == 1:
            return [
                "External API with verified DPA (no training on data, retention <= 30 days).",
                "Sensitive fields minimized before model submission.",
                "Output filtering for PII before user-visible response.",
                "Eval suite + staged rollout before broad launch.",
                "Audit log: actor, feature, data class, timestamp.",
            ]
        else:
            return [
                "Managed private endpoint or self-hosted required (verify with legal/DPO).",
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


def classify(spec: dict) -> ClassificationResult:
    result = ClassificationResult()
    text = extract_text(spec)
    max_tier = 0

    # --- Data type signals ---
    for label, terms, contrib in DATA_TYPE_SIGNALS:
        if any(term in text for term in terms):
            result.data_signals.append(f"{label} (Tier {contrib})")
            if contrib > max_tier:
                max_tier = contrib

    # --- Action signals ---
    for label, terms, contrib in ACTION_SIGNALS:
        if any(term in text for term in terms):
            result.action_signals.append(f"{label} (Tier {contrib})")
            if contrib > max_tier:
                max_tier = contrib

    # --- Domain signals ---
    domain = str(spec.get("domain", "")).lower()
    for label, terms, contrib in DOMAIN_SIGNALS:
        if any(term in (domain or text) for term in terms):
            result.domain_signals.append(f"{label} (Tier {contrib})")
            if contrib > max_tier:
                max_tier = contrib

    # --- Autonomy level ---
    autonomy = str(spec.get("autonomy_level", "")).lower().replace("-", "_").replace(" ", "_")
    if autonomy in AUTONOMY_SIGNALS:
        contrib = AUTONOMY_SIGNALS[autonomy]
        result.autonomy_signal = f"{autonomy} (Tier {contrib})"
        if contrib > max_tier:
            max_tier = contrib
    elif "agent" in text:
        contrib = 2
        result.autonomy_signal = "agent detected in text (Tier 2)"
        if contrib > max_tier:
            max_tier = contrib

    result.tier = max_tier

    # --- Build reasons ---
    if result.data_signals:
        result.reasons.append(f"Data types: {', '.join(result.data_signals)}")
    if result.action_signals:
        result.reasons.append(f"Actions: {', '.join(result.action_signals)}")
    if result.domain_signals:
        result.reasons.append(f"Domain: {', '.join(result.domain_signals)}")
    if result.autonomy_signal:
        result.reasons.append(f"Autonomy: {result.autonomy_signal}")

    # --- Mitigations ---
    if spec.get("human_in_loop") is True:
        result.mitigations_found.append("human_in_loop: true — reduces action risk by one tier in some cases")
    if spec.get("user_consent_obtained") is True:
        result.mitigations_found.append("user_consent_obtained: true — required for Tier 1+ but does not lower tier")

    if not result.reasons:
        result.reasons.append("No strong signals detected — defaulting to Tier 0.")

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
    print()
    print("Signals detected:")
    for r in result.reasons:
        print(f"  - {r}")
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
        "autonomy_signal": result.autonomy_signal,
        "mitigations_found": result.mitigations_found,
        "minimum_controls": result.minimum_controls,
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

    sys.exit(0)


if __name__ == "__main__":
    main()
