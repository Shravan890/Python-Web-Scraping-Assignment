"""Quotes to Scrape source scraper."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCE_NAME = "Quotes to Scrape"
BASE_URL = "https://quotes.toscrape.com/"
START_URL = urljoin(BASE_URL, "page/1/")


def _text(node) -> str | None:
    if node is None:
        return None
    value = node.get_text(" ", strip=True)
    return value or None


def _fetch(session: requests.Session, url: str, timeout: int, retries: int):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries:
                raise
    raise last_error  # pragma: no cover


def _parse_quote(card, page_url: str) -> dict[str, Any]:
    quote_node = card.select_one("span.text")
    author_node = card.select_one("small.author")
    tags = [tag.get_text(strip=True) for tag in card.select("div.tags a.tag")]

    return {
        "source": SOURCE_NAME,
        "source_url": page_url,
        "name_or_title": _text(quote_node),
        "category": None,
        "price": None,
        "rating": None,
        "author": _text(author_node),
        "tags": ", ".join(tags) if tags else None,
        "description": None,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape_quotes(
    session: requests.Session | None = None,
    start_url: str = START_URL,
    timeout: int = 20,
    retries: int = 3,
    logger=None,
) -> tuple[list[dict[str, Any]], int, list[dict[str, str]]]:
    """Scrape all quote pages by following the site's Next link."""
    session = session or requests.Session()
    session.headers.setdefault("User-Agent", "Python-Web-Scraping-Assignment/1.0")
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    page_url = start_url
    page_number = 0

    while page_url:
        page_number += 1
        try:
            response = _fetch(session, page_url, timeout, retries)
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("div.quote")

            if not cards:
                raise ValueError("No quote cards found on page")

            for card in cards:
                try:
                    records.append(_parse_quote(card, page_url))
                except Exception as exc:
                    errors.append({"url": page_url, "error": f"record parse: {exc}"})

            next_link = soup.select_one("li.next a")
            page_url = urljoin(page_url, next_link.get("href")) if next_link and next_link.get("href") else None

            if logger:
                logger.info("Quotes page %s processed: %s records", page_number, len(cards))

        except Exception as exc:
            errors.append({"url": page_url, "error": str(exc)})
            if logger:
                logger.error("Quotes page %s failed: %s", page_number, exc)
            break

    return records, page_number if page_number else 0, errors
