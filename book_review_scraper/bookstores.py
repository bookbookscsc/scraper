import re
from requests_html import HTMLSession
from book_review_scraper.exceptions import FindBookIDError, ScrapeReviewContentsError, ISBNError, PagingError
from book_review_scraper.helper import ReviewPagingHelper
from book_review_scraper.review import (NaverBookReview, NaverbookBookReviewInfo, KloverReview, BookLogReview,
                                        KyoboBookReviewInfo, Yes24MemberReview, Yes24SimpleReview, Yes24BookReviewInfo)
from book_review_scraper.config import (NaverBookConfig, Yes24Config, KyoboConfig)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://203.229.225.135/tm/?a=CR&b=MAC&c=300015071805&d=32&e=5301&f=Ym9vay5uYXZlci5jb20='
               '&g=1527138088560&h=1527138088581&y=0&z=0&x=1&w=2017-11-06&in=5301_00014684&id=20180524',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/66.0.3359.181 Safari/537.36',
}


class BookStore(object):
    """ 인터넷서점을 나타내는 클래스들의 부모 클래스

    """

    def __init__(self, scrape_config, search_url=None):
        """
        :param scrape_config: 가져올 리뷰 설정
        :param search_url: 책 id 를 찾기 위한 검색 url
        """
        self.session = HTMLSession()
        self.scrape_config = scrape_config
        self.search_url = search_url

    def get_review_page_info(self, isbn13):
        pass

    def prepare_gen_reviews(self, isbn13):
        """ 리뷰들을 가져올 준비를 한다.

        :param isbn13: 책의 isbn13
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
        review_info = self.get_review_page_info(isbn13)
        book_id = review_info.book_id

        helper = ReviewPagingHelper(self.scrape_config.start,
                                    self.scrape_config.end,
                                    self.scrape_config.per_page)

        start_page = helper.start_page
        end_page = helper.end_page
        start_review_idx = helper.start_idx
        end_review_idx = helper.end_idx
        count_to_get = helper.count_to_get

        return isbn13, book_id, start_page, end_page, start_review_idx, end_review_idx, count_to_get

    def gen_reviews(self, isbn13, book_id, start_page, end_page,
                    start_review_idx, end_review_idx, count_to_get):
        raise NotImplementedError

    def get_reviews(self, isbn13):
        """ 책의 리뷰들을 가지고 온다. (각각 인터넷 서점의 기본 정렬 순)

        :param isbn13: 책 isbn13
        :return: reviews 정보를 가지고 있는 제너레이터
        """
        prepared = self.prepare_gen_reviews(isbn13)
        yield from self.gen_reviews(*prepared)

    def __str__(self):
        return self.__class__.__name__


class Naverbook(BookStore):

    def __init__(self, scrape_config=NaverBookConfig.blog(1, 10)):
        super().__init__(
            scrape_config=scrape_config,
            search_url='http://book.naver.com/search/search.nhn?sm=sta_hty.book&sug=&where=nexearch&query='
        )
        self.id_a_tag_xpath = "//a[starts-with(@href,'http://book.naver.com/bookdb/book_detail.nhn?bid=')]"

    def get_review_page_info(self, isbn13):
        if re.match('[\d+]{13}', str(isbn13)) is None:
            raise ISBNError(bookstore=self, isbn13=isbn13)

        response = self.session.get(self.search_url + f'{isbn13}', headers=headers)

        try:
            row = response.html.xpath("//ul[@id='searchBiblioList']/li[@style='position:relative;']")[0]
            info_li = row.text.split('\n')
            info_text = info_li[3]
            rating_and_cnt = re.search('(\d+\.?\d{0,3})점 \| 네티즌리뷰 (\d+)건 \|', info_text).group(1, 2)
            id_a_tag = row.xpath(self.id_a_tag_xpath)[0]

            title = info_li[0]
            book_id = int(id_a_tag.attrs['href'].split('=')[-1])
            rating = float(rating_and_cnt[0])
            cnt = int(rating_and_cnt[1])
            return NaverbookBookReviewInfo(book_id, title, rating, cnt)

        except (ValueError, IndexError, AttributeError):
            raise FindBookIDError(isbn13=isbn13, bookstore=self)

    def gen_reviews(self, isbn13, book_id, start_page, end_page,
                    start_review_idx, end_review_idx, count_to_get):
        cur_page = start_page
        cur_count = 0

        response = self.session.get(self.scrape_config.url(book_id, cur_page),
                                    headers=headers)
        if not response.ok:
            raise PagingError(bookstore=self.__str__(), isbn13=isbn13)
        html = response.html

        while cur_page <= end_page:
            s = 0 if (cur_page != start_page) else start_review_idx
            e = self.scrape_config.per_page + 1 if (cur_page != end_page) else end_review_idx
            try:
                for li in html.xpath("//ul[@id='reviewList']/li")[s:e]:
                    title = li.xpath("//dl/dt")[0].text
                    text = li.xpath("//dl/dd[starts-with(@id,'review_text')]")[0].text
                    date = li.xpath("//dl/dd[@class='txt_inline']")[-1].text
                    detail_link = li.xpath("//dl/dt/a")[-1].attrs['href']
                    thumb_div = li.xpath("//div[@class='thumb']")
                    if thumb_div:
                        thumb_link = thumb_div[-1].xpath("//a/img")[-1].attrs['src']
                        yield NaverBookReview(title=title, text=text, created=date,
                                              detail_link=detail_link, thumb_nail_link=thumb_link, isbn13=isbn13)
                    else:
                        yield NaverBookReview(title, text=text, created=date,
                                              detail_link=detail_link, thumb_nail_link=None, isbn13=isbn13)
                    cur_count += 1
                    if cur_count >= count_to_get:
                        return
            except (IndexError, AttributeError, ValueError):
                raise ScrapeReviewContentsError(bookstore=self.__str__(), isbn13=isbn13, idx=cur_count)
            cur_page += 1
            response = self.session.get(self.scrape_config.url(book_id, cur_page),
                                        headers=headers)
            if not response.ok:
                raise PagingError(bookstore=self.__str__(), isbn13=isbn13)
            html = response.html


class Kyobo(BookStore):

    def __init__(self, scrape_config=KyoboConfig.klover(1, 10)):
        super().__init__(scrape_config=scrape_config,
                         search_url='http://www.kyobobook.co.kr/search/SearchKorbookMain.jsp?'
                                    'vPstrCategory=KOR&vPstrKeyWord={}&vPplace=top')

    def get_review_page_info(self, isbn13):
        if re.match('[\d+]{13}', str(isbn13)) is None:
            raise ISBNError(bookstore=self, isbn13=isbn13)

        response = self.session.get(self.search_url.format(isbn13), headers=headers)
        row = response.html.xpath("//table[@class='type_list']/tbody/tr")[0]

        book_title = row.xpath("//div[@class='title']//strong")[0].text
        klover_rating_text = row.xpath("//div[@class='review klover']//b")[0].text
        book_log_cnt_text = row.xpath("//div[@class='review booklog']//b")[0].text
        book_log_rating_text = row.xpath("//div[@class='rating']/img")[0].attrs['alt']

        klover_rating = float(re.search("\d+\.?\d{0,3}", klover_rating_text).group())
        book_log_cnt = int(book_log_cnt_text)
        book_log_rating = float(re.search('5점 만점에 (\d)점', book_log_rating_text).group(1))

        return KyoboBookReviewInfo(isbn13, book_title, klover_rating, book_log_rating, book_log_cnt)

    def gen_reviews(self, isbn13, book_id, start_page, end_page,
                    start_review_idx, end_review_idx, count_to_get):
        cur_page = start_page
        cur_count = 0
        response = self.session.get(self.scrape_config.url(book_id, cur_page), headers=headers)
        ul = response.html.xpath(self.scrape_config.ul_xpath, first=True)

        while cur_page <= end_page:
            s = 0 if (cur_page != start_page) else start_review_idx
            e = self.scrape_config.per_page + 1 if (cur_page != end_page) else end_review_idx

            try:
                for li in ul.xpath(self.scrape_config.li_xpath)[s:e]:
                    if self.scrape_config.review_type == KyoboConfig.KlOVER:
                        yield KloverReview(*self._parsing_klover_review(li, isbn13))
                    elif self.scrape_config.review_type == KyoboConfig.BOOK_LOG:
                        yield BookLogReview(*self._parsing_book_log_review(li, isbn13))
                    cur_count += 1
                    if cur_count >= count_to_get:
                        return
            except (IndexError, AttributeError, ValueError):
                raise ScrapeReviewContentsError(bookstore=self.__str__(), isbn13=isbn13, idx=cur_count)
            cur_page += 1

    def _parsing_klover_review(self, html, isbn13):
        created = html.xpath("//dl/dd[@class='date']")[0].text
        rating = html.xpath("//dl/dd[@class='kloverRating']/span")[0].text
        text = html.xpath("//dl/dd[@class='comment']/div[@class='txt']")[0].text
        likes = html.xpath("//li[@class='cmt_like']/span")[0].text
        return text, created, rating, likes, isbn13

    def _parsing_book_log_review(self, html, isbn13):
        full_text = html.text
        partial_text_list = full_text.split("\n")
        header = html.xpath("//div[@class='title']", first=True)
        title = header.xpath("//a/strong", first=True).text
        created_likes_text = header.xpath("//span", first=True).text
        created_and_likes = re.search("\| (\d{4}-\d{2}-\d{2}) \| 추천: (\d+) \|", created_likes_text).group(1, 2)
        created = created_and_likes[0]
        likes = int(created_and_likes[1])
        rating_text = header.xpath("//span/img", first=True).attrs['alt']
        rating = float(re.search('5점 만점에 (\d)점', rating_text).group(1))
        text = "\n".join(partial_text_list[1:-1])
        return title, text, rating, created, likes, isbn13


class Yes24(BookStore):

    def __init__(self, scrape_config=Yes24Config.simple(1, 10)):
        super().__init__(scrape_config,
                         search_url='http://www.yes24.com/searchcorner/Search?keywordAd=&keyword=&query={}')

    def calculate_rating(self, isbn13, star_images):
        if len(star_images) % 5 != 0:
            raise ScrapeReviewContentsError(bookstore=self, isbn13=isbn13)

        content_rating = sum(1 for src in star_images[:5] if 'Off' not in src)
        edit_rating = sum(1 for src in star_images[5:] if 'Off' not in src)

        return float(content_rating), float(edit_rating)

    def get_review_page_info(self, isbn13):
        if re.match('[\d+]{13}', str(isbn13)) is None:
            raise ISBNError(bookstore=self, isbn13=isbn13)

        response = self.session.get(self.search_url.format(isbn13), headers=headers)
        row = response.html.xpath("//div[@class='goodsList goodsList_list']//td[@ class ='goods_infogrp']")[0]
        book_id_text = row.xpath("td/p/a")[0].attrs['href']
        review_info_text = row.xpath("td/p[4]")[0].text
        review_rating_src = [img.attrs['src'] for img in row.xpath("td/p[4]/img")]

        book_id = int(re.search('goods\/(\d+)', book_id_text).group(1))
        book_title = row.xpath("td/p/a/strong")[0].text
        rating = self.calculate_rating(isbn13, review_rating_src)
        member_review_count = 0
        compiled_review_text = re.search('회원리뷰 \((\d+)개\)', review_info_text)

        if compiled_review_text is not None:
            member_review_count = int(compiled_review_text.group(1))

        return Yes24BookReviewInfo(book_id, book_title, rating[0], rating[1], member_review_count)

    def gen_reviews(self, isbn13, book_id, start_page, end_page,
                    start_review_idx, end_review_idx, count_to_get):
        cur_page = start_page
        cur_count = 0
        response = self.session.get(self.scrape_config.url(book_id, cur_page),
                                    headers=headers)

        ul = response.html.xpath("//ul[@class='list']", first=True)

        while cur_page <= end_page:
            s = 0 if (cur_page != start_page) else start_review_idx
            e = self.scrape_config.per_page + 1 if (cur_page != end_page) else end_review_idx
            try:
                for li in ul.xpath('//li')[s:e]:

                    if self.scrape_config.review_type == Yes24Config.SIMPLE:
                        yield Yes24SimpleReview(*self._parsing_simple_review(isbn13, li))

                    elif self.scrape_config.review_type == Yes24Config.MEMBER:
                        yield Yes24MemberReview(*self._parsing_member_review(isbn13, li))

                    cur_count += 1
                    if cur_count >= count_to_get:
                        return
            except (IndexError, AttributeError, ValueError):
                raise ScrapeReviewContentsError(bookstore=self.__str__(), isbn13=isbn13, idx=cur_count)
            cur_page += 1
            html = self.session.get(self.scrape_config.url(book_id, cur_page), headers=headers).html
            ul = html.xpath("//ul[@class='list']", first=True)

    def _parsing_simple_review(self, isbn13, html):
        text = html.xpath('//li/strong', first=True).text
        review_rating_src = [img.attrs['src'] for img in html.xpath('//li/p/img')]
        review_rating_text = html.xpath('//li/p', first=True).text.split('|')

        rating = self.calculate_rating(isbn13, review_rating_src)[0]
        likes = re.search('\d+', review_rating_text[2]).group()
        date = review_rating_text[1]
        return text, rating, date, likes, isbn13

    def _parsing_member_review(self, isbn13, html):
        title = html.xpath('//li/a/strong', first=True).text
        review_rating_src = [img.attrs['src'] for img in html.xpath('//li/p//img') if "sysimage" in img.attrs['src']]
        review_rating_text = html.xpath('//li/p')[0].text.split('|')
        likes_text = review_rating_text[3]

        likes = re.search('\d+', likes_text).group()
        detail_link = html.xpath('//li/span[2]/cite/a')[0].attrs['href']
        content_rating, edit_rating = self.calculate_rating(isbn13, review_rating_src)
        date = review_rating_text[2]
        full_text = "\n".join([p.text for p in html.xpath('//li/span[2]/p') if p.text])
        return title, full_text, date, likes, content_rating, edit_rating, detail_link, isbn13
