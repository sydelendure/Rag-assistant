# Regular Expressions & Type Hints #
import re
from typing import List, Dict, Union


# Major Topic & Chapter Header Detection #
def _is_major_topic(line: str) -> bool:
    """Detect if a line represents a major policy or chapter title."""
    clean = line.strip()
    if not clean or len(clean) > 80:
        return False

    # Patterns like: "POLICY: TRAVEL", "CHAPTER 2: LEAVE", "Code of Conduct", "PART I"
    if re.match(r"^(?:CHAPTER|PART|SECTION|MODULE)\s+[0-9IVXLCDM]+", clean, re.IGNORECASE):
        return True
    if re.search(r"\b(?:POLICY|GUIDELINES|CODE OF CONDUCT|HANDBOOK)\b", clean, re.IGNORECASE):
        return True
    if clean.startswith("# ") or clean.startswith("## "):
        return True
    if clean.isupper() and len(clean.split()) <= 6 and len(clean) >= 4:
        return True

    return False


# Sub-Section & Policy Clause Header Detection #
def _is_sub_section(line: str) -> bool:
    """Detect if a line represents a sub-section header."""
    clean = line.strip()
    if not clean or len(clean) > 65:
        return False

    # If it ends with a period and is a full sentence, it's body text, not a header
    if clean.endswith(".") and len(clean.split()) > 4:
        return False

    # Matches short titles: "1. Purpose", "2.1 Travel Allowance", "Section 3: Eligibility"
    if re.match(r"^\d+(?:\.\d+)*\.?\s+[A-Z][a-zA-Z0-9\s/&-]{2,50}$", clean):
        return True
    if re.match(r"^(?:Section|Article|Clause|Rule)\s+[0-9IVXLCDM]+", clean, re.IGNORECASE):
        return True
    if clean.startswith("### ") or clean.startswith("#### "):
        return True

    return False


# Recursive Window Boundary Splitter (750 chars / 100 overlap) #
def _split_long_text(text: str, max_chars: int = 750, overlap: int = 100) -> List[str]:
    """Split very long sections into overlapping sub-chunks."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to break on paragraph or sentence boundary
        split_point = text.rfind("\n", start, end)
        if split_point == -1 or split_point <= start:
            split_point = text.rfind(". ", start, end)
        if split_point == -1 or split_point <= start:
            split_point = end
        else:
            split_point += 2  # Include period and space

        chunks.append(text[start:split_point].strip())
        start = max(start + 1, split_point - overlap)

    return chunks


# Hierarchical Semantic Document Chunker #
def chunk_document(
    pages_or_text: Union[List[Dict[str, any]], str],
    document_name: str,
) -> List[Dict[str, any]]:
    """
    Chunk multi-page policy documents with hierarchical topic tracking and page numbers.

    Supports:
    - List of page dicts: [{"page": 1, "text": "..."}, {"page": 2, "text": "..."}]
    - Raw text string (falls back to page 1)
    """
    if isinstance(pages_or_text, str):
        pages = [{"page": 1, "text": pages_or_text}]
    else:
        pages = pages_or_text

    chunks = []
    clean_doc_name = document_name.replace("_", " ")
    for ext in [".pdf", ".csv", ".xlsx", ".xls", ".docx", ".doc", ".txt", ".md", ".png", ".jpg", ".jpeg", ".webp"]:
        clean_doc_name = clean_doc_name.replace(ext, "")

    current_topic = clean_doc_name
    current_section = "General Overview"
    current_content = []
    current_page = 1

    # Chunk Flush Closure #
    def flush_chunk():
        nonlocal current_content, current_section, current_topic, current_page
        if current_content:
            full_text = " ".join(current_content).strip()
            if full_text:
                sub_chunks = _split_long_text(full_text)
                for sc in sub_chunks:
                    chunks.append(
                        {
                            "text": sc,
                            "document": document_name,
                            "topic": current_topic,
                            "section": current_section,
                            "page": current_page,
                        }
                    )
            current_content = []

    # Iterate Through Lines & Detect Hierarchies #
    for page_data in pages:
        page_num = page_data.get("page", 1)
        raw_text = page_data.get("text", "")
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        for line in lines:
            if _is_major_topic(line):
                flush_chunk()
                current_topic = line.lstrip("#").strip()
                current_section = "Overview"
                current_page = page_num
            elif _is_sub_section(line):
                flush_chunk()
                current_section = line.lstrip("#").strip()
                current_page = page_num
            else:
                current_content.append(line)
                current_page = page_num

    # Flush Final Pending Chunk #
    flush_chunk()

    # Fallback Handling #
    if not chunks:
        for page_data in pages:
            raw_text = page_data.get("text", "").strip()
            if raw_text:
                sub_chunks = _split_long_text(raw_text)
                for sc in sub_chunks:
                    chunks.append(
                        {
                            "text": sc,
                            "document": document_name,
                            "topic": clean_doc_name,
                            "section": "General Overview",
                            "page": page_data.get("page", 1),
                        }
                    )

    return chunks


# Backward Compatibility Helper #
def chunk_text(text: str, document_name: str) -> List[Dict[str, str]]:
    """Backward compatibility wrapper for chunk_document."""
    return chunk_document(text, document_name)