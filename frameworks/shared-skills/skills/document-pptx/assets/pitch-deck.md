# Pitch Deck Template — 10-Slide Startup Presentation

Complete, copy-paste Python code for generating a startup pitch deck.

---

## Quick Start

```bash
pip install python-pptx
```

```python
python pitch_deck.py
# Output: pitch_deck.pptx
```

---

## Full Template Code

```python
"""
Pitch Deck Generator
Creates a 10-slide startup pitch deck following YC format.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RgbColor


# ============================================================
# CONFIGURATION - Edit these values
# ============================================================

COMPANY_NAME = "TechCorp"
TAGLINE = "AI-powered solutions for enterprise"
FOUNDER_NAMES = "Jane Doe & John Smith"
CONTACT_EMAIL = "founders@techcorp.com"

# Brand colors
PRIMARY_COLOR = RgbColor(0x00, 0x66, 0xCC)
SECONDARY_COLOR = RgbColor(0x00, 0x99, 0xFF)
DARK_COLOR = RgbColor(0x33, 0x33, 0x33)
LIGHT_COLOR = RgbColor(0xF5, 0xF5, 0xF5)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_title_slide(prs, title: str, subtitle: str):
    """Slide 1: Title"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(1))
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(44)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = DARK_COLOR
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.2), Inches(9), Inches(0.5))
    tf = sub_box.text_frame
    tf.paragraphs[0].text = subtitle
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.color.rgb = PRIMARY_COLOR
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    return slide


def add_content_slide(prs, title: str, bullets: list):
    """Standard content slide with bullets"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = DARK_COLOR

    # Bullets
    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(4.5))
    tf = content_box.text_frame
    tf.word_wrap = True

    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = f"• {bullet}"
        p.font.size = Pt(20)
        p.font.color.rgb = DARK_COLOR
        p.space_before = Pt(12)

    return slide


def add_metric_slide(prs, title: str, metrics: list):
    """Slide with 3-4 big metrics"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    # Metrics in row
    num_metrics = len(metrics)
    box_width = 9 / num_metrics

    for i, (value, label) in enumerate(metrics):
        x = Inches(0.5 + i * box_width)

        # Value
        val_box = slide.shapes.add_textbox(x, Inches(2), Inches(box_width - 0.2), Inches(1))
        tf = val_box.text_frame
        tf.paragraphs[0].text = value
        tf.paragraphs[0].font.size = Pt(48)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = PRIMARY_COLOR
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Label
        lbl_box = slide.shapes.add_textbox(x, Inches(3), Inches(box_width - 0.2), Inches(0.5))
        tf = lbl_box.text_frame
        tf.paragraphs[0].text = label
        tf.paragraphs[0].font.size = Pt(16)
        tf.paragraphs[0].font.color.rgb = DARK_COLOR
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    return slide


# ============================================================
# BUILD PRESENTATION
# ============================================================

def create_pitch_deck():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)  # 16:9

    # Slide 1: Title
    add_title_slide(prs, COMPANY_NAME, TAGLINE)

    # Slide 2: Problem
    add_content_slide(prs, "The Problem", [
        "Enterprises waste 40% of time on manual data processing",
        "Current solutions are expensive and require technical expertise",
        "No single platform integrates with existing workflows",
        "Compliance and security concerns block adoption"
    ])

    # Slide 3: Solution
    add_content_slide(prs, "Our Solution", [
        "AI-powered automation platform for enterprise data",
        "No-code interface accessible to business users",
        "Seamless integration with 100+ enterprise systems",
        "SOC2 and GDPR compliant from day one"
    ])

    # Slide 4: Market Size
    add_metric_slide(prs, "Market Opportunity", [
        ("$50B", "TAM"),
        ("$12B", "SAM"),
        ("$2B", "SOM"),
    ])

    # Slide 5: Business Model
    add_content_slide(prs, "Business Model", [
        "SaaS subscription: $500-5,000/month per enterprise",
        "Usage-based pricing for API calls",
        "Professional services for custom integrations",
        "90% gross margin at scale"
    ])

    # Slide 6: Traction
    add_metric_slide(prs, "Traction", [
        ("$1.2M", "ARR"),
        ("150%", "YoY Growth"),
        ("45", "Enterprise Clients"),
        ("95%", "Retention"),
    ])

    # Slide 7: Team (simple version)
    add_content_slide(prs, "Team", [
        "Jane Doe, CEO - 10 years enterprise SaaS (ex-Salesforce)",
        "John Smith, CTO - ML PhD, ex-Google AI",
        "Sarah Lee, VP Sales - Built $50M ARR at Datadog",
        "15 engineers from FAANG companies"
    ])

    # Slide 8: Competition
    add_content_slide(prs, "Competitive Landscape", [
        "Legacy vendors (SAP, Oracle): Expensive, slow, complex",
        "Point solutions (Zapier, Workato): Limited AI, no enterprise features",
        "Our advantage: AI-native + enterprise-grade + simple UX",
        "First mover in AI-powered enterprise automation"
    ])

    # Slide 9: Financials (chart)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "Financial Projections"
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    chart_data = CategoryChartData()
    chart_data.categories = ['2024', '2025', '2026', '2027', '2028']
    chart_data.add_series('ARR ($M)', (1.2, 4, 12, 30, 75))

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(1), Inches(1.3), Inches(8), Inches(4),
        chart_data
    ).chart
    chart.has_legend = False

    # Slide 10: Ask
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    ask_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(9), Inches(1))
    tf = ask_box.text_frame
    tf.paragraphs[0].text = "Raising $5M Series A"
    tf.paragraphs[0].font.size = Pt(40)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = PRIMARY_COLOR
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    use_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.8), Inches(9), Inches(1.5))
    tf = use_box.text_frame
    tf.paragraphs[0].text = "Use of Funds:"
    tf.paragraphs[0].font.size = Pt(20)
    tf.paragraphs[0].font.bold = True

    for item in ["50% Engineering & Product", "30% Sales & Marketing", "20% Operations"]:
        p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(18)

    contact_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(9), Inches(0.5))
    tf = contact_box.text_frame
    tf.paragraphs[0].text = f"{FOUNDER_NAMES} | {CONTACT_EMAIL}"
    tf.paragraphs[0].font.size = Pt(16)
    tf.paragraphs[0].font.color.rgb = DARK_COLOR
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Save
    prs.save('pitch_deck.pptx')
    print("Created: pitch_deck.pptx")


if __name__ == "__main__":
    create_pitch_deck()
```

