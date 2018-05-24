import re
import logging
from urllib3.exceptions import HTTPError
from requests_html import HTMLSession
from exceptions import (FailToGetTotalPageCountError,
                        PaginationError,
                        NotExistReviewsError)


class NaverBooksScraper:

    PAGE_LIMIT = 10

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
        self.logger = logger
        self.scraping_bid_sets = set()
        self.scraped_bid_sets = set()

    def update_scraping_bids_in(self, html):
        for link_in_html in html.links:
            try:
                bid = re.search('http:\/\/book.naver.com\/bookdb\/book_detail\.nhn\?bid=(\d+)', link_in_html).group(1)
                if bid not in self.scraped_bid_sets:
                    self.scraping_bid_sets.add(bid)
            except AttributeError:
                continue

    def gen_review_links(self, bid):
        url = f'http://book.naver.com/bookdb/review.nhn?bid={bid}'
        response = self.session.get(url, headers=self.headers)
        html = response.html
        self.update_scraping_bids_in(html)
        review_count = self.get_reviews_count(bid, html)
        self.logger.info(f'{bid} review count is {review_count}')
        del response

        def gen_reviews_links_per_page(cur_page):
            resp = self.session.get(url=f'{url}&page={cur_page}', headers=self.headers)
            try:
                if resp.ok:
                    for review_list in resp.html.xpath("//ul[@id='reviewList']/li/dl/dt/a"):
                        yield review_list.attrs['href']
                else:
                    raise HTTPError
            finally:
                del resp

        for page in range(1, NaverBooksScraper.PAGE_LIMIT):
            yield from gen_reviews_links_per_page(page)

    def get_reviews_count(self, bid, html):
        total_reviews_span = html.xpath("//span[@class='num']")[0]

        if total_reviews_span is None:
            raise FailToGetTotalPageCountError(book_name=bid)

        try:
            total_reviews = int(total_reviews_span.search('({}건)')[0].replace(',', ''))
        except ValueError:
            raise FailToGetTotalPageCountError(book_name=bid)

        return total_reviews

    def start(self, start_url='http://book.naver.com'):
        response = self.session.get(start_url, headers=self.headers)
        self.update_scraping_bids_in(response.html)
        del response

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

    try:
        scraper = NaverBooksScraper(logger=logger)
        scraper.start()
    except Exception as e:
        logger.error(e)


