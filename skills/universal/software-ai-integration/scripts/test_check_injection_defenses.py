"""Regression tests for fail-closed agent-config validation."""

import unittest

from check_injection_defenses import (
    check_output_structured_validation,
    check_retrieval_source_allowlist,
    check_tool_allowlist,
)


class InjectionDefenseValidationTests(unittest.TestCase):
    def test_structured_flag_requires_a_schema(self) -> None:
        result = check_output_structured_validation({"output_validation": {"structured": True}})
        self.assertFalse(result.passed)

    def test_boolean_output_schema_does_not_count_as_schema(self) -> None:
        result = check_output_structured_validation({"output_schema": True})
        self.assertFalse(result.passed)

    def test_empty_allowlist_entries_fail(self) -> None:
        self.assertFalse(check_tool_allowlist({"tools_allowed": [""]}).passed)
        self.assertFalse(check_retrieval_source_allowlist({"retrieval_sources": [""]}).passed)

    def test_valid_contract_passes(self) -> None:
        self.assertTrue(check_tool_allowlist({"tools_allowed": ["read_document"]}).passed)
        self.assertTrue(check_retrieval_source_allowlist({"retrieval_sources": ["internal_docs"]}).passed)
        self.assertTrue(
            check_output_structured_validation(
                {"output_validation": {"structured": True, "schema_ref": "SummarySchema"}}
            ).passed
        )


if __name__ == "__main__":
    unittest.main()
