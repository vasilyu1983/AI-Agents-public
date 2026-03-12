# Template Workflows

Mail merge, batch generation, and document automation patterns.

## Contents

- Template-Based Generation
- docxtpl Basics
- Mail Merge Patterns
- Batch Generation
- Advanced Template Features
- Workflow Automation
- Error Handling
- Related Resources

## Template-Based Generation

### Why Use Templates?

| Approach | Pros | Cons |
|----------|------|------|
| **Pure python-docx** | Full control, dynamic structure | More code, harder to maintain |
| **docxtpl templates** | Visual design in Word, simple code | Less dynamic, template constraints |
| **Hybrid** | Best of both | More complexity |

**Rule of thumb**: Use templates when non-developers need to maintain document design.

---

## docxtpl Basics

### Template Syntax

Templates use Jinja2 syntax inside Word documents:

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{ var }}` | Variable | `{{ customer_name }}` |
| `{% for item in items %}` | Loop | Iterate over list |
| `{% if condition %}` | Conditional | Show/hide sections |
| `{%p ... %}` | Paragraph-level | Whole paragraph conditional |
| `{%tr ... %}` | Table row | Loop over table rows |
| `{%tc ... %}` | Table cell | Loop over columns |

### Basic Template Fill

```python
from docxtpl import DocxTemplate

doc = DocxTemplate("invoice_template.docx")

context = {
    'invoice_number': 'INV-2025-001',
    'customer_name': 'Acme Corporation',
    'date': '2025-01-15',
    'items': [
        {'description': 'Consulting Services', 'hours': 40, 'rate': 150, 'total': 6000},
        {'description': 'Development', 'hours': 80, 'rate': 125, 'total': 10000},
    ],
    'subtotal': 16000,
    'tax': 1600,
    'total': 17600,
}

doc.render(context)
doc.save('invoice_INV-2025-001.docx')
```

### Template File Structure

In Word, create `invoice_template.docx`:

```text
                    INVOICE

Invoice #: {{ invoice_number }}
Date: {{ date }}
Customer: {{ customer_name }}

┌─────────────────────────────────────────────────┐
│ Description      │ Hours │ Rate   │ Total       │
├─────────────────────────────────────────────────┤
│{%tr for item in items %}                        │
│ {{ item.description }} │ {{ item.hours }} │ ${{ item.rate }} │ ${{ item.total }} │
│{%tr endfor %}                                   │
├─────────────────────────────────────────────────┤
│                  │       │ Subtotal: ${{ subtotal }} │
│                  │       │ Tax:      ${{ tax }}      │
│                  │       │ TOTAL:    ${{ total }}    │
└─────────────────────────────────────────────────┘
```

---

## Mail Merge Patterns

### Single-File Mail Merge

```python
from docxtpl import DocxTemplate
import json

# Load recipients
with open('recipients.json') as f:
    recipients = json.load(f)

# Generate personalized documents
for recipient in recipients:
    doc = DocxTemplate("letter_template.docx")
    doc.render(recipient)
    doc.save(f"letters/letter_{recipient['id']}.docx")
```

### recipients.json Structure

```json
[
  {
    "id": "001",
    "name": "John Smith",
    "company": "Acme Corp",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001"
  },
  {
    "id": "002",
    "name": "Jane Doe",
    "company": "Tech Inc",
    "address": "456 Oak Ave",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94102"
  }
]
```

### Mail Merge with CSV

```python
import csv
from docxtpl import DocxTemplate

