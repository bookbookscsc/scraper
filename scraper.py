import re
import math
from functools import lru_cache
from requests_html import HTMLSession
from exceptions import FindBookIDError


class Review:
    def __init__(self, title, thumb_link, content, created_date, detail_link):
        self.title = title
        self.content = content
        self.thumb_link = thumb_link
        self.created_date = created_date
        self.detail_link = detail_link


class BookStore(object):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://203.229.225.135/tm/?a=CR&b=MAC&c=300015071805&d=32&e=5301&f=Ym9vay5uYXZlci5jb20='
                   '&g=1527138088560&h=1527138088581&y=0&z=0&x=1&w=2017-11-06&in=5301_00014684&id=20180524',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/66.0.3359.181 Safari/537.36',
        'Connection': 'keep-alive'
    }

    def find_book_id_with_isbn(self, isbn):
        if re.match('[\d+]{10}|[\d+]{13} ', str(isbn)) is None:
            raise FindBookIDError(isbn=isbn, store=self)

        url_to_find_id = self.url_to_find_id
        id_a_tag_xpath = self.id_a_tag_xpath
        response = self.session.get(url_to_find_id + f'{isbn}', headers=BookStore.headers)
        try:
            return int(response.html.xpath(id_a_tag_xpath)[0].attrs['href'].split('=')[-1])
        except Exception:
            raise FindBookIDError(isbn=isbn, store=self)

    def make_book_review_url(self, book_id):
        return self.book_review_url + f'{book_id}'

    def get_review_page_info(self, isbn):
        book_id = self.find_book_id_with_isbn(isbn)
        book_review_url = self.make_book_review_url(book_id)
        book_detail_page_html = self.session.get(book_review_url, headers=BookStore.headers).html
        page_info = {
            'id': book_id,
            'url': book_review_url,
            'html': book_detail_page_html,
        }
        return page_info

    def get_reviews(self, isbn, count):
        pass


class Naver(BookStore):

    def __init__(self):
        self.session = HTMLSession()
        self.url_to_find_id = 'http://book.naver.com/search/search.nhn?sm=sta_hty.book&sug=&where=nexearch&query='
        self.id_a_tag_xpath = "//ul[@id='searchBiblioList']//a[starts-with(@href," \
                              "'http://book.naver.com/bookdb/book_detail.nhn?bid=')]"
        self.book_review_url = 'http://book.naver.com/bookdb/review.nhn?bid='
        self.review_info_xpath = "//div[@class='txt_desc']//strong"

    @lru_cache(maxsize=128)
    def find_book_id_with_isbn(self, isbn):
        return super(Naver, self).find_book_id_with_isbn(isbn)

    def get_review_page_info(self, isbn):
        review_page_info = super(Naver, self).get_review_page_info(isbn)
        review_info_component = review_page_info["html"].xpath(self.review_info_xpath)
        stars = float(re.search('\d\.?\d?', review_info_component[0].text).group())
        total = int(review_info_component[1].text)
        return {**review_page_info, **{'stars': stars, 'total': total}}

    def get_reviews(self, isbn, count):
        if count <= 0:
            return
        review_page_info = self.get_review_page_info(isbn)
        book_id = review_page_info['id']
        html = review_page_info['html']

        def gen_reviews(html, book_id, page, count):
            cur_page = 1
            cur_count = 0
            while cur_page <= page:
                for li in html.xpath("//ul[@id='reviewList']/li"):
                    thumb_div = li.xpath("//div[@class='thumb']")
                    detail_link = None
                    thumb_link = None
                    if thumb_div:
                        detail_link = thumb_div[-1].xpath("//a")[-1].attrs['href']
                        thumb_link = thumb_div[-1].xpath("//a/img")[-1].attrs['src']
                    title = li.xpath("//dl/dt")[0].text
                    content = li.xpath("//dl/dd[starts-with(@id,'review_text')]")[0].text
                    date = li.xpath("//dl/dd[@class='txt_inline']")[-1].text
                    yield Review(title, content, date, detail_link, thumb_link)
                    cur_count += 1
                    if cur_count >= count:
                        return
                cur_page += 1
                html = self.session.get(self.book_review_url + f'{book_id}&page={cur_page}').html

        page = math.ceil(count / 10)
        yield from gen_reviews(html, book_id, page, count)

    def __str__(self):
        return "Naver Book"


class Kyobo(BookStore):

    def __init__(self):
        self.session = HTMLSession()
        self.book_review_url = 'http://www.kyobobook.co.kr/product/detailViewKor.laf?barcode='

    def find_book_id_with_isbn(self, isbn):
        return isbn

    def make_book_review_url(self, book_id):
        return self.book_review_url + f'{book_id}' + '#review_simple'

    def get_review_page_info(self, isbn):
        review_page_info = super(Kyobo, self).get_review_page_info(isbn)
        html = review_page_info['html']
        html.render(retries=15, wait=2, scrolldown=5, sleep=0.3, keep_page=True)
        stars_info_text = html.xpath("//div[@class='klover_review']//strong[@class='score']")[-1].text
        stars = float(re.search('\d\.?\d?', stars_info_text).group())
        total = int(re.search("\((\d+)\)", html.xpath("//span[@class='kloverTotal']")[-1].text).group(1))
        return {**review_page_info, **{'stars': stars, 'total': total}}

    def get_reviews(self, isbn, count):
        if count <= 0:
            return
        review_page_info = self.get_review_page_info(isbn)
        html = review_page_info['html']

        def gen_reviews(html, page, count):
            cur_page = 1
            cur_count = 0
            while cur_page <= page:
                for li in html.xpath("//ul[@class='board_list']/li"):
                    yield li
                    cur_count += 1
                    if cur_count >= count:
                        return
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

