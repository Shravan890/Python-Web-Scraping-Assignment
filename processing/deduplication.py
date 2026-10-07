"""Duplicate detection based on normalized semantic keys."""

from __future__ import annotations

import re
from typing import Any


def normalize_key_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).casefold().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def duplicate_key(record: dict[str, Any]) -> tuple[str, ...]:
    source = normalize_key_text(record.get("source"))
    title = normalize_key_text(record.get("name_or_title"))
    author = normalize_key_text(record.get("author"))
    url = normalize_key_text(record.get("source_url"))

    if source == "books to scrape":
        # URL is the strongest identifier; title catches formatting differences.
        return source, url, title

    # Quotes do not have a unique product URL, so use source + quote + author.
    return source, title, author


def deduplicate_records(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen: set[tuple[str, ...]] = set()
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []

    for record in records:
        key = duplicate_key(record)
        if key in seen:
            duplicates.append(record)
        else:
            seen.add(key)
            unique.append(record)

    return unique, duplicates
