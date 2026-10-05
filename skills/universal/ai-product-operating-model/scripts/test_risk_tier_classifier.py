#!/usr/bin/env python3
"""
test_risk_tier_classifier.py — fail-closed regression tests for risk_tier_classifier.py.

Covers the EU AI Act Annex III use cases the classifier must map to Tier 2
(loan/credit scoring, CV/recruitment screening), the fail-closed default
for unknown/ambiguous input (must never silently default to Tier 0),
whole-word keyword matching (no substring hits), the Art 5 prohibited-practice
block, and the Art 50 transparency signal.

Usage:
    python3 scripts/test_risk_tier_classifier.py
"""

import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from risk_tier_classifier import classify, parse_text_spec  # noqa: E402


class AnnexIIIHighRiskCases(unittest.TestCase):
    """Annex III use cases must classify Tier 2, never Tier 0."""

    def test_loan_auto_approval_is_tier_2(self):
        result = classify(parse_text_spec("auto-approve loan applications"))
        self.assertEqual(result.tier, 2)
        self.assertFalse(result.needs_review)
        self.assertTrue(any("essential services eligibility" in s for s in result.annex_iii_signals))

    def test_cv_screening_is_tier_2(self):
        result = classify(parse_text_spec("screen job candidates CVs"))
        self.assertEqual(result.tier, 2)
        self.assertFalse(result.needs_review)
        self.assertTrue(any("employment / recruitment" in s for s in result.annex_iii_signals))

    def test_credit_scoring_json_spec_is_tier_2(self):
        spec = {
            "feature_name": "credit-eligibility-scorer",
            "description": "Score consumer creditworthiness for personal loan eligibility",
            "domain": "finance",
            "actions": ["eligibility_decision"],
        }
        result = classify(spec)
        self.assertEqual(result.tier, 2)

    def test_hiring_decision_in_plain_words_is_tier_2(self):
        result = classify(parse_text_spec("decide which applicants to hire"))
        self.assertEqual(result.tier, 2)

    def test_biometric_identification_is_tier_2(self):
        result = classify(parse_text_spec("run facial_recognition for building entry"))
        self.assertEqual(result.tier, 2)

    def test_law_enforcement_risk_scoring_is_tier_2(self):
        result = classify(parse_text_spec("crime_risk scoring for predictive_policing pilot"))
        self.assertEqual(result.tier, 2)


class FailClosedDefault(unittest.TestCase):
    """Unknown/ambiguous input must default to review or a high tier, never Tier 0."""

    def test_unknown_input_never_defaults_to_tier_0(self):
        result = classify(parse_text_spec("xyzzy plugh frobnicate"))
        self.assertGreaterEqual(result.tier, 1)
        self.assertTrue(result.needs_review)

    def test_empty_spec_never_defaults_to_tier_0(self):
        result = classify({})
        self.assertGreaterEqual(result.tier, 1)
        self.assertTrue(result.needs_review)

    def test_explicit_tier_0_signal_is_not_flagged_for_review(self):
        result = classify(parse_text_spec("display public documentation"))
        self.assertEqual(result.tier, 0)
        self.assertFalse(result.needs_review)


class WholeWordMatching(unittest.TestCase):
    """Keywords match whole words and their inflections, never substrings of other words."""

    def test_philosophy_does_not_hit_phi_health(self):
        result = classify(parse_text_spec("A philosophy blog summarizer for public posts"))
        self.assertFalse(any("health" in s for s in result.data_signals))
        self.assertEqual(result.tier, 0)

    def test_three_charts_do_not_hit_hr(self):
        result = classify(parse_text_spec("show three charts of public weather data"))
        self.assertFalse(any("HR" in s for s in result.data_signals + result.domain_signals))
        self.assertEqual(result.tier, 0)

    def test_credit_applicants_are_credit_not_recruitment(self):
        result = classify(parse_text_spec(
            "Automated loan approval decisions for consumer credit applicants"))
        self.assertEqual(result.tier, 2)
        self.assertTrue(any("essential services eligibility" in s for s in result.annex_iii_signals))
        self.assertFalse(any("employment" in s for s in result.annex_iii_signals))

    def test_job_applicants_in_plural_still_hit_recruitment(self):
        result = classify(parse_text_spec("screen applicants for the engineering role"))
        self.assertEqual(result.tier, 2)
        self.assertTrue(any("employment / recruitment" in s for s in result.annex_iii_signals))

    def test_plural_patients_still_hit_health(self):
        result = classify(parse_text_spec("summarize patients' discharge notes"))
        self.assertEqual(result.tier, 2)
        self.assertTrue(any("health" in s for s in result.data_signals))

    def test_underscore_and_hyphen_terms_match_spaced_text(self):
        result = classify(parse_text_spec("export all rows as a bulk-export"))
        self.assertTrue(any("bulk data export" in s for s in result.action_signals))


