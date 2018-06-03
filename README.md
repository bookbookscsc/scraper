#### A Simple Book Review Scraper

``` python

from book_review_scraper import bookstores
naverbook = bookstores.Naverbook()
for review in naverbook.get_reviews(isbn=9791158160784, count=10):
    print(review.title)
    print(review.text)
    ...

kyobo = bookstores.Kyobo()
for review in kyobo.get_reviews(isbn=9791158160784, count=10):
    print(review.title)
    print(review.text)
    ...

```pyth