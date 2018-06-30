import unittest
from book_review_scraper.bookstores import (Naverbook, Kyobo, Yes24)
from book_review_scraper.review import (NaverBookReview, Yes24SimpleReview,
                                        Yes24MemberReview, KloverReview, BookLogReview,
                                        Yes24BookReviewInfo)
from book_review_scraper.config import (NaverBookConfig, Yes24Config, KyoboConfig)

test_books_isbn13 = [9772383908006, 9791162540169, 9788932919126, 9788972756194]


class NaverbookTests(unittest.TestCase):

    def setUp(self):
        self.naverbook = Naverbook()

    def test_get_review(self):
        for isbn13 in test_books_isbn13:
            naver_config = NaverBookConfig(start=1, end=10)
            self.naverbook.scrape_config = naver_config
            for review in self.naverbook.get_reviews(isbn13):
                self.assertIsInstance(review, NaverBookReview)
            self.naverbook.scrape_config.start = 6
            self.naverbook.scrape_config.end = 10
            for review in self.naverbook.get_reviews(isbn13):
                self.assertIsInstance(review, NaverBookReview)

    def test_get_book_review_info(self):
        for isbn13 in test_books_isbn13:
            book_detail_info = self.naverbook.get_review_page_info(isbn13)
            self.assertIsInstance(book_detail_info.rating, float)
            self.assertIsInstance(book_detail_info.count, int)
            book_detail_info = self.naverbook.get_review_page_info(isbn13)
            self.assertIsInstance(book_detail_info.rating, float)
            self.assertIsInstance(book_detail_info.count, int)


class KyoboTests(unittest.TestCase):

    def setUp(self):
        self.kyobo = Kyobo()

    def test_klover_review(self):
        for isbn13 in test_books_isbn13:
            klover_config = KyoboConfig(KyoboConfig.KlOVER, start=1, end=10)
            self.kyobo.scrape_config = klover_config
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, KloverReview)
            self.kyobo.scrape_config.start = 6
            self.kyobo.scrape_config.end = 10
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, KloverReview)

    def test_book_log_review(self):
        for isbn13 in test_books_isbn13:
            book_log_config = KyoboConfig(KyoboConfig.BOOK_LOG, start=1, end=10)
            self.kyobo.scrape_config = book_log_config
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, BookLogReview)
            self.kyobo.scrape_config.start = 6
            self.kyobo.scrape_config.end = 10
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, BookLogReview)

    def test_get_book_detail_page_info(self):
        for isbn13 in test_books_isbn13:
            book_detail_info = self.kyobo.get_review_page_info(isbn13)
            self.assertIsInstance(book_detail_info.klover_rating, float)
            self.assertIsInstance(book_detail_info.book_log_rating, float)
            self.assertIsInstance(book_detail_info.book_log_count, int)

    def test_klover_and_boog_log_review(self):
        for isbn13 in test_books_isbn13:
            klover_config = KyoboConfig(KyoboConfig.KlOVER, start=1, end=10)
            book_log_config = KyoboConfig(KyoboConfig.BOOK_LOG, start=1, end=10)
            self.kyobo.scrape_config = klover_config
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, KloverReview)
            self.kyobo.scrape_config = book_log_config
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, BookLogReview)


class Yes24Tests(unittest.TestCase):

    def setUp(self):
        self.yes24 = Yes24()

    def test_simple_review(self):
        for isbn13 in test_books_isbn13:
            simple_review_config = Yes24Config(Yes24Config.SIMPLE, start=1, end=5)
            self.yes24.scrape_config = simple_review_config
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24SimpleReview)
            self.yes24.scrape_config.start = 6
            self.yes24.scrape_config.end = 10
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24SimpleReview)

    def test_member_review(self):
        for isbn13 in test_books_isbn13:
            simple_review_config = Yes24Config(Yes24Config.MEMBER, start=1, end=5)
            self.yes24.scrape_config = simple_review_config
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24MemberReview)
            self.yes24.scrape_config.start = 6
            self.yes24.scrape_config.end = 10
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24MemberReview)

    def test_simple_and_member_review(self):
        for isbn13 in test_books_isbn13:
            simple_review_config = Yes24Config(Yes24Config.SIMPLE, start=1, end=10)
            member_review_config = Yes24Config(Yes24Config.MEMBER, start=2, end=10)

            self.yes24.scrape_config = simple_review_config

            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24SimpleReview)

            self.yes24.scrape_config = member_review_config

            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24MemberReview)

    def test_get_review_info(self):
        for isbn13 in test_books_isbn13:
            review_info = self.yes24.get_review_page_info(isbn13)
            self.assertIsInstance(review_info, Yes24BookReviewInfo)
            self.assertIsInstance(review_info.content_rating, float)
            self.assertIsInstance(review_info.edit_rating, float)
            self.assertIsInstance(review_info.member_review_count, int)
            self.assertIsInstance(review_info.book_title, str)
            self.assertIsInstance(review_info.book_id, int)


if __name__ == '__main__':
    unittest.main()
