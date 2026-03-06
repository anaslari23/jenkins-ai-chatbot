"""
Jenkins AI Chatbot — Jenkins Documentation Crawler

Crawls https://www.jenkins.io/doc/ and its sub-pages to collect
Jenkins official documentation.

Usage:
    python -m ingestion.crawler_docs              # default max_pages=50
    python -m ingestion.crawler_docs --max-pages 10
"""

import argparse
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from ingestion.cleaner import clean_html, extract_title, make_record, save_records

BASE_URL = "https://www.jenkins.io/doc/"
DOMAIN = "www.jenkins.io"
CATEGORY = "docs"
OUTPUT_FILE = "jenkins_docs.json"

# Polite crawl delay in seconds
CRAWL_DELAY = 1.0
REQUEST_TIMEOUT = 15


def discover_links(html: str, base_url: str) -> list[str]:
    """Extract internal documentation links from the page."""
    soup = BeautifulSoup(html, "html.parser")
    links: set[str] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Only follow links under /doc/ on the same domain
        if parsed.netloc == DOMAIN and parsed.path.startswith("/doc/"):
            # Strip fragments and query params for deduplication
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            links.add(clean_url)

    return sorted(links)


def fetch_page(url: str) -> str | None:
    """Fetch a single page, return HTML or None on failure."""
    try:
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "JenkinsAIChatbot-Crawler/1.0 (educational project)"
            },
        )
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"[crawler_docs] Failed to fetch {url}: {e}")
        return None


def crawl(max_pages: int = 50) -> list[dict]:
    """
    Crawl Jenkins documentation starting from the docs landing page.

    Discovers internal links and follows them in BFS order, up to max_pages.
    Returns a list of cleaned JSON records.
    """
    print(f"[crawler_docs] Starting crawl (max_pages={max_pages})")

    visited: set[str] = set()
    queue: list[str] = [BASE_URL]
    records: list[dict] = []

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue

        visited.add(url)
        print(f"[crawler_docs] [{len(visited)}/{max_pages}] Fetching: {url}")

        html = fetch_page(url)
        if html is None:
            continue

        title = extract_title(html)
        content = clean_html(html)

        # Skip pages with very little content
        if len(content) < 100:
            print(f"[crawler_docs] Skipping (too short): {url}")
            continue

        record = make_record(
            title=title,
            source_url=url,
            content=content,
            category=CATEGORY,
        )
        records.append(record)

        # Discover new links
        new_links = discover_links(html, url)
        for link in new_links:
            if link not in visited:
                queue.append(link)

        time.sleep(CRAWL_DELAY)

    # Save results
    save_records(records, OUTPUT_FILE)
    print(f"[crawler_docs] Crawl complete — {len(records)} pages collected")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Jenkins documentation")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to crawl")
    args = parser.parse_args()
    crawl(max_pages=args.max_pages)
