"""
Redaction Engine for Document Content
=====================================
Redacts sensitive data from extracted document content and replaces it
with deterministic template variables (e.g. {PERSON_NAME_1}, {SSN_1}).

All redaction happens locally — no external APIs.
The redaction map (variable → original value) is persisted locally only.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure docreader venv packages are importable
_VENV_SITE = "/opt/data/.venv-docreader/lib/python3.13/site-packages"
if _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

# Try to import spaCy for NER
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except Exception:
    _nlp = None


# ── Regex Patterns ───────────────────────────────────────────────────────────

# Structured data patterns (high precision)
REGEX_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "SSN": [
        (r"\b\d{3}-\d{2}-\d{4}\b", "full"),
        (r"\b\d{3}\.\d{2}\.\d{4}\b", "full"),
        (r"\b\d{3}\s\d{2}\s\d{4}\b", "full"),
        (r"\b\d{9}\b", "masked"),
        # Partial SSN formats (e.g., 12-3456789, 123-45678)
        (r"\b\d{2}-\d{6,7}\b", "masked"),
        (r"\b\d{3}-\d{5,6}\b", "masked"),
    ],
    "CREDIT_CARD": [
        (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "masked"),  # 4111-1111-1111-1111
        (r"\b4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "masked"),  # Visa
        (r"\b5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "masked"),  # Mastercard
        (r"\b3[47]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{3}\b", "masked"),  # Amex
    ],
    "PHONE": [
        (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "full"),
        (r"\b\+\d{1,3}\s*\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{4}\b", "full"),
        (r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "full"),
        # Short phone formats (555-1234, +1 555-1234)
        (r"\b\d{3}[-.\s]?\d{4}\b", "full"),  # 7-digit local
        (r"\b\+\d{1,3}\s*\d{3}[-.\s]?\d{4}\b", "full"),  # International short
    ],
    "EMAIL": [
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "full"),
    ],
    "IBAN": [
        (r"\b[A-Z]{2}\d{2}(?:[ ]?\d{4}){2,7}\b", "full"),
    ],
    "BANK_ACCOUNT": [
        # Match 8-17 digit numbers NOT already matched as SSN/CREDIT_CARD
        # The negative lookbehind/lookahead avoids matching patterns like SSN (xxx-xx-xxxx)
        (r"(?<![-\d])(\d{8,17})(?![-\d])", "masked"),  # Standalone bank account numbers
    ],
    "API_KEY": [
        (r"\bsk-[A-Za-z0-9]{20,}\b", "full"),  # OpenAI-style
        (r"\bxox[bpoa]-[A-Za-z0-9-]+", "full"),  # Slack
        (r"\bghp_[A-Za-z0-9]{36}\b", "full"),  # GitHub PAT
        (r"\bAIza[0-9A-Za-z_-]{35}\b", "full"),  # Google API key
    ],
    "AWS_KEY": [
        (r"\bAKIA[0-9A-Z]{16}\b", "full"),
    ],
    "CREDENTIAL": [
        (r"\bBearer\s+[A-Za-z0-9._-]{20,}\b", "full"),
        (r"\bpassword\s*[=:]\s*\S+", "full"),
        (r"\btoken\s*[=:]\s*\S+", "full"),
        (r"\bapi[_-]?key\s*[=:]\s*\S+", "full"),
    ],
}

# Abbreviation-based custom PII patterns (user-defined, A, B, C, etc.)
DEFAULT_ABBREVIATIONS = {
    "A": "Client Name",
    "B": "Project Name",
    "C": "Internal System Name",
    "D": "Contract Reference",
    "E": "Case ID",
    "F": "Vendor Name",
    "G": "Department Code",
    "H": "Location Code",
    "I": "Employee ID",
    "J": "Cost Center",
}


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class RedactionResult:
    """Result of redacting a single text block."""
    redacted_text: str
    redactions: list[dict[str, Any]] = field(default_factory=list)
    category_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class RedactionMap:
    """Mapping from template variables to original (redacted) values."""
    map: dict[str, str] = field(default_factory=dict)
    category_counts: dict[str, int] = field(default_factory=dict)
    
    def add(self, var_name: str, original: str, category: str) -> None:
        """Add a mapping entry."""
        self.map[var_name] = original
        self.category_counts[category] = self.category_counts.get(category, 0) + 1
    
    def to_dict(self) -> dict:
        return {
            "map": self.map,
            "category_counts": self.category_counts,
            "created_at": datetime.now().isoformat(),
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "RedactionMap":
        obj = cls()
        obj.map = d.get("map", {})
        obj.category_counts = d.get("category_counts", {})
        return obj
    
    def save(self, path: Path) -> None:
        """Save the redaction map to a local file (NEVER leave volume)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))
    
    @classmethod
    def load(cls, path: Path) -> "RedactionMap":
        if not path.exists():
            return cls()
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


