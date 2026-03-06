"""
Jenkins AI Chatbot — Jenkins GitHub Repositories Crawler

Uses the GitHub REST API to fetch README files from jenkinsci
organization repositories.

Usage:
    python -m ingestion.crawler_github
    python -m ingestion.crawler_github --max-repos 30

Set GITHUB_TOKEN env var for higher API rate limits.
"""

import argparse
import base64
import os
import re
import time

import requests

from ingestion.cleaner import make_record, normalize_whitespace, save_records

GITHUB_ORG = "jenkinsci"
API_BASE = "https://api.github.com"
CATEGORY = "github"
OUTPUT_FILE = "jenkins_github.json"

CRAWL_DELAY = 0.5
REQUEST_TIMEOUT = 15


def _headers() -> dict[str, str]:
    """Build request headers, optionally with GitHub auth token."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "JenkinsAIChatbot-Crawler/1.0 (educational project)",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def fetch_repos(max_repos: int = 30) -> list[dict]:
    """Fetch repository metadata from the jenkinsci GitHub org."""
    repos: list[dict] = []
    page = 1
    per_page = min(max_repos, 100)

    while len(repos) < max_repos:
        url = f"{API_BASE}/orgs/{GITHUB_ORG}/repos?type=public&sort=updated&per_page={per_page}&page={page}"
        print(f"[crawler_github] Fetching repos page {page}")

        try:
            resp = requests.get(url, headers=_headers(), timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[crawler_github] Failed to fetch repos: {e}")
            break

        data = resp.json()
        if not data:
            break

        repos.extend(data)
        page += 1
        time.sleep(CRAWL_DELAY)

    return repos[:max_repos]


def fetch_readme(owner: str, repo: str) -> str | None:
    """Fetch and decode a repository README via the GitHub API."""
    url = f"{API_BASE}/repos/{owner}/{repo}/readme"

    try:
        resp = requests.get(url, headers=_headers(), timeout=REQUEST_TIMEOUT)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[crawler_github] Failed to fetch README for {repo}: {e}")
        return None

    data = resp.json()
    content_b64 = data.get("content", "")
    if not content_b64:
        return None

    try:
        return base64.b64decode(content_b64).decode("utf-8", errors="replace")
    except Exception:
        return None


def clean_markdown(text: str) -> str:
    """
    Convert markdown to plain text by stripping common markdown syntax.
    """
    # Remove images
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # Convert links to just their text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove markdown emphasis
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
    # Remove code block markers
    text = re.sub(r"```[a-z]*\n?", "", text)
    # Remove inline code backticks
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Normalise whitespace
    return normalize_whitespace(text)


def crawl(max_repos: int = 30) -> list[dict]:
    """
    Crawl README files from jenkinsci GitHub repositories.
    """
    print(f"[crawler_github] Starting crawl (max_repos={max_repos})")

    repos = fetch_repos(max_repos)
    print(f"[crawler_github] Found {len(repos)} repositories")

    records: list[dict] = []
    for i, repo in enumerate(repos, 1):
        repo_name = repo["full_name"]
        repo_url = repo["html_url"]
        description = repo.get("description") or ""

        print(f"[crawler_github] [{i}/{len(repos)}] Fetching README: {repo_name}")

        readme_md = fetch_readme(GITHUB_ORG, repo["name"])
        if readme_md is None:
            print(f"[crawler_github] No README found for {repo_name}")
            continue

        content = clean_markdown(readme_md)

        # Prepend description if available
        if description:
            content = f"{description}\n\n{content}"

        if len(content) < 50:
            continue

        record = make_record(
            title=repo_name,
            source_url=repo_url,
            content=content,
            category=CATEGORY,
        )
        records.append(record)

        time.sleep(CRAWL_DELAY)

    save_records(records, OUTPUT_FILE)
    print(f"[crawler_github] Crawl complete — {len(records)} repos collected")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Jenkins GitHub repos")
    parser.add_argument("--max-repos", type=int, default=30, help="Max repos to crawl")
    args = parser.parse_args()
    crawl(max_repos=args.max_repos)
