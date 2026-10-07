"""Record validation for the standardized dataset."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def _valid_url(value: Any) -> bool:
    if not value:
        return False
    parsed = urlparse(str(value))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_record(record: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if record.get("source") not in VALID_SOURCES:
        errors.append("unrecognized source")

    if not record.get("name_or_title"):
        errors.append("missing name_or_title")

    if not _valid_url(record.get("source_url")):
        errors.append("invalid or missing source_url")

    price = record.get("price")
    if price is not None:
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            errors.append("invalid price")

    rating = record.get("rating")
    if rating is not None:
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            errors.append("rating must be an integer from 1 to 5")

    return (not errors, errors)


def validate_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for record in records:
        ok, errors = validate_record(record)
        if ok:
            valid.append(record)
        else:
            rejected.append({"record": record, "errors": errors})

    return valid, rejected
