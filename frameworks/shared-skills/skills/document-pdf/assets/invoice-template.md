# Invoice PDF Template

Copy-paste templates for generating invoice PDFs.

---

## Node.js (PDFKit)

```typescript
import PDFDocument from 'pdfkit';
import fs from 'fs';

interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
}

interface InvoiceData {
  invoiceNumber: string;
  date: string;
  dueDate: string;
  company: {
    name: string;
    address: string[];
    email: string;
    phone: string;
  };
  billTo: {
    name: string;
    address: string[];
    email: string;
  };
  items: InvoiceItem[];
  taxRate: number;
  notes?: string;
}

function generateInvoice(data: InvoiceData, outputPath: string): void {
  const doc = new PDFDocument({ size: 'A4', margin: 50 });
  doc.pipe(fs.createWriteStream(outputPath));

  // Header
  doc.fontSize(24).font('Helvetica-Bold').text('INVOICE', { align: 'right' });
  doc.moveDown(0.5);
  doc.fontSize(10).font('Helvetica')
     .text(`Invoice #: ${data.invoiceNumber}`, { align: 'right' })
     .text(`Date: ${data.date}`, { align: 'right' })
     .text(`Due Date: ${data.dueDate}`, { align: 'right' });

  doc.moveDown(2);

  // Company info (left) and Bill To (right)
  const startY = doc.y;

  doc.fontSize(12).font('Helvetica-Bold').text('From:', 50);
  doc.fontSize(10).font('Helvetica')
     .text(data.company.name)
     .text(data.company.address.join('\n'))
     .text(data.company.email)
     .text(data.company.phone);

  doc.y = startY;
  doc.fontSize(12).font('Helvetica-Bold').text('Bill To:', 300);
  doc.fontSize(10).font('Helvetica')
     .text(data.billTo.name, 300)
     .text(data.billTo.address.join('\n'), 300)
     .text(data.billTo.email, 300);

  doc.moveDown(3);

  // Table header
  const tableTop = doc.y;
  const colWidths = { desc: 250, qty: 60, price: 80, total: 80 };

  doc.rect(50, tableTop, 495, 20).fill('#2c3e50');
  doc.fillColor('white').fontSize(10).font('Helvetica-Bold')
     .text('Description', 55, tableTop + 5)
     .text('Qty', 305, tableTop + 5, { width: colWidths.qty, align: 'center' })
     .text('Unit Price', 365, tableTop + 5, { width: colWidths.price, align: 'right' })
     .text('Total', 445, tableTop + 5, { width: colWidths.total, align: 'right' });

  // Table rows
  let y = tableTop + 25;
  let subtotal = 0;

  doc.fillColor('black').font('Helvetica');

  data.items.forEach((item, i) => {
    const lineTotal = item.quantity * item.unitPrice;
    subtotal += lineTotal;

    const bgColor = i % 2 === 0 ? '#f8f9fa' : '#ffffff';
    doc.rect(50, y - 5, 495, 20).fill(bgColor);

    doc.fillColor('black')
       .text(item.description, 55, y)
       .text(item.quantity.toString(), 305, y, { width: colWidths.qty, align: 'center' })
       .text(`$${item.unitPrice.toFixed(2)}`, 365, y, { width: colWidths.price, align: 'right' })
       .text(`$${lineTotal.toFixed(2)}`, 445, y, { width: colWidths.total, align: 'right' });

    y += 20;
  });

  // Totals
  y += 10;
  const tax = subtotal * data.taxRate;
  const total = subtotal + tax;

  doc.font('Helvetica')
     .text('Subtotal:', 365, y, { width: 80, align: 'right' })
     .text(`$${subtotal.toFixed(2)}`, 445, y, { width: 80, align: 'right' });

  y += 15;
  doc.text(`Tax (${(data.taxRate * 100).toFixed(0)}%):`, 365, y, { width: 80, align: 'right' })
     .text(`$${tax.toFixed(2)}`, 445, y, { width: 80, align: 'right' });

  y += 20;
  doc.rect(360, y - 5, 185, 25).fill('#2c3e50');
  doc.fillColor('white').font('Helvetica-Bold')
     .text('Total:', 365, y, { width: 80, align: 'right' })
     .text(`$${total.toFixed(2)}`, 445, y, { width: 80, align: 'right' });

  // Notes
  if (data.notes) {
    doc.fillColor('black').moveDown(4);
    doc.fontSize(10).font('Helvetica-Bold').text('Notes:');
    doc.font('Helvetica').text(data.notes);
  }

  // Footer
  doc.fontSize(8).fillColor('gray')
     .text('Thank you for your business!', 50, 780, { align: 'center' });

  doc.end();
}

