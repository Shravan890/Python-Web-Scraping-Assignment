"""Reusable data cleaning and normalization functions."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import pandas as pd

RATING_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
SCHEMA = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
]


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None
def clean_description(value: Any) -> str | None:
    text = clean_text(value)

    if not text:
        return None

    # Books to Scrape can sometimes expose a shortened preview
    # followed by the full description. Detect that repeated beginning
    # and keep the full version.
    prefix_length = 120
    search_limit = min(len(text), 1000)

    if len(text) > prefix_length * 2:
        prefix = text[:prefix_length]
        second_start = text.find(prefix, prefix_length, search_limit)

        if second_start != -1:
            text = text[second_start:]

    return text.strip() or None

def clean_price(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    cleaned = re.sub(r"[^0-9.\-]", "", str(value))
    if not cleaned:
        return None
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


def clean_rating(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value) if float(value).is_integer() else None
    normalized = str(value).strip().lower()
    if normalized in RATING_WORDS:
        return RATING_WORDS[normalized]
    try:
        number = int(float(normalized))
        return number
    except ValueError:
        return None


def clean_url(value: Any) -> str | None:
    if value is None:
        return None
    url = str(value).strip()
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url
    return None


def normalize_tags(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    parts = [clean_text(part) for part in text.split(",")]
    parts = [part for part in parts if part]
    return ", ".join(parts) if parts else None


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned = {key: record.get(key) for key in SCHEMA}
    for field in ["source", "name_or_title", "category", "author", "scraped_at"]:
        cleaned[field] = clean_text(cleaned[field])

    cleaned["description"] = clean_description(cleaned["description"])

    cleaned["source_url"] = clean_url(cleaned["source_url"])
    cleaned["price"] = clean_price(cleaned["price"])
    cleaned["rating"] = clean_rating(cleaned["rating"])
    cleaned["tags"] = normalize_tags(cleaned["tags"])
    return cleaned


def clean_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [clean_record(record) for record in records]


def to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(records, columns=SCHEMA)
