from requests_html import HTMLSession
import re

session = HTMLSession()


def get_bids(url):

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language':'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': f'www.naver.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    }

    def gen_bids(url):
        resp = session.get(url, headers=headers)
        for i, link in enumerate(resp.html.links):
            try:
                bid = re.search('http:\/\/book.naver.com\/bookdb\/book_detail\.nhn\?bid=(\d+)', link).group(1)
                yield bid
            except AttributeError as e:
                continue

    return gen_bids(url=url)


for bid in get_bids(url='http://book.naver.com/bookdb/book_detail.nhn?bid=11211133'):
    print(bid)
