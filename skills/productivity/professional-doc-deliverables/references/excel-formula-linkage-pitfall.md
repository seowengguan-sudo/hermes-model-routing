# Excel Formula Linkage Pitfalls — Session Detail

## The Problem (Aug 13, 2026 rebuild)

When building OAKAI_KPI_Dashboard_Rev17.xlsx (6-sheet manufacturing KPI dashboard),
two recurring Excel formula errors caused a broken deliverable on first run:

1. **Column-letter mismatch across sheets**: LOSS_ANALYSIS has 9 columns (A-I).
   The $ Impact formula referenced `J{r}` (column J = CM/Unit in INPUT sheet).
   But J doesn't exist in LOSS_ANALYSIS, so Excel shows #REF!.
   Correct cross-sheet ref: `='2. INPUT'!M{row}`.

2. **Self-referencing circular formulas at category headers**: Category header
   row had `=H{row}*52` but column H is the Annual $ Impact that itself depends
   on per-product rows. 5-Year Value should be `=H{header_row}*5`.

## The Fix Pattern

## Per-product $ Impact: `=D{r} * G{r} * '2. INPUT'!M{input_row}`
- Category header $ Impact: `=SUM(H{start}:H{end})`
- Grand total $ Impact: `=SUM(H8:H{last_product_row})`

## Concrete Column Mapping (Rev17 example)
When building cross-sheet formulas, write the column letter
explicitly as a string literal rather than `%d` integer formatting
which is error-prone:

- INPUT sheet columns: A=ID, B=Name, C=Std CT, D-H=Weekly Vol,
  I=Total Wkly Vol, J=Unit Price, K=Mat Cost, L=Util Cost, M=CM/Unit
- LOSS_ANALYSIS columns: A=#, B=Category, C=Product, D=Loss Metric,
  E=Unit, F=Cost Factor, G=Annual Vol, H=$ Impact, I=5-Yr Value

**Always map column letters to semantic names in a shared dict:**
```python
COL = {
    'input_vol': 'I',   # Total weekly volume in INPUT
    'input_cm': 'M',     # CM/Unit in INPUT
    'loss_impact': 'H',  # $ Impact column in LOSS_ANALYSIS
}
# Formula: f"='2. INPUT'!{COL['input_vol']}{input_row}*52"  (annual vol)
# Formula: f"=D{r}*{cm_ref}*{annual_vol}"  ($ impact)
```

**Pre-flight check**: enumerate every column letter referenced
in formulas and assert each exists in the target sheet's max_column.
Column J referenced in a 9-column (A-I) sheet => #REF! error.

## Mandatory 3-Step Guard

1. String inspection: no #REF!, no self-ref like H8=H8*52
2. LibreOffice headless recalc (or xlsx/scripts/recalc.py if available)
3. Value assertion: reopen with data_only=True, assert non-zero finite values

openpyxl writes formulas as strings — syntax checks alone prove nothing.

## Session Note

The `xlsx` skill provides `skills/productivity/xlsx/scripts/recalc.py`
(uses LibreOffice headless recalc). **Always run it** as the mandatory
second step before claiming formula output is valid. In the Aug 13 session,
LibreOffice was not available in the environment, so verification fell back
to a structural pattern check (column mapping pre-flight + cross-sheet ref
presence + SUM/RANK/non-circular assertions) — 25/25 checks passed. When
LibreOffice IS available, run recalc.py and then reopen with
`data_only=True` to assert non-zero finite values.

## Pattern Checklist (class-level — verify before every Excel build)

Use this checklist whenever you write a multi-sheet Excel workbook with
cross-sheet references:

1. [ ] **Column-letter mapping table** — before writing any formula, enumerate
       every column letter used in formulas for each sheet and assert each exists
       in that sheet's column range (e.g. referencing `J{r}` in a 9-column A–I
       sheet is a #REF! bug).
2. [ ] **Column-letter as string literals** — in Python generators, build column
       letters via a shared `COL` dict (see above) rather than `%d`/integer
       formatting which is error-prone for cross-sheet refs.
3. [ ] **Cross-sheet refs use full `'SheetName'!A1` syntax** — never assume
       shorthand column references resolve across sheets (they don't).
4. [ ] **No self-references in header/total rows** — e.g. `=H8*52` in row 8 when
       row 8 is itself a category header that *depends on* H8. Header total must
       `SUM` the range below (`=SUM(H9:H16)`).
5. [ ] **Category/total SUM ranges are correct** — `SUM(H{first_product}:H{last_product})`,
       not `SUM(I{...})` (wrong column — 5-year vs $ Impact).
6. [ ] **Annual volume = weekly_total × 52** (or parameterized from PARAMS sheet).
7. [ ] **5-year value = $ Impact × 5** at every level (product, category, grand total).
8. [ ] **RANK formula range is fixed** (`H$8:H$15`, not `H8:H15` which shifts per row).
9. [ ] **Data source for annual volume** is `'2. INPUT'!I{row}*52` (cross-sheet).
10. [ ] **CM/Unit reference** in $ Impact formulas is `'2. INPUT'!M{row}` (cross-sheet),
       never a local column that doesn't exist in the current sheet.

## Common User Complaints and Their Root Causes

| User says... | Root cause | Fix |
|---|---|---|
| "formula linkage from loop to loop is not working" | Cross-sheet reference uses a column that doesn't exist in the target sheet, or uses relative shorthand `J{r}` instead of `'Sheet'!col{row}` | Use explicit `'2. INPUT'!M{input_row}` syntax; enumerate all column refs in a COL dict before coding |
| "the input table looks too simple" | INPUT sheet has too few columns — only basic product data, no cost breakdown | Always include: Std Cycle Time, Weekly Volumes, Unit Price, Mat Cost, Util Cost, CM/Unit, Labor Cost, Overhead. Blue cells for client editable, yellow/auto-calc for derived |
| "broken formula linkage" | Category header row self-references or wrong column SUM | Header row = `SUM(H{start}:H{end})`; never `=H{row}*N` in a row that is itself the total |