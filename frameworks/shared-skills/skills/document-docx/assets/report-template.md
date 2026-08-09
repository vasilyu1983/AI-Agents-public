# Report Template

Copy-paste structure for professional reports with python-docx or docxtpl.

---

## Report Structure

```text
REPORT DOCUMENT
├── Title Page
│   ├── Report title (Heading 0, centered)
│   ├── Subtitle/date
│   ├── Author/organization
│   └── Logo (optional)
├── Table of Contents
├── Executive Summary (1 page max)
├── Body Sections
│   ├── Introduction/Background
│   ├── Methodology (if applicable)
│   ├── Findings/Results
│   │   ├── Section 1 with tables/charts
│   │   ├── Section 2 with data
│   │   └── Section 3 with analysis
│   ├── Discussion
│   └── Recommendations
├── Conclusion
├── Appendices
│   ├── Appendix A: Data Tables
│   ├── Appendix B: Methodology Details
│   └── Appendix C: References
└── Footer (page numbers, confidentiality notice)
```

---

## Python Implementation

### Full Report Generator

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from datetime import datetime

def create_report(title: str, author: str, sections: list, output_path: str):
    """Generate professional report document."""
    doc = Document()

    # ----- TITLE PAGE -----
    # Add spacing before title
    for _ in range(5):
        doc.add_paragraph()

    # Report title
    title_para = doc.add_heading(title, 0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Subtitle/date
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_run = date_para.add_run(datetime.now().strftime("%B %Y"))
    date_run.font.size = Pt(14)

    # Author
    author_para = doc.add_paragraph()
    author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author_para.add_run(f"Prepared by: {author}")

    # Page break after title
    doc.add_page_break()

    # ----- TABLE OF CONTENTS -----
    doc.add_heading('Table of Contents', 1)
    toc_para = doc.add_paragraph()
    toc_para.add_run('[Update field in Word to generate TOC]').italic = True
    doc.add_page_break()

    # ----- EXECUTIVE SUMMARY -----
    doc.add_heading('Executive Summary', 1)
    doc.add_paragraph(
        'This section provides a high-level overview of the report findings, '
        'key insights, and recommendations. Keep to one page maximum.'
    )
    doc.add_page_break()

    # ----- BODY SECTIONS -----
    for section in sections:
        doc.add_heading(section['title'], section.get('level', 1))

        if 'content' in section:
            doc.add_paragraph(section['content'])

        if 'table' in section:
            add_table(doc, section['table'])

        if 'bullets' in section:
            for bullet in section['bullets']:
                doc.add_paragraph(bullet, style='List Bullet')

    # ----- APPENDICES -----
    doc.add_page_break()
    doc.add_heading('Appendices', 1)
    doc.add_heading('Appendix A: Supporting Data', 2)
    doc.add_paragraph('[Insert supporting data tables here]')

    # ----- FOOTER -----
    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = f"Confidential | {datetime.now().year}"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.save(output_path)
    return output_path


def add_table(doc, table_data: dict):
    """Add formatted table to document."""
    headers = table_data['headers']
    rows = table_data['rows']

    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.style = 'Table Grid'

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.paragraphs[0].runs[0].bold = True

    # Data rows
    for row_idx, row_data in enumerate(rows):
        for col_idx, cell_data in enumerate(row_data):
            table.rows[row_idx + 1].cells[col_idx].text = str(cell_data)

    doc.add_paragraph()  # Spacing after table


# ----- USAGE EXAMPLE -----

sections = [
    {
        'title': 'Introduction',
        'level': 1,
        'content': 'This report analyzes the quarterly performance metrics...'
    },
    {
        'title': 'Methodology',
        'level': 1,
        'content': 'Data was collected from multiple sources including...',
        'bullets': [
            'Internal CRM system (Q1-Q4 2024)',
            'Customer surveys (n=500)',
            'Market research reports'
        ]
    },
    {
        'title': 'Key Findings',
        'level': 1,
        'content': 'Analysis revealed the following trends:'
    },
    {
        'title': 'Revenue Analysis',
        'level': 2,
        'table': {
            'headers': ['Quarter', 'Revenue', 'Growth'],
            'rows': [
                ['Q1', '$1.2M', '+5%'],
                ['Q2', '$1.4M', '+17%'],
                ['Q3', '$1.3M', '-7%'],
                ['Q4', '$1.8M', '+38%'],
            ]
        }
    },
    {
        'title': 'Recommendations',
        'level': 1,
        'bullets': [
            'Increase marketing spend in Q2 to capitalize on seasonal trends',
            'Implement customer retention program',
            'Expand into adjacent market segments'
        ]
    },
    {
        'title': 'Conclusion',
        'level': 1,
        'content': 'Based on the analysis, we recommend proceeding with...'
    }
]

create_report(
    title="Quarterly Performance Report",
    author="Analytics Team",
    sections=sections,
    output_path="quarterly_report.docx"
)
```

---

## docxtpl Template Version

### Template File (`report_template.docx`)

Create in Word with this structure:

```text
{{ report_title }}
{{ subtitle }}
Prepared by: {{ author }}
Date: {{ date }}

----------------------------------------

TABLE OF CONTENTS
[Update in Word]

----------------------------------------

EXECUTIVE SUMMARY

{{ executive_summary }}

----------------------------------------

{% for section in sections %}
{{ section.title }}

{{ section.content }}

{%tr for row in section.table_rows %}
| {{ row.col1 }} | {{ row.col2 }} | {{ row.col3 }} |
{%tr endfor %}

{% endfor %}

----------------------------------------

APPENDICES

{{ appendix_content }}
```

### Python Fill Script

```python
from docxtpl import DocxTemplate
from datetime import datetime

doc = DocxTemplate("report_template.docx")

context = {
    'report_title': 'Annual Performance Review',
    'subtitle': 'Fiscal Year 2024',
    'author': 'Strategic Planning Team',
    'date': datetime.now().strftime('%B %d, %Y'),
    'executive_summary': '''
        This annual review summarizes key achievements, challenges, and
        strategic recommendations for the upcoming fiscal year. Overall
        performance exceeded targets by 12%, driven by strong Q4 results.
    ''',
    'sections': [
        {
            'title': 'Financial Performance',
            'content': 'Revenue grew 18% year-over-year...',
            'table_rows': [
                {'col1': 'Metric', 'col2': '2023', 'col3': '2024'},
                {'col1': 'Revenue', 'col2': '$4.2M', 'col3': '$4.9M'},
                {'col1': 'Profit', 'col2': '$0.8M', 'col3': '$1.1M'},
            ]
        },
        {
            'title': 'Strategic Initiatives',
            'content': 'Three major initiatives were completed...',
            'table_rows': []
        }
    ],
    'appendix_content': 'Detailed data available upon request.'
}

doc.render(context)
doc.save('annual_review_2024.docx')
```

---

## Style Guide

### Typography

| Element | Font | Size | Style |
|---------|------|------|-------|
| Title | Calibri Light | 28pt | Bold, Centered |
| Heading 1 | Calibri | 16pt | Bold |
| Heading 2 | Calibri | 14pt | Bold |
| Body | Calibri | 11pt | Normal |
| Caption | Calibri | 10pt | Italic |

### Spacing

| Element | Before | After |
|---------|--------|-------|
| Heading 1 | 24pt | 12pt |
| Heading 2 | 18pt | 6pt |
| Paragraph | 0pt | 10pt |
| Table | 12pt | 12pt |

### Page Layout

| Property | Value |
|----------|-------|
| Margins | 1" all sides |
| Header | 0.5" from edge |
| Footer | 0.5" from edge |
| Line spacing | 1.15 |

---

## Related Resources

- [SKILL.md](../SKILL.md) - Quick reference
- [contract-template.md](contract-template.md) - Legal document structure
- [docx-patterns.md](../references/docx-patterns.md) - Advanced formatting
