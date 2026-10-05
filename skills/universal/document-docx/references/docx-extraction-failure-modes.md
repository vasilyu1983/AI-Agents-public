# DOCX Extraction Failure Modes For KB/RAG Ingestion

Load this when a DOCX feeds an index or knowledge base and any table, revision or filename could carry facts. Tool choice lives in [llm-extraction-workflows.md](llm-extraction-workflows.md); this file holds the silent-loss modes and their detection.

Evidence level: the python-docx API docs state that `Document.tables` lists only top-level tables (a table nested in a cell is not listed) and that `iter_inner_content()` yields body-level paragraphs and tables. They do not mention content controls. The content-control loss below was observed in a real corpus (a large share of its files were affected), so treat the detection check as the proof, not the docs.

## Detection check (run per file, before trusting the text)

Compare tables in the XML with tables python-docx returns. Count only top-level `w:tbl` (not nested in another `w:tbl`), because `Document.tables` skips nested ones.

```bash
python3 - in.docx <<'PY'
import sys, zipfile, xml.etree.ElementTree as ET
import docx
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SKIP = {"{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback", W + "txbxContent"}  # duplicates / text boxes
root = ET.fromstring(zipfile.ZipFile(sys.argv[1]).read("word/document.xml"))
def top(node, inside=False):
    n = 0
    for c in node:
        if c.tag in SKIP:
            continue
        if c.tag == W + "tbl":
            n += 0 if inside else 1
            n += top(c, True)
        else:
            n += top(c, inside)
    return n
xml_n, api_n = top(root), len(docx.Document(sys.argv[1]).tables)
print(f"xml_top_level_tables={xml_n} python_docx_tables={api_n}", "MISMATCH" if xml_n != api_n else "ok")
PY
```

A mismatch means tables were dropped (usually in content controls). Do not index that file until fixed.

## Failure modes

| Mode | Symptom | Handling |
|---|---|---|
| Tables inside content controls (`w:sdt` / `w:sdtContent`) | `Document.tables` and body-child iteration miss them; text silently absent | Descend the body XML recursively for every `w:tbl` (iterate all descendants, not only direct body children), convert each to rows, and keep document order. Re-run the detection check on the output |
| Tables pasted as images | No text exists; OCR of table images is unreliable | Flag the file and the page; do not index as authoritative. OCR output only as non-authoritative text marked `ocr`, never as the source of a number or a date |
| Tracked changes (`w:ins`, `w:del`) | Converters drop insertions or merge inserted and deleted text with no marker | Count revisions with `scripts/docx_inspect_ooxml.py`; if non-zero, set the policy explicitly: index the accepted text, or the original, and record which in metadata. Never mix |
| Embedded base64 / inline images | Bloated Markdown and index; images carry text the extractor ignores | Extract images to files, replace with a placeholder plus path, and check each for text (a table image falls under the row above) |
| Filenames and extensions that lie | A `.docx` that is a PDF, an old `.doc`, or a different document than its title | Check magic bytes before parsing (a DOCX is a ZIP: leading `PK`; legacy `.doc` is an OLE file) and compare title against body opening text; quarantine on mismatch |

## Gate

Per file, record: detection-check result, revision count and chosen policy, image-table count, magic-byte result. Ingest only files with no unexplained mismatch; list the rest as held out rather than indexed.

OOXML references to verify structure names: ECMA-376 / ISO 29500, Part 1, `w:sdt`, `w:sdtContent`, `w:ins`, `w:del`. Not fetched in this session; confirm element semantics against the spec before relying on edge cases.
