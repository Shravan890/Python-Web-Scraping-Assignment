# AI_USAGE.md

## AI Tool Used

**Tool:** ChatGPT

## How AI Was Used

AI assistance was used for:

- Understanding the assignment requirements.
- Planning the project structure.
- Designing the common data model.
- Drafting Requests + BeautifulSoup scraper architecture.
- Reviewing pagination and error-handling approaches.
- Designing cleaning, validation, and deduplication functions.
- Generating initial unit-test ideas.
- Reviewing README/documentation structure.
- Debugging encoding issues in scraped text.
- Improving description cleaning after reviewing generated output.

## Representative Prompts

Examples of prompts used:

1. "Explain the Python web scraping assignment step by step."
2. "Help design a reusable scraper for Books to Scrape and Quotes to Scrape."
3. "How should duplicate detection handle whitespace and capitalization differences?"
4. "Review the validation and error-handling design for this scraper."
5. "Suggest unit tests for price, rating, URL cleaning, and duplicate detection."
6. "Review the generated CSV and identify data-quality problems."

## AI-Assisted Code

AI assistance contributed to the initial implementation of:

- `scrapers/books_scraper.py`
- `scrapers/quotes_scraper.py`
- `processing/cleaning.py`
- `processing/validation.py`
- `processing/deduplication.py`
- `main.py`
- `tests/test_processing.py`
- `README.md`

## Important Changes Made After Review

The generated implementation was reviewed and tested locally.

During review, the Books to Scrape output showed two data-quality issues:

1. Some non-ASCII characters in descriptions were incorrectly decoded.
2. Some book descriptions contained a repeated shortened beginning followed by the full description.

The scraper was corrected to parse HTTP response content using the response bytes, which fixed the character-encoding issue.

A reusable `clean_description()` function was also added to the cleaning layer to detect and remove the repeated description beginning.

These changes were tested by rerunning the unit tests and the complete scraping pipeline.

## Review and Verification

The final implementation was tested locally using Python 3.11.9.

Unit tests were executed with:

```bash
python -m unittest discover -s tests -v