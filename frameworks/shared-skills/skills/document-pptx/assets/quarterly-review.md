# Quarterly Review Template — 8-Slide Business Presentation

Complete, copy-paste Python code for generating a quarterly business review deck.

---

## Quick Start

```bash
pip install python-pptx pandas
```

```python
python quarterly_review.py
# Output: q4_2025_review.pptx
```

---

## Full Template Code

```python
"""
Quarterly Business Review Generator
Creates an 8-slide QBR deck with dynamic data.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RgbColor
import pandas as pd
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

QUARTER = "Q4"
YEAR = "2025"
COMPANY_NAME = "TechCorp"
PRESENTER = "Product Team"

# Brand colors
PRIMARY = RgbColor(0x00, 0x66, 0xCC)
SECONDARY = RgbColor(0x00, 0x99, 0xFF)
SUCCESS = RgbColor(0x28, 0xA7, 0x45)
WARNING = RgbColor(0xFF, 0xC1, 0x07)
DANGER = RgbColor(0xDC, 0x35, 0x45)
DARK = RgbColor(0x33, 0x33, 0x33)


# ============================================================
# SAMPLE DATA (Replace with real data)
# ============================================================

kpis = {
    'revenue': {'value': '$4.2M', 'change': '+25%', 'status': 'success'},
    'customers': {'value': '1,250', 'change': '+180', 'status': 'success'},
    'nps': {'value': '72', 'change': '+5', 'status': 'success'},
    'churn': {'value': '2.1%', 'change': '-0.3%', 'status': 'success'},
}

monthly_revenue = pd.DataFrame({
    'Month': ['Oct', 'Nov', 'Dec'],
    'Revenue': [1.3, 1.4, 1.5],
    'Target': [1.2, 1.3, 1.4]
})

product_updates = [
    "Launched AI-powered analytics dashboard",
    "Reduced API latency by 40%",
    "Added SSO support for enterprise clients",
    "Released mobile app v2.0",
]

customer_wins = [
    ("Acme Corp", "$500K ARR", "Enterprise"),
    ("GlobalTech", "$250K ARR", "Mid-Market"),
    ("StartupXYZ", "$50K ARR", "Growth"),
]

challenges = [
    "Enterprise sales cycle longer than expected (avg 6 months)",
    "Technical debt slowing feature velocity",
    "Hiring for senior engineering roles",
]

next_quarter_goals = [
    "Launch v3.0 with workflow automation",
    "Achieve $5M ARR milestone",
    "Expand sales team by 5 reps",
    "Complete SOC2 Type II certification",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_title_slide(prs):
    """Slide 1: Title + Agenda"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(9), Inches(1))
    tf = title_box.text_frame
    tf.paragraphs[0].text = f"{QUARTER} {YEAR} Business Review"
    tf.paragraphs[0].font.size = Pt(40)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = DARK
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Presenter
    sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.8), Inches(9), Inches(0.5))
    tf = sub_box.text_frame
    tf.paragraphs[0].text = f"Presented by {PRESENTER}"
    tf.paragraphs[0].font.size = Pt(20)
    tf.paragraphs[0].font.color.rgb = PRIMARY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Date
    date_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.5), Inches(9), Inches(0.5))
    tf = date_box.text_frame
    tf.paragraphs[0].text = datetime.now().strftime("%B %d, %Y")
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = DARK
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    return slide


def add_kpi_dashboard(prs):
    """Slide 2: Executive Summary / KPIs"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "Executive Summary"
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    # KPI cards
    metrics = [
        ('Revenue', kpis['revenue']),
        ('Customers', kpis['customers']),
        ('NPS', kpis['nps']),
        ('Churn', kpis['churn']),
    ]

    for i, (label, data) in enumerate(metrics):
        x = Inches(0.5 + i * 2.4)
        y = Inches(1.5)

        # Value
        val_box = slide.shapes.add_textbox(x, y, Inches(2.2), Inches(1))
        tf = val_box.text_frame
        tf.paragraphs[0].text = data['value']
        tf.paragraphs[0].font.size = Pt(36)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = PRIMARY
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Label
        lbl_box = slide.shapes.add_textbox(x, Inches(2.5), Inches(2.2), Inches(0.4))
        tf = lbl_box.text_frame
        tf.paragraphs[0].text = label
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.color.rgb = DARK
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Change indicator
        status_color = SUCCESS if data['status'] == 'success' else (WARNING if data['status'] == 'warning' else DANGER)
        chg_box = slide.shapes.add_textbox(x, Inches(2.9), Inches(2.2), Inches(0.4))
        tf = chg_box.text_frame
        tf.paragraphs[0].text = data['change']
        tf.paragraphs[0].font.size = Pt(16)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = status_color
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    return slide


def add_revenue_slide(prs):
    """Slide 3: Revenue & Growth"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "Revenue & Growth"
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    # Chart
    chart_data = CategoryChartData()
    chart_data.categories = monthly_revenue['Month'].tolist()
    chart_data.add_series('Actual', monthly_revenue['Revenue'].tolist())
    chart_data.add_series('Target', monthly_revenue['Target'].tolist())

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(0.5), Inches(1.3), Inches(6), Inches(4),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.include_in_layout = False

    # Key insight
    insight_box = slide.shapes.add_textbox(Inches(6.8), Inches(1.5), Inches(2.7), Inches(3))
    tf = insight_box.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Key Insight"
    tf.paragraphs[0].font.size = Pt(16)
    tf.paragraphs[0].font.bold = True

    p = tf.add_paragraph()
    p.text = "Exceeded target by 7% in Q4. Enterprise deals drove growth."
    p.font.size = Pt(14)
    p.space_before = Pt(8)

    return slide


def add_product_slide(prs):
    """Slide 4: Product Updates"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "Product Updates"
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(4))
    tf = content_box.text_frame

    for i, update in enumerate(product_updates):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = f"[check] {update}"
        p.font.size = Pt(20)
        p.font.color.rgb = DARK
        p.space_before = Pt(16)

    return slide


def add_customers_slide(prs):
    """Slide 5: Customer Highlights"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "Customer Highlights"
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    # Table
    rows = len(customer_wins) + 1
    cols = 3
    table = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5), Inches(9), Inches(2.5)).table

    # Headers
    headers = ['Customer', 'Contract Value', 'Segment']
    for col, header in enumerate(headers):
        cell = table.cell(0, col)
        cell.text = header
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(14)

    # Data
    for row, (customer, value, segment) in enumerate(customer_wins, 1):
        table.cell(row, 0).text = customer
        table.cell(row, 1).text = value
        table.cell(row, 2).text = segment
        for col in range(3):
            table.cell(row, col).text_frame.paragraphs[0].font.size = Pt(14)

    return slide


def add_challenges_slide(prs):
    """Slide 6: Challenges & Learnings"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = "Challenges & Learnings"
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(4))
    tf = content_box.text_frame

    for i, challenge in enumerate(challenges):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = f"• {challenge}"
        p.font.size = Pt(20)
        p.font.color.rgb = DARK
        p.space_before = Pt(16)

    return slide


def add_goals_slide(prs):
    """Slide 7: Next Quarter Goals"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    tf.paragraphs[0].text = f"Q1 {int(YEAR)+1 if QUARTER == 'Q4' else YEAR} Goals"
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True

    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(4))
    tf = content_box.text_frame

    for i, goal in enumerate(next_quarter_goals):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = f"→ {goal}"
        p.font.size = Pt(20)
        p.font.color.rgb = PRIMARY
        p.space_before = Pt(16)

    return slide


def add_qa_slide(prs):
    """Slide 8: Q&A"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    qa_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(1.5))
    tf = qa_box.text_frame
    tf.paragraphs[0].text = "Questions?"
    tf.paragraphs[0].font.size = Pt(48)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = PRIMARY
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    contact_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.8), Inches(9), Inches(0.5))
    tf = contact_box.text_frame
    tf.paragraphs[0].text = f"{COMPANY_NAME} | {QUARTER} {YEAR}"
    tf.paragraphs[0].font.size = Pt(16)
    tf.paragraphs[0].font.color.rgb = DARK
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    return slide


# ============================================================
# BUILD PRESENTATION
# ============================================================

def create_quarterly_review():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)

    add_title_slide(prs)
    add_kpi_dashboard(prs)
    add_revenue_slide(prs)
    add_product_slide(prs)
    add_customers_slide(prs)
    add_challenges_slide(prs)
    add_goals_slide(prs)
    add_qa_slide(prs)

    filename = f'{QUARTER.lower()}_{YEAR}_review.pptx'
    prs.save(filename)
    print(f"Created: {filename}")


if __name__ == "__main__":
    create_quarterly_review()
```

