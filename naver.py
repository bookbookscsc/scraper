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
        self.session = HTMLSession(mock_browser=False)
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
        self.logger = None
        self.scraping_bid_sets = set()
        self.scraped_bid_sets = set()

    def update_scraping_bids_from(self, url):
        resp = self.session.get(url=url,
                                headers=self.headers)
        for link_in_html in resp.html.links:
            try:
                bid = re.search('http:\/\/book.naver.com\/bookdb\/book_detail\.nhn\?bid=(\d+)', link_in_html).group(1)
                if bid not in self.scraped_bid_sets:
                    self.scraping_bid_sets.add(bid)
            except AttributeError:
                continue
        del resp

    def gen_review_links(self, bid, page=0):
        total_page_num = self.total_page_num(bid, page)
        url = f'http://book.naver.com/bookdb/review.nhn?bid={bid}'
        self.update_scraping_bids_from(url)

        def gen_reviews_links_per_page(page):
            resp = self.session.get(url=f'{url}&page={page}', headers=self.headers)
            if resp.ok:
                for review_list in resp.html.xpath("//ul[@id='reviewList']/li/dl/dt/a"):
                    yield review_list.attrs['href']
            else:
                raise HTTPError
            del resp

        for page in range(1, total_page_num + 1):
            yield from gen_reviews_links_per_page(page)

    def total_page_num(self, bid, page):
        url = f'http://book.naver.com/bookdb/review.nhn?bid={bid}&page={page}'
        total_reviews_span = self.session.get(url=url, headers=self.headers).html.xpath("//span[@class='num']")[0]

        if total_reviews_span is None:
            raise FailToGetTotalPageCountError(book_name=bid)

        total_reviews = int(total_reviews_span.search('({}건)')[0].replace(',', ''))

        if total_reviews == 0:
            raise NotExistReviewsError(book_name=bid)

        total_page_num = math.ceil(total_reviews / 10)

        del total_reviews_span
        return total_page_num

    def set_logger(self, logger):
        self.logger = logger

    def start(self, start_url='http://book.naver.com'):
        self.update_scraping_bids_from(start_url)

        while True:
            bid = self.scraping_bid_sets.pop()
            print(f'bid : {bid}')
            print(f"current scraped_bid_sets count : {len(self.scraped_bid_sets)}")
            print(f"current scraping_bid_sets count : {len(self.scraping_bid_sets)}")
            try:
                for link in self.gen_review_links(bid):
                    print(link)

            except NotExistReviewsError:
                self.logger.error(f'book[bid={bid}], has not reviews')
                continue

            except PaginationError:
                self.logger.error(f'book[bid={bid}], reach end page')
                continue

            except FailToGetTotalPageCountError:
                self.logger.error(f'book[bid={bid}], fail to parse total reviews span')
                continue

            finally:
                self.scraped_bid_sets.add(bid)

            if not self.scraping_bid_sets:
                break


if __name__ == '__main__':
    naverbook_logger = logging.getLogger('Naver Books scraper logger')
    formatter = logging.Formatter('asctime : %(asctime)s '
                                  'funcName : %(funcName)s, '
                                  'message : %(message)s '
                                  'lineNums : %(lineno)d')

    file_handler = logging.FileHandler('naver.log')
    file_handler.setFormatter(formatter)
    naverbook_logger.addHandler(file_handler)
    naverbook_logger.setLevel(logging.INFO)

    naverbook_scraper = NaverBooksScraper()
    naverbook_scraper.logger = naverbook_logger

    try:
        naverbook_scraper.start()
    except Exception as e:
        naverbook_logger.error(e)
