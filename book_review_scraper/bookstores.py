import re
import math
from collections import namedtuple
from requests_html import HTMLSession
from book_review_scraper import cache
from book_review_scraper.exceptions import FindBookIDError, ScrapeReviewContentsError, ISBNError

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
    """ 인터넷서점을 나타내는 클래스

    """
    config = {}

    def __init__(self):
        self.session = HTMLSession()

    def _find_book_id_with_isbn13(self, isbn13):
        if re.match('[\d+]{13} ', str(isbn13)) is None:
            raise ISBNError(bookstore=self, isbn13=isbn13)
        url_to_find_id = self.url_to_find_id
        id_a_tag_xpath = self.id_a_tag_xpath
        response = self.session.get(url_to_find_id + f'{isbn13}', headers=config["headers"])
        try:
            return int(response.html.xpath(id_a_tag_xpath)[0].attrs['href'].split('=')[-1])
        except (ValueError, IndexError, AttributeError) as e:
            raise FindBookIDError(isbn13=isbn13, bookstore=self, reason=e)

    def _make_book_review_url(self, book_id):
        return self.book_review_url + f'{book_id}'

    def get_review_page_info(self, isbn13):
        book_id = self._find_book_id_with_isbn13(isbn13)
        book_review_url = self._make_book_review_url(book_id)
        book_detail_page_html = self.session.get(book_review_url, headers=config["headers"]).html
        page_info = {
            'id': book_id,
            'url': book_review_url,
            'html': book_detail_page_html,
        }
        return page_info

    @classmethod
    def get_reviews(cls, *args, **kwargs):
        raise NotImplementedError


class Naverbook(BookStore):

    Review = namedtuple("NaverbookReview", ["title", "text", "created", "detail_link", "thumb_nail_link"])

    def __init__(self):
        super().__init__()
        self.url_to_find_id = 'http://book.naver.com/search/search.nhn?sm=sta_hty.book&sug=&where=nexearch&query='
        self.id_a_tag_xpath = "//ul[@id='searchBiblioList']//a[starts-with(@href," \
                              "'http://book.naver.com/bookdb/book_detail.nhn?bid=')]"
        self.book_review_url = 'http://book.naver.com/bookdb/review.nhn?bid='
        self.review_info_xpath = "//div[@class='txt_desc']//strong"

    @cache.cache_book_id('Naverbooks')
    def _find_book_id_with_isbn13(self, isbn13):
        return super(Naverbook, self)._find_book_id_with_isbn13(isbn13)

    def get_review_page_info(self, isbn13):
        review_page_info = super(Naverbook, self).get_review_page_info(isbn13)
        review_info_component = review_page_info["html"].xpath(self.review_info_xpath)
        stars = float(re.search('\d\.?\d?', review_info_component[0].text).group())
        total = int(review_info_component[1].text)
        return {**review_page_info, **{'stars': stars, 'total': total}}

    @classmethod
    def get_reviews(cls, *args, **kwargs):
        isbn13 = kwargs['isbn13'] if 'isbn13' in kwargs else args[0]
        count = kwargs['count'] if 'count' in kwargs else args[1]
        bookstore = cls() if isinstance(cls, type) else cls
        if count <= 0:
            return

        review_page_info = bookstore.get_review_page_info(isbn13)
        book_id = review_page_info['id']
        html = review_page_info['html']

        def gen_reviews(html, book_id, page, count):
            cur_page = 1
            cur_count = 0
            while cur_page <= page:
                try:
                    for li in html.xpath("//ul[@id='reviewList']/li"):
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
                        if cur_count >= count:
                            return
                except (IndexError, AttributeError, ValueError) as e:
                    raise ScrapeReviewContentsError(bookstore=bookstore, isbn13=isbn13, reason=e)
                cur_page += 1
                html = bookstore.session.get(bookstore.book_review_url + f'{book_id}&page={cur_page}',
                                             headers=config["headers"]).html
        page = math.ceil(count / 10)
        yield from gen_reviews(html, book_id, page, count)

    def __str__(self):
        return "Naverbook"


class Kyobo(BookStore):

    Review = namedtuple("KyoboReview", ["text", "created", "rating", "likes"])

    def __init__(self):
        super().__init__()
        self.book_review_url = 'http://www.kyobobook.co.kr/product/detailViewKor.laf?barcode='

    def _find_book_id_with_isbn13(self, isbn13):
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

    @classmethod
    def get_reviews(cls, *args, **kwargs):
        isbn13 = kwargs['isbn13'] if 'isbn13' in kwargs else args[0]
        count = kwargs['count'] if 'count' in kwargs else args[1]
        bookstore = cls() if isinstance(cls, type) else cls
        if count <= 0:
            return
        review_page_info = bookstore.get_review_page_info(isbn13)
        html = review_page_info['html']

        def gen_reviews(html, page, count):
            cur_page = 1
            cur_count = 0
            while cur_page <= page:
                try:
                    for li in html.xpath("//ul[@class='board_list']/li/div[@class='comment_wrap']"):
                        date = li.xpath("//dl/dd[@class='date']")[0].text
                        rating = li.xpath("//dl/dd[@class='kloverRating']/span")[0].text
                        text = li.xpath("//dl/dd[@class='comment']/div[@class='txt']")[0].text
                        likes = li.xpath("//li[@class='cmt_like']/span")[0].text
                        yield Kyobo.Review(text=text.strip(), created=date, rating=float(rating), likes=int(likes))
                        cur_count += 1
                        if cur_count >= count:
                            return
                except (IndexError, AttributeError, ValueError) as e:
                    raise ScrapeReviewContentsError(bookstore=bookstore, isbn13=isbn13, reason=e)
                cur_page += 1
                js = f"javascript:_go_targetPage({cur_page})"
                html.render(script=js,
                            scrolldown=2,
                            wait=0.5,
                            keep_page=True)

        page = math.ceil(count / 15)
        yield from gen_reviews(html, page, count)

    def __str__(self):
        return "Kyobo"
