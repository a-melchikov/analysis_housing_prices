from logging import Logger
import os
import re
import time
from typing import Any
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from logging_config import LogConfig, LogLevel, LoggerSetup
from web_driver_setup import WebDriverSetup


def setup_logger() -> Logger:
    logger_setup = LoggerSetup(
        logger_name=__name__,
        log_config=LogConfig(
            level=LogLevel.DEBUG, console_level=LogLevel.INFO, filename=None
        ),
    )
    return logger_setup.get_logger()


logger: Logger = setup_logger()


def get_url(base_url: str, params: dict[str, Any]) -> str:
    logger.debug("Генерация ссылки функция get_url")
    url = base_url + "&".join(
        [
            f"{key}={'%2B'.join(value) if isinstance(value, list) else value}"
            for key, value in params.items()
        ]
    )
    logger.debug("Сгенерированный URL: %s", url)
    return url


def get_urls_apartments(
    driver: WebDriver,
    base_url: str,
    params: dict,
    start_offset: int = 0,
    end_offset: int = 300,
) -> set[str]:
    urls = set()
    logger.info("Начинаем сбор ссылок на квартиры")
    for offset in range(start_offset, end_offset, 20):
        params["offset"] = offset
        url: str = get_url(base_url, params)
        driver.get(url)
        logger.debug("Переход по URL: %s", url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jIdz3.c1NUU.xGMFS"))
            )
        except Exception as e:
            logger.error("Тайм-аут при ожидании загрузки квартир: %s", e)
            continue

        apartments = driver.find_elements(By.CLASS_NAME, "jIdz3.c1NUU.xGMFS")

        for apartment in apartments:
            try:
                link_element = apartment.find_element(By.CLASS_NAME, "a4tiB2")
                link = link_element.get_attribute("href")
                logger.debug("Найдена ссылка на квартиру: %s", link)
                urls.add(link)
            except Exception as e:
                logger.error("Ошибка при получении ссылки на квартиру: %s", link)

        logger.info("Найдено %s квартир на смещении %s", len(apartments), offset)
    logger.info("Всего уникальных квартир найдено: %s", len(urls))
    return urls


