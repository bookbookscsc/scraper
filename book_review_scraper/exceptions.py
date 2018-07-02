
class BookScrapingError(Exception):
    def __init__(self, bookstore, isbn13):
        self.bookstore = bookstore
        self.isbn13 = isbn13

    def __str__(self):
        return f" BookStore : {self.bookstore} isbn : {self.isbn13}"


class NoReviewError(BookScrapingError):
    def __str__(self):
        return super(NoReviewError, self).__str__() + " 리뷰가 없습니다."


class LastReviewError(BookScrapingError):
    def __str__(self):
        return super(LastReviewError, self).__str__() + " 마지막 리뷰 입니다."


class BookStoreSaleError(BookScrapingError):
    def __str__(self):
        return f"isbn13 : {self.isbn13} 은 {self.bookstore} 에서 판매 하지 않습니다."


class ISBNError(BookScrapingError):
    def __str__(self):
        return super(ISBNError, self).__str__() + " ISBN13 형식이 아닙니다."


class PaginationError(BookScrapingError):
    def __str__(self):
        return super(PaginationError, self).__str__() + " PaginationError Error"


class FindBookIDError(BookScrapingError):
    def __str__(self):
        return super(FindBookIDError, self).__str__() + f" Fail to find book id with {self.isbn13}"


class ParsingReviewInfoError(BookScrapingError):
    def __str__(self):
        return super(ParsingReviewInfoError, self).__str__() + " 리뷰 정보를 파싱하는데 실패했습니다."


class ScrapeReviewContentsError(BookScrapingError):
    def __init__(self, bookstore, isbn13, idx):
        super(ScrapeReviewContentsError, self).__init__(bookstore, isbn13)
        self.idx = idx

    def __str__(self):
        return super(ScrapeReviewContentsError, self).__str__() \
               + f" Fail to Scrape Review Contents of {self.isbn13}" \
               + f" idx : {self.idx}"


class HelperError(Exception):
    pass


class StarImagesError(HelperError):
    pass


class ConfigError(Exception):
    pass
