## Canonical PDF Generation Script

Usage: `./scripts/generate_pdf.sh <template_name> <output_path>`

- Routes all PDF generation through `/opt/data/skills/PDF/`
- Falls back to stdlib generator only if skill missing
- Uses persistent venv cache at `/tmp/hermes-runs/pdf-runtime`

Example:
```bash
cd /opt/data
./skills/productivity/documentation-generation/scripts/generate_pdf.sh coo_week1 /opt/data/workspace/OAKAI_W1_COOBrief.pdf
```

This ensures consistent formatting, brand compliance, and eliminates repeated venv recreation delays.

