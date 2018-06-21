#### A Simple Book Review Scraper

```python
from book_review_scraper import scraper

for review in scraper.get_reviews(isbn13=9788932919126, bookstores=Naverbook, count=20):
    print(review.title)
    print(review.text)

for review in scraper.get_reviews(isbn13=9788932919126, bookstores=Kyobo, count=10):
    print(review.title)
    print(review.text)

for review in scraper.get_reviews(isbn13=9788932919126, bookstores=(Naverbook, Kyobo), count=9):
    print(review.title)
    print(review.text)
```

또는

``` python

from book_review_scraper import bookstores
naverbook = bookstores.Naverbook()
for review in naverbook.get_reviews(isbn13=9791158160784, count=10):
    print(review.title)
    print(review.text)
    ...

kyobo = bookstores.Kyobo()
for review in kyobo.get_reviews(isbn13=9791158160784, count=10):
    print(review.title)
    print(review.text)
    ...

```

```python
각 서점의 리뷰는 namedtuple 로 구현되어 있습니다.

Kyobo.Review = namedtuple("NaverbookReview", ["title", "text", "created", "detail_link", "thumb_nail_link"])
Naverbook.Review = namedtuple("KyoboReview", ["text", "created", "rating", "likes"])

```