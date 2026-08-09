# Data Dashboard Template

Copy-paste template for generating Excel dashboards with charts, KPIs, and data tables.

---

## KPI Dashboard

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.utils import get_column_letter

def create_kpi_dashboard(data: dict, output_path: str = 'dashboard.xlsx'):
    """
    Generate a KPI dashboard with charts and metrics.

    Args:
        data: Dictionary with KPIs, trends, and breakdowns
        output_path: Output file path

    Example data:
        {
            'title': 'Q4 2024 Sales Dashboard',
            'kpis': [
                {'name': 'Total Revenue', 'value': 1250000, 'target': 1200000, 'format': 'currency'},
                {'name': 'Orders', 'value': 3420, 'target': 3000, 'format': 'number'},
                {'name': 'Conversion Rate', 'value': 0.032, 'target': 0.03, 'format': 'percent'},
                {'name': 'Avg Order Value', 'value': 365.50, 'target': 350, 'format': 'currency'},
            ],
            'monthly_trend': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'revenue': [85000, 92000, 88000, 95000, 102000, 98000,
                           105000, 112000, 108000, 115000, 125000, 125000],
                'orders': [240, 260, 250, 270, 290, 280, 300, 320, 310, 330, 360, 360],
            },
            'category_breakdown': [
                ('Electronics', 450000),
                ('Clothing', 380000),
                ('Home & Garden', 250000),
                ('Sports', 170000),
            ],
            'top_products': [
                ('Widget Pro X', 2500, 125000),
                ('Smart Watch Elite', 1800, 89000),
                ('Wireless Earbuds', 3200, 64000),
                ('Laptop Stand', 2100, 52000),
                ('Phone Case Premium', 4500, 45000),
            ]
        }
    """
    wb = Workbook()
    ws = wb.active
    ws.title = 'Dashboard'

    # Styles
    title_font = Font(bold=True, size=16, color='FFFFFF')
    header_font = Font(bold=True, size=11)
    kpi_value_font = Font(bold=True, size=24)
    kpi_label_font = Font(size=10, color='666666')
    section_fill = PatternFill(start_color='4472C4', fill_type='solid')
    kpi_positive_fill = PatternFill(start_color='C6EFCE', fill_type='solid')
    kpi_negative_fill = PatternFill(start_color='FFC7CE', fill_type='solid')

    # Page setup
    ws.sheet_view.showGridLines = False
    for col in range(1, 15):
        ws.column_dimensions[get_column_letter(col)].width = 12

    row = 1

    # ═══════════════════════════════════════════════════════════
    # TITLE SECTION
    # ═══════════════════════════════════════════════════════════

    ws.merge_cells('A1:N1')
    ws['A1'] = data['title']
    ws['A1'].font = title_font
    ws['A1'].fill = section_fill
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 35
    row = 3

    # ═══════════════════════════════════════════════════════════
    # KPI CARDS
    # ═══════════════════════════════════════════════════════════

    kpi_start_col = 1
    for i, kpi in enumerate(data['kpis']):
        col = kpi_start_col + (i * 3)

        # KPI Card background
        for r in range(row, row + 4):
            for c in range(col, col + 3):
                cell = ws.cell(row=r, column=c)
                cell.fill = PatternFill(start_color='F2F2F2', fill_type='solid')

        # KPI Name
        ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+2)
        cell = ws.cell(row=row, column=col)
        cell.value = kpi['name']
        cell.font = kpi_label_font
        cell.alignment = Alignment(horizontal='center')

        # KPI Value
        ws.merge_cells(start_row=row+1, start_column=col, end_row=row+1, end_column=col+2)
        cell = ws.cell(row=row+1, column=col)

        if kpi['format'] == 'currency':
            cell.value = kpi['value']
            cell.number_format = '$#,##0'
        elif kpi['format'] == 'percent':
            cell.value = kpi['value']
            cell.number_format = '0.0%'
        else:
            cell.value = kpi['value']
            cell.number_format = '#,##0'

        cell.font = kpi_value_font
        cell.alignment = Alignment(horizontal='center')

        # Target comparison
        ws.merge_cells(start_row=row+2, start_column=col, end_row=row+2, end_column=col+2)
        cell = ws.cell(row=row+2, column=col)

        if kpi['value'] >= kpi['target']:
            variance = (kpi['value'] - kpi['target']) / kpi['target']
            cell.value = f"+{variance:.1%} vs target"
            cell.font = Font(color='006400', size=10)
        else:
            variance = (kpi['target'] - kpi['value']) / kpi['target']
            cell.value = f"-{variance:.1%} vs target"
            cell.font = Font(color='8B0000', size=10)

        cell.alignment = Alignment(horizontal='center')

    row += 5

    # ═══════════════════════════════════════════════════════════
    # TREND CHART (Line)
    # ═══════════════════════════════════════════════════════════

    # Write trend data
    trend_data_row = row
    ws.cell(row=row, column=1, value='Month')
    ws.cell(row=row, column=2, value='Revenue')
    ws.cell(row=row, column=3, value='Orders')

    for i, label in enumerate(data['monthly_trend']['labels']):
        ws.cell(row=row+1+i, column=1, value=label)
        ws.cell(row=row+1+i, column=2, value=data['monthly_trend']['revenue'][i])
        ws.cell(row=row+1+i, column=3, value=data['monthly_trend']['orders'][i])

    # Create line chart
    chart = LineChart()
    chart.title = 'Monthly Revenue Trend'
    chart.style = 10
    chart.y_axis.title = 'Revenue ($)'
    chart.x_axis.title = 'Month'

    data_ref = Reference(ws, min_col=2, min_row=trend_data_row,
                         max_row=trend_data_row+12, max_col=2)
    cats = Reference(ws, min_col=1, min_row=trend_data_row+1,
                     max_row=trend_data_row+12)

    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats)
    chart.series[0].smooth = True
    chart.width = 18
    chart.height = 10

    ws.add_chart(chart, 'E8')

    row += 15

    # ═══════════════════════════════════════════════════════════
    # CATEGORY BREAKDOWN (Pie Chart)
    # ═══════════════════════════════════════════════════════════

    cat_data_row = row
    ws.cell(row=row, column=1, value='Category')
    ws.cell(row=row, column=2, value='Revenue')

    for i, (category, revenue) in enumerate(data['category_breakdown']):
        ws.cell(row=row+1+i, column=1, value=category)
        ws.cell(row=row+1+i, column=2, value=revenue)

    pie_chart = PieChart()
    pie_chart.title = 'Revenue by Category'

    data_ref = Reference(ws, min_col=2, min_row=cat_data_row,
                         max_row=cat_data_row+len(data['category_breakdown']))
    labels = Reference(ws, min_col=1, min_row=cat_data_row+1,
                       max_row=cat_data_row+len(data['category_breakdown']))

    pie_chart.add_data(data_ref, titles_from_data=True)
    pie_chart.set_categories(labels)

    pie_chart.dataLabels = DataLabelList()
    pie_chart.dataLabels.showPercent = True
    pie_chart.dataLabels.showCatName = True
    pie_chart.dataLabels.showVal = False

    pie_chart.width = 10
    pie_chart.height = 10

    ws.add_chart(pie_chart, 'A23')

    # ═══════════════════════════════════════════════════════════
    # TOP PRODUCTS TABLE
    # ═══════════════════════════════════════════════════════════

    table_row = row
    table_col = 5

    # Headers
    headers = ['Product', 'Units Sold', 'Revenue']
    for i, header in enumerate(headers):
        cell = ws.cell(row=table_row, column=table_col+i)
        cell.value = header
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='4472C4', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')

    # Data rows
    for i, (product, units, revenue) in enumerate(data['top_products']):
        row_num = table_row + 1 + i
        ws.cell(row=row_num, column=table_col, value=product)
        ws.cell(row=row_num, column=table_col+1, value=units).number_format = '#,##0'
        ws.cell(row=row_num, column=table_col+2, value=revenue).number_format = '$#,##0'

        # Alternating row colors
        if i % 2 == 0:
            for c in range(table_col, table_col+3):
                ws.cell(row=row_num, column=c).fill = PatternFill(
                    start_color='F2F2F2', fill_type='solid'
                )

    # Adjust column widths for table
    ws.column_dimensions[get_column_letter(table_col)].width = 20
    ws.column_dimensions[get_column_letter(table_col+1)].width = 12
    ws.column_dimensions[get_column_letter(table_col+2)].width = 12

    # Hide raw data columns
    ws.column_dimensions['A'].hidden = False
    ws.column_dimensions['B'].hidden = False
    ws.column_dimensions['C'].hidden = False

    wb.save(output_path)
    return output_path


