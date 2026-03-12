# Contract Template

Copy-paste structure for legal documents, agreements, and formal contracts.

---

## Contract Structure

```text
CONTRACT DOCUMENT
├── Header Block
│   ├── Agreement title
│   ├── Contract number (optional)
│   └── Effective date
├── Parties Section
│   ├── Party A (full legal name, address)
│   └── Party B (full legal name, address)
├── Recitals (WHEREAS clauses)
│   ├── Background context
│   └── Purpose of agreement
├── Definitions
│   └── Key terms defined
├── Terms and Conditions
│   ├── 1. Scope of Work/Services
│   ├── 2. Term and Termination
│   ├── 3. Compensation/Payment
│   ├── 4. Confidentiality
│   ├── 5. Intellectual Property
│   ├── 6. Representations & Warranties
│   ├── 7. Limitation of Liability
│   ├── 8. Indemnification
│   └── 9. General Provisions
│       ├── Governing Law
│       ├── Dispute Resolution
│       ├── Notices
│       ├── Entire Agreement
│       └── Amendments
├── Signature Block
│   ├── Party A signature, name, title, date
│   └── Party B signature, name, title, date
└── Exhibits/Schedules
    ├── Exhibit A: Scope of Work
    ├── Exhibit B: Pricing
    └── Exhibit C: SLA (if applicable)
```

---

## Python Implementation

### Contract Generator

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from datetime import datetime

