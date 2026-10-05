#!/usr/bin/env python3
"""Regression: build_vector_hub.sh produces the infra-free artifact set + a valid manifest."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SCRIPT = HERE / "build_vector_hub.sh"
CHECK = HERE / "check_brain_manifest.py"


def test_build_vector_hub_emits_artifacts_and_valid_manifest():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        hub = tmp / "hub"
        (hub / "sub").mkdir(parents=True)
        (hub / "index.md").write_text("# Title\n\nIntro text.\n\n## Section\n\nBody.\n")
        (hub / "sub" / "page.md").write_text("# Page\n\nContent here.\n")
        out = tmp / "out"

        subprocess.run(["bash", str(SCRIPT), str(hub), str(out)], check=True,
                        capture_output=True, text=True)

        for name in ("inventory.jsonl", "documents.jsonl", "chunks.jsonl", "brain-manifest.json"):
            assert (out / name).exists(), f"missing {name}"

        chunks = [l for l in (out / "chunks.jsonl").read_text().splitlines() if l.strip()]
        assert chunks, "chunks.jsonl is empty"

        docs = [json.loads(l) for l in (out / "documents.jsonl").read_text().splitlines() if l.strip()]
        assert docs and isinstance(docs[0]["metadata"], dict)
        assert docs[0]["corpus_type"] == "docs"

        r = subprocess.run([sys.executable, str(CHECK), str(out / "brain-manifest.json")],
                            capture_output=True, text=True)
        assert r.returncode == 0, f"manifest invalid: {r.stdout}{r.stderr}"

        # The manifest chunking block must describe what chunk_markdown.py
        # actually does, not a fictional sliding window. The splitter measures
        # words and uses parent-child for context; it has no overlap parameter.
        ch = json.loads((out / "brain-manifest.json").read_text())["chunking"]
        assert ch["max_tokens"] == 512, ch
        assert "overlap_tokens" not in ch, "chunk_markdown.py has no sliding overlap — do not claim one"
        assert ch["token_unit"] == "word_estimate", ch
        assert "parent-child" in ch["context"], ch
        assert "line-bounded" in ch["context"], ch


def test_build_vector_hub_indexes_repo_artifacts_without_markdown():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        hub = tmp / "repo"
        hub.mkdir()
        (hub / "repo-profile.json").write_text('{"repo":"api","owner":"platform"}\n')
        (hub / "service.ts").write_text("export function handler() { return 'ok' }\n")
        out = tmp / "out"

        subprocess.run(["bash", str(SCRIPT), str(hub), str(out), "repo-hub", "repo"], check=True,
                        capture_output=True, text=True)

        chunks = [json.loads(l) for l in (out / "chunks.jsonl").read_text().splitlines() if l.strip()]
        assert {c["source_path"] for c in chunks} == {"repo-profile.json", "service.ts"}
        assert all(c["citation_anchor"].startswith(c["source_path"]) for c in chunks)
        docs = [json.loads(l) for l in (out / "documents.jsonl").read_text().splitlines() if l.strip()]
        assert {d["doc_type"] for d in docs} == {"structured", "code"}
        assert all(d["corpus_type"] == "repo" for d in docs)


def test_build_vector_hub_fails_loud_on_no_indexable_files():
    with tempfile.TemporaryDirectory() as tmp:
        hub = Path(tmp) / "empty"
        hub.mkdir()
        r = subprocess.run(["bash", str(SCRIPT), str(hub), str(Path(tmp) / "out")],
                            capture_output=True, text=True)
        assert r.returncode != 0, "should fail when no markdown files exist"


if __name__ == "__main__":
    test_build_vector_hub_emits_artifacts_and_valid_manifest()
    test_build_vector_hub_indexes_repo_artifacts_without_markdown()
    test_build_vector_hub_fails_loud_on_no_indexable_files()
    print("ok")