# Example usage
if __name__ == '__main__':
    sample_data = {
        'title': 'Q4 2024 Sales Dashboard',
        'kpis': [
            {'name': 'Total Revenue', 'value': 1250000, 'target': 1200000, 'format': 'currency'},
            {'name': 'Orders', 'value': 3420, 'target': 3000, 'format': 'number'},
            {'name': 'Conversion Rate', 'value': 0.032, 'target': 0.03, 'format': 'percent'},
            {'name': 'Avg Order Value', 'value': 365.50, 'target': 350, 'format': 'currency'},
        ],
        'monthly_trend': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'revenue': [85000, 92000, 88000, 95000, 102000, 98000,
                       105000, 112000, 108000, 115000, 125000, 125000],
            'orders': [240, 260, 250, 270, 290, 280, 300, 320, 310, 330, 360, 360],
        },
        'category_breakdown': [
            ('Electronics', 450000),
            ('Clothing', 380000),
            ('Home & Garden', 250000),
            ('Sports', 170000),
        ],
        'top_products': [
            ('Widget Pro X', 2500, 125000),
            ('Smart Watch Elite', 1800, 89000),
            ('Wireless Earbuds', 3200, 64000),
            ('Laptop Stand', 2100, 52000),
            ('Phone Case Premium', 4500, 45000),
        ]
    }

    create_kpi_dashboard(sample_data)
