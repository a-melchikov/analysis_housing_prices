from typing import Any
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from web_driver_setup import WebDriverSetup


def get_url(base_url: str, params: dict[str, Any]) -> str:
    return base_url + "&".join(
        [
            f"{key}={'%2B'.join(value) if isinstance(value, list) else value}"
            for key, value in params.items()
        ]
    )


if __name__ == "__main__":
    web_driver_setup = WebDriverSetup(headless=True)
    driver: WebDriver = web_driver_setup.setup_driver()

    base_url: str = "https://orenburg.domclick.ru/search?"
    params: dict[str, Any] = {
        "deal_type": "sale",
        "category": "living",
        "offer_type": ["flat", "layout"],
        "aids": "5167",
        "rooms": ["1", "2", "3", "4+", "st"],
        "offset": 0,
    }

    try:
        urls = set()
        total_apartments = 0
        for offset in range(0, 200, 20):
            params["offset"] = offset
            url = get_url(base_url, params)
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jIdz3.c1NUU.xGMFS"))
            )

            apartments = driver.find_elements(By.CLASS_NAME, "jIdz3.c1NUU.xGMFS")

            for apartment in apartments:
                link_element = apartment.find_element(By.CLASS_NAME, "a4tiB2")
                link = link_element.get_attribute("href")
                print("Ссылка на объявление:", link)
                urls.add(link)
            total_apartments += len(apartments)
            print(f"Найдено {len(apartments)} квартир")
        print(f"В общем найдено {total_apartments} квартир")
        print(urls)
        print(len(urls))
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

    finally:
        driver.quit()
