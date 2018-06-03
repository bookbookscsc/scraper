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


class BookIdCacheError(Exception):

    def __init__(self, table, isbn):
        self.table = table
        self.isbn = isbn

    def __str__(self):
        return f"Table : {self.table} isbn : {self.isbn}"


class BookIdCacheMissError(BookIdCacheError):
    
    def __str__(self):
        return super(BookIdCacheMissError, self).__str__() + "cache miss"


class BookIdCacheExpiredError(BookIdCacheError):

    def __str__(self):
        return super(BookIdCacheMissError, self).__str__() + "cache expired"


