from book_review_scraper.exceptions import ConfigError


class ScrapeConfig:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class NaverBookConfig(ScrapeConfig):

    def __init__(self, start, end):
        super(NaverBookConfig, self).__init__(start, end)
        self.per_page = 10

    def url(self, book_id, page_num):
        return "https://book.naver.com/bookdb/review.nhn?bid={}&page={}".format(book_id, page_num)


class Yes24Config(ScrapeConfig):
    SIMPLE = 0
    MEMBER = 1

    def __init__(self, review_type, start, end):
        super(Yes24Config, self).__init__(start, end)
        self.review_type = review_type

    @property
    def review_type(self):
        return self._review_type

    @property
    def per_page(self):
        return 5

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


class KyoboConfig(ScrapeConfig):
    KlOVER = 0
    BOOK_LOG = 1

    def __init__(self, review_type, start, end):
        super(KyoboConfig, self).__init__(start, end)
        self.review_type = review_type

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
                    'gb=klover&barcode={}&ejkGb=KOR&mallGb=KOR&sortType=date&pageNumber={}&orderType=all'.format(book_id,
                                                                                                           page_num)
        else:
            return 'http://www.kyobobook.co.kr/product/detailViewMultiPopup.laf?' \
                   'pageGb=KOR&popupMode=memberReviewDetail&ejkGb=KOR&barcode={}' \
                   '&sortColumn=reg_date&targetPage{}=&pageNumber=1&perPage=10'.format(book_id, page_num)

