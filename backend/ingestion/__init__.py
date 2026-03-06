"""
Jenkins AI Chatbot — Ingestion Package

Provides crawler modules and cleaning utilities for collecting
Jenkins knowledge from various sources.
"""

from ingestion.cleaner import (  # noqa: F401
    clean_html,
    extract_title,
    make_record,
    normalize_whitespace,
    save_records,
    split_sections,
)
from ingestion import (  # noqa: F401
    crawler_community,
    crawler_docs,
    crawler_github,
    crawler_plugins,
)
