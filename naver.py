from requests_html import HTMLSession
from exceptions import FailToGetTotalPage, PaginationException
from urllib3.exceptions import HTTPError
import re, math


class NaverBookScraper:

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

    def get_bids(self, url):
        resp = self.session.get(url=url,
                                headers=self.headers)
        for i, link in enumerate(resp.html.links):
            try:
                bid = re.search('http:\/\/book.naver.com\/bookdb\/book_detail\.nhn\?bid=(\d+)', link).group(1)
                yield bid
            except AttributeError:
                continue

    def get_review_links(self, bid, page=None):
        total_page_num = self.total_page_num(bid, page)

        def gen_review_links_per_page(bid, page):
            if (0 < page <= total_page_num) is False:
                raise PaginationException

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
                except (PaginationException, HTTPError):
                    break

    def total_page_num(self, bid, page):
        url = f'http://book.naver.com/bookdb/review.nhn?bid={bid}&page={page}'
        try:
            total_reviews_span = self.session.get(url=url, headers=self.headers).html.xpath("//span[@class='num']")[0]
            total_reviews = int(total_reviews_span.search('({}건)')[0].replace(',', ''))
            total_page_num = math.ceil(total_reviews / 10)
        except Exception:
            raise FailToGetTotalPage
        return total_page_num


if __name__ == '__main__':
    naverbook_scraper = NaverBookScraper()
    for link in naverbook_scraper.get_review_links(13457707):
        print(link)
