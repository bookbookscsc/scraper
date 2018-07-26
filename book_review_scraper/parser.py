import re
from datetime import datetime
from .helper import calculate_rating


def parse_interpark_review_info(html, _):
    row = html.xpath("//div[@class='list_wrap']", first=True)
    count_html = row.xpath("div/div/div[2]/div/p", first=True)
    rating_html = row.xpath("//em[@class='rateNumber']", first=True)

    book_id = int(row.xpath("div/div/div/div/label/input", first=True).attrs['prdno'])
    count = int(re.search('\d+', count_html.text).group()) if count_html else 0
    rating = float(rating_html.text) if rating_html else 0.0
    title = row.xpath("div/div[2]/p[2]/b/a", first=True).text

    return book_id, title, rating, count


def parse_yes24_review_info(html, _):
    row = html.xpath("//div[@class='goodsList goodsList_list']//td[@ class ='goods_infogrp']", first=True)
    book_id_text = row.xpath("td/p/a", first=True).attrs['href']
    review_info_text = row.xpath("td/p[4]", first=True).text
    review_rating_src = [img.attrs['src'] for img in row.xpath("td/p[4]/img")]

    book_id = int(re.search('goods\/(\d+)', book_id_text).group(1))
    book_title = row.xpath("td/p/a/strong")[0].text
    content_rating, edit_rating = calculate_rating(review_rating_src)
    member_review_count = 0
    compiled_review_text = re.search('회원리뷰 \((\d+)개\)', review_info_text)

    if compiled_review_text is not None:
        member_review_count = int(compiled_review_text.group(1))

    return book_id, book_title, content_rating, edit_rating, member_review_count


def parse_kyobo_review_info(html, isbn13):
    row = html.xpath("//table[@class='type_list']/tbody/tr")[0]

    book_title = row.xpath("//div[@class='title']//strong")[0].text
    klover_rating_text = row.xpath("//div[@class='review klover']//b")[0].text
    book_log_cnt_text = row.xpath("//div[@class='review booklog']//b")[0].text
    book_log_rating_text = row.xpath("//div[@class='rating']/img")[0].attrs['alt']

    klover_rating = float(re.search("\d+\.?\d{0,3}", klover_rating_text).group())
    book_log_cnt = int(book_log_cnt_text)
    book_log_rating = float(re.search('5점 만점에 (\d)점', book_log_rating_text).group(1))
    return isbn13, book_title, klover_rating, book_log_rating, book_log_cnt


def parse_blog_review_info(html, _):
    row = html.xpath("//ul[@id='searchBiblioList']/li[@style='position:relative;']", first=True)
    info_li = row.text.split('\n')
    info_text = info_li[3]
    rating_and_cnt = re.search('(\d+\.?\d{0,3})점 \| 네티즌리뷰 (\d{0,3}),?(\d{0,3})건',
                               info_text).group(1, 2, 3)
    rating = float(rating_and_cnt[0])
    if rating_and_cnt[1] and rating_and_cnt[2]:
        count = int(rating_and_cnt[1]) * 1000 + int(rating_and_cnt[2])
    else:
        count = int(rating_and_cnt[1])
    id_a_tag = row.xpath("//a[starts-with(@href,'http://book.naver.com/bookdb/book_detail.nhn?bid=')]", first=True)
    title = info_li[0]
    book_id = int(id_a_tag.attrs['href'].split('=')[-1])
    return book_id, title, rating, count


def parse_inter_normal_review(json):
    pass


def parse_blog_review(html):
    title = html.xpath("//dl/dt")[0].text
    text = html.xpath("//dl/dd[starts-with(@id,'review_text')]")[0].text
    created = html.xpath("//dl/dd[@class='txt_inline']")[-1].text
    detail_link = html.xpath("//dl/dt/a")[-1].attrs['href']
    thumb_div = html.xpath("//div[@class='thumb']")
    if thumb_div:
        thumb_link = thumb_div[-1].xpath("//a/img")[-1].attrs['src']
    else:
        thumb_link = None
    return title, text, datetime.strptime(created.strip(), "%Y.%m.%d"), detail_link, thumb_link


def parse_klover_review(html):
    created = html.xpath("//dl/dd[@class='date']")[0].text
    rating = float(html.xpath("//dl/dd[@class='kloverRating']/span")[0].text)
    text = html.xpath("//dl/dd[@class='comment']/div[@class='txt']")[0].text
    likes = int(html.xpath("//li[@class='cmt_like']/span")[0].text)

    return text, datetime.strptime(created.strip(), "%Y-%m-%d"), rating, likes


def parse_book_log_review(html):
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
    return title, text, datetime.strptime(created.strip(), "%Y-%m-%d"), rating, likes


def parse_simple_review(html):
    text = html.xpath('//li/strong', first=True).text
    review_rating_src = [img.attrs['src'] for img in html.xpath('//li/p/img')]
    review_rating_text = html.xpath('//li/p', first=True).text.split('|')

    rating = calculate_rating(review_rating_src)[0]
    likes = int(re.search('\d+', review_rating_text[2]).group())
    created = review_rating_text[1]
    return text, rating, datetime.strptime(created.strip(), "%Y-%m-%d"), likes


def parse_member_review(html):
    title = html.xpath('//li/a/strong', first=True).text
    review_rating_src = [img.attrs['src'] for img in html.xpath('//li/p//img') if "sysimage" in img.attrs['src']]
    review_rating_text = html.xpath('//li/p')[0].text.split('|')
    likes_text = review_rating_text[3]

    likes = int(re.search('\d+', likes_text).group())
    detail_link = html.xpath('//li/span[2]/cite/a')[0].attrs['href']
    content_rating, edit_rating = calculate_rating(review_rating_src)
    created = review_rating_text[2]
    full_text = "\n".join([p.text for p in html.xpath('//li/span[2]/p') if p.text])
    return title, full_text, datetime.strptime(created.strip(), "%Y-%m-%d"), likes, content_rating, edit_rating, detail_link
