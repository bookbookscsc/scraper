import re
import logging
import math
from concurrent.futures import ProcessPoolExecutor
from urllib3.exceptions import HTTPError
from requests_html import HTMLSession
from exceptions import (FailToGetTotalPageCountError,
                        PaginationError,
                        NotExistReviewsError)


class NaverBookScraper(object):

    def __init__(self, logger=None):
        self.session = HTMLSession()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://203.229.225.135/tm/?a=CR&b=MAC&c=300015071805&d=32&e=5301&f=Ym9vay5uYXZlci5jb20='
                       '&g=1527138088560&h=1527138088581&y=0&z=0&x=1&w=2017-11-06&in=5301_00014684&id=20180524',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/66.0.3359.181 Safari/537.36',
            'Connection': 'keep-alive'
        }
        self.book_detail_url = 'http://book.naver.com/bookdb/review.nhn?bid='
        self.logger = logger

    def scrape(self, bid):
        response = self.session.get(self.book_detail_url + str(bid),
                                    headers=self.headers)
        html = response.html
        txt_desc = html.xpath("//div[@class='txt_desc']//strong")
        star = txt_desc[0].text
        review_count = int(txt_desc[1].text)
        print(star, review_count)
        if review_count > 0:
            for review in self.get_recently_reviews_in(html, bid, 10):
                print(review)

    def get_recently_reviews_in(self, html, bid, count):
        def gen_reviews(html, bid, page):
            cur_page = 1
            while cur_page <= page:
                for dl in html.xpath("//ul[@id='reviewList']/li/dl"):
                    title = dl.xpath("//dt")[0].text
                    text = dl.xpath("//dd[starts-with(@id,'review_text')]")[0].text
                    date = dl.xpath("//dd[@class='txt_inline']")[-1].text
                    link = dl.xpath("//a")[0].attrs['href']
                    yield (title, text, date, link)
                cur_page += 1
                html = self.session.get(self.book_detail_url + f'{bid}&page={cur_page}').html
        page = math.ceil(count / 10)
        yield from gen_reviews(html, bid, page)

    def save(self):
        #db에 저장
        pass


def prepare(logger):
    formatter = logging.Formatter('asctime : %(asctime)s '
                                  'funcName : %(funcName)s, '
                                  'message : %(message)s '
                                  'lineNums : %(lineno)d')

    file_handler = logging.FileHandler('naver.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


if __name__ == '__main__':
    logger = logging.getLogger('Naver Books scraper logger')
    prepare(logger)
    worker_count = 12
    pool = ProcessPoolExecutor(max_workers=worker_count)
    try:
        scraper = NaverBookScraper(logger=logger)
        pool.map(scraper.scrape, [7150363, 13552931, 13495999])
    except Exception as e:
        logger.error(e)