def create_contract(contract_data: dict, output_path: str):
    """Generate formal contract document."""
    doc = Document()

    # Set narrow margins for legal documents
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.25)

    # ----- HEADER -----
    title = doc.add_heading(contract_data['title'], 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if contract_data.get('contract_number'):
        num_para = doc.add_paragraph()
        num_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        num_para.add_run(f"Contract No. {contract_data['contract_number']}")

    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.add_run(f"Effective Date: {contract_data['effective_date']}")

    doc.add_paragraph()  # Spacing

    # ----- PARTIES -----
    doc.add_paragraph(
        f"This Agreement is entered into by and between:"
    )

    parties_para = doc.add_paragraph()
    parties_para.add_run(f"{contract_data['party_a']['name']}").bold = True
    parties_para.add_run(f", a {contract_data['party_a']['type']} ")
    parties_para.add_run(f"located at {contract_data['party_a']['address']} ")
    parties_para.add_run('("Party A"); and')

    parties_para2 = doc.add_paragraph()
    parties_para2.add_run(f"{contract_data['party_b']['name']}").bold = True
    parties_para2.add_run(f", a {contract_data['party_b']['type']} ")
    parties_para2.add_run(f"located at {contract_data['party_b']['address']} ")
    parties_para2.add_run('("Party B").')

    doc.add_paragraph()

    # ----- RECITALS -----
    doc.add_heading('RECITALS', 1)

    for i, recital in enumerate(contract_data.get('recitals', []), 1):
        para = doc.add_paragraph()
        para.add_run(f"WHEREAS, ").bold = True
        para.add_run(recital)

    now_para = doc.add_paragraph()
    now_para.add_run("NOW, THEREFORE, ").bold = True
    now_para.add_run(
        "in consideration of the mutual covenants and agreements herein, "
        "the parties agree as follows:"
    )

    doc.add_paragraph()

    # ----- DEFINITIONS -----
    if contract_data.get('definitions'):
        doc.add_heading('1. DEFINITIONS', 1)
        for term, definition in contract_data['definitions'].items():
            para = doc.add_paragraph()
            para.add_run(f'"{term}"').bold = True
            para.add_run(f" means {definition}")

    # ----- NUMBERED SECTIONS -----
    section_num = 2 if contract_data.get('definitions') else 1

    for section in contract_data.get('sections', []):
        doc.add_heading(f"{section_num}. {section['title'].upper()}", 1)

        if isinstance(section['content'], str):
            doc.add_paragraph(section['content'])
        elif isinstance(section['content'], list):
            for i, item in enumerate(section['content'], 1):
                para = doc.add_paragraph()
                para.add_run(f"{section_num}.{i} ").bold = True
                para.add_run(item)

        section_num += 1

    # ----- SIGNATURE BLOCK -----
    doc.add_page_break()
    doc.add_heading('SIGNATURES', 1)

    doc.add_paragraph(
        "IN WITNESS WHEREOF, the parties have executed this Agreement "
        f"as of the date first written above."
    )

    doc.add_paragraph()
    doc.add_paragraph()

    # Create signature table
    sig_table = doc.add_table(rows=4, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Party A signature
    sig_table.cell(0, 0).text = contract_data['party_a']['name'].upper()
    sig_table.cell(1, 0).text = "_" * 40
    sig_table.cell(2, 0).text = "Signature"
    sig_table.cell(3, 0).text = "Name: ________________  Title: ________________  Date: ________"

    # Party B signature
    sig_table.cell(0, 1).text = contract_data['party_b']['name'].upper()
    sig_table.cell(1, 1).text = "_" * 40
    sig_table.cell(2, 1).text = "Signature"
    sig_table.cell(3, 1).text = "Name: ________________  Title: ________________  Date: ________"

    # ----- EXHIBITS -----
    if contract_data.get('exhibits'):
        doc.add_page_break()
        for exhibit in contract_data['exhibits']:
            doc.add_heading(f"EXHIBIT {exhibit['letter']}: {exhibit['title']}", 1)
            doc.add_paragraph(exhibit.get('content', '[To be attached]'))

    doc.save(output_path)
    return output_path


# ----- USAGE EXAMPLE -----

contract_data = {
    'title': 'SERVICE AGREEMENT',
    'contract_number': 'SA-2025-001',
    'effective_date': 'January 15, 2025',

    'party_a': {
        'name': 'Acme Corporation',
        'type': 'Delaware corporation',
        'address': '123 Main Street, Wilmington, DE 19801'
    },

    'party_b': {
        'name': 'TechServices LLC',
        'type': 'California limited liability company',
        'address': '456 Innovation Drive, San Francisco, CA 94105'
    },

    'recitals': [
        'Party A desires to engage Party B to provide certain professional services;',
        'Party B has the expertise and resources to provide such services;',
        'The parties wish to set forth the terms under which Party B will provide services to Party A.'
    ],

    'definitions': {
        'Services': 'the professional services described in Exhibit A.',
        'Deliverables': 'the work product to be delivered under this Agreement.',
        'Confidential Information': 'any non-public information disclosed by either party.',
        'Term': 'the period beginning on the Effective Date and continuing for twelve (12) months.'
    },

    'sections': [
        {
            'title': 'Scope of Services',
            'content': [
                'Party B shall provide the Services described in Exhibit A.',
                'Party B shall perform all Services in a professional and workmanlike manner.',
                'Party B shall comply with all applicable laws and regulations.'
            ]
        },
        {
            'title': 'Compensation',
            'content': [
                'Party A shall pay Party B the fees set forth in Exhibit B.',
                'Payment shall be due within thirty (30) days of invoice.',
                'Late payments shall bear interest at 1.5% per month.'
            ]
        },
        {
            'title': 'Term and Termination',
            'content': [
                'This Agreement shall remain in effect for the Term unless earlier terminated.',
                'Either party may terminate with thirty (30) days written notice.',
                'Upon termination, Party B shall deliver all Deliverables completed to date.'
            ]
        },
        {
            'title': 'Confidentiality',
            'content': 'Each party agrees to maintain the confidentiality of the other party\'s Confidential Information and not to disclose such information to third parties without prior written consent.'
        },
        {
            'title': 'Limitation of Liability',
            'content': 'IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THIS AGREEMENT.'
        },
        {
            'title': 'Governing Law',
            'content': 'This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflicts of law principles.'
        }
    ],

    'exhibits': [
        {'letter': 'A', 'title': 'SCOPE OF WORK', 'content': '[Detailed scope to be attached]'},
        {'letter': 'B', 'title': 'PRICING SCHEDULE', 'content': '[Fee schedule to be attached]'}
    ]
}

create_contract(contract_data, 'service_agreement.docx')
```

---

## docxtpl Template Version

### Template File (`contract_template.docx`)

```text
{{ contract_title }}
Contract No. {{ contract_number }}
Effective Date: {{ effective_date }}

This Agreement is entered into by and between:

{{ party_a_name }}, a {{ party_a_type }} located at {{ party_a_address }} ("Party A"); and

{{ party_b_name }}, a {{ party_b_type }} located at {{ party_b_address }} ("Party B").

RECITALS

{% for recital in recitals %}
WHEREAS, {{ recital }}
{% endfor %}

NOW, THEREFORE, in consideration of the mutual covenants herein, the parties agree:

{% for section in sections %}
{{ loop.index }}. {{ section.title }}

{{ section.content }}

{% endfor %}

----------------------------------------

SIGNATURES

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

{{ party_a_name }}                    {{ party_b_name }}

_________________________            _________________________
Signature                            Signature

Name: ___________________            Name: ___________________
Title: ___________________           Title: ___________________
Date: ___________________            Date: ___________________
```

### Python Fill Script

```python
from docxtpl import DocxTemplate

doc = DocxTemplate("contract_template.docx")

context = {
    'contract_title': 'MASTER SERVICE AGREEMENT',
    'contract_number': 'MSA-2025-042',
    'effective_date': 'February 1, 2025',

    'party_a_name': 'Global Industries Inc.',
    'party_a_type': 'Nevada corporation',
    'party_a_address': '789 Corporate Blvd, Las Vegas, NV 89101',

    'party_b_name': 'Premier Consulting Group',
    'party_b_type': 'Texas limited partnership',
    'party_b_address': '321 Business Park, Austin, TX 78701',

    'recitals': [
        'Party A requires consulting services for digital transformation;',
        'Party B specializes in enterprise digital solutions;',
        'Both parties wish to formalize their business relationship.'
    ],

    'sections': [
        {'title': 'SERVICES', 'content': 'Party B shall provide consulting services as detailed in the attached Statement of Work.'},
        {'title': 'TERM', 'content': 'This Agreement shall have an initial term of one (1) year.'},
        {'title': 'FEES', 'content': 'Party A shall pay fees as specified in the applicable Statement of Work.'},
        {'title': 'CONFIDENTIALITY', 'content': 'Both parties shall maintain confidentiality of proprietary information.'},
        {'title': 'GOVERNING LAW', 'content': 'This Agreement is governed by the laws of the State of Texas.'},
    ]
}

doc.render(context)
doc.save('master_service_agreement.docx')
```

---

## Common Contract Types

| Type | Key Sections | Special Considerations |
|------|--------------|------------------------|
| **NDA** | Definition of Confidential Info, Term, Return of Materials | One-way vs mutual |
| **Service Agreement** | Scope, Deliverables, Payment, Term | SOW attachments |
| **Employment** | Position, Compensation, Benefits, Termination | At-will language |
| **License** | Grant, Restrictions, Fees, Term | IP ownership |
| **SaaS** | Service Levels, Data Security, Uptime | SLA attachment |

---

## Legal Formatting Best Practices

### Typography

| Element | Formatting |
|---------|------------|
| Section headers | ALL CAPS, Bold |
| Subsections | Title Case, Bold |
| Definitions | "Term" in quotes, bold on first use |
| Cross-references | "Section X" capitalized |

### Numbering

```text
1. FIRST LEVEL SECTION
   1.1 Second level subsection
       (a) Third level item
       (b) Third level item
           (i) Fourth level item
```

### Boilerplate Language

Standard clauses to include:

- **Entire Agreement**: This Agreement constitutes the entire agreement...
- **Severability**: If any provision is held invalid...
- **Waiver**: Failure to enforce any provision...
- **Assignment**: Neither party may assign without consent...
- **Notices**: All notices shall be in writing...
- **Counterparts**: May be executed in counterparts...

---

## Related Resources

- [SKILL.md](../SKILL.md) - Quick reference
- [report-template.md](report-template.md) - Report structure
- [docx-patterns.md](../references/docx-patterns.md) - Advanced formatting
