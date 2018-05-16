class BookScrapingError(Exception):
    def __init__(self, provider_name=None, book_name=None):
        self.provider_name = provider_name
        self.book_name = book_name


class ISBNNotFoundError(BookScrapingError):
    def __str__(self):
        return "페이지에서 ISBN 을 발견하지 못했습니다."


class BookLogDetailPopupNotOpenError(BookScrapingError):
    def __str__(self):
        return "북 로그 상세 페이지 팝업을 여는데 실패 했습니다."


class PaginationError(BookScrapingError):
    def __str__(self):
        return f"{self.book_name}, 올바른 페이지 범위가 아닙니다."


class NotExistReviewsError(BookScrapingError):
    def __str__(self):
        return f"{self.book_name} 의 리뷰가 없습니다."


class FailToGetTotalPageCountError(BookScrapingError):
    def __str__(self):
        return f"{self.book_name} 의 총 리뷰 개수를 구하는데 실패했습니다."
