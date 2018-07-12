class BookReviewInfo:

    def __init__(self, book_id, book_title):
        self.book_id = book_id
        self.book_title = book_title

    @classmethod
    def instance(cls, *args):
        return cls(*args)

    def __str__(self):
        return self.__dict__.__str__()


class NaverbookBookReviewInfo(BookReviewInfo):

    def __init__(self, book_id, book_title, rating, count):
        super(NaverbookBookReviewInfo, self).__init__(book_id, book_title)
        self.rating = rating
        self.count = count


class KyoboBookReviewInfo(BookReviewInfo):

    def __init__(self, book_id, book_title, klover_rating, book_log_rating, book_log_count):
        super(KyoboBookReviewInfo, self).__init__(book_id, book_title)
        self.klover_rating = klover_rating
        self.book_log_rating = book_log_rating
        self.book_log_count = book_log_count


class Yes24BookReviewInfo(BookReviewInfo):

    def __init__(self, book_id, book_title, content_rating, edit_rating, member_review_count):
        super(Yes24BookReviewInfo, self).__init__(book_id, book_title)
        self.content_rating = content_rating
        self.edit_rating = edit_rating
        self.member_review_count = member_review_count


class InterparkBookReviewInfo(BookReviewInfo):

    def __init__(self, book_id, book_title, normal_rating, normal_review_count):
        super(InterparkBookReviewInfo, self).__init__(book_id, book_title)
        self.normal_rating = normal_rating
        self.normal_review_count = normal_review_count