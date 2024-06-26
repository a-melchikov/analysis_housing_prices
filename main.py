from logging import Logger
import os
import time
from typing import Any
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        if os.path.isfile("urls.txt"):
            logger.info("Чтение ссылок из файла urls.txt")
            urls = read_from_txt("urls.txt")
        else:
            logger.info("Получение ссылок с сайта")
            urls: set[str] = get_urls_apartments(driver, base_url, params, 0, 300)
            save_to_txt(urls, "urls.txt")

        for url in urls:
            driver.get(url)
            logger.debug("Переход по ссылке: %s", url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "OzY5o"))
                )
                gallery_footer = driver.find_element(
                    By.CLASS_NAME, "gallery-footer-90b-17-1-3"
                )
                li_elements = gallery_footer.find_elements(By.TAG_NAME, "li")
                for elem in li_elements:
                    print(elem.text, end=" ")
                print()
            except Exception as e:
                logger.error("Ошибка при обработке ссылки на квартиру %s: %s", url, e)
            time.sleep(3)

    except Exception as e:
        logger.critical("Произошла ошибка: %s", e)

    finally:
        driver.quit()
        logger.info("Веб-драйвер закрыт")
