# Financial Statement Workbook Rules

Rules for generating income statement, balance sheet and cash-flow workbooks from code. The mechanics of writing a formula-first model belong to the official `xlsx` skill; this file holds the checks a generated statement must pass. Pair it with [spreadsheet-model-review-checklist.md](spreadsheet-model-review-checklist.md).

## Structure

- **Inputs as values, everything else as formulas.** Line items are inputs. Every subtotal, total, margin and derived line is a live formula (`=SUM(B5:B9)`, `=B12-B18`), so reviewers can trace outputs and edits recalculate.
- **Assumptions are visible input cells**, not constants inside formulas. The tax rate lives in its own labelled cell (`=B20*C21`, never `=B20*0.25`). Mark input cells with one consistent style, for example blue font, and state the convention on the sheet.
- **No silent defaults for assumptions.** If the source data lacks a tax rate, FX rate or period, fail the build or leave the input cell visibly empty and flagged. Never fill in a plausible number: `data.get("tax_rate", 0.25)` ships a made-up assumption that looks sourced.
- **One workbook, linked statements.** Put the three statements on separate sheets of one workbook. Link them with cross-sheet formulas: net income flows into retained earnings and into cash flow from operations, and ending cash equals balance-sheet cash. Three separate files cannot be linked or reconciled.
- **Period and entity are inputs.** Write the period label, currency and entity name into header cells taken from the source data. Do not hard-code them in code, filenames or sheet names.

## Sign Convention

Pick one convention and state it on the sheet: either expenses stored as positive numbers and subtracted in formulas, or expenses stored as negatives and summed. Mixing the two within a workbook is the most common way a generated statement produces a plausible but wrong net income.

## Fail-Loud Check Cells

Add a `Checks` block, or a sheet, of formulas that must evaluate to zero. Surface them next to the totals:

| Check | Formula shape | Must equal |
|-------|---------------|-----------|
| Balance sheet balances | `=TotalAssets-(TotalLiabilities+TotalEquity)` | 0 |
| Cash ties out | `=CF!EndingCash-BS!Cash` | 0 |
| Net income flows | `=IS!NetIncome-CF!NetIncome` | 0 |
| Source reconciliation | `=SUM(IS!Revenue)-SourceControlTotal` | 0 |

- Round the comparisons (`=ROUND(...,2)=0`) so floating-point residue does not raise false alarms.
- Apply conditional formatting so a non-zero check is visibly red, and add a single `ALL CHECKS PASS` cell.
- After recalculating (LibreOffice headless or Excel), read the check cells back with `data_only=True` and fail the pipeline if any is non-zero. Before recalculation caches may be empty or contain placeholder zeros; neither verifies that the checks passed. Require a recorded recalculation or independently computed control totals, and report unevaluated checks as "unverified".

## Formatting

- Use the accounting-style number format for currency columns, negatives in parentheses when the audience expects it, and the currency code in the header rather than a symbol baked into every cell.
- Totals get a top border; grand totals a double bottom border. Freeze the label column and the header row.
- Keep full precision in cells and round in the display only, unless a statutory rule requires rounded line items.

## Related Resources

- [../references/excel-formulas.md](../references/excel-formulas.md) - Formula writing and read-back rules
- [../references/excel-formatting.md](../references/excel-formatting.md) - Number formats and conditional formatting
- [../SKILL.md](../SKILL.md) - Parent skill