class Art5ProhibitedBlock(unittest.TestCase):
    """A possible Art 5 prohibited practice is a block, not just Tier 2."""

    def test_social_scoring_is_blocked(self):
        result = classify(parse_text_spec("social scoring of citizens for benefit access"))
        self.assertTrue(result.prohibited)
        self.assertEqual(result.tier, 2)
        self.assertTrue(any("BLOCKED" in c for c in result.minimum_controls))

    def test_workplace_emotion_recognition_is_blocked(self):
        result = classify(parse_text_spec("emotion recognition of employees during video calls"))
        self.assertTrue(result.prohibited)

    def test_emotion_recognition_outside_work_or_school_is_not_blocked(self):
        result = classify(parse_text_spec("emotion recognition for a driver fatigue safety alert"))
        self.assertFalse(result.prohibited)

    def test_annex_iii_case_is_not_blocked(self):
        result = classify(parse_text_spec("auto-approve loan applications"))
        self.assertFalse(result.prohibited)

    def test_intimate_content_amendment_is_pending_before_effective_date(self):
        result = classify(parse_text_spec("generate non-consensual intimate deepfakes"),
                          as_of=date(2026, 9, 27))
        self.assertFalse(result.prohibited)
        self.assertTrue(result.needs_review)
        self.assertEqual(result.tier, 2)
        self.assertTrue(result.pending_prohibition_signals)

    def test_intimate_content_amendment_blocks_after_effective_date(self):
        result = classify(parse_text_spec("generate non-consensual intimate deepfakes"),
                          as_of=date(2026, 12, 2))
        self.assertTrue(result.prohibited)
        self.assertEqual(result.pending_prohibition_signals, [])


class Art50TransparencySignal(unittest.TestCase):
    """Art 50 duties are reported separately and never clear the fail-closed flag."""

    def test_chatbot_gets_interaction_disclosure(self):
        result = classify(parse_text_spec("customer support chatbot answering order questions"))
        self.assertTrue(any("Art 50(1)" in s for s in result.transparency_signals))

    def test_image_generation_gets_marking_duty(self):
        result = classify(parse_text_spec("generate images for public marketing posts"))
        self.assertTrue(any("Art 50(2)" in s for s in result.transparency_signals))

    def test_transparency_signal_alone_keeps_needs_review(self):
        result = classify(parse_text_spec("chatbot"))
        self.assertTrue(result.transparency_signals)
        self.assertTrue(result.needs_review)
        self.assertGreaterEqual(result.tier, 1)

    def test_no_transparency_signal_for_back_office_summaries(self):
        result = classify(parse_text_spec("display public documentation"))
        self.assertEqual(result.transparency_signals, [])


class CliExitCodes(unittest.TestCase):
    """The exit code is the gate: unclassified input must not exit 0."""

    SCRIPT = Path(__file__).resolve().parent / "risk_tier_classifier.py"

    def run_cli(self, text):
        return subprocess.run([sys.executable, str(self.SCRIPT), "--text", text],
                              capture_output=True, text=True).returncode

    def test_unclassified_input_exits_2(self):
        self.assertEqual(self.run_cli("xyzzy plugh frobnicate"), 2)

    def test_classified_input_exits_0(self):
        self.assertEqual(self.run_cli("auto-approve loan applications"), 0)

    def test_prohibited_practice_exits_3(self):
        self.assertEqual(self.run_cli("social scoring of citizens for benefit access"), 3)


if __name__ == "__main__":
    unittest.main()
