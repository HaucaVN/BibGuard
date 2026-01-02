"""
Usage checker for bibliography entries in TeX files.
"""
from dataclasses import dataclass
from typing import Optional

from ..parsers.bib_parser import BibEntry
from ..parsers.tex_parser import TexParser, CitationContext


@dataclass
class UsageResult:
    """Result of checking if a bib entry is used."""
    entry_key: str
    is_used: bool
    usage_count: int
    contexts: list[CitationContext]
    line_numbers: list[int]
    
    @property
    def first_usage_line(self) -> Optional[int]:
        return self.line_numbers[0] if self.line_numbers else None


class UsageChecker:
    """Checks if bibliography entries are used in TeX files."""
    
    def __init__(self, tex_parser: TexParser):
        self.tex_parser = tex_parser
        self._cited_keys = tex_parser.get_all_cited_keys()
    
    def check_usage(self, entry: BibEntry) -> UsageResult:
        """Check if a bib entry is used in the TeX document."""
        key = entry.key
        is_used = key in self._cited_keys
        contexts = self.tex_parser.get_citation_contexts(key)
        
        return UsageResult(
            entry_key=key,
            is_used=is_used,
            usage_count=len(contexts),
            contexts=contexts,
            line_numbers=[ctx.line_number for ctx in contexts]
        )
    
    def get_unused_entries(self, entries: list[BibEntry]) -> list[BibEntry]:
        """Get list of entries that are not cited in the document."""
        unused = []
        for entry in entries:
            if entry.key not in self._cited_keys:
                unused.append(entry)
        return unused
    
    def get_missing_entries(self, entries: list[BibEntry]) -> list[str]:
        """Get list of citation keys that don't have corresponding bib entries."""
        entry_keys = {e.key for e in entries}
        missing = []
        for key in self._cited_keys:
            if key not in entry_keys:
                missing.append(key)
        return missing
    
    def get_combined_context(self, key: str, max_chars: int = 1000) -> str:
        """Get combined context for all usages of a key."""
        contexts = self.tex_parser.get_citation_contexts(key)
        if not contexts:
            return ""
        
        combined = []
        total_chars = 0
        
        for ctx in contexts:
            if total_chars + len(ctx.full_context) > max_chars:
                # Add truncated context
                remaining = max_chars - total_chars
                if remaining > 100:
                    combined.append(ctx.full_context[:remaining] + "...")
                break
            combined.append(ctx.full_context)
            total_chars += len(ctx.full_context)
        
        return "\n---\n".join(combined)
