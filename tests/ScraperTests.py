import unittest
from book_review_scraper import scraper
from book_review_scraper.bookstores import Naverbook, Kyobo


class ScraperTests(unittest.TestCase):

    def test_scraper_naverbook_meta_class(self):
        for review in scraper.get_reviews(isbn=9788932919126, bookstores=Naverbook, count=1):
            self.assertIsInstance(review, Naverbook.Review)

    def test_scraper_naverbook_iterable(self):
        for review in scraper.get_reviews(isbn=9788932919126, bookstores=[Naverbook], count=1):
            self.assertIsInstance(review, Naverbook.Review)

    def test_scraper_kyobo_meta_class(self):
        for review in scraper.get_reviews(isbn=9788932919126, bookstores=Kyobo, count=1):
            self.assertIsInstance(review, Kyobo.Review)

    def test_scraper_kyobo_iterable(self):
        for review in scraper.get_reviews(isbn=9788932919126, bookstores=[Kyobo], count=1):
            self.assertIsInstance(review, Kyobo.Review)

    def test_scraper_multiple_bookstroe(self):
        for review in scraper.get_reviews(isbn=9788932919126, bookstores=(Naverbook, Kyobo), count=1):
            print(review)
            self.assertTrue(isinstance(review, Naverbook.Review) or isinstance(review, Kyobo.Review))

