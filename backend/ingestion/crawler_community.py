"""
Jenkins AI Chatbot — Jenkins Community Discussions Crawler

Crawls https://community.jenkins.io (Discourse) using its public JSON API
to collect community Q&A topics.

Usage:
    python -m ingestion.crawler_community
    python -m ingestion.crawler_community --max-topics 50
"""

import argparse
import time

import requests

from ingestion.cleaner import (
    clean_html,
    make_record,
    normalize_whitespace,
    save_records,
)

BASE_URL = "https://community.jenkins.io"
CATEGORY = "community"
OUTPUT_FILE = "jenkins_community.json"

CRAWL_DELAY = 1.0
REQUEST_TIMEOUT = 15


def fetch_json(url: str) -> dict | None:
    """Fetch a JSON endpoint, return parsed dict or None on failure."""
    try:
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "JenkinsAIChatbot-Crawler/1.0 (educational project)",
                "Accept": "application/json",
            },
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"[crawler_community] Failed to fetch {url}: {e}")
        return None


def fetch_topic_list(page: int = 0) -> list[dict]:
    """Fetch a page of latest topics from Discourse."""
    url = f"{BASE_URL}/latest.json?page={page}"
    data = fetch_json(url)
    if data is None:
        return []

    topic_list = data.get("topic_list", {})
    topics = topic_list.get("topics", [])
    return topics


def fetch_topic_posts(topic_id: int) -> list[dict]:
    """Fetch all posts for a given topic."""
    url = f"{BASE_URL}/t/{topic_id}.json"
    data = fetch_json(url)
    if data is None:
        return []

    post_stream = data.get("post_stream", {})
    posts = post_stream.get("posts", [])
    return posts


def crawl(max_topics: int = 50) -> list[dict]:
    """
    Crawl Jenkins community discussions from Discourse.

    Fetches recent topics and their posts, cleans HTML content,
    and produces structured records.
    """
    print(f"[crawler_community] Starting crawl (max_topics={max_topics})")

    all_topics: list[dict] = []
    page = 0

    # Fetch topic list pages until we have enough
    while len(all_topics) < max_topics:
        topics = fetch_topic_list(page)
        if not topics:
            break
        all_topics.extend(topics)
        page += 1
        time.sleep(CRAWL_DELAY)

    all_topics = all_topics[:max_topics]
    print(f"[crawler_community] Found {len(all_topics)} topics")

    records: list[dict] = []
    for i, topic in enumerate(all_topics, 1):
        topic_id = topic["id"]
        title = topic.get("title", f"Topic {topic_id}")
        slug = topic.get("slug", "")
        topic_url = f"{BASE_URL}/t/{slug}/{topic_id}"

        print(f"[crawler_community] [{i}/{len(all_topics)}] Fetching: {title}")

        posts = fetch_topic_posts(topic_id)
        if not posts:
            continue

        # Combine all posts into one document
        post_texts: list[str] = []
        for post in posts:
            cooked = post.get(
                "cooked", ""
            )  # Discourse stores rendered HTML in 'cooked'
            if cooked:
                cleaned = clean_html(cooked)
                username = post.get("username", "unknown")
                post_texts.append(f"[{username}]:\n{cleaned}")

        content = normalize_whitespace("\n\n---\n\n".join(post_texts))

        if len(content) < 50:
            continue

        record = make_record(
            title=title,
            source_url=topic_url,
            content=content,
            category=CATEGORY,
        )
        records.append(record)

        time.sleep(CRAWL_DELAY)

    save_records(records, OUTPUT_FILE)
    print(f"[crawler_community] Crawl complete — {len(records)} topics collected")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Jenkins community discussions")
    parser.add_argument(
        "--max-topics", type=int, default=50, help="Max topics to crawl"
    )
    args = parser.parse_args()
    crawl(max_topics=args.max_topics)
