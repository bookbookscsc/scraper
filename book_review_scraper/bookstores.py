import re
from collections import namedtuple
from requests_html import HTMLSession
from book_review_scraper import cache
from book_review_scraper.exceptions import FindBookIDError, ScrapeReviewContentsError, ISBNError, PagingError
from book_review_scraper.helper import ReviewPagingHelper


config = {
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://203.229.225.135/tm/?a=CR&b=MAC&c=300015071805&d=32&e=5301&f=Ym9vay5uYXZlci5jb20='
                       '&g=1527138088560&h=1527138088581&y=0&z=0&x=1&w=2017-11-06&in=5301_00014684&id=20180524',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/66.0.3359.181 Safari/537.36',
        }
    }


class BookStore(object):
    """ 인터넷서점을 나타내는 클래스들의 부모 클래스

    """

    def __init__(self, book_review_url, search_url=None, id_a_tag_xpath=None):
        """

        :param book_review_url: 책 리뷰 페이지 url
        :param search_url: 책 id 를 찾기 위한 검색 url
        :param id_a_tag_xpath: 책 id 가 있는 a_tag 를 찾기 위한 xpath 문자열
        """
        self.session = HTMLSession()
        self.book_review_url = book_review_url
        self.search_url = search_url
        self.id_a_tag_xpath = id_a_tag_xpath

    def _find_book_id_with(self, isbn13):
        """ isbn13 을 검색 해서 서점 책 id를 찾아내는 메서드

        :param isbn13: 책의 isbn13
        :return: 서점의 책 id
        """
        if re.match('[\d+]{13}', str(isbn13)) is None:
            raise ISBNError(bookstore=self, isbn13=isbn13)
        response = self.session.get(self.search_url + f'{isbn13}', headers=config["headers"])
        try:
            return self.find_id(response.html)
        except (ValueError, IndexError, AttributeError):
            raise FindBookIDError(isbn13=isbn13, bookstore=self)

    def _find_id(self, html):
        """ html 에서 id 를 찾아 내는 메서드
        :param html: html
        :return: 책 id
        """
        pass

    def _make_book_review_url(self, book_id):
        """ 책의 id를 사용해서 책 리뷰 페이지 url 을 만든다

        :param book_id: 서점의 책 id
        :return: 책의 리뷰 페이지 url
        """
        return self.book_review_url + f'{book_id}'

    def get_review_page_info(self, isbn13):
        """ 리뷰 페이지 정보를 얻는다

        :param isbn13: 얻고 싶은 책의 isbn13
        :return: 리뷰 페이지 정보를 담고 있는 딕셔너리, 서점의 책 id, 책 리뷰 페이지 url, 책 리뷰 페이지 html
        """
        book_id = self._find_book_id_with(isbn13)
        book_review_url = self._make_book_review_url(book_id)
        book_review_page_html = self.session.get(book_review_url, headers=config["headers"]).html
        page_info = {
            'id': book_id,
            'url': book_review_url,
            'html': book_review_page_html,
        }
        return page_info

    def prepare_gen_reviews(self, isbn13, start, end):
        """ 리뷰들을 가져올 준비를 한다.

        :param isbn13: 책의 isbn13
        :param start: 가져올 리뷰의 첫번째 인덱스
        :param end: 가져올 리뷰의 마지막 인덱스
        :return: 리뷰를 가져오기 위한 준비물들을 튜플형태로 리턴
        isbn13 : 책 isbn13,
        book_id : 책 id,
        start_page : start_idx 번째에 있는 리뷰가 있는 페이지,
        end_page : end_idx 번째에 있는 리뷰가 있는 페이지,
        start_review_idx : start_page 안에서 start_idx 번째 리뷰의 idx
        end_review_idx : end_page 안에서 end_idx 번째 리뷰의 idx
        count_to_get : 총 얻을 리뷰의 개수
        html : 리뷰 페이지의 html

        ex) start = 16, end = 49, count of reviews per page = 10
        start_page = 2 , end_page = 5
        start_review_idx = 5, end_review_idx = 9
        count_to_get = 34
        """
        review_page_info = self.get_review_page_info(isbn13)
        book_id = review_page_info['id']

        helper = ReviewPagingHelper(start, end, Naverbook.REVIEWS_PER_PAGE)

        start_page = helper.start_page
        end_page = helper.end_page
        start_review_idx = helper.start_idx
        end_review_idx = helper.end_idx
        count_to_get = helper.count_to_get
        html = review_page_info['html']

        if start_page != 1:
            response = self.session.get(self.book_review_url + f'{book_id}&page={start_page}',
                                        headers=config["headers"])
            if not response.ok:
                raise PagingError(bookstore=self.__str__(), isbn13=isbn13)
            html = response.html

        return isbn13, book_id, start_page, end_page, start_review_idx, end_review_idx, count_to_get, html

    def gen_reviews(self, isbn13, book_id, start_page, end_page,
                    start_review_idx, end_review_idx, count_to_get, html):
        raise NotImplementedError

    @classmethod
    def get_reviews(cls, isbn13, start=1, end=10):
        """ 책의 리뷰들을 가지고 온다. (각각 인터넷 서점의 기본 정렬 순)

        :param isbn13: 책 isbn13
        :param start: 가져올 리뷰의 첫번째 idx
        :param end: 가져올 리뷰의 마지막 idx
        :return: reviews 정보를 가지고 있는 제너레이터
        """
        bookstore = cls() if isinstance(cls, type) else cls
        prepared = bookstore.prepare_gen_reviews(isbn13, start, end)
        yield from bookstore.gen_reviews(*prepared)

    def __str__(self):
        return self.__class__.__name__


