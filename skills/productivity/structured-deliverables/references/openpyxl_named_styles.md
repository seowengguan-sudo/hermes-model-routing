# Openpyxl Named Styles for KPI Dashboards (Aug 2026 Session)

## When to use
When building manufacturing KPI Excel deliverables that must match PDF brand identity (OAKAI teal/gold palette).

## Style Definitions

### Header Row Style
```python
HEADER_STYLE = NamedStyle(
    name="header",
    font=Font(bold=True, color="FFFFFF", size=11),
    fill=PatternFill("solid", fgColor="0B3D3D"),  # Deep teal
    alignment=Alignment(horizontal="center", vertical="center"),
    border=Border(left=Side(style='thin'), right=Side(style='thin'), 
                  top=Side(style='thin'), bottom=Side(style='thick'))
)
```

### Value Cells
```python
VALUE_STYLE = NamedStyle(
    name="value",
    font=Font(size=10, color="2B2B2B"),
    border=Border(left=Side(style='thin'), right=Side(style='thin'), 
                  top=Side(style='thin'), bottom=Side(style='thin'))
)
VALUE_STYLE.number_format = '#,##0.00'
```

### KPI Status Indicators
```python
KPI_GOOD = NamedStyle(
    name="kpi_good",
    font=Font(color="006100", bold=True),
    fill=PatternFill("solid", fgColor="C6EFCE")  # Light green
)

KPI_BAD = NamedStyle(
    name="kpi_bad",
    font=Font(color="9C0006", bold=True),
    fill=PatternFill("solid", fgColor="FFC7CE")  # Light red
)

KPI_WARN = NamedStyle(
    name="kpi_warn",
    font=Font(color="9C6500", bold=True),
    fill=PatternFill("solid", fgColor="FFEB9C")  # Light yellow
)
```

## Conditional Formatting Rules

### Variance-Based Coloring
```python
from openpyxl.formatting.rule import CellIsRule

# Green for positive/bonus
ws.conditional_formatting.add(
    "D2:D100",
    CellIsRule(operator='greaterThan', formula=['0'], 
               stopIfTrue=True, fill=PatternFill("solid", fgColor="C6EFCE"))
)

# Red for negative/over budget
ws.conditional_formatting.add(
    "D2:D100",
    CellIsRule(operator='lessThan', formula=['0'], 
               stopIfTrue=True, fill=PatternFill("solid", fgColor="FFC7CE"))
)
```

## Critical Pitfalls (Observed in Aug 2026 Session)

### 1. Style Registration Bug
```python
# WRONG - private attribute not available in modern openpyxl
if style.name not in [x.name for x in wb._style_list]:

# CORRECT - use _named_styles
existing = [s.name for s in wb._named_styles]
if style.name not in existing:
    wb.add_style(style)
    existing.append(style.name)
```

### 2. NamedStyle Number Format
```python
# WRONG - num_format is NOT a constructor parameter in openpyxl
NamedStyle(name="value", num_format='#,##0.00')

# CORRECT - set after creation
style = NamedStyle(name="value")
style.number_format = '#,##0.00'
```

### 3. Duplicate Style Registration
Always check for existing styles before calling `add_style()` to avoid:
```
KeyError: "Style 'header' already exists"
```

## Brand Color Reference Table

| Name | Hex | Usage |
|------|-----|-------|
| Deep Teal | `#0B3D3D` | Primary headers |
| Teal | `#0F5C56` | Section headers |
| Gold | `#C69B4B` | Accent elements |
| Charcoal | `#2B2B2B` | Body text |
| Dark Green | `#006100` | Positive KPI text |
| Light Green | `#C6EFCE` | Positive KPI fill |
| Dark Red | `#9C0006` | Negative KPI text |
| Light Red | `#FFC7CE` | Negative KPI fill |
| Light Yellow | `#FFEB9C` | Warning/neutral fill |
| Grey | `#6E6E6E` | Subtext, captions |

## Integration Pattern
Match these Excel palette values exactly to PDF brand colors defined in:
- `/opt/data/skills/PDF/oakai_pdf_template.py` (TEAL_DARK, TEAL, GOLD, CHARCOAL)

This ensures consistent visual identity across all OAKAI deliverables.
