# Financial Report Template

Copy-paste template for generating financial statements and reports in Excel.

---

## Income Statement

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

def create_income_statement(data: dict, output_path: str = 'income_statement.xlsx'):
    """
    Generate a professional income statement.

    Args:
        data: Dictionary with revenue, expenses, and metadata
        output_path: Output file path

    Example data:
        {
            'company': 'Acme Corp',
            'period': 'Q4 2024',
            'revenue': [
                ('Product Sales', 150000),
                ('Service Revenue', 50000),
                ('Other Income', 5000),
            ],
            'cogs': [
                ('Cost of Goods Sold', 80000),
            ],
            'operating_expenses': [
                ('Salaries & Wages', 45000),
                ('Rent', 12000),
                ('Utilities', 3000),
                ('Marketing', 8000),
                ('Depreciation', 5000),
            ],
            'other_expenses': [
                ('Interest Expense', 2000),
            ],
            'tax_rate': 0.25
        }
    """
    wb = Workbook()
    ws = wb.active
    ws.title = 'Income Statement'

    # Styles
    title_font = Font(bold=True, size=14)
    header_font = Font(bold=True, size=11)
    section_fill = PatternFill(start_color='E7E6E6', fill_type='solid')
    currency_format = '$#,##0.00'
    border = Border(bottom=Side(style='thin'))
    double_border = Border(bottom=Side(style='double'))

    row = 1

    # Title
    ws.merge_cells(f'A{row}:C{row}')
    ws[f'A{row}'] = f"{data['company']} - Income Statement"
    ws[f'A{row}'].font = title_font
    row += 1

    ws.merge_cells(f'A{row}:C{row}')
    ws[f'A{row}'] = f"Period: {data['period']}"
    row += 2

    # Column widths
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15

    # Revenue Section
    ws[f'A{row}'] = 'REVENUE'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_revenue = 0
    for item, amount in data['revenue']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_revenue += amount
        row += 1

    ws[f'A{row}'] = 'Total Revenue'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_revenue
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = header_font
    ws[f'B{row}'].border = border
    row += 2

    # COGS
    ws[f'A{row}'] = 'COST OF GOODS SOLD'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_cogs = 0
    for item, amount in data['cogs']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_cogs += amount
        row += 1

    ws[f'A{row}'] = 'Total COGS'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_cogs
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = header_font
    ws[f'B{row}'].border = border
    row += 2

    # Gross Profit
    gross_profit = total_revenue - total_cogs
    ws[f'A{row}'] = 'GROSS PROFIT'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = gross_profit
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    row += 2

    # Operating Expenses
    ws[f'A{row}'] = 'OPERATING EXPENSES'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_opex = 0
    for item, amount in data['operating_expenses']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_opex += amount
        row += 1

    ws[f'A{row}'] = 'Total Operating Expenses'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_opex
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = header_font
    ws[f'B{row}'].border = border
    row += 2

    # Operating Income
    operating_income = gross_profit - total_opex
    ws[f'A{row}'] = 'OPERATING INCOME'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = operating_income
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    row += 2

    # Other Expenses
    total_other = sum(amount for _, amount in data.get('other_expenses', []))
    if total_other > 0:
        ws[f'A{row}'] = 'OTHER EXPENSES'
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].fill = section_fill
        row += 1

        for item, amount in data['other_expenses']:
            ws[f'A{row}'] = f'  {item}'
            ws[f'B{row}'] = amount
            ws[f'B{row}'].number_format = currency_format
            row += 1
        row += 1

    # Income Before Tax
    income_before_tax = operating_income - total_other
    ws[f'A{row}'] = 'INCOME BEFORE TAX'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = income_before_tax
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = header_font
    row += 1

    # Tax
    tax = income_before_tax * data.get('tax_rate', 0.25)
    ws[f'A{row}'] = f"  Income Tax ({data.get('tax_rate', 0.25):.0%})"
    ws[f'B{row}'] = tax
    ws[f'B{row}'].number_format = currency_format
    row += 2

    # Net Income
    net_income = income_before_tax - tax
    ws[f'A{row}'] = 'NET INCOME'
    ws[f'A{row}'].font = Font(bold=True, size=14)
    ws[f'B{row}'] = net_income
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=14)
    ws[f'B{row}'].border = double_border

    wb.save(output_path)
    return output_path


