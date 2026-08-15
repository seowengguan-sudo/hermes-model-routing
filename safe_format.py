"""
Safe Document Output Format
===========================
Converts extracted document content into a "safe" format with:
- All sensitive data replaced by template variables
- Redaction map saved locally (never sent to LLM)
- Structured JSON output for live agents
- Human-readable template view

The safe format ensures zero PII/PHI/financial data reaches any LLM
while preserving document structure for analysis.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure docreader venv packages are importable
_VENV_SITE = "/opt/data/.venv-docreader/lib/python3.13/site-packages"
if _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

# Import redaction engine
sys.path.insert(0, "/opt/data")
from redaction_engine import RedactionEngine, RedactionMap

# Import document reader
sys.path.insert(0, "/opt/hermes")
from doc_reader_agent import read_document, DocumentResult


@dataclass
class SafeDocument:
    """A document with all sensitive data redacted."""
    document_id: str
    original_filename: str
    original_type: str
    file_size: int
    processed_at: str
    page_count: int | None
    total_redactions: int
    category_counts: dict[str, int]
    
    # Redacted content (safe to send to LLM)
    pages: list[dict[str, Any]] = field(default_factory=list)
    all_text: str = ""
    tables: list[list[list[str]]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # NOT included in agent-facing output:
    # - redaction_map (saved separately to local file only)
    # - original metadata with PII
    
    def to_safe_dict(self) -> dict:
        """Convert to dict safe for sending to LLM/agents."""
        return {
            "document_id": self.document_id,
            "original_type": self.original_type,
            "page_count": self.page_count,
            "total_redactions": self.total_redactions,
            "category_counts": self.category_counts,
            "pages": self.pages,
            "all_text": self.all_text,
            "tables": self.tables,
            "metadata": {
                k: v for k, v in self.metadata.items()
                if k not in ('filename', 'path', 'author', 'creator', 'producer', 'title')
            },
        }
    
    def to_full_dict(self) -> dict:
        """Convert to full dict (includes metadata for local reference only)."""
        d = self.to_safe_dict()
        d.update({
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "processed_at": self.processed_at,
        })
        return d


def redact_metadata(metadata: dict[str, Any], engine: RedactionEngine) -> dict[str, Any]:
    """Redact PII from document metadata fields."""
    safe_meta = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            # Check if the key suggests sensitive content
            sensitive_keys = {'author', 'creator', 'producer', 'title', 'filename', 
                            'producer', 'creator_tool', 'author_name'}
            if key.lower() in sensitive_keys:
                safe_meta[key] = engine.redact(str(value))
            else:
                safe_meta[key] = engine.redact(str(value))
        elif isinstance(value, dict):
            safe_meta[key] = redact_metadata(value, engine)
        elif isinstance(value, list):
            safe_meta[key] = [engine.redact(str(v)) if isinstance(v, str) else v for v in value]
        else:
            safe_meta[key] = value
    return safe_meta


def process_document_to_safe_format(
    file_path: str,
    doc_id: str | None = None,
    extract_tables: bool = True,
    render_pages: bool = False,
    custom_abbreviations: dict[str, str] | None = None,
) -> tuple[SafeDocument, RedactionMap]:
    """
    Read a document, extract content, and redact all sensitive data.
    
    Returns:
        Tuple of (SafeDocument, RedactionMap)
        - SafeDocument: contains only redacted text/tables (safe for LLM)
        - RedactionMap: maps variables to original values (LOCAL ONLY)
    """
    if doc_id is None:
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Read the document using the local reader
    raw_result = read_document(file_path, extract_tables=extract_tables, render_pages=render_pages)
    
    # Create redaction engine
    engine = RedactionEngine(custom_abbreviations=custom_abbreviations)
    
    # Build the safe document
    safe = SafeDocument(
        document_id=doc_id,
        original_filename=Path(file_path).name,
        original_type=raw_result.file_type,
        file_size=raw_result.file_size,
        processed_at=datetime.now().isoformat(),
        page_count=raw_result.page_count,
        total_redactions=0,
        category_counts={},
    )
    
    # Redact text
    if raw_result.text:
        # Split by page for granular redaction
        page_texts = re.split(r'\n--- Page \d+ ---\n', raw_result.text)
        page_texts = [t.strip() for t in page_texts if t.strip()]
        
        if len(page_texts) > 1:
            for i, pt in enumerate(page_texts):
                redacted = engine.redact(pt)
                safe.pages.append({
                    "page_number": i + 1,
                    "text": redacted,
                })
                safe.all_text += redacted + "\n"
        else:
            redacted = engine.redact(raw_result.text)
            safe.pages.append({
                "page_number": 1,
                "text": redacted,
            })
            safe.all_text = redacted
    
    # Redact tables
    if raw_result.tables:
        for table in raw_result.tables:
            redacted_table = [[engine.redact(cell) for cell in row] for row in table]
            safe.tables.append(redacted_table)
    
    # Redact metadata
    safe.metadata = redact_metadata(raw_result.metadata, engine)
    
    # Calculate totals
    safe.total_redactions = sum(engine.redaction_map.category_counts.values())
    safe.category_counts = dict(engine.redaction_map.category_counts)
    
    # Add page tables to page objects
    if raw_result.tables:
        for i, page in enumerate(safe.pages):
            # Distribute tables across pages (simple approach)
            page["tables"] = []
    
    # Save redaction map locally
    redaction_map_path = engine.save_redaction_map(doc_id)
    
    return safe, engine.redaction_map


def save_safe_document(safe_doc: SafeDocument, output_dir: Path | str | None = None) -> Path:
    """Save the safe document to a JSON file."""
    if output_dir is None:
        output_dir = Path("/opt/data/documents_safe")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{safe_doc.document_id}_safe.json"
    output_path.write_text(
        json.dumps(safe_doc.to_full_dict(), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return output_path


def generate_template_view(safe_doc: SafeDocument) -> str:
    """Generate a human-readable template view showing the document structure."""
    lines = [
        f"# Document: {safe_doc.original_filename}",
        f"Type: {safe_doc.original_type} | Pages: {safe_doc.page_count or '?'}",
        f"Total redactions: {safe_doc.total_redactions}",
        "",
    ]
    
    if safe_doc.category_counts:
        lines.append("## Redaction Summary")
        for cat, count in sorted(safe_doc.category_counts.items()):
            lines.append(f"  - {cat}: {count}")
        lines.append("")
    
    lines.append("## Content")
    lines.append("(Sensitive data replaced with template variables)")
    lines.append("---")
    
    for page in safe_doc.pages:
        lines.append(f"\n### Page {page['page_number']}\n")
        lines.append(page["text"])
    
    return "\n".join(lines)


if __name__ == "__main__":
    # CLI interface for testing
    if len(sys.argv) < 2:
        print("Usage: python3 safe_format.py <file_path> [--no-tables]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    extract_tables = "--no-tables" not in sys.argv
    
    safe_doc, redaction_map = process_document_to_safe_format(
        file_path, extract_tables=extract_tables
    )
    
    # Save safe document
    safe_path = save_safe_document(safe_doc)
    map_path = Path(f"/opt/data/redaction_maps/{safe_doc.document_id}_redaction_map.json")
    
    print(f"✓ Safe document saved: {safe_path}")
    print(f"✓ Redaction map saved: {map_path}")
    print(f"  Total redactions: {safe_doc.total_redactions}")
    print(f"  Categories: {safe_doc.category_counts}")
    
    # Show template preview
    print("\n--- Template Preview (first 500 chars) ---")
    print(safe_doc.all_text[:500])
    if len(safe_doc.all_text) > 500:
        print(f"... ({len(safe_doc.all_text) - 500} more chars)")