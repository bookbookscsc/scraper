import re
import math
import logging
from urllib3.exceptions import HTTPError
from requests_html import HTMLSession
from exceptions import (FailToGetTotalPageCountError,
                        PaginationError,
                        NotExistReviewsError)


class NaverBooksScraper:

    def __init__(self):
        self.session = HTMLSession()
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': f'www.naver.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36',
            'Connection': 'keep-alive'
        }

    def gen_bids(self, url):
        resp = self.session.get(url=url,
                                headers=self.headers)
        for link_in_html in resp.html.links:
            try:
                bid = re.search('http:\/\/book.naver.com\/bookdb\/book_detail\.nhn\?bid=(\d+)', link_in_html).group(1)
                yield int(bid)
            except AttributeError:
                continue

    def gen_review_links(self, bid, page=None):
        total_page_num = self.total_page_num(bid, page)

        def gen_review_links_per_page(bid, page):
            if (0 < page <= total_page_num) is False:
                raise PaginationError(book_name=bid)

            url = f'http://book.naver.com/bookdb/review.nhn?bid={bid}&page={page}'
            resp = self.session.get(url=url, headers=self.headers)
            if resp.ok:
                for review_list in resp.html.xpath("//ul[@id='reviewList']/li/dl/dt/a"):
                    yield review_list.attrs['href']
            else:
                raise HTTPError

        if page:
            yield from gen_review_links_per_page(bid, page)

        else:
            for page in range(1, 31):
                try:
                    yield from gen_review_links_per_page(bid, page)
                except (PaginationError, HTTPError):
                    break

    def total_page_num(self, bid, page):
        url = f'http://book.naver.com/bookdb/review.nhn?bid={bid}&page={page}'
        total_reviews_span = self.session.get(url=url, headers=self.headers).html.xpath("//span[@class='num']")[0]

        if total_reviews_span is None:
            raise FailToGetTotalPageCountError(book_name=bid)

        total_reviews = int(total_reviews_span.search('({}건)')[0].replace(',', ''))

        if total_reviews == 0:
            raise NotExistReviewsError(book_name=bid)

        total_page_num = math.ceil(total_reviews / 10)
        return total_page_num


if __name__ == '__main__':
    naverbooks_logger = logging.getLogger('Naver Books scraper logger')
    formatter = logging.Formatter('asctime : %(asctime)s '
                                  'funcName : %(funcName)s, '
                                  'message : %(message)s '
                                  'lineNums : %(lineno)d')

    file_handler = logging.FileHandler('naver.log')
    file_handler.setFormatter(formatter)
    naverbooks_logger.addHandler(file_handler)
    naverbooks_logger.setLevel(logging.INFO)

    naverbooks_scraper = NaverBooksScraper()

    try:
        for bid in naverbooks_scraper.gen_bids(url='http://book.naver.com/'):
            naverbooks_logger.info(f'try to get links, bid {bid}')
            try:
                for link in naverbooks_scraper.gen_review_links(bid, page=1):
                    logging.info(f'links of book, bid : {bid}')
            except NotExistReviewsError:
                continue
            logging.info(f'success to get links, bid {bid}')
    except Exception as e:
        naverbooks_logger.error(e)
