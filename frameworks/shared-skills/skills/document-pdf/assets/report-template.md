# Report PDF Template

Copy-paste templates for generating multi-page reports with cover pages, TOC, and sections.

---

## Node.js (PDFKit)

```typescript
import PDFDocument from 'pdfkit';
import fs from 'fs';

interface ReportSection {
  title: string;
  content: string;
  charts?: { title: string; data: number[] }[];
}

interface ReportData {
  title: string;
  subtitle: string;
  author: string;
  date: string;
  sections: ReportSection[];
}

function generateReport(data: ReportData, outputPath: string): void {
  const doc = new PDFDocument({
    size: 'A4',
    bufferPages: true,
    margins: { top: 72, bottom: 72, left: 72, right: 72 }
  });

  doc.pipe(fs.createWriteStream(outputPath));

  // Track sections for TOC
  const tocEntries: { title: string; page: number }[] = [];

  // ===== COVER PAGE =====
  doc.rect(0, 0, doc.page.width, doc.page.height).fill('#2c3e50');

  doc.fillColor('white')
     .fontSize(36)
     .font('Helvetica-Bold')
     .text(data.title, 72, 280, { align: 'center' });

  doc.fontSize(18)
     .font('Helvetica')
     .text(data.subtitle, 72, 340, { align: 'center' });

  doc.fontSize(12)
     .text(data.author, 72, 500, { align: 'center' })
     .text(data.date, 72, 520, { align: 'center' });

  // ===== TABLE OF CONTENTS =====
  doc.addPage();
  doc.fillColor('black')
     .fontSize(24)
     .font('Helvetica-Bold')
     .text('Table of Contents', { align: 'left' });

  doc.moveDown(2);

  // Placeholder for TOC (we'll come back to this)
  const tocPageNum = doc.bufferedPageRange().count;
  const tocY = doc.y;

  // ===== CONTENT SECTIONS =====
  data.sections.forEach((section, index) => {
    doc.addPage();

    // Track for TOC
    tocEntries.push({
      title: section.title,
      page: doc.bufferedPageRange().count,
    });

    // Section header
    doc.fillColor('#2c3e50')
       .fontSize(20)
       .font('Helvetica-Bold')
       .text(`${index + 1}. ${section.title}`);

    doc.moveDown();

    // Section content
    doc.fillColor('black')
       .fontSize(11)
       .font('Helvetica')
       .text(section.content, {
         align: 'justify',
         lineGap: 4,
       });

    // Charts (simple bar representation)
    if (section.charts) {
      section.charts.forEach(chart => {
        doc.moveDown(2);
        doc.fontSize(12).font('Helvetica-Bold').text(chart.title);
        doc.moveDown(0.5);

        const barWidth = 300;
        const barHeight = 15;
        const maxVal = Math.max(...chart.data);

        chart.data.forEach((val, i) => {
          const width = (val / maxVal) * barWidth;
          doc.rect(doc.x, doc.y, width, barHeight).fill('#3498db');
          doc.fillColor('black')
             .fontSize(9)
             .text(`${val}`, doc.x + width + 5, doc.y - barHeight + 3);
          doc.y += barHeight + 5;
        });
      });
    }
  });

  // ===== ADD PAGE NUMBERS =====
  const range = doc.bufferedPageRange();
  for (let i = 1; i < range.count; i++) {  // Skip cover page
    doc.switchToPage(i);
    doc.fontSize(9)
       .fillColor('gray')
       .text(
         `Page ${i} of ${range.count - 1}`,
         72,
         doc.page.height - 50,
         { align: 'center', width: doc.page.width - 144 }
       );
  }

  // ===== FILL IN TOC =====
  doc.switchToPage(tocPageNum - 1);
  doc.y = tocY;

  tocEntries.forEach((entry, i) => {
    const dots = '.'.repeat(60);
    doc.fontSize(11)
       .font('Helvetica')
       .fillColor('black')
       .text(`${i + 1}. ${entry.title}`, 72, doc.y, { continued: true })
       .text(dots.slice(0, 50 - entry.title.length), { continued: true })
       .text(`${entry.page}`, { align: 'right' });
    doc.moveDown(0.5);
  });

  doc.end();
}

// Usage
const reportData: ReportData = {
  title: 'Q4 2024 Performance Report',
  subtitle: 'Annual Review and 2025 Outlook',
  author: 'Analytics Team',
  date: 'January 2025',
  sections: [
    {
      title: 'Executive Summary',
      content: `This report provides a comprehensive overview of our Q4 2024 performance.
      Key highlights include a 25% increase in revenue, successful expansion into two new
      markets, and the launch of three new product lines. Customer satisfaction scores
      reached an all-time high of 92%, reflecting our continued focus on quality and service.

      The following sections provide detailed analysis of each business unit, financial
      metrics, and strategic initiatives completed during the quarter.`,
    },
    {
      title: 'Financial Performance',
      content: `Revenue for Q4 2024 reached $12.5M, representing a 25% increase over the
      same period last year. Operating margins improved by 3 percentage points to 18%,
      driven by operational efficiencies and favorable product mix.

      Key drivers of growth included strong performance in the enterprise segment and
      successful upselling initiatives in our existing customer base.`,
      charts: [
        { title: 'Monthly Revenue ($M)', data: [3.8, 4.2, 4.5] },
        { title: 'Customer Acquisition', data: [45, 52, 61] },
      ],
    },
    {
      title: 'Strategic Initiatives',
      content: `During Q4, we completed several key strategic initiatives:

      1. Market Expansion: Successfully entered the European and APAC markets
      2. Product Launch: Introduced three new product lines with strong initial adoption
      3. Technology: Completed cloud migration, reducing infrastructure costs by 30%
      4. Talent: Expanded team by 40 new hires across engineering and sales

      These initiatives position us well for continued growth in 2025.`,
    },
    {
      title: 'Outlook and Recommendations',
      content: `Based on current trends and market conditions, we project continued strong
      growth in 2025. Key focus areas include:

      - Scaling operations in new markets
      - Expanding product portfolio through R&D investment
      - Enhancing customer success programs
      - Pursuing strategic partnerships

      We recommend increasing investment in product development and customer success
      to capitalize on market opportunities.`,
    },
  ],
};

generateReport(reportData, 'report.pdf');
```

