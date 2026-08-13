## Manufacturing KPI Excel Template (Session: Aug 12, 2026)

When building manufacturing KPI dashboards in Excel, follow this structure:

### Column Layout
| Column | Header | Format | Notes |
|--------|--------|--------|-------|
| A | KPI | Text-left | Bold header |
| B | Target | Number | Blue text for inputs |
| C | Actual | Number | Black for formulas |
| D | Variance | Formula | Red for negative, green for positive |
| E | % Achievement | Percentage | Formula = Actual/Target |

### Color Coding Rules
- **Header row**: Deep blue (#1171B3) background, white bold text
- **Positive variance**: Green fill (#C6EFCE), dark green text (#006100)
- **Negative variance**: Red fill (#FFC7CE), dark red text (#9C0006)
- **Formula cells**: Black text, no fill
- **Input cells**: Yellow fill (#FFEB99) for user-editable targets

### Sample Formulas
```excel
D2: =C2-B2                    # Variance
E2: =IF(B2=0, "#DIV/0!", C2/B2)  # % Achievement
```

### Auto-Formatting Checklist
1. [ ] Set column widths (22 chars each)
2. [ ] Freeze top row
3. [ ] Apply number formats BEFORE writing values
4. [ ] Wrap long KPI names in column A
5. [ ] Add conditional formatting for variance colors
6. [ ] Include a "Last Updated" timestamp cell

### Integration with PENSOLAR
Map these KPIs to your solar project management workflow:
- Production Volume → Modules installed per week
- Defect Rate → Rework needed after inspection
- Delivery On-Time → Crew arrival vs scheduled
- Cost per Unit → RM/Cost per watt installed
- Machine Uptime → Inverter availability