```

---

## Sales Report Dashboard

```python
def create_sales_dashboard(sales_data: list, output_path: str = 'sales_dashboard.xlsx'):
    """
    Generate sales dashboard from transaction data.

    Args:
        sales_data: List of sales records
        output_path: Output file path

    Example sales_data:
        [
            {'date': '2024-01-15', 'product': 'Widget A', 'category': 'Electronics',
             'quantity': 5, 'unit_price': 99.99, 'region': 'North'},
            ...
        ]
    """
    import pandas as pd
    from datetime import datetime

    # Convert to DataFrame for analysis
    df = pd.DataFrame(sales_data)
    df['date'] = pd.to_datetime(df['date'])
    df['revenue'] = df['quantity'] * df['unit_price']
    df['month'] = df['date'].dt.strftime('%Y-%m')

    wb = Workbook()

    # ═══════════════════════════════════════════════════════════
    # SUMMARY SHEET
    # ═══════════════════════════════════════════════════════════

    ws_summary = wb.active
    ws_summary.title = 'Summary'

    # KPIs
    total_revenue = df['revenue'].sum()
    total_orders = len(df)
    avg_order_value = df['revenue'].mean()
    top_category = df.groupby('category')['revenue'].sum().idxmax()

    kpis = [
        ('Total Revenue', total_revenue, '$#,##0.00'),
        ('Total Orders', total_orders, '#,##0'),
        ('Avg Order Value', avg_order_value, '$#,##0.00'),
        ('Top Category', top_category, '@'),
    ]

    ws_summary['A1'] = 'Sales Dashboard Summary'
    ws_summary['A1'].font = Font(bold=True, size=16)

    for i, (label, value, fmt) in enumerate(kpis):
        ws_summary.cell(row=3+i, column=1, value=label)
        cell = ws_summary.cell(row=3+i, column=2, value=value)
        if fmt != '@':
            cell.number_format = fmt

    # Monthly trend
    monthly = df.groupby('month')['revenue'].sum().reset_index()

    row = 10
    ws_summary.cell(row=row, column=1, value='Month')
    ws_summary.cell(row=row, column=2, value='Revenue')

    for i, (_, month_row) in enumerate(monthly.iterrows()):
        ws_summary.cell(row=row+1+i, column=1, value=month_row['month'])
        ws_summary.cell(row=row+1+i, column=2, value=month_row['revenue'])

    # Add trend chart
    chart = BarChart()
    chart.title = 'Monthly Revenue'
    chart.type = 'col'

    data_ref = Reference(ws_summary, min_col=2, min_row=row,
                         max_row=row+len(monthly))
    cats = Reference(ws_summary, min_col=1, min_row=row+1,
                     max_row=row+len(monthly))

    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats)
    chart.width = 15
    chart.height = 8

    ws_summary.add_chart(chart, 'D3')

    # ═══════════════════════════════════════════════════════════
    # RAW DATA SHEET
    # ═══════════════════════════════════════════════════════════

    ws_data = wb.create_sheet('Raw Data')

    # Headers
    headers = ['Date', 'Product', 'Category', 'Quantity', 'Unit Price', 'Revenue', 'Region']
    for i, header in enumerate(headers, 1):
        cell = ws_data.cell(row=1, column=i, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color='4472C4', fill_type='solid')
        cell.font = Font(bold=True, color='FFFFFF')

    # Data
    for i, record in enumerate(sales_data, 2):
        ws_data.cell(row=i, column=1, value=record['date'])
        ws_data.cell(row=i, column=2, value=record['product'])
        ws_data.cell(row=i, column=3, value=record['category'])
        ws_data.cell(row=i, column=4, value=record['quantity'])
        ws_data.cell(row=i, column=5, value=record['unit_price']).number_format = '$#,##0.00'
        revenue = record['quantity'] * record['unit_price']
        ws_data.cell(row=i, column=6, value=revenue).number_format = '$#,##0.00'
        ws_data.cell(row=i, column=7, value=record['region'])

    # Auto-filter
    ws_data.auto_filter.ref = f'A1:G{len(sales_data)+1}'

    # Freeze header row
    ws_data.freeze_panes = 'A2'

    wb.save(output_path)
    return output_path