# Example usage
if __name__ == '__main__':
    sample_data = {
        'company': 'Acme Corporation',
        'period': 'Q4 2024',
        'revenue': [
            ('Product Sales', 150000),
            ('Service Revenue', 50000),
            ('Other Income', 5000),
        ],
        'cogs': [
            ('Cost of Goods Sold', 80000),
        ],
        'operating_expenses': [
            ('Salaries & Wages', 45000),
            ('Rent', 12000),
            ('Utilities', 3000),
            ('Marketing', 8000),
            ('Depreciation', 5000),
        ],
        'other_expenses': [
            ('Interest Expense', 2000),
        ],
        'tax_rate': 0.25
    }

    create_income_statement(sample_data)
```

---

## Balance Sheet

```python
def create_balance_sheet(data: dict, output_path: str = 'balance_sheet.xlsx'):
    """
    Generate a professional balance sheet.

    Args:
        data: Dictionary with assets, liabilities, and equity
        output_path: Output file path

    Example data:
        {
            'company': 'Acme Corp',
            'as_of': 'December 31, 2024',
            'current_assets': [
                ('Cash & Equivalents', 50000),
                ('Accounts Receivable', 35000),
                ('Inventory', 25000),
                ('Prepaid Expenses', 5000),
            ],
            'non_current_assets': [
                ('Property & Equipment', 150000),
                ('Less: Accumulated Depreciation', -30000),
                ('Intangible Assets', 20000),
            ],
            'current_liabilities': [
                ('Accounts Payable', 25000),
                ('Accrued Expenses', 10000),
                ('Short-term Debt', 15000),
            ],
            'non_current_liabilities': [
                ('Long-term Debt', 80000),
            ],
            'equity': [
                ('Common Stock', 50000),
                ('Retained Earnings', 75000),
            ]
        }
    """
    wb = Workbook()
    ws = wb.active
    ws.title = 'Balance Sheet'

    # Styles
    title_font = Font(bold=True, size=14)
    header_font = Font(bold=True, size=11)
    section_fill = PatternFill(start_color='E7E6E6', fill_type='solid')
    currency_format = '$#,##0.00'
    border = Border(bottom=Side(style='thin'))
    double_border = Border(bottom=Side(style='double'))

    row = 1

    # Title
    ws.merge_cells(f'A{row}:C{row}')
    ws[f'A{row}'] = f"{data['company']} - Balance Sheet"
    ws[f'A{row}'].font = title_font
    row += 1

    ws.merge_cells(f'A{row}:C{row}')
    ws[f'A{row}'] = f"As of: {data['as_of']}"
    row += 2

    # Column widths
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 18

    # ASSETS
    ws[f'A{row}'] = 'ASSETS'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    row += 1

    # Current Assets
    ws[f'A{row}'] = 'Current Assets'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_current_assets = 0
    for item, amount in data['current_assets']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_current_assets += amount
        row += 1

    ws[f'A{row}'] = 'Total Current Assets'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_current_assets
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].border = border
    row += 2

    # Non-Current Assets
    ws[f'A{row}'] = 'Non-Current Assets'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_non_current_assets = 0
    for item, amount in data['non_current_assets']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_non_current_assets += amount
        row += 1

    ws[f'A{row}'] = 'Total Non-Current Assets'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_non_current_assets
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].border = border
    row += 2

    # Total Assets
    total_assets = total_current_assets + total_non_current_assets
    ws[f'A{row}'] = 'TOTAL ASSETS'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = total_assets
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'].border = double_border
    row += 3

    # LIABILITIES
    ws[f'A{row}'] = 'LIABILITIES'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    row += 1

    # Current Liabilities
    ws[f'A{row}'] = 'Current Liabilities'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_current_liab = 0
    for item, amount in data['current_liabilities']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_current_liab += amount
        row += 1

    ws[f'A{row}'] = 'Total Current Liabilities'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_current_liab
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].border = border
    row += 2

    # Non-Current Liabilities
    ws[f'A{row}'] = 'Non-Current Liabilities'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_non_current_liab = 0
    for item, amount in data['non_current_liabilities']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_non_current_liab += amount
        row += 1

    ws[f'A{row}'] = 'Total Non-Current Liabilities'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_non_current_liab
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].border = border
    row += 2

    total_liabilities = total_current_liab + total_non_current_liab
    ws[f'A{row}'] = 'TOTAL LIABILITIES'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = total_liabilities
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'].border = border
    row += 3

    # EQUITY
    ws[f'A{row}'] = "SHAREHOLDERS' EQUITY"
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_equity = 0
    for item, amount in data['equity']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_equity += amount
        row += 1

    ws[f'A{row}'] = 'TOTAL EQUITY'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = total_equity
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'].border = border
    row += 2

    # Total Liabilities + Equity
    ws[f'A{row}'] = 'TOTAL LIABILITIES + EQUITY'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = total_liabilities + total_equity
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'].border = double_border

    wb.save(output_path)
    return output_path
