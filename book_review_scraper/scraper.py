from collections import Iterable
from .bookstores import Naverbook


def get_reviews(isbn13, bookstores=Naverbook, start=1, end=10):
    """
    :param isbn13: 리뷰를 보고 싶은 책의 isbn13
    :param bookstores: 리뷰를 가져올 인터넷 서점(BookStore) 메타 클래스
    :param count: 한 서점당 가져올 리뷰의 최대 리뷰 수
    :return: 각 서점의 리뷰들 제너레이터
    """
    if isinstance(bookstores, type):
        yield from bookstores.get_reviews(isbn13, start, end)
    elif isinstance(bookstores, Iterable):
        for bookstore in bookstores:
            yield from bookstore.get_reviews(isbn13, start, end)