---

## Python (ReportLab)

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from dataclasses import dataclass
from typing import Optional

@dataclass
class ChartData:
    title: str
    categories: list[str]
    values: list[float]

@dataclass
class ReportSection:
    title: str
    content: str
    chart: Optional[ChartData] = None

@dataclass
class ReportData:
    title: str
    subtitle: str
    author: str
    date: str
    sections: list[ReportSection]

class ReportGenerator:
    def __init__(self, data: ReportData, output_path: str):
        self.data = data
        self.output_path = output_path
        self.page_count = 0
        self.toc_entries = []

        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            'CoverTitle',
            parent=self.styles['Heading1'],
            fontSize=36,
            textColor=colors.white,
            alignment=1,  # Center
            spaceAfter=20,
        ))
        self.styles.add(ParagraphStyle(
            'CoverSubtitle',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.white,
            alignment=1,
        ))
        self.styles.add(ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=12,
        ))
        self.styles.add(ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=4,  # Justify
        ))

    def _header_footer(self, canvas, doc):
        """Add page numbers to all pages except cover."""
        if doc.page > 1:
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.gray)
            canvas.drawCentredString(
                A4[0] / 2,
                20 * mm,
                f'Page {doc.page - 1}'
            )
            canvas.restoreState()

    def _create_cover_page(self) -> list:
        """Generate cover page elements."""
        elements = []

        # Background rectangle (handled differently in platypus)
        # We'll use a drawing
        cover_bg = Drawing(A4[0], A4[1])
        cover_bg.add(Rect(0, 0, A4[0], A4[1], fillColor=colors.HexColor('#2c3e50')))
        elements.append(cover_bg)

        elements.append(Spacer(1, 200))
        elements.append(Paragraph(self.data.title, self.styles['CoverTitle']))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(self.data.subtitle, self.styles['CoverSubtitle']))
        elements.append(Spacer(1, 150))
        elements.append(Paragraph(self.data.author, self.styles['CoverSubtitle']))
        elements.append(Paragraph(self.data.date, self.styles['CoverSubtitle']))
        elements.append(PageBreak())

        return elements

    def _create_toc(self) -> list:
        """Generate table of contents."""
        elements = []
        elements.append(Paragraph('Table of Contents', self.styles['Heading1']))
        elements.append(Spacer(1, 20))

        # TOC entries will be added after we know page numbers
        for i, section in enumerate(self.data.sections):
            toc_line = f'{i + 1}. {section.title}'
            elements.append(Paragraph(toc_line, self.styles['Normal']))
            elements.append(Spacer(1, 8))

        elements.append(PageBreak())
        return elements

    def _create_chart(self, chart_data: ChartData) -> Drawing:
        """Create a bar chart."""
        drawing = Drawing(400, 200)

        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = 300
        chart.height = 125
        chart.data = [chart_data.values]
        chart.categoryAxis.categoryNames = chart_data.categories
        chart.bars[0].fillColor = colors.HexColor('#3498db')
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(chart_data.values) * 1.2

        drawing.add(chart)
        return drawing

    def _create_section(self, index: int, section: ReportSection) -> list:
        """Generate a report section."""
        elements = []

        # Section title
        title = f'{index + 1}. {section.title}'
        elements.append(Paragraph(title, self.styles['SectionTitle']))

        # Content paragraphs
        for para in section.content.split('\n\n'):
            if para.strip():
                elements.append(Paragraph(para.strip(), self.styles['BodyText']))
                elements.append(Spacer(1, 10))

        # Chart if present
        if section.chart:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(
                f'<b>{section.chart.title}</b>',
                self.styles['Normal']
            ))
            elements.append(self._create_chart(section.chart))

        elements.append(PageBreak())
        return elements

    def generate(self):
        """Generate the complete report."""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=25*mm,
        )

        story = []

        # Cover page (simplified - full cover needs canvas drawing)
        story.append(Paragraph(self.data.title, self.styles['Heading1']))
        story.append(Paragraph(self.data.subtitle, self.styles['Normal']))
        story.append(Spacer(1, 50))
        story.append(Paragraph(f'Author: {self.data.author}', self.styles['Normal']))
        story.append(Paragraph(f'Date: {self.data.date}', self.styles['Normal']))
        story.append(PageBreak())

        # Table of contents
        story.extend(self._create_toc())

        # Content sections
        for i, section in enumerate(self.data.sections):
            story.extend(self._create_section(i, section))

        doc.build(story, onFirstPage=self._header_footer,
                  onLaterPages=self._header_footer)

