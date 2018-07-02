import math
from book_review_scraper.exceptions import HelperError, StarImagesError


def calculate_rating(star_images):
    """ yes24 별 이미지링크 url 들로 내용점수, 편집점수를 계산합니다.
    ex) * * * o o * * * * o -> 3.0, 4.0
    ex) * * * * 0 -> 4.0
    :param star_images:
    :return: yes24 내용점수, 편집점수
    """
    if len(star_images) % 5 != 0:
        raise StarImagesError("별 이미지 배열의 개수는 5의 배수개여야 합니다")
    content_rating = sum(1 for src in star_images[:5] if 'Off' not in src)
    edit_rating = sum(1 for src in star_images[5:] if 'Off' not in src)
    return float(content_rating), float(edit_rating)


class ReviewPagingHelper(object):
    """ 리뷰 Pagination 할 때 도움을 주는 함수들을 모아 놓은 클래스 입니다.
    """
    def __init__(self, start, end, per_page):
        super().__init__()
        self.start = start
        self.end = end
        self.per_page = per_page

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def per_page(self):
        return self._per_page

    @start.setter
    def start(self, start):
        if start <= 0:
            self._start = 1
            return
        self._start = start

    @end.setter
    def end(self, end):
        if end < self._start:
            raise HelperError('end 는 start 보다 커야만 합니다.')
        self._end = end

    @per_page.setter
    def per_page(self, per_page):
        if per_page <= 0:
            raise HelperError('per_page 는 0보다 커야 합니다.')
        self._per_page = per_page

    @property
    def start_idx(self):
        mod = self._start % self._per_page
        if mod == 1:
            return 0
        if mod == 0:
            return self._per_page - 1
        return mod - 1

    @property
    def end_idx(self):
        mod = self._end % self._per_page
        if mod == 0:
            return self._per_page
        return mod

    @property
    def start_page(self):
        return math.ceil(self._start / self._per_page)

    @property
    def end_page(self):
        return math.ceil(self._end / self._per_page)

    @property
    def count_to_get(self):
        return self._end - self._start + 1
