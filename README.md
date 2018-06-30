#### A Simple Book Review Scraper

책의 isbn13 으로 인터넷 서점에서 리뷰를 스크래핑 합니다. (네이버북, 교보문고, Yes24)

#### 사용 방법

pip3 install book_review_scraper

```python
from book_review_scraper.bookstores import (Naverbook, Kyobo, Yes24)

naverbook = Naverbook()

for review in naverbook.get_reviews(9791162540169):
    print(review.title)
    print(review.text)
    print(review.created)
    ....

# 인터넷 서점의 기본정렬순(날짜) 으로 20번째 리뷰 부터 최대 50번째 리뷰까지 스크래핑 합니다.
# 리뷰가 30개 밖에 없다면 20번째 부터 30번째 까지 스크래핑 합니다.
naverbook.scraper_config = NaverBookConfig(start=20, end=50)

for review in naverbook.get_reviews(9791162540169):
    print(review.text)
```

서점마다 여러개의 리뷰 종류가 있을 수 있습니다.

ex) 교보문고는 북로그리뷰, 클로버리뷰가 있고, Yes24는 회원리뷰, 간단리뷰가 있습니다.

```python

from book_review_scraper.config import (NaverBookConfig, Yes24Config, KyoboConfig)

yes24 = Yes24()
simple_review_config = Yes24Config(Yes24Config.SIMPLE, start=1, end=10)
yes24.scrape_config = simple_review_config

for review in yes24.get_reviews(9791162540169):
    assertIsInstance(review, Yes24SimpleReview)

member_review_config = Yes24Config(Yes24Config.MEMBER, start=2, end=10)
yes24.scrape_config = member_review_config

for review in yes24.get_reviews(9791162540169):
    assertIsInstance(review, Yes24MemberReview)

klover_config = KyoboConfig(KyoboConfig.KlOVER, start=1, end=10)
book_log_config = KyoboConfig(KyoboConfig.BOOK_LOG, start=1, end=10)

kyobo.scrape_config = klover_config

for review in kyobo.get_reviews(9791162540169):
    assertIsInstance(review, KloverReview)

kyobo.scrape_config = book_log_config

for review in kyobo.get_reviews(9791162540169):
    assertIsInstance(review, BookLogReview)
```

책의 총 리뷰 개수, 총 점수를 얻고자 할때는

```python
book_review_info = kyobo.get_review_page_info(9791188461332)
assertIsInstance(book_review_info.book_log_rating, float)
assertIsInstance(book_review_info.klover_rating, float)
assertIsInstance(book_review_info.book_log_count, int)
```
### [0.8]()
> 리뷰 타입, 설정하는 하는 코드를 수정

```python
  simple_review_config = Yes24Config(Yes24Config.SIMPLE, start=1, end=10)
  # or
  simple_review_config = Yes24Config.simple(1, 10)

  klover_config = KyoboConfig(KyoboConfig.KlOVER, start=1, end=10)
  # or
  klover_config = KyoboConfig.klover(start=1, end=10)
```
### [0.7](https://github.com/bookbookscsc/scraper/commit/9b0ac084d987b18ec2464b02e3d51f60d43d1fb3)
> naverbook 리뷰 정보를 가져오는 정규식 수정
### [0.5](https://github.com/bookbookscsc/scraper/commit/4888aae1ade7c77c9b4df3e8830dd264f32101ad)
> yes24 검색 화면에 회원리뷰가 없을때 처리 추가, book_id 캐쉬하는 모듈 삭제