```

---

## Project Status Dashboard

```python
def create_project_dashboard(projects: list, output_path: str = 'project_dashboard.xlsx'):
    """
    Generate project status dashboard.

    Args:
        projects: List of project dictionaries

    Example:
        [
            {
                'name': 'Website Redesign',
                'status': 'In Progress',
                'progress': 0.65,
                'budget': 50000,
                'spent': 32000,
                'due_date': '2024-03-15',
                'owner': 'John Smith'
            },
            ...
        ]
    """
    from openpyxl.formatting.rule import DataBarRule, FormulaRule

    wb = Workbook()
    ws = wb.active
    ws.title = 'Projects'

    # Styles
    header_fill = PatternFill(start_color='4472C4', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')

    # Status colors
    status_colors = {
        'Completed': 'C6EFCE',
        'In Progress': 'FFEB9C',
        'At Risk': 'FFC7CE',
        'Not Started': 'F2F2F2',
    }

    # Headers
    headers = ['Project', 'Status', 'Progress', 'Budget', 'Spent', 'Remaining', 'Due Date', 'Owner']
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 12
    ws.column_dimensions['H'].width = 15

    for i, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=i, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    # Data
    for i, project in enumerate(projects, 2):
        ws.cell(row=i, column=1, value=project['name'])

        # Status with color
        status_cell = ws.cell(row=i, column=2, value=project['status'])
        status_cell.fill = PatternFill(
            start_color=status_colors.get(project['status'], 'FFFFFF'),
            fill_type='solid'
        )
        status_cell.alignment = Alignment(horizontal='center')

        # Progress
        ws.cell(row=i, column=3, value=project['progress']).number_format = '0%'

        # Budget
        ws.cell(row=i, column=4, value=project['budget']).number_format = '$#,##0'
        ws.cell(row=i, column=5, value=project['spent']).number_format = '$#,##0'

        # Remaining (formula)
        ws.cell(row=i, column=6, value=f'=D{i}-E{i}').number_format = '$#,##0'

        # Due date
        ws.cell(row=i, column=7, value=project['due_date'])

        # Owner
        ws.cell(row=i, column=8, value=project['owner'])

    # Add data bars for progress
    ws.conditional_formatting.add(
        f'C2:C{len(projects)+1}',
        DataBarRule(
            start_type='num', start_value=0,
            end_type='num', end_value=1,
            color='4472C4'
        )
    )

    # Highlight overbudget projects
    over_budget_fill = PatternFill(start_color='FFC7CE', fill_type='solid')
    ws.conditional_formatting.add(
        f'F2:F{len(projects)+1}',
        FormulaRule(formula=['F2<0'], fill=over_budget_fill)
    )

    # Freeze header
    ws.freeze_panes = 'A2'

    # Auto-filter
    ws.auto_filter.ref = f'A1:H{len(projects)+1}'

    wb.save(output_path)
    return output_path
```

---

## Usage Pattern

```python
# Import templates
from dashboard_templates import (
    create_kpi_dashboard,
    create_sales_dashboard,
    create_project_dashboard
)

# Generate KPI dashboard
kpi_data = fetch_kpi_data()  # From your data source
create_kpi_dashboard(kpi_data, 'reports/kpi_dashboard.xlsx')

# Generate sales dashboard from transactions
sales_records = fetch_sales_data()
create_sales_dashboard(sales_records, 'reports/sales_dashboard.xlsx')

# Generate project status
projects = fetch_project_status()
create_project_dashboard(projects, 'reports/project_status.xlsx')
```
