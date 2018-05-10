from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
import re

class KyoboScraper:
    domain = "http://www.kyobobook.co.kr/index.laf"
    timeout = 10

    def __init__(self):
        self.book_detail_pages_set = set()
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/66.0.3359.139 Safari/537.36")
        options.add_argument("lang=ko_KR")
        self.driver = webdriver.Chrome('chromedriver', chrome_options=options)

    def add_book_detail_links(self):
        self.driver.get(KyoboScraper.domain)
        a_tag_elements = WebDriverWait(self.driver, KyoboScraper.timeout).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 "//a[(contains(@href, 'barcode'))"
                                                 " and not (contains(@href, 'gift'))]"))
        )
        for element in a_tag_elements:
            new_page = element.get_attribute('href')
            if new_page not in self.book_detail_pages_set:
                print("add {0}".format(new_page))
                self.book_detail_pages_set.add(new_page)

    def get_book_log_reviews(self):
        for link in self.book_detail_pages_set:
            print("scraping {0}".format(link))
            self.driver.get(link)
            try :
                isbn_13 = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                    EC.presence_of_element_located((By.XPATH,
                                                   "//span[@title='ISBN-13']"))
                ).text
                # isbn 이 없는 페이지라면 종이책에 대한 상세 페이지가 아니라고 판단.q
            except TimeoutException as e:
                print(e.msg)
                continue

            # 리뷰의 총 개수 구하기
            total_span_element = self.driver.find_element(By.XPATH, "//h2[@class='title_detail_basic']/span")
            match = re.search("\((\d+)\)", total_span_element.text)
            if match is None:
                continue
            book_log_reviews_count = int(match.group(1))
            if book_log_reviews_count == 0:
                continue
            print("북 로그 개수 : {0}".format(book_log_reviews_count))

            try:
                open_popup_js = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//following::small/a[text()='전체보기']"))
                ).get_attribute('onclick')
                self.driver.execute_script(open_popup_js)
            except TimeoutException as e:
                print(e.msg)
                continue

            main_window = self.driver.current_window_handle

            for window_handle in self.driver.window_handles:
                if main_window != window_handle:
                    self.driver.switch_to.window(window_handle)
                    break

            try:
                book_log_reviews_div = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='title_detail_result']"))
                )
            except (TimeoutException, NoSuchElementException) as e:
                print("occur error {0}".format(e))
                self.close_popup(main_window)
                continue
            try:
                current_review_count = 0
                list_idx = 1
                while current_review_count < book_log_reviews_count:
                    if list_idx == 11:
                        self.driver.find_element(By.XPATH, "//a[@class='btn_next']").click()
                        book_log_reviews_div = WebDriverWait(self.driver, KyoboScraper.timeout).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@class='title_detail_result']"))
                        )
                        list_idx = 1
                        continue
                    li = book_log_reviews_div.find_element(By.XPATH, "//ul[@class='list_detail_booklog']/li[{0}]"
                                                           .format(list_idx))
                    print(list_idx, current_review_count)
                    list_idx += 1
                    current_review_count += 1
            except (TimeoutException, NoSuchElementException) as e:
                print("occur error {0}".format(e))
                self.close_popup(main_window)
                continue

    def close_popup(self, main_window):
        self.driver.close()
        self.driver.switch_to.window(main_window)

kyobo_scrapper = KyoboScraper()

try:
    kyobo_scrapper.add_book_detail_links()
    kyobo_scrapper.get_book_log_reviews()

except Exception as e:
    print("occur exception")
    e.with_traceback()
finally:
    kyobo_scrapper.driver.quit()
    print("kyobo web driver close...")