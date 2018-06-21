class BookScrapingError(Exception):
    def __init__(self, bookstore, isbn):
        self.bookstore = bookstore
        self.isbn = isbn

    def __str__(self):
        return f"BookStore : {self.bookstore} isbn : {self.isbn13}"


class ISBNError(BookScrapingError):
    def __str__(self):
        return super(ISBNError, self).__str__() + " ISBN Error"


class FindBookIDError(BookScrapingError):
    def __str__(self):
        return super(FindBookIDError, self).__str__() + f" Fail to find book id with {self.isbn13}"


class ScrapeReviewContentsError(BookScrapingError):
    def __str__(self):
        return super(ScrapeReviewContentsError, self).__str__() + f" Fail to Scrape Review Contents of {self.isbn13}"


class BookIdCacheError(Exception):

    def __init__(self, table, isbn13):
        self.table = table
        self.isbn13 = isbn13

    def __str__(self):
        return f" Table : {self.table} isbn : {self.isbn13}"


class BookIdCacheMissError(BookIdCacheError):
    
    def __str__(self):
        return super(BookIdCacheMissError, self).__str__() + " cache miss"


class BookIdCacheExpiredError(BookIdCacheError):

    def __str__(self):
        return super(BookIdCacheMissError, self).__str__() + " cache expired"


