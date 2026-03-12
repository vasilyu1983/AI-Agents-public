# PDF Forms and Interactive Elements

Patterns for creating, filling, reading, and flattening PDF forms.

---

## Contents

- [AcroForms vs XFA](#acroforms-vs-xfa)
- [Creating Forms with pdf-lib](#creating-forms-with-pdf-lib)
- [Filling Forms with pdf-lib](#filling-forms-with-pdf-lib)
- [Reading Form Data with pypdf](#reading-form-data-with-pypdf)
- [Flattening Forms](#flattening-forms)
- [Digital Signatures Overview](#digital-signatures-overview)
- [Common Pitfalls](#common-pitfalls)
- [Checklist: Form Development Review](#checklist-form-development-review)

---

## AcroForms vs XFA

**AcroForms** are the standard interactive form format. Every major PDF library supports them. Use AcroForms for all new work.

**XFA** is Adobe-proprietary, deprecated since PDF 2.0 (2017). Chrome, Firefox, Edge, Preview, and most libraries cannot render XFA. If you receive XFA, re-create as AcroForm. Never create new XFA forms.

---

## Creating Forms with pdf-lib

```typescript
import { PDFDocument, StandardFonts } from 'pdf-lib';

const pdfDoc = await PDFDocument.create();
const page = pdfDoc.addPage([600, 800]);
const form = pdfDoc.getForm();

// Text, dropdown, checkbox, radio group
const name = form.createTextField('fullName');
name.addToPage(page, { x: 150, y: 710, width: 250, height: 20 });

const country = form.createDropdown('country');
country.addOptions(['US', 'UK', 'Germany']);
country.addToPage(page, { x: 150, y: 670, width: 250, height: 20 });

const agree = form.createCheckBox('agreeTerms');
agree.addToPage(page, { x: 150, y: 635, width: 15, height: 15 });

const priority = form.createRadioGroup('priority');
priority.addOptionToPage('low', page, { x: 150, y: 597, width: 12, height: 12 });
priority.addOptionToPage('high', page, { x: 210, y: 597, width: 12, height: 12 });
```

---

## Filling Forms with pdf-lib

```typescript
const pdfDoc = await PDFDocument.load(existingBytes);
const form = pdfDoc.getForm();

form.getTextField('fullName').setText('Jane Smith');
form.getDropdown('country').select('Germany');
form.getCheckBox('agreeTerms').check();
form.getRadioGroup('priority').select('high');

// Discover field names in unknown forms
form.getFields().forEach(f => console.log(`${f.getName()} (${f.constructor.name})`));
```

---

## Reading Form Data with pypdf

```python
from pypdf import PdfReader, PdfWriter

def read_form(pdf_path: str) -> dict:
    fields = PdfReader(pdf_path).get_fields()
    if not fields:
        return {}
    return {n: str(f.get('/V', '')) for n, f in fields.items()}

def fill_form(input_path: str, output_path: str, data: dict) -> None:
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.append(reader)
    writer.update_page_form_field_values(writer.pages[0], data)
    with open(output_path, 'wb') as f:
        writer.write(f)
```

---

## Flattening Forms

Flattening converts fields into static page content. Use before distributing completed forms.

```typescript
// pdf-lib — straightforward
pdfDoc.getForm().flatten();
```

```python
# pypdf — remove AcroForm entry after filling
writer = PdfWriter()
writer.append(PdfReader('filled.pdf'))
if '/AcroForm' in writer._root_object:
    del writer._root_object['/AcroForm']
```

---

## Digital Signatures Overview

No general-purpose library (pdf-lib, pypdf, pdfkit) handles signing end-to-end. Use: **pyHanko** (self-hosted PKCS#11/PFX), **DocuSign/Adobe Sign API** (production e-sig), or **JSignPdf** (batch CLI). Do not implement PKCS#7/CMS from scratch.

---

## Common Pitfalls

- **Field naming conflicts**: merging PDFs with duplicate names causes overwrites. Namespace names (`form1_name`) before merging.
- **Font embedding**: fields using non-embedded fonts display squares. Always embed and call `form.updateFieldAppearances(font)`.
- **JavaScript in PDFs**: most non-Adobe viewers ignore it. Validate server-side, not in PDF JS.
- **Appearance streams**: some viewers skip regeneration. Call `updateFieldAppearances()` explicitly.

---

## Checklist: Form Development Review

- [ ] All fields use AcroForms (not XFA)
- [ ] Field names unique and namespaced if merging planned
- [ ] Tab order follows logical field sequence
- [ ] Fonts used in fields are embedded
- [ ] Form displays correctly in Adobe Reader, Chrome, and Preview
- [ ] Flatten works without missing values
- [ ] No business logic relies on embedded PDF JavaScript

---

## Do / Avoid

### Do

- Use AcroForms for all new forms.
- Flatten before distributing completed documents.
- Test in at least three viewers.
- Embed all fonts used in form fields.

### Avoid

- Creating XFA forms.
- Relying on PDF JavaScript for validation.
- Distributing editable forms when the intent is a final record.
- Assuming field names match across different PDF templates.

---

## Related

- [pdf-generation-patterns.md](pdf-generation-patterns.md) — Layout and generation code
- [pdf-extraction-patterns.md](pdf-extraction-patterns.md) — Reading form data and metadata
- [pdf-security-redaction.md](pdf-security-redaction.md) — Encryption and permissions