---

## Slide Structure Reference

| # | Slide | Purpose | Data Source |
|---|-------|---------|-------------|
| 1 | Title | Set context | Config vars |
| 2 | Executive Summary | KPIs at a glance | `kpis` dict |
| 3 | Revenue & Growth | Financial trends | `monthly_revenue` DataFrame |
| 4 | Product Updates | What shipped | `product_updates` list |
| 5 | Customer Highlights | Wins & logos | `customer_wins` list |
| 6 | Challenges | Honest retrospective | `challenges` list |
| 7 | Next Quarter | Forward-looking | `next_quarter_goals` list |
| 8 | Q&A | Discussion | None |

---

## Integration with Real Data

### From Database

```python
import sqlite3

conn = sqlite3.connect('metrics.db')
monthly_revenue = pd.read_sql('''
    SELECT strftime('%b', date) as Month,
           SUM(revenue) as Revenue,
           SUM(target) as Target
    FROM sales
    WHERE quarter = 'Q4' AND year = 2025
    GROUP BY Month
''', conn)
```

### From API

```python
import requests

response = requests.get('https://api.company.com/kpis', headers={'Authorization': 'Bearer ...'})
kpis = response.json()
```

### From CSV

```python
monthly_revenue = pd.read_csv('revenue.csv')
customer_wins = pd.read_csv('wins.csv').values.tolist()
```

---

## Related Resources

- [../references/pptx-charts.md](../references/pptx-charts.md) — Advanced chart styling
- [../references/pptx-layouts.md](../references/pptx-layouts.md) — Custom themes
- [pitch-deck.md](pitch-deck.md) — External presentation format
