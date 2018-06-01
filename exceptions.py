class BookScrapingError(Exception):
    def __init__(self, bookstore, isbn, reason=None):
        self.bookstore = bookstore
        self.isbn = isbn
        self.reason = reason

    def __str__(self):
        return f"Because of {self.reason}, In {self.bookstore}"


class FindBookIDError(BookScrapingError):
    def __str__(self):
        return super(FindBookIDError, self).__str__() + f"Fail to find book id with {self.isbn}"


class ScrapeReviewContentsError(BookScrapingError):
    def __str__(self):
        return super(ScrapeReviewContentsError, self).__str__() + f"Fail to Scrape Review Contents of {self.isbn}"


class BookLogDetailPopupNotOpenError(BookScrapingError):
    def __str__(self):
        return "북 로그 상세 페이지 팝업을 여는데 실패 했습니다."


class PaginationError(BookScrapingError):
    def __str__(self):
        return f"올바른 페이지 범위가 아닙니다."


class NotExistReviewsError(BookScrapingError):
    def __str__(self):
        return f"리뷰가 없습니다."


class FailToGetTotalPageCountError(BookScrapingError):
    def __str__(self):
        return f"총 리뷰 개수를 구하는데 실패했습니다."