def mail_merge_csv(template_path, csv_path, output_dir):
    """Generate documents from CSV data."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            doc = DocxTemplate(template_path)
            doc.render(row)

            # Generate unique filename
            filename = f"{output_dir}/{row.get('id', row.get('name', 'doc'))}.docx"
            doc.save(filename)
            print(f"Generated: {filename}")

# Usage
mail_merge_csv(
    template_path="contract_template.docx",
    csv_path="clients.csv",
    output_dir="contracts"
)
```

---

## Batch Generation

### Parallel Processing

```python
from docxtpl import DocxTemplate
from concurrent.futures import ProcessPoolExecutor
import os

def generate_document(args):
    """Generate single document (for parallel execution)."""
    template_path, context, output_path = args
    doc = DocxTemplate(template_path)
    doc.render(context)
    doc.save(output_path)
    return output_path

def batch_generate(template_path, contexts, output_dir, max_workers=4):
    """Generate multiple documents in parallel."""
    os.makedirs(output_dir, exist_ok=True)

    # Prepare arguments for each document
    tasks = [
        (template_path, ctx, f"{output_dir}/{ctx['filename']}.docx")
        for ctx in contexts
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(generate_document, tasks))

    return results

# Usage
contexts = [
    {'filename': 'report_q1', 'quarter': 'Q1', 'revenue': 1000000},
    {'filename': 'report_q2', 'quarter': 'Q2', 'revenue': 1200000},
    {'filename': 'report_q3', 'quarter': 'Q3', 'revenue': 1100000},
    {'filename': 'report_q4', 'quarter': 'Q4', 'revenue': 1500000},
]

generated = batch_generate("quarterly_template.docx", contexts, "reports")
print(f"Generated {len(generated)} documents")
```

### Progress Tracking

```python
from tqdm import tqdm
from docxtpl import DocxTemplate

def batch_generate_with_progress(template_path, contexts, output_dir):
    """Generate documents with progress bar."""
    os.makedirs(output_dir, exist_ok=True)

    for ctx in tqdm(contexts, desc="Generating documents"):
        doc = DocxTemplate(template_path)
        doc.render(ctx)
        doc.save(f"{output_dir}/{ctx['filename']}.docx")
```

---

## Advanced Template Features

### Conditional Sections

Template (`contract_template.docx`):

```text
{{ company_name }} Agreement

{%p if include_nda %}
CONFIDENTIALITY CLAUSE
This agreement includes non-disclosure provisions...
{%p endif %}

{%p if payment_terms == 'net30' %}
Payment is due within 30 days of invoice date.
{%p elif payment_terms == 'net60' %}
Payment is due within 60 days of invoice date.
{%p else %}
Payment is due upon receipt.
{%p endif %}
```

Python:

```python
context = {
    'company_name': 'Acme Corp',
    'include_nda': True,
    'payment_terms': 'net30',
}
```

### Nested Loops

Template:

```text
{% for department in departments %}
Department: {{ department.name }}

Employees:
{%tr for emp in department.employees %}
| {{ emp.name }} | {{ emp.role }} | {{ emp.email }} |
{%tr endfor %}

{% endfor %}
```

Python:

```python
context = {
    'departments': [
        {
            'name': 'Engineering',
            'employees': [
                {'name': 'Alice', 'role': 'Lead', 'email': 'alice@co.com'},
                {'name': 'Bob', 'role': 'Senior', 'email': 'bob@co.com'},
            ]
        },
        {
            'name': 'Sales',
            'employees': [
                {'name': 'Carol', 'role': 'Manager', 'email': 'carol@co.com'},
            ]
        },
    ]
}
```

### Images in Templates

```python
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

doc = DocxTemplate("report_template.docx")

# Add image to context
context = {
    'company_logo': InlineImage(doc, 'logo.png', width=Inches(2)),
    'chart': InlineImage(doc, 'sales_chart.png', width=Inches(5)),
    'signature': InlineImage(doc, 'signature.png', height=Inches(0.5)),
}

doc.render(context)
doc.save('report.docx')
```

Template placeholder: `{{ company_logo }}`

### Rich Text (Subdocuments)

```python
from docxtpl import DocxTemplate, RichText

doc = DocxTemplate("template.docx")

# Create rich text with formatting
rt = RichText()
rt.add('Important: ', bold=True, color='FF0000')
rt.add('Please review before signing.')

context = {
    'notice': rt,
}

doc.render(context)
```

---

## Workflow Automation

### Complete Pipeline

```python
import os
import json
from datetime import datetime
from docxtpl import DocxTemplate
from pathlib import Path

class DocumentPipeline:
    """End-to-end document generation pipeline."""

    def __init__(self, template_dir: str, output_dir: str):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, data_source: str) -> list:
        """Load data from JSON file."""
        with open(data_source) as f:
            return json.load(f)

    def validate_context(self, context: dict, required_fields: list) -> bool:
        """Validate required fields are present."""
        missing = [f for f in required_fields if f not in context]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        return True

    def generate(self, template_name: str, context: dict, output_name: str = None):
        """Generate single document."""
        template_path = self.template_dir / template_name
        doc = DocxTemplate(str(template_path))
        doc.render(context)

        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{template_name.replace('.docx', '')}_{timestamp}.docx"

        output_path = self.output_dir / output_name
        doc.save(str(output_path))
        return output_path

    def batch_generate(self, template_name: str, data_source: str,
                       filename_field: str = 'id'):
        """Generate multiple documents from data source."""
        data = self.load_data(data_source)
        generated = []

        for item in data:
            output_name = f"{item.get(filename_field, 'doc')}.docx"
            path = self.generate(template_name, item, output_name)
            generated.append(path)

        return generated

# Usage
pipeline = DocumentPipeline(
    template_dir="templates",
    output_dir="generated"
)

# Single document
pipeline.generate(
    template_name="invoice.docx",
    context={'customer': 'Acme', 'amount': 5000},
    output_name="invoice_acme.docx"
)

# Batch generation
pipeline.batch_generate(
    template_name="contract.docx",
    data_source="clients.json",
    filename_field="client_id"
)
```

### Integration with APIs

```python
import requests
from docxtpl import DocxTemplate

def generate_from_api(template_path: str, api_url: str, output_path: str):
    """Fetch data from API and generate document."""

    # Fetch data
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()

    # Generate document
    doc = DocxTemplate(template_path)
    doc.render(data)
    doc.save(output_path)

    return output_path

# Example: Generate invoice from order API
generate_from_api(
    template_path="invoice_template.docx",
    api_url="https://api.example.com/orders/12345",
    output_path="invoices/order_12345.docx"
)
```

---

## Error Handling

### Robust Generation

```python
from docxtpl import DocxTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_generate(template_path: str, context: dict, output_path: str) -> bool:
    """Generate document with error handling."""
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)
        doc.save(output_path)
        logger.info(f"Generated: {output_path}")
        return True

    except FileNotFoundError:
        logger.error(f"Template not found: {template_path}")
        return False

    except KeyError as e:
        logger.error(f"Missing template variable: {e}")
        return False

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return False

def batch_generate_safe(template_path: str, contexts: list, output_dir: str):
    """Batch generate with failure tracking."""
    results = {'success': [], 'failed': []}

    for ctx in contexts:
        output_path = f"{output_dir}/{ctx.get('id', 'unknown')}.docx"

        if safe_generate(template_path, ctx, output_path):
            results['success'].append(output_path)
        else:
            results['failed'].append(ctx)

    logger.info(f"Generated: {len(results['success'])}, Failed: {len(results['failed'])}")
    return results
```

---

## Related Resources

- [SKILL.md](../SKILL.md) - Quick reference
- [docx-patterns.md](docx-patterns.md) - Advanced formatting
- [docxtpl Documentation](https://docxtpl.readthedocs.io/)
