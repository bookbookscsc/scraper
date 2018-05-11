from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from exceptions import ISBNNotFoundException, BookLogDetailPopupNotOpenException, NotExistBookLogException
import re, math


class BookLogPageInfo:
    def __init__(self, isbn, page_num, div):
        self.isbn = isbn
        self.page_num = page_num
        self.div = div


class KyoboScraper:

    domain = "http://www.kyobobook.co.kr/index.laf"
    book_detail_xpath = "//a[(contains(@href, 'barcode')) and not (contains(@href, 'gift'))]"
    isbn_xpath = "//span[@title='ISBN-13']"
    book_log_count_per_page = 10
    timeout = 5

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
                                                 KyoboScraper.book_detail_xpath))
        )
        new_book_detail_links = set((elem.get_attribute('href') for elem in book_detail_a_tag_elems))
        self.book_detail_pages_set |= new_book_detail_links

    def get_isbn_13(self):
        try:
            isbn_13 = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                EC.presence_of_element_located((By.XPATH, KyoboScraper.isbn_xpath))
            ).text
        except TimeoutException:
            raise ISBNNotFoundException
        else:
            return isbn_13

    def get_book_log_count(self):
        total_span_element = self.driver.find_element(By.XPATH, "//h2[@class='title_detail_basic']/span")
        match = re.search("\((\d+)\)", total_span_element.text)
        if match is None:
            raise NotExistBookLogException

        book_log_reviews_count = int(match.group(1))

        if book_log_reviews_count == 0:
            raise NotExistBookLogException

        print("북 로그 개수 : {0}".format(book_log_reviews_count))
        return book_log_reviews_count

    def get_book_log_popup_div(self):
        try:
            open_popup_js = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                EC.presence_of_element_located((By.XPATH, "//following::small/a[text()='전체보기']"))
            ).get_attribute('onclick')
            self.driver.execute_script(open_popup_js)

            main_window = self.driver.current_window_handle

            for window_handle in self.driver.window_handles:
                if main_window != window_handle:
                    self.driver.switch_to.window(window_handle)
                    break
            return WebDriverWait(self.driver, KyoboScraper.timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='title_detail_result']"))
            )
        except TimeoutException:
            raise BookLogDetailPopupNotOpenException

    def get_book_logs(self, info):
        for page in range(info.page_num):
            try:
                li_xpath = "//ul[@class='list_detail_booklog']//li"
                li = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                    EC.presence_of_all_elements_located((By.XPATH, li_xpath))
                )
                yield from li
                if page == info.page_num - 1:
                    break
                self.driver.find_element(By.XPATH, "//a[@class='btn_next']").click()
                info.div = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='title_detail_result']"))
                )
            except (TimeoutException, NoSuchElementException) as e:
                raise e

    def get_reviews(self):
        book_detail_pages_set = self.book_detail_pages_set.copy()
        print("현재 책 디테일 페이지 개수 {0}".format(len(self.book_detail_pages_set)))
        for i, link in enumerate(book_detail_pages_set):
            print("지금까지 확인한 책 개수 {0}".format(i + 1))
            main_window = self.driver.current_window_handle
            print("start scraping {0}".format(link))
            self.driver.get(link)
            try:
                isbn_13 = self.get_isbn_13()
                book_log_count = self.get_book_log_count()
            except (ISBNNotFoundException, NotExistBookLogException) as e:
                print(e)
                self.book_detail_pages_set.remove(link)
                continue
            try:
                bool_logs_div = self.get_book_log_popup_div()
                page_num = math.ceil(book_log_count / KyoboScraper.book_log_count_per_page)
                book_log_info = BookLogPageInfo(isbn_13, page_num, bool_logs_div)
                book_logs = self.get_book_logs(book_log_info)
            except (BookLogDetailPopupNotOpenException, TimeoutException, NoSuchElementException) as e:
                print(e)
                continue
            else:
                self.book_detail_pages_set.remove(link)
                print("스크래핑한 북 로그 개수 : {0}".format(len(list(book_logs))))
            finally:
                self.switch_main_window(main_window)

    def switch_main_window(self, main_window):
        self.driver.close()
        self.driver.switch_to.window(main_window)


kyobo_scrapper = KyoboScraper()

try:
    kyobo_scrapper.add_book_detail_links()
    kyobo_scrapper.get_reviews()

except Exception as e:
    print("occur exception")
    print(e)
finally:
    kyobo_scrapper.driver.quit()
    print("kyobo web driver close...")