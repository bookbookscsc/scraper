import unittest
from book_review_scraper.exceptions import ISBNError, PagingError
from book_review_scraper.bookstores import Naverbook, Kyobo


class NaverbookTest(unittest.TestCase):

    def setUp(self):
        self.naverbook = Naverbook()

    def test_isbn_2_book_id(self):
        self.assertEqual(13608565, self.naverbook._find_book_id_with(9788932919126))
        self.assertEqual(13588502, self.naverbook._find_book_id_with('9788954651288'))
        self.assertEqual(8789740, self.naverbook._find_book_id_with(9788954634755))
        self.assertEqual(8752557, self.naverbook._find_book_id_with('9788954634526'))
        self.assertEqual(9651139, self.naverbook._find_book_id_with(9788954637954))
        self.assertEqual(10486743, self.naverbook._find_book_id_with('9788954640084'))
        self.assertEqual(7148809, self.naverbook._find_book_id_with(9788954620628))
        self.assertRaises(ISBNError, self.naverbook._find_book_id_with, 123123)
        self.assertRaises(ISBNError, self.naverbook._find_book_id_with, '123123')
        self.assertRaises(ISBNError, self.naverbook._find_book_id_with, '978895462062')

    def test_get_book_detail_page_info(self):
        book_detail_info = self.naverbook.get_review_page_info(9788932919126)
        self.assertIsInstance(book_detail_info['stars'], float)
        self.assertIsInstance(book_detail_info['total'], int)
        book_detail_info = self.naverbook.get_review_page_info(9791188461332)
        self.assertIsInstance(book_detail_info['stars'], float)
        self.assertIsInstance(book_detail_info['total'], int)

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


class KyoboTest(unittest.TestCase):

    def setUp(self):
        self.kyobo = Kyobo()

    def test_get_book_detail_page_info(self):
        book_detail_info = self.kyobo.get_review_page_info(9791162540169)
        self.assertIsInstance(book_detail_info['stars'], float)
        self.assertIsInstance(book_detail_info['total'], int)
        book_detail_info = self.kyobo.get_review_page_info(9791188461332)
        self.assertIsInstance(book_detail_info['stars'], float)
        self.assertIsInstance(book_detail_info['total'], int)

    def test_get_reviews(self):
        self.assertEqual(15, len(list(self.kyobo.get_reviews(9791162540169))))
        self.assertEqual(1, len(list(self.kyobo.get_reviews(9791162540169))))

    def test_scraping_reviews_content(self):
        for review in self.kyobo.get_reviews(9791158160784, 5):
            self.assertIsInstance(review.text, str)
            self.assertIsInstance(review.created, str)
            self.assertIsInstance(review.rating, float)
            self.assertIsInstance(review.likes, int)


if __name__ == '__main__':
    unittest.main()
