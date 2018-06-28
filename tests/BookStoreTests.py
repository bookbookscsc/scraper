import unittest
from book_review_scraper.bookstores import (Naverbook, Kyobo, Yes24)
from book_review_scraper.review import (NaverBookReview, Yes24SimpleReview,
                                        Yes24MemberReview, KloverReview, BookLogReview)
from book_review_scraper.config import (NaverBookConfig, Yes24Config, KyoboConfig)


class NaverbookTests(unittest.TestCase):

    def setUp(self):
        self.naverbook = Naverbook()

    def test_get_review(self):
        naver_config = NaverBookConfig(start=1, end=10)
        self.naverbook.scrape_config = naver_config
        count = 0
        for review in self.naverbook.get_reviews(9791162540169):
            self.assertIsInstance(review, NaverBookReview)
            count += 1
        self.assertEqual(10, count)
        self.naverbook.scrape_config.start = 6
        self.naverbook.scrape_config.end = 10
        count = 0
        for review in self.naverbook.get_reviews(9791162540169):
            self.assertIsInstance(review, NaverBookReview)
            count += 1
        self.assertEqual(5, count)

    def test_get_book_review_info(self):
        book_detail_info = self.naverbook.get_review_page_info(9788932919126)
        self.assertIsInstance(book_detail_info.rating, float)
        self.assertIsInstance(book_detail_info.count, int)
        book_detail_info = self.naverbook.get_review_page_info(9791188461332)
        self.assertIsInstance(book_detail_info.rating, float)
        self.assertIsInstance(book_detail_info.count, int)


class KyoboTests(unittest.TestCase):

    def setUp(self):
        self.kyobo = Kyobo()

    def test_klover_review(self):
        klover_config = KyoboConfig(KyoboConfig.KlOVER, start=1, end=10)
        self.kyobo.scrape_config = klover_config
        count = 0
        for review in self.kyobo.get_reviews(9791162540169):
            self.assertIsInstance(review, KloverReview)
            count += 1
        self.assertEqual(10, count)
        self.kyobo.scrape_config.start = 6
        self.kyobo.scrape_config.end = 10
        count = 0
        for review in self.kyobo.get_reviews(9791162540169):
            self.assertIsInstance(review, KloverReview)
            count += 1
        self.assertEqual(5, count)

    def test_book_log_review(self):
        book_log_config = KyoboConfig(KyoboConfig.BOOK_LOG, start=1, end=10)
        self.kyobo.scrape_config = book_log_config
        count = 0
        for review in self.kyobo.get_reviews(9791162540169):
            self.assertIsInstance(review, BookLogReview)
            count += 1
        self.assertEqual(10, count)
        self.kyobo.scrape_config.start = 6
        self.kyobo.scrape_config.end = 10
        count = 0
        for review in self.kyobo.get_reviews(9791162540169):
            self.assertIsInstance(review, BookLogReview)
            count += 1
        self.assertEqual(5, count)

    def test_get_book_detail_page_info(self):
        book_detail_info = self.kyobo.get_review_page_info(9791162540169)
        self.assertIsInstance(book_detail_info.klover_rating, float)
        self.assertIsInstance(book_detail_info.book_log_rating, float)
        self.assertIsInstance(book_detail_info.book_log_count, int)

        book_detail_info = self.kyobo.get_review_page_info(9791188461332)
        self.assertIsInstance(book_detail_info.book_log_rating, float)
        self.assertIsInstance(book_detail_info.klover_rating, float)
        self.assertIsInstance(book_detail_info.book_log_count, int)

    def test_klover_and_boog_log_review(self):
        klover_config = KyoboConfig(KyoboConfig.KlOVER, start=1, end=10)
        book_log_config = KyoboConfig(KyoboConfig.BOOK_LOG, start=1, end=10)

        self.kyobo.scrape_config = klover_config

        for review in self.kyobo.get_reviews(9791162540169):
            self.assertIsInstance(review, KloverReview)

        self.kyobo.scrape_config = book_log_config

        for review in self.kyobo.get_reviews(9791162540169):
            self.assertIsInstance(review, BookLogReview)


class Yes24Tests(unittest.TestCase):

    def setUp(self):
        self.yes24 = Yes24()

    def test_simple_review(self):
        simple_review_config = Yes24Config(Yes24Config.SIMPLE, start=1, end=5)
        self.yes24.scrape_config = simple_review_config
        count = 0
        for review in self.yes24.get_reviews(9791162540169):
            self.assertIsInstance(review, Yes24SimpleReview)
            count += 1
        self.assertEqual(5, count)
        self.yes24.scrape_config.start = 6
        self.yes24.scrape_config.end = 10
        count = 0
        for review in self.yes24.get_reviews(9791162540169):
            self.assertIsInstance(review, Yes24SimpleReview)
            count += 1
        self.assertEqual(5, count)

    def test_member_review(self):
        simple_review_config = Yes24Config(Yes24Config.MEMBER, start=1, end=5)
        self.yes24.scrape_config = simple_review_config
        count = 0
        for review in self.yes24.get_reviews(9791162540169):
            self.assertIsInstance(review, Yes24MemberReview)
            count += 1
        self.assertEqual(5, count)
        self.yes24.scrape_config.start = 6
        self.yes24.scrape_config.end = 10
        count = 0
        for review in self.yes24.get_reviews(9791162540169):
            self.assertIsInstance(review, Yes24MemberReview)
            count += 1
        self.assertEqual(5, count)

    def test_simple_and_member_review(self):
        simple_review_config = Yes24Config(Yes24Config.SIMPLE, start=1, end=10)
        member_review_config = Yes24Config(Yes24Config.MEMBER, start=2, end=10)

        self.yes24.scrape_config = simple_review_config

        for review in self.yes24.get_reviews(9791162540169):
            self.assertIsInstance(review, Yes24SimpleReview)

        self.yes24.scrape_config = member_review_config

        for review in self.yes24.get_reviews(9791162540169):
            self.assertIsInstance(review, Yes24MemberReview)


if __name__ == '__main__':
    unittest.main()
