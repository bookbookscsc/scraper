import re
import math
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException)
from selenium import webdriver
from exceptions import (ISBNNotFoundError,
                        BookLogDetailPopupNotOpenError,
                        NotExistReviewsError)



class KyoboScraper:

    class Xpath:
        book_detail_a_link = "//a[" \
                             "(contains(@href, 'barcode'))" \
                             " and not (contains(@href, 'gift'))" \
                             " and not (contains(@href, 'sam'))" \
                             " and not (contains(@href, 'digital'))" \
                             "]"
        isbn_span = "//span[@title='ISBN-13']"
        book_log_total_span = "//h2[@class='title_detail_basic']/span"
        book_log_popup_trigger_button = "//following::small/a[text()='전체보기']"
        book_log_popup_div = "//div[@class='title_detail_result']"
        book_log_li = "//ul[@class='list_detail_booklog']//li"
        book_log_next_page_button = "//a[@class='btn_next']"
        klover_total_span = "//span[@class='kloverTotal']"
        klover_div = "//ul[@class='board_list']//div[@class='comment_wrap']"
        klover_next_page_button = "//a[@href='javascript:_go_targetPage('{0}')']"

    domain = "http://www.kyobobook.co.kr/index.laf"
    timeout = 5
    book_log_count_per_page = 10
    klover_count_per_page = 15


    def __init__(self):
        self.book_detail_pages_set = set()
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/66.0.3359.139 Safari/537.36")
        options.add_argument("lang=ko_KR")
        self.driver = webdriver.Chrome('chromedriver', chrome_options=options)

    def add_book_detail_links(self, page_url=domain):
        self.driver.get(page_url)
        book_detail_a_tag_elems = WebDriverWait(self.driver, KyoboScraper.timeout).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 KyoboScraper.Xpath.book_detail_a_link))
        )
        new_book_detail_links = set((elem.get_attribute('href') for elem in book_detail_a_tag_elems))
        self.book_detail_pages_set |= new_book_detail_links

    def get_isbn_13(self):
        try:
            isbn_13 = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                EC.presence_of_element_located((By.XPATH, KyoboScraper.Xpath.isbn_span))
            ).text
        except TimeoutException:
            raise ISBNNotFoundError
        else:
            return isbn_13

    def get_review_count(self, xpath):
        time.sleep(0.5)
        total_span_element = self.driver.find_element(By.XPATH, xpath)
        match = re.search("\((\d+)\)", total_span_element.text)
        if match is None:
            raise NotExistReviewsError()

        reviews_count = int(match.group(1))

        if reviews_count == 0:
            raise NotExistReviewsError()

        print("리뷰 수: {0}".format(reviews_count))
        return reviews_count

    def open_book_log_popup_div(self):
        try:
            open_popup_js = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                EC.presence_of_element_located((By.XPATH, KyoboScraper.Xpath.book_log_popup_trigger_button))
            ).get_attribute('onclick')
            self.driver.execute_script(open_popup_js)

            main_window = self.driver.current_window_handle

            for window_handle in self.driver.window_handles:
                if main_window != window_handle:
                    self.driver.switch_to.window(window_handle)
                    break

        except TimeoutException:
            raise BookLogDetailPopupNotOpenError

    def get_book_logs(self, total_page_num):
        main_window = self.driver.current_window_handle
        self.open_book_log_popup_div()
        try:
            for cur_page in range(total_page_num):
                    li = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                        EC.presence_of_all_elements_located((By.XPATH, KyoboScraper.Xpath.book_log_li))
                    )
                    yield from li
                    if cur_page == total_page_num - 1:
                        break
                    self.driver.find_element(By.XPATH, KyoboScraper.Xpath.book_log_next_page_button).click()
        except (TimeoutException, NoSuchElementException) as e:
            raise e
        finally:
            self.switch_main_window(main_window)


    def get_klovers(self, total_page_num):
        for cur_page in range(total_page_num):
            li = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, KyoboScraper.Xpath.klover_div))
            )
            if cur_page < total_page_num - 1:
                self.driver.execute_script("javascript:_go_targetPage('{0}')".format(cur_page + 1))
            yield from li


    def get_reviews(self):
        book_detail_pages_set = self.book_detail_pages_set.copy()
        print("현재 책 디테일 페이지 개수 {0}".format(len(self.book_detail_pages_set)))
        for i, link in enumerate(book_detail_pages_set):
            print("start scraping {0}".format(link))
            self.driver.get(link)
            try:
                isbn_13 = self.get_isbn_13()
                # book_log_count = self.get_review_count(xpath=KyoboScraper.Xpath.book_log_total_span)
                self.driver.execute_script("location.href = '#review_simple'")
                klover_count = self.get_review_count(xpath=KyoboScraper.Xpath.klover_total_span)
            #
            except (ISBNNotFoundError, NotExistReviewsError, NoSuchElementException) as e:
                print(e)
                self.book_detail_pages_set.remove(link)
                continue
            finally:
                print("지금까지 확인한 책 개수 {0}".format(i + 1))

            try:
                # book_log_page_num = math.ceil(book_log_count / KyoboScraper.book_log_count_per_page)
                # book_logs = self.get_book_logs(book_log_page_num)
                # print("스크래핑한 북 로그 개수 : {0}".format(len(list(book_logs))))
                klover_page_num = math.ceil(klover_count / KyoboScraper.klover_count_per_page)
                klovers = self.get_klovers(total_page_num=klover_page_num)
                print(len(list(klovers)))
                # print("스크래핑한 클로버 리뷰 개수 : {0}".format(len(list(klovers))))
            except (BookLogDetailPopupNotOpenError, TimeoutException, NoSuchElementException) as e:
                print(e)
                continue
            else:
                self.book_detail_pages_set.remove(link)
            finally:
                print("지금까지 확인한 책 개수 {0}".format(i + 1))


    def switch_main_window(self, main_window):
        self.driver.close()
        self.driver.switch_to.window(main_window)


kyobo_scrapper = KyoboScraper()

try:
    kyobo_scrapper.add_book_detail_links()
    kyobo_scrapper.get_reviews()

except Exception as e:
    print(e)
finally:
    kyobo_scrapper.driver.quit()
    print("kyobo web driver close...")