def save_to_txt(urls: set[str], filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as file:
            for url in urls:
                file.write(f"{url}\n")
        logger.info("Ссылки сохранены в файл %s", filename)
    except Exception as e:
        logger.error("Ошибка при сохранении ссылок в файл: %s", e)


def read_from_txt(filename: str) -> set[str]:
    urls = set()
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                urls.add(line.strip())
        logger.info("Ссылки прочитаны из файла %s", filename)
    except Exception as e:
        logger.error("Ошибка при чтении ссылок из файла: %s", e)
    return urls


def get_price(driver: WebDriver) -> tuple[str, str]:
    price_element = driver.find_element(By.CLASS_NAME, "JfVCK").find_element(
        By.TAG_NAME, "span"
    )
    price = re.sub(r"\s+", "", price_element.get_attribute("textContent").strip())
    sqm_price_element = driver.find_element(By.CLASS_NAME, "xp7iu")
    sqm_price = re.sub(
        r"\s+", "", sqm_price_element.get_attribute("textContent").strip()
    )

    data = {
        "Цена": price,
        "Цена за квадрат": sqm_price,
    }
    return data


def get_gallery_footer(driver):
    gallery_footer = driver.find_element(By.CLASS_NAME, "gallery-footer-90b-17-1-3")
    li_elements = gallery_footer.find_elements(By.TAG_NAME, "li")
    data = {}
    for elem in li_elements:
        key = elem.find_element(By.TAG_NAME, "span").text
        value = elem.find_element(By.TAG_NAME, "div").text
        data[key] = value

    return data


def get_about_apartments(driver):
    try:
        # Ищем кнопку "Показать полностью"
        button = driver.find_element(
            By.XPATH, "//button[@data-e2e-id='detail-spoiler']"
        )

        # Спускаемся вниз до кнопки и нажимаем ее
        ActionChains(driver).move_to_element(button).perform()
        time.sleep(1)
        button.click()

    except NoSuchElementException:
        logger.warning("Кнопка 'Показать полностью' не найдена на странице")

    about_apartment = driver.find_element(By.XPATH, '//div[@data-e2e-id="О квартире"]')

    list_items = about_apartment.find_elements(By.TAG_NAME, "li")
    data = {}
    for item in list_items:
        key = item.get_attribute("data-e2e-id")
        value = item.text[len(key) :].strip()
        data[key] = value
    return data


def get_building_info(driver):
    data = {}
    try:
        building_info = driver.find_element(By.CLASS_NAME, "M9M9q")
        list_items = building_info.find_elements(By.TAG_NAME, "li")

        for item in list_items:
            try:
                key = item.get_attribute("data-e2e-id")
                value = item.text[len(key) :].strip()
                data[key] = value
            except Exception as e:
                logger.error("Ошибка при обработке элемента списка: %s", e)
                continue
    except NoSuchElementException:
        logger.warning("Элемент с классом 'M9M9q' не найден на странице")
    except Exception as e:
        logger.error("Произошла ошибка при попытке получить информацию о здании: %s", e)

    return data


def get_urls_zones(
    driver: WebDriver, params: dict[str, Any], zones: dict[str, int], base_url: str
) -> None:
    logger.info("Начинаем собирать данные для районов: %s", zones)
    for k, v in zones.items():
        params["aids"] = v
        logger.info("Ссылки собираются для %s района", k)
        urls: set[str] = get_urls_apartments(driver, base_url, params, 0, 200)
        save_to_txt(urls, f"{k}_urls_{len(urls)}.txt")
    logger.info("Сбор данных для районов закончен")


if __name__ == "__main__":
    web_driver_setup = WebDriverSetup(headless=False)
    driver: WebDriver = web_driver_setup.setup_driver()

    base_url: str = "https://orenburg.domclick.ru/search?"
    zones: dict[str, int] = {
        "дзержинский": 40840272,
        "промышленный": 40842569,
        "ленинский": 40842379,
        "центральный": 40842421,
    }
    params: dict[str, Any] = {
        "deal_type": "sale",
        "category": "living",
        "offer_type": ["flat", "layout"],
        "aids": "5167",
        "rooms": ["1", "2", "3", "4+", "st"],
        "offset": 0,
    }

    cookies_accepted = False
    filename = "ленинский_urls_200.txt"

    try:
        if os.path.isfile(filename):
            logger.info("Чтение ссылок из файла %s", filename)
            urls = read_from_txt(filename)
        else:
            logger.info("Получение ссылок с сайта")
            urls: set[str] = get_urls_apartments(driver, base_url, params, 0, 300)
            save_to_txt(urls, filename)

        for url in urls:
            driver.get(url)
            logger.debug("Переход по ссылке: %s", url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "OzY5o"))
                )

                data = {}

                if not cookies_accepted:
                    accept_cookie_button = driver.find_element(
                        By.XPATH, "//button[@data-e2e-id='cookie-alert-accept']"
                    )
                    accept_cookie_button.click()
                    time.sleep(1)
                    cookies_accepted = True
                data = {
                    "Ссылка": url,
                }
                data.update(get_price(driver))
                data.update(get_about_apartments(driver))
                data.update(get_building_info(driver))
                if any(filename.startswith(x) for x in zones):
                    data.update({"Район": f"{filename.split('_', maxsplit=1)[0]}"})
                print(data)

            except Exception as e:
                logger.error("Ошибка при обработке ссылки на квартиру %s: %s", url, e)

    except Exception as e:
        logger.critical("Произошла ошибка: %s", e)

    finally:
        driver.quit()
        logger.info("Веб-драйвер закрыт")
