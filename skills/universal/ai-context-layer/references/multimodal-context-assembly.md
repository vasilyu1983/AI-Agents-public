# Multimodal Context Assembly

Multimodal context layers fail when teams treat every modality as just "more
text to stuff into the prompt." The durable pattern is:

- pointers in the request
- typed projections in the bundle
- full payloads outside the model window unless explicitly needed

## Minimal contract set

- `ContextRef` for runtime pointers
- `ArtifactRef` for large or multimodal assets
- `LoadedArtifact` for typed, provenance-bearing payloads after load
- `ContextAssemblyRequest` and `ContextBundle` for per-surface budgets

## Assembly rules

- Documents: keep title, source ref, page or evidence id, and a short excerpt
- Images/screenshots: keep OCR or alt-style summary plus metadata like size
- Tool outputs: project only fields the current step needs
- Dashboards/tables: project metrics and dimensions, not full export payloads

## Budgeting

- Text tokens remain the hard bundle ceiling
- Artifact count is capped separately
- Inline artifact chars are capped separately from the original payload size
- Heavy artifact inspection can move to a sub-agent (P11)

## Failure checks

- A5 blocked: no monolithic multimodal prompt stuffing
- A23 blocked: OCR/text from artifacts is tagged as data, not instruction
- A29 blocked: raw file payloads do not enter the bundle

## Good fit

- Design review
- File-heavy research
- Workspace copilots
- Coding agents with logs, screenshots, and diffs
