#### A Simple Book Review Scraper

인터넷 서점에서 책의 리뷰를 스크래핑 합니다. (네이버북, 교보문고)

#### 사용 방법

```python
from book_review_scraper import scraper

for review in scraper.get_reviews(isbn13=9788932919126, bookstores=Naverbook, start=2, end=20):
    print(review.title)
    print(review.text)

for review in scraper.get_reviews(isbn13=9788932919126, bookstores=Kyobo, start=5, end=70):
    print(review.title)
    print(review.text)

for review in scraper.get_reviews(isbn13=9788932919126, bookstores=(Naverbook, Kyobo)):
    print(review.title)
    print(review.text)
```

또는

``` python

from book_review_scraper import bookstores
naverbook = bookstores.Naverbook()
for review in naverbook.get_reviews(isbn13=9791158160784, start=6, end=10):
    print(review.title)
    print(review.text)
    ...

kyobo = bookstores.Kyobo()
for review in kyobo.get_reviews(isbn13=9791158160784, start=6, end=20):
    print(review.title)
    print(review.text)
    ...

```

```python
각 서점의 리뷰는 namedtuple 로 구현되어 있습니다.

Kyobo.Review = namedtuple("NaverbookReview", ["title", "text", "created", "detail_link", "thumb_nail_link"])
Naverbook.Review = namedtuple("KyoboReview", ["text", "created", "rating", "likes"])

```