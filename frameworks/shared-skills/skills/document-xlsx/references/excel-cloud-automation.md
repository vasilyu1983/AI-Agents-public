# Excel Cloud Automation

Use cloud automation when the workbook lives in Microsoft 365 and you need native Excel features without shipping a local desktop file back and forth.

---

## Tool Selection

| Tool | Best For | Constraints |
|------|----------|-------------|
| Office Scripts | Excel on the web automation, tables, pivots, worksheet operations | Runs in Microsoft 365 contexts; TypeScript API |
| Microsoft Graph Excel | Remote workbook sessions, ranges, tables, charts, named items | Requires Graph auth and workbook location in OneDrive/SharePoint |
| xlwings | Desktop Excel automation with native feature access | Requires Excel installed on the machine |

---

## Office Scripts

Prefer Office Scripts when:

- The workbook is already in OneDrive or SharePoint
- The user needs native PivotTables or worksheet automation
- The workflow is initiated from Excel on the web, Power Automate, or Microsoft 365

### Create a Table

```typescript
function main(workbook: ExcelScript.Workbook) {
  const ws = workbook.getWorksheet("Raw Data");
  const table = ws.addTable(ws.getUsedRange(), true);
  table.setName("SalesTable");
  table.setShowTotals(true);
}
```

### Create a PivotTable

```typescript
function main(workbook: ExcelScript.Workbook) {
  const sourceTable = workbook.getTable("SalesTable");
  const pivotSheet = workbook.addWorksheet("Pivot");
  const pivot = workbook.addPivotTable("SalesPivot", sourceTable, pivotSheet.getRange("A1"));

  pivot.addRowHierarchy(pivot.getHierarchy("Region"));
  pivot.addColumnHierarchy(pivot.getHierarchy("Product"));
  pivot.addDataHierarchy(pivot.getHierarchy("Revenue"));
}
```

---

## Microsoft Graph Excel

Prefer Graph when:

- The workbook must be modified remotely from a service or backend job
- You need workbook sessions and object-model access over REST
- The workbook is stored in Microsoft 365 and human interaction is not required

Typical workflow:

1. Create or reuse a workbook session
2. Resolve the workbook item in OneDrive or SharePoint
3. Update ranges, tables, or named items
4. Close the session or persist changes

Graph is strong for remote workbook orchestration, but it is not a replacement for every desktop Excel feature.

---

## xlwings

Prefer xlwings when:

- You need native Excel behavior on a user or automation machine
- The workflow depends on Excel-specific rendering or a desktop add-in
- Office Scripts or Graph are not an option

Avoid xlwings for headless Linux CI or server environments without Excel.

---

## Decision Rules

- Workbook already lives in Microsoft 365:
  prefer Office Scripts first, Graph second.
- Native pivots required without desktop Excel:
  prefer Office Scripts.
- Service/backend job mutating hosted workbooks:
  prefer Graph sessions.
- Desktop Excel is available and the workflow is local:
  prefer xlwings.
- Pure export with no live workbook dependency:
  stay local with `XlsxWriter`, `openpyxl`, or `ExcelJS`.
