import unittest
from book_review_scraper.helper import ReviewPagingHelper
from book_review_scraper.exceptions import HelperError


class ReviewPagingHelperTests(unittest.TestCase):

    def test_review_helper_init(self):
        try:
            _ = ReviewPagingHelper(10, 1, 10)
        except HelperError:
            self.assertTrue(True)
        else:
            self.fail()
        try:
            _ = ReviewPagingHelper(1, 10, -20)
        except HelperError:
            self.assertTrue(True)
        else:
            self.fail()
        helper = ReviewPagingHelper(-1, 20, 10)
        self.assertEqual(1, helper.start)

    def test_review_start_and_end_idx(self):
        helper = ReviewPagingHelper(10, 20, 10)
        self.assertEqual(9, helper.start_idx)
        self.assertEqual(10, helper.end_idx)
        helper.start = 0
        helper.end = 19
        self.assertEqual(0, helper.start_idx)
        self.assertEqual(9, helper.end_idx)
        helper.start = 9
        helper.end = 21
        self.assertEqual(8, helper.start_idx)
        self.assertEqual(1, helper.end_idx)
        helper.start = 19
        helper.end = 20
        self.assertEqual(8, helper.start_idx)
        self.assertEqual(10, helper.end_idx)
        helper.start = 16
        helper.end = 49
        self.assertEqual(5, helper.start_idx)
        self.assertEqual(9, helper.end_idx)
        self.assertEqual(49 - 16 + 1, helper.count_to_get)

