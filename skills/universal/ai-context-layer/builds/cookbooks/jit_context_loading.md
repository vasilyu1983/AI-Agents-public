# Cookbook: Just-In-Time Context Loading

This is the build recipe for P12.

## Core rule

Carry refs in the request. Load artifacts only after selection.

## Minimal implementation

- Add `ContextRef` and `ArtifactRef` to the request.
- Add a `ReferenceResolver` that turns refs into evidence, live facts, and artifact refs.
- Add an `ArtifactLoader` that turns artifact refs into `LoadedArtifact`.
- Project loaded artifacts into compact typed views before compression.

## Use this for

- large documents
- screenshots / OCR surfaces
- dashboard and report assistants
- file-heavy coding or research flows

## Do not do this

- load the whole candidate set "just in case"
- inline raw file payloads in the bundle
- allow a generic artifact loader on every surface

## Verification

- only requested refs are resolved
- only selected artifacts are loaded
- `source_ref_id` and `evidence_id` survive formatting and compression
