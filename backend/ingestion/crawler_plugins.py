"""
Jenkins AI Chatbot — Jenkins Plugins Crawler

Crawls https://plugins.jenkins.io/ to collect plugin descriptions,
usage instructions, and metadata.

Usage:
    python -m ingestion.crawler_plugins
    python -m ingestion.crawler_plugins --max-pages 20
"""

import argparse
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from ingestion.cleaner import clean_html, extract_title, make_record, save_records

BASE_URL = "https://plugins.jenkins.io/"
DOMAIN = "plugins.jenkins.io"
CATEGORY = "plugins"
OUTPUT_FILE = "jenkins_plugins.json"

CRAWL_DELAY = 1.0
REQUEST_TIMEOUT = 15


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
        print(f"[crawler_plugins] Failed to fetch {url}: {e}")
        return None


def discover_plugin_links(html: str) -> list[str]:
    """Extract plugin detail page links from the plugins index."""
    soup = BeautifulSoup(html, "html.parser")
    links: set[str] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(BASE_URL, href)
        parsed = urlparse(full_url)

        # Plugin detail pages are direct children of plugins.jenkins.io
        # e.g. https://plugins.jenkins.io/git/
        if parsed.netloc == DOMAIN and parsed.path not in ("/", ""):
            path = parsed.path.strip("/")
            # Only top-level plugin pages (single path segment)
            if path and "/" not in path and not path.startswith("ui"):
                clean_url = f"{parsed.scheme}://{parsed.netloc}/{path}/"
                links.add(clean_url)

    return sorted(links)


def crawl(max_pages: int = 50) -> list[dict]:
    """
    Crawl Jenkins plugin pages.

    Fetches the plugin index, discovers plugin links, then crawls
    each plugin's detail page.
    """
    print(f"[crawler_plugins] Starting crawl (max_pages={max_pages})")

    # Fetch the plugin index page
    index_html = fetch_page(BASE_URL)
    if index_html is None:
        print("[crawler_plugins] Failed to fetch plugin index")
        return []

    plugin_urls = discover_plugin_links(index_html)
    print(f"[crawler_plugins] Discovered {len(plugin_urls)} plugin links")

    # Limit to max_pages
    plugin_urls = plugin_urls[:max_pages]

    records: list[dict] = []
    for i, url in enumerate(plugin_urls, 1):
        print(f"[crawler_plugins] [{i}/{len(plugin_urls)}] Fetching: {url}")

        html = fetch_page(url)
        if html is None:
            continue

        title = extract_title(html)
        content = clean_html(html)

        if len(content) < 50:
            print(f"[crawler_plugins] Skipping (too short): {url}")
            continue

        record = make_record(
            title=title,
            source_url=url,
            content=content,
            category=CATEGORY,
        )
        records.append(record)

        time.sleep(CRAWL_DELAY)

    save_records(records, OUTPUT_FILE)
    print(f"[crawler_plugins] Crawl complete — {len(records)} plugins collected")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Jenkins plugins")
    parser.add_argument(
        "--max-pages", type=int, default=50, help="Max plugins to crawl"
    )
    args = parser.parse_args()
    crawl(max_pages=args.max_pages)
