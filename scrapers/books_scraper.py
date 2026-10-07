"""Books to Scrape source scraper."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCE_NAME = "Books to Scrape"
BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def _text(node) -> str | None:
    """Return cleaned text from an HTML node."""
    if node is None:
        return None

    value = node.get_text(" ", strip=True)
    return value or None


def _fetch(
    session: requests.Session,
    url: str,
    timeout: int,
    retries: int,
):
    """Fetch a URL with bounded retries."""
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

    raise last_error


def _parse_book(
    card,
    page_url: str,
    session: requests.Session,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    """Extract a book from a catalogue card and its product page."""

    link = card.select_one("h3 a")

    title = link.get("title") if link else None
    product_href = link.get("href") if link else None

    product_url = (
        urljoin(page_url, product_href)
        if product_href
        else None
    )

    price_node = card.select_one(".price_color")
    rating_node = card.select_one("p.star-rating")

    rating = None

    if rating_node:
        for class_name in rating_node.get("class", []):
            if class_name in RATING_MAP:
                rating = RATING_MAP[class_name]
                break

    category = None
    description = None

    # Visit the individual book page to obtain category and description.
    if product_url:
        try:
            product_response = _fetch(
                session,
                product_url,
                timeout,
                retries,
            )

            product_soup = BeautifulSoup(
                product_response.content,
                "html.parser",
            )

            # Example breadcrumb:
            # Home > Books > Category > Book Title
            breadcrumb = product_soup.select(
                "ul.breadcrumb li a"
            )

            if len(breadcrumb) >= 3:
                category = _text(breadcrumb[2])

            description_node = product_soup.select_one(
                "#product_description + p"
            )

            description = _text(description_node)

        except Exception:
            # Do not crash the entire scraper because one
            # product page failed.
            category = None
            description = None

    return {
        "source": SOURCE_NAME,
        "source_url": product_url,
        "name_or_title": _text(link) or title,
        "category": category,
        "price": _text(price_node),
        "rating": rating,
        "author": None,
        "tags": None,
        "description": description,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape_books(
    session: requests.Session | None = None,
    start_url: str = START_URL,
    timeout: int = 20,
    retries: int = 3,
    logger=None,
) -> tuple[list[dict[str, Any]], int, list[dict[str, str]]]:
    """Scrape all Books to Scrape catalogue pages."""

    session = session or requests.Session()

    session.headers.setdefault(
        "User-Agent",
        "Python-Web-Scraping-Assignment/1.0",
    )

    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    page_url = start_url
    page_number = 0

    while page_url:

        page_number += 1

        try:
            response = _fetch(
                session,
                page_url,
                timeout,
                retries,
            )

            soup = BeautifulSoup(
                response.content,
                "html.parser",
            )

            cards = soup.select(
                "article.product_pod"
            )

            if not cards:
                raise ValueError(
                    "No book cards found on page"
                )

            for card in cards:

                try:
                    record = _parse_book(
                        card,
                        page_url,
                        session,
                        timeout,
                        retries,
                    )

                    records.append(record)

                except Exception as exc:

                    errors.append(
                        {
                            "url": page_url,
                            "error": f"record parse: {exc}",
                        }
                    )

            next_link = soup.select_one(
                "li.next a"
            )

            if (
                next_link
                and next_link.get("href")
            ):
                page_url = urljoin(
                    page_url,
                    next_link.get("href"),
                )
            else:
                page_url = None

            if logger:
                logger.info(
                    "Books page %s processed: %s records",
                    page_number,
                    len(cards),
                )

        except Exception as exc:

            errors.append(
                {
                    "url": page_url,
                    "error": str(exc),
                }
            )

            if logger:
                logger.error(
                    "Books page %s failed: %s",
                    page_number,
                    exc,
                )

            # Continue with Quotes in the main pipeline.
            break

    return (
        records,
        page_number if page_number else 0,
        errors,
    )