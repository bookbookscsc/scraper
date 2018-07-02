import unittest
from book_review_scraper.bookstores import (Naverbook, Kyobo, Yes24)
from book_review_scraper.review import (NaverBookReview, Yes24SimpleReview,
                                        Yes24MemberReview, KloverReview, BookLogReview,
                                        Yes24BookReviewInfo)
from book_review_scraper.config import (NaverBookConfig, Yes24Config, KyoboConfig)
from book_review_scraper.exceptions import NoReviewError, BookStoreSaleError, LastReviewError

many_reviews_books = [9791162540169, 9788932919126, 9788972756194]
less_reviews_books = [9788998342418]
no_review_book = 9772383908006
not_for_sale_in_yes24 = 9772383908006


class NaverbookTests(unittest.TestCase):

    def setUp(self):
        self.naverbook = Naverbook()

    def test_get_review(self):
        for isbn13 in many_reviews_books:
            self.naverbook.scrape_config = NaverBookConfig.blog(1, 10)
            for review in self.naverbook.get_reviews(isbn13):
                self.assertIsInstance(review, NaverBookReview)
                self.blog_review_type_check(review)
            self.naverbook.scrape_config.start = 6
            self.naverbook.scrape_config.end = 10
            for review in self.naverbook.get_reviews(isbn13):
                self.assertIsInstance(review, NaverBookReview)

    def test_get_book_review_info(self):
        for isbn13 in many_reviews_books:
            review_info = self.naverbook.get_review_info(isbn13)
            self.assertIsInstance(review_info.rating, float)
            self.assertIsInstance(review_info.count, int)
            review_info = self.naverbook.get_review_info(isbn13)
            self.assertIsInstance(review_info.rating, float)
            self.assertIsInstance(review_info.count, int)

    def blog_review_type_check(self, review):
        self.assertIsInstance(review.detail_link, str)
        if review.thumb_nail_link:
            self.assertIsInstance(review.thumb_nail_link, str)

    def test_no_review_book(self):
        try:
            next(self.naverbook.get_reviews(no_review_book))
        except NoReviewError:
            self.assertTrue(True)
        else:
            self.fail()

    def test_last_review(self):
        for isbn13 in less_reviews_books:
            self.naverbook.scrape_config.end = 11
            try:
                for review in self.naverbook.get_reviews(isbn13):
                    print(review)
            except LastReviewError:
                self.assertTrue(True)
            else:
                self.fail()


class KyoboTests(unittest.TestCase):

    def setUp(self):
        self.kyobo = Kyobo()

    def test_klover_review(self):
        for isbn13 in many_reviews_books:
            self.kyobo.scrape_config = KyoboConfig.klover(1, 10)
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, KloverReview)
                self.klover_review_type_check(review)
            self.kyobo.scrape_config.start = 6
            self.kyobo.scrape_config.end = 10
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, KloverReview)

    def test_book_log_review(self):
        for isbn13 in many_reviews_books:
            book_log_config = KyoboConfig(KyoboConfig.BOOK_LOG, start=1, end=10)
            self.kyobo.scrape_config = book_log_config
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, BookLogReview)
                self.book_log_review_type_check(review)
            self.kyobo.scrape_config.start = 6
            self.kyobo.scrape_config.end = 10
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, BookLogReview)

    def test_get_review_info(self):
        for isbn13 in many_reviews_books:
            review_info = self.kyobo.get_review_info(isbn13)
            self.assertIsInstance(review_info.klover_rating, float)
            self.assertIsInstance(review_info.book_log_rating, float)
            self.assertIsInstance(review_info.book_log_count, int)

    def test_klover_and_boog_log_review(self):
        for isbn13 in many_reviews_books:
            klover_config = KyoboConfig.klover(1, 10)
            book_log_config = KyoboConfig.book_log(1, 10)
            self.kyobo.scrape_config = klover_config
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, KloverReview)
            self.kyobo.scrape_config = book_log_config
            for review in self.kyobo.get_reviews(isbn13):
                self.assertIsInstance(review, BookLogReview)

    def klover_review_type_check(self, review):
        self.assertIsInstance(review.rating, float)
        self.assertIsInstance(review.likes, int)

    def book_log_review_type_check(self, review):
        self.assertIsInstance(review.rating, float)
        self.assertIsInstance(review.likes, int)

    def test_last_review(self):
        for isbn13 in less_reviews_books:
            try:
                self.kyobo.scrape_config.start = 10
                self.kyobo.scrape_config.end = 16
                for _ in self.kyobo.get_reviews(isbn13):
                    pass
            except LastReviewError:
                self.assertTrue(True)
            else:
                self.fail()


class Yes24Tests(unittest.TestCase):

    def setUp(self):
        self.yes24 = Yes24()

    def test_simple_review(self):
        for isbn13 in many_reviews_books:
            simple_review_config = Yes24Config.simple(1, 10)
            self.yes24.scrape_config = simple_review_config
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24SimpleReview)
                self.simple_review_type_check(review)
            self.yes24.scrape_config.start = 6
            self.yes24.scrape_config.end = 10
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24SimpleReview)

    def test_member_review(self):
        for isbn13 in many_reviews_books:
            simple_review_config = Yes24Config.member(1, 5)
            self.yes24.scrape_config = simple_review_config
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24MemberReview)
                self.member_review_type_check(review)
            self.yes24.scrape_config.start = 6
            self.yes24.scrape_config.end = 10
            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24MemberReview)

    def test_simple_and_member_review(self):
        for isbn13 in many_reviews_books:
            simple_review_config = Yes24Config.simple(1, 10)
            member_review_config = Yes24Config.member(2, 10)

            self.yes24.scrape_config = simple_review_config

            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24SimpleReview)

            self.yes24.scrape_config = member_review_config

            for review in self.yes24.get_reviews(isbn13):
                self.assertIsInstance(review, Yes24MemberReview)

    def test_get_review_info(self):
        for isbn13 in many_reviews_books:
            review_info = self.yes24.get_review_info(isbn13)
            self.assertIsInstance(review_info, Yes24BookReviewInfo)
            self.assertIsInstance(review_info.content_rating, float)
            self.assertIsInstance(review_info.edit_rating, float)
            self.assertIsInstance(review_info.member_review_count, int)
            self.assertIsInstance(review_info.book_title, str)
            self.assertIsInstance(review_info.book_id, int)

    def simple_review_type_check(self, review):
        self.assertIsInstance(review.rating, float)
        self.assertIsInstance(review.likes, int)

    def member_review_type_check(self, review):
        self.assertIsInstance(review.title, str)
        self.assertIsInstance(review.content_rating, float)
        self.assertIsInstance(review.edit_rating, float)
        self.assertIsInstance(review.likes, int)
        self.assertIsInstance(review.detail_link, str)

    def test_book_is_not_for_sale(self):
        try:
            next(self.yes24.get_reviews(not_for_sale_in_yes24))
        except BookStoreSaleError:
            self.assertTrue(True)
        else:
            self.fail()

    def test_last_review(self):
        for isbn13 in less_reviews_books:
            self.yes24.scrape_config.review_type = Yes24Config.SIMPLE
            self.yes24.scrape_config.end = 11
            try:
                for _ in self.yes24.get_reviews(isbn13):
                    pass
            except LastReviewError:
                self.assertTrue(True)
            else:
                self.fail()
            try:
                self.yes24.scrape_config.review_type = Yes24Config.MEMBER
                for _ in self.yes24.get_reviews(isbn13):
                    pass
            except LastReviewError:
                self.assertTrue(True)
            else:
                self.fail()


if __name__ == '__main__':
    unittest.main()
