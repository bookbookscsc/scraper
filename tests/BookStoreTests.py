import unittest
from book_review_scraper.exceptions import ISBNError, PagingError, FindBookIDError
from book_review_scraper.bookstores import Naverbook, Kyobo, Yes24


class NaverbookTests(unittest.TestCase):

    def setUp(self):
        self.naverbook = Naverbook()

    def test_isbn_2_book_id(self):
        self.assertEqual(13608565, self.naverbook.get_review_page_info(9788932919126).book_id)
        self.assertEqual(13588502, self.naverbook.get_review_page_info('9788954651288').book_id)
        self.assertEqual(8789740, self.naverbook.get_review_page_info(9788954634755).book_id)
        self.assertEqual(8752557, self.naverbook.get_review_page_info('9788954634526').book_id)
        self.assertEqual(9651139, self.naverbook.get_review_page_info(9788954637954).book_id)
        self.assertEqual(10486743, self.naverbook.get_review_page_info('9788954640084').book_id)
        self.assertEqual(7148809, self.naverbook.get_review_page_info(9788954620628).book_id)
        self.assertRaises(ISBNError, self.naverbook.get_review_page_info, 123123)
        self.assertRaises(ISBNError, self.naverbook.get_review_page_info, '123123')
        self.assertRaises(ISBNError, self.naverbook.get_review_page_info, '978895462062')

    def test_get_book_detail_page_info(self):
        book_detail_info = self.naverbook.get_review_page_info(9788932919126)
        self.assertIsInstance(book_detail_info.rating, float)
        self.assertIsInstance(book_detail_info.total_cnt, int)
        book_detail_info = self.naverbook.get_review_page_info(9791188461332)
        self.assertIsInstance(book_detail_info.rating, float)
        self.assertIsInstance(book_detail_info.total_cnt, int)

    def test_get_reviews(self):
        self.assertEqual(20, len(list(self.naverbook.get_reviews(9791162540169, start=1, end=20))))
        self.assertEqual(7, len(list(self.naverbook.get_reviews(9791162540169, start=2, end=8))))
        self.assertEqual(15, len(list(self.naverbook.get_reviews(9791162540169, start=15, end=29))))
        self.assertEqual(10, len(list(self.naverbook.get_reviews(9791162540169))))

    def test_scraping_reviews_content(self):
        for review in self.naverbook.get_reviews(9791158160784, 5):
            self.assertIsInstance(review.title, str)
            self.assertIsInstance(review.text, str)
            self.assertIsInstance(review.created, str)
            self.assertIsInstance(review.detail_link, str)
            if review.thumb_nail_link:
                self.assertIsInstance(review.detail_link, str)


class KyoboTests(unittest.TestCase):

    def setUp(self):
        self.kyobo = Kyobo()

    def test_get_book_detail_page_info(self):
        book_detail_info = self.kyobo.get_review_page_info(9791162540169)
        self.assertIsInstance(book_detail_info.klover_rating, float)
        self.assertIsInstance(book_detail_info.rating, float)
        self.assertIsInstance(book_detail_info.count, int)

        book_detail_info = self.kyobo.get_review_page_info(9791188461332)
        self.assertIsInstance(book_detail_info.klover_rating, float)
        self.assertIsInstance(book_detail_info.rating, float)
        self.assertIsInstance(book_detail_info.count, int)

    def test_get_reviews(self):
        self.assertEqual(20, len(list(self.kyobo.get_reviews(9791162540169, start=1, end=20))))
        self.assertEqual(11, len(list(self.kyobo.get_reviews(9791162540169, start=10, end=20))))

    def test_scraping_reviews_content(self):
        for review in self.kyobo.get_reviews(9791158160784, 5):
            self.assertIsInstance(review.text, str)
            self.assertIsInstance(review.created, str)
            self.assertIsInstance(review.rating, float)
            self.assertIsInstance(review.likes, int)


class Yes24Tests(unittest.TestCase):

    def setUp(self):
        self.yes24 = Yes24()

    def test_get_book_detail_page_info(self):
        book_review_info = self.yes24.get_review_page_info(9788974782221)
        self.assertIsInstance(book_review_info.rating, float)
        self.assertIsInstance(book_review_info.edit_rating, float)
        self.assertIsInstance(book_review_info.content_rating, float)
        self.assertEqual('사람아 아, 사람아!', book_review_info.book_title)
        self.assertEqual(1451055, book_review_info.book_id)

    def test_get_review(self):
        reviews = list(self.yes24.get_reviews(9791162540169, start=10, end=20))

        self.assertEqual("누구나 자기의 이야기로 '방송인'이 될 수 있는 시대를 살아가는 이들을 위한 교과서.", reviews[0].text)
        self.assertEqual('대도서관 너무 좋아요 사랑합니다♡', reviews[-1].text)


if __name__ == '__main__':
    unittest.main()
