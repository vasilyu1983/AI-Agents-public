#!/usr/bin/env python3
"""Tests for check_workflow_idempotency.py using the n8n fixtures in ../tests/fixtures/.

Run: cd scripts && python3 -m unittest -q test_check_workflow_idempotency
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT = Path(__file__).resolve().parent / "check_workflow_idempotency.py"
FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"


def run(path: Path, *extra: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, json.loads(proc.stdout)


def rules(result: dict) -> set[str]:
    return {issue["rule"] for issue in result["issues"]}


class N8nFixtureTests(unittest.TestCase):
    def run_workflow(self, workflow: dict, *extra: str) -> tuple[int, dict]:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "workflow.json"
            path.write_text(json.dumps(workflow), encoding="utf-8")
            return run(path, *extra)

    def test_retry_on_fail_with_idempotency_header_is_clean(self) -> None:
        # n8n expresses retries as retryOnFail/maxTries, the key as a header
        # parameter, and the failure branch as onError=continueErrorOutput.
        # A linter that only knows its own schema reports false positives here.
        code, result = run(FIXTURES / "n8n_http_idempotent.json", "--strict")
        self.assertEqual(result["issues"], [])
        self.assertEqual(code, 0)

    def test_post_without_key_or_retry_fails(self) -> None:
        code, result = run(FIXTURES / "n8n_http_missing_key.json")
        self.assertEqual(code, 1)
        self.assertIn("missing-idempotency-key", rules(result))
        self.assertIn("missing-retry-policy", rules(result))

    def test_retry_without_key_still_flags_missing_key(self) -> None:
        # Enabling retries must not hide a missing idempotency key.
        wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
        wf["nodes"][0]["parameters"].pop("headerParameters")
        tmp = FIXTURES.parent / "_tmp_retry_no_key.json"
        tmp.write_text(json.dumps(wf))
        try:
            code, result = run(tmp)
        finally:
            tmp.unlink()
        self.assertEqual(code, 1)
        self.assertIn("missing-idempotency-key", rules(result))
        self.assertNotIn("missing-retry-policy", rules(result))

    def test_retry_without_error_output_flags_missing_dlq(self) -> None:
        wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
        wf["nodes"][0].pop("onError")
        tmp = FIXTURES.parent / "_tmp_retry_no_dlq.json"
        tmp.write_text(json.dumps(wf))
        try:
            code, result = run(tmp)
        finally:
            tmp.unlink()
        self.assertEqual(code, 1)
        self.assertIn("sync-side-effect-without-dlq", rules(result))

    def test_unconnected_n8n_error_output_does_not_count_as_dlq(self) -> None:
        wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
        wf["connections"]["Create order"]["main"][1] = []
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("sync-side-effect-without-dlq", rules(result))

    def test_constant_n8n_idempotency_header_does_not_count(self) -> None:
        wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
        wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = "constant-order-key"
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("static-idempotency-key", rules(result))

    def test_connected_error_output_without_dlq_is_not_cleared(self) -> None:
        wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
        wf["nodes"][1]["name"] = "Inspect error"
        wf["connections"]["Create order"]["main"][1][0]["node"] = "Inspect error"
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("sync-side-effect-without-dlq", rules(result))

    def test_generic_nodes_with_explicit_dlq_are_supported(self) -> None:
        wf = {"nodes": [{"id": "create-order", "type": "http", "method": "POST",
                         "idempotency_key": "order-123", "retry": {"max_attempts": 3},
                         "dlq": "orders-dead-letter"}]}
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 0)
        self.assertNotIn("sync-side-effect-without-dlq", rules(result))

    def test_invalid_n8n_idempotency_header_values(self) -> None:
        for value in (None, 42, "", "=", "={{ 'constant' }}", "={{ 'it\\'s-constant' }}"):
            with self.subTest(value=value):
                wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
                wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = value
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 1)
                self.assertTrue({"missing-idempotency-key", "static-idempotency-key"} & rules(result))

    def test_dynamic_n8n_idempotency_header_concatenation(self) -> None:
        wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
        wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = (
            "={{ 'order-' + $json.orderId + '-retry' }}")
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 0)
        self.assertNotIn("static-idempotency-key", rules(result))

    def test_non_runtime_n8n_idempotency_header_values(self) -> None:
        # Each value is empty, malformed, or evaluates to the same key for every item.
        for value in ("=abc", "={{ }}", "{{ }}", "{{ $json.id }}", "={{ $json.id",
                      "={{ 42 }}", "={{ `abc` }}", "={{ 'a' + 'b' }}",
                      "={{ String('abc') }}", "={{ '$json.id' }}", "={{ $now }}"):
            with self.subTest(value=value):
                wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
                wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = value
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 1)
                self.assertIn("static-idempotency-key", rules(result))

    def test_runtime_n8n_idempotency_header_values(self) -> None:
        for value in ("={{ $json.id }}", "=order-{{ $json.orderId }}",
                      "={{ $('Webhook').item.json.id }}", "={{ `order-${$json.id}` }}"):
            with self.subTest(value=value):
                wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
                wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = value
                code, result = self.run_workflow(wf)
                self.assertEqual(result["issues"], [])
                self.assertEqual(code, 0)

    def test_n8n_direct_idempotency_parameter_values(self) -> None:
        # A key-named n8n parameter is an expression field, same as a header value.
        for value, clean in (("=abc", False), ("={{ 42 }}", False), ("abc", False),
                             ("={{ $json.id }}", True)):
            with self.subTest(value=value):
                wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
                wf["nodes"][0]["parameters"]["idempotencyKey"] = value
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 0 if clean else 1)
                self.assertEqual("static-idempotency-key" in rules(result), not clean)
        # Generic (non-n8n) nodes keep accepting a literal key under parameters.
        wf = {"nodes": [{"id": "create-order", "type": "http", "method": "POST",
                         "parameters": {"idempotency_key": "order-123"},
                         "retry": {"max_attempts": 3}, "dlq": "orders-dead-letter"}]}
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 0)

    def test_n8n_expression_edge_values(self) -> None:
        # Comments, per-workflow metadata and bare objects are the same for every item;
        # a "}}" inside a string literal does not end the expression.
        for value, clean in (('={{ /* $json */ "abc" }}', False), ("={{ $workflow.id }}", False),
                             ("={{ $workflow.name }}", False),
                             ('={{ $node["Webhook"].name }}', False), ("={{ $json }}", False),
                             ("={{ $input }}", False), ("={{ $('Webhook').item.json.id }}", True),
                             ('={{ $node["Webhook"].json.id }}', True),
                             ('={{ $json.a + "}}" }}', True)):
            with self.subTest(value=value):
                wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
                wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = value
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 0 if clean else 1)
                self.assertEqual("static-idempotency-key" in rules(result), not clean)

    def test_n8n_nested_key_and_disabled_node(self) -> None:
        with self.subTest(case="parameters.options.idempotencyKey"):
            wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
            params = wf["nodes"][0]["parameters"]
            params.pop("headerParameters")
            params["options"] = {"idempotencyKey": "={{ $json.id }}"}
            code, result = self.run_workflow(wf)
            self.assertEqual(result["issues"], [])
            self.assertEqual(code, 0)
        with self.subTest(case="disabled POST node never executes"):
            wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
            wf["nodes"].append({"id": "x1", "name": "Old create", "disabled": True,
                                "type": "n8n-nodes-base.httpRequest",
                                "parameters": {"method": "POST", "url": "https://api.example.com/x"}})
            code, result = self.run_workflow(wf)
            self.assertEqual(result["issues"], [])
            self.assertEqual(code, 0)

    def test_inert_n8n_dlq_node_does_not_count(self) -> None:
        # A disabled node or sticky note named like a DLQ never receives the failed item.
        for inert in ({"disabled": True}, {"type": "n8n-nodes-base.stickyNote"}):
            with self.subTest(inert=inert):
                wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
                wf["nodes"][1].update(inert)
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 1)
                self.assertIn("sync-side-effect-without-dlq", rules(result))

    def generic_charge(self, **key: object) -> dict:
        step = {"id": "charge", "type": "http", "method": "POST", "url": "https://api.example.com/charge",
                "retry": {"max_attempts": 3}, "dlq": "charge-dlq", **key}
        return {"steps": [step]}

    def test_generic_templated_keys_are_not_judged_by_n8n_expression_rules(self) -> None:
        # `={{ }}` is n8n syntax; other engines template keys as `${...}`, `{{ ... }}`, JSONPath
        # or a structured reference. Applying n8n rules to them reported correct generic keys
        # as static constants or as missing.
        for value in ("${order.id}", "{{ order.id }}", "$.order.id", {"path": "order.id"}):
            for placement, key in (
                ("header", {"parameters": {"headers": [{"name": "Idempotency-Key", "value": value}]}}),
                ("step field", {"idempotency_key": value}),
                ("parameters field", {"parameters": {"idempotencyKey": value}}),
            ):
                with self.subTest(value=value, placement=placement):
                    code, result = self.run_workflow(self.generic_charge(**key))
                    self.assertEqual(result["issues"], [])
                    self.assertEqual(code, 0)

    def test_generic_post_without_key_still_fails(self) -> None:
        # Scoping the n8n rules must not switch off key detection for other engines.
        for key in ({}, {"parameters": {"headers": [{"name": "Idempotency-Key"}]}}):
            with self.subTest(key=key):
                code, result = self.run_workflow(self.generic_charge(**key))
                self.assertEqual(code, 1)
                self.assertIn("missing-idempotency-key", rules(result))
                self.assertNotIn("static-idempotency-key", rules(result))

    def test_same_templated_key_in_n8n_is_still_static(self) -> None:
        # n8n evaluates only `={{ }}`; `${order.id}` there is sent as literal text.
        wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
        wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = "${order.id}"
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("static-idempotency-key", rules(result))

    def test_scoped_and_custom_n8n_node_types_keep_n8n_checks(self) -> None:
        # An export built only from @n8n/n8n-nodes-langchain (or a scoped community or
        # CUSTOM.* node) is still n8n; treating it as generic silently skipped key checks.
        for node_type in ("@n8n/n8n-nodes-langchain.toolHttpRequest",
                          "@acme/n8n-nodes-payments.charge", "CUSTOM.chargeCard"):
            with self.subTest(node_type=node_type):
                wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
                for node in wf["nodes"]:
                    node["type"] = node_type
                wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0]["value"] = "static-key-123"
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 1)
                self.assertIn("static-idempotency-key", rules(result))

    def test_invalid_json_is_input_error(self) -> None:
        tmp = FIXTURES.parent / "_tmp_invalid.json"
        tmp.write_text("{not json")
        try:
            code, result = run(tmp)
        finally:
            tmp.unlink()
        self.assertEqual(code, 2)
        self.assertIn("error", result)


def fixture(**header: object) -> dict:
    wf = json.loads((FIXTURES / "n8n_http_idempotent.json").read_text())
    wf["nodes"][0]["parameters"]["headerParameters"]["parameters"][0].update(header)
    return wf


def with_node(node: dict) -> dict:
    wf = fixture()
    wf["nodes"].insert(0, node)
    return wf


class Helpers(unittest.TestCase):
    run_workflow = N8nFixtureTests.run_workflow
    generic_charge = N8nFixtureTests.generic_charge


class N8nKeyScopeTests(Helpers):
    """A key must collapse retries and redeliveries of one item, and nothing else."""

    def test_execution_scoped_key_is_not_item_data(self) -> None:
        # One key per execution: N items collapse to one effect, and a redelivered webhook
        # (a new execution) gets a new key. Fails if `execution` returns to the item-data set.
        for value in ("={{ $execution.id }}", "={{ $execution.id + '-' + $runIndex }}"):
            with self.subTest(value=value):
                code, result = self.run_workflow(fixture(value=value))
                self.assertEqual(code, 1)
                self.assertEqual(rules(result), {"static-idempotency-key"})

    def test_batch_level_accessors_are_not_item_data(self) -> None:
        # .first()/.last()/.all()[n] return the same item for every item in the batch.
        for value in ("={{ $input.first().json.id }}", "={{ $input.last().json.id }}",
                      "={{ $input.all()[0].json.id }}", "={{ $('Webhook').first().json.id }}"):
            with self.subTest(value=value):
                code, result = self.run_workflow(fixture(value=value))
                self.assertEqual(code, 1)
                self.assertIn("static-idempotency-key", rules(result))

    def test_item_key_mixed_with_volatile_component_fails(self) -> None:
        # Reading item data is not enough: a per-attempt or batch-level part makes every
        # retry a new key, so the provider never deduplicates.
        for value in ("={{ $json.id + Date.now() }}", "={{ $json.id + new Date().getTime() }}",
                      "={{ $json.id + Math.random() }}", "={{ $json.id + $now }}",
                      "={{ $json.id }}-{{ $today }}", "={{ $json.id + $runIndex }}",
                      "={{ $json.id + $execution.id }}", "={{ $json.id + $input.first().json.x }}",
                      "={{ $json.id + $items('Webhook')[0].json.x }}"):
            with self.subTest(value=value):
                code, result = self.run_workflow(fixture(value=value))
                self.assertEqual(code, 1)
                self.assertEqual(rules(result), {"unstable-idempotency-key"})

    def test_clock_and_random_helpers_are_volatile(self) -> None:
        for value in ("={{ $json.id }}-{{ DateTime.now().toMillis() }}", "={{ $json.id + DateTime.local() }}",
                      "={{ $json.id + DateTime.utc() }}", "={{ $json.id + crypto.randomUUID() }}",
                      "={{ $json.id ? crypto.randomUUID() : '' }}", "={{ $json.id + Date() }}",
                      "={{ $json.id + performance.now() }}"):
            with self.subTest(value=value):
                code, result = self.run_workflow(fixture(value=value))
                self.assertEqual(code, 1)
                self.assertEqual(rules(result), {"unstable-idempotency-key"})

    def test_batch_key_message_points_to_item(self) -> None:
        code, result = self.run_workflow(fixture(value="={{ $('Webhook').first().json.id }}"))
        self.assertIn(".item", " ".join(i["message"] for i in result["issues"]))


class N8nSideEffectScopeTests(Helpers):
    """Only nodes that change external state are side effects."""

    WEBHOOK = {"id": "t1", "name": "Webhook", "type": "n8n-nodes-base.webhook",
               "parameters": {"path": "orders", "httpMethod": "POST"}}

    def test_post_webhook_trigger_without_key_is_clean(self) -> None:
        # httpMethod on a Webhook is the inbound request it accepts, not an outbound POST;
        # triggers have no retry setting, so flagging them was an error nobody could fix.
        for node in (self.WEBHOOK,
                     {"id": "t2", "name": "Form", "type": "n8n-nodes-base.formTrigger", "parameters": {}},
                     {"id": "t3", "name": "Run", "type": "n8n-nodes-base.manualTrigger", "parameters": {}},
                     {"id": "t4", "name": "Stripe events", "type": "n8n-nodes-base.stripeTrigger",
                      "parameters": {"events": ["charge.succeeded"]}},
                     {"id": "t5", "name": "Custom", "type": "@acme/n8n-nodes-x.OrderTRIGGER", "parameters": {}}):
            for extra in ((), ("--strict",)):
                with self.subTest(node=node["type"], extra=extra):
                    code, result = self.run_workflow(with_node(node), *extra)
                    self.assertEqual(result["issues"], [])
                    self.assertEqual(code, 0)

    def test_postgres_reads_are_clean(self) -> None:
        # "post" must not match inside "postgres"; an explicit read changes nothing.
        for params in ({"operation": "executeQuery", "query": "select 1"},
                       {"operation": "executeQuery", "query": "=  SELECT * FROM orders WHERE id = {{ $json.id }}"},
                       {"operation": "select", "table": "orders"}, {"operation": "getAll"}):
            with self.subTest(params=params):
                node = {"id": "q1", "name": "Load orders", "type": "n8n-nodes-base.postgres", "parameters": params}
                code, result = self.run_workflow(with_node(node))
                self.assertEqual(result["issues"], [])
                self.assertEqual(code, 0)

    def test_postgres_writes_are_still_side_effects(self) -> None:
        # A DB node cannot carry a key, so the finding is a DB-write warning, not a key error.
        # n8n omits default values, so a node with no operation is an unknown write.
        for params in ({"operation": "insert", "table": "orders"}, {"operation": "update", "table": "orders"},
                       {"operation": "executeQuery", "query": "UPDATE orders SET paid = true"},
                       {"operation": "executeQuery", "query": "SELECT 1; DELETE FROM orders"},
                       {"table": "orders"}):
            with self.subTest(params=params):
                node = {"id": "q1", "name": "Load orders", "type": "n8n-nodes-base.postgres", "parameters": params}
                code, result = self.run_workflow(with_node(node))
                self.assertEqual(code, 1)
                self.assertEqual(rules(result), {"non-idempotent-db-write", "missing-retry-policy"})
                self.assertEqual({i["severity"] for i in result["issues"]}, {"warning"})
                code, result = self.run_workflow(with_node(node), "--fail-on", "error")
                self.assertEqual(code, 0)

    def test_idempotent_db_writes_are_clean(self) -> None:
        # These are static candidates; business-key uniqueness and triggers need review.
        for params in ({"operation": "upsert", "table": "orders"}, {"operation": "upsert"},
                       {"operation": "executeQuery", "query": "INSERT INTO t VALUES (1) ON CONFLICT DO NOTHING"},
                       {"operation": "executeQuery", "query": "MERGE INTO t USING s ON t.id = s.id"},
                       {"operation": "executeQuery", "query": "INSERT IGNORE INTO t VALUES (1)"},
                       {"operation": "executeQuery", "query": "INSERT INTO t VALUES (1) ON DUPLICATE KEY UPDATE n = 1"},
                       {"operation": "executeQuery", "query": "INSERT INTO t VALUES (1) ON CONFLICT (id) DO UPDATE SET n = excluded.n"},
                       {"operation": "executeQuery", "query": "MERGE INTO t USING s ON t.id = s.id WHEN MATCHED THEN UPDATE SET n = s.n"},
                       {"operation": "executeQuery", "query": "WITH x AS (SELECT 1) SELECT * FROM x"}):
            for retry in ({}, {"retryOnFail": True, "maxTries": 3}):
                with self.subTest(params=params, retry=retry):
                    wf = {"nodes": [dict({"id": "q1", "name": "Postgres", "type": "n8n-nodes-base.postgres",
                                          "parameters": params}, **retry)], "connections": {}}
                    code, result = self.run_workflow(wf)
                    self.assertEqual(result["issues"], [])
                    self.assertEqual(code, 0)

    def test_conflict_update_increment_is_not_idempotent(self) -> None:
        for query in (
            "INSERT INTO t VALUES (1) ON CONFLICT (id) DO UPDATE SET n = n + 1",
            "INSERT INTO t VALUES (1) ON CONFLICT (id) DO UPDATE SET n = 1 + t.n",
            'INSERT INTO t VALUES (1) ON CONFLICT (id) DO UPDATE SET "n" = t."n" + 1',
            "MERGE INTO t USING s ON t.id = s.id WHEN MATCHED THEN UPDATE SET n = t.n + 1",
            "INSERT INTO t VALUES (1) ON DUPLICATE KEY UPDATE n = n + 1",
            "INSERT INTO t VALUES (1) ON CONFLICT (id) DO UPDATE SET n = random()",
            "INSERT INTO t VALUES (1) ON CONFLICT DO NOTHING; UPDATE t SET n = n + 1",
        ):
            with self.subTest(query=query):
                wf = {"nodes": [{"id": "q1", "name": "DB", "type": "n8n-nodes-base.postgres",
                                 "parameters": {"operation": "executeQuery", "query": query}}]}
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 1)
                self.assertIn("non-idempotent-db-write", rules(result))

    def test_app_node_write_operations_are_side_effects(self) -> None:
        # n8n keeps the operation under `parameters`; a retried Stripe charge with no key
        # passed clean even with --strict.
        for node_type, params in (("n8n-nodes-base.stripe", {"resource": "charge", "operation": "create"}),
                                  ("n8n-nodes-base.slack", {"resource": "message", "operation": "post"}),
                                  ("n8n-nodes-base.gmail", {"operation": "send"}),
                                  ("n8n-nodes-base.hubspot", {"resource": "deal", "operation": "upsert"})):
            for extra in ((), ("--strict",)):
                with self.subTest(node_type=node_type, extra=extra):
                    wf = {"nodes": [{"id": "s1", "name": "Step", "type": node_type, "parameters": params,
                                     "retryOnFail": True, "maxTries": 5}], "connections": {}}
                    code, result = self.run_workflow(wf, *extra)
                    self.assertEqual(code, 1)
                    self.assertIn("missing-idempotency-key", rules(result))
                    self.assertIn("sync-side-effect-without-dlq", rules(result))
        # More write verbs seen in real exports.
        for node_type, op in (("n8n-nodes-base.googleSheets", "append"), ("n8n-nodes-base.googleDrive", "upload"),
                              ("n8n-nodes-base.gmail", "reply"), ("n8n-nodes-base.redis", "publish"),
                              ("n8n-nodes-base.redis", "incr"), ("n8n-nodes-base.redis", "push"),
                              ("n8n-nodes-base.awsS3", "upload"), ("n8n-nodes-base.googleDrive", "move"),
                              ("n8n-nodes-base.googleDrive", "copy"), ("n8n-nodes-base.googleDrive", "share"),
                              ("n8n-nodes-base.slack", "invite"), ("n8n-nodes-base.slack", "archive"),
                              ("n8n-nodes-base.redis", "decr")):
            with self.subTest(node_type=node_type, op=op):
                wf = {"nodes": [{"id": "s1", "name": "Step", "type": node_type, "parameters": {"operation": op}}],
                      "connections": {}}
                code, result = self.run_workflow(wf)
                self.assertEqual(code, 1)
                self.assertIn("missing-idempotency-key", rules(result))
        # Core nodes transform items inside the workflow; their operations are not writes.
        for node_type, op in (("n8n-nodes-base.itemLists", "removeDuplicates"),
                              ("n8n-nodes-base.dateTime", "addToDate")):
            with self.subTest(node_type=node_type):
                code, result = self.run_workflow(with_node(
                    {"id": "c1", "name": "Tidy", "type": node_type, "parameters": {"operation": op}}))
                self.assertEqual(result["issues"], [])

    def test_http_v1_request_method_is_read(self) -> None:
        wf = fixture()
        params = wf["nodes"][0]["parameters"]
        params.pop("headerParameters")
        params["requestMethod"] = params.pop("method")
        wf["nodes"][0]["typeVersion"] = 1
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("missing-idempotency-key", rules(result))

    def test_dlq_target_is_not_linted_but_same_write_elsewhere_is(self) -> None:
        # The fixture's DLQ is a Redis push reached only through the error output: storing a
        # failed item twice is harmless. The same push on the normal path is a write.
        code, result = self.run_workflow(fixture())
        self.assertEqual(result["issues"], [])
        wf = fixture()
        wf["connections"]["Create order"]["main"] = [[{"node": "Dead letter queue", "type": "main", "index": 0}],
                                                     [{"node": "Dead letter queue", "type": "main", "index": 0}]]
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("dlq1", {i["step_id"] for i in result["issues"] if i["rule"] == "missing-idempotency-key"})

    def test_fallback_write_on_error_path_is_still_linted(self) -> None:
        # Only a DLQ-named error target is skipped: a fallback charge reached through the
        # error output is a billing write like any other.
        wf = fixture()
        wf["nodes"][1].update(name="Fallback charge", type="n8n-nodes-base.httpRequest",
                              parameters={"method": "POST", "url": "https://pay.example/charge"})
        wf["connections"]["Create order"]["main"][1][0]["node"] = "Fallback charge"
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("missing-idempotency-key", rules(result))

    def test_respond_to_webhook_is_not_a_side_effect(self) -> None:
        node = {"id": "r1", "name": "Respond to Webhook", "type": "n8n-nodes-base.respondToWebhook", "parameters": {}}
        code, result = self.run_workflow(with_node(node))
        self.assertEqual(result["issues"], [])
        self.assertEqual(code, 0)

    def test_n8n_dlq_field_without_error_route_does_not_count(self) -> None:
        # In n8n only the connected error output routes failures; a `dlq` field routes nothing.
        wf = fixture()
        wf["nodes"][0]["dlq"] = "orders-dead-letter"
        wf["nodes"][1].update(name="Nothing", type="n8n-nodes-base.noOp")
        wf["connections"]["Create order"]["main"][1][0]["node"] = "Nothing"
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("sync-side-effect-without-dlq", rules(result))

    def test_noop_named_dlq_does_not_count(self) -> None:
        # A No-Op node named "Dead letter queue" stores nothing; fails if the noOp exclusion goes.
        wf = fixture()
        wf["nodes"][1]["type"] = "n8n-nodes-base.noOp"
        code, result = self.run_workflow(wf)
        self.assertEqual(code, 1)
        self.assertIn("sync-side-effect-without-dlq", rules(result))


class InputAndKeyValueTests(Helpers):
    def test_array_of_workflows_is_linted_per_workflow(self) -> None:
        # A multi-workflow export is an array of workflow objects, not an array of steps.
        bad = json.loads((FIXTURES / "n8n_http_missing_key.json").read_text())
        good = fixture()
        code, result = self.run_workflow([good, bad])
        self.assertEqual(code, 1)
        self.assertIn("missing-idempotency-key", rules(result))
        self.assertEqual({issue["workflow"] for issue in result["issues"]}, {bad["name"]})
        # A bare step array is still one workflow.
        code, result = self.run_workflow([{"id": "charge", "type": "http", "method": "POST"}])
        self.assertEqual(code, 1)
        self.assertIn("missing-idempotency-key", rules(result))

    def test_non_workflow_input_is_input_error(self) -> None:
        # Empty workflows included: with nothing to lint, --fail-on error would pass anything.
        for data in ([], {}, "workflow", 42, None, {"data": [fixture()]}, [1, 2], {"nodes": []},
                     [{"nodes": []}], {"steps": [1]}):
            with self.subTest(data=data):
                code, result = self.run_workflow(data)
                self.assertEqual(code, 2)
                self.assertIn("error", result)
                code, result = self.run_workflow(data, "--fail-on", "error")
                self.assertEqual(code, 2)

    def test_generic_shape_regressions(self) -> None:
        # A group step with its own `steps` inside a bare step array is still a step.
        group = [{"id": "charge", "method": "POST", "idempotency_key": "order.id",
                  "retry_policy": {"max_attempts": 3}, "dlq": "q"},
                 {"id": "fanout", "type": "parallel", "steps": [{"id": "x"}]}]
        code, result = self.run_workflow(group)
        self.assertEqual((code, result["issues"]), (0, []))
        # Lower-case compound ids still start with a verb; "postgres" still is not "post".
        for step_id, flagged in (("sendgrid", True), ("createorder", True), ("postgresql-read", False),
                                  ("format_postal", False), ("postprocess", False)):
            with self.subTest(step_id=step_id):
                code, result = self.run_workflow({"steps": [{"id": step_id, "type": step_id}]})
                self.assertEqual("missing-retry-policy" in rules(result), flagged)
        # One empty workflow in a batch is reported, not an input error.
        code, result = self.run_workflow([{"name": "draft", "nodes": []}, fixture()])
        self.assertEqual(rules(result), {"no-steps-found"})

    def test_generic_empty_key_values_do_not_count(self) -> None:
        for key in ({"idempotency_key": None}, {"idempotency_key": ""}, {"idempotency_key": False},
                    {"idempotency_key": "   "},
                    {"parameters": {"headers": [{"name": "Idempotency-Key", "value": ""}]}}):
            with self.subTest(key=key):
                code, result = self.run_workflow(self.generic_charge(**key))
                self.assertEqual(code, 1)
                self.assertIn("missing-idempotency-key", rules(result))

    def test_provider_key_header_names(self) -> None:
        # Any header name containing "idempotency", plus PayPal-Request-Id.
        for name in ("X-Idempotency-Key", "PayPal-Request-Id", "idempotency-token"):
            with self.subTest(name=name):
                code, result = self.run_workflow(fixture(name=name))
                self.assertEqual(result["issues"], [])
                self.assertEqual(code, 0)
                code, result = self.run_workflow(fixture(name=name, value="constant-key"))
                self.assertIn("static-idempotency-key", rules(result))

    def test_fail_on_threshold(self) -> None:
        # Default keeps the old gate (any issue exits 1); --fail-on error lets warnings pass.
        warning_only = fixture()
        warning_only["nodes"][1]["type"] = "n8n-nodes-base.noOp"
        missing = json.loads((FIXTURES / "n8n_http_missing_key.json").read_text())
        for wf, extra, expected in ((warning_only, (), 1), (warning_only, ("--fail-on", "warning"), 1),
                                    (warning_only, ("--fail-on", "error"), 0),
                                    (missing, ("--fail-on", "error"), 1),
                                    (warning_only, ("--strict", "--fail-on", "error"), 0)):
            with self.subTest(extra=extra, expected=expected):
                code, result = self.run_workflow(wf, *extra)
                self.assertEqual(code, expected)
                self.assertTrue(result["issues"])


if __name__ == "__main__":
    unittest.main()
