"""Offline regressions for full-list dashboard writes; no Metabase connection."""
import argparse
import importlib.util
import json
import os
from pathlib import Path

import pytest


script = Path(os.environ.get("METABASE_TEST_MODULE", Path(__file__).with_name("metabase_api.py")))
spec = importlib.util.spec_from_file_location("metabase_api_under_test", script)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


@pytest.mark.parametrize("dashcards", [None, {}, "bad", [None], [{"card_id": 1}],
                                     [{"id": True}], [{"id": 0}], [{"id": -1}],
                                     [{"id": 1}, {"id": 1}],
                                     [{"id": 1, "series": [{"name": "missing id"}]}]])
def test_add_rejects_incomplete_dashboard_before_write(monkeypatch, tmp_path, dashcards):
    calls = []

    def request(method, path, body=None):
        calls.append(method)
        return "mock", 200, {"dashcards": dashcards}, b"", "application/json"

    monkeypatch.setattr(api, "_authed_request", request)
    placement = tmp_path / "placement.json"
    placement.write_text(json.dumps({"card_id": 2, "size_x": 4, "size_y": 3, "row": 0, "col": 0}))
    with pytest.raises(SystemExit):
        api.cmd_add_dashcard(argparse.Namespace(spec=str(placement), dashboard_id=5, dry_run=False))
    assert calls == ["GET"]


def test_missing_dashcards_key_is_not_an_empty_dashboard(monkeypatch):
    monkeypatch.setattr(api, "_authed_request", lambda *args: ("mock", 200, {}, b"", "application/json"))
    with pytest.raises(SystemExit):
        api._fetch_dashcards(5)


@pytest.mark.parametrize("ids", [[True], [0], ["1"], [1, 1], [-1, -1]])
def test_replace_rejects_invalid_ids_before_any_request(monkeypatch, tmp_path, ids):
    calls = []

    def request(*args):
        calls.append(args)
        return "mock", 200, {"dashcards": []}, b"", "application/json"

    monkeypatch.setattr(api, "_authed_request", request)
    layout = tmp_path / "layout.json"
    layout.write_text(json.dumps([{"id": value} for value in ids]))
    with pytest.raises(SystemExit):
        api.cmd_update_dashcards(argparse.Namespace(spec=str(layout), dashboard_id=5, dry_run=False, replace=True))
    assert calls == []


def test_add_preserves_existing_series_and_layout(monkeypatch, tmp_path):
    existing = {"id": 8, "row": 2, "col": 0, "size_x": 4, "size_y": 3,
                "dashboard_tab_id": 2, "parameter_mappings": [{"parameter_id": "filter"}],
                "series": [{"id": 9, "name": "hydrated card"}]}
    writes = []

    def request(method, path, body=None):
        if method == "GET":
            return "mock", 200, {"dashcards": [existing]}, b"", "application/json"
        writes.append(body)
        return "mock", 200, body, b"", "application/json"

    monkeypatch.setattr(api, "_authed_request", request)
    placement = tmp_path / "placement.json"
    placement.write_text(json.dumps({"card_id": 2, "size_x": 4, "size_y": 3, "row": 0, "col": 0}))
    api.cmd_add_dashcard(argparse.Namespace(spec=str(placement), dashboard_id=5, dry_run=False))
    assert writes[0]["dashcards"][0] == {**existing, "series": [{"id": 9}]}
    assert writes[0]["dashcards"][1]["id"] == -1


def test_explicit_empty_dashboard_is_valid(monkeypatch):
    monkeypatch.setattr(api, "_authed_request", lambda *args: ("mock", 200, {"dashcards": []}, b"", "application/json"))
    assert api._fetch_dashcards(5) == []
