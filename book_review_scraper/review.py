import book_review_scraper.parser as review_parser


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

    @classmethod
    def instance(cls, html, isbn13):
        return cls(*review_parser.parse_blog_review(html), isbn13)


class KyoboReview(Review):
    def __init__(self, text, created, rating, likes, isbn13):
        super(KyoboReview, self).__init__(text, created, isbn13)
        self.rating = rating
        self.likes = likes


class KloverReview(KyoboReview):
    def __init__(self, text, created, rating, likes, isbn13):
        super(KloverReview, self).__init__(text, created, rating, likes, isbn13)

    @classmethod
    def instance(cls, html, isbn13):
        return cls(*review_parser.parse_klover_review(html), isbn13)


class BookLogReview(KyoboReview):
    def __init__(self, title, text, created, rating, likes, isbn13):
        super(BookLogReview, self).__init__(text, created, rating, likes, isbn13)
        self.title = title

    @classmethod
    def instance(cls, html, isbn13):
        return cls(*review_parser.parse_book_log_review(html), isbn13)


class Yes24SimpleReview(Review):
    def __init__(self, text, rating, created, likes, isbn13):
        super(Yes24SimpleReview, self).__init__(text, created, isbn13)
        self.rating = rating
        self.likes = likes

    @classmethod
    def instance(cls, html, isbn13):
        return cls(*review_parser.parse_simple_review(html), isbn13)


class Yes24MemberReview(Review):
    def __init__(self, title, text, created, likes, content_rating, edit_rating, detail_link, isbn13):
        super(Yes24MemberReview, self).__init__(text, created, isbn13)
        self.title = title
        self.content_rating = content_rating
        self.edit_rating = edit_rating
        self.detail_link = detail_link
        self.likes = likes

    @classmethod
    def instance(cls, html, isbn13):
        return cls(*review_parser.parse_member_review(html), isbn13)


class InterparkNormalReview(Review):

    def __init__(self, title, text, created, rating, likes, isbn13):
        super(InterparkNormalReview, self).__init__(text, created, isbn13)
        self.title = title
        self.rating = rating
        self.likex = likes

    @classmethod
    def instance(cls, html, isbn13):
        return cls(*review_parser.parse_inter_normal_review(html), isbn13)


class InterparkExpectedReview(Review):
    pass
