import re
from .helper import calculate_rating


def parsing_review_info(info_text):
    rating_and_cnt = re.search('(\d+\.?\d{0,3})점 \| 네티즌리뷰 (\d{0,3}),?(\d{0,3})건',
                               info_text).group(1, 2, 3)
    rating = float(rating_and_cnt[0])
    if rating_and_cnt[1] and rating_and_cnt[2]:
        count = int(rating_and_cnt[1]) * 1000 + int(rating_and_cnt[2])
    else:
        count = int(rating_and_cnt[1])
    return rating, count


def parsing_blog_review(html):
    title = html.xpath("//dl/dt")[0].text
    text = html.xpath("//dl/dd[starts-with(@id,'review_text')]")[0].text
    date = html.xpath("//dl/dd[@class='txt_inline']")[-1].text
    detail_link = html.xpath("//dl/dt/a")[-1].attrs['href']
    thumb_div = html.xpath("//div[@class='thumb']")
    if thumb_div:
        thumb_link = thumb_div[-1].xpath("//a/img")[-1].attrs['src']
    else:
        thumb_link = None
    return title, text, date, detail_link, thumb_link


def parsing_klover_review(html):
    created = html.xpath("//dl/dd[@class='date']")[0].text
    rating = html.xpath("//dl/dd[@class='kloverRating']/span")[0].text
    text = html.xpath("//dl/dd[@class='comment']/div[@class='txt']")[0].text
    likes = html.xpath("//li[@class='cmt_like']/span")[0].text
    return text, created, rating, likes


def parsing_book_log_review(html):
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
    return title, text, rating, created, likes


def parsing_simple_review(html):
    text = html.xpath('//li/strong', first=True).text
    review_rating_src = [img.attrs['src'] for img in html.xpath('//li/p/img')]
    review_rating_text = html.xpath('//li/p', first=True).text.split('|')

    rating = calculate_rating(review_rating_src)[0]
    likes = re.search('\d+', review_rating_text[2]).group()
    date = review_rating_text[1]
    return text, rating, date, likes


def parsing_member_review(html):
    title = html.xpath('//li/a/strong', first=True).text
    review_rating_src = [img.attrs['src'] for img in html.xpath('//li/p//img') if "sysimage" in img.attrs['src']]
    review_rating_text = html.xpath('//li/p')[0].text.split('|')
    likes_text = review_rating_text[3]

    likes = re.search('\d+', likes_text).group()
    detail_link = html.xpath('//li/span[2]/cite/a')[0].attrs['href']
    content_rating, edit_rating = calculate_rating(review_rating_src)
    date = review_rating_text[2]
    full_text = "\n".join([p.text for p in html.xpath('//li/span[2]/p') if p.text])
    return title, full_text, date, likes, content_rating, edit_rating, detail_link

