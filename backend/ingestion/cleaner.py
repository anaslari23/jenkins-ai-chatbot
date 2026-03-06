"""
Jenkins AI Chatbot — HTML Cleaner & Text Extraction Utilities

Shared utilities used by all crawler modules to clean HTML content,
extract text, and produce structured JSON records.
"""

import json
import re
import uuid
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Comment

# Resolve project root (three levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_RAW_DIR = PROJECT_ROOT / "dataset" / "raw"


def clean_html(html: str) -> str:
    """
    Clean raw HTML and return plain text.

    Removes:
    - <script>, <style>, <nav>, <footer>, <header>, <aside> tags
    - HTML comments
    - Navigation elements (by common class/id patterns)
    - Normalises whitespace
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted tags entirely
    for tag_name in [
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "noscript",
        "iframe",
    ]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Remove common navigation / sidebar elements by class or id
    nav_patterns = re.compile(
        r"(navbar|nav-|sidebar|menu|breadcrumb|pagination|cookie|banner|advertisement|ad-)",
        re.IGNORECASE,
    )
    for el in soup.find_all(attrs={"class": nav_patterns}):
        el.decompose()
    for el in soup.find_all(attrs={"id": nav_patterns}):
        el.decompose()

    text = soup.get_text(separator="\n")
    return normalize_whitespace(text)


def normalize_whitespace(text: str) -> str:
    """Collapse excessive whitespace while preserving paragraph breaks."""
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    # Collapse multiple spaces on the same line
    text = re.sub(r"[ ]+", " ", text)
    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def extract_title(html: str) -> str:
    """Extract page title from HTML — prefers <title>, falls back to first <h1>."""
    soup = BeautifulSoup(html, "html.parser")

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return "Untitled"


def split_sections(text: str, max_length: int = 2000) -> list[str]:
    """
    Split text into sections.

    First tries to split on heading-like patterns (lines that look like
    markdown headings or ALL-CAPS lines).  If a section is still too long,
    splits on double-newline paragraph boundaries.
    """
    # Split on lines that look like headings
    heading_pattern = re.compile(r"\n(?=#{1,4}\s|[A-Z][A-Z\s]{4,}\n)")
    raw_sections = heading_pattern.split(text)

    sections: list[str] = []
    for section in raw_sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_length:
            sections.append(section)
        else:
            # Further split on paragraph boundaries
            paragraphs = section.split("\n\n")
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) + 2 <= max_length:
                    current_chunk = (
                        f"{current_chunk}\n\n{para}" if current_chunk else para
                    )
                else:
                    if current_chunk:
                        sections.append(current_chunk.strip())
                    current_chunk = para
            if current_chunk:
                sections.append(current_chunk.strip())

    return sections


def make_record(
    title: str,
    source_url: str,
    content: str,
    category: str,
    record_id: Optional[str] = None,
) -> dict:
    """
    Build a standard JSON record.

    Schema:
        id          — UUID string
        title       — page / document title
        source_url  — original URL
        content     — cleaned text
        category    — one of: docs, plugins, github, community
    """
    return {
        "id": record_id or str(uuid.uuid4()),
        "title": title,
        "source_url": source_url,
        "content": content,
        "category": category,
    }


def save_records(records: list[dict], filename: str) -> Path:
    """
    Save a list of records as a JSON file in dataset/raw/.

    Returns the path to the saved file.
    """
    DATASET_RAW_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATASET_RAW_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"[cleaner] Saved {len(records)} records → {filepath}")
    return filepath
