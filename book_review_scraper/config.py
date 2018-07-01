from book_review_scraper.exceptions import ConfigError
from book_review_scraper.review import (NaverBookReview,
                                        KloverReview,
                                        BookLogReview,
                                        Yes24MemberReview,
                                        Yes24SimpleReview)


class ScrapeConfig:
    def __init__(self, review_type, start, end):
        self.review_type = review_type
        self.start = start
        self.end = end

    @property
    def li_xpath(self):
        return "//li"



class NaverBookConfig(ScrapeConfig):

    BLOG = 0

    def __init__(self, review_type, start, end):
        super(NaverBookConfig, self).__init__(review_type, start, end)

    @classmethod
    def blog(cls, start, end):
        return cls(NaverBookConfig.BLOG, start, end)

    @property
    def per_page(self):
        return 10

    @property
    def ul_xpath(self):
        return "//ul[@id='reviewList']"

    def url(self, book_id, page_num):
        return "https://book.naver.com/bookdb/review.nhn?bid={}&page={}".format(book_id, page_num)

    @property
    def review_meta_class(self):
        return NaverBookReview



class Yes24Config(ScrapeConfig):
    SIMPLE = 0
    MEMBER = 1

    def __init__(self, review_type, start, end):
        super(Yes24Config, self).__init__(review_type, start, end)

    @classmethod
    def simple(cls, start, end):
        return cls(Yes24Config.SIMPLE, start, end)

    @classmethod
    def member(cls, start, end):
        return cls(Yes24Config.MEMBER, start, end)

    @property
    def per_page(self):
        return 5

    @property
    def review_type(self):
        return self._review_type

    @review_type.setter
    def review_type(self, review_type):
        if review_type is not Yes24Config.SIMPLE and review_type is not Yes24Config.MEMBER:
            raise ConfigError()
        self._review_type = review_type

    def url(self, book_id, page_num):
        if self.review_type is Yes24Config.SIMPLE:
            return "http://www.yes24.com/24/communityModules/AwordReviewList/{}?PageNumber={}".format(book_id,
                                                                                                      page_num)
        else:
            return "http://www.yes24.com/24/communityModules/ReviewList/{}?SetYn=N&PageNumber={}".format(book_id,
                                                                                                         page_num)

    @property
    def review_meta_class(self):
        if self.review_type is Yes24Config.SIMPLE:
            return Yes24SimpleReview
        else:
            return Yes24MemberReview

    @property
    def ul_xpath(self):
        return "//ul[@class='list']"


class KyoboConfig(ScrapeConfig):
    KlOVER = 0
    BOOK_LOG = 1

    def __init__(self, review_type, start, end):
        super(KyoboConfig, self).__init__(review_type, start, end)

    @classmethod
    def klover(cls, start, end):
        return cls(KyoboConfig.KlOVER, start, end)

    @classmethod
    def book_log(cls, start, end):
        return cls(KyoboConfig.BOOK_LOG, start, end)

    @property
    def review_type(self):
        return self._review_type

    @review_type.setter
    def review_type(self, review_type):
        if review_type is not KyoboConfig.KlOVER and review_type is not KyoboConfig.BOOK_LOG:
            raise ConfigError()
        self._review_type = review_type

    @property
    def per_page(self):
        if self.review_type is KyoboConfig.KlOVER:
            return 15
        elif self.review_type is KyoboConfig.BOOK_LOG:
            return 10

    @property
    def ul_xpath(self):
        if self.review_type is KyoboConfig.KlOVER:
            return "//ul[@class='board_list']"
        elif self.review_type is KyoboConfig.BOOK_LOG:
            return "//ul[@class='list_detail_booklog']"

    @property
    def li_xpath(self):
        if self.review_type is KyoboConfig.KlOVER:
            return "//li/div[@class='comment_wrap']"
        elif self.review_type is KyoboConfig.BOOK_LOG:
            return "//li"

    def url(self, book_id, page_num):
        if self.review_type is KyoboConfig.KlOVER:
            return 'http://www.kyobobook.co.kr/product/productSimpleReviewSort.laf?' \
                    'gb=klover&barcode={}&ejkGb=KOR&mallGb=KOR&sortType=date&pageNumber={}' \
                   '&orderType=all'.format(book_id, page_num)
        else:
            return 'http://www.kyobobook.co.kr/product/detailViewMultiPopup.laf?' \
                   'pageGb=KOR&popupMode=memberReviewDetail&ejkGb=KOR&barcode={}' \
                   '&sortColumn=reg_date&targetPage{}=&pageNumber=1&perPage=10'.format(book_id, page_num)

    @property
    def review_meta_class(self):
        if self.review_type is KyoboConfig.KlOVER:
            return KloverReview
        else:
            return BookLogReview

