"""Main entry point for the multi-source web scraping assignment."""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from processing.cleaning import SCHEMA, clean_records
from processing.deduplication import deduplicate_records
from processing.validation import validate_records
from scrapers.books_scraper import scrape_books
from scrapers.quotes_scraper import scrape_quotes

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "scraper.log"


def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("scraper")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    console_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-source scraping pipeline.")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    return parser.parse_args()


def run_pipeline(timeout: int = 20, retries: int = 3, output_dir: Path = OUTPUT_DIR) -> dict:
    logger = logging.getLogger("scraper")
    start = time.perf_counter()
    run_timestamp = datetime.now(timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Python-Web-Scraping-Assignment/1.0 (educational use)"
    })

    logger.info("Starting scraping pipeline")

    books, books_pages, books_errors = scrape_books(
        session=session, timeout=timeout, retries=retries, logger=logger
    )
    quotes, quotes_pages, quotes_errors = scrape_quotes(
        session=session, timeout=timeout, retries=retries, logger=logger
    )

    raw_records = books + quotes
    logger.info("Collected %s records total", len(raw_records))

    cleaned = clean_records(raw_records)
    valid, rejected = validate_records(cleaned)
    unique, duplicates = deduplicate_records(valid)

    df = pd.DataFrame(unique, columns=SCHEMA)
    dataset_path = output_dir / "final_dataset.csv"
    df.to_csv(dataset_path, index=False)

    elapsed = round(time.perf_counter() - start, 3)
    summary = {
        "run_timestamp_utc": run_timestamp,
        "execution_time_seconds": elapsed,
        "records_collected": {
            "Books to Scrape": len(books),
            "Quotes to Scrape": len(quotes),
            "total": len(raw_records),
        },
        "pages_processed": {
            "Books to Scrape": books_pages,
            "Quotes to Scrape": quotes_pages,
        },
        "records_after_cleaning": len(cleaned),
        "records_rejected_during_validation": len(rejected),
        "duplicates_detected_and_removed": len(duplicates),
        "final_record_count": len(unique),
        "page_errors": books_errors + quotes_errors,
        "validation_rejections": rejected,
        "notes": [
            "A source failure does not stop the other source.",
            "Duplicate detection is source-aware and uses normalized text.",
        ],
    }

    summary_path = output_dir / "summary_report.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("Final dataset: %s", dataset_path)
    logger.info("Summary report: %s", summary_path)
    logger.info("Pipeline completed in %.3f seconds", elapsed)
    return summary


if __name__ == "__main__":
    args = parse_args()
    configure_logging()
    run_pipeline(
        timeout=args.timeout,
        retries=args.retries,
        output_dir=Path(args.output_dir),
    )