// Usage
const invoiceData: InvoiceData = {
  invoiceNumber: 'INV-2025-001',
  date: '2025-01-15',
  dueDate: '2025-02-15',
  company: {
    name: 'Acme Corp',
    address: ['123 Business St', 'Suite 100', 'New York, NY 10001'],
    email: 'billing@acme.com',
    phone: '+1 (555) 123-4567',
  },
  billTo: {
    name: 'Client Company',
    address: ['456 Client Ave', 'Floor 5', 'Los Angeles, CA 90001'],
    email: 'accounts@client.com',
  },
  items: [
    { description: 'Web Development Services', quantity: 40, unitPrice: 150 },
    { description: 'UI/UX Design', quantity: 20, unitPrice: 125 },
    { description: 'Project Management', quantity: 10, unitPrice: 100 },
  ],
  taxRate: 0.08,
  notes: 'Payment is due within 30 days. Please include invoice number with payment.',
};

generateInvoice(invoiceData, 'invoice.pdf');
```

---

## Python (ReportLab)

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from dataclasses import dataclass

@dataclass
class InvoiceItem:
    description: str
    quantity: int
    unit_price: float

@dataclass
class InvoiceData:
    invoice_number: str
    date: str
    due_date: str
    company_name: str
    company_address: list[str]
    company_email: str
    bill_to_name: str
    bill_to_address: list[str]
    bill_to_email: str
    items: list[InvoiceItem]
    tax_rate: float
    notes: str = ''

def generate_invoice(data: InvoiceData, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           leftMargin=20*mm, rightMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                 fontSize=24, alignment=2)  # Right align

    story = []

    # Header
    story.append(Paragraph('INVOICE', title_style))
    story.append(Spacer(1, 10))

    # Invoice details
    invoice_info = [
        [f'Invoice #: {data.invoice_number}'],
        [f'Date: {data.date}'],
        [f'Due Date: {data.due_date}'],
    ]
    info_table = Table(invoice_info, colWidths=[170*mm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # From / Bill To
    addresses = [
        ['From:', 'Bill To:'],
        [data.company_name, data.bill_to_name],
        ['\n'.join(data.company_address), '\n'.join(data.bill_to_address)],
        [data.company_email, data.bill_to_email],
    ]
    addr_table = Table(addresses, colWidths=[85*mm, 85*mm])
    addr_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(addr_table)
    story.append(Spacer(1, 30))

    # Items table
    items_data = [['Description', 'Qty', 'Unit Price', 'Total']]
    subtotal = 0

    for item in data.items:
        line_total = item.quantity * item.unit_price
        subtotal += line_total
        items_data.append([
            item.description,
            str(item.quantity),
            f'${item.unit_price:.2f}',
            f'${line_total:.2f}',
        ])

    # Add totals
    tax = subtotal * data.tax_rate
    total = subtotal + tax

    items_data.extend([
        ['', '', 'Subtotal:', f'${subtotal:.2f}'],
        ['', '', f'Tax ({data.tax_rate*100:.0f}%):', f'${tax:.2f}'],
        ['', '', 'Total:', f'${total:.2f}'],
    ])

    items_table = Table(items_data, colWidths=[90*mm, 20*mm, 30*mm, 30*mm])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Body
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),

        # Alternating rows
        ('BACKGROUND', (0, 1), (-1, -4), colors.HexColor('#f8f9fa')),

        # Grid
        ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),

        # Totals
        ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (2, -3), (-1, -3), 1, colors.black),
        ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (2, -1), (-1, -1), colors.white),
    ]))
    story.append(items_table)

    # Notes
    if data.notes:
        story.append(Spacer(1, 30))
        story.append(Paragraph('<b>Notes:</b>', styles['Normal']))
        story.append(Paragraph(data.notes, styles['Normal']))

    doc.build(story)

# Usage
invoice_data = InvoiceData(
    invoice_number='INV-2025-001',
    date='2025-01-15',
    due_date='2025-02-15',
    company_name='Acme Corp',
    company_address=['123 Business St', 'Suite 100', 'New York, NY 10001'],
    company_email='billing@acme.com',
    bill_to_name='Client Company',
    bill_to_address=['456 Client Ave', 'Floor 5', 'Los Angeles, CA 90001'],
    bill_to_email='accounts@client.com',
    items=[
        InvoiceItem('Web Development Services', 40, 150.00),
        InvoiceItem('UI/UX Design', 20, 125.00),
        InvoiceItem('Project Management', 10, 100.00),
    ],
    tax_rate=0.08,
    notes='Payment is due within 30 days. Please include invoice number with payment.',
)

generate_invoice(invoice_data, 'invoice.pdf')
```

---

## Related

- [report-template.md](report-template.md) - Multi-page report generation
- [../references/pdf-generation-patterns.md](../references/pdf-generation-patterns.md) - Advanced patterns