---

## Slide Structure Reference

| # | Slide | Purpose | Key Elements |
|---|-------|---------|--------------|
| 1 | Title | First impression | Company name, tagline |
| 2 | Problem | Pain point | 3-4 bullets, quantified impact |
| 3 | Solution | Your product | Features tied to problems |
| 4 | Market | Opportunity size | TAM/SAM/SOM metrics |
| 5 | Business Model | Revenue strategy | Pricing, margins |
| 6 | Traction | Proof | ARR, growth, customers |
| 7 | Team | Credibility | Relevant experience |
| 8 | Competition | Positioning | Differentiation matrix |
| 9 | Financials | Projections | 5-year chart |
| 10 | Ask | Call to action | Amount, use of funds |

---

## Customization Tips

### Add Logo
```python
slide.shapes.add_picture('logo.png', Inches(0.3), Inches(0.2), width=Inches(1.5))
```

### Add Footer to All Slides
```python
for slide in prs.slides:
    footer = slide.shapes.add_textbox(Inches(0.3), Inches(5.3), Inches(9.4), Inches(0.3))
    tf = footer.text_frame
    tf.paragraphs[0].text = "Confidential | TechCorp 2025"
    tf.paragraphs[0].font.size = Pt(10)
    tf.paragraphs[0].font.color.rgb = RgbColor(0x99, 0x99, 0x99)
```

### Export to PDF
```python
# Requires LibreOffice or unoconv
import subprocess
subprocess.run(['unoconv', '-f', 'pdf', 'pitch_deck.pptx'])
```

---

## Related Resources

- [../references/pptx-layouts.md](../references/pptx-layouts.md) — Custom themes
- [../references/pptx-charts.md](../references/pptx-charts.md) — Financial charts
- [quarterly-review.md](quarterly-review.md) — Business review template
