# Advanced DOCX Patterns

Deep-dive into formatting, styles, headers/footers, and document structure.

## Contents

- Document Styles
- Headers and Footers
- Advanced Tables
- Page Layout
- Images and Shapes
- Hyperlinks
- Table of Contents
- Node.js Equivalents
- Related Resources

## Document Styles

### Built-in Styles (Python)

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE

doc = Document()

# Use built-in styles
doc.add_heading('Title', 0)  # Title style
doc.add_heading('Heading 1', 1)
doc.add_heading('Heading 2', 2)
doc.add_paragraph('Normal paragraph text.')
doc.add_paragraph('Quote style', style='Quote')
doc.add_paragraph('List item', style='List Bullet')
```

### Custom Styles

```python
from docx.shared import Pt, Inches
from docx.enum.text import WD_LINE_SPACING

# Create custom paragraph style
styles = doc.styles
custom_style = styles.add_style('CustomBody', WD_STYLE_TYPE.PARAGRAPH)
custom_style.font.name = 'Arial'
custom_style.font.size = Pt(11)
custom_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
custom_style.paragraph_format.space_after = Pt(12)

# Apply custom style
doc.add_paragraph('Styled paragraph', style='CustomBody')
```

### Character Styles

```python
# Create character style for emphasis
char_style = styles.add_style('Emphasis', WD_STYLE_TYPE.CHARACTER)
char_style.font.italic = True
char_style.font.color.rgb = RGBColor(0x42, 0x24, 0xE9)

# Apply in paragraph
para = doc.add_paragraph()
para.add_run('Normal text with ')
para.add_run('emphasized text', style='Emphasis')
para.add_run(' inline.')
```

---

## Headers and Footers

### Basic Header/Footer

```python
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Access default section
section = doc.sections[0]

# Header
header = section.header
header_para = header.paragraphs[0]
header_para.text = "Company Name"
header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Footer with page numbers
footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add page number field
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

run = footer_para.add_run()
fldChar1 = OxmlElement('w:fldChar')
fldChar1.set(qn('w:fldCharType'), 'begin')
run._r.append(fldChar1)

instrText = OxmlElement('w:instrText')
instrText.text = "PAGE"
run._r.append(instrText)

fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')
run._r.append(fldChar2)
```

### Different First Page Header

```python
section = doc.sections[0]
section.different_first_page_header_footer = True

# First page header (e.g., logo, full header)
first_header = section.first_page_header
first_header.paragraphs[0].text = "FULL COMPANY HEADER - First Page Only"

# Subsequent pages header (simplified)
header = section.header
header.paragraphs[0].text = "Company Name"
```

### Header with Logo

```python
header = section.header
header_para = header.paragraphs[0]

# Add logo
run = header_para.add_run()
run.add_picture('logo.png', width=Inches(1.5))

# Add company name next to logo
header_para.add_run('\t\tCompany Name')
```

---

## Advanced Tables

### Table with Merged Cells

```python
from docx.shared import Inches, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

table = doc.add_table(rows=4, cols=4)
table.style = 'Table Grid'

# Merge cells for header
cell_a1 = table.cell(0, 0)
cell_b1 = table.cell(0, 1)
cell_a1.merge(cell_b1)
cell_a1.text = "Merged Header"

# Set column widths
for row in table.rows:
    row.cells[0].width = Inches(2)
    row.cells[1].width = Inches(1.5)
```

### Styled Table with Alternating Rows

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def shade_cell(cell, color):
    """Apply shading to a cell."""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading)

# Create table
table = doc.add_table(rows=5, cols=3)
table.style = 'Table Grid'

# Header row styling
for cell in table.rows[0].cells:
    shade_cell(cell, "4472C4")  # Blue header
    cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    cell.paragraphs[0].runs[0].bold = True

# Alternating row colors
for i, row in enumerate(table.rows[1:], 1):
    color = "D9E2F3" if i % 2 == 0 else "FFFFFF"
    for cell in row.cells:
        shade_cell(cell, color)
```

---

## Page Layout

### Margins and Orientation

