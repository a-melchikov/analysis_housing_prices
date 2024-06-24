import time

from selenium.webdriver.chrome.webdriver import WebDriver

from web_driver_setup import WebDriverSetup

if __name__ == "__main__":
    web_driver_setup = WebDriverSetup(headless=False)
    driver: WebDriver = web_driver_setup.setup_driver()

    url = "https://orenburg.domclick.ru/search?deal_type=sale&category=living&offer_type=flat&offer_type=layout&aids=5167&rooms=1&rooms=2&rooms=3&rooms=4%2B&rooms=st&offset=0"
    driver.get(url=url)
    time.sleep(3)
