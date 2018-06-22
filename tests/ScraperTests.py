import unittest
from book_review_scraper import scraper
from book_review_scraper.bookstores import Naverbook, Kyobo
from book_review_scraper.exceptions import ISBNError


class ScraperTests(unittest.TestCase):

    def test_scraper_naverbook_meta_class(self):
        for review in scraper.get_reviews(isbn13=9788932919126, bookstores=Naverbook):
            self.assertIsInstance(review, Naverbook.Review)

    def test_scraper_naverbook_iterable(self):
        for review in scraper.get_reviews(isbn13=9788932919126, bookstores=[Naverbook]):
            self.assertIsInstance(review, Naverbook.Review)

    def test_scraper_kyobo_meta_class(self):
        for review in scraper.get_reviews(isbn13=9788932919126, bookstores=Kyobo):
            self.assertIsInstance(review, Kyobo.Review)

    def test_scraper_kyobo_iterable(self):
        for review in scraper.get_reviews(isbn13=9788932919126, bookstores=[Kyobo]):
            self.assertIsInstance(review, Kyobo.Review)

    def test_scraper_multiple_bookstore(self):
        for review in scraper.get_reviews(isbn13=9788932919126, bookstores=(Naverbook, Kyobo)):
            self.assertTrue(isinstance(review, Naverbook.Review) or isinstance(review, Kyobo.Review))

    def test_scraper_ISBNError(self):
        gen = scraper.get_reviews(isbn13='wjenwj')
        self.assertRaises(ISBNError, next, gen)