```

---

## Cash Flow Statement

```python
def create_cash_flow_statement(data: dict, output_path: str = 'cash_flow.xlsx'):
    """
    Generate cash flow statement.

    Args:
        data: Dictionary with operating, investing, financing activities

    Example data:
        {
            'company': 'Acme Corp',
            'period': 'Year Ended December 31, 2024',
            'beginning_cash': 30000,
            'operating': [
                ('Net Income', 45000),
                ('Depreciation', 5000),
                ('Changes in Receivables', -5000),
                ('Changes in Payables', 3000),
            ],
            'investing': [
                ('Purchase of Equipment', -25000),
                ('Sale of Investments', 10000),
            ],
            'financing': [
                ('Proceeds from Debt', 20000),
                ('Dividends Paid', -10000),
            ]
        }
    """
    wb = Workbook()
    ws = wb.active
    ws.title = 'Cash Flow'

    # Styles
    title_font = Font(bold=True, size=14)
    header_font = Font(bold=True, size=11)
    section_fill = PatternFill(start_color='E7E6E6', fill_type='solid')
    currency_format = '$#,##0.00'
    border = Border(bottom=Side(style='thin'))
    double_border = Border(bottom=Side(style='double'))

    row = 1
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 18

    # Title
    ws[f'A{row}'] = f"{data['company']} - Statement of Cash Flows"
    ws[f'A{row}'].font = title_font
    row += 1
    ws[f'A{row}'] = data['period']
    row += 2

    # Operating Activities
    ws[f'A{row}'] = 'OPERATING ACTIVITIES'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_operating = 0
    for item, amount in data['operating']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_operating += amount
        row += 1

    ws[f'A{row}'] = 'Net Cash from Operating Activities'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_operating
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].border = border
    row += 2

    # Investing Activities
    ws[f'A{row}'] = 'INVESTING ACTIVITIES'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_investing = 0
    for item, amount in data['investing']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_investing += amount
        row += 1

    ws[f'A{row}'] = 'Net Cash from Investing Activities'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_investing
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].border = border
    row += 2

    # Financing Activities
    ws[f'A{row}'] = 'FINANCING ACTIVITIES'
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = section_fill
    row += 1

    total_financing = 0
    for item, amount in data['financing']:
        ws[f'A{row}'] = f'  {item}'
        ws[f'B{row}'] = amount
        ws[f'B{row}'].number_format = currency_format
        total_financing += amount
        row += 1

    ws[f'A{row}'] = 'Net Cash from Financing Activities'
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'] = total_financing
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].border = border
    row += 2

    # Summary
    net_change = total_operating + total_investing + total_financing
    ws[f'A{row}'] = 'NET CHANGE IN CASH'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = net_change
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    row += 2

    ws[f'A{row}'] = 'Beginning Cash Balance'
    ws[f'B{row}'] = data['beginning_cash']
    ws[f'B{row}'].number_format = currency_format
    row += 1

    ws[f'A{row}'] = 'ENDING CASH BALANCE'
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'] = data['beginning_cash'] + net_change
    ws[f'B{row}'].number_format = currency_format
    ws[f'B{row}'].font = Font(bold=True, size=12)
    ws[f'B{row}'].border = double_border

    wb.save(output_path)
    return output_path
```

---

## Usage Pattern

```python
# Generate all three financial statements
from financial_templates import (
    create_income_statement,
    create_balance_sheet,
    create_cash_flow_statement
)

# Load your data from database/API
company_data = load_financial_data('ACME', '2024-Q4')

# Generate reports
create_income_statement(company_data['income'], 'reports/income_2024q4.xlsx')
create_balance_sheet(company_data['balance'], 'reports/balance_2024q4.xlsx')
create_cash_flow_statement(company_data['cashflow'], 'reports/cashflow_2024q4.xlsx')
```
