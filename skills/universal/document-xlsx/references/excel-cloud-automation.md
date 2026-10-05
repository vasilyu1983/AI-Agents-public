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

Native pivots from Office Scripts: see [excel-pivot-tables.md](excel-pivot-tables.md#office-scripts-native-pivot-microsoft-365).

---

## Microsoft Graph Excel

Prefer Graph when:

- The workbook must be modified remotely from a service or backend job
- You need workbook sessions and object-model access over REST
- The workbook is stored in Microsoft 365 and human interaction is not required

Typical workflow:

1. Resolve the workbook item in OneDrive or SharePoint
2. Create a workbook session (`createSession`) and pass its id on every call. Set `persistChanges` explicitly: a non-persistent session discards its edits, which suits what-if calculations but silently loses a real update
3. Update ranges, tables, or named items; read back the changed range to confirm
4. Close the session

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
