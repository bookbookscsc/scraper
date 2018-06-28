
class Review:
    def __init__(self, text, created, isbn13):
        self.text = text
        self.created = created
        self.isbn13 = isbn13

    def __str__(self):
        return self.__dict__.__str__()


class NaverBookReview(Review):
    def __init__(self, title, text, created, detail_link, thumb_nail_link, isbn13):
        super(NaverBookReview, self).__init__(text, created, isbn13)
        self.title = title
        self.detail_link = detail_link
        self.thumb_nail_link = thumb_nail_link


class KyoboReview(Review):
    def __init__(self, text, created, rating, likes, isbn13):
        super(KyoboReview, self).__init__(text, created, isbn13)
        self.rating = rating
        self.likes = likes


class KloverReview(KyoboReview):
    def __init__(self, text, created, rating, likes, isbn13):
        super(KloverReview, self).__init__(text, created, rating, likes, isbn13)


class BookLogReview(KyoboReview):
    def __init__(self, title, text, created, rating, likes, isbn13):
        super(BookLogReview, self).__init__(text, created, rating, likes, isbn13)
        self.title = title


class Yes24SimpleReview(Review):
    def __init__(self, text, rating, created, likes, isbn13):
        super(Yes24SimpleReview, self).__init__(text, created, isbn13)
        self.rating = rating
        self.likes = likes


class Yes24MemberReview(Review):
    def __init__(self, title, text, created, likes, content_rating, edit_rating, detail_link, isbn13):
        super(Yes24MemberReview, self).__init__(text, created, isbn13)
        self.title = title
        self.content_rating = content_rating
        self.edit_rating = edit_rating
        self.detail_link = detail_link
        self.likes = likes


class BookReviewInfo:

    def __init__(self, book_id, book_title, rating=None, count=None):
        self.book_id = book_id
        self.book_title = book_title
        self.rating = rating
        self.count = count


class NaverbookBookReviewInfo(BookReviewInfo):

    def __init__(self, book_id, book_title, rating, count):
        super(NaverbookBookReviewInfo, self).__init__(book_id, book_title, rating, count)


class KyoboBookReviewInfo(BookReviewInfo):

    def __init__(self, book_id, book_title, klover_rating, book_log_rating, count):
        self.klover_rating = klover_rating
        self.book_log_rating = book_log_rating
        super(KyoboBookReviewInfo, self).__init__(book_id, book_title, count=count)

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, dummy):
        self._rating = ((self.klover_rating / 2) + self.book_log_rating) / 2


class Yes24BookReviewInfo(BookReviewInfo):

    def __init__(self, book_id, book_title, content_rating, edit_rating, count):
        self.content_rating = content_rating
        self.edit_rating = edit_rating
        super(Yes24BookReviewInfo, self).__init__(book_id, book_title, count=count)

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, dummy):
        self._rating = (self.edit_rating + self.edit_rating) / 2