class Naverbook(BookStore):

    Review = namedtuple("NaverbookReview", ["title", "text", "created", "detail_link", "thumb_nail_link"])
    REVIEWS_PER_PAGE = 10

    def __init__(self):
        super().__init__(
            book_review_url='http://book.naver.com/bookdb/review.nhn?bid=',
            search_url='http://book.naver.com/search/search.nhn?sm=sta_hty.book&sug=&where=nexearch&query=',
            id_a_tag_xpath="//ul[@id='searchBiblioList']//a[starts-with(@href,"
                           "'http://book.naver.com/bookdb/book_detail.nhn?bid=')]"
        )
        self.review_info_xpath = "//div[@class='txt_desc']//strong"

    @cache.book_id('Naverbook')
    def _find_book_id_with(self, isbn13):
        return super(Naverbook, self)._find_book_id_with(isbn13)

    def _find_id(self, html):
        return int(html.xpath(self.id_a_tag_xpath)[0].attrs['href'].split('=')[-1])

    def get_review_page_info(self, isbn13):
        review_page_info = super(Naverbook, self).get_review_page_info(isbn13)
        review_info_component = review_page_info["html"].xpath(self.review_info_xpath)
        stars = float(re.search('\d\.?\d?', review_info_component[0].text).group())
        total = int(review_info_component[1].text)
        return {**review_page_info, **{'stars': stars, 'total': total}}

    def gen_reviews(self, isbn13, book_id, start_page, end_page,
                    start_review_idx, end_review_idx, count_to_get, html):
        cur_page = start_page
        cur_count = 0
        while cur_page <= end_page:
            s = 0 if (cur_page != start_page) else start_review_idx
            e = Naverbook.REVIEWS_PER_PAGE + 1 if (cur_page != end_page) else end_review_idx
            try:
                for li in html.xpath("//ul[@id='reviewList']/li")[s:e]:
                    title = li.xpath("//dl/dt")[0].text
                    text = li.xpath("//dl/dd[starts-with(@id,'review_text')]")[0].text
                    date = li.xpath("//dl/dd[@class='txt_inline']")[-1].text
                    detail_link = li.xpath("//dl/dt/a")[-1].attrs['href']
                    thumb_div = li.xpath("//div[@class='thumb']")
                    if thumb_div:
                        thumb_link = thumb_div[-1].xpath("//a/img")[-1].attrs['src']
                        yield Naverbook.Review(title=title, text=text, created=date,
                                               detail_link=detail_link, thumb_nail_link=thumb_link)
                    else:
                        yield Naverbook.Review(title, text=text, created=date,
                                               detail_link=detail_link, thumb_nail_link=None)
                    cur_count += 1
                    if cur_count >= count_to_get:
                        return
            except (IndexError, AttributeError, ValueError):
                raise ScrapeReviewContentsError(bookstore=self.__str__(), isbn13=isbn13)
            cur_page += 1
            response = self.session.get(self.book_review_url + f'{book_id}&page={cur_page}',
                                        headers=config["headers"])
            if not response.ok:
                raise PagingError(bookstore=self.__str__(), isbn13=isbn13)
            html = response.html


class Kyobo(BookStore):

    Review = namedtuple("KyoboReview", ["text", "created", "rating", "likes"])

    def __init__(self):
        super().__init__(book_review_url='http://www.kyobobook.co.kr/product/detailViewKor.laf?barcode=')

    def _find_book_id_with(self, isbn13):
        return isbn13

    def _make_book_review_url(self, book_id):
        return self.book_review_url + f'{book_id}' + '#review_simple'

    def get_review_page_info(self, isbn13):
        review_page_info = super(Kyobo, self).get_review_page_info(isbn13)
        html = review_page_info['html']
        html.render(retries=10, wait=2, scrolldown=5, sleep=0.3, keep_page=True)
        stars_info_text = html.xpath("//div[@class='klover_review']//strong[@class='score']")[-1].text
        stars = float(re.search('\d\.?\d?', stars_info_text).group())
        total = int(re.search("\((\d+)\)", html.xpath("//span[@class='kloverTotal']")[-1].text).group(1))
        return {**review_page_info, **{'stars': stars, 'total': total}}

    def gen_reviews(self, isbn13, book_id, start_page, end_page,
                    start_review_idx, end_review_idx, count_to_get, html):
        cur_page = start_page
        cur_count = 0
        while cur_page <= end_page:
            try:
                for li in html.xpath("//ul[@class='board_list']/li/div[@class='comment_wrap']"):
                    date = li.xpath("//dl/dd[@class='date']")[0].text
                    rating = li.xpath("//dl/dd[@class='kloverRating']/span")[0].text
                    text = li.xpath("//dl/dd[@class='comment']/div[@class='txt']")[0].text
                    likes = li.xpath("//li[@class='cmt_like']/span")[0].text
                    yield Kyobo.Review(text=text.strip(), created=date, rating=float(rating), likes=int(likes))
                    cur_count += 1
                    if cur_count >= count_to_get:
                        return
            except (IndexError, AttributeError, ValueError):
                raise ScrapeReviewContentsError(bookstore=self.__str__(), isbn13=isbn13)
            cur_page += 1
            js = f"javascript:_go_targetPage({cur_page})"
            html.render(script=js,
                        scrolldown=2,
                        wait=0.5,
                        keep_page=True)



