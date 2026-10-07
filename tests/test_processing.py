import unittest

from processing.cleaning import clean_price, clean_rating, clean_text, clean_url
from processing.deduplication import deduplicate_records


class TestCleaning(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(clean_text("  Hello   world "), "Hello world")

    def test_clean_price(self):
        self.assertEqual(clean_price("£51.77"), 51.77)

    def test_clean_rating(self):
        self.assertEqual(clean_rating("Three"), 3)
        self.assertEqual(clean_rating(5), 5)

    def test_clean_url(self):
        self.assertEqual(clean_url("https://example.com/a"), "https://example.com/a")
        self.assertIsNone(clean_url("not-a-url"))


class TestDeduplication(unittest.TestCase):
    def test_case_and_whitespace_duplicates(self):
        records = [
            {
                "source": "Quotes to Scrape",
                "source_url": "https://quotes.toscrape.com/page/1/",
                "name_or_title": " Example Quote ",
                "author": "John Doe",
            },
            {
                "source": "Quotes to Scrape",
                "source_url": "https://quotes.toscrape.com/page/2/",
                "name_or_title": "example quote",
                "author": "john doe",
            },
        ]
        unique, duplicates = deduplicate_records(records)
        self.assertEqual(len(unique), 1)
        self.assertEqual(len(duplicates), 1)


if __name__ == "__main__":
    unittest.main()
