from requests_html import HTMLSession
import re


class NaverBookScraper:

    def __init__(self):
        self.session = HTMLSession()
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': f'www.naver.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
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

    def get_review_links(self, bid, page=1):
        url = f'http://book.naver.com/bookdb/review.nhn?bid={bid}&page={page}'
        resp = self.session.get(url=url,
                                headers=self.headers)
        return (review_list.attrs['href'] for review_list in resp.html.xpath("//ul[@id='reviewList']/li//a"))


if __name__ == '__main__':
    nbs = NaverBookScraper()
    for review in nbs.get_review_links(bid=13542164, page=2):
        print(review)
