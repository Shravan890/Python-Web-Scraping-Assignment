# Python Web Scraping Interview Assignment

## 1. Overview

This project implements a reusable Python web-scraping and data-processing pipeline for:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

Pipeline:

**Scrape → Clean → Validate → Deduplicate → Consolidate → Export**

The implementation uses Requests + BeautifulSoup because the provided websites are static HTML practice sites and do not require browser automation.

## 2. Python Version

Recommended: Python 3.10+.

## 3. Project Structure

```text
Python_Web_Scraping_Assignment/
├── scrapers/
│   ├── __init__.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── output/
├── logs/
├── tests/
│   └── test_processing.py
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## 4. Installation

Create and activate a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 5. Run

```bash
python main.py
```

Optional:

```bash
python main.py --timeout 30 --retries 3
```

Outputs are created under `output/`:

- `final_dataset.csv`
- `summary_report.json`

Execution logs are written to:

- `logs/scraper.log`

## 6. Pagination

Books to Scrape starts at `/catalogue/page-1.html`. The scraper reads the `li.next a` link from each page and follows it until no Next link remains.

Quotes to Scrape starts at `/page/1/`. It also follows the site's `li.next a` link until the final page.

No fixed number of pages is hard-coded.

If an individual page fails after retries, the source scraper records the error and stops that source safely; the other source still runs.

## 7. Data Model

The common schema is:

- `source`
- `source_url`
- `name_or_title`
- `category`
- `price`
- `rating`
- `author`
- `tags`
- `description`
- `scraped_at`

Fields that do not apply to a source are stored as null/empty values rather than invented values.

## 8. Cleaning

Cleaning is intentionally separate from scraping.

- Whitespace is collapsed and trimmed.
- Prices are converted to numeric values.
- Book rating words (`One`–`Five`) are converted to integers 1–5.
- URLs are checked for HTTP/HTTPS schemes and a hostname.
- Tags are normalized into a comma-separated string.
- Empty text values become `None`.

## 9. Validation

A record is accepted only when:

- The source is recognized.
- `name_or_title` exists.
- `source_url` looks like a valid HTTP/HTTPS URL.
- Price is numeric and non-negative when present.
- Rating is an integer from 1 through 5 when present.

Rejected records and validation reasons are included in `summary_report.json`.

## 10. Deduplication

Duplicate detection is source-aware.

### Books

The key uses:

```text
normalized source + normalized source URL + normalized title
```

### Quotes

The key uses:

```text
normalized source + normalized quote text + normalized author
```

Normalization uses case folding, trimming, and collapsing repeated whitespace. This catches differences such as:

```text
"Example Book Title"
" Example Book Title "
"EXAMPLE BOOK TITLE"
```

without relying on exact raw string comparison.

## 11. Error Handling and Logging

Requests use timeouts and bounded retries.

Handled conditions include:

- connection/request failures
- HTTP errors
- timeouts
- missing selectors
- unexpected record formats
- invalid values
- individual page failures

Logging is written to `logs/scraper.log` and also displayed in the console.

## 12. Testing

Run:

```bash
python -m unittest discover -s tests -v
```

The included tests cover text cleanup, price conversion, rating conversion, URL validation, and duplicate detection.

## 13. Assumptions

- The provided sites remain available and retain their practice-site HTML structure.
- Only publicly accessible pages are scraped.
- No authentication, CAPTCHA, access control, or security mechanism is bypassed.
- Source-specific fields that do not exist are left empty/null.
- The scraper uses a descriptive User-Agent and bounded retries.

## 14. Known Limitations

- HTML selector changes on the source websites may require selector updates.
- If a source page fails completely, its next page cannot safely be discovered from that failed response, so that source stops while the other source continues.
- The pipeline is intended for this interview assignment, not as a high-volume production crawler.
- The source websites are educational scraping targets; their data should not be treated as real commercial inventory.

## 15. Reproducibility

From a clean environment:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The scraper generates a fresh dataset and summary report at runtime. Do not treat any pre-existing CSV/JSON files as authoritative; the source websites are the system of record for the assignment run.

## 16. AI Usage

See `AI_USAGE.md`.

## 17. Interview Talking Points

Be prepared to explain:

1. Why Requests + BeautifulSoup was chosen.
2. How the Next-link pagination works.
3. Why scraping and cleaning are separate.
4. Why null values are used for non-applicable fields.
5. How rating and price normalization works.
6. How duplicate keys are constructed.
7. Why validation occurs before deduplication.
8. How page failures are handled.
9. What happens if a selector changes.
10. How you would improve the solution for production.