# Usage
report_data = ReportData(
    title='Q4 2024 Performance Report',
    subtitle='Annual Review and 2025 Outlook',
    author='Analytics Team',
    date='January 2025',
    sections=[
        ReportSection(
            title='Executive Summary',
            content='''This report provides a comprehensive overview of our Q4 2024 performance.

Key highlights include a 25% increase in revenue, successful expansion into two new
markets, and the launch of three new product lines.

Customer satisfaction scores reached an all-time high of 92%.''',
        ),
        ReportSection(
            title='Financial Performance',
            content='''Revenue for Q4 2024 reached $12.5M, representing a 25% increase.

Operating margins improved by 3 percentage points to 18%, driven by operational
efficiencies and favorable product mix.''',
            chart=ChartData(
                title='Monthly Revenue ($M)',
                categories=['Oct', 'Nov', 'Dec'],
                values=[3.8, 4.2, 4.5],
            ),
        ),
        ReportSection(
            title='Strategic Initiatives',
            content='''During Q4, we completed several key strategic initiatives:

1. Market Expansion: Successfully entered European and APAC markets
2. Product Launch: Introduced three new product lines
3. Technology: Completed cloud migration, reducing costs by 30%
4. Talent: Expanded team by 40 new hires''',
        ),
    ],
)

generator = ReportGenerator(report_data, 'report.pdf')
generator.generate()
```

---

## Related

- [invoice-template.md](invoice-template.md) - Invoice generation
- [../references/pdf-generation-patterns.md](../references/pdf-generation-patterns.md) - Advanced patterns
