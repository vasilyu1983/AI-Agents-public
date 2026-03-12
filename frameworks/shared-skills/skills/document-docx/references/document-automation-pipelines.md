# Document Automation Pipelines

CI/CD and batch automation for DOCX generation. Architecture, pipeline integration, template versioning, quality gates, error handling, and a GitHub Actions example.

## Contents

- Pipeline Architecture
- Template Versioning
- Data Sources and Batch Generation
- Quality Gates
- Error Handling
- GitHub Actions Workflow
- Do / Avoid

---

## Pipeline Architecture

```text
  Template (.docx, git-tracked)
       ↓
  Data Source (JSON / CSV / API / DB)
       ↓
  Renderer (docxtpl / python-docx)
       ↓
  Quality Gates (size, parse, unresolved vars)
       ↓
  Output (.docx, optional .pdf)
```

Templates are design artifacts in git. Data is injected at render time. Output is validated before delivery.

---

## Template Versioning

DOCX files are binary -- diffs are not human-readable. Store in `templates/`, name with version (`invoice-v3.docx`), use Git LFS for files > 500KB, never edit outside the repo.

```bash
git lfs track "templates/*.docx"
```

Validate template variables before render:

```python
from docxtpl import DocxTemplate

def validate_template(path: str, expected: list[str]) -> list[str]:
    declared = DocxTemplate(path).get_undeclared_template_variables()
    missing = [v for v in expected if v not in declared]
    return [f"Missing: {missing}"] if missing else []
```

---

## Data Sources and Batch Generation

| Source | Library | Use Case |
|--------|---------|----------|
| JSON | `json.load()` | Config-driven, small datasets |
| CSV | `csv.DictReader()` | Mail merge, tabular records |
| REST API | `requests` | Live CRM/ERP data |
| Database | `sqlalchemy` | Bulk reports from production |

```python
from docxtpl import DocxTemplate
from concurrent.futures import ProcessPoolExecutor
import os

def render_one(args):
    template_path, record, output_path = args
    doc = DocxTemplate(template_path)
    doc.render(record)
    doc.save(output_path)
    return output_path

def batch_parallel(template_path, records, output_dir, workers=4):
    os.makedirs(output_dir, exist_ok=True)
    tasks = [(template_path, r, f"{output_dir}/{r['id']}.docx") for r in records]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(render_one, tasks))
```

Each worker re-opens the template -- docxtpl is not thread-safe.

---

## Quality Gates

```python
import os, re
from docx import Document

def quality_gate(path: str, max_mb: float = 10.0) -> list[str]:
    fails = []
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return ['File missing or empty']
    if os.path.getsize(path) / 1_048_576 > max_mb:
        fails.append(f'Exceeds {max_mb}MB limit')
    try:
        doc = Document(path)
    except Exception as e:
        return [f'Corrupted: {e}']
    unresolved = re.findall(r'\{\{.*?\}\}', '\n'.join(p.text for p in doc.paragraphs))
    if unresolved:
        fails.append(f'Unresolved variables: {unresolved}')
    return fails
```

Checklist: file exists and size > 0, within size budget, parses without error, no unresolved `{{ variables }}`, PDF conversion succeeds if required.

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError` | Wrong template path | Validate path before batch loop |
| Jinja2 `UndefinedError` | Missing context variable | Pre-check with `get_undeclared_template_variables()` |
| Corrupted output | Broken template XML or bad input chars | Validate template; sanitize input data |
| Font not found in PDF step | CI image missing the font | Install fonts in Dockerfile or use Arial |
| CI timeout | Large batch or slow PDF conversion | Parallelize; split batches; increase timeout |

---

## GitHub Actions Workflow

```yaml
name: Generate Documents
on:
  workflow_dispatch:
    inputs:
      data_file: { description: 'JSON data file', required: true, default: 'data/clients.json' }
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { lfs: true }
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install python-docx docxtpl
      - run: sudo apt-get install -y libreoffice-writer
      - run: python scripts/generate_batch.py --template templates/invoice.docx --data ${{ github.event.inputs.data_file }} --output output/
      - run: python scripts/quality_gate.py --dir output/
      - uses: actions/upload-artifact@v4
        with: { name: generated-documents, path: output/, retention-days: 30 }
```

---

## Do / Avoid

| Do | Avoid |
|----|-------|
| Version templates in git (LFS for large files) | Editing templates outside the repo |
| Validate template variables before batch runs | Discovering missing vars mid-batch |
| Run quality gates on every generated file | Assuming render success = correct output |
| Use ProcessPoolExecutor for large batches | Sharing DocxTemplate across threads |
| Install fonts in CI Docker image | Relying on fonts that differ local vs CI |
| Sanitize input data (strip control chars) | Passing raw API output into templates |

---

## Related Resources

- [template-workflows.md](template-workflows.md) - docxtpl patterns and mail merge
- [cross-platform-compatibility.md](cross-platform-compatibility.md) - Rendering and conversion
- [accessibility-compliance.md](accessibility-compliance.md) - Accessible output
- [SKILL.md](../SKILL.md) - Parent DOCX skill