```python
from docx.shared import Inches
from docx.enum.section import WD_ORIENT

section = doc.sections[0]

# Set margins
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1.25)
section.right_margin = Inches(1.25)

# Landscape orientation
section.orientation = WD_ORIENT.LANDSCAPE
# Swap width and height for landscape
new_width = section.page_height
new_height = section.page_width
section.page_width = new_width
section.page_height = new_height
```

### Section Breaks

```python
from docx.enum.section import WD_SECTION

# Add content to first section
doc.add_paragraph("First section content")

# Add section break (new page)
doc.add_section(WD_SECTION.NEW_PAGE)

# Second section with different orientation
section2 = doc.sections[1]
section2.orientation = WD_ORIENT.LANDSCAPE
doc.add_paragraph("Second section - landscape")
```

### Columns

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

section = doc.sections[0]
sectPr = section._sectPr

# Create 2-column layout
cols = OxmlElement('w:cols')
cols.set(qn('w:num'), '2')
cols.set(qn('w:space'), '720')  # Space between columns (in twips)
sectPr.append(cols)
```

---

## Images and Shapes

### Image Positioning

```python
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Inline image (centered)
para = doc.add_paragraph()
para.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = para.add_run()
run.add_picture('chart.png', width=Inches(5))

# Image with caption
doc.add_paragraph('Figure 1: Sales Chart', style='Caption')
```

### Floating Image (Advanced)

```python
from docx.oxml.ns import nsmap, qn
from docx.oxml import OxmlElement

def add_float_picture(paragraph, image_path, width, pos_x, pos_y):
    """Add floating image at specified position."""
    run = paragraph.add_run()
    inline = run.add_picture(image_path, width=width).inline

    # Convert to anchor (floating)
    anchor = OxmlElement('wp:anchor')
    # ... (complex XML manipulation for positioning)
    # See python-docx GitHub issues for full implementation
```

---

## Hyperlinks

### Add Hyperlink

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_hyperlink(paragraph, url, text, color="0000FF", underline=True):
    """Add clickable hyperlink to paragraph."""
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rPr.append(c)

    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)

    new_run.append(rPr)
    t = OxmlElement('w:t')
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

    return hyperlink

# Usage
para = doc.add_paragraph("Visit ")
add_hyperlink(para, "https://example.com", "our website")
para.add_run(" for more info.")
```

---

## Table of Contents

### Generate TOC Placeholder

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_toc(doc):
    """Add Table of Contents field."""
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()

    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')

    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

    # Note: TOC updates when document is opened in Word

add_toc(doc)
doc.add_paragraph("Right-click TOC in Word and select 'Update Field'", style='Caption')
```

---

## Node.js Equivalents

### Styles (docx library)

```typescript
import { Document, Paragraph, TextRun, HeadingLevel, AlignmentType } from 'docx';

const doc = new Document({
  styles: {
    paragraphStyles: [
      {
        id: "CustomBody",
        name: "Custom Body",
        basedOn: "Normal",
        next: "Normal",
        run: {
          font: "Arial",
          size: 22,  // Half-points
        },
        paragraph: {
          spacing: { after: 240 },  // Twips
        },
      },
    ],
  },
  sections: [{
    children: [
      new Paragraph({
        text: "Styled paragraph",
        style: "CustomBody",
      }),
    ],
  }],
});
```

### Headers/Footers (docx library)

```typescript
import { Document, Header, Footer, Paragraph, PageNumber, AlignmentType } from 'docx';

const doc = new Document({
  sections: [{
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            text: "Company Name",
            alignment: AlignmentType.CENTER,
          }),
        ],
      }),
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun("Page "),
              new PageNumber(),
              new TextRun(" of "),
              new PageNumber({ numberOfPages: true }),
            ],
          }),
        ],
      }),
    },
    children: [
      new Paragraph({ text: "Document content" }),
    ],
  }],
});
```

---

## Related Resources

- [SKILL.md](../SKILL.md) - Quick reference
- [template-workflows.md](template-workflows.md) - Batch generation patterns
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [docx.js Documentation](https://docx.js.org/)
