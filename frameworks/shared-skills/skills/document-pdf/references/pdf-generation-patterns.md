# PDF Generation Patterns

Advanced patterns for creating complex PDF documents with precise layouts.

---
## Table of Contents

- [Multi-Page Documents](#multi-page-documents)
- [Page Management (PDFKit)](#page-management-pdfkit)
- [Page Breaks (ReportLab)](#page-breaks-reportlab)
- [Content that spans pages](#content-that-spans-pages)
- [Force page break](#force-page-break)
- [Headers and Footers](#headers-and-footers)
- [Running Headers (ReportLab)](#running-headers-reportlab)
- [Headers (PDFKit)](#headers-pdfkit)
- [HTML to PDF Routes](#html-to-pdf-routes)
- [Browser-Faithful Rendering (Playwright)](#browser-faithful-rendering-playwright)
- [Semantic HTML Export (WeasyPrint)](#semantic-html-export-weasyprint)
- [Complex Tables](#complex-tables)
- [Styled Table (ReportLab)](#styled-table-reportlab)
- [Images and Graphics](#images-and-graphics)
- [Image Placement (pdf-lib)](#image-placement-pdf-lib)
- [Charts (ReportLab)](#charts-reportlab)
- [Bar chart](#bar-chart)
- [Pie chart](#pie-chart)
- [Fonts and Typography](#fonts-and-typography)
- [Custom Fonts (PDFKit)](#custom-fonts-pdfkit)
- [Font Embedding (pdf-lib)](#font-embedding-pdf-lib)
- [Performance Optimization](#performance-optimization)
- [Streaming Large PDFs (PDFKit)](#streaming-large-pdfs-pdfkit)
- [Batch Processing (pypdf)](#batch-processing-pypdf)
- [Related](#related)


## Multi-Page Documents

### Page Management (PDFKit)

```typescript
import PDFDocument from 'pdfkit';

const doc = new PDFDocument({ autoFirstPage: false });

// Add pages with different sizes
doc.addPage({ size: 'A4' });           // Standard page
doc.addPage({ size: 'LETTER' });       // US Letter
doc.addPage({ size: [612, 792] });     // Custom dimensions
doc.addPage({
  size: 'A4',
  layout: 'landscape',
  margins: { top: 50, bottom: 50, left: 72, right: 72 }
});
```

### Page Breaks (ReportLab)

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate('multi_page.pdf')
styles = getSampleStyleSheet()
story = []

# Content that spans pages
for i in range(50):
    story.append(Paragraph(f'Paragraph {i}', styles['Normal']))
    story.append(Spacer(1, 12))

# Force page break
story.append(PageBreak())
story.append(Paragraph('New Section', styles['Heading1']))

doc.build(story)
```

---

## Headers and Footers

### Running Headers (ReportLab)

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter

def header_footer(canvas, doc):
    canvas.saveState()

    # Header
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(72, letter[1] - 40, 'Company Name')
    canvas.drawRightString(letter[0] - 72, letter[1] - 40, 'Confidential')

    # Footer with page number
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(letter[0] / 2, 30, f'Page {doc.page}')

    canvas.restoreState()

doc = SimpleDocTemplate('with_headers.pdf')
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
```

### Headers (PDFKit)

```typescript
doc.on('pageAdded', () => {
  const top = doc.page.margins.top;
  doc.save();
  doc.fontSize(10)
     .text('Header Text', 50, top - 30, { align: 'left' })
     .text(`Page ${doc.bufferedPageRange().count}`, 0, top - 30, { align: 'right' });
  doc.restore();
});
```

---

## HTML to PDF Routes

Choose the renderer based on the source of truth:

- Use **Playwright** when the PDF must match an existing web page or design system in Chromium.
- Use **WeasyPrint** when you control semantic HTML and need a stronger path to tagged, accessible, or archival PDFs.

### Browser-Faithful Rendering (Playwright)

```typescript
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();

await page.goto('http://localhost:3000/report', { waitUntil: 'networkidle' });
await page.emulateMedia({ media: 'screen' });

await page.pdf({
  path: 'report.pdf',
  format: 'A4',
  printBackground: true,
  preferCSSPageSize: true,
  tagged: true,
  outline: true,
});

await browser.close();
```

### Semantic HTML Export (WeasyPrint)

```python
from weasyprint import HTML

HTML(filename='report.html', base_url='.').write_pdf(
    'report.pdf',
    presentational_hints=True,
)
```

If accessibility or archival compliance matters, enable the documented WeasyPrint tag and PDF variant options instead of treating a generic export as compliant by default.

---

## Complex Tables

### Styled Table (ReportLab)

```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

data = [
    ['Product', 'Qty', 'Price', 'Total'],
    ['Widget A', '10', '$50.00', '$500.00'],
    ['Widget B', '5', '$75.00', '$375.00'],
    ['Widget C', '20', '$25.00', '$500.00'],
    ['', '', 'Subtotal', '$1,375.00'],
    ['', '', 'Tax (8%)', '$110.00'],
    ['', '', 'Total', '$1,485.00'],
]

table = Table(data, colWidths=[200, 60, 80, 80])
table.setStyle(TableStyle([
    # Header row
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

    # Data rows
    ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),

    # Alternating row colors
    ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecf0f1')),
    ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ecf0f1')),

    # Totals section
    ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
    ('LINEABOVE', (2, -3), (-1, -3), 1, colors.black),

    # Grid
    ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
    ('BOX', (0, 0), (-1, -1), 1, colors.black),
]))
```

---

## Images and Graphics

### Image Placement (pdf-lib)

```typescript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

const pdfDoc = await PDFDocument.create();
const page = pdfDoc.addPage([600, 800]);

// Embed PNG
const pngBytes = fs.readFileSync('logo.png');
const pngImage = await pdfDoc.embedPng(pngBytes);
const pngDims = pngImage.scale(0.5);

page.drawImage(pngImage, {
  x: 50,
  y: 700,
  width: pngDims.width,
  height: pngDims.height,
});

// Embed JPG
const jpgBytes = fs.readFileSync('photo.jpg');
const jpgImage = await pdfDoc.embedJpg(jpgBytes);

page.drawImage(jpgImage, {
  x: 50,
  y: 400,
  width: 200,
  height: 150,
});
```

### Charts (ReportLab)

```python
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie

# Bar chart
drawing = Drawing(400, 200)
chart = VerticalBarChart()
chart.x = 50
chart.y = 50
chart.width = 300
chart.height = 125
chart.data = [[10, 20, 30, 40], [15, 25, 35, 45]]
chart.categoryAxis.categoryNames = ['Q1', 'Q2', 'Q3', 'Q4']
drawing.add(chart)

# Pie chart
pie_drawing = Drawing(200, 200)
pie = Pie()
pie.x = 50
pie.y = 50
pie.width = 100
pie.height = 100
pie.data = [30, 25, 20, 15, 10]
pie.labels = ['A', 'B', 'C', 'D', 'E']
pie_drawing.add(pie)
```

---

## Fonts and Typography

### Custom Fonts (PDFKit)

```typescript
// Register custom fonts
doc.registerFont('CustomFont', 'fonts/CustomFont-Regular.ttf');
doc.registerFont('CustomFont-Bold', 'fonts/CustomFont-Bold.ttf');

doc.font('CustomFont').fontSize(12).text('Regular text');
doc.font('CustomFont-Bold').fontSize(14).text('Bold heading');
```

### Font Embedding (pdf-lib)

```typescript
import { PDFDocument, StandardFonts } from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import fs from 'fs';

const pdfDoc = await PDFDocument.create();
pdfDoc.registerFontkit(fontkit);

// Embed custom font
const fontBytes = fs.readFileSync('fonts/Roboto-Regular.ttf');
const customFont = await pdfDoc.embedFont(fontBytes);

// Use standard font
const helvetica = await pdfDoc.embedFont(StandardFonts.Helvetica);

const page = pdfDoc.addPage();
page.drawText('Custom Font Text', {
  font: customFont,
  size: 24,
  x: 50,
  y: 700,
});
```

---

## Performance Optimization

### Streaming Large PDFs (PDFKit)

```typescript
import PDFDocument from 'pdfkit';
import fs from 'fs';

const doc = new PDFDocument({ bufferPages: false }); // Don't buffer
doc.pipe(fs.createWriteStream('large.pdf'));

// Generate content incrementally
for (let i = 0; i < 1000; i++) {
  doc.addPage();
  doc.text(`Page ${i + 1}`);
  doc.flushPages(); // Write pages immediately
}

doc.end();
```

### Batch Processing (pypdf)

```python
from pypdf import PdfWriter, PdfReader
from pathlib import Path

def batch_add_watermark(input_dir: Path, watermark_pdf: str, output_dir: Path):
    watermark = PdfReader(watermark_pdf).pages[0]

    for pdf_file in input_dir.glob('*.pdf'):
        reader = PdfReader(pdf_file)
        writer = PdfWriter()

        for page in reader.pages:
            page.merge_page(watermark)
            writer.add_page(page)

        output_path = output_dir / pdf_file.name
        with open(output_path, 'wb') as f:
            writer.write(f)
```

---

## ATS-Optimized Document Generation

Applicant Tracking Systems (Workday, Greenhouse, Lever, Ashby) parse uploaded PDFs using text extraction and keyword matching. Documents that are visually appealing but poorly structured for machine parsing get rejected or misclassified.

### ATS Constraints

| Requirement | Why | Implementation |
|-------------|-----|----------------|
| Real text, not images | ATS extracts text, cannot OCR | Use font-embedded text, never rasterized headings |
| Standard section headings | ATS maps sections by keyword | Use "Experience", "Education", "Skills" — not creative alternatives |
| Single-column layout | Multi-column parsing is unreliable | Avoid tables or columns for primary content flow |
| No headers/footers for critical data | Some ATS skip headers/footers | Keep name and contact info in the main body |
| Standard fonts | Glyph mapping failures cause garbled text | Use system fonts (Helvetica, Arial, Times) or embed fully |
| No watermarks or background images | Interfere with text extraction | Use white background, no decorative layers |

### Generation Pattern (PDFKit)

```typescript
import PDFDocument from 'pdfkit';

const doc = new PDFDocument({
  size: 'A4',
  margins: { top: 50, bottom: 50, left: 60, right: 60 },
  // No autoFirstPage tricks — keep structure simple for ATS
});

// Name — in body, not header
doc.fontSize(18).font('Helvetica-Bold').text('Candidate Name');
doc.fontSize(10).font('Helvetica')
   .text('email@example.com | +44 7700 000000 | London, UK');
doc.moveDown(0.5);

// Standard section heading
doc.fontSize(13).font('Helvetica-Bold').text('Experience');
doc.moveTo(60, doc.y).lineTo(535, doc.y).stroke(); // underline
doc.moveDown(0.3);

// Role entry — linear flow, no columns
doc.fontSize(11).font('Helvetica-Bold').text('Senior Engineer — Company Name');
doc.fontSize(10).font('Helvetica').text('Jan 2023 – Present');
doc.fontSize(10).font('Helvetica')
   .text('• Led migration of payment processing to Stripe Connect', { indent: 10 });
```

### Keyword Optimization

AI job-search tools (e.g., career-ops) generate per-job CVs by matching job description keywords to candidate experience. When building PDF generation for CV/resume tools:

- Extract keywords from job descriptions programmatically
- Map keywords to candidate experience entries
- Place matched keywords in context (not keyword-stuffed lists)
- Preserve natural language — ATS increasingly use NLP, not just keyword counts

**Reference:** career-ops (github.com/santifer/career-ops) demonstrates production-grade ATS-optimized PDF generation across 45+ company portal formats.

---

## Related

- [pdf-extraction-patterns.md](pdf-extraction-patterns.md) - Text and table extraction
- [../assets/invoice-template.md](../assets/invoice-template.md) - Invoice generation
- [../assets/report-template.md](../assets/report-template.md) - Report generation
