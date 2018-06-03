import unittest
from exceptions import FindBookIDError
from book_review_scraper import Naverbook, Kyobo


class NaverbookTest(unittest.TestCase):

    def setUp(self):
        self.naverbook = Naverbook()

    def test_isbn_2_book_id(self):
        self.assertEqual(13608565, self.naverbook.find_book_id_with_isbn(9788932919126))
        self.assertEqual(13588502, self.naverbook.find_book_id_with_isbn('9788954651288'))
        self.assertEqual(8789740, self.naverbook.find_book_id_with_isbn(9788954634755))
        self.assertEqual(8752557, self.naverbook.find_book_id_with_isbn('9788954634526'))
        self.assertEqual(9651139, self.naverbook.find_book_id_with_isbn(9788954637954))
        self.assertEqual(10486743, self.naverbook.find_book_id_with_isbn('9788954640084'))
        self.assertEqual(7148809, self.naverbook.find_book_id_with_isbn(9788954620628))
        self.assertRaises(FindBookIDError, self.naverbook.find_book_id_with_isbn, 123123)
        self.assertRaises(FindBookIDError, self.naverbook.find_book_id_with_isbn, '123123')
        self.assertRaises(FindBookIDError, self.naverbook.find_book_id_with_isbn, '978895462062')

    def test_get_book_detail_page_info(self):
        book_detail_info = self.naverbook.get_review_page_info(9788932919126)
        self.assertIsInstance(book_detail_info['stars'], float)
        self.assertIsInstance(book_detail_info['total'], int)
        book_detail_info = self.naverbook.get_review_page_info(9791188461332)
        self.assertIsInstance(book_detail_info['stars'], float)
        self.assertIsInstance(book_detail_info['total'], int)

    def test_get_reviews(self):
        self.assertEqual(30, len(list(self.naverbook.get_reviews(9791162540169, 30))))
        self.assertEqual(40, len(list(self.naverbook.get_reviews(9791162540169, 40))))
        self.assertEqual(1, len(list(self.naverbook.get_reviews(9791162540169, 1))))

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
        self.assertEqual(15, len(list(self.kyobo.get_reviews(9791162540169, 15))))
        self.assertEqual(1, len(list(self.kyobo.get_reviews(9791162540169, 1))))

    def test_scraping_reviews_content(self):
        for review in self.kyobo.get_reviews(9791158160784, 5):
            self.assertIsInstance(review.text, str)
            self.assertIsInstance(review.created, str)
            self.assertIsInstance(review.rating, float)
            self.assertIsInstance(review.likes, int)


if __name__ == '__main__':
    unittest.main()
