
class ISBNNotFoundException(Exception):
    def __str__(self):
        return "페이지에서 ISBN 을 발견하지 못했습니다."


class BookLogDetailPopupNotOpenException(Exception):
    def __str__(self):
        return "북 로그 상세 페이지 팝업을 여는데 실패 했습니다."


class NotExistBookLogException(Exception):
    def __str__(self):
        return "북로그 리뷰가 없습니다."