# ── Redaction Engine ────────────────────────────────────────────────────────

class RedactionEngine:
    """
    Redacts sensitive data from text using regex patterns + NER +
    custom abbreviation-based patterns.
    
    Produces deterministic template variables like {SSN_1}, {PERSON_NAME_1},
    {CUSTOM_ABBREV_A_1} so the document structure is preserved for agents
    while the actual PII/PHI is never exposed.
    
    The redaction map (variable → original value) is persisted locally only.
    """
    
    def __init__(
        self,
        custom_abbreviations: dict[str, str] | None = None,
        custom_patterns: dict[str, list[str]] | None = None,
        redaction_dir: Path | None = None,
    ):
        self.custom_abbreviations = custom_abbreviations or dict(DEFAULT_ABBREVIATIONS)
        self.custom_patterns = custom_patterns or {}
        self.redaction_dir = redaction_dir or Path("/opt/data/redaction_maps")
        self.redaction_map = RedactionMap()
        self._counters: dict[str, int] = {}
        self._used_values: set[str] = set()
    
    def _next_var(self, category: str) -> str:
        """Generate the next template variable name for a category."""
        self._counters[category] = self._counters.get(category, 0) + 1
        return f"{category}_{self._counters[category]}"
    
    def _redact_regex(self, text: str) -> str:
        """Apply regex-based redaction patterns."""
        for category, patterns in REGEX_PATTERNS.items():
            for pattern, mask_type in patterns:
                def replace_fn(match: re.Match) -> str:
                    original = match.group(0)
                    # Skip if already seen (deduplicate)
                    key = f"{category}:{original}"
                    if key in self._used_values:
                        return self._find_existing_var(category, original)
                    
                    self._used_values.add(key)
                    var_name = self._next_var(category)
                    var_placeholder = f"{{{var_name}}}"
                    
                    # Store in redaction map
                    if mask_type == "masked":
                        # Store the masked version in the map
                        if category == "CREDIT_CARD":
                            stored = f"****-****-****-{original[-4:]}"
                        elif category == "BANK_ACCOUNT":
                            stored = f"****{original[-4:]}" if len(original) > 4 else "****"
                        else:
                            stored = original
                    else:
                        stored = original
                    
                    self.redaction_map.add(var_placeholder, stored, category)
                    return var_placeholder
                
                text = re.sub(pattern, replace_fn, text, flags=re.IGNORECASE)
        
        return text
    
    # Common words that NER may incorrectly tag as PERSON/ORG
    # Filtered out to reduce false positives
    NER_SKIP_WORDS = frozenset({
        "email", "phone", "address", "date", "name", "client", "project",
        "company", "organization", "department", "manager", "contact",
        "total", "amount", "balance", "cost", "price", "fee", "rate",
        "invoice", "receipt", "payment", "order", "contract", "agreement",
        "service", "support", "account", "member", "user", "customer",
    })

    def _redact_ner(self, text: str) -> str:
        """Apply NER-based redaction for names, organizations, locations."""
        if _nlp is None:
            return text
        
        doc = _nlp(text)
        # Process in reverse order to preserve offsets
        spans_to_redact = []
        for ent in doc.ents:
            # Map spaCy entity types to our categories
            type_map = {
                "PERSON": "PERSON_NAME",
                "ORG": "ORGANIZATION",
                "GPE": "LOCATION",
                "LOC": "LOCATION",
                "FAC": "LOCATION",
            }
            mapped = type_map.get(ent.label_)
            if mapped:
                # Skip common words that NER may incorrectly tag as PERSON/ORG
                if ent.text.lower() in self.NER_SKIP_WORDS:
                    continue
                # Skip single-character entities (likely noise)
                if len(ent.text) <= 2 and ent.label_ in ("PERSON", "ORG"):
                    continue
                spans_to_redact.append((ent.start_char, ent.end_char, mapped, ent.text))
        
        # Apply redaction in reverse order
        for start, end, category, text_val in reversed(spans_to_redact):
            key = f"{category}:{text_val}"
            if key in self._used_values:
                replacement = self._find_existing_var(category, text_val)
            else:
                self._used_values.add(key)
                var_name = self._next_var(category)
                var_placeholder = f"{{{var_name}}}"
                self.redaction_map.add(var_placeholder, text_val, category)
                replacement = var_placeholder
            
            text = text[:start] + replacement + text[end:]
        
        return text
    
    def _find_existing_var(self, category: str, value: str) -> str:
        """Find an existing variable for a value we've already seen."""
        key = f"{category}:{value}"
        for var, orig in self.redaction_map.map.items():
            if orig == value:
                return var
        # Shouldn't happen, but fallback
        var_name = self._next_var(category)
        var_placeholder = f"{{{var_name}}}"
        self.redaction_map.add(var_placeholder, value, category)
        return var_placeholder
    
    def _redact_abbreviations(self, text: str) -> str:
        """Redact custom abbreviation-based patterns (A, B, C, etc.).
        
        Matches patterns where an abbreviation letter acts as a label:
        e.g., 'Client A: value', 'Project B: value', 'A: John Smith'
        Requires the abbreviation to be followed by a colon, dash, or be a 
        standalone single letter followed by relevant context.
        """
        if not self.custom_abbreviations:
            return text
        
        for abbrev, description in self.custom_abbreviations.items():
            # Match patterns like "A: value", "A - value", "Client A: value"
            # Only match when the abbreviation is used as a label (followed by colon/dash/newline)
            pattern = rf"\b{re.escape(abbrev)}\s*[:\-]\s*([^\n,;.]+)"
            text = re.sub(
                pattern,
                self._make_abbrev_replace_fn(abbrev, description),
                text,
                flags=re.IGNORECASE,
            )
        
        return text
    
    def _make_abbrev_replace_fn(self, abbrev: str, description: str):
        """Create a regex replacement function for custom abbreviations."""
        def replace_fn(match: re.Match) -> str:
            original = match.group(1).strip()
            if not original:
                return match.group(0)
            
            category = f"CUSTOM_{abbrev}"
            key = f"{category}:{original}"
            
            if key in self._used_values:
                return self._find_existing_var(category, original)
            
            self._used_values.add(key)
            var_name = self._next_var(category)
            var_placeholder = f"{{{var_name}}}"
            self.redaction_map.add(var_placeholder, original, category)
            return f"{{{abbrev}}}={var_placeholder}"
        
        return replace_fn
    
    def redact(self, text: str) -> str:
        """
        Redact all sensitive data from text.
        
        Returns redacted text with template variables.
        The redaction map is available via self.redaction_map.
        """
        # Order matters: NER first (on original text for best context), 
        # then regex (structured data), then abbreviations (custom labels)
        text = self._redact_ner(text)
        text = self._redact_regex(text)
        text = self._redact_abbreviations(text)
        return text
    
    def save_redaction_map(self, doc_id: str) -> Path:
        """Save the redaction map to a local file."""
        map_file = self.redaction_dir / f"{doc_id}_redaction_map.json"
        self.redaction_map.save(map_file)
        return map_file